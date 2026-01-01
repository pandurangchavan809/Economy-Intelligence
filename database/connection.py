# # import os
# # import mysql.connector
# # from dotenv import load_dotenv

# # load_dotenv()

# # def get_connection():
# #     return mysql.connector.connect(
# #         host=os.getenv("DB_HOST"),
# #         user=os.getenv("DB_USER"),
# #         password=os.getenv("DB_PASSWORD"),
# #         database=os.getenv("DB_NAME")
# #     )

import os
import mysql.connector
import streamlit as st

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets["DB_PORT"]),
            # --- MANDATORY FOR AIVEN ---
            ssl_disabled=False  
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error connecting to Aiven: {err}")
        return None
    
