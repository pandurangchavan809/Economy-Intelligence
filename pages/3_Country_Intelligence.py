# # from auth.auth import require_login
# # require_login()

# import streamlit as st
# from datetime import datetime, timezone
# from streamlit_autorefresh import st_autorefresh

# from utils.db import fetch_df
# from utils.formatters import format_number, format_percent
# from utils.live_counter import live_nominal_value, live_population_value

# # ---------------- CONFIG ----------------
# st.set_page_config(layout="wide")
# # refresh every 1s to show live counters
# st_autorefresh(interval=1000, key="country_live_refresh")

# CURRENT_YEAR = datetime.utcnow().year
# # NOTE: stored base-year rows (e.g. 2024) are meant to be treated as Jan 1, stored_year + 1
# # We still expose BASE_YEAR variable for UI text if needed.
# BASE_YEAR = CURRENT_YEAR - 1

# # ----------------- SMALL SQL HELPERS -----------------
# def table_has_column(table_name: str, column_name: str) -> bool:
#     q = """
#     SELECT COUNT(*) FROM information_schema.COLUMNS
#     WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s
#     """
#     df = fetch_df(q, (table_name, column_name))
#     return bool(df.iloc[0, 0])

# def get_country_list():
#     q = "SELECT country_id, name, iso3, flag_url FROM countries ORDER BY name"
#     return fetch_df(q)

# def fetch_latest_indicator_by_country(country_id, prefer_years=None):
#     if prefer_years:
#         for y in prefer_years:
#             df = fetch_df("SELECT * FROM economic_indicators WHERE country_id=%s AND year=%s LIMIT 1", (country_id, y))
#             if not df.empty:
#                 return df.iloc[0].to_dict()
#     df = fetch_df("SELECT * FROM economic_indicators WHERE country_id=%s ORDER BY year DESC LIMIT 1", (country_id,))
#     if df.empty:
#         return {}
#     return df.iloc[0].to_dict()

# def get_country_population(country_id, year_prefer=None):
#     if table_has_column("country_population", "population"):
#         if year_prefer:
#             df = fetch_df("SELECT population, year FROM country_population WHERE country_id=%s AND year=%s LIMIT 1", (country_id, year_prefer))
#             if not df.empty:
#                 return int(df.iloc[0]["population"]), int(df.iloc[0]["year"])
#         df = fetch_df("SELECT population, year FROM country_population WHERE country_id=%s AND population IS NOT NULL ORDER BY year DESC LIMIT 1", (country_id,))
#         if not df.empty:
#             return int(df.iloc[0]["population"]), int(df.iloc[0]["year"])
#     # fallback to economic_indicators.population column
#     if table_has_column("economic_indicators", "population"):
#         df = fetch_df("SELECT population, year FROM economic_indicators WHERE country_id=%s AND population IS NOT NULL ORDER BY year DESC LIMIT 1", (country_id,))
#         if not df.empty:
#             return int(df.iloc[0]["population"]), int(df.iloc[0]["year"])
#     return None, None

# def get_population_growth_rate(country_id, year):
#     if table_has_column("country_population_growth", "population_growth"):
#         df = fetch_df("SELECT population_growth FROM country_population_growth WHERE country_id=%s AND year=%s LIMIT 1", (country_id, year))
#         if not df.empty:
#             return float(df.iloc[0,0])
#     # compute from two latest population entries
#     if table_has_column("country_population", "population"):
#         df = fetch_df("SELECT year, population FROM country_population WHERE country_id=%s AND population IS NOT NULL ORDER BY year DESC LIMIT 2", (country_id,))
#         if len(df) >= 2:
#             p_new = float(df.iloc[0]["population"])
#             p_old = float(df.iloc[1]["population"])
#             if p_old > 0:
#                 return (p_new - p_old) / p_old * 100.0
#     return None

# def get_trade_for_country(country_id):
#     if not table_has_column("country_trade", "exports_usd"):
#         return None
#     df = fetch_df("SELECT exports_usd, imports_usd, trade_balance_usd, year FROM country_trade WHERE country_id=%s ORDER BY year DESC LIMIT 1", (country_id,))
#     if df.empty:
#         return None
#     return df.iloc[0].to_dict()

