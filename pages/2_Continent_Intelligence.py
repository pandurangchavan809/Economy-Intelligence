# import streamlit as st
# # REMOVED st_autorefresh (We use Fragments now)

# from utils.db import fetch_df
# from utils.aggregations import (
#     get_all_continent_core,
#     get_continent_detail,
# )
# from utils.formatters import (
#     format_trillions_from_billions,
#     format_trillions_raw,
#     format_number,
#     format_percent,
#     format_trillion_live,
# )
# from utils.live_counter import (
#     live_continent_nominal_value,
#     live_continent_population_value,
# )

# # ---------------- CONFIG ----------------
# st.set_page_config(layout="wide")

# CURRENT_YEAR = 2025
# BASE_YEAR = 2024

# # ---------------- HEADER ----------------
# st.markdown("## 🌍 Continent Intelligence")
# st.markdown("Live macroeconomic overview by continent")
# st.markdown("---")

# # ---------------- LOAD DATA ----------------
# df = get_all_continent_core(BASE_YEAR, CURRENT_YEAR)

# # population growth map
# pop_growth_df = fetch_df(
#     """
#     SELECT continent_code, growth_rate
#     FROM continent_population_growth
#     WHERE year = %s
#     """,
#     (CURRENT_YEAR,),
# )
# pop_growth_map = dict(zip(
#     pop_growth_df.continent_code,
#     pop_growth_df.growth_rate
# ))

# # ---------------- FRAGMENT 1: OVERVIEW TABLE ----------------
# # We wrap the table generation in a fragment to make it tick
# @st.fragment(run_every="1s")
# def render_live_table(data_df, growth_map):
#     st.markdown("### 📊 Continents Overview")
#     rows = []

#     for _, r in data_df.iterrows():
#         live_gdp_trillion = live_continent_nominal_value(
#             r['continent_code'],
#             r['gdp_usd'],
#             r['real_growth'],
#             r['inflation'],
#             BASE_YEAR,
#         )

#         live_population = live_continent_population_value(
#             r['continent_code'],
#             r['population'],
#             growth_map.get(r['continent_code'], 0),
#             BASE_YEAR,
#         )

#         rows.append({
#             "Continent": r['continent_name'],
#             "GDP (Live)": format_trillion_live(live_gdp_trillion),
#             "Population": format_number(live_population),
#             "Real Growth": format_percent(r['real_growth']),
#             "Inflation": format_percent(r['inflation']),
#             "Trade Balance": format_trillions_raw(r['trade_balance_usd']),
#         })

#     st.dataframe(rows, use_container_width=True, hide_index=True)

# # Call the fragment
# render_live_table(df, pop_growth_map)

# # ---------------- CONTINENT SELECT ----------------
# st.markdown("---")

# continent_map = dict(zip(df.continent_name, df.continent_code))
# selected = st.selectbox("Select Continent", df.continent_name.tolist())
# code = continent_map[selected]

# # ---------------- CONTINENT DETAIL ----------------
# # Fetch the row normally
# detail_series = get_continent_detail(code, BASE_YEAR).iloc[0]

# # !!! CRITICAL FIX !!!
# # Convert Pandas Series to a simple Dictionary. 
# # This prevents the KeyError inside the fragment.
# detail = detail_series.to_dict()

# pop_growth = pop_growth_map.get(code, 0)
# nominal_growth = detail['real_growth'] + detail['inflation']

# # ---------------- FRAGMENT 2: LIVE DETAIL HEADER ----------------
# @st.fragment(run_every="1s")
# def render_live_detail(d, p_growth):
#     # Notice we use d['key'] because 'd' is now a dictionary
#     live_gdp_trillion = live_continent_nominal_value(
#         d['continent_code'],
#         d['gdp_usd'],
#         d['real_growth'],
#         d['inflation'],
#         BASE_YEAR,
#     )

#     live_population = live_continent_population_value(
#         d['continent_code'],
#         d['population'],
#         p_growth,
#         BASE_YEAR,
#     )

#     st.markdown(f"## 🌍 {d['continent_name']} — Live Economy")
#     st.caption(f"From Jan 1, {CURRENT_YEAR} up to now (current USD)")

