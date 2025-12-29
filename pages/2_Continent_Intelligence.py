# # from auth.auth import require_login
# # require_login()

# import streamlit as st
# from streamlit_autorefresh import st_autorefresh

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

# st_autorefresh(interval=1000, key="continent_live_refresh")

# # ---------------- HEADER ----------------
# st.markdown("## 🌍 Continent Intelligence")
# st.markdown("Live macroeconomic overview by continent")
# st.markdown("---")

# # ---------------- LOAD DATA ----------------
# df = get_all_continent_core(BASE_YEAR, CURRENT_YEAR)

# # population growth map (needed for live population)
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

# # ---------------- OVERVIEW TABLE ----------------
# st.markdown("### 📊 Continents Overview")

# rows = []

# for _, r in df.iterrows():

#     live_gdp_trillion = live_continent_nominal_value(
#         r.continent_code,
#         r.gdp_usd,          # stored in BILLIONS
#         r.real_growth,
#         r.inflation,
#         BASE_YEAR,
#     )

#     live_population = live_continent_population_value(
#         r.continent_code,
#         r.population,
#         pop_growth_map.get(r.continent_code, 0),
#         BASE_YEAR,
#     )

#     rows.append({
#         "Continent": r.continent_name,
#         "GDP (Live)": format_trillion_live(live_gdp_trillion),
#         "Population": format_number(live_population),
#         "Real Growth": format_percent(r.real_growth),
#         "Inflation": format_percent(r.inflation),
#         "Trade Balance": format_trillions_raw(r.trade_balance_usd),
#     })

# st.dataframe(rows, use_container_width=True, hide_index=True)

# # ---------------- CONTINENT SELECT ----------------
# st.markdown("---")

# continent_map = dict(zip(df.continent_name, df.continent_code))
# selected = st.selectbox("Select Continent", df.continent_name.tolist())
# code = continent_map[selected]

# # ---------------- CONTINENT DETAIL ----------------
# detail = get_continent_detail(code, BASE_YEAR).iloc[0]

# pop_growth = pop_growth_map.get(code, 0)

# live_gdp_trillion = live_continent_nominal_value(
#     code,
#     detail.gdp_usd,
#     detail.real_growth,
#     detail.inflation,
#     BASE_YEAR,
# )

# live_population = live_continent_population_value(
#     code,
#     detail.population,
#     pop_growth,
#     BASE_YEAR,
# )

# nominal_growth = detail.real_growth + detail.inflation

# st.markdown(f"## 🌍 {detail.continent_name} — Live Economy")
# st.caption(f"From Jan 1, {CURRENT_YEAR} up to now (current USD)")

# st.markdown(
#     f"""
#     <h1 style="text-align:center">
#         {format_trillion_live(live_gdp_trillion)}
#     </h1>
#     <p style="text-align:center;color:gray">
#         Source: IMF World Economic Outlook (Nominal GDP – Live Projection)
#     </p>
#     """,
#     unsafe_allow_html=True,
# )

# # ---------------- GROWTH METRICS ----------------
# st.markdown("---")

# c1, c2, c3, c4 = st.columns(4)
# c1.metric("Real Growth", format_percent(detail.real_growth))
# c2.metric("Inflation", format_percent(detail.inflation))
# c3.metric("Nominal Growth", format_percent(nominal_growth))
# c4.metric("Base GDP (2024)", format_trillions_from_billions(detail.gdp_usd))

# # ---------------- POPULATION ----------------
# st.markdown("---")
# st.markdown("### 👥 Population")

# c1, c2, c3 = st.columns(3)
# c1.metric("Population (Live)", format_number(live_population))
# c2.metric("GDP per Capita", f"${detail.gdp_per_capita_usd:,.0f}")
# c3.metric("Population Growth", format_percent(pop_growth))

# # ---------------- TRADE ----------------
# st.markdown("---")
# st.markdown("### 🌐 Trade")

# trade = fetch_df(
#     """
#     SELECT exports_usd, imports_usd, trade_balance_usd
#     FROM continent_trade
#     WHERE continent_code = %s AND year = %s
#     """,
#     (code, CURRENT_YEAR),
# ).iloc[0]

# c1, c2, c3 = st.columns(3)
# c1.metric("Exports", format_trillions_raw(trade.exports_usd))
# c2.metric("Imports", format_trillions_raw(trade.imports_usd))
# c3.metric("Trade Balance", format_trillions_raw(trade.trade_balance_usd))

# # ---------------- FOOTER ----------------
# st.markdown("---")
# st.caption(
#     """
#     **Data Sources:**  
#     IMF · World Bank · United Nations  

#     **Methodology:**  
#     Live values are projected from base-year data using real growth, inflation,
#     and population growth rates.

#     **Disclaimer:**  
#     Live GDP figures are expressed in current USD using exchange-rate assumptions
#     as of **January 1, 2025**. Minor deviations may occur due to rounding,
#     exchange-rate movement, and projection methodology.

#     © Economy Intelligence Platform
#     """
# )




import streamlit as st

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

# ---------------- LOAD DATA (Runs once) ----------------
# This runs only ONCE when the user opens the page.
df = get_all_continent_core(BASE_YEAR, CURRENT_YEAR)

