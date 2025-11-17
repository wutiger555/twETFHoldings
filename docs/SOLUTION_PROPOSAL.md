# 專案重構方案：改用統一資料來源

## 🎯 目標

取代現有的多爬蟲架構，改用**統一的官方資料來源**，實現：
1. ✅ 所有 ETF 持股資料
2. ✅ 個股即時/歷史價格
3. ✅ 零維護成本
4. ✅ 完全免費開源

---

## 📊 資料來源架構

### 第一層：ETF 持股資料

#### 選項 A：投信投顧公會（推薦）
**網址**：https://www.sitca.org.tw/

**優勢**：
- 所有投信公司的 ETF 持股資料統一在此
- 每日更新
- 格式標準化

**實作方式**：
```python
# 範例：取得所有 ETF 持股明細
import requests
from bs4 import BeautifulSoup

def get_etf_holdings_from_sitca(etf_code):
    """
    從投信投顧公會網站取得 ETF 持股
    這裡只需要一個爬蟲，適用所有 ETF
    """
    url = f"https://www.sitca.org.tw/Products/ETF/Stock.aspx?txtStockCode={etf_code}"
    # 實作統一爬蟲邏輯
    pass
```

#### 選項 B：證交所開放資料（你現在已經在用）
**網址**：https://mopsfin.twse.com.tw/opendata/

**已驗證可用的 API**：
```python
# 基金基本資料（你已經在用）
https://mopsfin.twse.com.tw/opendata/t187ap47_L.csv

# 可能也有持股資料（需要測試）
https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv
```

**優勢**：
- 官方資料，最可靠
- CSV 格式，易處理
- 不會被擋

---

### 第二層：個股價格資料

#### 選項 A：twstock（開源 Python 套件）
**GitHub**：https://github.com/mlouielu/twstock

**特色**：
- ✅ 完全免費
- ✅ 支援即時報價
- ✅ 支援歷史資料
- ✅ Python 原生，易整合

**安裝**：
```bash
pip install twstock
```

**使用範例**：
```python
import twstock

# 即時報價
stock = twstock.realtime.get('2330')  # 台積電
print(stock['realtime']['latest_trade_price'])

# 歷史資料
stock_data = twstock.Stock('2330')
prices = stock_data.price  # 最近 31 天收盤價
dates = stock_data.date
```

#### 選項 B：yfinance
**GitHub**：https://github.com/ranaroussi/yfinance

**特色**：
- ✅ 國際通用
- ✅ 支援台股（代碼加 .TW 或 .TWO）
- ✅ 功能強大

**使用範例**：
```python
import yfinance as yf

# 取得台積電資料
tsmc = yf.Ticker("2330.TW")
hist = tsmc.history(period="1mo")  # 近一個月
current_price = hist['Close'].iloc[-1]
```

#### 選項 C：證交所 OpenAPI（盤後資料）
**API Base**：https://openapi.twse.com.tw/v1/

**範例端點**：
```python
# 每日收盤行情
https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL

# ETF 淨值
https://openapi.twse.com.tw/v1/ETFNavData
```

---

## 🔧 重構實作方案

### 階段一：統一 ETF 持股爬蟲（1-2 天）

**目標**：用一個爬蟲取代現在的多個爬蟲

#### 新架構：
```
scripts/
├── scraper_v2.py          # 新版爬蟲
│   ├── ETFHoldingsScraper  # 統一的持股爬蟲
│   └── StockPriceFetcher   # 個股價格抓取器
├── scraper.py             # 舊版（保留備用）
└── data_sources/
    ├── sitca.py           # 投信投顧公會
    ├── twse_opendata.py   # 證交所開放資料
    └── stock_price.py     # 股價資料（twstock/yfinance）
```

#### 新的 scraper_v2.py 概念：
```python
import twstock
import requests
from typing import Dict, List, Any

class UnifiedETFScraper:
    """統一的 ETF 爬蟲 - 適用所有投信公司"""

    def get_all_etf_list(self) -> List[str]:
        """從證交所取得所有 ETF 代碼"""
        url = "https://www.twse.com.tw/rwd/zh/ETF/domestic?response=json"
        response = requests.get(url, verify=False)
        data = response.json()
        return [item[0] for item in data['data']]

    def get_etf_holdings(self, etf_code: str) -> Dict[str, Any]:
        """
        從投信投顧公會取得持股
        這裡只需要一個邏輯，所有 ETF 都適用
        """
        # 實作統一爬蟲
        pass

    def enrich_with_stock_prices(self, holdings: List[Dict]) -> List[Dict]:
        """為每個持股加上即時價格"""
        for holding in holdings:
            stock_code = holding['code']
            try:
                # 使用 twstock 取得即時報價
                stock = twstock.realtime.get(stock_code)
                holding['current_price'] = stock['realtime']['latest_trade_price']
                holding['change_percent'] = stock['realtime']['change']
            except:
                holding['current_price'] = None
        return holdings

# 使用方式
scraper = UnifiedETFScraper()
etf_codes = scraper.get_all_etf_list()  # 自動取得所有 ETF

for code in etf_codes:
    holdings = scraper.get_etf_holdings(code)
    enriched = scraper.enrich_with_stock_prices(holdings)
    # 儲存...
```

