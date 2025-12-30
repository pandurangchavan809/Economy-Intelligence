# import os
# import mysql.connector
# from dotenv import load_dotenv

# load_dotenv()

# def get_connection():
#     return mysql.connector.connect(
#         host=os.getenv("DB_HOST"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#         database=os.getenv("DB_NAME")
#     )


import os
import mysql.connector
import streamlit as st # Import streamlit to access secrets

def get_connection():
    # On Streamlit Cloud, st.secrets works like environment variables
    return mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        port=int(st.secrets["DB_PORT"]) # Aiven requires port 22611
    )


# import os
# import mysql.connector
# import streamlit as st
# from dotenv import load_dotenv

# # Try to load local .env, but it won't exist on Streamlit Cloud (which is fine)
# load_dotenv()

# def get_connection():
#     # Streamlit Cloud priority: check st.secrets first
#     if "DB_HOST" in st.secrets:
#         return mysql.connector.connect(
#             host=st.secrets["DB_HOST"],
#             user=st.secrets["DB_USER"],
#             password=st.secrets["DB_PASSWORD"],
#             database=st.secrets["DB_NAME"],
#             port=int(st.secrets["DB_PORT"])
#         )
#     # Local priority: check .env file
#     else:
#         return mysql.connector.connect(
#             host=os.getenv("DB_HOST"),
#             user=os.getenv("DB_USER"),
#             password=os.getenv("DB_PASSWORD"),
#             database=os.getenv("DB_NAME")
#         )



