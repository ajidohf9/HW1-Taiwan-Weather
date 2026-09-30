"""Taiwan Weather Forecast Web App.

Built with Python, Streamlit, SQLite, and CWA API.
HW1 - Antigravity x Gemini x GitHub Project.
"""

import os
import importlib
import streamlit as st
import pandas as pd
import datetime

import src.cwa_api
import src.db
import src.visualizer

importlib.reload(src.cwa_api)
importlib.reload(src.db)
importlib.reload(src.visualizer)

from src.cwa_api import fetch_cwa_forecast, REGION_MAP
from src.db import init_db, save_forecasts, get_latest_forecasts, get_location_forecast, get_all_locations, DEFAULT_DB_PATH
from src.visualizer import (
    create_temperature_comparison_chart,
    create_trend_chart,
    create_taiwan_weather_map
)

# Page configuration
st.set_page_config(
    page_title="台灣即時天氣預報系統 | Taiwan Weather Forecast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(120deg, #1E88E5, #00ACC1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 4px solid #1E88E5;
    }
    .weather-card {
        padding: 14px;
        border-radius: 8px;
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-top: 3px solid #00ACC1;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)


def get_weather_icon(state: str) -> str:
    """Return an appropriate emoji for a weather description."""
    if "雨" in state or "陣雨" in state:
        return "🌧️"
    elif "雷" in state:
        return "⛈️"
    elif "陰" in state:
        return "☁️"
    elif "多雲" in state:
        return "⛅"
    elif "晴" in state:
        return "☀️"
    elif "霧" in state:
        return "🌫️"
    return "🌤️"


def ensure_data_loaded():
    """Ensure data exists in SQLite database upon startup."""
    init_db()
    existing = get_latest_forecasts()
    if not existing:
        records, is_live, msg = fetch_cwa_forecast()
        save_forecasts(records)


def main():
    ensure_data_loaded()

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ 設定與資料同步")
        st.markdown("連線至 **中央氣象署 (CWA)** 開放資料 API")
        
        default_key = os.environ.get("CWA_API_KEY", "").strip()
        active_key = default_key

        if default_key and default_key != "your_api_key_here":
            st.success("🟢 **氣象署 API 授權已配置**")
            st.caption("✨ 系統已自動套用您的授權碼，直接點擊下方按鈕即可同步。")
            with st.expander("⚙️ 變更授權碼設定"):
                custom_key = st.text_input(
                    "更換 CWA API Key",
                    value=default_key,
                    type="password",
                    help="預設已讀取 .env 檔，如欲切換其他 Key 可在此修改。"
                )
                if custom_key.strip():
                    active_key = custom_key.strip()
        else:
            api_key_input = st.text_input(
                "CWA API Key (授權碼)",
                type="password",
                help="未輸入時將以全台示範數據即時展示。可至 opendata.cwa.gov.tw 免費申請。"
            )
            active_key = api_key_input.strip()
            if active_key:
                st.caption("🟢 **狀態**: 已自訂授權碼")
            else:
                st.caption("⚪ **狀態**: 示範展示模式 (可輸入 API Key 切換即時資料)")

        sync_btn = st.button("🔄 同步更新氣象資料", use_container_width=True)
        if sync_btn:
            with st.spinner("正在獲取最新天氣資料並寫入 SQLite 資料庫..."):
                records, is_live, msg = fetch_cwa_forecast(active_key)
                saved_count = save_forecasts(records)
                if is_live:
                    st.success(f"✅ {msg} (更新 {saved_count} 筆)")
                    st.rerun()
                else:
                    st.info(f"ℹ️ {msg} (已寫入 {saved_count} 筆)")
        
        st.divider()
        st.markdown("### 📊 專案技術標籤")
        st.markdown("""
        - 🚀 **Framework**: Streamlit
        - 💾 **Database**: SQLite3
        - 🌐 **API**: CWA Open Data (F-C0032-001)
        - 📈 **Visualization**: Plotly Interactive
        - 🤖 **Pair Programmer**: Antigravity x Gemini
        """)
        
        st.divider()
        st.caption("AI Coding Agent 專案實作 · Made with ❤️")

    # Main Header
    st.markdown('<div class="main-header">🌤️ 台灣天氣預報系統 (Taiwan Weather Forecast)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">整合中央氣象署開放資料 API、SQLite 本地儲存與互動式視覺化分析</div>', unsafe_allow_html=True)

    # Fetch latest data from SQLite
    latest_rows = get_latest_forecasts()
    if not latest_rows:
        st.warning("目前尚無氣象資料，請點選左側選單的「同步更新氣象資料」。")
        return

    df = pd.DataFrame(latest_rows)

    # Key Metrics Section
    avg_max = round(df["max_temp"].mean(), 1)
    avg_min = round(df["min_temp"].mean(), 1)
    avg_rain = round(df["rain_prob"].mean(), 0)
    hottest_city = df.loc[df["max_temp"].idxmax()]
    coldest_city = df.loc[df["min_temp"].idxmin()]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="🌡️ 全台平均氣溫", value=f"{avg_min}°C ~ {avg_max}°C")
    with c2:
        st.metric(label="🌧️ 平均降雨機率", value=f"{int(avg_rain)} %")
    with c3:
        st.metric(label="🔥 最熱縣市", value=f"{hottest_city['location_name']}", delta=f"{hottest_city['max_temp']}°C")
    with c4:
        st.metric(label="❄️ 最低溫縣市", value=f"{coldest_city['location_name']}", delta=f"{coldest_city['min_temp']}°C", delta_color="inverse")

    st.markdown("---")

    # Tabs for different views
    tab_map, tab_regions, tab_city, tab_database = st.tabs([
        "🗺️ 台灣氣象地圖", "🏙️ 分區概況與比較", "🔍 單一縣市 36H 趨勢", "🗄️ SQLite 資料庫查詢"
    ])

    with tab_map:
        st.subheader("📍 全台即時氣候分布圖")
        st.markdown("地圖顯示各縣市預報最高溫色彩與氣象概況，支援平移、縮放與懸停細節檢視。")
        map_fig = create_taiwan_weather_map(df)
        st.plotly_chart(map_fig, use_container_width=True)

    with tab_regions:
        st.subheader("📊 全台氣溫比較與分區預報")
        chart_fig = create_temperature_comparison_chart(df)
        st.plotly_chart(chart_fig, use_container_width=True)

        selected_region = st.radio(
            "選擇分區篩選：",
            ["全部", "北部", "中部", "南部", "東部", "離島"],
            horizontal=True
        )

        filtered_df = df if selected_region == "全部" else df[df["region"] == selected_region]

        # Display city cards in a responsive grid
        cols = st.columns(3)
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 3]:
                icon = get_weather_icon(row["weather_state"])
                st.markdown(f"""
                <div class="weather-card">
                    <h4>{icon} {row['location_name']} <small style="color:gray;">({row['region']})</small></h4>
                    <p><b>天氣現象:</b> {row['weather_state']}</p>
                    <p><b>溫度範圍:</b> {row['min_temp']}°C ~ {row['max_temp']}°C</p>
                    <p><b>降雨機率:</b> 💧 {row['rain_prob']}%</p>
                    <p><b>舒適度:</b> {row['comfort']}</p>
                </div>
                """, unsafe_allow_html=True)

    with tab_city:
        st.subheader("🔍 單一縣市 36 小時未來趨勢")
        all_cities = sorted(df["location_name"].unique())
        selected_city = st.selectbox("請選擇欲查詢之縣市：", all_cities, index=all_cities.index("臺北市") if "臺北市" in all_cities else 0)

        city_forecasts = get_location_forecast(selected_city)
        if city_forecasts:
            city_df = pd.DataFrame(city_forecasts)
            
            # Format periods for chart display
            def format_period(row):
                try:
                    s = datetime.datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S")
                    e = datetime.datetime.strptime(row["end_time"], "%Y-%m-%d %H:%M:%S")
                    return f"{s.strftime('%m/%d %H時')} ~ {e.strftime('%m/%d %H時')}"
                except Exception:
                    return f"{row['start_time'][5:16]} ~ {row['end_time'][5:16]}"

            city_df["period_label"] = city_df.apply(format_period, axis=1)

            trend_fig = create_trend_chart(city_df, selected_city)
            st.plotly_chart(trend_fig, use_container_width=True)

            st.write("📋 **36 小時詳細分段資料**")
            display_cols = ["start_time", "end_time", "weather_state", "min_temp", "max_temp", "rain_prob", "comfort"]
            st.dataframe(
                city_df[display_cols].rename(columns={
                    "start_time": "開始時間",
                    "end_time": "結束時間",
                    "weather_state": "天氣現象",
                    "min_temp": "最低溫 (°C)",
                    "max_temp": "最高溫 (°C)",
                    "rain_prob": "降雨機率 (%)",
                    "comfort": "舒適度"
                }),
                use_container_width=True
            )
        else:
            st.info("查無此縣市資料。")

    with tab_database:
        st.subheader("🗄️ SQLite 儲存狀態與資料表檢視")
        st.write(f"資料庫檔案位置：`{DEFAULT_DB_PATH}`")
        
        all_rows = get_latest_forecasts()
        st.write(f"目前共儲存 **{len(df)}** 個縣市最新預報資料。")
        st.dataframe(df, use_container_width=True)

        # Download CSV
        csv_data = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載預報資料 (CSV)",
            data=csv_data,
            file_name=f"taiwan_weather_{datetime.date.today()}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
