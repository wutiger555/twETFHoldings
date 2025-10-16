# 台股 ETF 資訊管線 (v5.0)

這是一個採用自動化資料管道、無伺服器 (Serverless) 架構的專案，用於抓取、儲存並提供台灣 ETF 的持股資訊。專案經過精心設計，包含了一套完整的本地開發測試流程，以及一個全自動的生產環境部署方案。

## 核心架構

本專案採用**生產者-消費者分離**的穩定架構：

1.  **爬蟲 (Producer)**: `scripts/scraper.py` 是唯一的資料生產者。它負責連線到外部網站，抓取最新的 ETF 資料，並將結果儲存為本地的 JSON 檔案。

2.  **API (Consumer)**: `app/main.py` 作為本地開發測試伺服器。它只負責讀取由爬蟲產生的本地檔案，並透過 API 提供查詢服務，讓開發者能快速驗證資料正確性。

3.  **自動化 (Automation)**: `.github/workflows/scrape_data.yml` 負責在生產環境中，定時自動化執行爬蟲，並將抓取到的持股資料發布為一個高效能的靜態 API。

---

## 工作流程指南

本專案有兩種主要的工作流程：**本地開發**與**生產部署**。

### 一、 本地開發與測試流程

在您想要新增爬蟲、修改程式碼或驗證資料時，請遵循此流程。

#### **1. 環境設定 (僅需一次)**

確保您已安裝 Python 3 和 Google Chrome 瀏覽器。在專案根目錄下，執行：

```bash
# 安裝所有必要的函式庫
pip install -r requirements.txt
```

#### **2. 設定抓取目標 (`config.json`)**

`config.json` 是管理爬蟲目標的唯一入口。您可以透過編輯此檔案來決定要抓取哪些 ETF。

- **`code`**: ETF 的代碼。
- **`firm`**: 對應到 `scripts/scraper.py` 中 `SCRAPERS` 字典的鍵，用來指定使用哪個爬蟲模組。
- **`enabled`**: 設為 `true` 的目標才會被執行。

#### **3. 執行爬蟲 (`scripts/scraper.py`)**

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

#### **4. 啟動本地 API 伺服器進行驗證**

資料抓取完畢後，啟動本地的 Flask API 伺服器來驗證 `data/` 資料夾中的產出是否正確。

```bash
flask --app app/main run
```
- 伺服器將運行在 `http://127.0.0.1:5000`。
- 訪問 `http://127.0.0.1:5000/apidocs/` 查看本地測試用的 Swagger UI。

--- 

### 二、 生產部署：GitHub 自動化流程

當您在本地完成所有開發與測試後，將專案推送到 GitHub 公開儲存庫，即可實現全自動化。

#### **1. 運作方式**

`.github/workflows/scrape_data.yml` 設定檔會讓 GitHub Actions 定時（預設為每日台灣時間凌晨4點）自動執行 `python scripts/scraper.py` 的**完整模式**。當腳本執行完畢後，若 `data/` 資料夾有任何變動，Actions 會自動將這些新檔案 commit 並 push 回您的儲存庫。

#### **2. 最終 API 端點 (使用 jsDelivr)**

您的 App 或任何前端應用，最終只需要請求以下格式的 URL 即可獲得由 GitHub Actions 自動更新的最新資料。請將 `YourUsername` 和 `YourRepo` 替換為您自己的 GitHub 使用者名稱和儲存庫名稱。

- **ETF 總列表 API**:
  `https://cdn.jsdelivr.net/gh/YourUsername/YourRepo/data/etf_list.json`

- **指定 ETF 持股 API** (以 0050 為例):
  `https://cdn.jsdelivr.net/gh/YourUsername/YourRepo/data/0050.json`

---

## 如何擴充爬蟲 (支援不同投信)

1.  **在 `config.json` 中新增目標**，並指定一個新的 `firm` ID (例如 `"fubon"`)。
2.  **在 `scripts/scraper.py` 中建立新的爬蟲類別** (例如 `FubonScraper`)，讓它繼承 `BaseScraper`，並在 `scrape` 方法中實作針對該網站的抓取邏輯。
3.  **註冊新的爬蟲類別**: 在 `SCRAPERS` 字典中，將 `firm` ID 與您新建的類別關聯起來。