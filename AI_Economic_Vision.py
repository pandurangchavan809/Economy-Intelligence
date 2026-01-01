import os
import json
import time
import pandas as pd
import plotly.express as px
import streamlit as st
import google.generativeai as genai

# from dotenv import load_dotenv   ## avoid for cloud

# load_dotenv()  ##.....avoid for cloud run

st.set_page_config(page_title="AI Economics Dashboard", layout="wide")

# API Configuration  for local
# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     st.error("🚨 API Key not found. Please check your .env file.")
#     st.stop()

# API configuration for cloud :-----

if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    st.error("🚨 API Key not found in Secrets. Please add GEMINI_API_KEY to your Streamlit Settings.")
    st.stop()

genai.configure(api_key=API_KEY)
MODEL_ID = "gemini-2.5-flash" 

# Styling for high-end financial dashboard
st.markdown("""
    <style>
    .main { background-color: #0b0d11; color: #ffffff; }
    .stPlotlyChart { border: 1px solid #1f2937; border-radius: 10px; padding: 5px; }
    h1 { color: #00d4ff; font-weight: 800; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

#2. DATA ENGINE (10-Year History) :-
@st.cache_data(ttl=3600)
def fetch_historical_intel(country):
    """Generates 10 years of data (2015-2025) with proper scaling."""
    prompt = f"""
    Act as a senior economic researcher. Generate a JSON object for {country} for years 2015 to 2025.
    Rules:
    1. GDP must be in Nominal USD Billions (e.g., Japan 2025 is ~4300.0 to 4500.0). 
    2. Inflation, Unemployment, and FDI must be realistic percentages.
    3. Return ONLY a raw JSON object with this exact schema:
    {{
        "data": [
            {{"year": 2015, "gdp": 4444.0, "inflation": 0.8, "unemp": 3.4, "fdi": 0.1}},
            ... (up to 2025)
        ],
        "summary": "1-sentence expert trend summary."
    }}
    Ensure {country} GDP matches historical Billion-scale values accurately.
    """
    
    try:
        model = genai.GenerativeModel(MODEL_ID)
        response = model.generate_content(prompt)
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(raw_text)
    except Exception as e:
        if "429" in str(e):
            time.sleep(3)
            return fetch_historical_intel(country)
        st.error(f"Error fetching data: {e}")
        return None

#3. UI LAYOUT :
st.title("📊 AI Economics Dashboard")
st.caption(f"Engine: {MODEL_ID.upper()} | Timeline: 2015 — 2025")

with st.sidebar:
    st.header("Search Country")
    selected_country = st.text_input("Enter Country", "Japan")
    if st.button("🔄 Update Analysis"):
        st.cache_data.clear()
        st.rerun()

# ---:::: 4. VISUALIZATION ENGINE -----::::
data_package = fetch_historical_intel(selected_country)

if data_package:
    df = pd.DataFrame(data_package['data'])
    st.info(f"**Market Note:** {data_package.get('summary')}")
    
    col1, col2 = st.columns(2)

    with col1:
        # GDP Graph
        st.subheader("Total GDP (Billions USD)")
        fig_gdp = px.line(df, x='year', y='gdp', markers=True, 
                          template="plotly_dark", line_shape='spline')
        fig_gdp.update_traces(line_color='#00d4ff', fill='tozeroy', fillcolor='rgba(0, 212, 255, 0.1)')
        fig_gdp.update_layout(margin=dict(l=20, r=20, t=20, b=20), xaxis_title="Year", yaxis_title="USD Billions")
        st.plotly_chart(fig_gdp, use_container_width=True)

        # Unemployment Rate
        st.subheader("Unemployment Rate (%)")
        fig_un = px.line(df, x='year', y='unemp', markers=True, template="plotly_dark")
        fig_un.update_traces(line_color='#76ff03')
        st.plotly_chart(fig_un, use_container_width=True)

    with col2:
        st.subheader("Inflation Rate (%)")
        fig_inf = px.bar(df, x='year', y='inflation', template="plotly_dark")
        fig_inf.update_traces(marker_color='#ff4b4b', width=0.4, marker_line_width=0)
        fig_inf.update_layout(bargap=0.2, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_inf, use_container_width=True)

        # FDI Trend
        st.subheader("FDI (% of GDP)")
        fig_fdi = px.bar(df, x='year', y='fdi', template="plotly_dark")
        fig_fdi.update_traces(marker_color='#ffaa00', width=0.4)
        st.plotly_chart(fig_fdi, use_container_width=True)

# --- 5. CHAT CONSULTANT ---
st.divider()
st.subheader("💬 AI Economic Consultant")
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input(f"Ask about {selected_country}'s fiscal policy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        response = genai.GenerativeModel(MODEL_ID).generate_content(f"Analyze {selected_country}: {prompt}")
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
