import pandas as pd
from database.connection import get_connection

WEO_PATH = "data/raw/WEO_Data.csv"


def load_country_continent_map(conn):
    """Return dataframe with iso3 (upper) and continent_code"""
    df = pd.read_sql(
        """
        SELECT iso3, continent_code
        FROM countries
        WHERE iso3 IS NOT NULL
          AND continent_code IS NOT NULL
        """,
        conn,
    )
    df["iso3"] = df["iso3"].str.upper()
    return df


def load_continent_from_weo_by_token(series_token, table, value_col, year, agg="sum"):
    """
    Robust loader: extracts the middle token of SERIES_CODE (ISO3.SERIESTOKEN.*)
    and aggregates by continent using the countries table mapping.
    series_token example: 'NGDPD', 'NGDP_RPCH', 'PCPIPCH'
    """
    conn = get_connection()
    cur = conn.cursor()

    country_map = load_country_continent_map(conn)

    weo = pd.read_csv(WEO_PATH, low_memory=False)

    # Ensure SERIES_CODE exists
    if "SERIES_CODE" not in weo.columns:
        raise RuntimeError("WEO CSV missing SERIES_CODE column")

    # Extract token and iso3
    # Example SERIES_CODE: 'HND.NGDPPC.A' -> iso3='HND', token='NGDPPC'
    split = weo["SERIES_CODE"].str.split(".", expand=True)
    weo["iso3"] = split.iloc[:, 0].str.upper()
    weo["token"] = split.iloc[:, 1].astype(str).str.upper()

    # Verify year column exists
    if str(year) not in weo.columns:
        raise RuntimeError(f"WEO CSV missing column for year {year}")

    # Filter by token and available value
    subset = weo[(weo["token"] == series_token.upper()) & weo[str(year)].notna()]

    # If nothing matched by token, try a text-based fallback using SERIES_NAME / INDICATOR heuristics
    if subset.empty:
        # simple fallback map for common series tokens -> indicator keywords
        fallback_map = {
            "NGDPD": ["gross domestic product", "current prices", "current"],
            "NGDP_RPCH": ["real GDP growth", "real GDP", "growth"],
            "PCPIPCH": ["inflation", "consumer prices", "cpi"],
        }
        keywords = fallback_map.get(series_token.upper(), [])
        if keywords:
            # search INDICATOR and SERIES_NAME columns if available
            text_cols = [c for c in ("INDICATOR", "SERIES_NAME") if c in weo.columns]
            if text_cols:
                mask = False
                for kw in keywords:
                    for col in text_cols:
                        mask = mask | weo[col].str.contains(kw, case=False, na=False)
                subset = weo[mask & weo[str(year)].notna()]

    if subset.empty:
        # Provide helpful debugging info in the error
        tokens_available = sorted(weo["token"].dropna().unique().tolist())
        raise RuntimeError(
            f"No IMF data matched for token '{series_token}' and year {year}.\n"
            f"Tokens present in WEO file (sample): {tokens_available[:20]}...\n"
            f"Check whether your WEO file contains the expected series tokens."
        )

    subset = subset[["iso3", str(year)]].rename(columns={str(year): "value"})

    # Merge with country map
    merged = subset.merge(country_map, on="iso3", how="inner")

    if merged.empty:
        iso3_present = sorted(subset["iso3"].unique().tolist())[:20]
        raise RuntimeError(
            f"No ISO3 matches between WEO file and countries table for series '{series_token}' {year}.\n"
            f"ISO3s found in WEO sample: {iso3_present}...\n"
            f"Make sure countries.iso3 uses standard ISO3 codes that match WEO."
        )

    # aggregate
    if agg == "sum":
        result = merged.groupby("continent_code")["value"].sum()
    elif agg == "mean":
        result = merged.groupby("continent_code")["value"].mean()
    else:
        raise ValueError("Invalid aggregation type (use 'sum' or 'mean')")

    # write to table (replace year rows)
    cur.execute(f"DELETE FROM {table} WHERE year = %s", (year,))
    for continent, val in result.items():
        cur.execute(
            f"INSERT INTO {table} (continent_code, year, {value_col}) VALUES (%s, %s, %s)",
            (continent, year, float(val)),
        )

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ {table} loaded for {year}")


def load_continent_population(year=2024):
    conn = get_connection()
    cur = conn.cursor()

    country_map = pd.read_sql(
        """
        SELECT iso3, continent_code
        FROM countries
        WHERE iso3 IS NOT NULL
          AND continent_code IS NOT NULL
        """,
        conn,
    )

    weo = pd.read_csv(WEO_PATH, low_memory=False)

    # ✅ CORRECT population series filter
    weo = weo[
        weo["SERIES_CODE"].str.endswith(".LP.A", na=False)
        & weo[str(year)].notna()
    ][["SERIES_CODE", str(year)]]

    if weo.empty:
        raise RuntimeError(f"No IMF population data for {year}")

    weo["iso3"] = weo["SERIES_CODE"].str.split(".").str[0]
    weo["population"] = weo[str(year)] * 1_000_000  # millions → persons

    merged = weo.merge(country_map, on="iso3", how="inner")

    if merged.empty:
        raise RuntimeError("No country–continent population matches")

    cur.execute("DELETE FROM continent_population WHERE year = %s", (year,))

    for continent, pop in (
        merged.groupby("continent_code")["population"].sum().items()
    ):
        cur.execute(
            """
            INSERT INTO continent_population (continent_code, year, population)
            VALUES (%s, %s, %s)
            """,
            (continent, year, int(pop)),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ continent_population loaded from IMF WEO")

def load_continent_population_growth_manual(year=2025):
    data = {
        "AF": 2.41,
        "AS": 0.82,
        "EU": -0.12,
        "NA": 0.63,
        "SA": 0.94,
        "OC": 1.08,
    }

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM continent_population_growth WHERE year = %s",
        (year,)
    )

    for continent, growth in data.items():
        cur.execute(
            """
            INSERT INTO continent_population_growth
            (continent_code, year, growth_rate)
            VALUES (%s, %s, %s)
            """,
            (continent, year, growth),
        )

    conn.commit()
    cur.close()
    conn.close()

    print("✅ continent_population_growth inserted manually")



if __name__ == "__main__":
    # ----- Nominal GDP (sum per continent) -----
    load_continent_from_weo_by_token("NGDPD", "continent_nominal_gdp", "gdp_usd", 2024, "sum")

    # ----- Real GDP growth (mean per continent) -----
    load_continent_from_weo_by_token("NGDP_RPCH", "continent_real_gdp_growth", "real_growth", 2025, "mean")

    # ----- Inflation (mean per continent) -----
    load_continent_from_weo_by_token("PCPIPCH", "continent_inflation", "inflation", 2025, "mean")

    # ----- Population -----
    load_continent_population(2024)

    ## ------growth population------
    load_continent_population_growth_manual(year=2025)
