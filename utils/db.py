# import pandas as pd
# from database.connection import get_connection


# def fetch_df(query, params=None):
#     conn = get_connection()
#     try:
#         # Using a context manager ensures the connection closes even if there's an error
#         df = pd.read_sql(query, conn, params=params)
#         return df
#     finally:
#         conn.close()

# # def fetch_df(query, params=None):
# #     conn = get_connection()
# #     df = pd.read_sql(query, conn, params=params)
# #     conn.close()
# #     return df

import pandas as pd
import mysql.connector
from database.connection import get_connection

def fetch_df(query, params=None):
    conn = get_connection()
    try:
        # We use standard pandas read_sql
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()

def execute_query(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()