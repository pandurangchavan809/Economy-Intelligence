# etl/country_trade_exchange.py
import requests
import time
from database.connection import get_connection

BASE_URL = "https://api.worldbank.org/v2/country/{iso3}/indicator/{indicator}"

INDICATORS = {
    "exports": "NE.EXP.GNFS.CD",
    "imports": "NE.IMP.GNFS.CD",
    "exchange_rate": "PA.NUS.FCRF",
}

START_YEAR = 2004
END_YEAR = 2025
REQUEST_TIMEOUT = 25
SLEEP_BETWEEN_COUNTRIES = 0.6


def safe_float(v):
    """Convert v to float or return None (handles None, 'n/a', '')"""
    if v is None:
        return None
    try:
        return float(v)
    except Exception:
        return None


def fetch_series(iso3, indicator):
    """
    Return a list of records for the given country iso3 and WB indicator.
    Always returns a list (never None). If anything goes wrong it returns [].
    """
    url = BASE_URL.format(iso3=iso3, indicator=indicator)
    params = {"format": "json", "per_page": 2000, "date": f"{START_YEAR}:{END_YEAR}"}
    try:
        r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except Exception as e:
        print(f"⚠️ Request error for {iso3} {indicator}: {e}")
        return []

    if r.status_code != 200:
        print(f"⚠️ HTTP {r.status_code} for {iso3} {indicator}")
        return []

    try:
        data = r.json()
    except Exception as e:
        print(f"⚠️ JSON decode error for {iso3} {indicator}: {e}")
        return []

    # World Bank returns a two-item array: [meta, data]
    if not isinstance(data, list) or len(data) < 2:
        return []

    series = data[1]
    if series is None or not isinstance(series, list):
        return []

    return series


def run():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    # fetch countries with iso3
    cur.execute("SELECT country_id, iso3 FROM countries WHERE iso3 IS NOT NULL")
    countries = cur.fetchall()

    trade_sql = """
        INSERT INTO country_trade
        (country_id, year, exports_usd, imports_usd, trade_balance_usd)
        VALUES (%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            exports_usd = VALUES(exports_usd),
            imports_usd = VALUES(imports_usd),
            trade_balance_usd = VALUES(trade_balance_usd)
    """

    fx_sql = """
        INSERT INTO country_exchange_rate
        (country_id, year, exchange_rate)
        VALUES (%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            exchange_rate = VALUES(exchange_rate)
    """

    for c in countries:
        iso3 = c["iso3"]
        cid = c["country_id"]
        print(f"🌍 Processing {iso3} (country_id={cid})")

        exports = fetch_series(iso3, INDICATORS["exports"])
        imports = fetch_series(iso3, INDICATORS["imports"])
        fx = fetch_series(iso3, INDICATORS["exchange_rate"])

        # Build per-year mapping
        yearly = {}

        # safe parse exports
        for row in exports:
            if not row or "date" not in row:
                continue
            try:
                yr = int(row["date"])
            except Exception:
                continue
            val = safe_float(row.get("value"))
            if val is not None:
                yearly.setdefault(yr, {})["exports"] = val

        # safe parse imports
        for row in imports:
            if not row or "date" not in row:
                continue
            try:
                yr = int(row["date"])
            except Exception:
                continue
            val = safe_float(row.get("value"))
            if val is not None:
                yearly.setdefault(yr, {})["imports"] = val

        # insert exchange rates (we store regardless of exports/imports)
        for row in fx:
            if not row or "date" not in row:
                continue
            try:
                yr = int(row["date"])
            except Exception:
                continue
            rate = safe_float(row.get("value"))
            # only insert if we have a numeric rate
            if rate is not None:
                try:
                    cur.execute(fx_sql, (cid, yr, rate))
                except Exception as e:
                    print(f"⚠️ DB error inserting FX for {iso3} {yr}: {e}")

        # insert trade per year (calculate trade_balance when both sides exist)
        for yr, vals in yearly.items():
            exp = vals.get("exports")
            imp = vals.get("imports")
            bal = None
            if (exp is not None) and (imp is not None):
                bal = exp - imp
            try:
                cur.execute(trade_sql, (cid, yr, exp, imp, bal))
            except Exception as e:
                print(f"⚠️ DB error inserting trade for {iso3} {yr}: {e}")

        # Respectful pause
        time.sleep(SLEEP_BETWEEN_COUNTRIES)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Country trade & exchange ETL complete")


if __name__ == "__main__":
    run()
