import os
import requests
from dotenv import load_dotenv
from database.connection import get_connection

load_dotenv()

API_KEY = os.getenv("COUNTRYLAYER_API_KEY")
BASE_URL = "http://api.countrylayer.com/v2/all"

if not API_KEY:
    raise Exception("COUNTRYLAYER_API_KEY not found. Check .env file.")

print("Using API key:", API_KEY[:4], "****")


def fetch_countries():
    params = {"access_key": API_KEY}
    response = requests.get(BASE_URL, params=params, timeout=30)

    print("Status code:", response.status_code)

    try:
        data = response.json()
    except Exception:
        raise Exception("Invalid JSON response from CountryLayer")

    # CountryLayer error handling
    if isinstance(data, dict) and data.get("success") is False:
        error = data.get("error", {})
        raise Exception(
            f"CountryLayer API error: {error.get('code')} - {error.get('info')}"
        )

    if not isinstance(data, list):
        raise Exception("Unexpected CountryLayer response format")

    return data



def insert_countries(countries):
    conn = get_connection()
    try:
        # debug: show which database we're connected to
        print("DB connected to:", getattr(conn, 'database', None))
    except Exception:
        pass
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO countries
        (name, iso2, iso3, capital, continent, region, population, flag_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            population = VALUES(population),
            capital = VALUES(capital),
            region = VALUES(region),
            flag_url = VALUES(flag_url)
    """

    inserted = 0

    for c in countries:
        try:
            population = c.get("population")
            # countrylayer/restcountries sometimes use different keys for flag(s)
            flag = c.get("flag") or c.get("flags") or None

            # debug: print values that will be inserted for troubleshooting
            if population is None or flag is None:
                print(f"⚠️ Missing data for {c.get('name')}: population={population} flag={flag}")

            data = (
                c.get("name"),
                c.get("alpha2Code"),
                c.get("alpha3Code"),
                c.get("capital"),
                c.get("region"),
                c.get("subregion"),
                population,
                flag,
            )

            cursor.execute(insert_query, data)
            inserted += 1

        except Exception as e:
            # include the country name and the full exception for easier debugging
            print(f"Skipped {c.get('name')}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Inserted / updated {inserted} countries")


def run():
    print("🌍 Fetching countries from CountryLayer...")
    countries = fetch_countries()
    print(f"📦 Retrieved {len(countries)} records")

    insert_countries(countries)
    print("🎯 CountryLayer ETL completed successfully")


if __name__ == "__main__":
    run()
