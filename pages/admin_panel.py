# import streamlit as st
# import pandas as pd
# from utils.db import fetch_df, execute_query

# # ::::::::::::::::::: SECURITY ::::::::::::::::::::::::::::::::::::::::::::
# def check_password():
#     if "admin_authenticated" not in st.session_state:
#         st.session_state["admin_authenticated"] = False
    
#     if st.session_state["admin_authenticated"]:
#         return True

#     st.sidebar.title("🔒 Admin Login")
#     admin_id = st.sidebar.text_input("Admin ID")
#     password = st.sidebar.text_input("Password", type="password")
    
#     if st.sidebar.button("Login"):
#         # Access secrets directly from st.secrets (defined in Streamlit Cloud Dashboard)
#         try:
#             if password == st.secrets["ADMIN_PASS"] and admin_id == st.secrets["ADMIN_ID"]:
#                 st.session_state["admin_authenticated"] = True
#                 st.rerun()
#             else:
#                 st.sidebar.error("Invalid Credentials")
#         except KeyError:
#             st.sidebar.error("Secrets not configured! Add ADMIN_ID and ADMIN_PASS to Streamlit Secrets.")
#     return False

# if check_password():
#     st.title("🛠️ Economic Intelligence: Admin Control")
#     st.markdown("Update your Aiven Database values for Quarterly/Yearly consistency.")

#     # --- SIDEBAR TOOLS ---
#     st.sidebar.success("Authenticated")
#     if st.sidebar.button("Logout"):
#         st.session_state["admin_authenticated"] = False
#         st.rerun()

#     # --- TABBED INTERFACE ---
#     tab1, tab2, tab3 = st.tabs(["📊 Global Data", "🌍 Continent Data", "🏳️ Country Data"])

#     # ::::::::::::::::::: TAB 1: GLOBAL :::::::::::::::::::
#     with tab1:
#         st.subheader("Global Macroeconomic Updates")
#         g_table = st.selectbox("Select Global Table", 
#             ["global_nominal_gdp", "global_real_gdp_growth", "global_inflation", "global_population", "global_trade"])
        
#         g_df = fetch_df(f"SELECT * FROM {g_table} ORDER BY year DESC")
#         edited_g = st.data_editor(g_df, num_rows="dynamic", key="g_editor")
        
#         if st.button("Save Global Changes"):
#             st.info("Global data manual override required for bulk sync. Use the SQL command below for specific updates.")

#     # ::::::::::::::::::: TAB 2: CONTINENT :::::::::::::::::::
#     with tab2:
#         st.subheader("Continent Level Updates")
#         c_table = st.selectbox("Select Continent Table", 
#             ["continent_nominal_gdp", "continent_real_gdp_growth", "continent_inflation", "continent_trade", "continent_population"])
        
#         c_df = fetch_df(f"SELECT * FROM {c_table} ORDER BY year DESC, continent_code ASC")
#         edited_c = st.data_editor(c_df, num_rows="dynamic", key="c_editor")
        
#         if st.button("Save Continent Changes"):
#             st.success("Changes captured. Note: Direct table-sync logic is best handled via SQL below for large datasets.")

#     # ::::::::::::::::::: TAB 3: COUNTRY :::::::::::::::::::
#     with tab3:
#         st.subheader("Country Level Updates")
#         # Fetch country list for the dropdown
#         try:
#             all_countries = fetch_df("SELECT country_id, name FROM countries ORDER BY name")
#             target_country = st.selectbox("Select Country to Edit", all_countries['name'])
#             c_id = all_countries[all_countries['name'] == target_country]['country_id'].values[0]

#             co_table = st.selectbox("Metric Category", ["economic_indicators", "country_trade", "country_population"])
            
#             co_df = fetch_df(f"SELECT * FROM {co_table} WHERE country_id = %s", (int(c_id),))
#             edited_co = st.data_editor(co_df, num_rows="dynamic", key="co_editor")
            
#             if st.button("Update Country Data"):
#                 st.success(f"Validated updates for {target_country}.")
#         except Exception as e:
#             st.error(f"Could not load country list: {e}")

#     # ::::::::::::::::::: MANUAL SQL OVERRIDE (The Core CRUD Tool) :::::::::::::::::::
#     st.markdown("---")
#     st.subheader("🚀 Powerful SQL Command Center")
#     st.caption("Use this to Add, Update, or Delete specific rows in your Aiven Database.")
    
#     with st.expander("Show SQL Examples"):
#         st.code("-- Update 2025 GDP Growth\nUPDATE global_real_gdp_growth SET real_growth = 3.2 WHERE year = 2025;")
#         st.code("-- Add new country trade data\nINSERT INTO country_trade (country_id, exports_usd, year) VALUES (10, 500000000, 2025);")

#     sql_input = st.text_area("Write SQL Query", height=150, placeholder="UPDATE ... SET ... WHERE ...")
    
#     if st.button("Execute Query"):
#         if sql_input:
#             try:
#                 rows_affected = execute_query(sql_input)
#                 st.success(f"Query Executed! Rows affected: {rows_affected}")
#                 # Clear cache if you have it implemented to show new data immediately
#             except Exception as e:
#                 st.error(f"SQL Error: {e}")
#         else:
#             st.warning("Please enter a query first.")

