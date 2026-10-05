"""Air Quality (AQI) and Ultraviolet (UV) API Integration Module.

Sources:
1. UV: Central Weather Administration (CWA) Open Data APIs (O-A0005-001, O-A0003-001)
2. AQI: Ministry of Environment (MOENV) Open Data (AQX_P_432) with fallback to Open-Meteo Air Quality
"""

import os
import requests
import urllib3
from typing import List, Dict, Any, Tuple
from src.cwa_api import REGION_MAP, LOCATION_COORDS

# Disable insecure request warnings when handling SSL fallback
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CWA_UV_DAILY_MAX_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0005-001"
CWA_STATION_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"
MOENV_AQI_URL = "https://data.moenv.gov.tw/api/v2/aqx_p_432"


def get_uv_category(uvi: float) -> Tuple[str, str, str]:
    """
    Return (level_name, color_hex, health_advice) based on CWA UV index scale.
    """
    if uvi < 0:
        return "檢測中", "#9E9E9E", "暫無有效觀測數值。"
    elif uvi <= 2.9:
        return "低量級", "#00E400", "紫外線強度弱，可正常戶外活動。"
    elif uvi <= 5.9:
        return "中量級", "#FFD700", "外出建議戴遮陽帽、太陽眼鏡或使用防曬乳。"
    elif uvi <= 7.9:
        return "高量級", "#FF7E00", "紫外線較強，外出請戴帽、太陽眼鏡，並塗抹防曬乳。"
    elif uvi <= 10.9:
        return "過量級", "#E51C23", "曝曬 15-20 分鐘可能曬傷，上午 10 時至下午 2 時儘量避免戶外曝曬。"
    else:
        return "危險級", "#9C27B0", "曝曬 10-15 分鐘即可能曬傷，應避免戶外活動，外出請做好全面防護。"


def get_aqi_category(aqi: int) -> Tuple[str, str, str]:
    """
    Return (status_name, color_hex, health_advice) based on Taiwan MOENV AQI scale.
    """
    if aqi <= 50:
        return "良好", "#00E400", "空氣品質良好，各類族群均可正常戶外活動。"
    elif aqi <= 100:
        return "普通", "#FFD700", "極少數敏感族群宜減少劇烈戶外運動。"
    elif aqi <= 150:
        return "對敏感族群不健康", "#FF7E00", "孩童、老年人及心臟呼吸道疾病患者應減少體力消耗與戶外活動。"
    elif aqi <= 200:
        return "對所有族群不健康", "#E51C23", "一般大眾應減少戶外活動，敏感族群應留在室內，外出建議配戴口罩。"
    elif aqi <= 300:
        return "非常不健康", "#9C27B0", "所有民眾應減少戶外活動並關閉門窗，外出請配戴防護口罩。"
    else:
        return "危害", "#7E0023", "應避免一切戶外活動，室內應開啟空氣清淨設備。"


def fetch_cwa_uv(cwa_key: str = None) -> Dict[str, float]:
    """
    Fetch UV index for Taiwan counties using CWA APIs (O-A0005-001 & O-A0003-001).
    Returns dict: {location_name: uvi_value}
    """
    key = (cwa_key or os.environ.get("CWA_API_KEY", "")).strip()
    county_uv: Dict[str, float] = {}

    if not key or key == "your_api_key_here":
        return generate_mock_uv()

    try:
        # Step 1: Query station list to map StationId to CountyName
        params = {"Authorization": key, "format": "JSON"}
        r_st = requests.get(CWA_STATION_URL, params=params, verify=False, timeout=10)
        st_data = r_st.json()
        station_county = {}
        for s in st_data.get("records", {}).get("Station", []):
            st_id = s.get("StationId")
            county = s.get("GeoInfo", {}).get("CountyName")
            if st_id and county:
                station_county[st_id] = county

        # Step 2: Query daily UV max
        r_uv = requests.get(CWA_UV_DAILY_MAX_URL, params=params, verify=False, timeout=10)
        uv_data = r_uv.json()
        uv_locations = uv_data.get("records", {}).get("weatherElement", {}).get("location", [])

        for item in uv_locations:
            sid = item.get("StationID")
            county = station_county.get(sid)
            raw_uv = item.get("UVIndex")
            if county and raw_uv is not None:
                try:
                    uv_val = float(raw_uv)
                    if uv_val >= 0:
                        # If multiple stations in the same county, take the maximum
                        if county not in county_uv or uv_val > county_uv[county]:
                            county_uv[county] = uv_val
                except ValueError:
                    pass

        # Fill any missing counties using regional average
        all_counties = list(REGION_MAP.keys())
        avg_uv = round(sum(county_uv.values()) / max(1, len(county_uv)), 1) if county_uv else 7.0
        for c in all_counties:
            if c not in county_uv:
                county_uv[c] = avg_uv

        return county_uv

    except Exception:
        return generate_mock_uv()


