# utils/sql_helpers.py
from typing import Optional, Tuple
from utils.db import fetch_df

def table_has_column(table_name: str, column_name: str) -> bool:
    """
    Returns True if `information_schema` shows the column for the current database.
    Uses the same DB connection as fetch_df.
    """
    q = """
    SELECT COUNT(*) AS cnt
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = %s
      AND COLUMN_NAME = %s
    """
    df = fetch_df(q, (table_name, column_name))
    return int(df.iloc[0, 0]) > 0


def get_country_keys(country_id: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (iso3, country_name) for a given country_id using countries table.
    If row missing, returns (None, None).
    """
    df = fetch_df("SELECT iso3, name FROM countries WHERE country_id = %s LIMIT 1", (country_id,))
    if df.empty:
        return None, None
    return df.iloc[0]["iso3"], df.iloc[0]["name"]
