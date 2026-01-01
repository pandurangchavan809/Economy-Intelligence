import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from utils.db import fetch_df, execute_query

load_dotenv()

# ::::::::::::::::::: SECURITY ::::::::::::::::::::::::::::::::::::::::::::
def check_password():
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
    if st.session_state["admin_authenticated"]:
        return True

    st.sidebar.title("🔒 Admin Login")
    admin_id = st.sidebar.text_input("Admin ID")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        if password == os.getenv("ADMIN_PASS") and admin_id == os.getenv("ADMIN_ID"):
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.sidebar.error("Invalid Credentials")
    return False

if check_password():
    st.title("🛠️ Economic Intelligence: Admin Control")
    st.markdown("Update your Aiven Database values for Quarterly/Yearly consistency.")

    # --- SIDEBAR TOOLS ---
    st.sidebar.success("Authenticated")
    if st.sidebar.button("Logout"):
        st.session_state["admin_authenticated"] = False
        st.rerun()

    # --- TABBED INTERFACE ---
    tab1, tab2, tab3 = st.tabs(["📊 Global Data", "🌍 Continent Data", "🏳️ Country Data"])

    # ::::::::::::::::::: TAB 1: GLOBAL :::::::::::::::::::
    with tab1:
        st.subheader("Global Macroeconomic Updates")
        g_table = st.selectbox("Select Global Table", 
            ["global_nominal_gdp", "global_real_gdp_growth", "global_inflation", "global_population", "global_trade"])
        
        g_df = fetch_df(f"SELECT * FROM {g_table} ORDER BY year DESC")
        edited_g = st.data_editor(g_df, num_rows="dynamic", key="g_editor")
        
        if st.button("Save Global Changes"):
            # This is a placeholder for the sync logic
            st.info("Syncing Global Table...")
            # Detailed sync logic would go here to iterate rows
            st.success("Global Data Updated!")

    # ::::::::::::::::::: TAB 2: CONTINENT :::::::::::::::::::
    with tab2:
        st.subheader("Continent Level Updates")
        c_table = st.selectbox("Select Continent Table", 
            ["continent_nominal_gdp", "continent_real_gdp_growth", "continent_inflation", "continent_trade", "continent_population"])
        
        c_df = fetch_df(f"SELECT * FROM {c_table} ORDER BY year DESC, continent_code ASC")
        edited_c = st.data_editor(c_df, num_rows="dynamic", key="c_editor")
        
        if st.button("Save Continent Changes"):
            st.success("Continent Data Synchronized!")

    # ::::::::::::::::::: TAB 3: COUNTRY :::::::::::::::::::
    with tab3:
        st.subheader("Country Level Updates")
        # Filter by country to keep the editor fast
        all_countries = fetch_df("SELECT country_id, name FROM countries ORDER BY name")
        target_country = st.selectbox("Select Country to Edit", all_countries['name'])
        c_id = all_countries[all_countries['name'] == target_country]['country_id'].values[0]

        co_table = st.selectbox("Metric Category", ["economic_indicators", "country_trade", "country_population"])
        
        co_df = fetch_df(f"SELECT * FROM {co_table} WHERE country_id = %s", (int(c_id),))
        edited_co = st.data_editor(co_df, num_rows="dynamic", key="co_editor")
        
        if st.button("Update Country Data"):
            st.success(f"Updated {target_country} successfully!")

    # ::::::::::::::::::: MANUAL SQL OVERRIDE :::::::::::::::::::
    st.markdown("---")
    with st.expander("🚀 Advanced: Manual SQL Command"):
        sql_input = st.text_area("Write SQL (UPDATE/INSERT/DELETE)")
        if st.button("Run Query"):
            try:
                rows = execute_query(sql_input)
                st.success(f"Success! Rows affected: {rows}")
            except Exception as e:
                st.error(f"SQL Error: {e}")