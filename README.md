
# 台股 ETF 資訊專案 (v5.2 - 本地開發版)

這是一個用於抓取、儲存並透過本地 API 提供台灣 ETF 持股資訊的專案。專案採用模組化設計，可輕易擴充以支援多家不同投信公司的網站，並包含完整的本地開發與測試流程。

## 核心架構

本專案採用**生產者-消費者分離**的穩定架構：

1.  **爬蟲 (Producer)**: `scripts/scraper.py` 是唯一的資料生產者。它負責連線到外部網站，抓取最新的 ETF 資料，並將結果儲存為本地的 JSON 檔案。

2.  **API (Consumer)**: `app/main.py` 作為本地開發測試伺服器。它只負責讀取由爬蟲產生的本地檔案，並透過 API 提供查詢服務，讓開發者能快速驗證資料正確性。

## 專案結構

```
/twETFHoldings/
├── app/                  # Flask 應用程式目錄
│   └── main.py           # API 伺服器主程式
├── data/                 # (由爬蟲自動產生)
│   ├── 0050.json
│   └── etf_list.json
├── scripts/
│   └── scraper.py        # 爬蟲主程式
├── config.json           # 爬蟲目標設定檔
├── .gitignore
├── CHANGELOG.md
├── README.md
└── requirements.txt
```

## 本地開發與測試流程

### 1. 環境設定

確保您已安裝 Python 3 和 Google Chrome 瀏覽器。在專案根目錄下，執行：

```bash
# 安裝所有必要的函式庫
pip install -r requirements.txt
```

### 2. 設定抓取目標 (`config.json`)

`config.json` 是管理爬蟲目標的唯一入口。您可以透過編輯此檔案來決定要抓取哪些 ETF。

- **`code`**: ETF 的代碼。
- **`firm`**: 對應到 `scripts/scraper.py` 中 `SCRAPERS` 字典的鍵，用來指定使用哪個爬蟲模組。
- **`enabled`**: 設為 `true` 的目標才會被執行。

### 3. 執行爬蟲 (`scripts/scraper.py`)

此腳本提供兩種執行模式：

- **完整模式 (全面更新)**
  不帶任何參數執行，將會抓取 `config.json` 中所有 `"enabled": true` 的 ETF，並在最後更新總清單 `data/etf_list.json`。
  ```bash
  python scripts/scraper.py
  ```

- **測試模式 (單獨測試)**
  在開發新爬蟲時，可透過傳入 ETF 代碼作為參數，僅針對特定目標進行測試，以節省時間。此模式**不會**更新 `etf_list.json`。
  ```bash
  # 僅測試 0050
  python scripts/scraper.py 0050
  ```

### 4. 在本機運行 API 伺服器進行驗證

資料抓取完畢後，啟動本地的 Flask API 伺服器來驗證結果。

```bash
flask --app app/main run
```
- 伺服器將運行在 `http://127.0.0.1:5000`。
- 訪問 `http://127.0.0.1:5000/apidocs/` 查看本地測試用的 Swagger UI。

## 如何擴充爬蟲 (支援不同投信)

1.  **在 `config.json` 中新增目標**，並指定一個新的 `firm` ID (例如 `"fubon"`)。
2.  **在 `scripts/scraper.py` 中建立新的爬蟲類別** (例如 `FubonScraper`)，讓它繼承 `BaseScraper`，並在 `scrape` 方法中實作針對該網站的抓取邏輯。
3.  **註冊新的爬蟲類別**: 在 `SCRAPERS` 字典中，將 `firm` ID 與您新建的類別關聯起來。
