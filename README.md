# 🌤️ Taiwan Weather Forecast Web App (台灣即時天氣與環境觀測系統)

> **打造你的 AI Coding Agent** — Antigravity × Gemini × GitHub 專案實作作業 (HW1)。  
> 本專案採**雙架構部署模式**：提供 **Vercel Web Portal** 前端傳送門與 **Streamlit Community Cloud** 雲端原生運算雙連結。

---

## 🌐 線上展示與快速連結 (Live Demos)

- ⚡ **Vercel 官方展示傳送門 (Live Web Portal)**：[https://hw1-taiwan-weather.vercel.app](https://hw1-taiwan-weather.vercel.app)
- 🚀 **Streamlit Cloud 原生全功能系統 (Live Streamlit App)**：[https://hw1-taiwan-weather.streamlit.app](https://hw1-taiwan-weather.streamlit.app)
- 🐱 **GitHub 專案原始碼倉庫**：[https://github.com/ajidohf9/HW1-Taiwan-Weather](https://github.com/ajidohf9/HW1-Taiwan-Weather)
- 📊 **Vercel Serverless Function 監控端點**：`/api/status`

---

## 📌 專案簡介 (Overview)

本專案為使用 **Python**、**Streamlit** 與 **Vercel Serverless** 打造的現代化台灣即時天氣觀測與防災預警系統。  
全面串接**中央氣象署（CWA）開放資料 API**、**環境部空氣品質監測** 與本地 **SQLite 智慧快取資料庫**，具備毛玻璃（Glassmorphism）極光質感、雙主題即時切換、4 大地圖圖層、7 大多維度排序、即時災害警特報連動，以及時間序列歷史軌跡追蹤。

---

## 🚀 核心功能特色 (Core Features)

1. **🗺️ 台灣互動觀測地圖 (4 大全方位圖層)**：
   - 🌤️ 即時氣溫與天氣現象（Plasma 熱感色階）
   - 🌧️ 降雨機率分佈圖層（PoP 降雨風險漸層）
   - ☀️ 紫外線指數 (UVI) 分布（YlOrRd 警告色階）
   - 🌿 空氣品質指標 (AQI) 分布（綠黃橘紅紫標準空品色階）
   - 支援「地名與數值」、「僅數值」與「圓點標記」三種地圖標註模式，深淺主題高對比適配。

2. **🏙️ 分區天氣與 22 縣市多維度排序卡片**：
   - 支援「全部 / 北部 / 中部 / 南部 / 東部 / 離島」分區快速切換。
   - 7 大維度排序：最高溫、最低溫、降雨機率、AQI 最佳/最差、紫外線最強。
   - 前三名榮譽金銀銅牌（🥇🥈🥉）徽章與關鍵字即時模糊搜尋。
   - 視覺化降雨機率進度條與三段式雨具決策建議。

3. **🚨 即時氣象警特報與防災預警專區**：
   - 串接氣象署即時災害特報 API（`W-C0033-001`），涵蓋強風、豪雨、低溫、濃霧、高溫資訊與颱風警報。
   - 首頁頂端動態呼吸燈警報 Banner，支援展開受影響縣市清單與防災指引。
   - 全台縣市卡片右上角動態警報 Badge 連動，防災重點區域一目瞭然。

4. **🔍 單一縣市 36 小時深入預報**：
   - 晝夜時段氣象指標卡（天氣、降雨機率、高低溫、舒適度、紫外線）。
   - 雙 Y 軸互動 Plotly 曲線圖（氣溫折線 + 降雨機率長條圖）。
   - 專屬一鍵下載該縣市 36H 預報 CSV。

5. **📅 未來一週 (7-Day) 天氣預報**：
   - 串接一週全台鄉鎮預報 API（`F-D0047-091`），呈現 14 時段早晚溫差走勢。
   - 體感溫度帶、最高/最低溫填充區間與濕度氣象指標。
   - 專屬一鍵下載 7 天預報資料 CSV。

6. **🌿 紫外線與環境部 AQI 專區**：
   - 全台 22 縣市空氣品質 (AQI) 與紫外線 (UVI) 排名比較長條圖。
   - 單一縣市雙指針儀表盤（Gauge Charts），即時對照 PM2.5 / PM10 數值。
   - 完整台灣官方防護分級對照表與外出健康指引。

7. **📈 SQLite 歷史軌跡追蹤圖表**：
   - 本地 `weather_history` 資料表與複合索引，自動保存歷次同步觀測紀錄。
   - 5 大單一縣市歷史趨勢模式：綜合指標、氣溫區間帶、降雨變化、AQI歷程、UVI晝夜軌跡。
   - 自由多選 2~5 個縣市進行跨區域趨勢走勢對比。

8. **⚡ 智慧快取指示器與系統效能優化**：
   - 建立 `system_cache_meta` 快取中繼架構，首頁頂端 4 段式動態新鮮度呼吸燈。
   - 側邊欄支援動態滑動調整 TTL（5 / 15 / 30 / 60 分鐘）。
   - 本地 SQLite 快取命中載入加速 98% 以上（~14ms 極速響應）。

9. **🗄️ SQLite 資料庫管理與 100% 完整 CSV 匯出**：
   - 內建 6 大資料表即時瀏覽器。
   - 全功能分頁支援 UTF-8 (BOM) 一鍵匯出 CSV，完全相容 Excel 與資料分析軟體。

---

## 🛠️ 技術架構 (Tech Stack)

| 領域 | 技術與套件 |
| :--- | :--- |
| **前端入口 (Portal)** | HTML5, Vanilla CSS (Glassmorphism), Vanilla JS |
| **無伺服器架構** | Vercel Serverless Functions (Python Runtime, `vercel.json`) |
| **核心 Web 應用** | Python 3.10+, Streamlit |
| **資料庫儲存** | SQLite3 (本地輕量化持久關聯式資料庫) |
| **資料來源 API** | 中央氣象署開放資料平台 (CWA Open Data API) / 環境部空氣品質監測 |
| **互動資料視覺化** | Plotly (Scatter Mapbox, Bar, Line, Gauge, Subplots) |
| **雲端主機託管** | Vercel (Web Portal) + Streamlit Community Cloud (Python Backend) |

---

## 📁 專案檔案結構 (Project Structure)

```text
HW1-Taiwan-Weather/
│
├── vercel.json                 # Vercel 部署設定檔
├── index.html                  # Vercel Web Portal 傳送門展示頁
│
├── api/
│   └── status.py               # Vercel Python Serverless 狀態監控端點
│
├── app.py                      # Streamlit 7 大分頁主應用程式
├── requirements.txt            # Python 相依套件清單
├── README.md                   # 專案說明與部署指南
├── PROGRESS.md                 # 開發歷程與功能稽核日誌
├── .env.example                # 環境變數範例檔
├── .env                        # 個人 API 授權碼（已加入 .gitignore 保護）
│
├── data/
│   └── weather.db              # SQLite 本地資料庫
│
├── src/
│   ├── cwa_api.py              # CWA 36H 預報 API 模組
│   ├── forecast_7d_api.py      # CWA 一週 7-Day 預報 API 模組
│   ├── cwa_alerts_api.py       # CWA 即時災害警特報 API 模組
│   ├── aqi_uv_api.py           # 環境部 AQI 與紫外線 API 模組
│   ├── db.py                   # SQLite 資料庫連線、快取與 CRUD
│   └── visualizer.py           # Plotly 互動圖表與地圖模組 (深/淺雙主題)
│
└── tests/
    └── test_all_features.py    # 全功能自動化回歸測試套件
```

---

## 🚀 部署指南 (Deployment Guide)

### 做法一：部署到 Streamlit Community Cloud (Python 後端)
1. 確保最新程式碼已 Push 到 GitHub（`ajidohf9/HW1-Taiwan-Weather`）。
2. 前往 [Streamlit Community Cloud](https://share.streamlit.io/) 並使用 GitHub 帳號登入。
3. 點擊 **"Create app"**，設定如下：
   - **Repository**: `ajidohf9/HW1-Taiwan-Weather`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. 展開下方 **"Advanced settings..."**，於 **Secrets** 填寫：
   ```toml
   CWA_API_KEY = "你的中央氣象署授權碼"
   ```
5. 點擊 **"Deploy!"**，約 1 分鐘後即可取得專屬公開網址（如：`https://hw1-taiwan-weather.streamlit.app`）。

---

### 做法二：部署到 Vercel (Web Portal 傳送門)
1. 前往 [Vercel 官網](https://vercel.com/) 並使用 GitHub 帳號登入。
2. 點擊 **"Add New... -> Project"**。
3. 選擇並 Import 您的 GitHub 倉庫 `ajidohf9/HW1-Taiwan-Weather`。
4. Framework Preset 保持預設（**Other**），直接點擊 **"Deploy"**。
5. 部署完成後，即可獲得官方網址 `https://hw1-taiwan-weather.vercel.app`。
6. 進入網址即可看到極光毛玻璃 Portal 入口，並直接在線上互動全功能氣象儀表板！

---

## ⚡ 本地開發與執行 (Local Development)

### 1. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 2. 設定氣象署 API 金鑰
複製 `.env.example` 為 `.env` 並填入授權碼：
```env
CWA_API_KEY=你的中央氣象署授權碼
```
*(可至 [中央氣象署開放資料平臺](https://opendata.cwa.gov.tw/) 免費取得授權碼)*

### 3. 本地啟動 Streamlit
```bash
streamlit run app.py
```
啟動後瀏覽器打開 `http://localhost:8501` 即可體驗完整功能。

### 4. 執行全自動功能測試
```bash
python tests/test_all_features.py
```
全部 7 大資料表、9 種圖表與極端值防禦將自動運行驗證。
