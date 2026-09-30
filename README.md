# 🌤️ Taiwan Weather Forecast Web App (台灣天氣預報系統)

> **打造你的 AI Coding Agent** — Antigravity × Gemini × GitHub 專案實作作業。

---

## 📌 專案簡介
本專案為使用 **Python** 與 **Streamlit** 開發的台灣即時天氣預報 Web 應用程式。串接**中央氣象署（CWA）開放資料 API** 與本地 **SQLite 資料庫**，提供動態互動式全台地圖、分區概況比較、單一縣市 36 小時趨勢圖，以及 SQLite 資料庫瀏覽與 CSV 匯出功能。

---

## 🚀 核心功能特色 (Features)
1. **中央氣象署 API 即時串接**：
   - 支援自動載入環境變數 `CWA_API_KEY` 或透過側邊欄動態輸入。
   - 即時解析全台 22 縣市三時段預報數據（氣候、降雨機率、高低溫、舒適度）。
2. **SQLite 本地持久化儲存**：
   - 包含自動建立資料表與 `ON CONFLICT` 更新機制，保障離線或重複同步時資料一致性。
3. **互動式全台氣候地圖**：
   - 採用 Plotly Mapbox 呈現全台地理分布與溫度熱力散佈點。
4. **分區概況與卡片檢視**：
   - 支援北部、中部、南部、東部、離島快速切換與天氣卡片。
5. **單一縣市 36 小時趨勢分析**：
   - 雙 Y 軸互動折線與柱狀圖（氣溫走勢 + 降雨機率）。
6. **資料庫檢視與 CSV 匯出**：
   - 內建資料表瀏覽器，支援一鍵下載即時氣象 CSV。

---

## 🛠️ 技術架構 (Tech Stack)
- **程式語言**：Python 3.10+
- **Web 框架**：Streamlit
- **資料儲存**：SQLite3
- **資料來源**：中央氣象署開放資料平台 (CWA Open Data API - `F-C0032-001`)
- **圖表視覺化**：Plotly (Scatter Mapbox, Bar, Line Charts)
- **環境設定**：python-dotenv

---

## 📁 專案檔案結構
```text
HW1-Taiwan-Weather/
│
├── .env.example          # 環境變數範例檔
├── .env                  # 個人 API Key（已列入 .gitignore 保護）
├── .gitignore            # Git 忽略清單
├── requirements.txt      # Python 依賴清單
├── README.md             # 專案說明文件
├── app.py                # Streamlit 主應用程式
│
├── data/
│   └── weather.db        # SQLite 資料庫檔案
│
└── src/
    ├── __init__.py
    ├── cwa_api.py        # 中央氣象署 API 串接與資料解析
    ├── db.py             # SQLite 資料庫連線與 CRUD 操作
    └── visualizer.py     # Plotly 互動視覺化與地圖模組
```

---

## ⚡ 快速開始 (Quick Start)

### 1. 安裝相依套件
```bash
pip install -r requirements.txt
```

### 2. 設定 API 授權碼
複製 `.env.example` 為 `.env` 並填入中央氣象署 API 授權碼：
```env
CWA_API_KEY=你的CWA授權碼
```
*(可至 [中央氣象署開放資料平臺](https://opendata.cwa.gov.tw/) 免費申請)*

### 3. 啟動 Streamlit 應用程式
```bash
streamlit run app.py
```
啟動後瀏覽器打開 `http://localhost:8501` 即可體驗完整功能。

