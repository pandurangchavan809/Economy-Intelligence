import streamlit as st
import pandas as pd
from utils.db import fetch_df, execute_query

# ::::::::::::::::::: SECURITY ::::::::::::::::::::::::::::::::::::::::::::
def check_password():
    if "admin_authenticated" not in st.session_state:
        st.session_state["admin_authenticated"] = False
    
    if st.session_state["admin_authenticated"]:
        return True

    st.sidebar.title("Admin Login")
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
    st.title("Economic Intelligence: Admin Control")
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
            # Fetch countries for the dropdown
            all_countries = fetch_df("SELECT country_id, name FROM countries ORDER BY name")
            target_country = st.selectbox("Select Country to Edit", all_countries['name'])
            c_id = all_countries[all_countries['name'] == target_country]['country_id'].values[0]

            # Filter for country-related tables
            country_tables = [t for t in all_tables_list if t.startswith('country_') or 'indicator' in t]
            co_table = st.selectbox("Metric Category", country_tables if country_tables else all_tables_list)
            
            # --- BUG FIX LOGIC START ---
            # Check the actual columns of the selected table to avoid "Unknown column" errors
            columns_df = fetch_df(f"DESCRIBE {co_table}")
            existing_cols = columns_df.iloc[:, 0].tolist()

            if 'country_id' in existing_cols:
                # Standard filtering
                co_df = fetch_df(f"SELECT * FROM {co_table} WHERE country_id = %s", (int(c_id),))
                edited_co = st.data_editor(co_df, num_rows="dynamic", key="co_editor")
                
                if st.button("Update Country Data"):
                    st.success(f"Updates for {target_country} staged.")
            else:
                # Fallback if country_id doesn't exist (e.g., the table uses different naming)
                st.warning(f"The table '{co_table}' does not have a 'country_id' column. Available columns: {', '.join(existing_cols)}")
                st.info("Showing all rows for this table instead:")
                co_df = fetch_df(f"SELECT * FROM {co_table} LIMIT 100")
                st.dataframe(co_df)
            # --- BUG FIX LOGIC END ---

        except Exception as e:
            st.error(f"Could not load country list: {e}")

    # ::::::::::::::::::: MANUAL SQL OVERRIDE (The Core CRUD Tool) :::::::::::::::::::
    st.markdown("---")
    st.subheader("Powerful SQL Command Center")
    st.caption("Use this to Add, Update, or Delete specific rows in your Aiven Database.")
    
    with st.expander("Show SQL Examples"):
        st.code("-- Update 2025 GDP Growth\nUPDATE global_real_gdp_growth SET real_growth = 3.2 WHERE year = 2025;")
        st.code("-- Add new country trade data\nINSERT INTO country_trade (country_id, exports_usd, year) VALUES (10, 500000000, 2025);")

    sql_input = st.text_area("Write SQL Query", height=150, placeholder="UPDATE ... SET ... WHERE ...")
    
    if st.button("Execute Query"):
        if sql_input:
            try:
                output = execute_query(sql_input)
            
            # Check if the output is a list of data (from a SELECT)
                if isinstance(output, list): 
                    if output: # If rows were returned
                        st.write("### 📋 Query Results")
                    # Convert the list of tuples into a clean DataFrame
                        st.dataframe(pd.DataFrame(output), use_container_width=True)
                    else:
                        st.info("Query executed successfully, but no rows were found.")
                else:
                    st.success(f"Action Successful! Rows affected: {output}")
            except Exception as e:
                st.error(f"SQL Error: {e}")

    # ---------------- FOOTER ----------------
    st.markdown("---")
    st.caption("Admin Panel · Economic Intelligence Platform")
