# 台股 ETF 資訊專案 (v7.0)

這是一個用於抓取、儲存並透過本地 API 提供台灣 ETF 持股資訊的專案。專案採用高度模組化、可擴充的設計，讓開發者可以輕易地為新的證券投信公司新增爬蟲模組，並整合了一個 React 前端應用程式，用於將數據視覺化呈現。

## 設計理念

本專案的架構基於以下幾個核心設計理念：

- **模組化 (Modularity)**: 每家投信公司的爬蟲邏輯都被封裝在獨立的類別 (`class`) 中，與其他爬蟲完全解耦。
- **可擴充性 (Extensibility)**: `scripts/scraper.py` 中的 `SCRAPERS` 字典扮演著一個簡單的「插件註冊中心」。只需將新的爬蟲類別加入此字典，即可讓主程式辨識並執行。
- **職責分離 (Separation of Concerns)**: 專案被明確切分為三個獨立部分：
    1.  **爬蟲 (`scripts`)**: 唯一的職責是抓取原始資料，並返回一個標準化的 Python 物件。
    2.  **後端 API (`app`)**: 負責讀取爬蟲產生的 JSON 檔案，並透過 API 將資料提供給前端。
    3.  **前端應用 (`frontend`)**: 負責呈現 UI 介面與數據視覺化。
- **資源效率 (Resource Efficiency)**: 透過 `needs_browser` 屬性，爬蟲執行緒可以智慧地判斷是否需要啟動耗費資源的 Selenium 瀏覽器。
- **資料一致性 (Data Consistency)**: 所有爬蟲模組都返回固定結構的資料，由主執行緒統一處理，確保最終產出的 JSON 檔案格式一致。

## 專案狀態

- **v7.0**
- **支援的投信公司**:
    - ✅ **元大投信 (Yuanta)** - `firm: "yuanta"` (使用 Selenium)
    - ✅ **富邦投信 (Fubon)** - `firm: "fubon"` (使用 Requests)
    - ⏳ **國泰投信 (Cathay)** - `firm: "cathay"` (待開發)

## 資料來源

本專案的資料來自以下幾個公開來源：

1.  **基金基本資料**: 
    - **來源**: 台灣證券交易所 - 公開資訊觀測站
    - **URL**: `https://mopsfin.twse.com.tw/opendata/t187ap47_L.csv`
2.  **元大投信持股資料**:
    - **來源**: 元大投信官網
    - **URL**: `https://www.yuantaetfs.com/product/detail/{etf_code}/ratio`
3.  **富邦投信持股資料**:
    - **來源**: 富邦投信官網
    - **URL**: `https://websys.fsit.com.tw/FubonETF/Fund/Assets.aspx?stkId={etf_code}`

## 應用程式啟動與使用指南

本專案包含「後端 (爬蟲與 API)」和「前端 (視覺化網站)」兩部分，需要分別啟動。

### 1. 環境設定

確保您已安裝 Python 3, Node.js, npm, 以及 Google Chrome 瀏覽器。

```bash
# 1. 安裝 Python 後端依賴
pip install -r requirements.txt

# 2. 安裝 Node.js 前端依賴
cd frontend
npm install
cd ..
```

### 2. 執行資料抓取 (爬蟲)

在專案根目錄下，執行爬蟲腳本以獲取最新的 ETF 資料。腳本會自動下載 ETF 持股資料與基金基本資料，並存放在 `data/` 目錄下。

```bash
# 抓取 config.json 中所有 "enabled": true 的目標
python scripts/scraper.py
```

### 3. 啟動本地服務 (API 與網站)

請打開**兩個**獨立的終端機視窗，並在專案根目錄下分別執行以下指令：

**終端機 1: 啟動後端 API 伺服器**
```bash
flask --app app/main run
```
- 此服務將運行在 `http://127.0.0.1:5000`，負責提供數據服務。
- 訪問 `http://127.0.0.1:5000/apidocs/` 可查看 API 文件。

**終端機 2: 啟動前端 React 網站**
```bash
cd frontend
npm start
```
- 此服務將運行在 `http://localhost:3000`。
- 執行後，您的預設瀏覽器將會自動開啟此網址，呈現視覺化儀表板。

## 專案維護與擴充

### 爬蟲失效維護

如果某家投信的爬蟲失效 (通常是因為其官網改版)，請參考 `SCRAPING_STRATEGIES.md` 文件。該文件詳細記錄了每個爬蟲的抓取邏輯與目標 URL，能幫助您快速定位問題並進行修正。

### 如何擴充新的爬蟲模組

1.  **在 `config.json` 中新增目標**，並指定一個新的 `firm` ID (例如 `"cathay"`)。
2.  **在 `scripts/scraper.py` 中建立新的爬蟲類別** (例如 `CathayScraper`)，讓它繼承 `BaseScraper`。
3.  **設定資源需求**: 在新類別中設定 `needs_browser = True` (動態網站) 或 `False` (靜態網站)。
4.  **實作 `scrape` 方法**: 在方法中實作抓取邏輯，最後返回一個包含 `"name"` 和 `"holdings"` 的字典。
5.  **註冊爬蟲**: 在 `SCRAPERS` 字典中，將新的 `firm` ID 與您新建的類別關聯起來。
6.  **單獨測試**: `python scripts/scraper.py <your_new_etf_code>`
