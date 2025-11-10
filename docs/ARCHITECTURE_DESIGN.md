# 台股 ETF App 完整架構設計
## React Native iOS App + Flask Backend + FinMind API

---

## 🎯 專案目標

打造一個 **React Native iOS App**，提供：
1. ✅ 300+ 台股 ETF 持股資訊
2. ✅ 個股即時價格與技術分析
3. ✅ 跨 ETF 持股分析
4. ✅ 自選清單與通知
5. ✅ 完全使用 FinMind 免費方案（600 req/hr）

---

## 🏗️ 三層架構設計

```
┌─────────────────────────────────────────────────────────────┐
│                    React Native iOS App                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  ETF 列表    │  │  ETF 詳情    │  │  個股詳情    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  自選清單    │  │  搜尋功能    │  │  設定頁面    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  本地快取：AsyncStorage + SQLite                             │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend Server                      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  RESTful API Layer                                    │   │
│  │  - /api/v1/etfs                                       │   │
│  │  - /api/v1/etf/:code/holdings                        │   │
│  │  - /api/v1/stock/:code                               │   │
│  │  - /api/v1/stock/:code/history                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Cache Layer (Redis)                                  │   │
│  │  - ETF 清單快取（24h）                                │   │
│  │  - ETF 持股快取（24h）                                │   │
│  │  - 股價快取（15min）                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Data Persistence (PostgreSQL / SQLite)              │   │
│  │  - 歷史持股資料                                       │   │
│  │  - 歷史股價資料                                       │   │
│  │  - 使用者自選清單                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FinMind API Client                                   │   │
│  │  - 請求限流器（600 req/hr）                           │   │
│  │  - 批次請求優化                                       │   │
│  │  - 錯誤重試機制                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ↕                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Background Jobs (Celery / APScheduler)              │   │
│  │  - 每日收盤後更新 ETF 持股                            │   │
│  │  - 每 15 分鐘更新熱門股價                             │   │
│  │  - 每週清理過期快取                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP/REST API (限流)
┌─────────────────────────────────────────────────────────────┐
│                    FinMind API                                │
│               (免費：600 requests / hour)                     │
│                                                               │
│  - TaiwanStockInfo (ETF 清單)                                │
│  - TaiwanStockHoldingsPer (ETF 持股)                         │
│  - TaiwanStockPrice (股價日線)                               │
│  - TaiwanStockPriceTick (即時報價 - 付費)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 快取策略設計

### 1. 後端快取層（Redis）

**目的**：最大化減少對 FinMind API 的請求

#### 快取規劃表

| 資料類型 | 更新頻率 | 快取時間 | FinMind API 呼叫 | 說明 |
|---------|---------|---------|-----------------|------|
| **ETF 清單** | 每日 1 次 | 24 小時 | 1 次/天 | 上市 ETF 清單變動不頻繁 |
| **ETF 持股** | 每日 1 次 | 24 小時 | 1 次/ETF/天 | 持股明細每日更新即可 |
| **股價日線** | 每日 1 次 | 24 小時 | 1 次/股票/天 | 收盤後更新 |
| **股價即時** | 每 15 分鐘 | 15 分鐘 | N/A | 使用日線資料模擬 |
| **搜尋索引** | 每日 1 次 | 24 小時 | 0 次 | 從快取資料建立 |

#### Redis 鍵值設計

```python
# ETF 清單
"etf:list" → JSON array
TTL: 86400 秒（24h）

# ETF 持股
"etf:holdings:{code}" → JSON object
TTL: 86400 秒（24h）

# 股價資料
"stock:price:{code}:daily" → JSON object
TTL: 86400 秒（24h）

# 股價歷史（30天）
"stock:history:{code}:30d" → JSON array
TTL: 3600 秒（1h）

