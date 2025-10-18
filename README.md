# 台股 ETF 資訊整合平台 (v7.0)

[![Language](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一個自動化抓取、整合並視覺化呈現台灣證券市場 ETF 持股資訊的完整解決方案。

<!-- Placeholder for a screenshot or GIF of the dashboard -->
<!-- ![Dashboard Screenshot](...) -->

---

## 關於此專案

台灣的 ETF 相關資訊分散在各大投信公司的網站以及政府的公開資料平台中，格式各異，查詢不便。本專案旨在解決此問題，透過建立一個自動化的資料整合流程，並搭配一個現代化的互動式儀表板，為使用者提供一個一站式的 ETF 持股查詢與分析平台。

## ✨ 專案特色

- **模組化爬蟲架構**: 可輕易為新的投信公司擴充爬蟲，且互不影響。
- **智慧抓取模式**: 系統會自動判斷目標網站類型，選擇最高效的抓取方式 (直接請求 `requests` 或模擬瀏覽器 `selenium`)。
- **多來源資料整合**: 整合了各投信官網的「即時持股資料」與證交所的「基金基本資料」，提供更全面的資訊維度。
- **前後端分離設計**: 
  - **RESTful API**: 後端使用 Flask 提供清晰的 API 接口，方便未來與其他應用 (如手機 App) 介接。
  - **React 前端**: 前端使用 React 打造，提供現代化、響應式的互動體驗。
- **互動式數據視覺化**: 使用 `Recharts` 圖表庫，將複雜的持股數據以直觀、美觀的圖表呈現。
- **結構化日誌與報告**: 每次爬蟲任務結束後，都會產生詳細的執行報告，並儲存於 `logs/` 目錄下，便於追蹤與維護。

## 🛠️ 技術棧

| 層級      | 技術/函式庫                                       |
| :-------- | :------------------------------------------------ |
| **後端**  | Python, Flask, Selenium, Requests, BeautifulSoup4 |
| **前端**  | React, React-Bootstrap, React-Router, Recharts    |
| **開發工具**| pip, npm, webdriver-manager                       |

## 🏗️ 架構與資料流

本專案的資料流清晰地劃分為「生產」與「消費」兩個階段。

### 資料生產 (執行 `scripts/scraper.py`)

當爬蟲腳本執行時，會產生以下三種核心的 JSON 檔案並存放於 `data/` 目錄：

1.  **`fund_basic_info.json`**: 
    - **內容**: 所有在台灣上市基金的「基本資料」。
    - **來源**: 從**證交所 Open Data** (`mopsfin.twse.com.tw`) 下載的 CSV 轉換而來。
    - **用途**: 作為一個基礎的資料庫，供 API 查詢特定 ETF 的成立日期、追蹤指數等靜態資訊。

2.  **`<ETF_CODE>.json`** (例如 `0050.json`):
    - **內容**: 單一 ETF 的詳細「持股資訊」。
    - **來源**: 由對應的爬蟲模組（如 `YuantaScraper`）從該投信官網抓取。
    - **用途**: 提供該 ETF 最核心的持股分佈資料。

3.  **`etf_list.json`**:
    - **內容**: 一份所有**成功抓取**的 ETF 的清單，包含代碼、名稱、發行商等。
    - **來源**: 在完整抓取任務結束後，由主程式匯總所有成功結果而產生。
    - **用途**: 供前端儀表板主頁快速獲取已同步的 ETF 列表。

### 資料消費 (啟動 API 與前端)

1.  **後端 API (`app/main.py`)**: 啟動後，它會監聽請求，並根據請求內容讀取 `data/` 目錄下的 JSON 檔案，將資料回傳。
2.  **前端應用 (`frontend/`)**: 
    - **儀表板頁面**: 呼叫 `/cached/etfs` API，獲取 `etf_list.json` 的內容，並將 ETF 列表呈現出來。
    - **詳情頁面**: 當使用者點擊某支 ETF (如 `0050`) 時，頁面會**同時發送兩個 API 請求**：
        1.  呼叫 `/cached/holdings/0050` 獲取其**持股資料**。
        2.  呼叫 `/cached/fund_info/0050` 獲取其**基本資料**。
    - 前端在獲取到這兩份資料後，會將其**智慧地結合**，呈現出包含完整資訊的最終頁面。

## 🚀 快速上手指南

### 1. 環境準備

請確保您的開發環境中已安裝以下軟體：
- Python (3.9+)
- Node.js (16.x+)
- npm
- Google Chrome 瀏覽器

### 2. 專案安裝

```bash
# 1. 複製專案
# git clone <repository_url>
# cd twETFHoldings

# 2. 安裝 Python 後端依賴
pip install -r requirements.txt

# 3. 安裝 Node.js 前端依賴
cd frontend
npm install
cd ..
```

### 3. 執行應用程式

**步驟 3.1: 執行一次完整資料抓取**

在首次啟動前，必須先執行一次完整的爬蟲任務，以產生必要的資料檔案。

```bash
python scripts/scraper.py
```

**步驟 3.2: 啟動本地服務**

請打開**兩個**獨立的終端機視窗，並在專案**根目錄**下分別執行：

- **在第一個終端機 (用於後端):**
  ```bash
  flask --app app/main run
  ```
  *您將會看到服務運行在 `http://127.0.0.1:5000` 的訊息。*

- **在第二個終端機 (用於前端):**
  ```bash
  cd frontend
  npm start
  ```
  *此指令會自動在您的瀏覽器中打開 `http://localhost:3000`。*

**步驟 3.3: 查看結果**

- 瀏覽 `http://localhost:3000` 即可看到視覺化儀表板。
- 瀏覽 `http://127.0.0.1:5000/apidocs/` 可查看後端 API 的詳細文件。

## 🔧 專案維護與擴充

### 爬蟲失效維護

投信公司的網站隨時可能改版，若您發現某個爬蟲失效（通常會在執行報告中看到 `[FAILURE]` 標記），請參考 `SCRAPING_STRATEGIES.md` 文件。該文件詳細記錄了每個爬蟲的抓取邏輯與目標 URL，能幫助您快速定位問題並進行修正。

### 如何擴充新的爬蟲模組

1.  **在 `config.json` 中新增目標**，並指定一個新的 `firm` ID (例如 `"cathay"`)。
2.  **在 `scripts/scraper.py` 中建立新的爬蟲類別** (例如 `CathayScraper`)，讓它繼承 `BaseScraper`。
3.  **設定資源需求**: 在新類別中設定 `needs_browser = True` (動態網站) 或 `False` (靜態網站)。
4.  **實作 `scrape` 方法**: 在方法中實作抓取邏輯，最後返回一個包含 `"name"` 和 `"holdings"` 的字典。
5.  **註冊爬蟲**: 在 `SCRAPERS` 字典中，將新的 `firm` ID 與您新建的類別關聯起來。
6.  **單獨測試**: `python scripts/scraper.py <your_new_etf_code>`