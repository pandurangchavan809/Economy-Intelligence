import streamlit as st
import time
from etl.world_bank import run as run_world_bank_etl

st.set_page_config(page_title="Data Refresh", page_icon="🔄")

st.title("🔄 Database Synchronization")
st.markdown("""
This tool fetches the latest macroeconomic data from the **World Bank API** and syncs it directly to your **Aiven Cloud Database**.
""")

if "etl_running" not in st.session_state:
    st.session_state.etl_running = False

# Security Check (Optional: reuse your password logic)
if st.sidebar.button("Logout"):
    st.session_state["admin_authenticated"] = False
    st.rerun()

if st.button("🚀 Start Global Data Refresh", disabled=st.session_state.etl_running):
    st.session_state.etl_running = True
    
    with st.status("Fetching Data from World Bank...", expanded=True) as status:
        try:
            st.write("📡 Connecting to Aiven Cloud...")
            # We call the function from your world_bank.py
            # Note: You might want to modify world_bank.py slightly 
            # to accept a streamlit progress bar object if you want it visual
            run_world_bank_etl() 
            
            status.update(label="✅ Update Complete!", state="complete", expanded=False)
            st.success("All country data has been refreshed and committed to Aiven.")
            
        except Exception as e:
            st.error(f"Error during update: {e}")
            status.update(label="❌ Update Failed", state="error")
    
    st.session_state.etl_running = False

