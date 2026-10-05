from http.server import BaseHTTPRequestHandler
import json
import datetime


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function providing API status for Taiwan Weather App."""

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

        response_payload = {
            "status": "online",
            "service": "Taiwan Weather Forecast System (台灣天氣預報系統)",
            "course": "打造你的 AI Coding Agent (HW1)",
            "author": "ajidohf9",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "deployments": {
                "vercel_portal": "https://hw1-taiwan-weather.vercel.app",
                "streamlit_cloud": "https://hw1-taiwan-weather.streamlit.app",
                "github_repo": "https://github.com/ajidohf9/HW1-Taiwan-Weather"
            },
            "features": [
                "36H Forecast (CWA F-C0032-001)",
                "7-Day Weather Trend (CWA F-D0047-091)",
                "Disaster & Hazard Alerts (CWA W-C0033-001)",
                "AQI & UV Index (MOENV / Open-Meteo)",
                "Interactive Maps & Plotly Analytics",
                "SQLite Local Persistence & Historical Tracking"
            ]
        }

        self.wfile.write(json.dumps(response_payload, ensure_ascii=False, indent=2).encode("utf-8"))
