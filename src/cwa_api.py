"""CWA (Central Weather Administration) Open Data API Client."""

import os
import requests
import urllib3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# Try loading .env file
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    load_dotenv(dotenv_path=env_path)
except Exception:
    pass

# Mapping of counties/cities to region in Taiwan
REGION_MAP = {
    "基隆市": "北部", "臺北市": "北部", "新北市": "北部", "桃園市": "北部",
    "新竹市": "北部", "新竹縣": "北部", "宜蘭縣": "北部",
    "苗栗縣": "中部", "臺中市": "中部", "彰化縣": "中部", "南投縣": "中部", "雲林縣": "中部",
    "嘉義市": "南部", "嘉義縣": "南部", "臺南市": "南部", "高雄市": "南部", "屏東縣": "南部",
    "花蓮縣": "東部", "臺東縣": "東部",
    "澎湖縣": "離島", "金門縣": "離島", "連江縣": "離島"
}

# Approximate geographic centers for visual mapping
LOCATION_COORDS = {
    "基隆市": {"lat": 25.1276, "lon": 121.7392},
    "臺北市": {"lat": 25.0330, "lon": 121.5654},
    "新北市": {"lat": 24.9157, "lon": 121.6739},
    "桃園市": {"lat": 24.9936, "lon": 121.3010},
    "新竹市": {"lat": 24.8138, "lon": 120.9675},
    "新竹縣": {"lat": 24.8383, "lon": 121.0177},
    "苗栗縣": {"lat": 24.5602, "lon": 120.8214},
    "臺中市": {"lat": 24.1477, "lon": 120.6736},
    "彰化縣": {"lat": 24.0518, "lon": 120.5161},
    "南投縣": {"lat": 23.9609, "lon": 120.9719},
    "雲林縣": {"lat": 23.7092, "lon": 120.4313},
    "嘉義市": {"lat": 23.4800, "lon": 120.4491},
    "嘉義縣": {"lat": 23.4518, "lon": 120.2559},
    "臺南市": {"lat": 22.9997, "lon": 120.2270},
    "高雄市": {"lat": 22.6273, "lon": 120.3014},
    "屏東縣": {"lat": 22.5519, "lon": 120.5487},
    "宜蘭縣": {"lat": 24.7021, "lon": 121.7377},
    "花蓮縣": {"lat": 23.9872, "lon": 121.6016},
    "臺東縣": {"lat": 22.7583, "lon": 121.1444},
    "澎湖縣": {"lat": 23.5711, "lon": 119.5793},
    "金門縣": {"lat": 24.4493, "lon": 118.3766},
    "連江縣": {"lat": 26.1505, "lon": 119.9499}
}

CWA_36H_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"


def fetch_cwa_forecast(api_key: str = None) -> Tuple[List[Dict[str, Any]], bool, str]:
    """
    Fetch 36-hour weather forecasts from CWA API.
    Returns: (forecast_records, is_live_data, message)
    """
    # Try resolving API key from parameter or environment
    key = (api_key or os.environ.get("CWA_API_KEY", "")).strip()

    if not key or key == "your_api_key_here":
        # Fallback to realistic mock data so the app always displays nicely
        records = generate_mock_forecasts()
        return records, False, "使用內建模擬展示資料（未設定 CWA API Key）"

    params = {
        "Authorization": key,
        "format": "JSON"
    }

    try:
        try:
            response = requests.get(CWA_36H_API_URL, params=params, timeout=10)
        except requests.exceptions.SSLError:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(CWA_36H_API_URL, params=params, verify=False, timeout=10)

        response.raise_for_status()
        data = response.json()

        success_val = str(data.get("success", "")).lower()
        if success_val != "true":
            records = generate_mock_forecasts()
            return records, False, "API 回應失敗，切換為模擬資料"

        records = parse_cwa_json(data)
        return records, True, f"成功從氣象署 API 更新 {len(records)} 筆即時預報資料"

    except Exception as e:
        records = generate_mock_forecasts()
        return records, False, f"API 連線異常 ({str(e)})，已自動切換為備用模擬資料"