# 熱門股票清單（從所有 ETF 持股統計）
"stats:popular_stocks" → JSON array
TTL: 86400 秒（24h）
```

---

### 2. 資料庫持久化層（PostgreSQL / SQLite）

**目的**：儲存歷史資料，支援趨勢分析

#### 資料表設計

```sql
-- ETF 基本資料
CREATE TABLE etfs (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    tracking_index VARCHAR(200),
    issuer VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ETF 持股歷史
CREATE TABLE etf_holdings (
    id SERIAL PRIMARY KEY,
    etf_code VARCHAR(10) REFERENCES etfs(code),
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    shares BIGINT,
    weight DECIMAL(10, 4),
    market_value DECIMAL(20, 2),
    record_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(etf_code, stock_code, record_date)
);
CREATE INDEX idx_holdings_etf ON etf_holdings(etf_code, record_date);
CREATE INDEX idx_holdings_stock ON etf_holdings(stock_code, record_date);

-- 股票基本資料
CREATE TABLE stocks (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    industry VARCHAR(50),
    market VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 股價歷史
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) REFERENCES stocks(code),
    date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, date)
);
CREATE INDEX idx_prices_stock ON stock_prices(stock_code, date DESC);

-- 使用者自選清單（為 App 準備）
CREATE TABLE user_watchlists (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    item_type VARCHAR(10) NOT NULL, -- 'ETF' or 'STOCK'
    item_code VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_type, item_code)
);
CREATE INDEX idx_watchlist_user ON user_watchlists(user_id);
```

---

### 3. App 本地快取（React Native）

**目的**：離線瀏覽、快速載入

#### 快取策略

```javascript
// AsyncStorage：輕量資料
- 使用者設定
- 自選清單
- 最近瀏覽

// SQLite：結構化資料
- ETF 清單（最多 500 筆）
- 常用 ETF 持股（最多 10 個 ETF）
- 股價資料（最多 50 檔股票 × 30 天）

// 圖片快取
- ETF logo
- 股票圖示
```

#### 快取更新策略

```javascript
// 1. 啟動時檢查
App 啟動 → 檢查快取時間 → 超過 1 小時則背景更新

// 2. 下拉刷新
使用者手動刷新 → 強制從後端取得最新資料

// 3. 智慧預載
進入 ETF 列表 → 預載前 20 個 ETF 的持股資料
```

---

## 🤖 定時任務設計

使用 **APScheduler** 實作定時更新

### 任務規劃表

| 任務名稱 | 執行時間 | 頻率 | 目的 | FinMind 呼叫量 |
|---------|---------|------|------|---------------|
| **更新 ETF 清單** | 每日 14:00 | 1 次/天 | 取得最新 ETF 清單 | 1 次 |
| **更新所有 ETF 持股** | 每日 14:30-16:00 | 1 次/天 | 更新所有 ETF 持股 | 300 次 (分批) |
| **更新熱門股價** | 每日 14:30 | 1 次/天 | 更新前 100 熱門股票 | 100 次 |
| **更新自選股價** | 每 15 分鐘 | 營業日 | 更新使用者自選股票 | 視自選數量 |
| **清理過期快取** | 每週日 02:00 | 1 次/週 | 清理 Redis 過期資料 | 0 次 |
| **備份資料庫** | 每日 03:00 | 1 次/天 | 備份 PostgreSQL | 0 次 |

### 總請求量估算

```python
# 每日請求量估算
ETF 清單: 1 次
ETF 持股: 300 次 (所有 ETF)
股價更新: 100 次 (熱門股票)
自選更新: 50 次 (估計平均)
---------------------------------------
總計: 451 次/天

# 小時分布
14:00-16:00: 集中更新 (400 次)
其他時間: 零星更求 (51 次)

