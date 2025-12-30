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


# import os
# import mysql.connector
# import streamlit as st # Import streamlit to access secrets

# def get_connection():
#     # On Streamlit Cloud, st.secrets works like environment variables
#     return mysql.connector.connect(
#         host=st.secrets["DB_HOST"],
#         user=st.secrets["DB_USER"],
#         password=st.secrets["DB_PASSWORD"],
#         database=st.secrets["DB_NAME"],
#         port=int(st.secrets["DB_PORT"]) # Aiven requires port 22611
#     )



import streamlit as st
import mysql.connector

# Use st.cache_resource to keep the connection alive but refresh it regularly
@st.cache_resource(ttl=3600) # Refreshes every 1 hour to prevent stale connections
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            port=int(st.secrets["DB_PORT"]),
            connect_timeout=10 # Increase timeout to allow Aiven to wake up
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None
    



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



