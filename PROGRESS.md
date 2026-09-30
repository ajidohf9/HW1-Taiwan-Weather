# 📋 HW1 台灣天氣預報系統 - 專案進度與接續開發交接紀錄

> **專案作者**：ajidohf9  
> **專案倉庫**：https://github.com/ajidohf9/HW1-Taiwan-Weather  
> **最新更新時間**：2026-09-30  
> **技術架構**：Python 3.10+ / Streamlit / SQLite3 / CWA Open Data API / Plotly

---

## 📌 目前作業進度總結
依據「打造你的 AI Coding Agent：Antigravity × Gemini × GitHub」作業規範，目前進度如下：

- [x] **步驟 1**：下載並安裝 Antigravity IDE。
- [x] **步驟 2**：啟動並使用內建 Gemini 協同開發。
- [x] **步驟 3**：建立專案結構（`app.py`, `src/`, `data/`, `requirements.txt`, `README.md`）。
- [x] **步驟 4**：建立 GitHub 遠端倉庫（`ajidohf9/HW1-Taiwan-Weather`）。
- [x] **步驟 5**：取得 Git Repository URL。
- [x] **步驟 6**：完成本地 Git 與遠端 GitHub 連結。
- [x] **步驟 7**：進行 Vibe Coding 架構規劃。
- [x] **步驟 8**：【已完成】開發 → 測試 → 儲存：
  - 成功串接中央氣象署 API（36 小時預報 `F-C0032-001`）。
  - 已修復 Windows Python SSL 憑證驗證連線問題。
  - 已建立本地 SQLite 資料庫與持久化儲存機制。
  - 已完成程式碼 Commit 並正式 Push 到 GitHub。
- [ ] **步驟 9**：【當前階段】持續迭代與優化功能（詳見下方規劃）。
- [ ] **步驟 10**：專案完工展示與成果回報。

---

## 🛠️ 已解決的重要相容性與技術細節
在新電腦環境接續開發時，請注意以下已處理的重點：
1. **氣象署 SSL 連線容錯**：
   - 位於 `src/cwa_api.py`，已加入 Windows 環境憑證缺少 SKI 時的自動安全備援連線機制。
2. **Plotly 7 地圖相容**：
   - 位於 `src/visualizer.py`，新版 Plotly 已將 `scatter_mapbox` 升級為 `scatter_map`，程式碼已內建自動判斷相容機制。
3. **API 授權碼保護**：
   - 授權碼不納入 Git 追蹤，置於本地 `.env` 檔案中（變數名：`CWA_API_KEY`）。
4. **模組動態重載**：
   - `app.py` 內建 `importlib.reload`，避免 Streamlit 記憶體模組快取不同步。

---

## 🎯 步驟 9：建議接續優化方向（Next Steps）
換到新電腦後，AI 與使用者可直接從以下方向挑選 1~2 項進行進階優化：
1. **氣象警特報整合**：串接 CWA 大雨特報、低溫特報或強風特報 API，於首頁頂端顯示即時跑馬燈或警告 Banner。
2. **紫外線與空氣品質 (AQI)**：整合環境部開放資料，讓使用者同時掌握天氣與空氣品質指標。
3. **更美觀的深色主題或自訂 UI**：利用 Streamlit 自訂 CSS，加入毛玻璃質感卡片與動態氣象圖示。
4. **一週天氣預報 (7-Day Forecast)**：擴充支援氣象署 7 天未來天氣 API。

---

## 💡 新電腦接手指令
若由其他 AI 或在新電腦上讀取此專案，請確保：
1. 建立 `.env` 並寫入 `CWA_API_KEY`。
2. 執行 `pip install -r requirements.txt`。
3. 執行 `streamlit run app.py` 啟動服務。