# 安全邊界
600 req/hr - 400 req (尖峰) = 200 req 緩衝
✅ 充足！
```

---

## 🔧 後端架構重構

### 新的目錄結構

```
twETFHoldings/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Flask app 入口
│   ├── config.py               # 配置管理
│   ├── extensions.py           # Redis, DB 初始化
│   │
│   ├── api/                    # RESTful API
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── etf.py         # ETF 相關端點
│   │   │   ├── stock.py       # 股票相關端點
│   │   │   ├── search.py      # 搜尋功能
│   │   │   ├── user.py        # 使用者自選
│   │   │   └── stats.py       # 統計資料
│   │   └── v2/                # 未來版本
│   │
│   ├── services/               # 業務邏輯層
│   │   ├── __init__.py
│   │   ├── finmind.py         # FinMind API 客戶端
│   │   ├── cache.py           # 快取管理
│   │   ├── etf_service.py     # ETF 業務邏輯
│   │   └── stock_service.py   # 股票業務邏輯
│   │
│   ├── models/                 # 資料模型
│   │   ├── __init__.py
│   │   ├── etf.py
│   │   ├── stock.py
│   │   └── user.py
│   │
│   ├── tasks/                  # 定時任務
│   │   ├── __init__.py
│   │   ├── scheduler.py       # APScheduler 配置
│   │   ├── etf_tasks.py       # ETF 更新任務
│   │   └── stock_tasks.py     # 股價更新任務
│   │
│   └── utils/                  # 工具函數
│       ├── __init__.py
│       ├── rate_limiter.py    # 限流器
│       └── helpers.py
│
├── mobile/                     # React Native App
│   ├── src/
│   │   ├── screens/           # 頁面
│   │   │   ├── HomeScreen.js
│   │   │   ├── ETFListScreen.js
│   │   │   ├── ETFDetailScreen.js
│   │   │   ├── StockDetailScreen.js
│   │   │   └── WatchlistScreen.js
│   │   │
│   │   ├── components/        # 元件
│   │   │   ├── ETFCard.js
│   │   │   ├── StockItem.js
│   │   │   ├── PriceChart.js
│   │   │   └── HoldingTable.js
│   │   │
│   │   ├── services/          # API 呼叫
│   │   │   ├── api.js
│   │   │   └── cache.js
│   │   │
│   │   ├── store/             # 狀態管理 (Redux/Zustand)
│   │   │   ├── etfSlice.js
│   │   │   ├── stockSlice.js
│   │   │   └── userSlice.js
│   │   │
│   │   └── utils/
│   │       ├── storage.js     # AsyncStorage 封裝
│   │       └── database.js    # SQLite 封裝
│   │
│   ├── ios/                   # iOS 專案
│   ├── android/               # Android 專案 (未來)
│   ├── package.json
│   └── app.json
│
├── scripts/
│   ├── scraper_finmind.py    # 新版爬蟲（使用 FinMind）
│   └── init_db.py            # 資料庫初始化
│
├── tests/
│   ├── test_api.py
│   ├── test_services.py
│   └── test_cache.py
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.worker
│   └── docker-compose.yml
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 API 設計（v1）

### 基礎設計原則

```
基礎 URL: https://api.yourapp.com/api/v1
認證: Bearer Token (可選，初期不需要)
回應格式: JSON
錯誤處理: 統一錯誤格式
```

### API 端點設計

#### 1. ETF 相關