# def get_pct_shares(country_id, iso3, continent_code, year):
#     pct_cont = None
#     pct_world = None
#     # try country_continent_gdp_share (by iso3 or country name)
#     if table_has_column("country_continent_gdp_share", "pct_of_continent"):
#         if table_has_column("country_continent_gdp_share", "iso3") and iso3:
#             df = fetch_df("SELECT pct_of_continent FROM country_continent_gdp_share WHERE iso3=%s AND year=%s LIMIT 1", (iso3, year))
#             if not df.empty:
#                 pct_cont = float(df.iloc[0,0])
#         if pct_cont is None:
#             name = fetch_df("SELECT name FROM countries WHERE country_id=%s LIMIT 1", (country_id,))
#             if not name.empty:
#                 df = fetch_df("SELECT pct_of_continent FROM country_continent_gdp_share WHERE country=%s AND year=%s LIMIT 1", (name.iloc[0,0], year))
#                 if not df.empty:
#                     pct_cont = float(df.iloc[0,0])
#     # try world share view
#     if table_has_column("country_world_gdp_share", "pct_of_world"):
#         if table_has_column("country_world_gdp_share", "iso3") and iso3:
#             df = fetch_df("SELECT pct_of_world FROM country_world_gdp_share WHERE iso3=%s AND year=%s LIMIT 1", (iso3, year))
#             if not df.empty:
#                 pct_world = float(df.iloc[0,0])
#         if pct_world is None:
#             name = fetch_df("SELECT name FROM countries WHERE country_id=%s LIMIT 1", (country_id,))
#             if not name.empty:
#                 df = fetch_df("SELECT pct_of_world FROM country_world_gdp_share WHERE country=%s AND year=%s LIMIT 1", (name.iloc[0,0], year))
#                 if not df.empty:
#                     pct_world = float(df.iloc[0,0])
#     # fallback compute using economic_indicators.gdp and continent/world aggregates
#     if pct_cont is None or pct_world is None:
#         df_g = fetch_df("SELECT gdp FROM economic_indicators WHERE country_id=%s AND year=%s LIMIT 1", (country_id, year))
#         if df_g.empty:
#             df_g = fetch_df("SELECT gdp FROM economic_indicators WHERE country_id=%s AND gdp IS NOT NULL ORDER BY year DESC LIMIT 1", (country_id,))
#         country_gdp = float(df_g.iloc[0]["gdp"]) if not df_g.empty else None
#         if pct_cont is None and country_gdp is not None and continent_code:
#             df_cont = fetch_df("SELECT gdp_usd FROM continent_nominal_gdp WHERE continent_code=%s AND year=%s LIMIT 1", (continent_code, year))
#             if not df_cont.empty and df_cont.iloc[0,0] is not None:
#                 cont_usd = float(df_cont.iloc[0,0]) * 1e9
#                 if cont_usd > 0:
#                     pct_cont = country_gdp / cont_usd * 100.0
#         if pct_world is None and country_gdp is not None:
#             df_world = fetch_df("SELECT SUM(gdp_usd) AS world_sum_billion FROM continent_nominal_gdp WHERE year=%s", (year,))
#             if not df_world.empty and df_world.iloc[0,0] is not None:
#                 world_usd = float(df_world.iloc[0,0]) * 1e9
#                 if world_usd > 0:
#                     pct_world = country_gdp / world_usd * 100.0
#     return pct_cont, pct_world

# # ----------------- PAGE -----------------
# st.title("🌐 Country Intelligence")
# st.caption("Live snapshot — GDP, population, trade and more (values update every second)")
# st.markdown("---")

# # selector
# countries_df = get_country_list()
# labels = [f"{r['name']} ({r['iso3']})" if r['iso3'] else r['name'] for _, r in countries_df.iterrows()]
# id_map = {labels[i]: int(countries_df.iloc[i]["country_id"]) for i in range(len(labels))}
# selected = st.selectbox("Search / select a country", labels, index=0)
# country_id = id_map[selected]

