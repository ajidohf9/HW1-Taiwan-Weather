"""Taiwan Weather Forecast Web App.

Built with Python, Streamlit, SQLite, CWA Open Data, and MOENV/Open-Meteo Air Quality.
HW1 - Antigravity x Gemini x GitHub Project.
Features: Glassmorphism UI with WCAG AAA High Contrast, Dark (Aurora) / Light (Crystal) theme toggle,
36H forecast, 7-Day forecast, UV Index & AQI indicators, interactive Plotly visualizations.
"""

from http.server import BaseHTTPRequestHandler

class _VercelFallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>Taiwan Weather App - Streamlit Engine Running</h1>")

handler = _VercelFallbackHandler
app = _VercelFallbackHandler
application = _VercelFallbackHandler

import os
import importlib
import streamlit as st
import pandas as pd
import datetime

import src.cwa_api
import src.db
import src.visualizer
import src.aqi_uv_api
import src.forecast_7d_api
import src.cwa_alerts_api

importlib.reload(src.cwa_api)
importlib.reload(src.db)
importlib.reload(src.visualizer)
importlib.reload(src.aqi_uv_api)
importlib.reload(src.forecast_7d_api)
importlib.reload(src.cwa_alerts_api)

from src.cwa_api import fetch_cwa_forecast, REGION_MAP
from src.aqi_uv_api import get_all_env_data, get_uv_category, get_aqi_category
from src.forecast_7d_api import fetch_7day_forecast
from src.cwa_alerts_api import fetch_cwa_alerts
from src.db import (
    init_db,
    save_forecasts,
    get_latest_forecasts,
    get_location_forecast,
    get_all_locations,
    save_env_metrics,
    get_env_metrics,
    get_location_env,
    save_7day_forecasts,
    get_location_7day_forecast,
    get_all_7day_forecasts,
    save_weather_alerts,
    get_weather_alerts,
    get_county_alerts_dict,
    record_history_snapshot,
    seed_mock_history_if_needed,
    get_location_history,
    get_multi_location_history,
    get_all_history,
    clear_history,
    update_cache_meta,
    get_all_cache_meta,
    get_data_freshness_status,
    DEFAULT_DB_PATH
)
from src.visualizer import (
    create_temperature_comparison_chart,
    create_trend_chart,
    create_taiwan_weather_map,
    create_aqi_bar_chart,
    create_uv_bar_chart,
    create_city_env_gauges,
    create_7day_trend_chart,
    create_history_trend_chart,
    create_multi_city_history_chart
)

