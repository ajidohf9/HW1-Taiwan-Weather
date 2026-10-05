import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from src import db, visualizer

print('=== 1. DB connection and tables ===')
conn = db.get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]
print('Tables in DB:', tables)
for t in tables:
    cursor.execute(f"SELECT count(*) FROM {t}")
    print(f"  {t}: {cursor.fetchone()[0]} rows")
conn.close()

print('=== 2. Testing db query functions ===')
locs = db.get_all_locations()
print('get_all_locations count:', len(locs))

latest_fc = db.get_latest_forecasts()
print('get_latest_forecasts count:', len(latest_fc))

all_7d = db.get_all_7day_forecasts()
print('get_all_7day_forecasts count:', len(all_7d))

env = db.get_env_metrics()
print('get_env_metrics count:', len(env))

alerts = db.get_weather_alerts()
print('get_weather_alerts count:', len(alerts))

county_alerts = db.get_county_alerts_dict()
print('get_county_alerts_dict keys count:', len(county_alerts))

freshness = db.get_data_freshness_status()
print('get_data_freshness_status level:', freshness.get('level'))

hist = db.get_all_history(limit=50)
print('get_all_history count:', len(hist))

sample_loc = locs[0] if locs else '臺北市'
loc_fc = db.get_location_forecast(sample_loc)
print(f'get_location_forecast({sample_loc}): {len(loc_fc)} rows')
loc_7d = db.get_location_7day_forecast(sample_loc)
print(f'get_location_7day_forecast({sample_loc}): {len(loc_7d)} rows')
loc_env = db.get_location_env(sample_loc)
print(f'get_location_env({sample_loc}) exists:', loc_env is not None)
loc_hist = db.get_location_history(sample_loc, limit=10)
print(f'get_location_history({sample_loc}): {len(loc_hist)} rows')

multi_hist = db.get_multi_location_history(locs[:3])
print(f'get_multi_location_history: {len(multi_hist)} rows')

print('=== 3. Testing Visualizer with real data ===')
for theme in ['dark', 'light']:
    # Map modes: temperature, rain, aqi, uv
    for mode in ['temperature', 'rain', 'aqi', 'uv']:
        for label_mode in ['both', 'name', 'value']:
            fig_map = visualizer.create_taiwan_weather_map(
                latest_fc, env_df=env, mode=mode, theme=theme, label_mode=label_mode
            )
            assert fig_map is not None, f"Map failed for mode {mode}, theme {theme}"
    
    # Temperature comparison chart
    fig_comp = visualizer.create_temperature_comparison_chart(latest_fc, theme=theme)
    assert fig_comp is not None

    # 36h chart
    fig_36h = visualizer.create_trend_chart(loc_fc, sample_loc, theme=theme)
    assert fig_36h is not None

    # 7d chart
    fig_7d = visualizer.create_7day_trend_chart(loc_7d, sample_loc, theme=theme)
    assert fig_7d is not None

    # AQI & UV charts
    fig_aqi = visualizer.create_aqi_bar_chart(env, theme=theme)
    assert fig_aqi is not None
    fig_uv = visualizer.create_uv_bar_chart(env, theme=theme)
    assert fig_uv is not None

    # Gauge
    if loc_env:
        fig_gauge = visualizer.create_city_env_gauges(loc_env, theme=theme)
        assert fig_gauge is not None

    # History charts
    if len(hist) > 0:
        for m in ['composite', 'temp_band', 'rain', 'aqi', 'uv']:
            # Test with list of dicts
            fig_h_list = visualizer.create_history_trend_chart(hist, sample_loc, metric_mode=m, theme=theme)
            assert fig_h_list is not None
            # Test with DataFrame
            fig_h_df = visualizer.create_history_trend_chart(pd.DataFrame(hist), sample_loc, metric_mode=m, theme=theme)
            assert fig_h_df is not None
        
        for m in ['avg_temp', 'rain_prob', 'aqi', 'uv_index', 'pm25']:
            # Test with list of dicts
            fig_mh_list = visualizer.create_multi_city_history_chart(multi_hist, metric=m, theme=theme)
            assert fig_mh_list is not None
            # Test with DataFrame
            fig_mh_df = visualizer.create_multi_city_history_chart(pd.DataFrame(multi_hist), metric=m, theme=theme)
            assert fig_mh_df is not None

print('Real data tests passed successfully!')

print('=== 4. Testing Visualizer with EMPTY / Edge Case data ===')
empty_df = pd.DataFrame()
for theme in ['dark', 'light']:
    fig_e1 = visualizer.create_taiwan_weather_map(empty_df, env_df=empty_df, theme=theme)
    assert fig_e1 is not None
    fig_e2 = visualizer.create_temperature_comparison_chart(empty_df, theme=theme)
    assert fig_e2 is not None
    fig_e3 = visualizer.create_trend_chart(empty_df, '臺北市', theme=theme)
    assert fig_e3 is not None
    fig_e4 = visualizer.create_7day_trend_chart(empty_df, '臺北市', theme=theme)
    assert fig_e4 is not None
    fig_e5 = visualizer.create_aqi_bar_chart(empty_df, theme=theme)
    assert fig_e5 is not None
    fig_e6 = visualizer.create_uv_bar_chart(empty_df, theme=theme)
    assert fig_e6 is not None
    fig_e7 = visualizer.create_city_env_gauges({}, theme=theme)
    assert fig_e7 is not None
    fig_e8 = visualizer.create_history_trend_chart(empty_df, '臺北市', theme=theme)
    assert fig_e8 is not None
    fig_e9 = visualizer.create_multi_city_history_chart(empty_df, theme=theme)
    assert fig_e9 is not None

print('Empty & edge case tests passed successfully!')
print('=== ALL TESTS PASSED WITH 0 ERRORS! ===')