# # fetch meta
# meta = fetch_df("SELECT country_id,name,iso2,iso3,capital,continent,continent_code,flag_url FROM countries WHERE country_id=%s LIMIT 1", (country_id,))
# if meta.empty:
#     st.error("Country metadata missing.")
#     st.stop()
# meta = meta.iloc[0]
# country_name = meta["name"]
# iso3 = meta["iso3"]
# flag_url = meta["flag_url"]
# capital = meta["capital"]
# continent_code = meta["continent_code"]

# # header row
# c1, c2 = st.columns([1, 6])
# if flag_url:
#     c1.image(flag_url, width=96)
# c2.header(f"{country_name} — Live Overview")
# c2.caption(f"Capital: {capital or '—'} · ISO3: {iso3 or '—'} · Continent: {meta.get('continent') or '—'}")
# st.markdown("---")

# # indicators
# ind = fetch_latest_indicator_by_country(country_id, prefer_years=[BASE_YEAR, BASE_YEAR-1, BASE_YEAR-2])
# gdp = ind.get("gdp")
# gdp_year = ind.get("year")
# real_growth = ind.get("gdp_growth")
# inflation = ind.get("inflation")
# unemployment = ind.get("unemployment")
# military_spending = ind.get("military_spending") or ind.get("military")
# debt_gdp = ind.get("debt_gdp") or ind.get("debt_to_gdp")
# exchange_rate = ind.get("exchange_rate")
# ind_population = ind.get("population")

# # population base and live
# pop_val, pop_year = get_country_population(country_id, year_prefer=BASE_YEAR)
# if pop_val is None and ind_population:
#     pop_val = int(ind_population); pop_year = ind.get("year")
# if pop_val:
#     pop_growth_rate = get_population_growth_rate(country_id, CURRENT_YEAR)
#     # treat stored population year as Jan 1 of (stored_year + 1)
#     pop_base_year = (pop_year or BASE_YEAR) + 1
#     live_pop = live_population_value(pop_val, pop_growth_rate or 0.0, pop_base_year)
#     population_display = format_number(int(live_pop))
# else:
#     live_pop = None
#     pop_growth_rate = None
#     population_display = "Not available"

# # GDP live: base year = stored_gdp_year + 1 (so 2024 row -> start = 2025-01-01)
# country_gdp_usd = None
# if gdp is not None:
#     try:
#         country_gdp_usd = float(gdp)
#     except Exception:
#         country_gdp_usd = None

# live_gdp_display = "Not available"
# live_gdp_usd = None
# if country_gdp_usd is not None:
#     base_for_gdp = (gdp_year or BASE_YEAR) + 1
#     live_gdp_usd = live_nominal_value(country_gdp_usd, real_growth or 0.0, inflation or 0.0, base_for_gdp)
#     live_gdp_display = f"${live_gdp_usd / 1e12:,.8f} T"

# # GDP per capita
# gdp_per_capita_display = "Not available"
# if live_gdp_usd is not None and live_pop:
#     try:
#         gdp_per = live_gdp_usd / float(live_pop)
#         gdp_per_capita_display = f"${gdp_per:,.0f}"
#     except Exception:
#         pass

# # shares
# pct_cont, pct_world = get_pct_shares(country_id, iso3, continent_code, BASE_YEAR)
# pct_cont_display = format_percent(pct_cont) if pct_cont is not None else "Not available"
# pct_world_display = format_percent(pct_world) if pct_world is not None else "Not available"

# # trade, military, debt
# trade = get_trade_for_country(country_id)
# if trade:
#     ex = trade.get("exports_usd"); im = trade.get("imports_usd"); tb = trade.get("trade_balance_usd")
#     ex_disp = f"${float(ex)/1e12:,.2f} T" if ex is not None else "Not available"
#     im_disp = f"${float(im)/1e12:,.2f} T" if im is not None else "Not available"
#     tb_disp = f"${float(tb)/1e12:,.2f} T" if tb is not None else "Not available"
# else:
#     ex_disp = im_disp = tb_disp = "Not available"

