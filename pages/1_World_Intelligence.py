# from auth.auth import require_login
# require_login()

import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from utils.live_counter import (
    live_nominal_value,
    live_population_value,
)
from utils.formatters import (
    format_trillions,
    format_trillions_live,
    format_number,
    format_currency,
)
from utils.aggregations import (
    get_world_nominal_gdp,
    get_world_real_growth,
    get_world_inflation,
    get_world_population,
    get_world_population_growth,
    get_global_trade,
)

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")

# 🔁 Trigger rerun every 1 second
st_autorefresh(interval=1000, key="world_live")

CURRENT_YEAR = datetime.utcnow().year
BASE_YEAR = CURRENT_YEAR - 1

# ---------------- HEADER ----------------
st.markdown("## 🌍 World Intelligence Hub")
st.markdown("**Live global economic overview**")

# ---------------- DB DATA ----------------
world_gdp_base = get_world_nominal_gdp(BASE_YEAR)
global_growth = get_world_real_growth(CURRENT_YEAR)
global_inflation = get_world_inflation(CURRENT_YEAR)

world_population_base = get_world_population(BASE_YEAR)
population_growth = get_world_population_growth(CURRENT_YEAR)

exports, imports, trade_balance = get_global_trade(BASE_YEAR)

# ---------------- LIVE VALUES ----------------
world_gdp_live = live_nominal_value(
    base_value=world_gdp_base,
    real_growth=global_growth,
    inflation=global_inflation,
    base_year=CURRENT_YEAR,
)

world_population_live = live_population_value(
    base_population=world_population_base,
    growth_rate=population_growth,
    base_year=CURRENT_YEAR,
)

# ---------------- WORLD GDP ----------------
st.markdown("---")
st.markdown("### 🌐 World GDP Live")
st.caption(f"From Jan 1, {CURRENT_YEAR} up to now (current USD)")

st.markdown(
    f"""
    <h1 style="text-align:center; font-weight:700;">
        {format_trillions_live(world_gdp_live)}
    </h1>
    <p style="text-align:center; color:gray;">
        Source: IMF WEO – Nominal GDP (Live)
    </p>
    """,
    unsafe_allow_html=True,
)

# ---------------- SNAPSHOT ----------------
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)

c1.metric("World Real GDP Growth", f"{global_growth:.2f}%")
c2.metric("World Inflation", f"{global_inflation:.2f}%")
c3.metric("Nominal Growth", f"{(global_growth + global_inflation):.2f}%")
c4.metric(f"Base GDP ({BASE_YEAR})", format_trillions(world_gdp_base))

# ---------------- POPULATION ----------------
st.markdown("### 👥 World Population")

# Live GDP per capita
gdp_per_capita_live = world_gdp_live / world_population_live

c5, c6, c7 = st.columns(3)

c5.metric(
    "Population (Live)",
    format_number(world_population_live),
)

c6.metric(
    "Population Growth",
    f"{population_growth:.2f}%",
)

c7.metric(
    "GDP per Capita (Live)",
    format_currency(gdp_per_capita_live),
)

# ---------------- TRADE ----------------
st.markdown("### 🌍 Global Trade")

c7, c8, c9 = st.columns(3)
c7.metric("Global Exports", format_trillions(exports))
c8.metric("Global Imports", format_trillions(imports))
c9.metric(
    "Trade Balance",
    format_trillions(trade_balance),
    delta="Surplus" if trade_balance > 0 else "Deficit",
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(
    """
    **Sources:** IMF WEO · World Bank · National Statistical Agencies  
    Live values update every second using official IMF-based growth rates.
    """
)

st.info("Drill down into continents and countries using the sidebar.")
