# 台股 ETF 持股資訊專案 (v6.0)

這是一個用於抓取、儲存並透過本地 API 提供台灣 ETF 持股資訊的專案。專案採用高度模組化、可擴充的設計，讓開發者可以輕易地為新的證券投信公司新增爬蟲模組。

## 設計理念

本專案的架構基於以下幾個核心設計理念：

- **模組化 (Modularity)**: 每家投信公司的爬蟲邏輯都被封裝在獨立的類別 (`class`) 中，與其他爬蟲完全解耦。

- **可擴充性 (Extensibility)**: `scripts/scraper.py` 中的 `SCRAPERS` 字典扮演著一個簡單的「插件註冊中心」。只需將新的爬蟲類別加入此字典，即可讓主程式辨識並執行，無需修改核心邏輯。

- **職責分離 (Separation of Concerns)**:
    - **爬蟲 (`Scraper`)**: 唯一的職責是訪問目標網站、解析 HTML 並返回一個標準化的 Python 物件。它**不關心**資料如何儲存。
    - **執行緒 (`Task Runner`)**: 負責接收爬蟲回傳的資料、添加額外元資訊 (如更新時間戳)，並將其格式化、寫入最終的 JSON 檔案。

- **資源效率 (Resource Efficiency)**: 透過 `needs_browser` 類別屬性，執行緒可以智慧地判斷是否需要為某個爬蟲任務啟動耗費資源的 Selenium 瀏覽器。對於可直接透過 HTTP 請求完成的靜態網站，可大幅提升執行效率。

- **資料一致性 (Data Consistency)**: 所有爬蟲模組都必須返回一個固定結構的資料，並由執行緒統一處理，確保最終產出的所有 `data/*.json` 檔案都有一致的格式。

## 專案狀態

- **v6.0**
- **支援的投信公司**:
    - ✅ **元大投信 (Yuanta)** - `firm: "yuanta"` (使用 Selenium)
    - ✅ **富邦投信 (Fubon)** - `firm: "fubon"` (使用 Requests)
    - ⏳ **國泰投信 (Cathay)** - `firm: "cathay"` (待開發)

## 核心資料流

當 `scripts/scraper.py` 執行時，資料處理流程如下：

1.  **讀取設定**: `main()` 函式讀取 `config.json`，篩選出所有 `enabled: true` 的 ETF 目標。
2.  **任務分配**: 主程式使用 `ThreadPoolExecutor` 為每一個目標非同步地派發一個 `run_scraper_task` 任務。
3.  **選擇爬蟲**: `run_scraper_task` 根據目標中的 `firm` ID，從 `SCRAPERS` 字典中找到對應的爬蟲類別 (例如 `FubonScraper`)。
4.  **判斷資源**: 檢查爬蟲類別的 `needs_browser` 屬性：
    - 若為 `True`，則啟動一個 Selenium WebDriver 實例。
    - 若為 `False`，則跳過此步驟。
5.  **執行抓取**: 呼叫爬蟲實例的 `.scrape()` 方法。需要瀏覽器的爬蟲會傳入 `driver` 物件，反之則不傳。
6.  **返回資料**: 爬蟲完成解析後，返回一個包含 `name` 和 `holdings` 的標準 Python 字典。
7.  **處理與儲存**: `run_scraper_task` 接收到字典後，添加 `last_updated_utc` 時間戳，組裝成最終的 JSON 結構，並寫入到 `data/` 目錄下對應的 `.json` 檔案。
8.  **產出總表**: 若在完整模式下執行，`main()` 會收集所有成功抓取的 ETF 資訊，最後覆寫一份 `data/etf_list.json` 作為總清單。

## 輸出資料格式

所有 ETF 的持股資料都會被儲存為 JSON 檔案，格式如下：

```json
{
    "last_updated_utc": "2025-10-18T15:44:28.546035+00:00",
    "holdings": [
        {
            "asset_type": "stock",
            "code": "2330",
            "name": "台積電",
            "shares": 118172064,
            "weight": 62.1732
        },
        {
            "asset_type": "bond",
            "code": "A00107",
            "name": "100央債甲7",
            "shares": null,
            "weight": 0.0535
        }
    ]
}
```
- **`asset_type`**: `string` - 資產類別，例如 "stock", "future", "bond"。
- **`shares`**: `integer | null` - 持有股數或口數。若該資產無此資訊，則為 `null`。
- **`weight`**: `float | null` - 佔比權重(%)。若該資產無此資訊，則為 `null`。

## 開發與測試指南

### 1. 環境設定

確保您已安裝 Python 3 和 Google Chrome 瀏覽器。在專案根目錄下，執行：

```bash
# 安裝所有必要的函式庫
pip install -r requirements.txt
```

### 2. 執行現有爬蟲

- **設定目標**: 編輯 `config.json`，將您想抓取的 ETF 的 `"enabled"` 設為 `true`。
- **執行**:
  ```bash
  # 抓取所有 "enabled": true 的目標
  python scripts/scraper.py

  # 僅抓取單一目標進行測試
  python scripts/scraper.py 006208
  ```

### 3. 如何擴充新的爬蟲模組

假設我們要為「國泰投信」新增一個爬蟲，其 `firm` ID 為 `cathay`。

**步驟 1: 分析目標網站**

- 前往國泰投信的持股頁面，判斷其為靜態或動態載入。
- **靜態網站**: 如果「檢視網頁原始碼」可以看到完整資料，使用 `requests` 即可。
- **動態網站**: 如果資料由 JavaScript 產生，則需要使用 `selenium`。

**步驟 2: 新增設定 (`config.json`)**

在 `etf_targets` 列表中，加入國泰的 ETF，並確保 `firm` ID 是唯一的。

```json
{
    "code": "00878",
    "firm": "cathay",
    "enabled": true
}
```

**步驟 3: 建立爬蟲類別 (`scripts/scraper.py`)**

在 `scraper.py` 中，建立一個繼承自 `BaseScraper` 的新類別。

```python
class CathayScraper(BaseScraper):
    # 根據步驟 1 的分析結果設定
    needs_browser = True # 或 False

    def scrape(self, **kwargs):
        # 如果 needs_browser = True, driver 物件會被傳入
        if self.needs_browser:
            driver = kwargs.get('driver')
            if not driver:
                raise ValueError("A Selenium driver is required for this scraper.")
        
        # --- 實作你的抓取邏輯 ---
        # 1. 存取目標 URL
        # 2. 解析 HTML (使用 BeautifulSoup)
        # 3. 遍歷表格，將資料存入一個 list of dicts
        
        etf_name = "抓取到的基金名稱"
        holdings_data = [
            {"asset_type": "stock", "code": "...", "name": "...", "shares": ..., "weight": ...},
            # ...
        ]

        # 4. 返回標準格式的字典
        return {"name": etf_name, "holdings": holdings_data}
```

**步驟 4: 註冊爬蟲**

在 `SCRAPERS` 字典中，將新的 `firm` ID 與剛建立的類別關聯起來。

```python
SCRAPERS = {
    "yuanta": YuantaScraper,
    "fubon": FubonScraper,
    "cathay": CathayScraper, # 新增此行
}
```

**步驟 5: 測試**

使用單獨測試模式，確保新的爬蟲可以正確運作。

```bash
python scripts/scraper.py 00878
```
確認 `data/00878.json` 檔案已成功產生且內容無誤後，即可完成擴充。