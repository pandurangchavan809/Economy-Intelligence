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

# def execute_query(query, params=None):
#     """Executes any SQL command. Handles unread results using buffering."""
#     conn = get_connection()
#     # Adding buffered=True is the key fix for the "Unread result" error
#     cursor = conn.cursor(buffered=True) 
#     try:
#         cursor.execute(query, params)
        
#         # If it was a SELECT query, we must fetch to clear the unread results
#         if query.strip().upper().startswith("SELECT"):
#             result = cursor.fetchall()
#             conn.commit()
#             return result # Returns the rows found
            
#         conn.commit()
#         return cursor.rowcount # Returns number of rows updated/deleted
#     except Exception as e:
#         conn.rollback()
#         raise e
#     finally:
#         cursor.close()
#         conn.close()

def execute_query(query, params=None):
    conn = get_connection()
    # Adding buffered=True is the critical fix
    cursor = conn.cursor(buffered=True) 
    try:
        cursor.execute(query, params)
        # For SELECT queries, fetch all data to clear the buffer
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
            conn.commit()
            return result
        
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()