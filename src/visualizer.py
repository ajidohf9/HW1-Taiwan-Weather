"""Data Visualization Module for Taiwan Weather App using Plotly."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any
from src.cwa_api import LOCATION_COORDS


def create_temperature_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """Create a temperature range bar chart comparing cities."""
    fig = go.Figure()

    # Sort by region and location
    sorted_df = df.sort_values(by=["region", "max_temp"], ascending=[True, False])

    fig.add_trace(go.Bar(
        x=sorted_df["location_name"],
        y=sorted_df["max_temp"] - sorted_df["min_temp"],
        base=sorted_df["min_temp"],
        marker=dict(
            color=sorted_df["max_temp"],
            colorscale="Viridis",
            colorbar=dict(title="最高溫 (°C)"),
            showscale=True
        ),
        text=[f"{min_t}°C ~ {max_t}°C" for min_t, max_t in zip(sorted_df["min_temp"], sorted_df["max_temp"])],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>最低溫: %{base}°C<br>最高溫: %{customdata}°C<br>氣象: %{text}<extra></extra>",
        customdata=sorted_df["max_temp"]
    ))

    fig.update_layout(
        title="全台各縣市氣溫區間分佈 (°C)",
        xaxis_title="縣市",
        yaxis_title="氣溫 (°C)",
        yaxis=dict(range=[min(df["min_temp"].min() - 3, 10), max(df["max_temp"].max() + 5, 35)]),
        hovermode="x unified",
        template="plotly_white",
        height=450,
        margin=dict(l=40, r=40, t=60, b=80)
    )

    return fig


def create_trend_chart(periods_df: pd.DataFrame, city_name: str) -> go.Figure:
    """Create a multi-period temperature & rain probability trend for a selected city."""
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
        line=dict(color="#FF5722", width=3),
        marker=dict(size=10),
        text=[f"{t}°C" for t in periods_df["max_temp"]],
        textposition="top center"
    ))

    # Line for Min Temp
    fig.add_trace(go.Scatter(
        x=periods_df["period_label"],
        y=periods_df["min_temp"],
        mode="lines+markers+text",
        name="最低溫 (°C)",
        line=dict(color="#2196F3", width=3),
        marker=dict(size=10),
        text=[f"{t}°C" for t in periods_df["min_temp"]],
        textposition="bottom center"
    ))

    # Bar for Rain Probability on secondary axis
    fig.add_trace(go.Bar(
        x=periods_df["period_label"],
        y=periods_df["rain_prob"],
        name="降雨機率 (%)",
        marker=dict(color="rgba(33, 150, 243, 0.3)"),
        yaxis="y2",
        text=[f"{p}%" for p in periods_df["rain_prob"]],
        textposition="auto"
    ))

    fig.update_layout(
        title=f"{city_name} 36 小時天氣與降雨機率趨勢",
        template="plotly_white",
        yaxis=dict(
            title="溫度 (°C)",
            range=[min(periods_df["min_temp"].min() - 4, 10), max(periods_df["max_temp"].max() + 5, 38)]
        ),
        yaxis2=dict(
            title="降雨機率 (%)",
            overlaying="y",
            side="right",
            range=[0, 100],
            showgrid=False
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=40, r=40, t=70, b=40)
    )

    return fig


def create_taiwan_weather_map(df: pd.DataFrame) -> go.Figure:
    """Create an interactive map of Taiwan displaying weather conditions and temperatures."""
    map_data = []
    for _, row in df.iterrows():
        loc = row["location_name"]
        coords = LOCATION_COORDS.get(loc)
        if coords:
            map_data.append({
                "location": loc,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "weather": row["weather_state"],
                "temp": f"{row['min_temp']}~{row['max_temp']}°C",
                "rain_prob": row["rain_prob"],
                "max_temp": row["max_temp"],
                "comfort": row["comfort"]
            })

    map_df = pd.DataFrame(map_data)

    # Plotly 6+ / 7+ uses scatter_map instead of scatter_mapbox
    map_func = getattr(px, "scatter_map", None) or getattr(px, "scatter_mapbox", None)
    map_style_param = "map_style" if hasattr(px, "scatter_map") else "mapbox_style"

    kwargs = {
        "lat": "lat",
        "lon": "lon",
        "hover_name": "location",
        "hover_data": {
            "lat": False,
            "lon": False,
            "weather": True,
            "temp": True,
            "rain_prob": True,
            "comfort": True
        },
        "color": "max_temp",
        "color_continuous_scale": "Plasma",
        "size": [18] * len(map_df),
        "zoom": 6.8,
        "center": {"lat": 23.8, "lon": 120.9},
        map_style_param: "carto-positron",
        "title": "台灣即時天氣觀測地圖 (點選查看細節)"
    }

    fig = map_func(map_df, **kwargs)

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=550,
        coloraxis_colorbar=dict(title="最高溫 (°C)")
    )

    return fig