# Population growth map
pop_growth_df = fetch_df(
    """
    SELECT continent_code, growth_rate
    FROM continent_population_growth
    WHERE year = %s
    """,
    (CURRENT_YEAR,),
)
pop_growth_map = dict(zip(
    pop_growth_df.continent_code,
    pop_growth_df.growth_rate
))

# ---------------- FRAGMENT 1: OVERVIEW TABLE ----------------
# This isolated function runs every 1 second without reloading the page.
@st.fragment(run_every="1s")
def render_live_table(data_df, growth_map):
    st.markdown("### 📊 Continents Overview")
    rows = []
    
    # We iterate through the dataframe passed to us
    for _, r in data_df.iterrows():
        # Calculate live values locally
        live_gdp = live_continent_nominal_value(
            r['continent_code'], 
            r['gdp_usd'], 
            r['real_growth'], 
            r['inflation'], 
            BASE_YEAR
        )
        live_pop = live_continent_population_value(
            r['continent_code'], 
            r['population'], 
            growth_map.get(r['continent_code'], 0), 
            BASE_YEAR
        )

        rows.append({
            "Continent": r['continent_name'],
            "GDP (Live)": format_trillion_live(live_gdp),
            "Population": format_number(live_pop),
            "Real Growth": format_percent(r['real_growth']),
            "Inflation": format_percent(r['inflation']),
            "Trade Balance": format_trillions_raw(r['trade_balance_usd']),
        })
    
    st.dataframe(rows, use_container_width=True, hide_index=True)

# Call the table fragment
render_live_table(df, pop_growth_map)


# ---------------- SELECT CONTINENT (Static) ----------------
# This part is OUTSIDE the fragment, so the dropdown doesn't flicker/reset.
st.markdown("---")

continent_map = dict(zip(df.continent_name, df.continent_code))
selected = st.selectbox("Select Continent", df.continent_name.tolist())
code = continent_map[selected]


# ---------------- PREPARE DATA FOR DETAIL VIEW ----------------
# Fetch the detail row once when selection changes
detail_res = get_continent_detail(code, BASE_YEAR)

if not detail_res.empty:
    row = detail_res.iloc[0]
    
    # CRITICAL FIX: Convert Pandas Row to a simple Dictionary.
    # This prevents the "KeyError" / "AttributeError" inside the fragment.
    detail_dict = {
        'code': row['continent_code'],
        'name': row['continent_name'],
        'gdp_usd': row['gdp_usd'],
        'real_growth': row['real_growth'],
        'inflation': row['inflation'],
        'population': row['population'],
        'gdp_per_capita_usd': row['gdp_per_capita_usd']
    }
    
    selected_growth_rate = pop_growth_map.get(code, 0)
    nominal_growth = detail_dict['real_growth'] + detail_dict['inflation']


    # ---------------- FRAGMENT 2: LIVE DETAIL HEADER ----------------
    # This updates the big numbers every second.
    @st.fragment(run_every="1s")
    def render_live_detail(d, growth_rate):
        # Calculate live values
        live_gdp_trillion = live_continent_nominal_value(
            d['code'],
            d['gdp_usd'],
            d['real_growth'],
            d['inflation'],
            BASE_YEAR,
        )

        live_population = live_continent_population_value(
            d['code'],
            d['population'],
            growth_rate,
            BASE_YEAR,
        )

        st.markdown(f"## 🌍 {d['name']} — Live Economy")
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
        
        # We also put the Live Population metrics inside here so they update too
        st.markdown("---")
        st.markdown("### 👥 Population")
        c1, c2, c3 = st.columns(3)
        c1.metric("Population (Live)", format_number(live_population))
        c2.metric("GDP per Capita", f"${d['gdp_per_capita_usd']:,.0f}")
        c3.metric("Population Growth", format_percent(growth_rate))

    # Call the detail fragment
    render_live_detail(detail_dict, selected_growth_rate)


    # ---------------- STATIC METRICS (Below the fragment) ----------------
    # These do not need to update every second, so they stay outside.
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Real Growth", format_percent(detail_dict['real_growth']))
    c2.metric("Inflation", format_percent(detail_dict['inflation']))
    c3.metric("Nominal Growth", format_percent(nominal_growth))
    c4.metric("Base GDP (2024)", format_trillions_from_billions(detail_dict['gdp_usd']))


    # ---------------- TRADE (Static) ----------------
    st.markdown("---")
    st.markdown("### 🌐 Trade")

    trade_df = fetch_df(
        """
        SELECT exports_usd, imports_usd, trade_balance_usd
        FROM continent_trade
        WHERE continent_code = %s AND year = %s
        """,
        (code, CURRENT_YEAR),
    )
    
    if not trade_df.empty:
        trade = trade_df.iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Exports", format_trillions_raw(trade['exports_usd']))
        c2.metric("Imports", format_trillions_raw(trade['imports_usd']))
        c3.metric("Trade Balance", format_trillions_raw(trade['trade_balance_usd']))
    else:
        st.info("Trade data not available for this year.")

else:
    st.error("No data found for the selected continent.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption(
    """
    **Data Sources:** IMF · World Bank · United Nations  

    **Methodology:** Live values are projected from base-year data using real growth, inflation,
    and population growth rates.

    **Disclaimer:** Live GDP figures are expressed in current USD using exchange-rate assumptions
    as of **January 1, 2025**. Minor deviations may occur due to rounding,
    exchange-rate movement, and projection methodology.

    © Economy Intelligence Platform
    """
)