#     st.markdown(
#         f"""
#         <h1 style="text-align:center">
#             {format_trillion_live(live_gdp_trillion)}
#         </h1>
#         <p style="text-align:center;color:gray">
#             Source: IMF World Economic Outlook (Nominal GDP – Live Projection)
#         </p>
#         """,
#         unsafe_allow_html=True,
#     )
    
#     # We moved the live population metrics inside the fragment so they update too
#     st.markdown("---")
#     st.markdown("### 👥 Population")

#     c1, c2, c3 = st.columns(3)
#     c1.metric("Population (Live)", format_number(live_population))
#     c2.metric("GDP per Capita", f"${d['gdp_per_capita_usd']:,.0f}")
#     c3.metric("Population Growth", format_percent(p_growth))

# # Call the fragment with the dictionary
# render_live_detail(detail, pop_growth)

# # ---------------- GROWTH METRICS (Static) ----------------
# # These are outside the fragment, so they don't flicker
# st.markdown("---")

# c1, c2, c3, c4 = st.columns(4)
# c1.metric("Real Growth", format_percent(detail['real_growth']))
# c2.metric("Inflation", format_percent(detail['inflation']))
# c3.metric("Nominal Growth", format_percent(nominal_growth))
# c4.metric("Base GDP (2024)", format_trillions_from_billions(detail['gdp_usd']))

# # ---------------- TRADE (Static) ----------------
# st.markdown("---")
# st.markdown("### 🌐 Trade")

# trade_series = fetch_df(
#     """
#     SELECT exports_usd, imports_usd, trade_balance_usd
#     FROM continent_trade
#     WHERE continent_code = %s AND year = %s
#     """,
#     (code, CURRENT_YEAR),
# ).iloc[0]

# # It is good practice to convert this to dict too, though not strictly required here since it's not in a fragment
# trade = trade_series.to_dict()

# c1, c2, c3 = st.columns(3)
# c1.metric("Exports", format_trillions_raw(trade['exports_usd']))
# c2.metric("Imports", format_trillions_raw(trade['imports_usd']))
# c3.metric("Trade Balance", format_trillions_raw(trade['trade_balance_usd']))

# # ---------------- FOOTER ----------------
# st.markdown("---")
# st.caption(
#     """
#     **Data Sources:** IMF · World Bank · United Nations  

#     **Methodology:** Live values are projected from base-year data using real growth, inflation,
#     and population growth rates.

#     **Disclaimer:** Live GDP figures are expressed in current USD using exchange-rate assumptions
#     as of **January 1, 2025**. Minor deviations may occur due to rounding,
#     exchange-rate movement, and projection methodology.

#     © Economy Intelligence Platform
#     """
# )

import streamlit as st
# REMOVED st_autorefresh (We use Fragments now)

from utils.db import fetch_df
from utils.aggregations import (
    get_all_continent_core,
    get_continent_detail,
)
from utils.formatters import (
    format_trillions_from_billions,
    format_trillions_raw,
    format_number,
    format_percent,
    format_trillion_live,
)
from utils.live_counter import (
    live_continent_nominal_value,
    live_continent_population_value,
)

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")

CURRENT_YEAR = 2025
BASE_YEAR = 2024

# ---------------- HEADER ----------------
st.markdown("## 🌍 Continent Intelligence")
st.markdown("Live macroeconomic overview by continent")
st.markdown("---")

# ---------------- LOAD DATA ----------------
df = get_all_continent_core(BASE_YEAR, CURRENT_YEAR)
# Force column names to lowercase to prevent KeyErrors
df.columns = [c.lower() for c in df.columns]

# population growth map
pop_growth_df = fetch_df(
    """
    SELECT continent_code, growth_rate
    FROM continent_population_growth
    WHERE year = %s
    """,
    (CURRENT_YEAR,),
)
pop_growth_df.columns = [c.lower() for c in pop_growth_df.columns]
pop_growth_map = dict(zip(
    pop_growth_df.continent_code,
    pop_growth_df.growth_rate
))

