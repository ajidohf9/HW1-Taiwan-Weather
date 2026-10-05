from http.server import BaseHTTPRequestHandler
import json
import datetime
import os


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function providing both Web Portal and API status."""

    def do_GET(self):
        req_path = self.path.split("?")[0].rstrip("/")

        # API Status Endpoint
        if any(req_path.endswith(p) for p in ("/api/status", "/api/status.py", "/status", "/api")) or "status" in req_path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()

            payload = {
                "status": "online",
                "service": "Taiwan Weather Forecast System (台灣天氣預報系統)",
                "course": "打造你的 AI Coding Agent (HW1)",
                "author": "ajidohf9",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "deployments": {
                    "vercel_portal": "https://hw-1-taiwan-weather-dun.vercel.app",
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
            self.wfile.write(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        # Serve Web Portal (HTML) for root and any other routes
        candidate_paths = [
            os.path.join(os.path.dirname(__file__), "index.html"),
            os.path.join(os.path.dirname(__file__), "..", "index.html"),
            os.path.join(os.getcwd(), "index.html"),
            os.path.join(os.getcwd(), "api", "index.html")
        ]

        html_content = None
        for p in candidate_paths:
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    break
                except Exception:
                    continue

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()

        if html_content:
            self.wfile.write(html_content.encode("utf-8"))
        else:
            fallback = "<html><body><h1>🌤️ 台灣天氣預報系統</h1><p>Vercel Portal is running.</p></body></html>"
            self.wfile.write(fallback.encode("utf-8"))