---

### 階段二：後端 API 擴充（1 天）

**新增端點**：

```python
# app/main.py

@cached_ns.route('/holdings/<string:etf_code>/with_prices')
class EnrichedHoldingResource(Resource):
    """取得持股資料 + 即時價格"""

    def get(self, etf_code: str):
        # 讀取持股資料
        holdings = load_holdings(etf_code)

        # 加上即時價格
        for holding in holdings['holdings']:
            stock_code = holding['code']
            price = get_realtime_price(stock_code)  # 使用 twstock
            holding['current_price'] = price

        return holdings

@live_ns.route('/stock/<string:stock_code>/quote')
class StockQuoteResource(Resource):
    """取得個股即時報價"""

    def get(self, stock_code: str):
        import twstock
        stock = twstock.realtime.get(stock_code)
        return {
            'code': stock_code,
            'price': stock['realtime']['latest_trade_price'],
            'change': stock['realtime']['change'],
            'volume': stock['realtime']['accumulate_trade_volume']
        }
```

---

### 階段三：前端功能擴充（2-3 天）

**新功能：個股詳情頁**

```jsx
// frontend/src/pages/StockDetail.js

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const StockDetail = () => {
  const { stockCode } = useParams();
  const [stockData, setStockData] = useState(null);

  useEffect(() => {
    // 取得個股即時報價
    fetch(`http://127.0.0.1:5001/live/stock/${stockCode}/quote`)
      .then(res => res.json())
      .then(data => setStockData(data));
  }, [stockCode]);

  return (
    <div>
      <h1>{stockCode}</h1>
      <h2>目前價格：{stockData?.price}</h2>
      <p>漲跌：{stockData?.change}%</p>
      {/* K 線圖、技術指標等 */}
    </div>
  );
};
```

**修改 ETFDetail.js**：持股列表加上可點擊連結

```jsx
// 原本的持股表格
<td>{h.code}</td>

// 改成可點擊的連結
<td>
  <Link to={`/stock/${h.code}`}>{h.code}</Link>
</td>
```

---

## 📈 新舊架構對比

| 項目 | 舊架構 | 新架構 |
|------|--------|--------|
| 爬蟲數量 | 3+ (每家投信一個) | 1 (統一爬蟲) |
| 維護成本 | 高（網站改版要修改） | 低（官方 API 穩定） |
| 資料完整性 | 部分 ETF | 所有 ETF |
| 個股價格 | ❌ 無 | ✅ 有（即時） |
| 執行速度 | 慢（Selenium） | 快（純 requests） |
| 錯誤率 | 高 | 低 |

---

## 🎯 具體執行步驟

### Step 1: 驗證資料來源（1 小時）

```bash
# 測試投信投顧公會
python3 -c "
import requests
# 測試是否能取得 0050 持股
url = 'https://www.sitca.org.tw/Products/ETF/...'
# 驗證...
"

# 測試 twstock
pip install twstock
python3 -c "
import twstock
stock = twstock.realtime.get('2330')
print(stock)
"
```

### Step 2: 建立新爬蟲（4 小時）

1. 建立 `scripts/scraper_v2.py`
2. 實作 `UnifiedETFScraper`
3. 測試 5-10 個 ETF
4. 比對新舊資料一致性

### Step 3: 整合股價功能（2 小時）

1. 安裝 `twstock`
2. 實作價格抓取函數
3. 測試即時報價

### Step 4: 更新 API（2 小時）

1. 新增 `/holdings/<code>/with_prices` 端點
2. 新增 `/stock/<code>/quote` 端點
3. 測試 API

### Step 5: 前端擴充（4 小時）

1. 建立 `StockDetail.js`
2. 修改 `ETFDetail.js` 加上連結
3. 測試使用者流程

### Step 6: 切換到新架構（1 小時）

1. 備份舊 scraper.py
2. 重新命名 scraper_v2.py
3. 更新 README

---

## 💡 進階功能建議

1. **K 線圖**：使用 `lightweight-charts` 顯示股價走勢
2. **技術指標**：MA、RSI、MACD 等
3. **比價功能**：比較不同 ETF 持有同一檔股票的權重
4. **歷史追蹤**：記錄持股變化
5. **自動通知**：持股異動時發送通知

---

## 🔍 風險評估

| 風險 | 機率 | 影響 | 緩解方案 |
|------|------|------|----------|
| 投信投顧公會改版 | 中 | 高 | 保留證交所 CSV 方案 |
| twstock API 限制 | 低 | 中 | 改用 yfinance |
| 資料延遲 | 低 | 低 | 說明更新頻率 |

---

## 📚 需要安裝的套件

```bash
# requirements.txt 新增
twstock>=1.3.1
yfinance>=0.2.18

# 移除（不再需要）
selenium>=4.36.0
webdriver-manager>=4.0.2
```

---

## ✅ 預期成果

重構完成後：

1. **爬蟲執行時間**：從 5-10 分鐘 → 1-2 分鐘
2. **維護時間**：從每月數小時 → 幾乎為零
3. **ETF 覆蓋率**：從 23 個 → 300+ 個
4. **新功能**：個股詳情頁、即時報價、K 線圖
5. **程式碼行數**：減少 50%
