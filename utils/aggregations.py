from utils.db import fetch_df

def get_world_nominal_gdp(year=2024):
    q = """
    SELECT gdp_usd
    FROM global_nominal_gdp
    WHERE year = %s
    """
    df = fetch_df(q, (year,))
    return float(df.iloc[0]["gdp_usd"])


def get_world_real_growth(year=2025):
    q = """
    SELECT real_growth
    FROM global_real_gdp_growth
    WHERE year = %s
    """
    df = fetch_df(q, (year,))
    return float(df.iloc[0]["real_growth"])


def get_world_inflation(year=2025):
    q = """
    SELECT inflation
    FROM global_inflation
    WHERE year = %s
    """
    df = fetch_df(q, (year,))
    return float(df.iloc[0]["inflation"])

def get_world_population(year):
    q = "SELECT population FROM global_population WHERE year = %s"
    return float(fetch_df(q, (year,)).iloc[0]["population"])


def get_world_population_growth(year):
    q = "SELECT growth_rate FROM global_population_growth WHERE year = %s"
    return float(fetch_df(q, (year,)).iloc[0]["growth_rate"])


def get_global_trade(year):
    q = """
    SELECT exports_usd, imports_usd, trade_balance_usd
    FROM global_trade
    WHERE year = %s
    """
    df = fetch_df(q, (year,))
    return (
        float(df["exports_usd"].iloc[0]),
        float(df["imports_usd"].iloc[0]),
        float(df["trade_balance_usd"].iloc[0]),
    )



### contineunt
def get_all_continent_base_gdp(year):
    q = """
    SELECT continent_code, gdp_usd
    FROM continent_nominal_gdp
    WHERE year = %s
    """
    return fetch_df(q, (year,))


def get_all_continent_growth(year):
    q = """
    SELECT continent_code, real_growth
    FROM continent_real_gdp_growth
    WHERE year = %s
    """
    return fetch_df(q, (year,))


def get_all_continent_inflation(year):
    q = """
    SELECT continent_code, inflation
    FROM continent_inflation
    WHERE year = %s
    """
    return fetch_df(q, (year,))


def get_all_continent_population(year):
    q = """
    SELECT continent_code, population
    FROM continent_population
    WHERE year = %s
    """
    return fetch_df(q, (year,))


def get_all_continent_trade(year):
    q = """
    SELECT continent_code, exports_usd, imports_usd, trade_balance_usd
    FROM continent_trade
    WHERE year = %s
    """
    return fetch_df(q, (year,))


def get_continent_world_share(year):
    q = """
    SELECT continent_code, continent_name, pct_of_world
    FROM continent_world_gdp_share
    WHERE year = %s
    """
    return fetch_df(q, (year,))


def get_top_countries_by_continent(continent_code, year, limit=7):
    q = """
    SELECT
        country,
        gdp,
        pct_of_continent
    FROM continent_country_gdp_share
    WHERE continent_code = %s
      AND year = %s
    ORDER BY gdp DESC
    LIMIT %s
    """
    return fetch_df(q, (continent_code, year, limit))


## contineunt
import pandas as pd
from utils.db import fetch_df


def get_all_continent_core(gdp_year, trade_year=None):
    """
    gdp_year   → GDP / population base year
    trade_year → trade year (defaults to gdp_year)
    """

    if trade_year is None:
        trade_year = gdp_year

    return fetch_df(
        """
        SELECT
            c.code AS continent_code,
            c.name AS continent_name,
            g.gdp_usd,
            p.population,
            rg.real_growth,
            i.inflation,
            t.trade_balance_usd
        FROM continents c
        LEFT JOIN continent_nominal_gdp g
            ON g.continent_code = c.code AND g.year = %s
        LEFT JOIN continent_population p
            ON p.continent_code = c.code AND p.year = %s
        LEFT JOIN continent_real_gdp_growth rg
            ON rg.continent_code = c.code
        LEFT JOIN continent_inflation i
            ON i.continent_code = c.code
        LEFT JOIN continent_trade t
            ON t.continent_code = c.code AND t.year = %s
        WHERE c.code <> 'AN'
        ORDER BY g.gdp_usd DESC
        """,
        params=(gdp_year, gdp_year, trade_year),
    )



def get_continent_detail(code, year):
    return fetch_df(
        """
        SELECT
            c.name AS continent_name,
            g.gdp_usd,
            p.population,
            gpc.gdp_per_capita_usd,
            rg.real_growth,
            i.inflation
        FROM continents c
        LEFT JOIN continent_nominal_gdp g
            ON g.continent_code = c.code AND g.year = %s
        LEFT JOIN continent_population p
            ON p.continent_code = c.code AND p.year = %s
        LEFT JOIN continent_gdp_per_capita gpc
            ON gpc.continent_code = c.code AND gpc.year = %s
        LEFT JOIN continent_real_gdp_growth rg
            ON rg.continent_code = c.code
        LEFT JOIN continent_inflation i
            ON i.continent_code = c.code
        WHERE c.code = %s
        """,
        params=(year, year, year, code),
    )