```javascript
// 取得所有 ETF 清單
GET /api/v1/etfs
Query Parameters:
  - page: 頁碼 (default: 1)
  - limit: 每頁數量 (default: 50)
  - issuer: 發行商篩選 (optional)
  - type: ETF 類型篩選 (optional)

Response:
{
  "success": true,
  "data": {
    "etfs": [
      {
        "code": "0050",
        "name": "元大台灣50",
        "issuer": "元大投信",
        "type": "股票型",
        "nav": 150.5,
        "change_percent": 1.2
      },
      ...
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 300,
      "total_pages": 6
    }
  },
  "cached_at": "2025-01-10T14:30:00Z"
}

// 取得單一 ETF 基本資訊
GET /api/v1/etf/:code

Response:
{
  "success": true,
  "data": {
    "code": "0050",
    "name": "元大台灣50",
    "issuer": "元大投信",
    "type": "股票型",
    "tracking_index": "台灣50指數",
    "inception_date": "2003-06-30",
    "nav": 150.5,
    "aum": 250000000000,  // 資產規模
    "expense_ratio": 0.32  // 經理費
  },
  "cached_at": "2025-01-10T14:30:00Z"
}

// 取得 ETF 持股明細
GET /api/v1/etf/:code/holdings
Query Parameters:
  - date: 指定日期 (optional, default: latest)

Response:
{
  "success": true,
  "data": {
    "etf_code": "0050",
    "etf_name": "元大台灣50",
    "record_date": "2025-01-10",
    "holdings": [
      {
        "stock_code": "2330",
        "stock_name": "台積電",
        "shares": 50000000,
        "weight": 45.5,
        "market_value": 15000000000,
        "current_price": 600.0,  // 即時價格
        "change_percent": 1.5
      },
      ...
    ],
    "total_stocks": 50,
    "total_market_value": 33000000000
  },
  "cached_at": "2025-01-10T14:30:00Z"
}

// 取得 ETF 持股變化
GET /api/v1/etf/:code/holdings/changes
Query Parameters:
  - days: 比較天數 (default: 7)

Response:
{
  "success": true,
  "data": {
    "comparison_dates": ["2025-01-03", "2025-01-10"],
    "changes": [
      {
        "stock_code": "2330",
        "stock_name": "台積電",
        "weight_change": 0.5,  // 權重變化
        "shares_change": 1000000,  // 股數變化
        "action": "increase"  // increase/decrease/new/removed
      },
      ...
    ]
  }
}
```

#### 2. 股票相關

```javascript
// 取得個股基本資訊
GET /api/v1/stock/:code

Response:
{
  "success": true,
  "data": {
    "code": "2330",
    "name": "台積電",
    "industry": "半導體",
    "market": "上市",
    "price": 600.0,
    "change": 9.0,
    "change_percent": 1.52,
    "volume": 25000000,
    "market_cap": 15600000000000,
    "held_by_etfs": [
      {
        "etf_code": "0050",
        "etf_name": "元大台灣50",
        "weight": 45.5
      },
      ...
    ]
  },
  "cached_at": "2025-01-10T14:30:00Z"
}

// 取得個股歷史價格
GET /api/v1/stock/:code/history
Query Parameters:
  - period: 時間範圍 (7d/30d/90d/1y, default: 30d)
  - interval: 資料間隔 (daily/weekly, default: daily)

Response:
{
  "success": true,
  "data": {
    "stock_code": "2330",
    "period": "30d",
    "prices": [
      {
        "date": "2025-01-10",
        "open": 595.0,
        "high": 605.0,
        "low": 590.0,
        "close": 600.0,
        "volume": 25000000
      },
      ...
    ]
  },
  "cached_at": "2025-01-10T14:30:00Z"
}

// 批次取得股價（為 App 優化）
POST /api/v1/stocks/batch
Body:
{
  "codes": ["2330", "2317", "2454"]
}

Response:
{
  "success": true,
  "data": [
    {
      "code": "2330",
      "price": 600.0,
      "change_percent": 1.52
    },
    ...
  ]
}
```

#### 3. 搜尋功能

```javascript
// 全域搜尋
GET /api/v1/search
Query Parameters:
  - q: 搜尋關鍵字 (必填)
  - type: 類型篩選 (etf/stock/all, default: all)

Response:
{
  "success": true,
  "data": {
    "etfs": [
      {
        "code": "0050",
        "name": "元大台灣50",
        "type": "ETF"
      }
    ],
    "stocks": [
      {
        "code": "2330",
        "name": "台積電",
        "type": "STOCK"
      }
    ]
  }
}
```

#### 4. 統計資料

