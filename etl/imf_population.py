import pandas as pd
from database.connection import get_connection

WEO_PATH = "data/raw/WEO_Data.csv"

def run(years=(2024, 2025)):
    df = pd.read_csv(WEO_PATH, low_memory=False)

    # IMF population series
    df = df[df["SERIES_CODE"].str.endswith(".LP.A", na=False)]

    conn = get_connection()
    cur = conn.cursor()

    for year in years:
        if str(year) not in df.columns:
            continue

        year_df = df[["COUNTRY", str(year)]].dropna()
        year_df[str(year)] = (year_df[str(year)] * 1_000_000).astype("int64")

        for _, row in year_df.iterrows():
            cur.execute(
                """
                INSERT INTO country_population (country_id, year, population, source)
                SELECT country_id, %s, %s, 'IMF_WEO'
                FROM countries
                WHERE name = %s
                ON DUPLICATE KEY UPDATE
                    population = VALUES(population),
                    source = 'IMF_WEO'
                """,
                (year, int(row[str(year)]), row["COUNTRY"]),
            )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ IMF population ETL completed")

if __name__ == "__main__":
    run()