#     # ---------------- FOOTER ----------------
#     st.markdown("---")
#     st.caption("© Admin Panel · Economic Intelligence Platform")


import streamlit as st
import pandas as pd
from utils.db import fetch_df, execute_query

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
        try:
            if password == st.secrets["ADMIN_PASS"] and admin_id == st.secrets["ADMIN_ID"]:
                st.session_state["admin_authenticated"] = True
                st.rerun()
            else:
                st.sidebar.error("Invalid Credentials")
        except KeyError:
            st.sidebar.error("Secrets not configured! Add ADMIN_ID and ADMIN_PASS to Streamlit Secrets.")
    return False

if check_password():
    st.title("🛠️ Economic Intelligence: Admin Control")
    st.markdown("Update your Aiven Database values for Quarterly/Yearly consistency.")

    # --- SIDEBAR TOOLS ---
    st.sidebar.success("Authenticated")
    if st.sidebar.button("Logout"):
        st.session_state["admin_authenticated"] = False
        st.rerun()

    # DYNAMIC METADATA: Get all tables and views available in the database
    try:
        # 'SHOW FULL TABLES' returns two columns: table name and 'BASE TABLE' or 'VIEW'
        tables_meta = fetch_df("SHOW FULL TABLES")
        all_tables_list = tables_meta.iloc[:, 0].tolist()
    except Exception as e:
        st.error(f"Error fetching database metadata: {e}")
        all_tables_list = []

    # --- TABBED INTERFACE ---
    tab1, tab2, tab3 = st.tabs(["📊 Global Data", "🌍 Continent Data", "🏳️ Country Data"])

    # ::::::::::::::::::: TAB 1: GLOBAL :::::::::::::::::::
    with tab1:
        st.subheader("Global Macroeconomic Updates")
        # Filter list to only show global-prefixed tables
        global_tables = [t for t in all_tables_list if t.startswith('global_')]
        g_table = st.selectbox("Select Global Table", global_tables if global_tables else all_tables_list)
        
        g_df = fetch_df(f"SELECT * FROM {g_table} ORDER BY year DESC")
        edited_g = st.data_editor(g_df, num_rows="dynamic", key="g_editor")
        
        if st.button("Save Global Changes"):
            st.info("Direct synchronization logic is best handled via the SQL Command Center below for specific row updates.")

    # ::::::::::::::::::: TAB 2: CONTINENT :::::::::::::::::::
    with tab2:
        st.subheader("Continent Level Updates")
        continent_tables = [t for t in all_tables_list if t.startswith('continent_')]
        c_table = st.selectbox("Select Continent Table", continent_tables if continent_tables else all_tables_list)
        
        c_df = fetch_df(f"SELECT * FROM {c_table} ORDER BY year DESC")
        edited_c = st.data_editor(c_df, num_rows="dynamic", key="c_editor")
        
        if st.button("Save Continent Changes"):
            st.success("Changes captured in editor. Use SQL below to commit specific data points.")

    # ::::::::::::::::::: TAB 3: COUNTRY :::::::::::::::::::
    with tab3:
        st.subheader("Country Level Updates")
        try:
            # FIX: Fetching ALL countries without any LIMIT
            all_countries = fetch_df("SELECT country_id, name FROM countries ORDER BY name")
            target_country = st.selectbox("Select Country to Edit", all_countries['name'])
            c_id = all_countries[all_countries['name'] == target_country]['country_id'].values[0]

            # Filter for country-related tables
            country_tables = [t for t in all_tables_list if t.startswith('country_') or 'indicator' in t]
            co_table = st.selectbox("Metric Category", country_tables if country_tables else all_tables_list)
            
            # Using parameterized query to prevent injection
            co_df = fetch_df(f"SELECT * FROM {co_table} WHERE country_id = %s", (int(c_id),))
            edited_co = st.data_editor(co_df, num_rows="dynamic", key="co_editor")
            
            if st.button("Update Country Data"):
                st.success(f"Updates for {target_country} staged.")
        except Exception as e:
            st.error(f"Could not load country list: {e}")

    # ::::::::::::::::::: MANUAL SQL OVERRIDE (The Core CRUD Tool) :::::::::::::::::::
    st.markdown("---")
    st.subheader("🚀 Powerful SQL Command Center")
    st.caption("Use this to Add, Update, or Delete specific rows in your Aiven Database.")
    
    with st.expander("Show SQL Examples"):
        st.code("-- Update 2025 GDP Growth\nUPDATE global_real_gdp_growth SET real_growth = 3.2 WHERE year = 2025;")
        st.code("-- Add new country trade data\nINSERT INTO country_trade (country_id, exports_usd, year) VALUES (10, 500000000, 2025);")

    sql_input = st.text_area("Write SQL Query", height=150, placeholder="UPDATE ... SET ... WHERE ...")
    
    if st.button("Execute Query"):
        if sql_input:
            try:
                rows_affected = execute_query(sql_input)
                st.success(f"Query Executed! Rows affected: {rows_affected}")
            except Exception as e:
                st.error(f"SQL Error: {e}")
        else:
            st.warning("Please enter a query first.")

    # ---------------- FOOTER ----------------
    st.markdown("---")
    st.caption("© Admin Panel · Economic Intelligence Platform")