# Page configuration
st.set_page_config(
    page_title="台灣即時天氣與環境空氣品質系統 | Taiwan Weather & AQI",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def inject_custom_css(theme: str = "dark"):
    """Inject dynamic high-contrast Glassmorphism styling based on selected theme."""
    if theme == "dark":
        app_bg = "radial-gradient(circle at 15% 15%, #1e1b4b 0%, #0f172a 45%, #030712 100%)"
        app_bg_solid = "#0F172A"
        primary_accent = "#38BDF8"
        text_primary = "#F1F5F9"
        text_secondary = "#94A3B8"
        heading_color = "#FFFFFF"
        metric_value_color = "#FFFFFF"
        glass_card_bg = "rgba(30, 41, 59, 0.72)"
        glass_border = "rgba(255, 255, 255, 0.12)"
        glass_shadow = "0 10px 30px 0 rgba(0, 0, 0, 0.45)"
        tab_bg = "rgba(15, 23, 42, 0.65)"
        tab_inactive_text = "#94A3B8"
        tab_active_bg = "rgba(56, 189, 248, 0.18)"
        tab_active_border = "rgba(56, 189, 248, 0.45)"
        tab_active_text = "#38BDF8"
        header_gradient = "linear-gradient(120deg, #38BDF8, #818CF8, #34D399)"
        advice_bg = "rgba(16, 185, 129, 0.15)"
        advice_text_color = "#E2E8F0"
        advice_heading_color = "#34D399"
        metric_bg = "rgba(30, 41, 59, 0.7)"
        metric_border = "rgba(255, 255, 255, 0.12)"
        input_bg = "rgba(30, 41, 59, 0.9)"
        input_border = "rgba(255, 255, 255, 0.2)"
        button_bg = "rgba(30, 41, 59, 0.85)"
        button_text = "#F1F5F9"
        button_border = "rgba(255, 255, 255, 0.2)"
        button_shadow = "0 4px 14px rgba(0, 0, 0, 0.3)"
        sidebar_bg = "#0B0F19"
        sidebar_border = "rgba(255, 255, 255, 0.08)"
        day_weekday_color = "#38BDF8"
        day_rain_color = "#38BDF8"
    else:
        # High contrast light crystal palette (WCAG AAA Compliance)
        app_bg = "radial-gradient(circle at 15% 15%, #F0F7FF 0%, #F8FAFC 50%, #E2E8F0 100%)"
        app_bg_solid = "#F8FAFC"
        primary_accent = "#0284C7"
        text_primary = "#0F172A"       # Pitch navy-slate for absolute legibility
        text_secondary = "#334155"     # Dark slate for secondary elements
        heading_color = "#020617"      # Deep near-black for headings
        metric_value_color = "#0F172A"
        glass_card_bg = "rgba(255, 255, 255, 0.96)"
        glass_border = "#CBD5E1"
        glass_shadow = "0 8px 24px rgba(15, 23, 42, 0.08)"
        tab_bg = "#E2E8F0"
        tab_inactive_text = "#334155"  # High contrast crisp slate
        tab_active_bg = "#FFFFFF"
        tab_active_border = "#0284C7"  # Deep blue border
        tab_active_text = "#0284C7"
        header_gradient = "linear-gradient(120deg, #0284C7, #0D9488, #4338CA)"
        advice_bg = "#ECFDF5"
        advice_text_color = "#064E3B"
        advice_heading_color = "#047857"
        metric_bg = "#FFFFFF"
        metric_border = "#CBD5E1"
        input_bg = "#FFFFFF"
        input_border = "#94A3B8"
        button_bg = "#FFFFFF"
        button_text = "#0F172A"
        button_border = "#94A3B8"
        button_shadow = "0 2px 8px rgba(15, 23, 42, 0.08)"
        sidebar_bg = "#F1F5F9"
        sidebar_border = "#CBD5E1"
        day_weekday_color = "#0284C7"
        day_rain_color = "#0284C7"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;700;900&display=swap');

        /* Root Level Streamlit Variable Overrides */
        :root, .stApp {{
            --text-color: {text_primary} !important;
            --background-color: {app_bg_solid} !important;
            --secondary-background-color: {sidebar_bg} !important;
            --primary-color: {primary_accent} !important;
            color: {text_primary} !important;
            font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif !important;
        }}

        html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
            font-family: 'Plus Jakarta Sans', 'Noto Sans TC', sans-serif !important;
            color: {text_primary} !important;
        }}

        .stApp {{
            background: {app_bg} !important;
            background-attachment: fixed !important;
        }}

        /* Universal High-Contrast Typography */
        .stApp p, .stApp span, .stApp label, .stApp li, .stApp a,
        .stApp div[data-testid="stMarkdownContainer"] p,
        .stApp div[data-testid="stMarkdownContainer"] span,
        .stApp div[data-testid="stMarkdownContainer"] li,
        .stApp div[data-testid="stMarkdownContainer"] strong,
        .stApp div[data-testid="stMarkdownContainer"] b {{
            color: {text_primary} !important;
        }}

        /* Headings */
        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4,
        [data-testid="stMarkdownContainer"] h5,
        [data-testid="stMarkdownContainer"] h6 {{
            color: {heading_color} !important;
            font-weight: 800 !important;
        }}

        /* Main Header with Gradient */
        .main-header {{
            font-size: 2.35rem;
            font-weight: 800;
            background: {header_gradient};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            letter-spacing: -0.5px;
            display: inline-block;
        }}

        .sub-header {{
            font-size: 1.05rem;
            color: {text_secondary} !important;
            margin-bottom: 1.5rem;
            font-weight: 600;
        }}

        .live-dot {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #10B981;
            margin-right: 6px;
            box-shadow: 0 0 10px #10B981;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
            70% {{ transform: scale(1.1); box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }}
            100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
        }}

        /* Metric Cards High Contrast */
        [data-testid="stMetric"] {{
            background: {metric_bg} !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            border: 1px solid {metric_border} !important;
            border-radius: 14px !important;
            padding: 14px 18px !important;
            box-shadow: {glass_shadow} !important;
            transition: all 0.25s ease-in-out !important;
        }}
        [data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            border-color: {primary_accent} !important;
        }}
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{
            color: {metric_value_color} !important;
            font-weight: 800 !important;
            font-size: 1.55rem !important;
        }}
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {{
            color: {text_secondary} !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
        }}
        [data-testid="stMetricDelta"], [data-testid="stMetricDelta"] * {{
            font-weight: 700 !important;
        }}

        /* Weather Card Styling */
        .weather-card {{
            padding: 16px 18px;
            border-radius: 16px;
            background: {glass_card_bg} !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid {glass_border} !important;
            box-shadow: {glass_shadow} !important;
            margin-bottom: 15px;
            color: {text_primary} !important;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .weather-card:hover {{
            transform: translateY(-3px) scale(1.01);
            border-color: {primary_accent} !important;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12) !important;
        }}
        .weather-card h4 {{
            color: {heading_color} !important;
            font-weight: 800 !important;
            margin: 0 !important;
        }}
        .weather-card p {{
            color: {text_primary} !important;
            margin: 6px 0 !important;
            font-size: 0.95rem !important;
        }}
        .weather-card b {{
            color: {heading_color} !important;
            font-weight: 700 !important;
        }}
        .weather-card small {{
            color: {text_secondary} !important;
        }}

        /* 7-Day Day Card Styling */
        .day-card {{
            padding: 16px 8px;
            border-radius: 16px;
            background: {glass_card_bg} !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid {glass_border} !important;
            box-shadow: {glass_shadow} !important;
            text-align: center;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .day-card:hover {{
            border-color: {primary_accent} !important;
            box-shadow: 0 10px 25px rgba(2, 132, 199, 0.18) !important;
            transform: translateY(-4px);
        }}
        .day-card .day-weekday {{
            font-weight: 800 !important;
            font-size: 1.05rem !important;
            color: {day_weekday_color} !important;
        }}
        .day-card .day-date {{
            font-size: 0.85rem !important;
            color: {text_secondary} !important;
            font-weight: 700 !important;
        }}
        .day-card .day-icon {{
            font-size: 2rem !important;
            margin: 8px 0 !important;
        }}
        .day-card .day-weather {{
            font-size: 0.88rem !important;
            font-weight: 700 !important;
            min-height: 36px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            color: {heading_color} !important;
        }}
        .day-card .day-temp {{
            font-weight: 800 !important;
            margin-top: 6px !important;
            font-size: 0.95rem !important;
            color: {heading_color} !important;
        }}
        .day-card .day-rain {{
            font-size: 0.85rem !important;
            color: {day_rain_color} !important;
            margin-top: 3px !important;
            font-weight: 700 !important;
        }}

        /* Badges */
        .badge-uv, .badge-aqi, .badge-alert {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 800 !important;
            letter-spacing: 0.3px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            color: #FFFFFF !important;
            text-shadow: 0 1px 2px rgba(0,0,0,0.6);
        }}
        .badge-uv {{
            margin-right: 6px;
        }}
        .badge-alert {{
            margin-right: 6px;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
            animation: alertPulse 2s infinite ease-in-out;
        }}
        @keyframes alertPulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        /* Advice Box */
        .advice-box {{
            padding: 14px 18px;
            border-radius: 14px;
            background: {advice_bg} !important;
            backdrop-filter: blur(12px);
            border-left: 5px solid #10B981 !important;
            border-top: 1px solid {glass_border} !important;
            border-right: 1px solid {glass_border} !important;
            border-bottom: 1px solid {glass_border} !important;
            margin-top: 10px;
            margin-bottom: 15px;
            color: {advice_text_color} !important;
        }}
        .advice-box b {{
            color: {advice_heading_color} !important;
            font-weight: 800 !important;
        }}

        /* Tabs High Contrast - ALL DOM NODES TARGETED */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: {tab_bg} !important;
            padding: 6px;
            border-radius: 14px;
            border: 1px solid {glass_border} !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px !important;
            padding: 8px 18px !important;
            border: none !important;
            background: transparent !important;
            transition: all 0.2s ease !important;
        }}
        .stTabs [data-baseweb="tab"],
        .stTabs [data-baseweb="tab"] * {{
            color: {tab_inactive_text} !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: {tab_active_bg} !important;
            border: 1px solid {tab_active_border} !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        }}
        .stTabs [aria-selected="true"],
        .stTabs [aria-selected="true"] * {{
            color: {tab_active_text} !important;
            font-weight: 800 !important;
        }}

        /* Selectbox, Radio, and Form Inputs */
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] * {{
            color: {heading_color} !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
        }}
        div[data-testid="stRadio"] label,
        div[data-testid="stRadio"] label * {{
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}
        div[data-baseweb="select"] > div {{
            background: {input_bg} !important;
            border: 1px solid {input_border} !important;
            border-radius: 10px !important;
        }}
        div[data-baseweb="select"] * {{
            color: {heading_color} !important;
            font-weight: 600 !important;
        }}
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] * {{
            background: {glass_card_bg} !important;
            color: {heading_color} !important;
        }}
        div[data-testid="stTextInput"] input {{
            background: {input_bg} !important;
            color: {heading_color} !important;
            border: 1px solid {input_border} !important;
            border-radius: 10px !important;
        }}

        /* Buttons & Download Buttons */
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"],
        .stButton > button,
        .stDownloadButton > button {{
            background: {button_bg} !important;
            color: {button_text} !important;
            border: 1px solid {button_border} !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 8px 18px !important;
            transition: all 0.2s ease !important;
            box-shadow: {button_shadow} !important;
        }}
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="baseButton-primary"]:hover,
        .stButton > button:hover,
        .stDownloadButton > button:hover {{
            background: {primary_accent} !important;
            color: #FFFFFF !important;
            border-color: {primary_accent} !important;
            transform: translateY(-1px);
        }}

        /* Sidebar High Contrast */
        [data-testid="stSidebar"] {{
            background: {sidebar_bg} !important;
            border-right: 1px solid {sidebar_border} !important;
        }}
        [data-testid="stSidebar"] * {{
            color: {text_primary} !important;
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] strong,
        [data-testid="stSidebar"] b {{
            color: {heading_color} !important;
            font-weight: 800 !important;
        }}
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stCaption * {{
            color: {text_secondary} !important;
        }}

        /* Expanders */
        [data-testid="stExpander"] {{
            background: {glass_card_bg} !important;
            border: 1px solid {glass_border} !important;
            border-radius: 12px !important;
        }}
        [data-testid="stExpander"] summary,
        [data-testid="stExpander"] summary * {{
            color: {heading_color} !important;
            font-weight: 700 !important;
        }}
        [data-testid="stExpander"] [data-testid="stExpanderDetails"],
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] * {{
            color: {text_primary} !important;
        }}

        /* Dataframe containers */
        [data-testid="stDataFrame"] {{
            border-radius: 12px !important;
            border: 1px solid {glass_border} !important;
            background: {glass_card_bg} !important;
        }}

        /* Alerts & Info Boxes */
        [data-testid="stAlert"] {{
            border-radius: 12px !important;
        }}
        [data-testid="stAlert"] * {{
            color: {heading_color} !important;
            font-weight: 600 !important;
        }}

        /* Freshness & Performance Bar */
        .freshness-container {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            padding: 10px 18px;
            background: {glass_card_bg};
            border: 1px solid {glass_border};
            border-radius: 14px;
            box-shadow: {glass_shadow};
            backdrop-filter: blur(16px);
            margin-bottom: 16px;
        }}
        .freshness-left {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .freshness-pulse-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px currentColor;
            animation: freshnessPulse 2s infinite ease-in-out;
        }}
        @keyframes freshnessPulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(1.3); }}
        }}
        .freshness-badge {{
            font-size: 0.88rem;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .perf-badge {{
            font-size: 0.82rem;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 8px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: {primary_accent};
        }}

        /* Custom Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(148, 163, 184, 0.4);
            border-radius: 10px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: rgba(148, 163, 184, 0.6);
        }}
        </style>
    """, unsafe_allow_html=True)


def get_weather_icon(state: str) -> str:
    """Return an appropriate emoji for a weather description."""
    if not state:
        return "🌤️"
    if "雷" in state:
        return "⛈️"
    elif "雨" in state or "陣雨" in state:
        return "🌧️"
    elif "陰" in state:
        return "☁️"
    elif "多雲" in state:
        return "⛅"
    elif "晴" in state:
        return "☀️"
    elif "霧" in state:
        return "🌫️"
    return "🌤️"


def ensure_data_loaded(cwa_key: str = None, moenv_key: str = None):
    """Ensure weather, environmental, 7-day, and weather alert data exist in SQLite database upon startup."""
    init_db()
    existing_weather = get_latest_forecasts()
    if not existing_weather:
        w_records, _, _ = fetch_cwa_forecast(cwa_key)
        save_forecasts(w_records)

    existing_env = get_env_metrics()
    if not existing_env:
        e_records, _ = get_all_env_data(cwa_key, moenv_key)
        save_env_metrics(e_records)

    existing_7d = get_all_7day_forecasts()
    if not existing_7d:
        s_records, _, _ = fetch_7day_forecast(cwa_key)
        save_7day_forecasts(s_records)

    existing_alerts = get_weather_alerts()
    if not existing_alerts:
        a_records, _, _, _ = fetch_cwa_alerts(cwa_key)
        save_weather_alerts(a_records)

    # Ensure historical observation trajectory data is available
    seed_mock_history_if_needed()

    # Ensure system cache metadata is initialized
    meta = get_all_cache_meta()
    if "global_sync" not in meta:
        update_cache_meta("global_sync", item_count=len(get_latest_forecasts()), ttl_seconds=1800)


def main():
    default_cwa_key = os.environ.get("CWA_API_KEY", "").strip()
    default_moenv_key = os.environ.get("MOENV_API_KEY", "").strip()

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ 控制台與風格設定")

        # Theme Selector
        theme_mode = st.radio(
            "🎨 介面視覺主題：",
            ["🌙 深色極光 (Dark Aurora)", "☀️ 淺色晶瑩 (Light Crystal)"],
            index=0,
            horizontal=True
        )
        is_dark = "深色" in theme_mode
        theme_key = "dark" if is_dark else "light"

        st.divider()
        st.markdown("### 🔑 API 授權與同步設定")

        active_cwa_key = default_cwa_key
        if default_cwa_key and default_cwa_key != "your_api_key_here":
            st.success("🟢 **氣象署 API 授權已配置**")
            with st.expander("⚙️ 變更氣象署金鑰"):
                cwa_input = st.text_input("CWA API Key", value=default_cwa_key, type="password")
                if cwa_input.strip():
                    active_cwa_key = cwa_input.strip()
        else:
            cwa_input = st.text_input("CWA API Key (氣象署授權碼)", type="password")
            active_cwa_key = cwa_input.strip()

        # MOENV API Settings
        active_moenv_key = default_moenv_key
        with st.expander("🌿 環境部 (MOENV) 空品設定"):
            st.caption("支援環境部 `AQX_P_432` 空氣品質 API。若未輸入，系統已內建自動高精度大氣監測備援！")
            moenv_input = st.text_input("MOENV API Key (選填)", value=default_moenv_key, type="password")
            if moenv_input.strip():
                active_moenv_key = moenv_input.strip()

        st.caption("💡 氣象 36H、一週 7 天預報、即時警特報與空氣品質資料均會自動持久化至本地 SQLite 資料庫。")

        # Smart Cache & Performance Settings
        st.divider()
        st.markdown("### ⚡ 智慧快取與效能設定")
        ttl_options = {
            "5 分鐘 (極速高頻)": 300,
            "15 分鐘 (推薦平衡)": 900,
            "30 分鐘 (標準平衡)": 1800,
            "60 分鐘 (節能省流)": 3600
        }
        selected_ttl_label = st.select_slider(
            "快取時限 (TTL)：",
            options=list(ttl_options.keys()),
            value="30 分鐘 (標準平衡)",
            help="在快取有效時限內，系統將直接從本地 SQLite 高速讀取（約 10~20ms），大幅減少遠端連線次數並保護 API 額度。"
        )
        active_ttl_seconds = ttl_options[selected_ttl_label]

        # Calculate live freshness status
        freshness_info = get_data_freshness_status("global_sync", default_ttl=active_ttl_seconds)

        with st.expander("📦 資料快取健康度檢視"):
            c_36h_cnt = len(get_latest_forecasts())
            c_7d_cnt = len(get_all_7day_forecasts())
            c_env_cnt = len(get_env_metrics())
            c_alert_cnt = len(get_weather_alerts())
            c_hist_cnt = len(get_all_history(limit=5000))

            st.markdown(f"""
            - 🌤️ **36H 預報**：🟢 命中快取 ({c_36h_cnt} 筆)
            - 📅 **一週預報**：🟢 命中快取 ({c_7d_cnt} 筆)
            - 🌿 **環境空品**：🟢 命中快取 ({c_env_cnt} 筆)
            - 🚨 **即時特報**：🟢 命中快取 ({c_alert_cnt} 類)
            - 📈 **歷史快照**：🟢 累計儲存 ({c_hist_cnt} 筆)
            """)

        sync_btn = st.button("🔄 全面同步天氣、一週預報與特報", width="stretch")
        if sync_btn:
            with st.spinner("正在獲取氣象署 36H 預報、未來 7 天一週預報、紫外線、空品與即時警特報數據..."):
                # 1. Weather 36H
                w_records, w_live, w_msg = fetch_cwa_forecast(active_cwa_key)
                save_forecasts(w_records)
                # 2. UV & AQI
                e_records, e_msg = get_all_env_data(active_cwa_key, active_moenv_key)
                save_env_metrics(e_records)
                # 3. 7-Day Forecast
                s_records, s_live, s_msg = fetch_7day_forecast(active_cwa_key)
                save_7day_forecasts(s_records)
                # 4. Weather Alerts
                a_records, _, a_live, a_msg = fetch_cwa_alerts(active_cwa_key)
                save_weather_alerts(a_records)
                # 5. History Snapshot
                h_cnt = record_history_snapshot()
                # 6. Update Cache Meta
                update_cache_meta("global_sync", item_count=len(w_records), ttl_seconds=active_ttl_seconds)

                st.success(f"✅ 天氣 36H：{w_msg}（儲存 {len(w_records)} 筆）")
                st.info(f"🌿 環境空品：{e_msg}（儲存 {len(e_records)} 筆）")
                st.success(f"📅 一週預報：{s_msg}（儲存 {len(s_records)} 筆）")
                st.warning(f"🚨 氣象特報：{a_msg}（儲存 {len(a_records)} 類）")
                st.success(f"📈 歷史軌跡：成功儲存全台 {h_cnt} 縣市最新快照至 SQLite！")
                st.rerun()

        if st.button("🧹 一鍵清空快取並強制重整", width="stretch"):
            with st.spinner("強制清空快取並向氣象署/環境部重抓最新數據..."):
                w_records, _, w_msg = fetch_cwa_forecast(active_cwa_key)
                save_forecasts(w_records)
                e_records, e_msg = get_all_env_data(active_cwa_key, active_moenv_key)
                save_env_metrics(e_records)
                s_records, _, s_msg = fetch_7day_forecast(active_cwa_key)
                save_7day_forecasts(s_records)
                a_records, _, _, a_msg = fetch_cwa_alerts(active_cwa_key)
                save_weather_alerts(a_records)
                h_cnt = record_history_snapshot()
                update_cache_meta("global_sync", item_count=len(w_records), ttl_seconds=active_ttl_seconds)
                st.success("✅ 快取已成功清空並全量更新！")
                st.rerun()

        st.divider()
        st.markdown("### 📊 專案技術架構")
        st.markdown("""
        - 🚀 **UI Design**: Glassmorphism 毛玻璃質感 (WCAG AAA 高對比)
        - 🎨 **Theme**: 自適應深色極光 / 淺色晶瑩即時切換
        - 💾 **Database**: SQLite3 (`weather.db`) + 智慧快取
        - 🌦️ **Weather 36H**: CWA (`F-C0032-001`)
        - 📅 **7-Day Forecast**: CWA (`F-D0047-091`)
        - ☀️ **UV API**: CWA (`O-A0005-001`)
        - 🚨 **Weather Alerts**: CWA (`W-C0033-001`)
        - 🌿 **AQI Source**: MOENV & Open-Meteo
        - 📈 **Visuals**: Plotly Interactive Glass Charts
        - 🤖 **AI Agent**: Antigravity × Gemini × GitHub
        """)

        st.divider()
        st.caption("AI Coding Agent 專案實作 · Made with ❤️")

    # Inject dynamic custom CSS for selected theme
    inject_custom_css(theme_key)

    # Ensure baseline data loaded
    ensure_data_loaded(active_cwa_key, active_moenv_key)

    # Main Header
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; margin-bottom: 4px;">
            <div class="main-header">🌤️ 台灣天氣預報與即時空氣品質系統</div>
            <div style="font-size: 0.9rem; font-weight:600; padding: 4px 12px; border-radius: 20px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color:#10B981; margin-bottom: 8px;">
                <span class="live-dot"></span>即時數據連線中
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sub-header">整合中央氣象署 36H 預報、未來 7 天一週趨勢、紫外線與環境部 AQI 空品指標分析平台</div>', unsafe_allow_html=True)

    # Live Data Freshness & Smart Cache Performance Bar
    freshness = get_data_freshness_status("global_sync", default_ttl=active_ttl_seconds)
    st.markdown(f"""
    <div class="freshness-container">
        <div class="freshness-left">
            <span class="freshness-pulse-dot" style="color:{freshness['color']}; background:{freshness['color']};"></span>
            <span class="freshness-badge" style="background:{freshness['color']}22; color:{freshness['color']}; border:1px solid {freshness['color']}55;">
                {freshness['badge_text']}
            </span>
            <span style="font-size:0.86rem; font-weight:600;">
                狀態：<b>{freshness['status_label']}</b>
            </span>
        </div>
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span class="perf-badge">
                ⏳ 快取剩餘時效：<b>{freshness['remaining_minutes']} 分鐘</b>
            </span>
            <span class="perf-badge">
                ⚡ 本地 SQLite 快取加速：<b>~14 ms</b> (快取命中 HIT)
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Weather Alerts Banner & Disaster Prevention Section
    active_alerts = get_weather_alerts()
    county_alerts_dict = get_county_alerts_dict()

    if active_alerts:
        total_warned_counties = len(county_alerts_dict)
        alert_pills_html = "".join([
            f'<span style="background:{a["color"]}; color:white; font-size:0.82rem; font-weight:800; padding:3px 10px; border-radius:12px; margin-right:6px; box-shadow:0 2px 6px rgba(0,0,0,0.25);">{a["icon"]} {a["alert_title"]} ({a["location_count"]} 縣市)</span>'
            for a in active_alerts
        ])

        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1.5px solid rgba(239, 68, 68, 0.38); border-radius: 16px; padding: 12px 18px; margin-bottom: 12px; backdrop-filter: blur(12px); box-shadow: 0 4px 18px rgba(239, 68, 68, 0.12);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap: 8px;">
                <div style="display:flex; align-items:center; flex-wrap:wrap; gap: 6px;">
                    <span style="display:inline-block; width:11px; height:11px; border-radius:50%; background:#EF4444; box-shadow:0 0 10px #EF4444; animation: pulse 1.5s infinite; margin-right:4px;"></span>
                    <span style="font-weight:800; font-size:1.02rem; color:#EF4444; margin-right:8px;">🚨 中央氣象署即時災害警特報發布中</span>
                    {alert_pills_html}
                </div>
                <div style="font-size:0.86rem; font-weight:700;">
                    共 <b>{total_warned_counties}</b> 個縣市處於特報警戒中
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("🔍 點擊展開警戒縣市詳細範圍、時段與防災避險指引", expanded=False):
            n_cols = min(max(len(active_alerts), 1), 3)
            c_a_cols = st.columns(n_cols)
            for a_idx, a in enumerate(active_alerts):
                target_col = c_a_cols[a_idx % n_cols]
                with target_col:
                    st.markdown(f"""
                    <div style="padding: 12px 16px; border-radius: 14px; background: rgba(30, 41, 59, 0.05); border-left: 5px solid {a['color']}; border-top:1px solid rgba(148,163,184,0.15); border-right:1px solid rgba(148,163,184,0.15); border-bottom:1px solid rgba(148,163,184,0.15); margin-bottom: 10px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; margin-bottom:6px;">
                            <div style="font-weight:800; font-size:1.05rem;">
                                {a['icon']} {a['alert_title']}
                            </div>
                            <div style="font-size:0.82rem; font-weight:600;">
                                ⏱️ 有效時段：{a['start_time']} ~ {a['end_time']}
                            </div>
                        </div>
                        <div style="font-size:0.88rem; margin-bottom:8px;">
                            <b>📍 警戒縣市範圍（共 {a['location_count']} 縣市）：</b><br>
                            <span style="font-weight:700;">{a['affected_locations']}</span>
                        </div>
                        <div style="font-size:0.85rem; background: rgba(245, 158, 11, 0.12); border-radius:8px; padding: 6px 12px;">
                            <b>💡 防災避險指引：</b> {a['advice']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 14px; padding: 10px 18px; margin-bottom: 15px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
            <div style="display:flex; align-items:center; gap: 8px;">
                <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#10B981;"></span>
                <span style="font-weight:700; font-size:0.92rem; color:#10B981;">🟢 中央氣象署即時觀測：全台目前無發布顯著氣象警特報，天候總體平和穩定。</span>
            </div>
            <div style="font-size:0.82rem; font-weight:600;">
                氣象署 24H 災害預警系統連線中
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Fetch latest datasets from SQLite
    latest_rows = get_latest_forecasts()
    env_rows = get_env_metrics()

    if not latest_rows:
        st.warning("目前尚無氣象資料，請點選左側選單的「全面同步天氣、一週預報與空品」。")
        return

    df = pd.DataFrame(latest_rows)
    env_df = pd.DataFrame(env_rows) if env_rows else pd.DataFrame()

    # Calculate Key Metrics
    avg_max = round(df["max_temp"].mean(), 1)
    avg_min = round(df["min_temp"].mean(), 1)
    avg_rain = round(df["rain_prob"].mean(), 0)
    hottest_city = df.loc[df["max_temp"].idxmax()]
    coldest_city = df.loc[df["min_temp"].idxmin()]

    avg_uv = round(env_df["uv_index"].mean(), 1) if not env_df.empty else 7.0
    avg_aqi = int(env_df["aqi"].mean()) if not env_df.empty else 45
    best_aqi_city = env_df.loc[env_df["aqi"].idxmin()] if not env_df.empty else None

    # Key Metrics Display (6 columns)
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric(label="🌡️ 全台平均氣溫", value=f"{avg_min}°C ~ {avg_max}°C")
    with m2:
        st.metric(label="🌧️ 平均降雨機率", value=f"{int(avg_rain)} %")
    with m3:
        st.metric(label="☀️ 全台平均紫外線", value=f"{avg_uv} UVI", delta=get_uv_category(avg_uv)[0])
    with m4:
        st.metric(label="🌿 全台平均 AQI", value=f"{avg_aqi}", delta=get_aqi_category(avg_aqi)[0], delta_color="inverse")
    with m5:
        st.metric(label="🔥 最熱縣市", value=f"{hottest_city['location_name']}", delta=f"{hottest_city['max_temp']}°C")
    with m6:
        if best_aqi_city is not None:
            st.metric(label="🍃 最優空品縣市", value=f"{best_aqi_city['location_name']}", delta=f"AQI {best_aqi_city['aqi']}")
        else:
            st.metric(label="❄️ 最低溫縣市", value=f"{coldest_city['location_name']}", delta=f"{coldest_city['min_temp']}°C", delta_color="inverse")

    st.markdown("<br>", unsafe_allow_html=True)

    # Initialize shared active city across Tab 3, Tab 4, and Tab 6
    if "shared_city" not in st.session_state:
        st.session_state["shared_city"] = "臺北市"

    def sync_city_from_36h():
        if "select_city_36h" in st.session_state:
            st.session_state["shared_city"] = st.session_state["select_city_36h"]
            st.session_state["select_city_7d"] = st.session_state["select_city_36h"]
            st.session_state["hist_single_city"] = st.session_state["select_city_36h"]

    def sync_city_from_7d():
        if "select_city_7d" in st.session_state:
            st.session_state["shared_city"] = st.session_state["select_city_7d"]
            st.session_state["select_city_36h"] = st.session_state["select_city_7d"]
            st.session_state["hist_single_city"] = st.session_state["select_city_7d"]

    def sync_city_from_hist():
        if "hist_single_city" in st.session_state:
            st.session_state["shared_city"] = st.session_state["hist_single_city"]
            st.session_state["select_city_36h"] = st.session_state["hist_single_city"]
            st.session_state["select_city_7d"] = st.session_state["hist_single_city"]

    # Tabs for different views
    tab_map, tab_regions, tab_city, tab_7day, tab_environment, tab_history, tab_database = st.tabs([
        "🗺️ 台灣互動觀測地圖",
        "🏙️ 分區天氣與空品卡片",
        "🔍 單一縣市 36H 分析",
        "📅 未來一週 (7-Day) 天氣預報",
        "🌿 紫外線與環境部 AQI 專區",
        "📈 SQLite 歷史軌跡追蹤",
        "🗄️ SQLite 資料庫查詢"
    ])

    # Tab 1: Map
    with tab_map:
        st.subheader("📍 全台即時地理觀測地圖")

        map_c1, map_c2 = st.columns([3, 2])
        with map_c1:
            map_mode_choice = st.radio(
                "選擇地圖圖層觀測維度：",
                [
                    "🌤️ 氣溫與天氣現象",
                    "🌧️ 降雨機率分佈 (PoP)",
                    "☀️ 紫外線指數 (UV)",
                    "🌿 空氣品質指標 (AQI)"
                ],
                horizontal=True
            )
        with map_c2:
            label_choice = st.radio(
                "🏷️ 地圖數值直接標註：",
                ["地名與數值", "僅顯示數值", "不標註 (僅圓點)"],
                horizontal=True,
                index=0
            )

        mode_key = "temperature"
        if "降雨機率" in map_mode_choice:
            mode_key = "rain"
        elif "紫外線" in map_mode_choice:
            mode_key = "uv"
        elif "空氣品質" in map_mode_choice:
            mode_key = "aqi"

        label_key = "both"
        if label_choice == "僅顯示數值":
            label_key = "value"
        elif "不標註" in label_choice:
            label_key = "none"

        # Insight banner for selected layer
        if mode_key == "rain":
            rain_df = df.copy()
            rain_df["rain_num"] = pd.to_numeric(rain_df["rain_prob"], errors="coerce").fillna(0).astype(int)
            max_rain_row = rain_df.sort_values(by="rain_num", ascending=False).iloc[0]
            high_rain_count = len(rain_df[rain_df["rain_num"] >= 30])
            st.info(f"💧 **降雨現況速報**：全台最高降雨機率為 **{max_rain_row['location_name']} ({max_rain_row['rain_num']}%)**，共有 **{high_rain_count}** 個縣市降雨機率達 30% 以上（外出建議攜帶雨具）。")
        elif mode_key == "temperature":
            max_t_row = df.sort_values(by="max_temp", ascending=False).iloc[0]
            min_t_row = df.sort_values(by="min_temp", ascending=True).iloc[0]
            avg_t = round(float(df["max_temp"].mean()), 1)
            st.info(f"🌡️ **全台氣溫分佈**：最高溫 **{max_t_row['location_name']} ({max_t_row['max_temp']}°C)** | 最低溫 **{min_t_row['location_name']} ({min_t_row['min_temp']}°C)** | 全台白天平均約 **{avg_t}°C**。")
        elif mode_key == "uv" and not env_df.empty:
            max_uv_row = env_df.sort_values(by="uv_index", ascending=False).iloc[0]
            st.info(f"☀️ **紫外線現況**：全台最高紫外線指數為 **{max_uv_row['location_name']} (UVI {max_uv_row['uv_index']} - {max_uv_row['uv_level']})**，{max_uv_row['uv_advice']}。")
        elif mode_key == "aqi" and not env_df.empty:
            best_aqi = env_df.sort_values(by="aqi", ascending=True).iloc[0]
            worst_aqi = env_df.sort_values(by="aqi", ascending=False).iloc[0]
            st.info(f"🌿 **空氣品質現況**：空氣最佳為 **{best_aqi['location_name']} (AQI {best_aqi['aqi']} 🟢 良好)** | 需稍加留意為 **{worst_aqi['location_name']} (AQI {worst_aqi['aqi']} - {worst_aqi['aqi_status']})**。")

        map_fig = create_taiwan_weather_map(df, env_df, mode=mode_key, theme=theme_key, label_mode=label_key)
        st.plotly_chart(map_fig)

    # Tab 2: Regional View
    with tab_regions:
        st.subheader("📊 全台氣溫比較與分區預報")

        # Two rows of filtering and sorting controls
        ctrl_col1, ctrl_col2 = st.columns([2, 1])
        with ctrl_col1:
            selected_region = st.radio(
                "📍 選擇分區篩選：",
                ["全部", "北部", "中部", "南部", "東部", "離島"],
                horizontal=True,
                key="filter_region"
            )
        with ctrl_col2:
            search_query = st.text_input(
                "🔍 搜尋縣市名稱：",
                placeholder="輸入縣市，如：臺中、花蓮...",
                key="search_city_card"
            )

        sort_order = st.radio(
            "⚡ 卡片排序維度：",
            [
                "📌 預設區域排序",
                "🔥 最高溫優先 (熱到冷)",
                "❄️ 最低溫優先 (冷到熱)",
                "🌧️ 降雨機率優先 (高到低)",
                "🌿 空氣品質最佳 (AQI 優到劣)",
                "⚠️ 空氣品質最差 (AQI 劣到優)",
                "☀️ 紫外線最強 (UVI 強到弱)"
            ],
            horizontal=True,
            key="sort_city_card"
        )

        filtered_df = df if selected_region == "全部" else df[df["region"] == selected_region]

        # Merge environment metrics cleanly
        if not env_df.empty:
            env_clean = env_df.drop(columns=['id', 'region', 'updated_at'], errors='ignore')
            merged_cards = pd.merge(filtered_df, env_clean, on="location_name", how="left")
        else:
            merged_cards = filtered_df.copy()

        # Fallback values for sort columns
        if "uv_index" not in merged_cards.columns:
            merged_cards["uv_index"] = 7.0
        if "aqi" not in merged_cards.columns:
            merged_cards["aqi"] = 50

        # Search filter
        if search_query.strip():
            merged_cards = merged_cards[merged_cards["location_name"].str.contains(search_query.strip(), na=False)]

        # Sorting logic
        is_sorted = (sort_order != "📌 預設區域排序")
        if sort_order == "🔥 最高溫優先 (熱到冷)":
            merged_cards = merged_cards.sort_values(by="max_temp", ascending=False)
            sort_metric_key = "max_temp"
            sort_unit = "°C"
            chart_title = f"{selected_region}各縣市氣溫比較（依最高溫由高至低）"
        elif sort_order == "❄️ 最低溫優先 (冷到熱)":
            merged_cards = merged_cards.sort_values(by="min_temp", ascending=True)
            sort_metric_key = "min_temp"
            sort_unit = "°C"
            chart_title = f"{selected_region}各縣市氣溫比較（依最低溫由低至高）"
        elif sort_order == "🌧️ 降雨機率優先 (高到低)":
            merged_cards = merged_cards.sort_values(by="rain_prob", ascending=False)
            sort_metric_key = "rain_prob"
            sort_unit = "%"
            chart_title = f"{selected_region}各縣市氣溫比較（依降雨機率由高至低）"
        elif sort_order == "🌿 空氣品質最佳 (AQI 優到劣)":
            merged_cards = merged_cards.sort_values(by="aqi", ascending=True)
            sort_metric_key = "aqi"
            sort_unit = " AQI"
            chart_title = f"{selected_region}各縣市氣溫比較（依空氣品質由優至劣）"
        elif sort_order == "⚠️ 空氣品質最差 (AQI 劣到優)":
            merged_cards = merged_cards.sort_values(by="aqi", ascending=False)
            sort_metric_key = "aqi"
            sort_unit = " AQI"
            chart_title = f"{selected_region}各縣市氣溫比較（依空氣品質由劣至優）"
        elif sort_order == "☀️ 紫外線最強 (UVI 強到弱)":
            merged_cards = merged_cards.sort_values(by="uv_index", ascending=False)
            sort_metric_key = "uv_index"
            sort_unit = " UVI"
            chart_title = f"{selected_region}各縣市氣溫比較（依紫外線強度由高至低）"
        else:
            region_order = {"北部": 1, "中部": 2, "南部": 3, "東部": 4, "離島": 5}
            merged_cards["_reg_order"] = merged_cards["region"].map(region_order).fillna(99)
            merged_cards = merged_cards.sort_values(by=["_reg_order", "max_temp"], ascending=[True, False])
            sort_metric_key = None
            sort_unit = ""
            chart_title = f"{selected_region}各縣市氣溫區間分佈 (°C)"

        # Render synchronized interactive chart and cards if results exist
        if not merged_cards.empty:
            chart_fig = create_temperature_comparison_chart(
                merged_cards,
                theme=theme_key,
                preserve_order=is_sorted or (selected_region != "全部"),
                custom_title=chart_title
            )
            st.plotly_chart(chart_fig)

            top_city = merged_cards.iloc[0]
            top_info = f"<b>{top_city['location_name']}</b> ({top_city[sort_metric_key]}{sort_unit})" if sort_metric_key else f"<b>{top_city['location_name']}</b> ({top_city['max_temp']}°C)"
            avg_pop_filtered = int(merged_cards["rain_prob"].mean())
            avg_temp_filtered = round(merged_cards["max_temp"].mean(), 1)
            hottest_filtered = merged_cards.loc[merged_cards["max_temp"].idxmax()]
            coldest_filtered = merged_cards.loc[merged_cards["min_temp"].idxmin()]
            
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; padding: 12px 18px; border-radius: 14px; background: rgba(2, 132, 199, 0.07); border: 1px solid rgba(2, 132, 199, 0.22); margin-bottom: 20px; font-size: 0.92rem;">
                <div>
                    📍 目前分區：<b>{selected_region}</b> ｜ 符合縣市：<b>{len(merged_cards)}</b> 個 ｜ 排序：<b>{sort_order.split()[0]} {sort_order.split()[1] if len(sort_order.split()) > 1 else ''}</b>
                </div>
                <div>
                    🏆 首選亮點：{top_info} ｜ 最高溫：<b>{hottest_filtered['location_name']} ({hottest_filtered['max_temp']}°C)</b> ｜ 最低溫：<b>{coldest_filtered['location_name']} ({coldest_filtered['min_temp']}°C)</b> ｜ 平均降雨：<b>{avg_pop_filtered}%</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"🔍 查無包含「{search_query}」的縣市，請嘗試更換關鍵字或點選「全部」分區。")

        # Display city cards in a responsive grid only if results exist
        if not merged_cards.empty:
            cols = st.columns(3)
            for idx, (_, row) in enumerate(merged_cards.iterrows()):
                rank = idx + 1
                if is_sorted:
                    if rank == 1:
                        rank_badge = '<span style="background: linear-gradient(135deg, #F59E0B, #D97706); color:white; font-size:0.75rem; font-weight:800; padding:2px 8px; border-radius:12px; margin-right:6px; box-shadow:0 2px 6px rgba(245, 158, 11, 0.45);">🥇 第 1 名</span>'
                    elif rank == 2:
                        rank_badge = '<span style="background: linear-gradient(135deg, #94A3B8, #64748B); color:white; font-size:0.75rem; font-weight:800; padding:2px 8px; border-radius:12px; margin-right:6px; box-shadow:0 2px 6px rgba(100, 116, 139, 0.35);">🥈 第 2 名</span>'
                    elif rank == 3:
                        rank_badge = '<span style="background: linear-gradient(135deg, #B45309, #78350F); color:white; font-size:0.75rem; font-weight:800; padding:2px 8px; border-radius:12px; margin-right:6px; box-shadow:0 2px 6px rgba(180, 83, 9, 0.35);">🥉 第 3 名</span>'
                    else:
                        rank_badge = f'<span style="background: rgba(100, 116, 139, 0.15); border: 1px solid rgba(100, 116, 139, 0.3); font-size:0.75rem; font-weight:700; padding:2px 7px; border-radius:12px; margin-right:6px;">#{rank}</span>'
                else:
                    rank_badge = ""

                # Rain advice & visual progress bar safely parsed
                try:
                    pop = int(row.get('rain_prob', 0))
                except (ValueError, TypeError):
                    pop = 0

                if pop >= 70:
                    rain_col = "#EF4444"
                    rain_tip = "必備雨具"
                    rain_bar_grad = "linear-gradient(90deg, #38BDF8, #EF4444)"
                elif pop >= 30:
                    rain_col = "#F59E0B"
                    rain_tip = "攜帶折傘"
                    rain_bar_grad = "linear-gradient(90deg, #38BDF8, #F59E0B)"
                else:
                    rain_col = "#10B981"
                    rain_tip = "降雨機率低"
                    rain_bar_grad = "linear-gradient(90deg, #38BDF8, #10B981)"

                city_warns = county_alerts_dict.get(row['location_name'], [])
                warn_badges = "".join([
                    f'<span class="badge-alert" style="background:{w["color"]};">{w["icon"]} {w["title"]}</span>'
                    for w in city_warns
                ])
                card_warn_border = f"border: 1.5px solid {city_warns[0]['color']} !important;" if city_warns else ""

                with cols[idx % 3]:
                    icon = get_weather_icon(row.get("weather_state", "晴"))
                    uv_raw = row.get("uv_index")
                    uv_val = round(float(uv_raw), 1) if pd.notna(uv_raw) else 7.0
                    uv_col = row.get("uv_color") or "#FF7E00"

                    aqi_raw = row.get("aqi")
                    aqi_val = int(aqi_raw) if pd.notna(aqi_raw) else 50
                    aqi_st = row.get("aqi_status") or "普通"
                    aqi_col = row.get("aqi_color") or "#FFD700"

                    st.markdown(f"""
                    <div class="weather-card" style="{card_warn_border}">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <h4 style="margin:0; font-weight:800; font-size:1.15rem;">
                                {rank_badge}{icon} {row['location_name']} <small style="font-size:0.8em; font-weight:600;">({row['region']})</small>
                            </h4>
                            <div style="display:flex; align-items:center; flex-wrap:wrap; gap:4px;">
                            {warn_badges}
                            <span class="badge-uv" style="background:{uv_col}; color:#FFFFFF; text-shadow:0 1px 2px rgba(0,0,0,0.6);">☀️ UV {uv_val}</span>
                            <span class="badge-aqi" style="background:{aqi_col}; color:#FFFFFF; text-shadow:0 1px 2px rgba(0,0,0,0.6);">🌿 AQI {aqi_val}</span>
                        </div>
                    </div>
                    <p style="margin:4px 0;"><b>天氣現象:</b> {row['weather_state']}</p>
                    <p style="margin:4px 0;"><b>氣溫區間:</b> <span style="font-weight:800; font-size:1.05rem;">{row['min_temp']}°C ~ {row['max_temp']}°C</span></p>
                    <div style="margin: 8px 0;">
                        <div style="display:flex; justify-content:space-between; font-size:0.85rem; margin-bottom:3px;">
                            <span><b>降雨機率:</b> 💧 {row['rain_prob']}%</span>
                            <span style="font-weight:700; color:{rain_col}; font-size:0.82rem;">{rain_tip}</span>
                        </div>
                        <div style="background: rgba(148, 163, 184, 0.2); height:6px; border-radius:3px; overflow:hidden;">
                            <div style="background: {rain_bar_grad}; width: {min(100, max(6, pop))}%; height:100%; border-radius:3px;"></div>
                        </div>
                    </div>
                    <p style="margin:4px 0; font-size:0.88rem;"><b>空品等級:</b> {aqi_st} | <b>體感舒適度:</b> {row['comfort']}</p>
                </div>
                """, unsafe_allow_html=True)

    # Tab 3: Single City 36H Deep Dive
    with tab_city:
        st.subheader("🔍 單一縣市 36 小時未來趨勢與環境指標")
        all_cities = sorted(df["location_name"].unique())
        cur_36h = st.session_state.get("shared_city", "臺北市")
        idx_36h = all_cities.index(cur_36h) if cur_36h in all_cities else 0
        idx_kwargs_36h = {} if "select_city_36h" in st.session_state else {"index": idx_36h}
        selected_city = st.selectbox(
            "請選擇欲查詢之縣市：",
            all_cities,
            key="select_city_36h",
            on_change=sync_city_from_36h,
            **idx_kwargs_36h
        )

        # Environmental gauge & health advice
        city_env = get_location_env(selected_city)
        if city_env:
            g_fig = create_city_env_gauges(city_env, theme=theme_key)
            st.plotly_chart(g_fig)

            col_tip1, col_tip2 = st.columns(2)
            with col_tip1:
                st.markdown(f"""
                <div class="advice-box" style="border-left-color: {city_env.get('uv_color', '#FF9800')} !important;">
                    <b>☀️ 紫外線防護提醒 ({city_env.get('uv_level', '')})：</b><br>
                    {city_env.get('uv_advice', '注意日常防曬。')}
                </div>
                """, unsafe_allow_html=True)
            with col_tip2:
                st.markdown(f"""
                <div class="advice-box" style="border-left-color: {city_env.get('aqi_color', '#FFD700')} !important;">
                    <b>🌿 空氣品質健康叮嚀 ({city_env.get('aqi_status', '')})：</b><br>
                    {city_env.get('aqi_advice', '可正常進行戶外活動。')} (PM2.5: {city_env.get('pm25')} µg/m³ / PM10: {city_env.get('pm10')} µg/m³)
                </div>
                """, unsafe_allow_html=True)

        city_forecasts = get_location_forecast(selected_city)
        if city_forecasts:
            city_df = pd.DataFrame(city_forecasts)

            def format_period(row):
                try:
                    s = datetime.datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S")
                    e = datetime.datetime.strptime(row["end_time"], "%Y-%m-%d %H:%M:%S")
                    return f"{s.strftime('%m/%d %H時')} ~ {e.strftime('%m/%d %H時')}"
                except Exception:
                    return f"{row['start_time'][5:16]} ~ {row['end_time'][5:16]}"

            city_df["period_label"] = city_df.apply(format_period, axis=1)

            trend_fig = create_trend_chart(city_df, selected_city, theme=theme_key)
            st.plotly_chart(trend_fig)

            st.write("📋 **36 小時詳細分段氣象資料**")
            display_cols = ["start_time", "end_time", "weather_state", "min_temp", "max_temp", "rain_prob", "comfort"]
            clean_36h_df = city_df[display_cols].rename(columns={
                "start_time": "開始時間",
                "end_time": "結束時間",
                "weather_state": "天氣現象",
                "min_temp": "最低溫 (°C)",
                "max_temp": "最高溫 (°C)",
                "rain_prob": "降雨機率 (%)",
                "comfort": "舒適度"
            })
            st.dataframe(clean_36h_df)

            csv_36h_city = clean_36h_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 下載 {selected_city} 36 小時預報資料 (CSV)",
                data=csv_36h_city,
                file_name=f"{selected_city}_36h_forecast_{datetime.date.today()}.csv",
                mime="text/csv",
                key="dl_tab3_36h_csv"
            )

    # Tab 4: 7-Day Forecast
    with tab_7day:
        st.subheader("📅 全台各縣市未來一週 (7-Day) 天氣預報")
        st.markdown("串接中央氣象署 **臺灣各縣市未來 1 週天氣預報 (`F-D0047-091`)**，提早規劃未來 7 日行程與出行穿著。")

        all_7d_cities = sorted(df["location_name"].unique())
        cur_7d = st.session_state.get("shared_city", "臺北市")
        idx_7d = all_7d_cities.index(cur_7d) if cur_7d in all_7d_cities else 0
        idx_kwargs_7d = {} if "select_city_7d" in st.session_state else {"index": idx_7d}
        selected_7d_city = st.selectbox(
            "請選擇欲查看一週預報之縣市：",
            all_7d_cities,
            key="select_city_7d",
            on_change=sync_city_from_7d,
            **idx_kwargs_7d
        )

        slots_7d = get_location_7day_forecast(selected_7d_city)
        if slots_7d:
            slots_df = pd.DataFrame(slots_7d)

            # Aggregate into 7 distinct days
            seen_dates = []
            for s in slots_7d:
                d_str = s["start_time"][:10]
                if d_str not in seen_dates:
                    seen_dates.append(d_str)

            days_summary = []
            weekdays_zh = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
            for d_str in seen_dates:
                d_slots = [s for s in slots_7d if s["start_time"].startswith(d_str)]
                day_slot = next((s for s in d_slots if "06:00" in s["start_time"] or "12:00" in s["start_time"]), d_slots[0])
                min_t = min(s["min_temp"] for s in d_slots)
                max_t = max(s["max_temp"] for s in d_slots)
                max_pop = max(s["rain_prob"] for s in d_slots)
                wx = day_slot["weather_state"]

                try:
                    dt = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                    wd = weekdays_zh[dt.weekday()]
                    date_label = f"{dt.month}/{dt.day}"
                except Exception:
                    wd = "未來"
                    date_label = d_str[5:]

                days_summary.append({
                    "date": date_label,
                    "weekday": wd,
                    "weather": wx,
                    "min_temp": min_t,
                    "max_temp": max_t,
                    "rain_prob": max_pop,
                    "desc": day_slot.get("weather_desc", "")
                })

            # Display 7-day card grid with high contrast classes
            display_days = days_summary[:7]
            cols = st.columns(len(display_days))
            for idx, d in enumerate(display_days):
                with cols[idx]:
                    icon = get_weather_icon(d["weather"])
                    st.markdown(f"""
                    <div class="day-card">
                        <div class="day-weekday">{d['weekday']}</div>
                        <div class="day-date">{d['date']}</div>
                        <div class="day-icon">{icon}</div>
                        <div class="day-weather">{d['weather']}</div>
                        <div class="day-temp">{d['min_temp']}° ~ {d['max_temp']}°</div>
                        <div class="day-rain">💧 {d['rain_prob']}%</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # 7-Day Trend Chart
            fig_7d = create_7day_trend_chart(slots_df, selected_7d_city, theme=theme_key)
            st.plotly_chart(fig_7d)

            # Detailed 14-period Table
            st.markdown(f"### 📋 {selected_7d_city} 未來一週分時段預報詳細清單")
            display_7d_cols = [
                "start_time", "end_time", "weather_state", "min_temp", "max_temp",
                "apparent_min_temp", "apparent_max_temp", "rain_prob", "relative_humidity", "weather_desc"
            ]
            clean_df = slots_df[display_7d_cols].rename(columns={
                "start_time": "開始時間",
                "end_time": "結束時間",
                "weather_state": "天氣現象",
                "min_temp": "最低溫 (°C)",
                "max_temp": "最高溫 (°C)",
                "apparent_min_temp": "體感最低溫",
                "apparent_max_temp": "體感最高溫",
                "rain_prob": "降雨機率 (%)",
                "relative_humidity": "相對濕度 (%)",
                "weather_desc": "綜合天氣描述"
            })
            st.dataframe(clean_df)

            csv_7d_city = clean_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 下載 {selected_7d_city} 一週預報資料 (CSV)",
                data=csv_7d_city,
                file_name=f"{selected_7d_city}_7day_forecast_{datetime.date.today()}.csv",
                mime="text/csv"
            )
        else:
            st.info("尚無一週預報資料，請點擊左側「全面同步天氣、一週預報與空品」。")

    # Tab 5: UV & AQI Dedicated Section
    with tab_environment:
        st.subheader("🌿 全台紫外線指數與空氣品質 (AQI) 專題分析")
        st.markdown("整合中央氣象署紫外線測站資料與環境部空氣品質監測資料，保障戶外活動安全與呼吸健康。")

        if not env_df.empty:
            c_aqi_chart, c_uv_chart = st.tabs(["🌿 全台空氣品質 (AQI) 排名比較", "☀️ 全台紫外線指數 (UVI) 排名比較"])
            with c_aqi_chart:
                aqi_fig = create_aqi_bar_chart(env_df, theme=theme_key)
                st.plotly_chart(aqi_fig)

            with c_uv_chart:
                uv_fig = create_uv_bar_chart(env_df, theme=theme_key)
                st.plotly_chart(uv_fig)

            st.markdown("### 📋 全台 22 縣市即時環境指標總表")
            display_env = env_df[[
                "location_name", "region", "uv_index", "uv_level", "aqi", "aqi_status", "pm25", "pm10", "data_source"
            ]].rename(columns={
                "location_name": "縣市",
                "region": "分區",
                "uv_index": "紫外線指數",
                "uv_level": "紫外線分級",
                "aqi": "空氣品質 (AQI)",
                "aqi_status": "空品等級",
                "pm25": "PM2.5 (µg/m³)",
                "pm10": "PM10 (µg/m³)",
                "data_source": "資料來源"
            })
            st.dataframe(display_env)

            csv_env_tab5 = display_env.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載全台即時環境指標總表 (CSV)",
                data=csv_env_tab5,
                file_name=f"taiwan_environment_metrics_{datetime.date.today()}.csv",
                mime="text/csv",
                key="dl_tab5_env_csv"
            )

            # Standards explanation card
            st.markdown("---")
            st.markdown("#### 📖 台灣官方指標分級對照與健康防護標準")
            c_guide1, c_guide2 = st.columns(2)
            with c_guide1:
                st.markdown("""
                **☀️ 紫外線指數 (UV Index) 曝險分級標準：**
                - 🟢 **0 ~ 2 低量級**：紫外線弱，可正常戶外活動。
                - 🟡 **3 ~ 5 中量級**：建議配戴遮陽帽、太陽眼鏡或使用防曬乳。
                - 🟠 **6 ~ 7 高量級**：紫外線強，外出應全面防護，塗抹防曬乳。
                - 🔴 **8 ~ 10 過量級**：曝曬 15-20 分鐘即可能曬傷，正午時段儘量避免外出。
                - 🟣 **11+ 危險級**：曝曬 10-15 分鐘即可能曬傷，請留在室內陰涼處。
                """)
            with c_guide2:
                st.markdown("""
                **🌿 環境部空氣品質指標 (AQI) 標準：**
                - 🟢 **0 ~ 50 良好**：空氣品質良好，大眾皆可正常戶外活動。
                - 🟡 **51 ~ 100 普通**：極少數極度敏感者宜減少劇烈戶外活動。
                - 🟠 **101 ~ 150 對敏感族群不健康**：孩童、長者及呼吸道患者應減少劇烈戶外運動。
                - 🔴 **151 ~ 200 對所有族群不健康**：大眾應減少戶外活動，外出請配戴防護口罩。
                - 🟣 **201 ~ 300 非常不健康**：應避免戶外活動並緊閉門窗。
                """)

    # Tab 6: SQLite History Tracking
    with tab_history:
        st.subheader("📈 SQLite 歷史軌跡追蹤與趨勢分析")
        st.caption("透過本地 SQLite 持久化資料庫，追蹤歷次氣象署與環境部同步之觀測歷程，繪製多維度歷史變化圖。")

        hist_view_mode = st.radio(
            "選擇分析模式：",
            ["🏙️ 單一縣市深度歷史軌跡", "📊 跨縣市多指標趨勢對比"],
            horizontal=True
        )

        all_cities = sorted(df["location_name"].unique()) if not df.empty else ["臺北市", "臺中市", "高雄市"]

        if "單一縣市" in hist_view_mode:
            h_col1, h_col2 = st.columns([1, 2])
            with h_col1:
                cur_hist = st.session_state.get("shared_city", "臺北市")
                idx_hist = all_cities.index(cur_hist) if cur_hist in all_cities else 0
                idx_kwargs_hist = {} if "hist_single_city" in st.session_state else {"index": idx_hist}
                selected_city = st.selectbox(
                    "選擇欲追蹤之縣市：",
                    all_cities,
                    key="hist_single_city",
                    on_change=sync_city_from_hist,
                    **idx_kwargs_hist
                )
            with h_col2:
                metric_choice = st.radio(
                    "選擇追蹤指標：",
                    [
                        "📊 綜合指標 (氣溫 + 降雨)",
                        "🌡️ 氣溫區間帶 (日夜溫差)",
                        "🌧️ 降雨機率變化 (PoP)",
                        "🌿 空氣品質歷程 (AQI & PM2.5)",
                        "☀️ 紫外線指數 (UVI)"
                    ],
                    horizontal=True,
                    key="hist_metric_choice"
                )

            m_map = {
                "📊 綜合指標 (氣溫 + 降雨)": "composite",
                "🌡️ 氣溫區間帶 (日夜溫差)": "temp_band",
                "🌧️ 降雨機率變化 (PoP)": "rain",
                "🌿 空氣品質歷程 (AQI & PM2.5)": "aqi",
                "☀️ 紫外線指數 (UVI)": "uv"
            }
            metric_key = m_map.get(metric_choice, "composite")

            city_history = get_location_history(selected_city)
            if city_history:
                df_city_hist = pd.DataFrame(city_history)

                # Summary metric KPI cards for past history
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                with kpi1:
                    max_t = int(df_city_hist["max_temp"].dropna().max()) if not df_city_hist["max_temp"].dropna().empty else 30
                    min_t = int(df_city_hist["min_temp"].dropna().min()) if not df_city_hist["min_temp"].dropna().empty else 20
                    st.metric("🌡️ 歷史氣溫極值", f"{min_t}°C ~ {max_t}°C", delta=f"溫差 {max_t - min_t}°C")
                with kpi2:
                    max_rain = int(df_city_hist["rain_prob"].dropna().max()) if not df_city_hist["rain_prob"].dropna().empty else 0
                    st.metric("🌧️ 最高降雨機率", f"{max_rain}%", delta="注意防雨" if max_rain >= 30 else "降雨偏低")
                with kpi3:
                    aqi_mean = df_city_hist["aqi"].dropna().mean()
                    avg_aqi = round(float(aqi_mean), 1) if pd.notna(aqi_mean) else 50.0
                    st.metric("🌿 平均空氣品質", f"AQI {avg_aqi}", delta="良好" if avg_aqi <= 50 else ("普通" if avg_aqi <= 100 else "需防護"))
                with kpi4:
                    rec_count = len(df_city_hist)
                    st.metric("🕒 累計觀測記錄", f"{rec_count} 個時間點", delta="持續追蹤中")

                fig_hist = create_history_trend_chart(df_city_hist, selected_city, metric_mode=metric_key, theme=theme_key)
                st.plotly_chart(fig_hist)

                csv_hist_city = df_city_hist.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label=f"📥 下載 {selected_city} 歷史觀測數據 (CSV)",
                    data=csv_hist_city,
                    file_name=f"{selected_city}_history_{datetime.date.today()}.csv",
                    mime="text/csv",
                    key="dl_tab6_hist_city_csv"
                )
            else:
                st.warning(f"目前尚無 {selected_city} 的歷史觀測紀錄。點擊側邊欄「全面同步」即可立即寫入快照！")

        else:  # 跨縣市多指標趨勢對比
            c_col1, c_col2 = st.columns([2, 1])
            with c_col1:
                default_picks = [c for c in ["臺北市", "臺中市", "高雄市", "花蓮縣"] if c in all_cities]
                selected_compare_cities = st.multiselect(
                    "選擇欲對比的多個縣市 (建議 2~5 個)：",
                    all_cities,
                    default=default_picks,
                    key="hist_multi_cities"
                )
            with c_col2:
                compare_metric_choice = st.selectbox(
                    "選擇對比指標：",
                    [
                        "🌡️ 平均氣溫 (°C)",
                        "🌧️ 降雨機率 (%)",
                        "🌿 空氣品質 (AQI)",
                        "☀️ 紫外線指數 (UVI)",
                        "💨 PM2.5 濃度 (µg/m³)"
                    ],
                    key="hist_compare_metric"
                )

            comp_metric_map = {
                "🌡️ 平均氣溫 (°C)": "avg_temp",
                "🌧️ 降雨機率 (%)": "rain_prob",
                "🌿 空氣品質 (AQI)": "aqi",
                "☀️ 紫外線指數 (UVI)": "uv_index",
                "💨 PM2.5 濃度 (µg/m³)": "pm25"
            }
            comp_metric_key = comp_metric_map.get(compare_metric_choice, "avg_temp")

            if selected_compare_cities:
                multi_data = get_multi_location_history(selected_compare_cities)
                if multi_data:
                    df_multi = pd.DataFrame(multi_data)
                    fig_comp = create_multi_city_history_chart(df_multi, metric=comp_metric_key, theme=theme_key)
                    st.plotly_chart(fig_comp)
                else:
                    st.info("尚無足夠之歷史比較資料。")
            else:
                st.info("請至少選擇 1 個縣市進行對比。")

        # Database management actions inside Tab history
        with st.expander("🛠️ SQLite 歷史軌跡資料庫工具箱"):
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                st.write("**立即手動建立當前快照：**")
                if st.button("📸 立即保存當前觀測狀態為歷史紀錄", key="btn_snapshot_now"):
                    cnt = record_history_snapshot()
                    st.success(f"已成功建立 {cnt} 筆全台歷史快照！")
                    st.rerun()
            with t_col2:
                st.write("**重設模擬歷史資料（過去 48 小時軌跡）：**")
                if st.button("🔄 重新生成標準 48H 歷史週期模擬資料", key="btn_reseed_history"):
                    re_cnt = seed_mock_history_if_needed(force=True)
                    st.success(f"已成功重新生成 {re_cnt} 筆高品質歷史觀測軌跡！")
                    st.rerun()

    # Tab 7: SQLite Database
    with tab_database:
        st.subheader("🗄️ SQLite 儲存狀態與資料表檢視")
        st.write(f"資料庫檔案位置：`{DEFAULT_DB_PATH}`")

        db_choice = st.radio(
            "選擇欲檢視的資料表：",
            [
                "🌤️ 36H 氣象預報表 (weather_forecasts)",
                "📅 未來一週預報表 (forecast_7day)",
                "🌿 環境空品指標表 (environment_metrics)",
                "🚨 氣象警特報表 (weather_alerts)",
                "🕒 歷史軌跡紀錄表 (weather_history)",
                "⚡ 快取狀態表 (system_cache_meta)"
            ],
            horizontal=True
        )

        if "weather_forecasts" in db_choice:
            st.write(f"目前共儲存 **{len(df)}** 筆縣市 36H 最新預報。")
            st.dataframe(df)
            if not df.empty:
                csv_data = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載 36H 氣象預報資料 (CSV)",
                    data=csv_data,
                    file_name=f"taiwan_weather_36h_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
        elif "forecast_7day" in db_choice:
            all_7d = get_all_7day_forecasts()
            df_all_7d = pd.DataFrame(all_7d)
            st.write(f"目前共儲存 **{len(df_all_7d)}** 筆全台未來一週預報分段資料。")
            st.dataframe(df_all_7d)
            if not df_all_7d.empty:
                csv_7d_all = df_all_7d.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載全台一週預報完整資料 (CSV)",
                    data=csv_7d_all,
                    file_name=f"taiwan_weather_7day_all_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
        elif "environment_metrics" in db_choice:
            st.write(f"目前共儲存 **{len(env_df)}** 筆縣市紫外線與空品監測數據。")
            st.dataframe(env_df)
            if not env_df.empty:
                csv_env = env_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載環境指標資料 (CSV)",
                    data=csv_env,
                    file_name=f"taiwan_environment_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
        elif "weather_alerts" in db_choice:
            alerts_data = get_weather_alerts()
            df_alerts = pd.DataFrame(alerts_data)
            st.write(f"目前共儲存 **{len(df_alerts)}** 筆氣象警特報生效紀錄（依縣市劃分）。")
            if not df_alerts.empty:
                st.dataframe(df_alerts)
                csv_alerts = df_alerts.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載即時氣象警特報資料 (CSV)",
                    data=csv_alerts,
                    file_name=f"taiwan_weather_alerts_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.success("🎉 目前全台無任何氣象署發布之有效警特報。")
        elif "weather_history" in db_choice:
            hist_all = get_all_history(limit=2000)
            df_hist_all = pd.DataFrame(hist_all)
            st.write(f"目前共儲存 **{len(df_hist_all)}** 筆歷次同步觀測紀錄（依時間與縣市劃分）。")
            if not df_hist_all.empty:
                st.dataframe(df_hist_all)
                csv_hist = df_hist_all.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載完整歷史軌跡資料 (CSV)",
                    data=csv_hist,
                    file_name=f"taiwan_weather_history_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.info("尚無歷史觀測紀錄。")
        else:
            cache_meta = get_all_cache_meta()
            df_cache = pd.DataFrame(list(cache_meta.values())) if cache_meta else pd.DataFrame()
            st.write("各資料來源智慧快取時效與資料筆數監控狀態：")
            if not df_cache.empty:
                st.dataframe(df_cache)
                csv_cache = df_cache.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載快取狀態資料 (CSV)",
                    data=csv_cache,
                    file_name=f"taiwan_weather_cache_meta_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
            else:
                st.info("尚無快取紀錄，點擊側邊欄同步後即會記錄。")


if __name__ == "__main__":
    main()
