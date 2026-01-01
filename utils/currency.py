import requests
import streamlit as st
from countryinfo import CountryInfo

@st.cache_data(ttl=3600)

def get_rate_by_country_name(country_name):
    try:
        # 1. Automatically find the currency code from the country name
        country = CountryInfo(country_name)
        currencies = country.currencies() # Returns a list like ['INR']
        
        if not currencies:
            return None, None
            
        currency_code = currencies[0]

        # 2. Fetch the live exchange rate for that code
        url = f"https://api.exchangerate-api.com/v4/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        rate = data.get("rates", {}).get(currency_code)
        
        return rate, currency_code
        
    except Exception as e:
        print(f"Error finding currency for {country_name}: {e}")
        return None, None
    
    