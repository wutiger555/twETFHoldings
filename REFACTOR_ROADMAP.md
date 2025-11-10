# 專案重構路線圖

## 🎯 核心問題

**現狀**：需要為每家投信公司維護獨立爬蟲
- 元大投信 → `YuantaScraper` (Selenium)
- 富邦投信 → `FubonScraper` (requests)
- 國泰投信 → `CathayScraper` (未實作)
- ...更多投信 → 需要更多爬蟲

**痛點**：
1. ❌ 維護成本高（網站改版就掛）
2. ❌ 覆蓋率低（只有 23 個 ETF）
3. ❌ 無法顯示個股價格
4. ❌ 執行速度慢（Selenium）

---

## 🚀 解決方案：三個選項

### 選項 A：FinMind API（最推薦）⭐⭐⭐⭐⭐

**官網**：https://finmind.github.io/
**註冊**：https://finmindtrade.com/

#### 優勢
- ✅ **一站式解決方案**：ETF 持股 + 個股價格 + 財報數據
- ✅ **完全免費**：註冊後 600 請求/小時
- ✅ **RESTful API**：不需要爬蟲
- ✅ **資料完整**：涵蓋所有台股 ETF
- ✅ **維護成本為零**：官方維護

#### 可用資料
```python
# 1. ETF 持股明細
dataset: "TaiwanStockHoldingsPer"

# 2. 個股價格（日線）
dataset: "TaiwanStockPrice"

# 3. 個股資訊
dataset: "TaiwanStockInfo"

# 4. 財務報表
dataset: "TaiwanStockFinancialStatements"

# 更多：https://finmind.github.io/tutor/TaiwanMarket/DataList/
```

#### 實作步驟
1. 註冊並取得 API Token
2. 使用 `finmind_example.py` 測試
3. 重寫 `scraper.py`：
   ```python
   # 舊架構：多個爬蟲類別
   class YuantaScraper(BaseScraper): ...
   class FubonScraper(BaseScraper): ...

   # 新架構：統一 API 呼叫
   class FinMindDataFetcher:
       def get_all_etf_holdings(self):
           # 一次取得所有 ETF
           pass

       def get_stock_prices(self, stock_codes: list):
           # 批次取得股價
           pass
   ```
4. 更新前端：顯示個股價格

#### 限制
- ⚠️ 免費版有流量限制（600 req/hr）
- ⚠️ 資料可能有延遲（非即時）

---

### 選項 B：投信投顧公會爬蟲 ⭐⭐⭐

**網址**：https://www.sitca.org.tw/

#### 優勢
- ✅ **統一來源**：所有投信的 ETF 都在這
- ✅ **官方資料**：最權威
- ✅ **一個爬蟲搞定**：不用為每家投信寫爬蟲

#### 缺點
- ❌ 仍需爬蟲（可能改版）
- ❌ 沒有個股價格（需要額外來源）

#### 實作步驟
1. 研究網站結構
2. 寫一個統一爬蟲
3. 配合其他 API 取得股價

---

### 選項 C：混合方案 ⭐⭐⭐⭐

結合證交所開放資料 + 股價 API

#### ETF 持股：證交所 CSV
```python
# 你已經在用的
https://mopsfin.twse.com.tw/opendata/t187ap47_L.csv

# 可能還有其他端點（需要研究）
https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv
```

#### 個股價格：選擇其一
1. **yfinance**：國際通用，台股支援
2. **twstock**：台股專用，功能豐富
3. **證交所 OpenAPI**：官方但只有盤後

---

## 📊 方案比較表

| 項目 | 現況 | FinMind (A) | 投信公會 (B) | 混合方案 (C) |
|------|------|-------------|--------------|--------------|
| **爬蟲數量** | 3+ | 0 | 1 | 1 |
| **ETF 覆蓋** | 23 個 | 全部 | 全部 | 部分 |
| **個股價格** | ❌ | ✅ | ❌ | ✅ |
| **維護成本** | 高 | 零 | 中 | 低 |
| **實作難度** | - | ⭐ | ⭐⭐⭐ | ⭐⭐ |
| **資料完整性** | 中 | 高 | 高 | 中 |
| **執行速度** | 慢 | 快 | 中 | 快 |
| **成本** | 免費 | 免費 | 免費 | 免費 |

**推薦順序**：A > C > B

---

## 🛠️ 重構實作計劃

### 階段 1：驗證 FinMind（半天）

**目標**：確認 FinMind 能滿足需求

**步驟**：
```bash
# 1. 註冊 FinMind
# https://finmindtrade.com/

# 2. 測試 API
python finmind_example.py

# 3. 驗證資料
# - 檢查 ETF 持股是否完整
# - 檢查股價資料是否準確
# - 確認請求限制是否足夠
```

**決策點**：
- ✅ 如果 FinMind 滿足需求 → 進入階段 2
- ❌ 如果有問題 → 考慮選項 C（混合方案）

---

### 階段 2：建立新爬蟲（1 天）

**目標**：建立基於 FinMind 的資料抓取系統

**文件結構**：
```
scripts/
├── scraper.py           # 舊版（保留）
├── scraper_finmind.py   # 新版（FinMind）
└── data_fetchers/
    ├── finmind.py       # FinMind API 封裝
    └── price.py         # 價格資料處理
```