# ---------------- FRAGMENT 1: OVERVIEW TABLE ----------------
@st.fragment(run_every="1s")
def render_live_table(data_df, growth_map):
    st.markdown("### 📊 Continents Overview")
    rows = []

    for _, r in data_df.iterrows():
        # Use .get() to safely access keys
        c_code = r.get('continent_code')
        
        live_gdp_trillion = live_continent_nominal_value(
            c_code,
            r.get('gdp_usd', 0),
            r.get('real_growth', 0),
            r.get('inflation', 0),
            BASE_YEAR,
        )

        live_population = live_continent_population_value(
            c_code,
            r.get('population', 0),
            growth_map.get(c_code, 0),
            BASE_YEAR,
        )

        rows.append({
            "Continent": r.get('continent_name'),
            "GDP (Live)": format_trillion_live(live_gdp_trillion),
            "Population": format_number(live_population),
            "Real Growth": format_percent(r.get('real_growth', 0)),
            "Inflation": format_percent(r.get('inflation', 0)),
            "Trade Balance": format_trillions_raw(r.get('trade_balance_usd', 0)),
        })

    # Fix for 2026 Deprecation: use_container_width -> width="stretch"
    st.dataframe(rows, width="stretch", hide_index=True)

# Call the fragment
render_live_table(df, pop_growth_map)

# ---------------- CONTINENT SELECT ----------------
st.markdown("---")

# Use lowercase keys for the map
continent_map = dict(zip(df.continent_name, df.continent_code))
selected = st.selectbox("Select Continent", df.continent_name.tolist())
code = continent_map[selected]

# ---------------- CONTINENT DETAIL ----------------
detail_query = get_continent_detail(code, BASE_YEAR)
detail_query.columns = [c.lower() for c in detail_query.columns]
detail_series = detail_query.iloc[0]

# Convert to dict and ensure keys are stable
detail = detail_series.to_dict()

pop_growth = pop_growth_map.get(code, 0)
nominal_growth = detail.get('real_growth', 0) + detail.get('inflation', 0)

# ---------------- FRAGMENT 2: LIVE DETAIL HEADER ----------------
@st.fragment(run_every="1s")
def render_live_detail(d, p_growth):
    # Use .get() to handle any potential missing keys during refresh
    c_code = d.get('continent_code')
    
    live_gdp_trillion = live_continent_nominal_value(
        c_code,
        d.get('gdp_usd', 0),
        d.get('real_growth', 0),
        d.get('inflation', 0),
        BASE_YEAR,
    )

    live_population = live_continent_population_value(
        c_code,
        d.get('population', 0),
        p_growth,
        BASE_YEAR,
    )

    st.markdown(f"## 🌍 {d.get('continent_name')} — Live Economy")
    st.caption(f"From Jan 1, {CURRENT_YEAR} up to now (current USD)")

    st.markdown(
        f"""
        <h1 style="text-align:center">
            {format_trillion_live(live_gdp_trillion)}
        </h1>
        <p style="text-align:center;color:gray">
            Source: IMF World Economic Outlook (Nominal GDP – Live Projection)
        </p>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("---")
    st.markdown("### 👥 Population")

    c1, c2, c3 = st.columns(3)
    c1.metric("Population (Live)", format_number(live_population))
    c2.metric("GDP per Capita", f"${d.get('gdp_per_capita_usd', 0):,.0f}")
    c3.metric("Population Growth", format_percent(p_growth))

# Call the fragment
render_live_detail(detail, pop_growth)

# ---------------- GROWTH METRICS (Static) ----------------
st.markdown("---")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Real Growth", format_percent(detail.get('real_growth', 0)))
c2.metric("Inflation", format_percent(detail.get('inflation', 0)))
c3.metric("Nominal Growth", format_percent(nominal_growth))
c4.metric("Base GDP (2024)", format_trillions_from_billions(detail.get('gdp_usd', 0)))

# ---------------- TRADE (Static) ----------------
st.markdown("---")
st.markdown("### 🌐 Trade")

trade_res = fetch_df(
    """
    SELECT exports_usd, imports_usd, trade_balance_usd
    FROM continent_trade
    WHERE continent_code = %s AND year = %s
    """,
    (code, CURRENT_YEAR),
)
trade_res.columns = [c.lower() for c in trade_res.columns]
trade = trade_res.iloc[0].to_dict()

c1, c2, c3 = st.columns(3)
c1.metric("Exports", format_trillions_raw(trade.get('exports_usd', 0)))
c2.metric("Imports", format_trillions_raw(trade.get('imports_usd', 0)))
c3.metric("Trade Balance", format_trillions_raw(trade.get('trade_balance_usd', 0)))

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("© Economy Intelligence Platform")