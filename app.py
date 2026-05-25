import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Midnight Luxury Weather Dashboard",
    page_icon="🌌",
    layout="wide"
)

# ---------------- LOAD CSS ---------------- #
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("⚙️ Dashboard Settings")

city = st.sidebar.text_input(
    "Enter City",
    value="Ahmedabad"
)

api_key = st.sidebar.text_input(
    "OpenWeather API Key",
    type="password"
)

units = st.sidebar.selectbox(
    "Select Unit",
    ["metric", "imperial"]
)

temperature_unit = "°C" if units == "metric" else "°F"

# ---------------- API ---------------- #
def get_weather(city, api_key, units):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={api_key}&units={units}"
    )
    return requests.get(url).json()


def get_forecast(city, api_key, units):
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast?"
        f"q={city}&appid={api_key}&units={units}"
    )
    return requests.get(url).json()


def get_air_pollution(lat, lon, api_key):
    url = (
        f"https://api.openweathermap.org/data/2.5/air_pollution?"
        f"lat={lat}&lon={lon}&appid={api_key}"
    )
    return requests.get(url).json()


# ---------------- BUTTON ---------------- #
if st.sidebar.button("✨ Get Weather"):

    if not api_key:
        st.warning("Please enter your API key.")
        st.stop()

    weather = get_weather(city, api_key, units)

    if weather.get("cod") != 200:
        st.error("Invalid city or API key.")
        st.stop()

    forecast = get_forecast(city, api_key, units)

    lat = weather["coord"]["lat"]
    lon = weather["coord"]["lon"]

    air = get_air_pollution(lat, lon, api_key)

    # ---------------- HERO SECTION ---------------- #
    st.markdown(
        f"""
        <div class="hero-card">
            <h1>🌌 {weather['name']}</h1>
            <h2>{weather['weather'][0]['main']}</h2>
            <h1>{weather['main']['temp']} {temperature_unit}</h1>
            <p>Feels Like: {weather['main']['feels_like']} {temperature_unit}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- METRIC CARDS ---------------- #
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>🌡 Temperature</h3>
                <h2>{weather['main']['temp']} {temperature_unit}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>💧 Humidity</h3>
                <h2>{weather['main']['humidity']}%</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>💨 Wind Speed</h3>
                <h2>{weather['wind']['speed']}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class='metric-card'>
                <h3>📊 Pressure</h3>
                <h2>{weather['main']['pressure']} hPa</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- FORECAST ---------------- #
    st.subheader("📈 Temperature Forecast")

    dates = []
    temps = []

    for item in forecast["list"]:
        dates.append(item["dt_txt"])
        temps.append(item["main"]["temp"])

    forecast_df = pd.DataFrame({
        "Date": dates,
        "Temperature": temps
    })

    fig = px.line(
        forecast_df,
        x="Date",
        y="Temperature",
        markers=True
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- AQI ---------------- #
    st.subheader("🌫 Air Quality Analytics")

    aqi = air["list"][0]["main"]["aqi"]
    components = air["list"][0]["components"]

    c1, c2 = st.columns(2)

    with c1:
        st.metric("AQI Index", aqi)

    with c2:
        pollution_df = pd.DataFrame({
            "Component": list(components.keys()),
            "Value": list(components.values())
        })

        bar_fig = px.bar(
            pollution_df,
            x="Component",
            y="Value"
        )

        bar_fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            bar_fig,
            use_container_width=True
        )

    # ---------------- MAP ---------------- #
    st.subheader("📍 Location")

    map_df = pd.DataFrame({
        "lat": [lat],
        "lon": [lon]
    })

    st.map(map_df)

    # ---------------- SUNRISE SUNSET ---------------- #
    sunrise = datetime.fromtimestamp(
        weather["sys"]["sunrise"]
    ).strftime("%I:%M %p")

    sunset = datetime.fromtimestamp(
        weather["sys"]["sunset"]
    ).strftime("%I:%M %p")

    s1, s2 = st.columns(2)

    with s1:
        st.markdown(
            f"""
            <div class='sun-card'>
                <h3>🌅 Sunrise</h3>
                <h2>{sunrise}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    with s2:
        st.markdown(
            f"""
            <div class='sun-card'>
                <h3>🌇 Sunset</h3>
                <h2>{sunset}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- FORECAST TABLE ---------------- #
    st.subheader("📋 Forecast Table")

    forecast_table = []

    for item in forecast["list"]:
        forecast_table.append({
            "Date": item["dt_txt"],
            "Temp": item["main"]["temp"],
            "Humidity": item["main"]["humidity"],
            "Weather": item["weather"][0]["main"]
        })

    table_df = pd.DataFrame(forecast_table)

    st.dataframe(
        table_df,
        use_container_width=True
    )

    csv = table_df.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name="forecast.csv",
        mime="text/csv"
    )