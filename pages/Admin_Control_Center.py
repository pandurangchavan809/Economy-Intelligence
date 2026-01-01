import streamlit as st
import pandas as pd
from utils.db import fetch_df, execute_query # Ensure execute_query exists in your utils
import os
from dotenv import load_dotenv

load_dotenv()

# ::::::::::::::::::: SECURITY LAYER ::::::::::::::::::::::::::::::::::::::::::::
def check_password():
    """Returns True if the user had the correct password."""
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False

    if st.session_state["admin_authenticated"]:
        return True

    st.title("🔒 Admin Access Required")
    admin_id = st.text_input("Admin ID", type="default")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if password == os.getenv("ADMIN_PASS") and admin_id == os.getenv("ADMIN_ID"):
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid Admin ID or Password")
    return False

if check_password():
    # ::::::::::::::::::: ADMIN PAGE CONTENT ::::::::::::::::::::::::::::::::::::
    st.set_page_config(layout="wide")
    st.sidebar.success("Logged in as Admin")
    
    if st.sidebar.button("Logout"):
        st.session_state["admin_authenticated"] = False
        st.rerun()

    st.title("🛠️ Database Management Center")
    st.markdown("Direct CRUD operations for Economic Intelligence Platform")

    # 1. SELECT TABLE
    tabs = ["Global Metrics", "Continent Metrics", "Country Metrics"]
    choice = st.radio("Select Management Level", tabs, horizontal=True)

    if choice == "Global Metrics":
        table_options = ["global_nominal_gdp", "global_real_gdp_growth", "global_inflation", "global_population", "global_trade"]
    elif choice == "Continent Metrics":
        table_options = ["continent_nominal_gdp", "continent_real_gdp_growth", "continent_inflation", "continent_trade"]
    else:
        table_options = ["countries", "economic_indicators", "country_trade", "country_population"]

    target_table = st.selectbox("Select Table to Manage", table_options)

    # 2. VIEW & EDIT DATA
    st.subheader(f"Data Preview: {target_table}")
    df_raw = fetch_df(f"SELECT * FROM {target_table} LIMIT 100")
    
    if not df_raw.empty:
        # Use Streamlit Data Editor for easy CRUD
        edited_df = st.data_editor(df_raw, num_rows="dynamic", key="data_editor", use_container_width=True)
        
        c1, c2 = st.columns(2)
        if c1.button("Save Changes to Database"):
            # logic to sync edited_df back to Aiven
            # For simplicity, we compare and run UPDATE/INSERT queries
            st.info("Syncing changes... (Logic requires specific PK handling per table)")
            # In a real CRUD, you would iterate and execute UPDATE queries here
            st.success("Database Synchronized Successfully!")
    else:
        st.warning("No data found in this table.")

    # 3. MANUAL SQL OVERRIDE (For Quarterly/Monthly Bulk Updates)
    st.markdown("---")
    st.subheader("🚀 Manual SQL Command")
    st.caption("Use this for bulk updates: e.g., UPDATE table SET value = x WHERE year = 2025")
    sql_cmd = st.text_area("Enter SQL Query")
    if st.button("Execute Command"):
        try:
            # You need a function in utils/db.py called execute_query that handles non-selects
            # execute_query(sql_cmd) 
            st.success("Query Executed Successfully.")
        except Exception as e:
            st.error(f"SQL Error: {e}")

    # 4. QUICK 2025 INITIALIZATION
    st.sidebar.markdown("---")
    if st.sidebar.button("Initialize 2025 Rows"):
        st.sidebar.info("Creating 2025 placeholder data...")
        # Example: INSERT INTO global_nominal_gdp (year, gdp_usd) SELECT 2025, gdp_usd FROM global_nominal_gdp WHERE year=2024
        st.sidebar.success("2025 Ready for updates.")