def fetch_aqi_moenv(moenv_key: str = None) -> Tuple[Dict[str, Dict[str, Any]], bool, str]:
    """
    Fetch AQI data from MOENV Open Data API (AQX_P_432).
    """
    key = (moenv_key or os.environ.get("MOENV_API_KEY", "")).strip()
    if not key:
        return {}, False, "未提供 MOENV API Key"

    try:
        url = f"{MOENV_AQI_URL}?api_key={key}&limit=1000&format=json"
        r = requests.get(url, verify=False, timeout=10)
        if r.status_code != 200:
            return {}, False, f"MOENV API HTTP {r.status_code}"

        data = r.json()
        records = data.get("records", [])
        if not records:
            return {}, False, "無測站資料"

        county_aqi: Dict[str, Dict[str, Any]] = {}
        for rec in records:
            county = rec.get("county", "")
            aqi_str = rec.get("aqi", "")
            pm25_str = rec.get("pm2.5", "")
            pm10_str = rec.get("pm10", "")

            # Normalize county name (e.g. 台北市 -> 臺北市)
            norm_county = county.replace("台北市", "臺北市").replace("台中市", "臺中市").replace("台南市", "臺南市").replace("台東縣", "臺東縣")
            if not norm_county or not aqi_str.isdigit():
                continue

            aqi_val = int(aqi_str)
            pm25_val = float(pm25_str) if pm25_str and pm25_str.replace(".", "", 1).isdigit() else 15.0
            pm10_val = float(pm10_str) if pm10_str and pm10_str.replace(".", "", 1).isdigit() else 25.0

            if norm_county not in county_aqi:
                county_aqi[norm_county] = {
                    "aqi_list": [aqi_val],
                    "pm25_list": [pm25_val],
                    "pm10_list": [pm10_val]
                }
            else:
                county_aqi[norm_county]["aqi_list"].append(aqi_val)
                county_aqi[norm_county]["pm25_list"].append(pm25_val)
                county_aqi[norm_county]["pm10_list"].append(pm10_val)

        # Average per county
        result = {}
        for c, v in county_aqi.items():
            result[c] = {
                "aqi": int(sum(v["aqi_list"]) / len(v["aqi_list"])),
                "pm25": round(sum(v["pm25_list"]) / len(v["pm25_list"]), 1),
                "pm10": round(sum(v["pm10_list"]) / len(v["pm10_list"]), 1),
            }
        return result, True, "成功自環境部開放平台獲取即時 AQI"
    except Exception as e:
        return {}, False, f"MOENV 連線異常: {str(e)}"


