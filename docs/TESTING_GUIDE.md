# 完整測試教學文件

從零開始測試整個後端系統的完整指南。

---

## 📋 目錄

1. [環境準備](#環境準備)
2. [安裝依賴](#安裝依賴)
3. [配置環境變數](#配置環境變數)
4. [啟動 Redis](#啟動-redis)
5. [啟動後端服務](#啟動後端服務)
6. [測試 API](#測試-api)
7. [使用 Docker 測試](#使用-docker-測試)
8. [常見問題](#常見問題)

---

## 環境準備

### 必要軟體

請確保以下軟體已安裝：

#### 1. Python 3.11+

```bash
# macOS (使用 Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# Windows
# 前往 https://www.python.org/downloads/ 下載安裝

# 驗證安裝
python3 --version  # 應顯示 Python 3.11.x
```

#### 2. Git

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt-get install git

# 驗證
git --version
```

#### 3. Redis (選擇其一)

**選項 A: 本地安裝**

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# 驗證
redis-cli ping  # 應返回 PONG
```

**選項 B: Docker**

```bash
# 安裝 Docker Desktop
# macOS: https://docs.docker.com/desktop/install/mac-install/
# Windows: https://docs.docker.com/desktop/install/windows-install/

# 啟動 Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 驗證
docker ps  # 應看到 redis 容器運行中
```

**選項 C: 免費的 Redis Cloud (推薦用於測試)**

```bash
# 1. 前往 https://redis.com/try-free/
# 2. 註冊免費帳號（30MB 免費額度）
# 3. 建立資料庫並取得連接字串
# 格式: redis://default:password@redis-12345.cloud.redislabs.com:12345
```

---

## 安裝依賴

### Step 1: Clone 專案

```bash
# 如果還沒有 clone
git clone https://github.com/your-username/twETFHoldings.git
cd twETFHoldings
```

### Step 2: 建立虛擬環境

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 驗證（應看到 (venv) 前綴）
which python  # 應指向 venv 中的 python
```

### Step 3: 安裝 Python 套件

```bash
# 安裝所有依賴
pip install -r requirements.txt
pip install -r requirements_new.txt

# 安裝 gunicorn (生產環境用)
pip install gunicorn

# 驗證安裝
pip list | grep Flask
pip list | grep redis
pip list | grep APScheduler
```

**常見錯誤處理**：

```bash
# 如果安裝失敗，升級 pip
pip install --upgrade pip setuptools wheel

# 如果 psycopg2 安裝失敗（PostgreSQL 驅動）
# 使用二進制版本
pip install psycopg2-binary

# 如果在 M1/M2 Mac 上遇到問題
arch -arm64 pip install -r requirements.txt
```

---

## 配置環境變數

### Step 1: 複製環境變數範本

```bash
# 複製 .env.example 為 .env
cp .env.example .env

# 編輯 .env
nano .env  # 或使用任何文字編輯器
```

### Step 2: 設定必要變數

最低限度需要設定：

```bash
# .env 檔案內容

# FinMind API Token (必填)
FINMIND_TOKEN=your_finmind_token_here

# Redis URL (根據你的設定選擇一個)
# 本地 Redis
REDIS_URL=redis://localhost:6379/0

# 或 Redis Cloud
# REDIS_URL=redis://default:password@redis-12345.cloud.redislabs.com:12345

# Flask 環境
FLASK_ENV=development
FLASK_APP=app.main_new
```

### Step 3: 取得 FinMind Token

```bash
# 1. 前往 https://finmindtrade.com/
# 2. 點擊右上角「註冊」
# 3. 填寫資料並驗證 Email
# 4. 登入後點擊「API Token」
# 5. 複製 Token 並貼到 .env 檔案

# 範例：
FINMIND_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 4: 驗證環境變數

```bash
# 測試環境變數是否載入
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
print(f'FINMIND_TOKEN: {os.getenv(\"FINMIND_TOKEN\")[:20]}...')
print(f'REDIS_URL: {os.getenv(\"REDIS_URL\")}')
"

# 應該顯示你的配置
```

---

## 啟動 Redis

### 方法 A: 本地 Redis

```bash
# macOS (如果未自動啟動)
brew services start redis

# 驗證
redis-cli ping  # 應返回 PONG

# 查看連接狀態
redis-cli
> info server
> exit
```

### 方法 B: Docker Redis

```bash
# 啟動 Redis 容器
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# 驗證
docker logs redis  # 應看到 "Ready to accept connections"

# 測試連接
docker exec -it redis redis-cli ping
```

### 方法 C: Redis Cloud

不需要本地啟動，直接使用雲端服務。

---

## 啟動後端服務

### 方法 A: Flask 開發伺服器（推薦用於測試）

```bash
# 確保虛擬環境已啟動
source venv/bin/activate  # macOS/Linux

# 啟動服務
python3 -m flask --app app.main_new run

# 或使用環境變數
export FLASK_APP=app.main_new
flask run

# 應該看到：
# * Running on http://127.0.0.1:5001
# * Debug mode: on
```

### 方法 B: Gunicorn（生產模式）

```bash
# 安裝 gunicorn
pip install gunicorn

# 啟動服務
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app.main_new:app

# 應該看到：
# [INFO] Starting gunicorn 20.1.0
# [INFO] Listening at: http://0.0.0.0:5000
```

### 驗證服務啟動

```bash
# 在另一個終端機執行

# 測試 1: 健康檢查
curl http://localhost:5001/health

# 應該返回：
# {
#   "status": "healthy",
#   "services": {
#     "redis": "connected",
#     "finmind": "connected"
#   }
# }

# 測試 2: API 首頁
curl http://localhost:5001/

# 應該返回 JSON 格式的歡迎訊息

# 測試 3: API 文件
open http://localhost:5001/docs/  # macOS
# 或瀏覽器開啟 http://localhost:5001/docs/
```

---

## 測試 API

### 使用 curl 測試

#### 1. 取得 ETF 清單

```bash
curl http://localhost:5001/api/v1/etf/etfs | jq
```

**預期回應**：
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "items": [
      {
        "code": "0050",
        "name": "元大台灣50",
        "type": "ETF"
      },
      ...
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 300
    }
  }
}
```

#### 2. 取得 ETF 持股

```bash
curl http://localhost:5001/api/v1/etf/etf/0050/holdings | jq
```

#### 3. 取得個股價格

```bash
curl http://localhost:5001/api/v1/stock/2330 | jq
```

#### 4. 搜尋功能

```bash
curl "http://localhost:5001/api/v1/search?q=台積電" | jq
```

### 使用 Postman 測試

1. **下載 Postman**
   - https://www.postman.com/downloads/

2. **匯入 API Collection**

創建一個新的 Collection，加入以下請求：

```
GET http://localhost:5001/health
GET http://localhost:5001/api/v1/etf/etfs
GET http://localhost:5001/api/v1/etf/etf/0050
GET http://localhost:5001/api/v1/etf/etf/0050/holdings
GET http://localhost:5001/api/v1/stock/2330
GET http://localhost:5001/api/v1/stock/2330/history?period=30d
GET http://localhost:5001/api/v1/search?q=台積電
POST http://localhost:5001/api/v1/stock/batch
  Body: {"codes": ["2330", "2317", "2454"]}
```

3. **測試結果**

所有請求都應該返回 `200 OK` 和 `"success": true`。

### 使用 Python 測試

創建測試腳本 `test_api.py`：

```python
import requests
import json

BASE_URL = "http://localhost:5001/api/v1"

def test_health():
    """測試健康檢查"""
    response = requests.get("http://localhost:5001/health")
    print(f"健康檢查: {response.status_code}")
    print(json.dumps(response.json(), ensure_ascii=False, indent=2))

def test_etf_list():
    """測試 ETF 清單"""
    response = requests.get(f"{BASE_URL}/etf/etfs")
    data = response.json()
    print(f"\nETF 清單: {response.status_code}")
    print(f"找到 {len(data['data']['items'])} 個 ETF")

def test_etf_holdings():
    """測試 ETF 持股"""
    response = requests.get(f"{BASE_URL}/etf/etf/0050/holdings")
    data = response.json()
    print(f"\n0050 持股: {response.status_code}")
    if data['success']:
        holdings = data['data']['holdings']
        print(f"持股數量: {len(holdings)}")
        if holdings:
            print(f"第一筆: {holdings[0]}")

def test_stock_price():
    """測試個股價格"""
    response = requests.get(f"{BASE_URL}/stock/2330")
    data = response.json()
    print(f"\n台積電價格: {response.status_code}")
    print(json.dumps(data['data'], ensure_ascii=False, indent=2))

def test_search():
    """測試搜尋"""
    response = requests.get(f"{BASE_URL}/search?q=台積電")
    data = response.json()
    print(f"\n搜尋結果: {response.status_code}")
    print(f"找到 {data['data']['total']} 筆")

if __name__ == "__main__":
    print("開始測試 API...\n")
    test_health()
    test_etf_list()
    test_etf_holdings()
    test_stock_price()
    test_search()
    print("\n測試完成！")
```

執行測試：

```bash
python test_api.py
```

---

## 使用 Docker 測試

### Step 1: 建立 Docker 映像

```bash
# 確保在專案根目錄
cd twETFHoldings

# 建立映像
docker build -t etf-api .

# 驗證
docker images | grep etf-api
```

### Step 2: 使用 Docker Compose 啟動

```bash
# 啟動所有服務（Flask + Redis）
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f backend

# 測試 API
curl http://localhost:5001/health
```

### Step 3: 停止服務

```bash
# 停止服務
docker-compose down

# 停止並刪除數據
docker-compose down -v
```

---

## 常見問題

### 問題 1: FinMind API 返回 403

**錯誤訊息**：
```
FinMind API 錯誤: Forbidden
```

**解決方法**：
```bash
# 檢查 Token 是否正確
echo $FINMIND_TOKEN

# 重新取得 Token
# 1. 登入 https://finmindtrade.com/
# 2. 重新生成 Token
# 3. 更新 .env 檔案
```

### 問題 2: Redis 連接失敗

**錯誤訊息**：
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

**解決方法**：
```bash
# 檢查 Redis 是否運行
redis-cli ping

# 如果沒有回應，啟動 Redis
brew services start redis  # macOS
sudo systemctl start redis-server  # Linux
docker start redis  # Docker

# 如果還是失敗，檢查 .env 中的 REDIS_URL
```

### 問題 3: 端口已被占用

**錯誤訊息**：
```
OSError: [Errno 48] Address already in use
```

**解決方法**：
```bash
# 找出占用 5000 端口的程序
lsof -i:5000

# 終止該程序
kill -9 PID

# 或使用不同端口
export PORT=8000
flask run --port 8000
```

### 問題 4: 模組找不到

**錯誤訊息**：
```
ModuleNotFoundError: No module named 'redis'
```

**解決方法**：
```bash
# 確認虛擬環境已啟動
source venv/bin/activate

# 重新安裝依賴
pip install -r requirements.txt
pip install -r requirements_new.txt

# 驗證安裝
pip list | grep redis
```

### 問題 5: API 回應很慢

**可能原因**：
- FinMind API 回應慢
- Redis 快取未啟用

**解決方法**：
```bash
# 1. 檢查 Redis 是否運行
redis-cli ping

# 2. 檢查快取狀態
curl http://localhost:5001/health | jq '.services.redis'

# 3. 手動預載資料
python -c "
from app.services.finmind import FinMindClient
from app.services.cache import cache, CacheKeys, CacheTTL

client = FinMindClient()
etfs = client.get_all_etfs()
cache.set(CacheKeys.ETF_LIST, etfs, CacheTTL.DAY_1)
print(f'已快取 {len(etfs)} 個 ETF')
"
```

### 問題 6: 定時任務未運行

**解決方法**：
```bash
# 1. 檢查 SCHEDULER_ENABLED
grep SCHEDULER_ENABLED .env

# 2. 手動測試定時任務
python app/tasks/scheduler.py

# 3. 查看日誌
tail -f logs/scrape_run_*.log
```

---

## 效能測試

### 測試快取效能

```bash
# 第一次請求（應該較慢，從 FinMind 取得）
time curl http://localhost:5001/api/v1/etf/etfs > /dev/null

# 第二次請求（應該很快，從快取取得）
time curl http://localhost:5001/api/v1/etf/etfs > /dev/null

# 預期：第二次應該快 10 倍以上
```

### 測試 API 速率

```bash
# 安裝 Apache Bench
brew install httpd  # macOS
sudo apt-get install apache2-utils  # Linux

# 測試 100 個請求
ab -n 100 -c 10 http://localhost:5001/api/v1/etf/etfs

# 查看結果
# Requests per second: XX [#/sec]
```

---

## 下一步

測試成功後：

1. ✅ 閱讀 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 學習如何部署
2. ✅ 閱讀 [EXPO_INTEGRATION.md](./EXPO_INTEGRATION.md) 學習如何整合 React Native
3. ✅ 查看 API 文件：http://localhost:5001/docs/

---

## 附錄：完整測試清單

```bash
# 複製以下指令逐一執行

# 1. 健康檢查
curl http://localhost:5001/health

# 2. API 首頁
curl http://localhost:5001/

# 3. ETF 清單
curl http://localhost:5001/api/v1/etf/etfs | jq

# 4. 單一 ETF
curl http://localhost:5001/api/v1/etf/etf/0050 | jq

# 5. ETF 持股
curl http://localhost:5001/api/v1/etf/etf/0050/holdings | jq

# 6. 個股資訊
curl http://localhost:5001/api/v1/stock/2330 | jq

# 7. 個股歷史
curl http://localhost:5001/api/v1/stock/2330/history?period=30d | jq

# 8. 批次查詢
curl -X POST http://localhost:5001/api/v1/stock/batch \
  -H "Content-Type: application/json" \
  -d '{"codes": ["2330", "2317", "2454"]}' | jq

# 9. 搜尋
curl "http://localhost:5001/api/v1/search?q=台積電" | jq

# 10. 市場統計
curl http://localhost:5001/api/v1/stats/market | jq

# 如果所有測試都通過，恭喜！🎉
# 你的後端已經成功運行了
```

---

**測試完成！** 🎉

接下來請查看 [部署教學](./DEPLOYMENT_GUIDE.md) 學習如何將後端部署到雲端。
