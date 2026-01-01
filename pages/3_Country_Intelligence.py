import streamlit as st
from datetime import datetime, timezone

from utils.db import fetch_df
from utils.formatters import format_number, format_percent
from utils.live_counter import live_nominal_value, live_population_value
from utils.currency import get_rate_by_country_name

#::::::::::------------------ CONFIG --------------:::::::::::::::::
st.set_page_config(layout="wide", page_title="Country Intelligence")

# Use timezone-aware UTC
CURRENT_YEAR = datetime.now(timezone.utc).year
# stored base-year rows (e.g. 2024) are treated as Jan 1, stored_year + 1
BASE_YEAR = CURRENT_YEAR - 1

# --------::::::::::: Small SQL Helpers ::::::::::::::::::---------
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
    if df.empty:
        return {}
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
        if not df.empty:
            return float(df.iloc[0,0])
    
    if table_has_column("country_population", "population"):
        df = fetch_df("SELECT year, population FROM country_population WHERE country_id=%s AND population IS NOT NULL ORDER BY year DESC LIMIT 2", (country_id,))
        if len(df) >= 2:
            p_new = float(df.iloc[0]["population"])
            p_old = float(df.iloc[1]["population"])
            if p_old > 0:
                return (p_new - p_old) / p_old * 100.0
    return None

def get_trade_for_country(country_id):
    if not table_has_column("country_trade", "exports_usd"):
        return None
    df = fetch_df("SELECT exports_usd, imports_usd, trade_balance_usd, year FROM country_trade WHERE country_id=%s ORDER BY year DESC LIMIT 1", (country_id,))
    if df.empty:
        return None
    return df.iloc[0].to_dict()

def get_pct_shares(country_id, iso3, continent_code, year):
    pct_cont = None
    pct_world = None
    
    # try country_continent_gdp_share (by iso3 or country name)
    if table_has_column("country_continent_gdp_share", "pct_of_continent"):
        if table_has_column("country_continent_gdp_share", "iso3") and iso3:
            df = fetch_df("SELECT pct_of_continent FROM country_continent_gdp_share WHERE iso3=%s AND year=%s LIMIT 1", (iso3, year))
            if not df.empty:
                pct_cont = float(df.iloc[0,0])
        if pct_cont is None:
            name_res = fetch_df("SELECT name FROM countries WHERE country_id=%s LIMIT 1", (country_id,))
            if not name_res.empty:
                df = fetch_df("SELECT pct_of_continent FROM country_continent_gdp_share WHERE country=%s AND year=%s LIMIT 1", (name_res.iloc[0,0], year))
                if not df.empty:
                    pct_cont = float(df.iloc[0,0])
                    
    # try world share view
    if table_has_column("country_world_gdp_share", "pct_of_world"):
        if table_has_column("country_world_gdp_share", "iso3") and iso3:
            df = fetch_df("SELECT pct_of_world FROM country_world_gdp_share WHERE iso3=%s AND year=%s LIMIT 1", (iso3, year))
            if not df.empty:
                pct_world = float(df.iloc[0,0])
        if pct_world is None:
            name_res = fetch_df("SELECT name FROM countries WHERE country_id=%s LIMIT 1", (country_id,))
            if not name_res.empty:
                df = fetch_df("SELECT pct_of_world FROM country_world_gdp_share WHERE country=%s AND year=%s LIMIT 1", (name_res.iloc[0,0], year))
                if not df.empty:
                    pct_world = float(df.iloc[0,0])
                    
    # fallback compute using aggregates
    if pct_cont is None or pct_world is None:
        df_g = fetch_df("SELECT gdp FROM economic_indicators WHERE country_id=%s AND year=%s LIMIT 1", (country_id, year))
        if df_g.empty:
            df_g = fetch_df("SELECT gdp FROM economic_indicators WHERE country_id=%s AND gdp IS NOT NULL ORDER BY year DESC LIMIT 1", (country_id,))
        country_gdp = float(df_g.iloc[0]["gdp"]) if not df_g.empty else None
        
        if pct_cont is None and country_gdp is not None and continent_code:
            df_cont = fetch_df("SELECT gdp_usd FROM continent_nominal_gdp WHERE continent_code=%s AND year=%s LIMIT 1", (continent_code, year))
            if not df_cont.empty and df_cont.iloc[0,0] is not None:
                cont_usd = float(df_cont.iloc[0,0]) * 1e9
                if cont_usd > 0:
                    pct_cont = country_gdp / cont_usd * 100.0
                    
        if pct_world is None and country_gdp is not None:
            df_world = fetch_df("SELECT SUM(gdp_usd) AS world_sum_billion FROM continent_nominal_gdp WHERE year=%s", (year,))
            if not df_world.empty and df_world.iloc[0,0] is not None:
                world_usd = float(df_world.iloc[0,0]) * 1e9
                if world_usd > 0:
                    pct_world = country_gdp / world_usd * 100.0
                    
    return pct_cont, pct_world

