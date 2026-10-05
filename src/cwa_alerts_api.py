"""CWA Weather Warning Alerts Module (中央氣象署即時氣象警特報).

Dataset: W-C0033-001 (氣象預警與災害特報)
Supports:
- 陸上強風特報
- 大雨、豪雨、大豪雨、超大豪雨特報
- 低溫特報
- 濃霧特報
- 高溫資訊
- 颱風警報
"""

import os
import requests
import urllib3
from typing import Dict, List, Tuple, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CWA_ALERTS_API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/W-C0033-001"


def _get_alert_meta(phenomena: str, significance: str) -> Tuple[str, str, str]:
    """Return (icon, color, advice) for a specific weather warning."""
    title = f"{phenomena}{significance}"
    if "強風" in phenomena:
        return (
            "💨",
            "#F59E0B",
            "沿海與空曠地區風力強勁，戶外活動請留意掉落物及吹落招牌，行車行經橋樑請防範側風。"
        )
    elif "豪雨" in phenomena:
        return (
            "⛈️",
            "#EF4444",
            "短延時強降雨警戒中，山區嚴防坍方落石與溪水暴漲，低窪地區請慎防積淹水，避免外出至危險水域。"
        )
    elif "雨" in phenomena:
        return (
            "🌧️",
            "#0284C7",
            "對流雲系發展旺盛，請攜帶雨具，出門留意行車安全與路面濕滑。"
        )
    elif "低溫" in phenomena:
        return (
            "❄️",
            "#6366F1",
            "強冷空氣籠罩，早晚氣溫極低，長輩與心血管疾病患者請加強保暖，室內使用瓦斯請保持通風。"
        )
    elif "濃霧" in phenomena or "霧" in phenomena:
        return (
            "🌫️",
            "#64748B",
            "部分地區能見度偏低（不足200公尺），行車請開啟霧燈並減速慢行，留意交通與航班異動。"
        )
    elif "高溫" in phenomena:
        return (
            "🔥",
            "#EA580C",
            "天氣炎熱高溫，外出請隨時補充水分預防熱傷害，正午時段儘量減少戶外劇烈活動。"
        )
    elif "颱風" in phenomena:
        return (
            "🌀",
            "#DC2626",
            "颱風警報發布中，嚴禁前往海邊觀浪或山區戲水，請加強固定門窗、堆沙包做好防颱措施。"
        )
    return (
        "⚠️",
        "#EAB308",
        f"氣象署發布{title}，請留意天候變化並做好相關防護準備。"
    )