# mil_display = "Not available"
# if military_spending:
#     try:
#         mil_display = f"${float(military_spending)/1e9:,.2f} B"
#     except Exception:
#         mil_display = "Not available"
# elif table_has_column("country_military_share", "military_spending"):
#     dfm = fetch_df("SELECT military_spending FROM country_military_share WHERE country=%s ORDER BY year DESC LIMIT 1", (country_name,))
#     if not dfm.empty:
#         mil_display = f"${float(dfm.iloc[0,0])/1e9:,.2f} B"

# debt_display = format_percent(debt_gdp) if debt_gdp is not None else "Not available"
# exrate_display = f"{exchange_rate}" if exchange_rate else "Not available"

# # --- UI metrics (clean)
# st.markdown("### Key Indicators")
# k1, k2, k3, k4 = st.columns([3,2,2,2])
# k1.metric("GDP (Live)", live_gdp_display)
# k2.metric("Population", population_display)
# k3.metric("GDP per Capita (Live)", gdp_per_capita_display)
# k4.metric("Population growth", format_percent(pop_growth_rate) if pop_growth_rate is not None else "Not available")

# k5, k6, k7, k8 = st.columns([2,2,2,2])
# k5.metric("Real GDP growth", format_percent(real_growth) if real_growth is not None else "Not available")
# k6.metric("Inflation", format_percent(inflation) if inflation is not None else "Not available")
# nom_val = None
# if real_growth is not None or inflation is not None:
#     nom_val = (real_growth or 0.0) + (inflation or 0.0)
# k7.metric("Nominal growth (est.)", format_percent(nom_val) if nom_val is not None else "Not available")
# k8.metric("Base GDP (stored)", f"${(country_gdp_usd / 1e12):,.2f} T" if country_gdp_usd else "Not available")

# st.markdown("---")
# st.markdown("### Trade & External")
# t1, t2, t3 = st.columns(3)
# t1.metric("Exports (latest)", ex_disp)
# t2.metric("Imports (latest)", im_disp)
# t3.metric("Trade balance", tb_disp)

# st.markdown("---")
# st.markdown("### Other")
# o1, o2, o3 = st.columns(3)
# o1.metric("Military spending (latest)", mil_display)
# o2.metric("Debt-to-GDP", debt_display)
# o3.metric("Exchange rate (local per USD)", exrate_display)

# st.markdown("---")
# st.markdown("### Relative shares")
# s1, s2, s3 = st.columns(3)
# s1.metric("Share of continent", pct_cont_display)
# s2.metric("Share of world", pct_world_display)
# s3.metric("Unemployment Rate", format_percent(unemployment) if unemployment is not None else "Not available")

# st.markdown("---")
# st.markdown(
#     f"""
#     **Sources:** IMF WEO · World Bank · country ETL.  
#     **Disclaimer:** Live values use the stored base-year snapshot and pro-rata nominal growth from Jan 1 of base-year (stored_year + 1). Exchange-rate conversions come from the ETL snapshot — live USD estimates may differ slightly from other sources.
#     """
# )


import streamlit as st
from datetime import datetime, UTC # Prevent deprecation warnings

from utils.db import fetch_df
from utils.formatters import format_number, format_percent
from utils.live_counter import live_nominal_value, live_population_value

# ---------------- CONFIG ----------------
st.set_page_config(layout="wide")

# Use timezone-aware UTC for the year
CURRENT_YEAR = datetime.now(UTC).year
BASE_YEAR = CURRENT_YEAR - 1

# ----------------- SMALL SQL HELPERS -----------------
def table_has_column(table_name: str, column_name: str) -> bool:
    q = """
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s
    """
    df = fetch_df(q, (table_name, column_name))
    return bool(df.iloc[0, 0])

def get_country_list():
    q = "SELECT country_id, name, iso3, flag_url FROM countries ORDER BY name"
    return fetch_df(q)

