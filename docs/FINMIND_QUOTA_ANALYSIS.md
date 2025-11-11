# FinMind API 免費額度分析與優化策略

## 📊 FinMind 免費方案限制

### 官方限制

| 項目 | 免費方案 |
|------|---------|
| **每小時請求數** | 600 requests/hour |
| **每日請求數** | 約 14,400 requests/day |
| **需要註冊** | 否（但建議註冊取得 Token）|
| **速率限制** | 10 requests/second |
| **資料延遲** | 即時 (T+0) |

**官方連結**: https://finmindtrade.com/

---

## 🧮 實際使用量估算

### 後端 API 請求分析

#### 情境 1: 輕度使用 (10 個活躍用戶/天)

| API 端點 | 請求頻率 | 快取時間 | 每日請求數 |
|---------|---------|---------|-----------|
| **ETF 列表** | 每 5 分鐘 | 5 min | 288/day |
| **ETF 持股 (20個熱門)** | 每 5 分鐘 | 5 min | 5,760/day (20 × 288) |
| **個股價格 (50個)** | 每 5 分鐘 | 5 min | 14,400/day (50 × 288) |
| **搜尋** | 用戶觸發 | 無快取 | ~200/day |
| **總計** | - | - | **~20,650/day** ❌ |

> ⚠️ **超過限制！** 需要優化策略

#### 情境 2: 優化後 (使用定時任務)

| 任務 | 執行頻率 | 每日請求數 |
|------|---------|-----------|
| **更新 ETF 列表** | 每日 14:00 | 1/day |
| **更新 100 個 ETF 持股** | 每日 14:30 | 100/day |
| **更新 50 個熱門股價** | 每日 14:30 | 50/day |
| **用戶即時查詢 (快取 15 分鐘)** | - | ~300/day |
| **總計** | - | **~451/day** ✅ |

> ✅ **遠低於限制！** 安全使用

---

## ✅ 推薦策略：定時任務 + 長快取

### 實作方案

#### 1. 定時任務排程 (APScheduler)

```python
# backend/tasks/scheduler.py

# 每日 14:00 更新 ETF 列表 (1 次請求)
scheduler.add_daily_job(update_etf_list, hour=14, minute=0)

# 每日 14:30 批次更新 ETF 持股 (100 次請求)
scheduler.add_daily_job(update_all_etf_holdings, hour=14, minute=30)

# 每日 14:30 批次更新熱門股價 (50 次請求)
scheduler.add_daily_job(update_popular_stock_prices, hour=14, minute=30)
```

**總計**: ~151 requests/day

#### 2. 快取策略

| 資料類型 | 快取時間 | 說明 |
|---------|---------|------|
| **ETF 列表** | 24 小時 | 每日更新一次即可 |
| **ETF 持股** | 24 小時 | 持股變動不大 |
| **個股價格** | 15 分鐘 | 即時性要求較高 |
| **搜尋結果** | 1 小時 | 降低重複搜尋 |

#### 3. 用戶即時查詢

```python
# 當用戶查詢 ETF 時
1. 先檢查 Redis 快取（15 分鐘）
2. 快取未過期 → 直接返回
3. 快取過期 → 呼叫 FinMind API
4. 儲存到 Redis

# 預估每日用戶查詢: ~300 次
# 其中 80% 命中快取 → 只有 60 次實際 API 請求
```

---

## 📈 擴展性分析

### 不同用戶量下的請求數

| 活躍用戶/天 | 定時任務 | 用戶查詢 (20% Miss) | 總請求數 | 是否安全 |
|-----------|---------|-------------------|---------|---------|
| **10 人** | 151 | 60 | **211** | ✅ 極度安全 |
| **50 人** | 151 | 300 | **451** | ✅ 安全 |
| **100 人** | 151 | 600 | **751** | ✅ 安全 |
| **500 人** | 151 | 3,000 | **3,151** | ✅ 安全 |
| **1,000 人** | 151 | 6,000 | **6,151** | ⚠️ 接近上限 |
| **5,000 人** | 151 | 30,000 | **30,151** | ❌ 超過限制 |

### 結論

- ✅ **500 人以下** - 免費額度完全足夠
- ⚠️ **500-1,000 人** - 需要優化快取策略
- ❌ **1,000 人以上** - 考慮付費方案或自建資料源

---

## 💡 進階優化技巧

### 1. 增加快取命中率

