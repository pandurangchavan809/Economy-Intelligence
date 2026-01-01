# import requests
# import time
# from database.connection import get_connection

# BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
# START_YEAR = 2004
# END_YEAR = 2025

# INDICATORS = {
#     "gdp": "NY.GDP.MKTP.CD",
#     "gdp_growth": "NY.GDP.MKTP.KD.ZG",
#     "inflation": "FP.CPI.TOTL.ZG",
#     "unemployment": "SL.UEM.TOTL.ZS",
#     "military_spending": "MS.MIL.XPND.CD",
#     "debt_gdp": "GC.DOD.TOTL.GD.ZS"
# }

# TOP_COUNTRIES = [
#     "USA", "CHN", "JPN", "DEU", "IND",
#     "GBR", "FRA", "ITA", "BRA", "CAN",
#     "RUS", "KOR", "AUS", "ESP", "MEX"
# ]



# def fetch_indicator(country, indicator, retries=3):
#     url = BASE_URL.format(country=country, indicator=indicator)
#     params = {
#         "format": "json",
#         "per_page": 1000,
#         "date": f"{START_YEAR}:{END_YEAR}"
#     }

#     for attempt in range(1, retries + 1):
#         try:
#             r = requests.get(url, params=params, timeout=60)
#             data = r.json()

#             if not isinstance(data, list) or len(data) < 2:
#                 return []

#             return data[1]

#         except requests.exceptions.ReadTimeout:
#             print(f"⏳ Timeout for {country}-{indicator} (attempt {attempt})")
#             time.sleep(2 * attempt)

#         except Exception as e:
#             print(f"⚠️ Error for {country}-{indicator}: {e}")
#             return []

#     print(f"❌ Failed after retries: {country}-{indicator}")
#     return []



# def run():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)

#     cursor.execute("SELECT country_id, iso3 FROM countries")
#     country_map = {row["iso3"]: row["country_id"] for row in cursor.fetchall()}

#     insert_sql = """
#         INSERT INTO economic_indicators
#         (country_id, year, gdp, gdp_growth, inflation,
#          unemployment, debt_gdp, military_spending)
#         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
#         ON DUPLICATE KEY UPDATE
#             gdp = VALUES(gdp),
#             gdp_growth = VALUES(gdp_growth),
#             inflation = VALUES(inflation),
#             unemployment = VALUES(unemployment),
#             debt_gdp = VALUES(debt_gdp),
#             military_spending = VALUES(military_spending)
#     """

#     for iso3 in TOP_COUNTRIES:
#         print(f"📊 Processing {iso3}")
#         values_by_year = {}
#         time.sleep(1)


#         for field, indicator in INDICATORS.items():
#             records = fetch_indicator(iso3, indicator)
#             for r in records:
#                 year = int(r["date"])
#                 values_by_year.setdefault(year, {})[field] = r["value"]

#         for year, metrics in values_by_year.items():
#             cursor.execute(
#                 insert_sql,
#                 (
#                     country_map.get(iso3),
#                     year,
#                     metrics.get("gdp"),
#                     metrics.get("gdp_growth"),
#                     metrics.get("inflation"),
#                     metrics.get("unemployment"),
#                     metrics.get("debt_gdp"),
#                     metrics.get("military_spending"),
#                 )
#             )

#     conn.commit()
#     cursor.close()
#     conn.close()
#     print("✅ World Bank ETL completed successfully")


# if __name__ == "__main__":
#     run()






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
            r = requests.get(url, params=params, timeout=60)
            data = r.json()

            # If the API returns an error message or empty data
            if not isinstance(data, list) or len(data) < 2:
                return []

            return data[1]

        except requests.exceptions.ReadTimeout:
            print(f"⏳ Timeout for {country}-{indicator} (attempt {attempt})")
            time.sleep(2 * attempt)
        except Exception as e:
            print(f"⚠️ Error for {country}-{indicator}: {e}")
            return []

    print(f"❌ Failed after retries: {country}-{indicator}")
    return []

def run():
    conn = get_connection()
    if not conn:
        print("❌ Could not establish database connection.")
        return

    cursor = conn.cursor(dictionary=True)

    # 1. Fetch ALL countries from your Aiven DB
    print("🌍 Fetching country list from Aiven...")
    cursor.execute("SELECT country_id, iso3 FROM countries WHERE iso3 IS NOT NULL")
    country_rows = cursor.fetchall()
    
    # Map ISO3 -> country_id
    country_map = {row["iso3"]: row["country_id"] for row in country_rows}
    all_iso_codes = list(country_map.keys())

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

    total_countries = len(all_iso_codes)
    print(f"🚀 Starting ingestion for {total_countries} countries...")

    for index, iso3 in enumerate(all_iso_codes):
        # Validation: Skip if iso3 is invalid or looks like a placeholder
        if not iso3 or len(iso3) != 3:
            print(f"⏩ Skipping invalid ISO3: {iso3}")
            continue

        print(f"📊 [{index+1}/{total_countries}] Processing {iso3}")
        values_by_year = {}

        # Fetch indicators for this specific country
        for field, indicator in INDICATORS.items():
            records = fetch_indicator(iso3, indicator)
            
            # If World Bank returns no data for this ISO3/Indicator, move on
            if not records:
                continue

            for r in records:
                # Basic validation for year and data point
                if r.get("date") and r.get("value") is not None:
                    year = int(r["date"])
                    values_by_year.setdefault(year, {})[field] = r["value"]

        # Insert data into Aiven
        if values_by_year:
            for year, metrics in values_by_year.items():
                cursor.execute(
                    insert_sql,
                    (
                        country_map.get(iso3),
                        year,
                        metrics.get("gdp"),
                        metrics.get("gdp_growth"),
                        metrics.get("inflation"),
                        metrics.get("unemployment"),
                        metrics.get("debt_gdp"),
                        metrics.get("military_spending"),
                    )
                )
            # Commit after each country to ensure data is saved incrementally
            conn.commit()
            print(f"✅ Saved {iso3}")
        else:
            print(f"ℹ️ No data found for {iso3} in World Bank records.")

        # --- THE BREATH ---
        # 1.5 second delay prevents IP blocking and rate limiting
        time.sleep(1.5)

    cursor.close()
    conn.close()
    print("🏁 Full World Bank ETL completed successfully!")

if __name__ == "__main__":
    run()