def fetch_latest_indicator_by_country(country_id, prefer_years=None):
    if prefer_years:
        for y in prefer_years:
            df = fetch_df("SELECT * FROM economic_indicators WHERE country_id=%s AND year=%s LIMIT 1", (country_id, y))
            if not df.empty:
                return df.iloc[0].to_dict()
    df = fetch_df("SELECT * FROM economic_indicators WHERE country_id=%s ORDER BY year DESC LIMIT 1", (country_id,))
    if df.empty: return {}
    return df.iloc[0].to_dict()

def get_country_population(country_id, year_prefer=None):
    if table_has_column("country_population", "population"):
        if year_prefer:
            df = fetch_df("SELECT population, year FROM country_population WHERE country_id=%s AND year=%s LIMIT 1", (country_id, year_prefer))
            if not df.empty:
                return int(df.iloc[0]["population"]), int(df.iloc[0]["year"])
        df = fetch_df("SELECT population, year FROM country_population WHERE country_id=%s AND population IS NOT NULL ORDER BY year DESC LIMIT 1", (country_id,))
        if not df.empty:
            return int(df.iloc[0]["population"]), int(df.iloc[0]["year"])
    if table_has_column("economic_indicators", "population"):
        df = fetch_df("SELECT population, year FROM economic_indicators WHERE country_id=%s AND population IS NOT NULL ORDER BY year DESC LIMIT 1", (country_id,))
        if not df.empty:
            return int(df.iloc[0]["population"]), int(df.iloc[0]["year"])
    return None, None

def get_population_growth_rate(country_id, year):
    if table_has_column("country_population_growth", "population_growth"):
        df = fetch_df("SELECT population_growth FROM country_population_growth WHERE country_id=%s AND year=%s LIMIT 1", (country_id, year))
        if not df.empty: return float(df.iloc[0,0])
    if table_has_column("country_population", "population"):
        df = fetch_df("SELECT year, population FROM country_population WHERE country_id=%s AND population IS NOT NULL ORDER BY year DESC LIMIT 2", (country_id,))
        if len(df) >= 2:
            p_new, p_old = float(df.iloc[0]["population"]), float(df.iloc[1]["population"])
            if p_old > 0: return (p_new - p_old) / p_old * 100.0
    return None

def get_trade_for_country(country_id):
    if not table_has_column("country_trade", "exports_usd"): return None
    df = fetch_df("SELECT exports_usd, imports_usd, trade_balance_usd, year FROM country_trade WHERE country_id=%s ORDER BY year DESC LIMIT 1", (country_id,))
    return df.iloc[0].to_dict() if not df.empty else None

def get_pct_shares(country_id, iso3, continent_code, year):
    pct_cont, pct_world = None, None
    if table_has_column("country_continent_gdp_share", "pct_of_continent"):
        if table_has_column("country_continent_gdp_share", "iso3") and iso3:
            df = fetch_df("SELECT pct_of_continent FROM country_continent_gdp_share WHERE iso3=%s AND year=%s LIMIT 1", (iso3, year))
            if not df.empty: pct_cont = float(df.iloc[0,0])
    if table_has_column("country_world_gdp_share", "pct_of_world"):
        if table_has_column("country_world_gdp_share", "iso3") and iso3:
            df = fetch_df("SELECT pct_of_world FROM country_world_gdp_share WHERE iso3=%s AND year=%s LIMIT 1", (iso3, year))
            if not df.empty: pct_world = float(df.iloc[0,0])
    return pct_cont, pct_world

# ----------------- PAGE START -----------------
st.title("🌐 Country Intelligence")
st.caption("Live snapshot — Values update every second locally")
st.markdown("---")

# Country Selector
countries_df = get_country_list()
labels = [f"{r['name']} ({r['iso3']})" if r['iso3'] else r['name'] for _, r in countries_df.iterrows()]
id_map = {labels[i]: int(countries_df.iloc[i]["country_id"]) for i in range(len(labels))}
selected = st.selectbox("Search / select a country", labels, index=0)
country_id = id_map[selected]