```python
# backend/services/cache.py

class CacheManager:
    def __init__(self):
        self.ttl = {
            'ETF_LIST': 86400,        # 24 小時
            'ETF_HOLDINGS': 86400,    # 24 小時
            'STOCK_PRICE': 900,       # 15 分鐘（原本 1 分鐘）
            'SEARCH': 3600,           # 1 小時
        }
```

### 2. 批次請求優化

```python
# 一次請求多個股票價格
codes = ['2330', '2317', '2454', '2308', '2303']
prices = client.get_batch_prices(codes)  # 1 次 API 請求
```

### 3. 預載熱門資料

```python
# 預先載入最常查詢的 20 個 ETF
POPULAR_ETFS = ['0050', '0056', '00878', '00881', ...]

for etf_code in POPULAR_ETFS:
    holdings = client.get_etf_holdings(etf_code)
    cache.set(f'etf_holdings:{etf_code}', holdings, ttl=86400)
```

### 4. 降級策略

```python
# 當接近限制時，自動降級
if request_count > 500:
    # 增加快取時間到 1 小時
    cache.set(..., ttl=3600)
elif request_count > 800:
    # 只返回快取資料
    return cache.get(...) or "服務繁忙，請稍後再試"
```

---

## 🚀 監控與警報

### 1. 請求計數器

```python
# backend/services/finmind.py

class FinMindRateLimiter:
    def __init__(self):
        self.hourly_count = 0
        self.daily_count = 0

    def check_limit(self):
        if self.hourly_count >= 550:  # 90% 警戒線
            logger.warning("接近每小時限制！")
        if self.daily_count >= 13000:  # 90% 警戒線
            logger.warning("接近每日限制！")
```

### 2. 快取命中率監控

```python
# 記錄快取命中率
cache_hits = 0
cache_misses = 0
hit_rate = cache_hits / (cache_hits + cache_misses) * 100

logger.info(f"快取命中率: {hit_rate:.2f}%")
```

### 3. 使用 Sentry 監控

```python
import sentry_sdk

sentry_sdk.capture_message(
    f"FinMind API 使用量: {daily_count}/14400",
    level="warning"
)
```

---

## 💰 付費方案對比

### 當免費額度不夠時

| 方案 | 價格 | 請求限制 | 適用場景 |
|------|------|---------|---------|
| **免費** | $0 | 600/hour | < 500 活躍用戶 |
| **基礎** | $99/月 | 10,000/hour | 500-5,000 用戶 |
| **專業** | $299/月 | 50,000/hour | 5,000-20,000 用戶 |
| **企業** | 議價 | 無限制 | > 20,000 用戶 |

### 替代方案

1. **自建爬蟲** (不推薦)
   - 維護成本高
   - 容易被封鎖
   - 法律風險

2. **其他 API 服務**
   - Yahoo Finance API (免費但不穩定)
   - Alpha Vantage (免費 5 calls/min)
   - IEX Cloud (付費，更可靠)

3. **混合策略**
   - 使用 FinMind 作為主要來源
   - 用 Yahoo Finance 作為備援
   - 關鍵資料自行快取

---

## 📋 檢查清單

### 部署前確認

- [ ] 已設定 `FINMIND_TOKEN` 環境變數
- [ ] 已啟用 Redis 快取
- [ ] 已配置定時任務
- [ ] 已設定快取 TTL
- [ ] 已實作速率限制
- [ ] 已設定監控與警報
- [ ] 已測試快取命中率 (> 80%)

### 持續監控

- [ ] 每日檢查 API 使用量
- [ ] 監控快取命中率
- [ ] 追蹤錯誤率
- [ ] 定期檢視用戶增長

---

## 🎯 結論

### ✅ 免費額度足夠使用的情況

1. **使用定時任務** - 每日只需 ~150 次請求
2. **長時間快取** - ETF 資料 24 小時，股價 15 分鐘
3. **預載熱門資料** - 減少即時請求
4. **高快取命中率** - 目標 > 80%

**估算**: 在 **500 個活躍用戶**以下，免費額度綽綽有餘！

### ⚠️ 需要優化的信號

- 每日請求數 > 10,000
- 快取命中率 < 60%
- 頻繁觸發速率限制
- 用戶回報回應慢

### 📞 需要幫助？

- FinMind 官方文件: https://finmindtrade.com/document/
- 聯繫方式: support@finmindtrade.com
- GitHub Issues: 回報問題與建議

---

**最後更新**: 2025-11-10
**適用版本**: v2.0.0+
