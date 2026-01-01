import requests
import time
from database.connection import get_connection

BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
START_YEAR = 2004
END_YEAR = 2025

INDICATORS = {
    "gdp": "NY.GDP.MKTP.CD",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "military_spending": "MS.MIL.XPND.CD",
    "debt_gdp": "GC.DOD.TOTL.GD.ZS"
}

def fetch_indicator(country, indicator, retries=3):
    url = BASE_URL.format(country=country, indicator=indicator)
    params = {
        "format": "json",
        "per_page": 1000,
        "date": f"{START_YEAR}:{END_YEAR}"
    }

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, params=params, timeout=30)
            
            # If server error, retry
            if r.status_code != 200:
                time.sleep(1)
                continue

            data = r.json()

            # API Structure Validation
            if not isinstance(data, list) or len(data) < 2:
                return []
            
            if data[1] is None:
                return []
            
            return data[1]

        except Exception as e:
            # Only print error on the last attempt to keep logs clean
            if attempt == retries:
                print(f"Failed to fetch {country}-{indicator}: {e}")
            time.sleep(1.5 * attempt) # Exponential backoff for retries
            
    return [] # Always return an empty list if all retries fail

def run(progress_callback=None):
    conn = get_connection()
    if not conn:
        print("Database connection failed.")
        return

    cursor = conn.cursor(dictionary=True)

    # INTELLIGENT RESUME LOGIC
    # Only select countries that exist in 'countries' table but NOT in 'economic_indicators'
    resume_query = """
        SELECT c.country_id, c.iso3 
        FROM countries c
        LEFT JOIN (
            SELECT DISTINCT country_id FROM economic_indicators
        ) e ON c.country_id = e.country_id
        WHERE e.country_id IS NULL AND c.iso3 IS NOT NULL
    """
    
    print("Analyzing database to find missing countries...")
    cursor.execute(resume_query)
    country_rows = cursor.fetchall()
    
    country_map = {row["iso3"]: row["country_id"] for row in country_rows}
    all_iso_codes = list(country_map.keys())

    # If no countries left, we are done
    if not all_iso_codes:
        print("Database is already 100% synchronized!")
        if progress_callback:
            progress_callback(1, 1, "DONE")
        return

    insert_sql = """
        INSERT INTO economic_indicators 
        (country_id, year, gdp, gdp_growth, inflation, 
         unemployment, debt_gdp, military_spending)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE
            gdp = VALUES(gdp),
            gdp_growth = VALUES(gdp_growth),
            inflation = VALUES(inflation),
            unemployment = VALUES(unemployment),
            debt_gdp = VALUES(debt_gdp),
            military_spending = VALUES(military_spending)
    """

    total_remaining = len(all_iso_codes)
    print(f"Resuming sync for remaining {total_remaining} countries...")

    for index, iso3 in enumerate(all_iso_codes):
        # PROGRESS CALLBACK
        if progress_callback:
            progress_callback(index + 1, total_remaining, iso3)

        values_by_year = {}

        #ROBUST DATA FETCHING
        for field, indicator in INDICATORS.items():
            records = fetch_indicator(iso3, indicator)
            
            # Safety check: ensure 'records' is iterable before looping
            if not records: 
                continue

            for r in records:
                # Extra safety: Ensure 'r' is a dictionary and has required keys
                if isinstance(r, dict) and r.get("date") and r.get("value") is not None:
                    try:
                        year = int(r["date"])
                        values_by_year.setdefault(year, {})[field] = r["value"]
                    except ValueError:
                        continue

        # ATOMIC COMMIT
        if values_by_year:
            for year, metrics in values_by_year.items():
                cursor.execute(insert_sql, (
                    country_map.get(iso3), year, 
                    metrics.get("gdp"),
                    metrics.get("gdp_growth"), 
                    metrics.get("inflation"),
                    metrics.get("unemployment"), 
                    metrics.get("debt_gdp"),
                    metrics.get("military_spending")
                ))
            conn.commit() # Save specifically after this country finishes
            print(f"Synced {iso3}")
        else:
            # Even if no data, we 'commit' nothing but still sleep to respect API limits
            print(f"No data available for {iso3}")

        time.sleep(1.2) # Rate limit protection

    cursor.close()
    conn.close()
    print("Synchronization complete.")

if __name__ == "__main__":
    run()