def fetch_cwa_alerts(cwa_key: str = None, api_key: str = None) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, str]]], bool, str]:
    """
    Fetch active weather warnings from CWA W-C0033-001.

    Returns:
        alert_records: List of aggregated alerts with affected locations & metadata
        county_alerts_map: Dict mapping county name to its active alert list
        is_live: True if live from API, False otherwise
        message: Status message
    """
    effective_key = cwa_key if cwa_key is not None else api_key
    key = (effective_key or os.environ.get("CWA_API_KEY", "")).strip()

    if not key or key == "your_api_key_here":
        return _get_mock_alerts("未設定 API 授權碼，載入備援展示特報數據")

    try:
        params = {"Authorization": key}
        response = requests.get(CWA_ALERTS_API_URL, params=params, verify=False, timeout=12)
        response.encoding = "utf-8"

        if response.status_code != 200:
            return _get_mock_alerts(f"API 回應異常 (HTTP {response.status_code})")

        data = response.json()
        if not data.get("success"):
            return _get_mock_alerts("API 回傳非成功狀態")

        locations = data.get("records", {}).get("location", [])

        # Parse alerts grouped by alert title
        alerts_by_title: Dict[str, Dict[str, Any]] = {}
        county_alerts_map: Dict[str, List[Dict[str, str]]] = {}

        for loc in locations:
            loc_name = loc.get("locationName", "").strip()
            hazards = loc.get("hazardConditions", {}).get("hazards", [])

            for h in hazards:
                info = h.get("info", {})
                phenomena = info.get("phenomena", "").strip()
                significance = info.get("significance", "").strip()
                title = f"{phenomena}{significance}"
                if not title:
                    continue

                valid_time = h.get("validTime", {})
                start_t = valid_time.get("startTime", "")
                end_t = valid_time.get("endTime", "")

                icon, color, advice = _get_alert_meta(phenomena, significance)

                if title not in alerts_by_title:
                    alerts_by_title[title] = {
                        "alert_title": title,
                        "phenomena": phenomena,
                        "significance": significance,
                        "start_time": start_t,
                        "end_time": end_t,
                        "icon": icon,
                        "color": color,
                        "advice": advice,
                        "locations": []
                    }

                if loc_name and loc_name not in alerts_by_title[title]["locations"]:
                    alerts_by_title[title]["locations"].append(loc_name)

                # Add to county map
                if loc_name:
                    if loc_name not in county_alerts_map:
                        county_alerts_map[loc_name] = []
                    # Check if already added
                    if not any(a["title"] == title for a in county_alerts_map[loc_name]):
                        county_alerts_map[loc_name].append({
                            "title": title,
                            "phenomena": phenomena,
                            "icon": icon,
                            "color": color,
                            "start_time": start_t,
                            "end_time": end_t
                        })

        alert_records = []
        for title, details in alerts_by_title.items():
            alert_records.append({
                "alert_title": details["alert_title"],
                "phenomena": details["phenomena"],
                "significance": details["significance"],
                "start_time": details["start_time"],
                "end_time": details["end_time"],
                "icon": details["icon"],
                "color": details["color"],
                "advice": details["advice"],
                "location_count": len(details["locations"]),
                "affected_locations": ", ".join(details["locations"])
            })

        count = len(alert_records)
        msg = f"即時同步成功（全台發布 {count} 類警特報）" if count > 0 else "即時同步成功（全台目前無顯著警特報）"
        return alert_records, county_alerts_map, True, msg

    except Exception as e:
        return _get_mock_alerts(f"連線失敗: {str(e)[:50]}")


def _get_mock_alerts(reason: str) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, str]]], bool, str]:
    """Provide realistic backup weather warning data when API is offline."""
    mock_records = [
        {
            "alert_title": "陸上強風特報",
            "phenomena": "陸上強風",
            "significance": "特報",
            "start_time": "2026-10-04 23:00:00",
            "end_time": "2026-10-05 23:00:00",
            "icon": "💨",
            "color": "#F59E0B",
            "advice": "東北季風增強，沿海空曠地區風力偏強，戶外活動請留意高空掉落物與側風安全。",
            "location_count": 14,
            "affected_locations": "基隆市, 新北市, 桃園市, 新竹縣, 新竹市, 苗栗縣, 臺中市, 彰化縣, 雲林縣, 嘉義縣, 臺南市, 屏東縣, 澎湖縣, 金門縣"
        }
    ]
    county_alerts_map = {
        "基隆市": [{"title": "陸上強風特報", "phenomena": "陸上強風", "icon": "💨", "color": "#F59E0B", "start_time": "2026-10-04 23:00:00", "end_time": "2026-10-05 23:00:00"}],
        "新北市": [{"title": "陸上強風特報", "phenomena": "陸上強風", "icon": "💨", "color": "#F59E0B", "start_time": "2026-10-04 23:00:00", "end_time": "2026-10-05 23:00:00"}],
        "苗栗縣": [{"title": "陸上強風特報", "phenomena": "陸上強風", "icon": "💨", "color": "#F59E0B", "start_time": "2026-10-04 23:00:00", "end_time": "2026-10-05 23:00:00"}],
        "臺中市": [{"title": "陸上強風特報", "phenomena": "陸上強風", "icon": "💨", "color": "#F59E0B", "start_time": "2026-10-04 23:00:00", "end_time": "2026-10-05 23:00:00"}],
        "澎湖縣": [{"title": "陸上強風特報", "phenomena": "陸上強風", "icon": "💨", "color": "#F59E0B", "start_time": "2026-10-04 23:00:00", "end_time": "2026-10-05 23:00:00"}]
    }
    return mock_records, county_alerts_map, False, f"使用備援警特報數據（{reason}）"
