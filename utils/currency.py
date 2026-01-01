import requests
import streamlit as st

@st.cache_data(ttl=3600)
def get_exchange_rate(target_currency):
    """
    Fetches the rate for 1 USD to the target_currency.
    """
    if not target_currency:
        return None
        
    # Using the ExchangeRate-API (Free tier)
    url = f"https://api.exchangerate-api.com/v4/latest/USD"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Get the specific rate for the country's currency
        rate = data.get("rates", {}).get(target_currency)
        return rate
    except Exception as e:
        print(f"⚠️ Currency API Error: {e}")
        return None