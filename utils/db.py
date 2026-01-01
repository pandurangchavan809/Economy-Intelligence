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
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()

def execute_query(query, params=None):
    """Executes INSERT, UPDATE, DELETE and returns row count."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit() # This saves the data to Aiven
        count = cursor.rowcount
        return count
    except Exception as e:
        conn.rollback() # This protects your data if there is an error
        raise e
    finally:
        cursor.close()
        conn.close()