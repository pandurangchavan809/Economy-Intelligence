import streamlit as st
import time
from etl.world_bank import run as run_world_bank_etl

st.set_page_config(page_title="Admin ETL Control", page_icon="🔄", layout="wide")

st.title("🔄 World Bank Data Synchronization")
st.info("This process will update economic indicators for approximately 250 countries. Total duration: ~15 minutes.")

# Initialize session state for the log
if "etl_log" not in st.session_state:
    st.session_state.etl_log = []

if "etl_running" not in st.session_state:
    st.session_state.etl_running = False

# Sidebar status
with st.sidebar:
    st.header("Pipeline Status")
    if st.session_state.etl_running:
        st.warning("⚠️ Sync in Progress...")
    else:
        st.success("🟢 Ready to Sync")

# Main Action Button
if st.button("🚀 Start Global Data Refresh", disabled=st.session_state.etl_running):
    st.session_state.etl_running = True
    st.session_state.etl_log = [] # Clear old logs
    
    # UI Components for progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Current Activity")
        activity_log = st.empty()
    with col2:
        st.subheader("Completed Countries")
        completed_list = st.empty()

    # Define the callback function that the ETL script will call
    def update_ui(current, total, iso3):
        # 1. Update Progress Bar
        progress = current / total
        progress_bar.progress(progress)
        
        # 2. Update Status text
        status_text.markdown(f"**Step {current} of {total}**: Fetching data for `{iso3}`")
        
        # 3. Add to log and update display
        st.session_state.etl_log.append(f"✅ {iso3} processed")
        
        # Only show the last 15 items in the list to keep it clean
        activity_log.info(f"Currently working on: **{iso3}**")
        completed_list.code("\n".join(st.session_state.etl_log[-15:]))

    # Run the ETL
    try:
        run_world_bank_etl(progress_callback=update_ui)
        st.success("🎉 Database Synchronization Successful!")
        st.balloons()
    except Exception as e:
        st.error(f"❌ Error occurred: {e}")
    finally:
        st.session_state.etl_running = False

st.markdown("---")
st.caption("Admin Tool • Economic Intelligence Platform • Powered by World Bank API")