import streamlit as st
import pandas as pd
import plotly.express as px
import pycountry

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Climate Change Tracker", layout="wide")

# ---------------------------
# CUSTOM MODERN DARK THEME
# ---------------------------
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top left, #1C1E26, #0D0E12);
        color: #E0E0E0;
    }
    [data-testid="stSidebar"] {
        background: #14151A;
    }
    .main-title {
        font-size: 2.2em;
        color: #4FC3F7;
        font-weight: bold;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 1em;
        color: #B0BEC5;
        margin-bottom: 25px;
    }
    .metric-card {
        background: linear-gradient(180deg, rgba(30, 33, 40, 0.85), rgba(15, 16, 20, 0.95));
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.6);
        transition: all 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: scale(1.02);
        box-shadow: 0px 4px 20px rgba(79,195,247,0.3);
    }
    .stPlotlyChart {
        background: linear-gradient(180deg, rgba(25, 26, 32, 0.95), rgba(10, 11, 15, 0.95));
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    h2, h3, h4 {
        color: #4FC3F7 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER
# ---------------------------
st.markdown("<div class='main-title'> EarthMetrics — Global Climate Analysis</div>", unsafe_allow_html=True)
st.markdown("""
<div class='subtitle'>
A comprehensive data-driven visualization of global temperature trends and the pace of climate change.<br>
</div>
""", unsafe_allow_html=True)


# ---------------------------
# LOAD DATA
# ---------------------------
@st.cache_data(ttl=24*3600)
def load_data():
    df = pd.read_csv("data/GlobalLandTemperaturesByCountry.csv")
    df["dt"] = pd.to_datetime(df["dt"], errors="coerce")
    df["Year"] = df["dt"].dt.year
    df = df.dropna(subset=["AverageTemperature", "Country", "Year"])
    df = df[df["Year"] >= 1900]
    df = df.groupby(["Country", "Year"], as_index=False)["AverageTemperature"].mean()
    return df

data = load_data()

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("Filters")
min_year, max_year = int(data["Year"].min()), int(data["Year"].max())
year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (1980, max_year))

# ---------------------------
# CONTINENT MAPPING (simplified)
# ---------------------------
def map_continent(country):
    asia = ["India", "China", "Japan", "Indonesia", "Saudi Arabia"]
    europe = ["Germany", "France", "Spain", "Italy", "United Kingdom"]
    africa = ["South Africa", "Egypt", "Nigeria", "Kenya"]
    na = ["United States", "Canada", "Mexico"]
    sa = ["Brazil", "Argentina", "Chile"]
    oceania = ["Australia", "New Zealand"]
    if country in asia: return "Asia"
    if country in europe: return "Europe"
    if country in africa: return "Africa"
    if country in na: return "North America"
    if country in sa: return "South America"
    if country in oceania: return "Oceania"
    return "Other"

data["Continent"] = data["Country"].apply(map_continent)
filtered = data[(data["Year"] >= year_range[0]) & (data["Year"] <= year_range[1])]

# ---------------------------
# ---------------------------
# GLOBAL METRICS (Centered + Fixed Box Size)
# ---------------------------
st.markdown("""
<style>
.metric-container {
    display: flex;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 30px;
}
.metric-card {
    flex: 1;
    background: linear-gradient(180deg, rgba(30,33,40,0.85), rgba(15,16,20,0.95));
    border-radius: 16px;
    padding: 25px;
    text-align: center;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.6);
    transition: all 0.2s ease-in-out;
    height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.metric-card:hover {
    transform: scale(1.02);
    box-shadow: 0px 4px 20px rgba(79,195,247,0.3);
}
.metric-label {
    color: #B0BEC5;
    font-size: 16px;
}
.metric-value {
    color: #4FC3F7;
    font-size: 30px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Calculate metrics
global_avg = f"{filtered['AverageTemperature'].mean():.2f}"
warmest_year = int(filtered.loc[filtered['AverageTemperature'].idxmax(), 'Year'])
countries = len(filtered["Country"].unique())

# Render metric cards in one row
st.markdown(f"""
<div class='metric-container'>
    <div class='metric-card'>
        <div class='metric-label'> Global Average Temperature (°C)</div>
        <div class='metric-value'>{global_avg}</div>
    </div>
    <div class='metric-card'>
        <div class='metric-label'> Warmest Year</div>
        <div class='metric-value'>{warmest_year}</div>
    </div>
    <div class='metric-card'>
        <div class='metric-label'> Countries Tracked</div>
        <div class='metric-value'>{countries}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------
# ANIMATED GLOBAL MAP (Below Metrics)
# ---------------------------
st.markdown("### Global Temperature Map")

def get_iso3(country):
    try:
        return pycountry.countries.lookup(country).alpha_3
    except:
        return None

filtered["iso_alpha"] = filtered["Country"].apply(get_iso3)

fig_map = px.choropleth(
    filtered,
    locations="iso_alpha",
    locationmode="ISO-3",
    color="AverageTemperature",
    animation_frame="Year",
    color_continuous_scale="Turbo",
    range_color=(filtered["AverageTemperature"].min(), filtered["AverageTemperature"].max()),
    labels={"AverageTemperature": "Avg Temp (°C)"}
)

fig_map.update_layout(
    template="plotly_dark",
    margin=dict(l=10, r=10, t=40, b=10),
    height=550
)
st.plotly_chart(fig_map, use_container_width=True)

# ---------------------------
# BELOW MAP: TWO CHARTS (Global Trends)
# ---------------------------
col_left, col_right = st.columns(2)

# Global Average Trend
global_avg = filtered.groupby("Year")["AverageTemperature"].mean().reset_index()

with col_left:
    st.markdown("### Yearly Global Average Temperature")
    fig_trend = px.area(global_avg, x="Year", y="AverageTemperature",
                        color_discrete_sequence=["#FF9800"])
    fig_trend.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_trend, use_container_width=True)

# Rate of Change
global_avg["Change"] = global_avg["AverageTemperature"].diff()
with col_right:
    st.markdown("### Rate of Temperature Change (°C/Year)")
    fig_rate = px.line(global_avg, x="Year", y="Change",
                       color_discrete_sequence=["#00BCD4"])
    fig_rate.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_rate, use_container_width=True)

# ---------------------------
# COUNTRY-LEVEL TRENDS
# ---------------------------
st.markdown("---")
st.markdown("### Country-Specific Trends")

available_countries = sorted(filtered["Country"].unique().tolist())
selected_country = st.selectbox(
    "Select Country",
    available_countries,
    index=available_countries.index("India") if "India" in available_countries else 0
)

country_df = filtered[filtered["Country"] == selected_country]
if not country_df.empty:
    fig_country = px.line(country_df, x="Year", y="AverageTemperature",
                          title=f"{selected_country} — Temperature Trend",
                          color_discrete_sequence=["#FF7043"], markers=True)
    fig_country.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_country, use_container_width=True)