# ----------------- PAGE START ---------------------------------------------------------------
st.title("🌐 Country Intelligence")
st.caption("Live snapshot — Real-time values calculated locally")
st.markdown("---")

# 1. Selector (static)----
countries_df = get_country_list()
labels = [f"{r['name']} ({r['iso3']})" if r['iso3'] else r['name'] for _, r in countries_df.iterrows()]
id_map = {labels[i]: int(countries_df.iloc[i]["country_id"]) for i in range(len(labels))}

# SET DEFAULT AS INDIA
default_idx = 0
for i, label in enumerate(labels):
    if "(IND)" in label:
        default_idx = i
        break

selected = st.selectbox("Search / select a country", labels, index=default_idx)
country_id = id_map[selected]

#2.Fetch Metadata (Static) :-
meta_df = fetch_df("SELECT country_id,name,iso2,iso3,capital,continent,continent_code,flag_url FROM countries WHERE country_id=%s LIMIT 1", (country_id,))
if meta_df.empty:
    st.error("Country metadata missing.")
    st.stop()
meta = meta_df.iloc[0]

#header row
c1, c2 = st.columns([1, 6])
if meta["flag_url"]:
    c1.image(meta["flag_url"], width=96)
c2.header(f"{meta['name']} — Live Overview")
c2.caption(f"Capital: {meta['capital'] or '—'} · ISO3: {meta['iso3'] or '—'} · Continent: {meta.get('continent') or '—'}")
st.markdown("---")

#3.Data Extraction for calculations
ind = fetch_latest_indicator_by_country(country_id, prefer_years=[BASE_YEAR, BASE_YEAR-1, BASE_YEAR-2])
pop_val, pop_year = get_country_population(country_id, year_prefer=BASE_YEAR)
if pop_val is None and ind.get("population"):
    pop_val = int(ind.get("population"))
    pop_year = ind.get("year")
pop_growth_rate = get_population_growth_rate(country_id, CURRENT_YEAR)

#.....Live Fragments...........
# This part updates every second without reloading the whole page or DB queries as implementing fragments......

@st.fragment(run_every="1s")
def render_live_metrics(indicator_dict, p_val, p_year, p_growth):
    # Population calculation
    live_pop = None
    population_display = "Not available"
    if p_val:
        p_base = (p_year or BASE_YEAR) + 1
        live_pop = live_population_value(p_val, p_growth or 0.0, p_base)
        population_display = format_number(int(live_pop))

    # GDP calculation
    gdp_val = indicator_dict.get("gdp")
    live_gdp_display = "Not available"
    live_gdp_usd = None
    if gdp_val is not None:
        try:
            g_base = (indicator_dict.get("year") or BASE_YEAR) + 1
            live_gdp_usd = live_nominal_value(
                float(gdp_val), 
                indicator_dict.get("gdp_growth") or 0.0, 
                indicator_dict.get("inflation") or 0.0, 
                g_base
            )
            live_gdp_display = f"${live_gdp_usd / 1e12:,.8f} T"
        except: pass

    # Per Capita
    gdp_pc_display = "Not available"
    if live_gdp_usd and live_pop:
        gdp_pc_display = f"${(live_gdp_usd / live_pop):,.0f}"

    st.markdown("### Key Indicators")
    k1, k2, k3, k4 = st.columns([3,2,2,2])
    k1.metric("GDP (Live)", live_gdp_display)
    k2.metric("Population", population_display)
    k3.metric("GDP per Capita (Live)", gdp_pc_display)
    k4.metric("Population growth", format_percent(p_growth) if p_growth is not None else "Not available")