**核心程式碼**：
```python
# scripts/scraper_finmind.py

from data_fetchers.finmind import FinMindAPI

class FinMindETFScraper:
    def __init__(self, token: str):
        self.api = FinMindAPI(token)

    def fetch_all_etfs(self):
        """取得所有 ETF 清單"""
        etfs = self.api.get_all_etfs()
        return [etf['stock_id'] for etf in etfs]

    def fetch_etf_holdings(self, etf_code: str):
        """取得 ETF 持股明細"""
        holdings = self.api.get_etf_holdings(etf_code)
        return self.process_holdings(holdings)

    def enrich_with_prices(self, holdings: list):
        """為持股加上即時價格"""
        stock_codes = [h['code'] for h in holdings]
        prices = self.api.get_batch_prices(stock_codes)

        for holding in holdings:
            code = holding['code']
            if code in prices:
                holding['current_price'] = prices[code]
                holding['market_value'] = holding['shares'] * prices[code]

        return holdings

    def run(self):
        """執行完整抓取流程"""
        etfs = self.fetch_all_etfs()
        print(f"找到 {len(etfs)} 個 ETF")

        for etf_code in etfs:
            holdings = self.fetch_etf_holdings(etf_code)
            enriched = self.enrich_with_prices(holdings)
            self.save_to_json(etf_code, enriched)
```

---

### 階段 3：API 擴充（半天）

**目標**：後端支援個股價格查詢

**新增端點**：
```python
# app/main.py

@cached_ns.route('/holdings/<string:etf_code>/enriched')
class EnrichedHoldingResource(Resource):
    """持股資料 + 即時價格"""
    def get(self, etf_code: str):
        holdings = load_holdings(etf_code)
        # 加上即時價格
        return enrich_holdings_with_prices(holdings)

@live_ns.route('/stock/<string:stock_code>')
class StockResource(Resource):
    """個股詳情"""
    def get(self, stock_code: str):
        return {
            'code': stock_code,
            'price': get_latest_price(stock_code),
            'change': get_price_change(stock_code),
            'volume': get_volume(stock_code)
        }
```

---

### 階段 4：前端新功能（1 天）

**目標**：支援個股詳情頁

**新增頁面**：
```
frontend/src/pages/
├── Dashboard.js      # 現有
├── ETFDetail.js      # 現有
└── StockDetail.js    # 新增
```

**功能**：
1. 點擊持股中的個股代碼 → 跳轉到個股詳情頁
2. 顯示個股資訊：
   - 即時價格
   - 漲跌幅
   - 成交量
   - K 線圖（可選）
   - 哪些 ETF 持有此股票

**路由設定**：
```jsx
// App.js
<Routes>
  <Route path="/" element={<Dashboard />} />
  <Route path="/etf/:etfCode" element={<ETFDetail />} />
  <Route path="/stock/:stockCode" element={<StockDetail />} /> {/* 新增 */}
</Routes>
```

---

### 階段 5：測試與切換（半天）

**測試清單**：
- [ ] 新爬蟲能成功抓取所有 ETF
- [ ] 持股資料與舊版一致
- [ ] 價格資料正確
- [ ] API 回應正常
- [ ] 前端顯示正確

**切換步驟**：
```bash
# 1. 備份舊版
mv scripts/scraper.py scripts/scraper_old.py
mv scripts/scraper_finmind.py scripts/scraper.py

# 2. 更新設定
# 修改 config.json（可能不需要 firm 欄位了）

# 3. 重新抓取資料
python scripts/scraper.py

# 4. 驗證資料
python scripts/validate_data.py

# 5. 重啟服務
flask --app app/main run
```

---

## 📈 預期成果

### 數據指標

| 指標 | 重構前 | 重構後 | 改善 |
|------|--------|--------|------|
| ETF 數量 | 23 | 300+ | 📈 1200% |
| 爬蟲執行時間 | 5-10 分鐘 | 1-2 分鐘 | 📉 80% |
| 維護時間/月 | 2-4 小時 | < 10 分鐘 | 📉 95% |
| 程式碼行數 | ~500 行 | ~300 行 | 📉 40% |
| 錯誤率 | 5-10% | < 1% | 📉 90% |

### 新功能
- ✅ 個股即時價格
- ✅ 個股詳情頁
- ✅ 持股市值計算
- ✅ 跨 ETF 持股分析（同一股票被哪些 ETF 持有）

### 技術債務清除
- ✅ 移除 Selenium 依賴
- ✅ 統一資料來源
- ✅ 簡化架構
- ✅ 改善錯誤處理

---

## 🎯 下一步行動

### 立即行動（今天）
1. ✅ 閱讀 `SOLUTION_PROPOSAL.md`
2. ✅ 閱讀 `finmind_example.py`
3. ⬜ 註冊 FinMind 帳號
4. ⬜ 測試 `python finmind_example.py`

### 本週行動
1. ⬜ 驗證 FinMind 資料完整性
2. ⬜ 決定採用方案（A/B/C）
3. ⬜ 開始階段 2：建立新爬蟲

### 兩週內完成
1. ⬜ 完成所有 5 個階段
2. ⬜ 上線新版系統
3. ⬜ 下線舊爬蟲
4. ⬜ 更新文件

---

## 📞 需要協助？

如果在重構過程中遇到問題：

1. **FinMind API 問題**
   - 官方文件：https://finmind.github.io/
   - GitHub Issues：https://github.com/FinMind/FinMind/issues

2. **架構設計問題**
   - 參考 `SOLUTION_PROPOSAL.md`
   - 查看 `finmind_example.py` 範例

3. **實作細節問題**
   - 先在小範圍測試（5-10 個 ETF）
   - 確認無誤後再擴展到全部

---

## 🎉 重構完成後

你將擁有：
- 🚀 更快的執行速度
- 🛠️ 更低的維護成本
- 📊 更完整的資料
- 💰 更多的功能
- 😊 更好的使用者體驗

**開始重構吧！** 🚀