```javascript
// 熱門股票排行
GET /api/v1/stats/popular-stocks
Query Parameters:
  - limit: 數量 (default: 20)

Response:
{
  "success": true,
  "data": [
    {
      "rank": 1,
      "stock_code": "2330",
      "stock_name": "台積電",
      "held_by_etf_count": 85,  // 被幾個 ETF 持有
      "total_weight": 1250.5,   // 總權重
      "avg_weight": 14.7        // 平均權重
    },
    ...
  ]
}

// ETF 持股重疊分析
GET /api/v1/stats/overlap
Query Parameters:
  - codes: ETF 代碼列表 (comma-separated)

Response:
{
  "success": true,
  "data": {
    "etfs": ["0050", "0056"],
    "overlap_stocks": [
      {
        "stock_code": "2330",
        "stock_name": "台積電",
        "in_etfs": ["0050", "0056"],
        "weights": {
          "0050": 45.5,
          "0056": 8.2
        }
      },
      ...
    ],
    "overlap_ratio": 0.65  // 重疊率
  }
}
```

#### 5. 使用者功能

```javascript
// 取得自選清單
GET /api/v1/user/watchlist
Headers:
  Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": {
    "etfs": ["0050", "0056"],
    "stocks": ["2330", "2317"]
  }
}

// 新增到自選
POST /api/v1/user/watchlist
Body:
{
  "type": "ETF",  // ETF or STOCK
  "code": "0050"
}

// 移除自選
DELETE /api/v1/user/watchlist/:type/:code
```

---

## 📱 React Native App 設計

### 頁面結構

```
App
├── 首頁 (HomeScreen)
│   ├── 統計卡片（ETF 總數、熱門股票等）
│   ├── 我的自選
│   └── 最近瀏覽
│
├── ETF 列表 (ETFListScreen)
│   ├── 搜尋欄
│   ├── 篩選器（發行商、類型）
│   └── ETF 卡片列表
│
├── ETF 詳情 (ETFDetailScreen)
│   ├── ETF 基本資訊
│   ├── 淨值走勢圖
│   ├── 持股明細表格
│   └── 相似 ETF 推薦
│
├── 個股詳情 (StockDetailScreen)
│   ├── 股價資訊
│   ├── K 線圖
│   ├── 技術指標
│   └── 被哪些 ETF 持有
│
├── 自選清單 (WatchlistScreen)
│   ├── ETF 自選
│   └── 個股自選
│
└── 設定 (SettingsScreen)
    ├── 通知設定
    ├── 快取管理
    └── 關於
```

### 核心元件設計

```javascript
// ETFCard.js - ETF 卡片元件
<ETFCard
  code="0050"
  name="元大台灣50"
  nav={150.5}
  changePercent={1.2}
  onPress={() => navigation.navigate('ETFDetail', { code: '0050' })}
/>

// StockItem.js - 股票列表項目
<StockItem
  code="2330"
  name="台積電"
  price={600.0}
  changePercent={1.52}
  weight={45.5}
  onPress={() => navigation.navigate('StockDetail', { code: '2330' })}
/>

// PriceChart.js - 價格走勢圖
<PriceChart
  data={priceHistory}
  type="line"  // line, candlestick
  indicators={['MA5', 'MA20']}
/>

// HoldingTable.js - 持股明細表格
<HoldingTable
  holdings={etfHoldings}
  sortBy="weight"  // weight, market_value
  onStockPress={(code) => navigation.navigate('StockDetail', { code })}
/>
```

---

## 🔐 限流策略

### FinMind API 限流器

