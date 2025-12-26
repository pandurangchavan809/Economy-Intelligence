import pandas as pd
from database.connection import get_connection

WEO_FILE = "data/raw/WEO_Data.csv"
START_YEAR = 2005
END_YEAR = 2025


def run():
    print("🌍 Loading IMF WEO dataset (manual CSV)...")

    df = pd.read_csv(WEO_FILE, low_memory=False)

    # --- Normalize ONLY values, NOT column names ---
    df["COUNTRY"] = df["COUNTRY"].astype(str).str.strip()
    df["UNIT"] = df["UNIT"].astype(str).str.strip()
    df["SERIES_NAME"] = df["SERIES_NAME"].astype(str).str.strip().str.lower()

    # --- Robust filter for WORLD real GDP growth ---
    df_world = df[
        (df["COUNTRY"] == "World") &
        (df["UNIT"] == "Percent") &
        (df["SERIES_NAME"].str.contains("gross domestic product")) &
        (df["SERIES_NAME"].str.contains("constant prices"))
    ]

    if df_world.empty:
        raise Exception("World real GDP growth row not found in IMF WEO file")

    conn = get_connection()
    cursor = conn.cursor()

    for year in range(START_YEAR, END_YEAR + 1):
        year_col = str(year)
        if year_col not in df_world.columns:
            continue

        value = df_world[year_col].values[0]

        if pd.isna(value):
            continue

        cursor.execute(
            """
            INSERT INTO global_indicators (year, global_growth)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                global_growth = VALUES(global_growth)
            """,
            (year, float(value)),
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ IMF WEO global GDP growth loaded successfully (2005–2025)")


if __name__ == "__main__":
    run()
