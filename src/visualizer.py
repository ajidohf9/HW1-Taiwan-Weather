"""Data Visualization Module for Taiwan Weather App using Plotly.

Supports adaptive Dark (Aurora Glass) & Light (Crystal Glass) themes.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime
from typing import List, Dict, Any
from src.cwa_api import LOCATION_COORDS


def _get_theme_config(theme: str = "light") -> Dict[str, Any]:
    """Helper to return consistent layout styling for dark or light theme."""
    is_dark = (theme == "dark")
    return {
        "template": "plotly_dark" if is_dark else "plotly_white",
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font_color": "#F8FAFC" if is_dark else "#0F172A",
        "grid_color": "rgba(255, 255, 255, 0.12)" if is_dark else "#CBD5E1",
        "map_style": "carto-darkmatter" if is_dark else "carto-positron"
    }


def _create_empty_fig(title_text: str, msg: str, theme: str = "light", height: int = 400) -> go.Figure:
    """Helper to generate an empty styled Plotly figure with a friendly message."""
    t = _get_theme_config(theme)
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title_text, font=dict(color=t["font_color"], size=16)),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[dict(text=msg, showarrow=False, font=dict(size=14, color=t["font_color"]))],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        height=height
    )
    return fig


def create_temperature_comparison_chart(df: pd.DataFrame, theme: str = "light", preserve_order: bool = False, custom_title: str = None) -> go.Figure:
    """Create a temperature range bar chart comparing cities."""
    t = _get_theme_config(theme)
    title_text = custom_title if custom_title else "各縣市氣溫區間分佈 (°C)"

    if isinstance(df, list):
        df = pd.DataFrame(df) if df else pd.DataFrame()
    if df is None or df.empty or "location_name" not in df.columns:
        return _create_empty_fig(title_text, "無可用氣溫數據，請點擊立即同步資料", theme=theme)

    fig = go.Figure()

    if preserve_order:
        sorted_df = df.copy()
    else:
        sorted_df = df.sort_values(by=["region", "max_temp"], ascending=[True, False])

    fig.add_trace(go.Bar(
        x=sorted_df["location_name"],
        y=sorted_df["max_temp"] - sorted_df["min_temp"],
        base=sorted_df["min_temp"],
        marker=dict(
            color=sorted_df["max_temp"],
            colorscale="Viridis",
            colorbar=dict(
                title=dict(text="最高溫 (°C)", font=dict(color=t["font_color"])),
                tickfont=dict(color=t["font_color"])
            ),
            showscale=True
        ),
        text=[f"{min_t}°~{max_t}°" for min_t, max_t in zip(sorted_df["min_temp"], sorted_df["max_temp"])],
        textposition="outside",
        textfont=dict(color=t["font_color"], size=11),
        hovertemplate="<b>%{x}</b><br>最低溫: %{base}°C<br>最高溫: %{customdata}°C<br>氣象: %{text}<extra></extra>",
        customdata=sorted_df["max_temp"]
    ))

    fig.update_layout(
        title=dict(text=title_text, font=dict(color=t["font_color"], size=16)),
        xaxis_title=dict(text="縣市", font=dict(color=t["font_color"])),
        yaxis_title=dict(text="氣溫 (°C)", font=dict(color=t["font_color"])),
        yaxis=dict(
            range=[min(df["min_temp"].min() - 3, 10), max(df["max_temp"].max() + 5, 35)],
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        xaxis=dict(gridcolor=t["grid_color"], tickfont=dict(color=t["font_color"]), tickangle=-35),
        hovermode="x unified",
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        height=450,
        margin=dict(l=40, r=40, t=60, b=80)
    )

    return fig


def create_trend_chart(periods_df: pd.DataFrame, city_name: str, theme: str = "light") -> go.Figure:
    """Create a multi-period temperature & rain probability trend for a selected city."""
    t = _get_theme_config(theme)
    title_text = f"🌡️ {city_name} 36 小時氣溫與降雨趨勢"

    if isinstance(periods_df, list):
        periods_df = pd.DataFrame(periods_df) if periods_df else pd.DataFrame()
    if periods_df is None or periods_df.empty or "max_temp" not in periods_df.columns:
        return _create_empty_fig(title_text, "無可用預報數據，請點擊立即同步資料", theme=theme)

    df_copy = periods_df.copy()
    if "period_label" not in df_copy.columns:
        if "start_time" in df_copy.columns:
            df_copy["period_label"] = df_copy["start_time"].astype(str)
        else:
            df_copy["period_label"] = [f"時段 {i+1}" for i in range(len(df_copy))]
    periods_df = df_copy

    fig = go.Figure()

    # Line for Max Temp
    fig.add_trace(go.Scatter(
        x=periods_df["period_label"],
        y=periods_df["max_temp"],
        mode="lines+markers+text",
        name="最高溫 (°C)",
        line=dict(color="#FF7043", width=3),
        marker=dict(size=10),
        text=[f"{t}°C" for t in periods_df["max_temp"]],
        textposition="top center",
        textfont=dict(color=t["font_color"], size=11)
    ))

    # Line for Min Temp
    fig.add_trace(go.Scatter(
        x=periods_df["period_label"],
        y=periods_df["min_temp"],
        mode="lines+markers+text",
        name="最低溫 (°C)",
        line=dict(color="#29B6F6", width=3),
        marker=dict(size=10),
        text=[f"{t}°C" for t in periods_df["min_temp"]],
        textposition="bottom center",
        textfont=dict(color=t["font_color"], size=11)
    ))

    # Bar for Rain Probability on secondary axis
    fig.add_trace(go.Bar(
        x=periods_df["period_label"],
        y=periods_df["rain_prob"],
        name="降雨機率 (%)",
        marker=dict(color="rgba(3, 169, 244, 0.25)" if theme != "dark" else "rgba(41, 182, 246, 0.35)",
                    line=dict(color="#0284C7" if theme != "dark" else "#29B6F6", width=1)),
        yaxis="y2",
        text=[f"{p}%" for p in periods_df["rain_prob"]],
        textposition="outside",
        textfont=dict(color=t["font_color"], size=11)
    ))

    fig.update_layout(
        title=dict(text=f"{city_name} 36 小時天氣與降雨機率趨勢", font=dict(color=t["font_color"], size=16)),
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        yaxis=dict(
            title=dict(text="溫度 (°C)", font=dict(color=t["font_color"])),
            range=[min(periods_df["min_temp"].min() - 4, 10), max(periods_df["max_temp"].max() + 5, 38)],
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        yaxis2=dict(
            title=dict(text="降雨機率 (%)", font=dict(color=t["font_color"])),
            overlaying="y",
            side="right",
            range=[0, 100],
            showgrid=False,
            tickfont=dict(color=t["font_color"])
        ),
        xaxis=dict(gridcolor=t["grid_color"], tickfont=dict(color=t["font_color"])),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=t["font_color"])),
        height=400,
        margin=dict(l=40, r=40, t=70, b=40)
    )

    return fig


def create_taiwan_weather_map(
    df: pd.DataFrame,
    env_df: pd.DataFrame = None,
    mode: str = "temperature",
    theme: str = "light",
    label_mode: str = "both"
) -> go.Figure:
    """
    Create an interactive map of Taiwan displaying weather, precipitation, UV, or AQI.
    mode options: 'temperature', 'rain', 'uv', 'aqi'
    label_mode options: 'both' (county + value), 'value' (value only), 'none' (markers only)
    """
    t = _get_theme_config(theme)

    if isinstance(df, list):
        df = pd.DataFrame(df) if df else pd.DataFrame()
    if isinstance(env_df, list):
        env_df = pd.DataFrame(env_df) if env_df else pd.DataFrame()

    if df is None or df.empty or "location_name" not in df.columns:
        return _create_empty_fig("🌤️ 台灣天氣分佈地圖", "無可用地圖數據，請點擊立即同步資料", theme=theme, height=570)

    merged = df.copy()
    if env_df is not None and not env_df.empty and "location_name" in env_df.columns:
        env_cols = [c for c in ["location_name", "uv_index", "uv_level", "uv_advice", "aqi", "aqi_status", "pm25", "pm10", "aqi_advice"] if c in env_df.columns]
        merged = pd.merge(
            merged,
            env_df[env_cols],
            on="location_name",
            how="left"
        )

    map_data = []
    for _, row in merged.iterrows():
        loc = row["location_name"]
        coords = LOCATION_COORDS.get(loc)
        if coords:
            # Parse rain probability safely
            raw_rain = row.get("rain_prob", 0)
            try:
                rain_val = int(raw_rain)
            except (ValueError, TypeError):
                rain_val = 0

            # Actionable advice based on rain probability
            if rain_val >= 70:
                rain_adv = "強降雨機率高，出門必備雨具"
            elif rain_val >= 30:
                rain_adv = "有短暫陣雨機率，外出建議攜帶折傘"
            else:
                rain_adv = "降雨機率低，天氣晴朗乾爽"

            max_t = row.get("max_temp", 28)
            min_t = row.get("min_temp", 20)
            uv_val = round(float(row.get("uv_index", 7.0)), 1)
            aqi_val = int(row.get("aqi", 50))

            # Determine direct map label text based on mode and label_mode
            if label_mode == "none":
                lbl_text = None
            elif label_mode == "value":
                if mode in ("rain", "precipitation"):
                    lbl_text = f"{rain_val}%"
                elif mode == "uv":
                    lbl_text = f"UVI {uv_val}"
                elif mode == "aqi":
                    lbl_text = f"AQI {aqi_val}"
                else:
                    lbl_text = f"{max_t}°C"
            else:  # "both" (default: county name + value)
                if mode in ("rain", "precipitation"):
                    lbl_text = f"{loc} {rain_val}%"
                elif mode == "uv":
                    lbl_text = f"{loc} ☀️{uv_val}"
                elif mode == "aqi":
                    lbl_text = f"{loc} 🌿{aqi_val}"
                else:
                    lbl_text = f"{loc} {max_t}°C"

            item = {
                "location": loc,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "weather": row.get("weather_state", "晴"),
                "temp": f"{min_t}~{max_t}°C",
                "rain_prob": f"{rain_val}%",
                "rain_val": rain_val,
                "rain_advice": rain_adv,
                "comfort": row.get("comfort", "舒適"),
                "max_temp": max_t,
                "uv_index": uv_val,
                "uv_level": row.get("uv_level", "高量級"),
                "uv_advice": row.get("uv_advice", "做好防曬"),
                "aqi": aqi_val,
                "aqi_status": row.get("aqi_status", "普通"),
                "pm25": row.get("pm25", 15.0),
                "pm10": row.get("pm10", 25.0),
                "aqi_advice": row.get("aqi_advice", "正常活動"),
                "label": lbl_text
            }
            map_data.append(item)

    map_df = pd.DataFrame(map_data)
    if map_df.empty:
        return _create_empty_fig("🌤️ 台灣天氣分佈地圖", "無符合座標之縣市資料", theme=theme, height=570)

    map_func = getattr(px, "scatter_map", None) or getattr(px, "scatter_mapbox", None)
    map_style_param = "map_style" if hasattr(px, "scatter_map") else "mapbox_style"

    range_color = None
    if mode == "uv":
        color_col = "uv_index"
        colorscale = "YlOrRd"
        title_text = "☀️ 台灣各縣市即時紫外線 (UV) 分布圖"
        colorbar_title = "紫外線指數 (UVI)"
        range_color = [0, 15]
        hover_data = {
            "lat": False,
            "lon": False,
            "uv_index": True,
            "uv_level": True,
            "weather": True,
            "temp": True,
            "uv_advice": True
        }
    elif mode == "aqi":
        color_col = "aqi"
        colorscale = "RdYlGn_r"
        title_text = "🌿 台灣各縣市空氣品質指標 (AQI) 分布圖"
        colorbar_title = "空氣品質 (AQI)"
        range_color = [0, 150]
        hover_data = {
            "lat": False,
            "lon": False,
            "aqi": True,
            "aqi_status": True,
            "pm25": True,
            "pm10": True,
            "aqi_advice": True
        }
    elif mode in ("rain", "precipitation"):
        color_col = "rain_val"
        colorscale = [
            [0.0, "#BAE6FD"],   # 0% 晴朗乾爽 (天藍淺色)
            [0.2, "#38BDF8"],   # 20% 微弱飄雨
            [0.4, "#0284C7"],   # 40% 短暫陣雨
            [0.7, "#1D4ED8"],   # 70% 顯著降雨 (深藍)
            [1.0, "#312E81"]    # 100% 強降雨 (深紫靛藍)
        ]
        title_text = "🌧️ 台灣各縣市即時降雨機率 (PoP) 分布圖"
        colorbar_title = "降雨機率 (%)"
        range_color = [0, 100]
        hover_data = {
            "lat": False,
            "lon": False,
            "rain_prob": True,
            "rain_advice": True,
            "weather": True,
            "temp": True,
            "comfort": True
        }
    else:
        color_col = "max_temp"
        colorscale = "Plasma"
        title_text = "🌤️ 台灣各縣市即時氣溫與天氣現象分布圖"
        colorbar_title = "最高溫 (°C)"
        hover_data = {
            "lat": False,
            "lon": False,
            "weather": True,
            "temp": True,
            "rain_prob": True,
            "comfort": True
        }

    kwargs = {
        "lat": "lat",
        "lon": "lon",
        "hover_name": "location",
        "hover_data": hover_data,
        "color": color_col,
        "color_continuous_scale": colorscale,
        "size": [22] * len(map_df),
        "zoom": 6.8,
        "center": {"lat": 23.8, "lon": 120.9},
        map_style_param: t["map_style"],
        "template": t["template"]
    }

    if range_color:
        kwargs["range_color"] = range_color

    if label_mode != "none":
        kwargs["text"] = "label"

    fig = map_func(map_df, **kwargs)

    # Style direct value/name labels
    if label_mode != "none":
        fig.update_traces(
            mode="markers+text",
            textposition="top right",
            textfont=dict(
                size=11,
                family="Plus Jakarta Sans, Noto Sans TC, sans-serif",
                color=t["font_color"]
            )
        )

    fig.update_layout(
        title=dict(text=title_text, font=dict(color=t["font_color"], size=16)),
        template=t["template"],
        margin=dict(l=0, r=0, t=50, b=0),
        height=570,
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        coloraxis_colorbar=dict(
            title=dict(text=colorbar_title, font=dict(color=t["font_color"])),
            tickfont=dict(color=t["font_color"])
        )
    )
    return fig


def create_aqi_bar_chart(env_df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Create a ranked bar chart comparing AQI across all counties with color coding."""
    t = _get_theme_config(theme)
    title_text = "🌿 全台各縣市空氣品質指標 (AQI) 排名比較"

    if isinstance(env_df, list):
        env_df = pd.DataFrame(env_df) if env_df else pd.DataFrame()
    if env_df is None or env_df.empty or "aqi" not in env_df.columns:
        return _create_empty_fig(title_text, "無可用空氣品質數據，請點擊立即同步資料", theme=theme)

    df_sorted = env_df.sort_values(by="aqi", ascending=True).copy()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["location_name"],
        y=df_sorted["aqi"],
        marker=dict(
            color=df_sorted["aqi_color"] if "aqi_color" in df_sorted.columns else "#2196F3"
        ),
        text=[f"{aqi} ({st})" for aqi, st in zip(df_sorted["aqi"], df_sorted["aqi_status"])],
        textposition="outside",
        textfont=dict(color=t["font_color"], size=11),
        hovertemplate="<b>%{x}</b><br>AQI 指標: %{y}<br>狀態: %{text}<br>PM2.5: %{customdata[0]} µg/m³<br>PM10: %{customdata[1]} µg/m³<extra></extra>",
        customdata=list(zip(df_sorted["pm25"], df_sorted["pm10"]))
    ))

    # Add reference threshold lines for AQI standard
    fig.add_hline(y=50, line_dash="dash", line_color="#00E400", annotation_text="良好 (<=50)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=11))
    fig.add_hline(y=100, line_dash="dash", line_color="#FFD700", annotation_text="普通 (<=100)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=11))
    fig.add_hline(y=150, line_dash="dash", line_color="#FF7E00", annotation_text="敏感不健康 (<=150)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=11))

    fig.update_layout(
        title=dict(text=title_text, font=dict(color=t["font_color"], size=16)),
        xaxis_title=dict(text="縣市", font=dict(color=t["font_color"])),
        yaxis_title=dict(text="AQI 數值", font=dict(color=t["font_color"])),
        yaxis=dict(range=[0, max(120, df_sorted["aqi"].max() + 25)], gridcolor=t["grid_color"], tickfont=dict(color=t["font_color"])),
        xaxis=dict(gridcolor=t["grid_color"], tickfont=dict(color=t["font_color"]), tickangle=-35),
        hovermode="x unified",
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        height=450,
        margin=dict(l=40, r=40, t=60, b=80)
    )
    return fig


def create_uv_bar_chart(env_df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Create a bar chart comparing UV Index across counties."""
    t = _get_theme_config(theme)
    title_text = "☀️ 全台各縣市紫外線指數 (UVI) 分布比較"

    if isinstance(env_df, list):
        env_df = pd.DataFrame(env_df) if env_df else pd.DataFrame()
    if env_df is None or env_df.empty or "uv_index" not in env_df.columns:
        return _create_empty_fig(title_text, "無可用紫外線數據，請點擊立即同步資料", theme=theme)

    df_sorted = env_df.sort_values(by="uv_index", ascending=False).copy()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sorted["location_name"],
        y=df_sorted["uv_index"],
        marker=dict(
            color=df_sorted["uv_color"] if "uv_color" in df_sorted.columns else "#FF9800"
        ),
        text=[f"{uv} ({lvl})" for uv, lvl in zip(df_sorted["uv_index"], df_sorted["uv_level"])],
        textposition="outside",
        textfont=dict(color=t["font_color"], size=11),
        hovertemplate="<b>%{x}</b><br>紫外線指數: %{y}<br>等級: %{text}<extra></extra>"
    ))

    fig.add_hline(y=3, line_dash="dot", line_color="#FFD700", annotation_text="中量級 (>=3)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=11))
    fig.add_hline(y=6, line_dash="dot", line_color="#FF7E00", annotation_text="高量級 (>=6)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=11))
    fig.add_hline(y=8, line_dash="dot", line_color="#E51C23", annotation_text="過量級 (>=8)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=11))
    fig.add_hline(y=11, line_dash="dot", line_color="#9C27B0", annotation_text="危險級 (>=11)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=11))

    fig.update_layout(
        title=dict(text=title_text, font=dict(color=t["font_color"], size=16)),
        xaxis_title=dict(text="縣市", font=dict(color=t["font_color"])),
        yaxis_title=dict(text="紫外線指數 (UVI)", font=dict(color=t["font_color"])),
        yaxis=dict(range=[0, max(12, df_sorted["uv_index"].max() + 3)], gridcolor=t["grid_color"], tickfont=dict(color=t["font_color"])),
        xaxis=dict(gridcolor=t["grid_color"], tickfont=dict(color=t["font_color"]), tickangle=-35),
        hovermode="x unified",
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        height=450,
        margin=dict(l=40, r=40, t=60, b=80)
    )
    return fig


def create_city_env_gauges(city_row: Dict[str, Any], theme: str = "light") -> go.Figure:
    """Create dual gauges for a specific city showing UV and AQI."""
    from plotly.subplots import make_subplots
    t = _get_theme_config(theme)

    if not city_row or not isinstance(city_row, dict):
        city_row = {}

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=["☀️ 紫外線指數 (UVI)", "🌿 空氣品質指標 (AQI)"]
    )

    raw_uvi = city_row.get("uv_index", 7.0)
    uvi = round(float(raw_uvi), 1) if pd.notna(raw_uvi) else 7.0
    uv_level = city_row.get("uv_level", "高量級")
    raw_aqi = city_row.get("aqi", 50)
    aqi = int(raw_aqi) if pd.notna(raw_aqi) else 50
    aqi_status = city_row.get("aqi_status", "普通")

    # UV Gauge (0 to 15)
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=uvi,
        title={'text': f"<b>{uv_level}</b><br><span style='font-size:0.8em;color:{t['font_color']};'>CWA 觀測值</span>", 'font': {'color': t["font_color"]}},
        number={'suffix': " UVI", 'font': {'color': t["font_color"], 'size': 34}},
        gauge={
            'axis': {'range': [0, 15], 'tickwidth': 1, 'tickcolor': t["font_color"]},
            'bar': {'color': city_row.get("uv_color", "#FF9800"), 'thickness': 0.3},
            'steps': [
                {'range': [0, 2.9], 'color': "rgba(0, 228, 0, 0.25)"},
                {'range': [2.9, 5.9], 'color': "rgba(255, 215, 0, 0.25)"},
                {'range': [5.9, 7.9], 'color': "rgba(255, 126, 0, 0.25)"},
                {'range': [7.9, 10.9], 'color': "rgba(229, 28, 35, 0.25)"},
                {'range': [10.9, 15], 'color': "rgba(156, 39, 176, 0.25)"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': uvi
            }
        }
    ), row=1, col=1)

    # AQI Gauge (0 to 300)
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=aqi,
        title={'text': f"<b>{aqi_status}</b><br><span style='font-size:0.8em;color:{t['font_color']};'>PM2.5: {city_row.get('pm25', 15)} µg/m³</span>", 'font': {'color': t["font_color"]}},
        number={'suffix': " AQI", 'font': {'color': t["font_color"], 'size': 34}},
        gauge={
            'axis': {'range': [0, 250], 'tickwidth': 1, 'tickcolor': t["font_color"]},
            'bar': {'color': city_row.get("aqi_color", "#FFD700"), 'thickness': 0.3},
            'steps': [
                {'range': [0, 50], 'color': "rgba(0, 228, 0, 0.25)"},
                {'range': [50, 100], 'color': "rgba(255, 215, 0, 0.25)"},
                {'range': [100, 150], 'color': "rgba(255, 126, 0, 0.25)"},
                {'range': [150, 200], 'color': "rgba(229, 28, 35, 0.25)"},
                {'range': [200, 250], 'color': "rgba(156, 39, 176, 0.25)"}
            ],
            'threshold': {
                'line': {'color': "darkred", 'width': 4},
                'thickness': 0.75,
                'value': aqi
            }
        }
    ), row=1, col=2)

    fig.for_each_annotation(lambda a: a.update(font=dict(color=t["font_color"], size=14)))

    fig.update_layout(
        height=320,
        margin=dict(l=30, r=30, t=50, b=20),
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"])
    )
    return fig


def create_7day_trend_chart(df_slots: pd.DataFrame, city_name: str, theme: str = "light") -> go.Figure:
    """Create interactive 7-day temperature range and rain probability trend chart."""
    t = _get_theme_config(theme)
    title_text = f"📅 {city_name} 未來一週 (7 天) 氣溫變化與降雨機率曲線"

    if isinstance(df_slots, list):
        df_slots = pd.DataFrame(df_slots) if df_slots else pd.DataFrame()
    if df_slots is None or df_slots.empty or "max_temp" not in df_slots.columns:
        return _create_empty_fig(title_text, "無可用 7 天預報數據，請點擊立即同步資料", theme=theme, height=480)

    df_copy = df_slots.copy()

    # Create readable period labels, e.g. "10/05 (一) 白天", "10/05 (一) 晚上"
    def make_label(row):
        try:
            st_str = str(row["start_time"])[:16].replace("T", " ")
            dt = datetime.datetime.strptime(st_str[:10], "%Y-%m-%d")
            hour = int(st_str[11:13]) if len(st_str) >= 13 else 6
            weekdays = ["一", "二", "三", "四", "五", "六", "日"]
            wd = weekdays[dt.weekday()]
            slot_name = "白天" if 6 <= hour < 18 else "晚上"
            return f"{dt.month}/{dt.day} ({wd}) {slot_name}"
        except Exception:
            return str(row["start_time"])[5:16]

    df_copy["slot_label"] = df_copy.apply(make_label, axis=1)

    fig = go.Figure()

    # Apparent temperature zone
    fig.add_trace(go.Scatter(
        x=df_copy["slot_label"],
        y=df_copy["apparent_max_temp"],
        mode="lines",
        line=dict(color="rgba(255, 112, 67, 0.45)", width=1.5, dash="dot"),
        name="體感最高溫 (°C)",
        hoverinfo="skip"
    ))

    # Min Temp line
    fig.add_trace(go.Scatter(
        x=df_copy["slot_label"],
        y=df_copy["min_temp"],
        mode="lines+markers+text",
        name="最低溫 (°C)",
        line=dict(color="#29B6F6", width=3),
        marker=dict(size=8, color="#29B6F6"),
        text=[f"{temp}°" for temp in df_copy["min_temp"]],
        textposition="bottom center",
        textfont=dict(color=t["font_color"], size=11),
        hovertemplate="<b>%{x}</b><br>最低溫: %{y}°C<extra></extra>"
    ))

    # Max Temp line (with fill to Min Temp)
    fig.add_trace(go.Scatter(
        x=df_copy["slot_label"],
        y=df_copy["max_temp"],
        mode="lines+markers+text",
        name="最高溫 (°C)",
        line=dict(color="#FF5722", width=3),
        fill='tonexty',
        fillcolor='rgba(255, 87, 34, 0.15)',
        marker=dict(size=8, color="#FF5722"),
        text=[f"{temp}°" for temp in df_copy["max_temp"]],
        textposition="top center",
        textfont=dict(color=t["font_color"], size=11),
        hovertemplate="<b>%{x}</b><br>最高溫: %{y}°C<br>天氣: %{customdata[0]}<br>濕度: %{customdata[1]}%<extra></extra>",
        customdata=list(zip(df_copy["weather_state"], df_copy["relative_humidity"]))
    ))

    # Rain Probability Bar Chart on Secondary Y Axis
    fig.add_trace(go.Bar(
        x=df_copy["slot_label"],
        y=df_copy["rain_prob"],
        name="降雨機率 (%)",
        yaxis="y2",
        marker=dict(color="rgba(3, 169, 244, 0.25)" if theme != "dark" else "rgba(3, 169, 244, 0.35)", line=dict(color="#03A9F4", width=1)),
        text=[f"{p}%" if p > 0 else "" for p in df_copy["rain_prob"]],
        textposition="outside",
        textfont=dict(color=t["font_color"], size=11),
        hovertemplate="<b>%{x}</b><br>降雨機率: %{y}%<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text=f"📅 {city_name} 未來一週 (7 天) 氣溫變化與降雨機率曲線", font=dict(color=t["font_color"], size=16)),
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        xaxis=dict(
            title=dict(text="預報時段", font=dict(color=t["font_color"])),
            tickangle=-35,
            showgrid=True,
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        yaxis=dict(
            title=dict(text="溫度 (°C)", font=dict(color=t["font_color"])),
            range=[max(5, df_copy["min_temp"].min() - 4), df_copy["max_temp"].max() + 5],
            showgrid=True,
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        yaxis2=dict(
            title=dict(text="降雨機率 (%)", font=dict(color=t["font_color"])),
            overlaying="y",
            side="right",
            range=[0, 100],
            showgrid=False,
            tickfont=dict(color=t["font_color"])
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, font=dict(color=t["font_color"])),
        height=480,
        margin=dict(l=40, r=40, t=80, b=80),
        hovermode="x unified"
    )
    return fig


def create_history_trend_chart(history_df: pd.DataFrame, city_name: str, metric_mode: str = "composite", theme: str = "light") -> go.Figure:
    """
    Create historical trajectory trend chart for a single city.
    metric_mode options:
      - 'composite': Temperature line + Rain probability bars on dual axes
      - 'temp_band': Max, Min, and Avg temperature band chart
      - 'rain': Rain probability trend with risk zones
      - 'aqi': AQI and PM2.5 trajectory with safety thresholds
      - 'uv': UV Index trajectory with diurnal peaks
    """
    t = _get_theme_config(theme)
    title_text = f"📈 {city_name} 歷史觀測趨勢圖"

    if isinstance(history_df, list):
        history_df = pd.DataFrame(history_df) if history_df else pd.DataFrame()
    if history_df is None or history_df.empty or "recorded_at" not in history_df.columns:
        return _create_empty_fig(title_text, "尚無歷史軌跡數據，系統將隨定時同步累積", theme=theme, height=450)

    df_sorted = history_df.sort_values(by="recorded_at", ascending=True).copy()

    # Format recorded_at for cleaner x-axis labels
    df_sorted["time_label"] = df_sorted["recorded_at"].apply(lambda x: str(x)[5:16] if len(str(x)) >= 16 else str(x))

    fig = go.Figure()

    if metric_mode == "temp_band":
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["max_temp"],
            mode="lines",
            name="最高溫 (°C)",
            line=dict(color="#FF7043", width=2, dash="dash"),
            hovertemplate="<b>最高溫</b>: %{y}°C<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["min_temp"],
            mode="lines",
            name="最低溫 (°C)",
            line=dict(color="#38BDF8", width=2, dash="dash"),
            fill="tonexty",
            fillcolor="rgba(255, 167, 38, 0.12)" if theme != "dark" else "rgba(255, 167, 38, 0.2)",
            hovertemplate="<b>最低溫</b>: %{y}°C<extra></extra>"
        ))
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["avg_temp"],
            mode="lines+markers",
            name="平均氣溫 (°C)",
            line=dict(color="#F59E0B", width=3),
            marker=dict(size=7, color="#F59E0B"),
            hovertemplate="<b>平均溫</b>: %{y}°C<br>天氣: %{customdata[0]}<br>舒適度: %{customdata[1]}<extra></extra>",
            customdata=list(zip(df_sorted["weather_state"], df_sorted["comfort"]))
        ))
        title_text = f"🌡️ {city_name} 歷史氣溫軌跡與日夜溫差區間帶"
        y_title = "溫度 (°C)"

    elif metric_mode == "rain":
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["rain_prob"],
            mode="lines+markers",
            name="降雨機率 (%)",
            line=dict(color="#0284C7", width=3),
            marker=dict(size=8, color="#0284C7"),
            fill="tozeroy",
            fillcolor="rgba(2, 132, 199, 0.18)" if theme != "dark" else "rgba(2, 132, 199, 0.3)",
            hovertemplate="<b>降雨機率</b>: %{y}%<br>天氣: %{customdata}<extra></extra>",
            customdata=df_sorted["weather_state"]
        ))
        fig.add_hline(y=30, line_dash="dash", line_color="#F59E0B", annotation_text="短暫降雨 (30%)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=10))
        fig.add_hline(y=70, line_dash="dash", line_color="#EF4444", annotation_text="強降雨警戒 (70%)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=10))
        title_text = f"🌧️ {city_name} 歷史降雨機率變化軌跡"
        y_title = "降雨機率 (%)"

    elif metric_mode == "aqi":
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["aqi"],
            mode="lines+markers",
            name="空氣品質 AQI",
            line=dict(color="#10B981", width=3),
            marker=dict(size=7, color="#10B981"),
            hovertemplate="<b>AQI</b>: %{y}<br>狀態: %{customdata}<extra></extra>",
            customdata=df_sorted["aqi_status"]
        ))
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["pm25"],
            mode="lines+markers",
            name="PM2.5 (µg/m³)",
            yaxis="y2",
            line=dict(color="#A855F7", width=2, dash="dot"),
            marker=dict(size=6, color="#A855F7"),
            hovertemplate="<b>PM2.5</b>: %{y} µg/m³<extra></extra>"
        ))
        fig.add_hline(y=50, line_dash="dash", line_color="#10B981", annotation_text="良好 (<=50)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=10))
        fig.add_hline(y=100, line_dash="dash", line_color="#F59E0B", annotation_text="普通 (<=100)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=10))
        title_text = f"🌿 {city_name} 歷史空氣品質 (AQI) 與 PM2.5 軌跡"
        y_title = "空氣品質 (AQI)"

    elif metric_mode == "uv":
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["uv_index"],
            mode="lines+markers",
            name="紫外線指數 (UVI)",
            line=dict(color="#EC4899", width=3),
            marker=dict(size=8, color="#EC4899"),
            fill="tozeroy",
            fillcolor="rgba(236, 72, 153, 0.15)" if theme != "dark" else "rgba(236, 72, 153, 0.25)",
            hovertemplate="<b>UVI</b>: %{y}<br>等級: %{customdata}<extra></extra>",
            customdata=df_sorted["uv_level"]
        ))
        fig.add_hline(y=6, line_dash="dash", line_color="#F59E0B", annotation_text="高量級 (6)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=10))
        fig.add_hline(y=8, line_dash="dash", line_color="#EF4444", annotation_text="過量級 (8)", annotation_position="top left", annotation_font=dict(color=t["font_color"], size=10))
        title_text = f"☀️ {city_name} 歷史紫外線指數 (UVI) 軌跡"
        y_title = "紫外線指數 (UVI)"

    else:  # 'composite' (default)
        fig.add_trace(go.Scatter(
            x=df_sorted["time_label"],
            y=df_sorted["avg_temp"],
            mode="lines+markers",
            name="平均氣溫 (°C)",
            line=dict(color="#FF7043", width=3),
            marker=dict(size=8, color="#FF7043"),
            fill="tozeroy",
            fillcolor="rgba(255, 112, 67, 0.12)" if theme != "dark" else "rgba(255, 112, 67, 0.22)",
            hovertemplate="<b>時間</b>: %{x}<br>氣溫: %{y}°C<br>天氣: %{customdata[0]}<br>舒適度: %{customdata[1]}<extra></extra>",
            customdata=list(zip(df_sorted["weather_state"], df_sorted["comfort"]))
        ))
        fig.add_trace(go.Bar(
            x=df_sorted["time_label"],
            y=df_sorted["rain_prob"],
            name="降雨機率 (%)",
            yaxis="y2",
            marker=dict(
                color="rgba(2, 132, 199, 0.28)" if theme != "dark" else "rgba(56, 189, 248, 0.35)",
                line=dict(color="#0284C7" if theme != "dark" else "#38BDF8", width=1)
            ),
            hovertemplate="降雨機率: %{y}%<extra></extra>"
        ))
        title_text = f"📈 {city_name} 歷史氣溫與降雨機率綜合趨勢"
        y_title = "溫度 (°C)"

    layout_kwargs = dict(
        title=dict(text=title_text, font=dict(color=t["font_color"], size=16)),
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        xaxis=dict(
            title=dict(text="觀測紀錄時間", font=dict(color=t["font_color"])),
            tickangle=-30,
            showgrid=True,
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        yaxis=dict(
            title=dict(text=y_title, font=dict(color=t["font_color"])),
            showgrid=True,
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, font=dict(color=t["font_color"])),
        height=450,
        margin=dict(l=40, r=40, t=80, b=70),
        hovermode="x unified"
    )

    if metric_mode in ("composite", "aqi"):
        layout_kwargs["yaxis2"] = dict(
            title=dict(text="降雨機率 (%)" if metric_mode == "composite" else "PM2.5 (µg/m³)", font=dict(color=t["font_color"])),
            overlaying="y",
            side="right",
            range=[0, 100] if metric_mode == "composite" else None,
            showgrid=False,
            tickfont=dict(color=t["font_color"])
        )

    fig.update_layout(**layout_kwargs)
    return fig


def create_multi_city_history_chart(history_df: pd.DataFrame, metric: str = "avg_temp", theme: str = "light") -> go.Figure:
    """
    Create a comparative multi-city historical line chart.
    metric options: 'avg_temp', 'rain_prob', 'aqi', 'uv_index', 'pm25'
    """
    t = _get_theme_config(theme)
    metric_meta = {
        "avg_temp": {"name": "平均氣溫", "unit": "°C", "title": "🌡️ 各縣市歷史平均氣溫走勢比較"},
        "rain_prob": {"name": "降雨機率", "unit": "%", "title": "🌧️ 各縣市歷史降雨機率走勢比較"},
        "aqi": {"name": "空氣品質 (AQI)", "unit": "", "title": "🌿 各縣市歷史空氣品質 (AQI) 走勢比較"},
        "uv_index": {"name": "紫外線指數 (UVI)", "unit": "", "title": "☀️ 各縣市歷史紫外線指數 (UVI) 走勢比較"},
        "pm25": {"name": "PM2.5 濃度", "unit": "µg/m³", "title": "💨 各縣市歷史 PM2.5 濃度走勢比較"}
    }
    meta = metric_meta.get(metric, metric_meta["avg_temp"])

    if isinstance(history_df, list):
        history_df = pd.DataFrame(history_df) if history_df else pd.DataFrame()
    if history_df is None or history_df.empty or "location_name" not in history_df.columns or "recorded_at" not in history_df.columns:
        return _create_empty_fig(meta["title"], "尚無多縣市歷史比較數據，請點擊立即同步資料", theme=theme, height=450)

    color_palette = [
        "#38BDF8", "#F59E0B", "#10B981", "#EC4899", "#8B5CF6",
        "#06B6D4", "#EF4444", "#84CC16", "#F97316", "#6366F1"
    ]

    df_copy = history_df.sort_values(by="recorded_at", ascending=True).copy()
    df_copy["time_label"] = df_copy["recorded_at"].apply(lambda x: str(x)[5:16] if len(str(x)) >= 16 else str(x))

    fig = go.Figure()
    cities = df_copy["location_name"].unique()

    for idx, city in enumerate(cities):
        city_data = df_copy[df_copy["location_name"] == city]
        color = color_palette[idx % len(color_palette)]
        unit_str = f" {meta['unit']}" if meta['unit'] else ""

        fig.add_trace(go.Scatter(
            x=city_data["time_label"],
            y=city_data[metric],
            mode="lines+markers",
            name=city,
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            hovertemplate=f"<b>{city}</b>: %{{y}}{unit_str}<extra></extra>"
        ))

    fig.update_layout(
        title=dict(text=meta["title"], font=dict(color=t["font_color"], size=16)),
        template=t["template"],
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(color=t["font_color"]),
        xaxis=dict(
            title=dict(text="觀測紀錄時間", font=dict(color=t["font_color"])),
            tickangle=-30,
            showgrid=True,
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        yaxis=dict(
            title=dict(text=f"{meta['name']}{' (' + meta['unit'] + ')' if meta['unit'] else ''}", font=dict(color=t["font_color"])),
            showgrid=True,
            gridcolor=t["grid_color"],
            tickfont=dict(color=t["font_color"])
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1, font=dict(color=t["font_color"])),
        height=460,
        margin=dict(l=40, r=40, t=80, b=70),
        hovermode="x unified"
    )
    return fig