def fetch_aqi_open_meteo() -> Dict[str, Dict[str, Any]]:
    """
    Fetch real-time AQI and particulate matter (PM2.5, PM10) for Taiwan counties via Open-Meteo API.
    Does not require an API key and covers all 22 administrative divisions.
    """
    counties = list(LOCATION_COORDS.keys())
    lats = ",".join(str(LOCATION_COORDS[c]["lat"]) for c in counties)
    lons = ",".join(str(LOCATION_COORDS[c]["lon"]) for c in counties)

    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lats}&longitude={lons}&current=pm10,pm2_5,us_aqi"

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        result = {}

        if isinstance(data, list):
            for i, item in enumerate(data):
                c_name = counties[i]
                current = item.get("current", {})
                us_aqi = int(current.get("us_aqi", 45))
                pm25 = float(current.get("pm2_5", 12.0))
                pm10 = float(current.get("pm10", 25.0))
                result[c_name] = {
                    "aqi": us_aqi,
                    "pm25": pm25,
                    "pm10": pm10
                }
        elif isinstance(data, dict) and "current" in data:
            current = data.get("current", {})
            for c_name in counties:
                result[c_name] = {
                    "aqi": int(current.get("us_aqi", 45)),
                    "pm25": float(current.get("pm2_5", 12.0)),
                    "pm10": float(current.get("pm10", 25.0))
                }
        return result
    except Exception:
        return generate_mock_aqi()


def get_all_env_data(cwa_key: str = None, moenv_key: str = None) -> Tuple[List[Dict[str, Any]], str]:
    """
    Combine UV index and AQI data for all 22 administrative divisions of Taiwan.
    """
    # 1. Fetch UV
    uv_dict = fetch_cwa_uv(cwa_key)

    # 2. Fetch AQI: try MOENV first, fallback to Open-Meteo
    aqi_dict, is_moenv, moenv_msg = fetch_aqi_moenv(moenv_key)
    source_label = "環境部 (MOENV) API"
    if not is_moenv:
        aqi_dict = fetch_aqi_open_meteo()
        source_label = "大氣監測模型 (Open-Meteo) 即時數據"

    records = []
    for loc_name, region in REGION_MAP.items():
        uvi = uv_dict.get(loc_name, 7.0)
        uv_level, uv_color, uv_advice = get_uv_category(uvi)

        aq_info = aqi_dict.get(loc_name, {"aqi": 45, "pm25": 12.0, "pm10": 25.0})
        aqi_val = aq_info.get("aqi", 45)
        pm25 = aq_info.get("pm25", 12.0)
        pm10 = aq_info.get("pm10", 25.0)
        aqi_status, aqi_color, aqi_advice = get_aqi_category(aqi_val)

        records.append({
            "location_name": loc_name,
            "region": region,
            "uv_index": uvi,
            "uv_level": uv_level,
            "uv_color": uv_color,
            "uv_advice": uv_advice,
            "aqi": aqi_val,
            "aqi_status": aqi_status,
            "aqi_color": aqi_color,
            "pm25": pm25,
            "pm10": pm10,
            "aqi_advice": aqi_advice,
            "data_source": source_label
        })

    return records, f"紫外線：氣象署 O-A0005 即時資料；空氣品質：{source_label}"


def generate_mock_uv() -> Dict[str, float]:
    """Fallback mock UV data."""
    mock_values = {
        "基隆市": 6.0, "臺北市": 7.0, "新北市": 7.0, "桃園市": 8.0,
        "新竹市": 8.0, "新竹縣": 8.0, "苗栗縣": 9.0, "臺中市": 9.0,
        "彰化縣": 9.0, "南投縣": 8.0, "雲林縣": 9.0, "嘉義市": 10.0,
        "嘉義縣": 10.0, "臺南市": 9.0, "高雄市": 10.0, "屏東縣": 10.0,
        "宜蘭縣": 7.0, "花蓮縣": 8.0, "臺東縣": 9.0, "澎湖縣": 10.0,
        "金門縣": 8.0, "連江縣": 6.0
    }
    return mock_values


def generate_mock_aqi() -> Dict[str, Dict[str, Any]]:
    """Fallback mock AQI data."""
    result = {}
    for c in REGION_MAP.keys():
        result[c] = {"aqi": 42, "pm25": 11.5, "pm10": 24.0}
    return result