def parse_cwa_json(cwa_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse CWA F-C0032-001 JSON structure into flat record list."""
    records = []
    locations = cwa_json.get("records", {}).get("location", [])

    for loc in locations:
        loc_name = loc.get("locationName", "")
        region = REGION_MAP.get(loc_name, "其他")

        # Organize elements by time periods (usually 3 time slots)
        elements = {elem["elementName"]: elem.get("time", []) for elem in loc.get("weatherElement", [])}

        time_slots = elements.get("Wx", [])
        for i, slot in enumerate(time_slots):
            start_time = slot.get("startTime", "")
            end_time = slot.get("endTime", "")
            wx = slot.get("parameter", {}).get("parameterName", "晴")

            pop = 0
            if "PoP" in elements and len(elements["PoP"]) > i:
                pop_val = elements["PoP"][i].get("parameter", {}).get("parameterName", "0")
                pop = int(pop_val) if pop_val.isdigit() else 0

            min_t = 20
            if "MinT" in elements and len(elements["MinT"]) > i:
                min_val = elements["MinT"][i].get("parameter", {}).get("parameterName", "20")
                min_t = int(min_val) if min_val.isdigit() else 20

            max_t = 28
            if "MaxT" in elements and len(elements["MaxT"]) > i:
                max_val = elements["MaxT"][i].get("parameter", {}).get("parameterName", "28")
                max_t = int(max_val) if max_val.isdigit() else 28

            comfort = "舒適"
            if "CI" in elements and len(elements["CI"]) > i:
                comfort = elements["CI"][i].get("parameter", {}).get("parameterName", "舒適")

            records.append({
                "location_name": loc_name,
                "region": region,
                "start_time": start_time,
                "end_time": end_time,
                "weather_state": wx,
                "rain_prob": pop,
                "min_temp": min_t,
                "max_temp": max_t,
                "comfort": comfort
            })

    return records


def generate_mock_forecasts() -> List[Dict[str, Any]]:
    """Generate realistic 36-hour mock forecasts for all 22 Taiwan administrative divisions."""
    records = []
    now = datetime.now()
    
    # 3 typical forecast periods: Today morning/afternoon, Tonight, Tomorrow
    periods = [
        (now.strftime("%Y-%m-%d 12:00:00"), (now + timedelta(hours=12)).strftime("%Y-%m-%d 00:00:00")),
        ((now + timedelta(hours=12)).strftime("%Y-%m-%d 00:00:00"), (now + timedelta(hours=24)).strftime("%Y-%m-%d 12:00:00")),
        ((now + timedelta(hours=24)).strftime("%Y-%m-%d 12:00:00"), (now + timedelta(hours=36)).strftime("%Y-%m-%d 00:00:00")),
    ]

    city_presets = {
        "臺北市": ("多雲時晴", 20, 20, 27, "舒適至微熱"),
        "新北市": ("多雲短暫雨", 30, 19, 26, "舒適"),
        "基隆市": ("陰短暫雨", 40, 19, 24, "舒適至稍有涼意"),
        "桃園市": ("多雲", 20, 19, 26, "舒適"),
        "新竹市": ("晴時多雲", 10, 20, 27, "舒適"),
        "新竹縣": ("晴時多雲", 10, 19, 27, "舒適"),
        "苗栗縣": ("晴朗", 10, 19, 28, "舒適至微熱"),
        "臺中市": ("晴時多雲", 10, 21, 29, "舒適至微熱"),
        "彰化縣": ("晴朗", 10, 21, 28, "舒適至微熱"),
        "南投縣": ("多雲午後短暫陣雨", 30, 18, 27, "舒適"),
        "雲林縣": ("晴時多雲", 10, 21, 29, "舒適至微熱"),
        "嘉義市": ("晴時多雲", 10, 21, 30, "微熱"),
        "嘉義縣": ("晴時多雲", 10, 21, 29, "微熱"),
        "臺南市": ("晴朗", 10, 22, 30, "微熱至悶熱"),
        "高雄市": ("晴時多雲", 10, 23, 31, "悶熱"),
        "屏東縣": ("多雲短暫陣雨", 20, 23, 31, "悶熱"),
        "宜蘭縣": ("陰局部短暫雨", 50, 19, 25, "舒適至稍涼"),
        "花蓮縣": ("多雲短暫陣雨", 30, 21, 27, "舒適"),
        "臺東縣": ("多雲局部雨", 30, 22, 28, "舒適至微熱"),
        "澎湖縣": ("晴時多雲", 10, 22, 28, "舒適"),
        "金門縣": ("晴朗", 0, 18, 26, "舒適至稍涼"),
        "連江縣": ("陰天", 20, 16, 21, "稍有涼意")
    }

    for city, (wx, pop, mint, maxt, ci) in city_presets.items():
        region = REGION_MAP.get(city, "北部")
        for i, (st, et) in enumerate(periods):
            # slight variation per slot
            slot_wx = wx if i == 0 else ("晴時多雲" if "雨" not in wx else "多雲")
            records.append({
                "location_name": city,
                "region": region,
                "start_time": st,
                "end_time": et,
                "weather_state": slot_wx,
                "rain_prob": max(0, pop + (i * 5 - 5)),
                "min_temp": mint + (1 if i == 1 else 0),
                "max_temp": maxt - (2 if i == 1 else 0),
                "comfort": ci
            })

    return records
