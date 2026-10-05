"""7-Day Weather Forecast API Module for Taiwan Weather App.

Dataset: Central Weather Administration (CWA) F-D0047-091
(臺灣各縣市未來 1 週天氣預報)
"""

import os
import requests
import urllib3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from src.cwa_api import REGION_MAP

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CWA_7DAY_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"


def fetch_7day_forecast(api_key: str = None) -> Tuple[List[Dict[str, Any]], bool, str]:
    """
    Fetch 7-day (1-week) weather forecast for all Taiwan administrative divisions.
    Returns: (records, is_live_data, message)
    """
    key = (api_key or os.environ.get("CWA_API_KEY", "")).strip()

    if not key or key == "your_api_key_here":
        records = generate_mock_7day_forecast()
        return records, False, "使用示範展示資料（未配置 CWA API 授權碼）"

    params = {
        "Authorization": key,
        "format": "JSON"
    }

    try:
        try:
            r = requests.get(CWA_7DAY_API_URL, params=params, timeout=15)
        except requests.exceptions.SSLError:
            r = requests.get(CWA_7DAY_API_URL, params=params, verify=False, timeout=15)

        r.raise_for_status()
        data = r.json()

        if str(data.get("success", "")).lower() != "true":
            records = generate_mock_7day_forecast()
            return records, False, "CWA API 回應未成功，切換為模擬資料"

        records = parse_cwa_7day_json(data)
        return records, True, f"成功從氣象署 API 更新 {len(records)} 筆一週預報資料"

    except Exception as e:
        records = generate_mock_7day_forecast()
        return records, False, f"API 連線異常 ({str(e)})，已自動切換為一週備用示範資料"


def parse_cwa_7day_json(cwa_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse CWA F-D0047-091 JSON structure into flat record list."""
    records = []
    locations = cwa_json.get("records", {}).get("Locations", [{}])[0].get("Location", [])

    for loc in locations:
        loc_name = loc.get("LocationName", "")
        region = REGION_MAP.get(loc_name, "北部")

        # Map element name to its list of time slots
        elements = {elem.get("ElementName"): elem.get("Time", []) for elem in loc.get("WeatherElement", [])}

        max_t_list = elements.get("最高溫度", [])
        min_t_list = elements.get("最低溫度", [])
        avg_t_list = elements.get("平均溫度", [])
        app_max_list = elements.get("最高體感溫度", [])
        app_min_list = elements.get("最低體感溫度", [])
        pop_list = elements.get("12小時降雨機率", [])
        wx_list = elements.get("天氣現象", [])
        rh_list = elements.get("相對濕度", [])
        desc_list = elements.get("天氣預報綜合描述", [])

        num_slots = len(max_t_list)

        for i in range(num_slots):
            st = max_t_list[i].get("StartTime", "")
            et = max_t_list[i].get("EndTime", "")

            # Temperature values
            def get_val(lst, key, default):
                if i < len(lst):
                    vals = lst[i].get("ElementValue", [{}])
                    if vals and key in vals[0]:
                        v = vals[0][key]
                        try:
                            return int(float(v))
                        except (ValueError, TypeError):
                            return default
                return default

            def get_str(lst, key, default):
                if i < len(lst):
                    vals = lst[i].get("ElementValue", [{}])
                    if vals and key in vals[0]:
                        return vals[0][key]
                return default

            max_t = get_val(max_t_list, "MaxTemperature", 28)
            min_t = get_val(min_t_list, "MinTemperature", 22)
            avg_t = get_val(avg_t_list, "Temperature", int((max_t + min_t) / 2))
            app_max = get_val(app_max_list, "MaxApparentTemperature", max_t)
            app_min = get_val(app_min_list, "MinApparentTemperature", min_t)

            # Rain probability (some later slots may be "-" or missing)
            pop_str = get_str(pop_list, "ProbabilityOfPrecipitation", "20")
            pop = int(pop_str) if pop_str.isdigit() else 20

            wx = get_str(wx_list, "Weather", "多雲")
            rh = get_val(rh_list, "RelativeHumidity", 75)
            desc = get_str(desc_list, "WeatherDescription", "")

            records.append({
                "location_name": loc_name,
                "region": region,
                "start_time": st,
                "end_time": et,
                "min_temp": min_t,
                "max_temp": max_t,
                "avg_temp": avg_t,
                "apparent_min_temp": app_min,
                "apparent_max_temp": app_max,
                "rain_prob": pop,
                "weather_state": wx,
                "relative_humidity": rh,
                "weather_desc": desc
            })

    return records


def generate_mock_7day_forecast() -> List[Dict[str, Any]]:
    """Generate realistic 7-day mock forecast records for all 22 counties."""
    records = []
    now = datetime.now()
    all_counties = list(REGION_MAP.keys())

    weather_patterns = ["多雲時晴", "晴時多雲", "多雲短暫雨", "晴天", "陰天", "短暫陣雨", "多雲"]

    for city in all_counties:
        region = REGION_MAP.get(city, "北部")
        base_temp = 24 if region == "北部" else (26 if region == "中部" else 27)

        for day in range(7):
            day_date = now + timedelta(days=day)
            # Day slot (06:00 ~ 18:00)
            st_day = day_date.strftime("%Y-%m-%d 06:00:00")
            et_day = day_date.strftime("%Y-%m-%d 18:00:00")
            wx_day = weather_patterns[(day + len(city)) % len(weather_patterns)]
            max_t = base_temp + (day % 3)
            min_t = max_t - 6

            records.append({
                "location_name": city,
                "region": region,
                "start_time": st_day,
                "end_time": et_day,
                "min_temp": min_t,
                "max_temp": max_t,
                "avg_temp": int((max_t + min_t) / 2),
                "apparent_min_temp": min_t - 1,
                "apparent_max_temp": max_t + 2,
                "rain_prob": 20 + (day * 5) % 40,
                "weather_state": wx_day,
                "relative_humidity": 70 + (day % 15),
                "weather_desc": f"{city}{day_date.strftime('%m/%d')}{wx_day}，溫度約 {min_t}~{max_t} 度。"
            })

            # Night slot (18:00 ~ 06:00 next day)
            st_night = day_date.strftime("%Y-%m-%d 18:00:00")
            et_night = (day_date + timedelta(days=1)).strftime("%Y-%m-%d 06:00:00")
            wx_night = "多雲" if "雨" not in wx_day else "陰短暫雨"

            records.append({
                "location_name": city,
                "region": region,
                "start_time": st_night,
                "end_time": et_night,
                "min_temp": min_t - 1,
                "max_temp": max_t - 4,
                "avg_temp": min_t + 1,
                "apparent_min_temp": min_t - 2,
                "apparent_max_temp": max_t - 3,
                "rain_prob": 15 + (day * 5) % 35,
                "weather_state": wx_night,
                "relative_humidity": 80,
                "weather_desc": f"{city}夜間{wx_night}，稍有涼意。"
            })

    return records