```python
# app/utils/rate_limiter.py

import time
from collections import deque
from threading import Lock

class FinMindRateLimiter:
    """
    FinMind API 限流器
    免費版：600 requests / hour
    """
    def __init__(self, max_requests=600, time_window=3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = Lock()

    def acquire(self):
        """
        取得請求許可
        若超過限制則等待
        """
        with self.lock:
            now = time.time()

            # 清理過期的請求記錄
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()

            # 檢查是否超過限制
            if len(self.requests) >= self.max_requests:
                # 計算需要等待的時間
                oldest = self.requests[0]
                wait_time = self.time_window - (now - oldest) + 1
                print(f"[RateLimiter] 達到限制，等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
                return self.acquire()  # 遞迴重試

            # 記錄本次請求
            self.requests.append(now)
            return True

    def get_remaining(self):
        """取得剩餘請求數"""
        with self.lock:
            now = time.time()
            # 清理過期記錄
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()
            return self.max_requests - len(self.requests)

# 全域實例
finmind_limiter = FinMindRateLimiter(max_requests=600, time_window=3600)
```

---

## 🎨 UI/UX 設計建議

### 設計風格

**參考對象**：
- Yahoo Finance (資訊密度)
- Robinhood (極簡美學)
- Trading 212 (互動體驗)

**色彩方案**：
```javascript
const colors = {
  primary: '#422AFB',      // 主色（紫色）
  secondary: '#7551FF',    // 次要色
  success: '#23A455',      // 上漲（綠色）
  danger: '#E31A1A',       // 下跌（紅色）
  background: '#F5F7FA',   // 背景色
  card: '#FFFFFF',         // 卡片背景
  text: '#1A202C',         // 主要文字
  textSecondary: '#718096' // 次要文字
};
```

### 關鍵 UX 優化

1. **骨架屏載入**：資料載入時顯示骨架屏
2. **下拉刷新**：支援手勢刷新資料
3. **無限滾動**：ETF 列表使用虛擬滾動
4. **快速操作**：長按加入自選、滑動查看更多
5. **離線提示**：網路斷線時顯示快取資料 + 提示
6. **搜尋優化**：即時搜尋 + 歷史記錄

---

## ⚡ 效能優化

### 1. API 優化

```javascript
// ❌ 避免：N+1 查詢問題
for (let etf of etfs) {
  const holdings = await api.getHoldings(etf.code);  // 100 次請求
}

// ✅ 優化：批次查詢
const etfCodes = etfs.map(e => e.code);
const allHoldings = await api.getBatchHoldings(etfCodes);  // 1 次請求
```

### 2. App 端優化

```javascript
// 使用 React.memo 避免不必要的重渲染
const ETFCard = React.memo(({ code, name, nav, changePercent }) => {
  return (
    <View>
      <Text>{name}</Text>
      <Text>{nav}</Text>
    </View>
  );
});

// 使用 FlatList 的優化 props
<FlatList
  data={etfs}
  renderItem={renderItem}
  keyExtractor={(item) => item.code}
  initialNumToRender={10}
  maxToRenderPerBatch={10}
  windowSize={5}
  removeClippedSubviews={true}  // Android 優化
  getItemLayout={getItemLayout}  // 固定高度優化
/>
```

### 3. 圖片優化

```javascript
// 使用 Fast Image
import FastImage from 'react-native-fast-image';

<FastImage
  source={{ uri: logoUrl }}
  style={{ width: 40, height: 40 }}
  resizeMode={FastImage.resizeMode.contain}
/>
```

---

## 🧪 測試策略

### 後端測試

```python
# tests/test_api.py
def test_get_etf_list():
    response = client.get('/api/v1/etfs')
    assert response.status_code == 200
    assert 'data' in response.json

def test_cache_hit():
    # 第一次請求
    response1 = client.get('/api/v1/etf/0050')
    # 第二次請求（應該從快取取得）
    response2 = client.get('/api/v1/etf/0050')
    assert response1.json == response2.json
```

### App 測試

```javascript
// __tests__/ETFListScreen.test.js
import { render, waitFor } from '@testing-library/react-native';

test('loads and displays ETF list', async () => {
  const { getByText } = render(<ETFListScreen />);

  await waitFor(() => {
    expect(getByText('元大台灣50')).toBeTruthy();
  });
});
```