# Static Meta Load
meta = fetch_df("SELECT country_id,name,iso2,iso3,capital,continent,continent_code,flag_url FROM countries WHERE country_id=%s LIMIT 1", (country_id,))
if meta.empty:
    st.error("Country metadata missing.")
    st.stop()
meta = meta.iloc[0]

# Display Static Header
c1, c2 = st.columns([1, 6])
if meta["flag_url"]:
    c1.image(meta["flag_url"], width=96)
c2.header(f"{meta['name']} — Live Overview")
c2.caption(f"Capital: {meta['capital'] or '—'} · ISO3: {meta['iso3'] or '—'} · Continent: {meta['continent'] or '—'}")
st.markdown("---")

# Fetch Base Data once
ind = fetch_latest_indicator_by_country(country_id, prefer_years=[BASE_YEAR, BASE_YEAR-1])
pop_val, pop_year = get_country_population(country_id, year_prefer=BASE_YEAR)
pop_growth_rate = get_population_growth_rate(country_id, CURRENT_YEAR)

# ----------------- LIVE FRAGMENT -----------------

@st.fragment(run_every="1s")
def render_live_metrics(ind, pop_val, pop_year, pop_growth_rate):
    gdp = ind.get("gdp")
    real_growth = ind.get("gdp_growth") or 0.0
    inflation = ind.get("inflation") or 0.0
    
    # Calculate Live Pop
    live_pop = None
    population_display = "Not available"
    if pop_val:
        base_year_pop = (pop_year or BASE_YEAR) + 1
        live_pop = live_population_value(pop_val, pop_growth_rate or 0.0, base_year_pop)
        population_display = format_number(int(live_pop))

    # Calculate Live GDP
    live_gdp_display = "Not available"
    live_gdp_usd = None
    if gdp is not None:
        base_for_gdp = (ind.get("year") or BASE_YEAR) + 1
        live_gdp_usd = live_nominal_value(float(gdp), real_growth, inflation, base_for_gdp)
        live_gdp_display = f"${live_gdp_usd / 1e12:,.8f} T"

    # Per Capita
    gdp_per_capita_display = "Not available"
    if live_gdp_usd and live_pop:
        gdp_per_capita_display = f"${(live_gdp_usd / live_pop):,.0f}"

    st.markdown("### Key Indicators")
    k1, k2, k3, k4 = st.columns([3,2,2,2])
    k1.metric("GDP (Live)", live_gdp_display)
    k2.metric("Population", population_display)
    k3.metric("GDP per Capita (Live)", gdp_per_capita_display)
    k4.metric("Pop Growth", format_percent(pop_growth_rate) if pop_growth_rate is not None else "N/A")

# Start fragment
render_live_metrics(ind, pop_val, pop_year, pop_growth_rate)

# ----------------- STATIC REMAINDER -----------------
st.markdown("---")
st.markdown("### Growth & Stored Data")
c5, c6, c7, c8 = st.columns([2,2,2,2])
c5.metric("Real GDP growth", format_percent(ind.get("gdp_growth")))
c6.metric("Inflation", format_percent(ind.get("inflation")))
nom_val = (ind.get("gdp_growth") or 0.0) + (ind.get("inflation") or 0.0)
c7.metric("Nominal growth (est.)", format_percent(nom_val))
c8.metric("Base GDP (stored)", f"${(float(ind.get('gdp') or 0)/1e12):,.2f} T")

# Trade & Shares (Static)
st.markdown("---")
trade = get_trade_for_country(country_id)
st.markdown("### Trade & External")
t1, t2, t3 = st.columns(3)
if trade:
    t1.metric("Exports", f"${float(trade['exports_usd'])/1e12:,.2f} T")
    t2.metric("Imports", f"${float(trade['imports_usd'])/1e12:,.2f} T")
    t3.metric("Trade balance", f"${float(trade['trade_balance_usd'])/1e12:,.2f} T")
else:
    st.write("Trade data not available.")

# Footnote
st.markdown("---")
st.caption("Sources: IMF WEO · World Bank · Local ETL Snapshots")