#call frag.
render_live_metrics(ind, pop_val, pop_year, pop_growth_rate)

#---- STATIC REMAINDER ---
st.markdown("---")
k5, k6, k7, k8 = st.columns([2,2,2,2])
k5.metric("Real GDP growth", format_percent(ind.get("gdp_growth")))
k6.metric("Inflation", format_percent(ind.get("inflation")))
nom_val = (ind.get("gdp_growth") or 0.0) + (ind.get("inflation") or 0.0)
k7.metric("Nominal growth (est.)", format_percent(nom_val))
k8.metric("Base GDP (stored)", f"${(float(ind.get('gdp') or 0)/1e12):,.2f} T")

# Trade Section
st.markdown("---")
st.markdown("### Trade & External")
trade = get_trade_for_country(country_id)
t1, t2, t3 = st.columns(3)
if trade:
    ex = trade.get("exports_usd"); im = trade.get("imports_usd"); tb = trade.get("trade_balance_usd")
    t1.metric("Exports (latest)", f"${float(ex)/1e12:,.2f} T" if ex is not None else "Not available")
    t2.metric("Imports (latest)", f"${float(im)/1e12:,.2f} T" if im is not None else "Not available")
    t3.metric("Trade balance", f"${float(tb)/1e12:,.2f} T" if tb is not None else "Not available")
else:
    st.write("Trade data not available.")

# Military & Debt
st.markdown("---")
st.markdown("### Other")
o1, o2, o3 = st.columns(3)

# Military Spending Logic
m_spending = ind.get("military_spending") or ind.get("military")
mil_display = "Not available"
if m_spending:
    mil_display = f"${float(m_spending)/1e9:,.2f} B"
elif table_has_column("country_military_share", "military_spending"):
    dfm = fetch_df("SELECT military_spending FROM country_military_share WHERE country=%s ORDER BY year DESC LIMIT 1", (meta["name"],))
    if not dfm.empty:
        mil_display = f"${float(dfm.iloc[0,0])/1e9:,.2f} B"

o1.metric("Military spending (latest)", mil_display)
debt_val = ind.get("debt_gdp") or ind.get("debt_to_gdp")
o2.metric("Debt-to-GDP", format_percent(debt_val) if debt_val is not None else "Not available")

# Use the name you already have (e.g., "India", "Brazil")
country_name = meta.get("name") 

if country_name:
    rate, code = get_rate_by_country_name(country_name)
    
    if rate:
        o3.metric(
            label=f"Exchange rate (USD/{code})", 
            value=f"{rate:,.2f} {code}",
            help=f"Live rate for 1 USD in {country_name}"
        )
    else:
        o3.metric("Exchange rate", "Not available")
else:
    o3.metric("Exchange rate", "No Country Selected")


# Shares Section
st.markdown("---")
st.markdown("### Relative shares")
pct_cont, pct_world = get_pct_shares(country_id, meta["iso3"], meta["continent_code"], BASE_YEAR)
s1, s2, s3 = st.columns(3)
s1.metric("Share of continent", format_percent(pct_cont) if pct_cont is not None else "Not available")
s2.metric("Share of world", format_percent(pct_world) if pct_world is not None else "Not available")
s3.metric("Unemployment Rate", format_percent(ind.get("unemployment")) if ind.get("unemployment") is not None else "Not available")

#----------------- Footer-----------------------------
st.markdown("---")
st.markdown(
    f"""
    **Sources:** IMF WEO · World Bank · country ETL.  
    **Disclaimer:** Live values use the stored base-year snapshot and pro-rata nominal growth. No page flicker occurs as calculations are isolated in fragments.
    """
)