---

## 📦 部署方案

### 後端部署

**選項 A：Heroku (最簡單)**
```bash
heroku create your-app
heroku addons:create heroku-redis:hobby-dev
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**選項 B：AWS (較彈性)**
- EC2: Flask App
- ElastiCache: Redis
- RDS: PostgreSQL
- CloudWatch: 監控

**選項 C：Docker + VPS (最省錢)**
```bash
docker-compose up -d
# 包含 Flask + Redis + PostgreSQL
```

### App 部署

**iOS TestFlight**
```bash
cd mobile
npx react-native bundle --platform ios
# 使用 Xcode 打包上傳
```

---

## 💰 成本估算

| 項目 | 免費方案 | 付費方案 |
|------|---------|---------|
| FinMind API | 免費 (600 req/hr) | $0 |
| 後端伺服器 | Heroku Free / GCP Free Tier | ~$5/月 |
| Redis | Redis Cloud Free (30MB) | $0-10/月 |
| PostgreSQL | Heroku Hobby ($0) | $0-10/月 |
| **總計** | **$0/月** | **$5-25/月** |

---

## 🎯 開發里程碑

### 第 1 週：後端重構
- [ ] 建立新的 Flask 專案結構
- [ ] 整合 FinMind API 客戶端
- [ ] 實作 Redis 快取層
- [ ] 建立 PostgreSQL 資料表
- [ ] 實作核心 API (ETF, Stock)

### 第 2 週：定時任務 & 測試
- [ ] 實作 APScheduler 定時任務
- [ ] 實作限流器
- [ ] 撰寫單元測試
- [ ] 測試快取機制
- [ ] 部署到測試環境

### 第 3 週：React Native App 基礎
- [ ] 建立 React Native 專案
- [ ] 實作基礎路由與導航
- [ ] 實作 ETF 列表頁面
- [ ] 實作 ETF 詳情頁面
- [ ] 整合後端 API

### 第 4 週：App 進階功能
- [ ] 實作個股詳情頁面
- [ ] 實作自選清單功能
- [ ] 實作本地快取 (SQLite)
- [ ] 實作價格圖表
- [ ] UI/UX 優化

### 第 5 週：測試 & 上線
- [ ] App 功能測試
- [ ] 效能優化
- [ ] 撰寫文件
- [ ] TestFlight 內測
- [ ] App Store 上架

---

## 📚 技術棧總結

### 後端
- **語言**: Python 3.11+
- **框架**: Flask 3.x
- **快取**: Redis 7.x
- **資料庫**: PostgreSQL 15
- **任務排程**: APScheduler
- **資料來源**: FinMind API

### 前端
- **框架**: React Native 0.73+
- **語言**: JavaScript / TypeScript
- **狀態管理**: Zustand / Redux Toolkit
- **路由**: React Navigation 6
- **圖表**: react-native-chart-kit
- **本地儲存**: AsyncStorage + SQLite

### 開發工具
- **版本控制**: Git + GitHub
- **API 測試**: Postman / Thunder Client
- **除錯**: React Native Debugger
- **部署**: Docker + GitHub Actions

---

## 🎉 預期成果

完成後你將擁有：

1. ✅ **完整的 iOS App**
   - 300+ 台股 ETF 資訊
   - 個股價格與技術分析
   - 自選清單功能
   - 離線瀏覽支援

2. ✅ **高效能後端**
   - 多層快取架構
   - 自動定時更新
   - API 限流保護
   - 完全使用免費方案

3. ✅ **零維護成本**
   - 不需要維護爬蟲
   - 資料自動更新
   - 錯誤自動重試

4. ✅ **可擴展架構**
   - 易於新增功能
   - 支援 Android
   - 支援 Web 版

---

**準備好開始了嗎？讓我們開始實作吧！** 🚀
