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
from database.connection import get_connection

def fetch_df(query, params=None):
    """Fetches data from the database and returns it as a DataFrame."""
    conn = get_connection()
    try:
        # Using a context manager ensures the connection closes even if there's an error
        df = pd.read_sql(query, conn, params=params)
        return df
    finally:
        conn.close()

def execute_query(query, params=None):
    """Executes a command that doesn't return rows (INSERT, UPDATE, DELETE)."""
    conn = get_connection() 
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit() # Mandatory for saving changes
        return cursor.rowcount # Returns the number of affected rows
    except Exception as e:
        print(f"Error executing query: {e}")
        conn.rollback() # Undo changes if an error occurs
        raise e
    finally:
        cursor.close()
        conn.close()