# 🚀 完整設定指南 - 從零到部署

> **從環境準備到生產部署的完整教學**

---

## 📋 目錄

1. [環境準備](#環境準備)
2. [本地開發設定](#本地開發設定)
3. [Docker 容器化](#docker-容器化)
4. [本地測試](#本地測試)
5. [部署方案比較](#部署方案比較)
6. [生產部署](#生產部署)
7. [Mobile App 開發](#mobile-app-開發)
8. [常見問題](#常見問題)

---

## 🔧 環境準備

### 必須安裝的軟體

#### 1. Python 3.11+

```bash
# macOS (使用 Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Windows
# 從 https://www.python.org/downloads/ 下載安裝

# 驗證安裝
python3 --version  # 應該顯示 3.11.x
```

#### 2. Node.js 18+ (用於 Mobile App)

```bash
# macOS
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# 從 https://nodejs.org/ 下載安裝

# 驗證安裝
node --version  # 應該顯示 v18.x.x
npm --version
```

#### 3. Git

```bash
# macOS
brew install git

# Ubuntu/Debian
sudo apt install git

# 驗證安裝
git --version
```

#### 4. Redis (本地開發用)

**選項 A: 使用 Docker (推薦)**

```bash
# 安裝 Docker Desktop
# macOS: https://docs.docker.com/desktop/install/mac-install/
# Windows: https://docs.docker.com/desktop/install/windows-install/
# Linux: https://docs.docker.com/engine/install/

# 啟動 Redis 容器
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 驗證
docker ps  # 應該看到 redis 容器運行中
```

**選項 B: 直接安裝 Redis**

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# 驗證
redis-cli ping  # 應該返回 PONG
```

---

## 💻 本地開發設定

### 1. Clone 專案

```bash
git clone https://github.com/your-username/twETFHoldings.git
cd twETFHoldings
```

### 2. 後端設定

#### 2.1 建立虛擬環境

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 確認虛擬環境已啟動 (命令提示符前面會有 (venv))
```

#### 2.2 安裝依賴

```bash
# 安裝所有 Python 套件
pip install -r requirements.txt

# 確認安裝成功
pip list | grep Flask  # 應該看到 Flask 3.1.2
```

#### 2.3 設定環境變數

```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案
nano .env  # 或使用任何文字編輯器
```

```.env
# .env 內容

# FinMind API Token (選填，但建議註冊取得)
# 註冊網址: https://finmindtrade.com/
FINMIND_TOKEN=your_token_here_or_leave_empty

# Redis 連線 (本地開發)
REDIS_URL=redis://localhost:6379/0

# Flask 環境
FLASK_ENV=development
FLASK_DEBUG=1

# 密鑰 (開發環境可以隨意設定)
SECRET_KEY=dev-secret-key-change-in-production

# 資料庫 (使用 SQLite)
DATABASE_URL=sqlite:///etf_app.db

# 排程器開關
SCHEDULER_ENABLED=true

# 日誌級別
LOG_LEVEL=INFO
```

#### 2.4 啟動後端

##### 方法 1: 使用便捷腳本（推薦）

```bash
# 使用智能啟動腳本（自動處理端口衝突）
./run_dev.sh
```

這個腳本會：
- ✅ 自動檢查虛擬環境
- ✅ 自動檢查 Redis 連接
- ✅ 自動處理 macOS AirPlay 端口衝突
- ✅ 啟用熱重載

##### 方法 2: 手動啟動

```bash
# 確保 Redis 正在運行
docker ps  # 或 redis-cli ping

# 啟動 Flask 開發伺服器
python -m flask --app backend.main run

# 或使用以下命令啟用熱重載
python -m flask --app backend.main run --reload

# 預期輸出:
# * Running on http://127.0.0.1:5001
# * Restarting with stat
# * Debugger is active!
```

##### ⚠️ macOS 用戶特別注意

**如果遇到 403 Forbidden 錯誤**，這是因為 macOS Monterey (12.0) 及以上版本的 **AirPlay Receiver** 佔用了 5000 端口。

**快速解決方案：**

1. **關閉 AirPlay Receiver（推薦）**
   - 打開 **系統設定** (System Settings)
   - 前往 **通用** > **AirDrop 與接續互通**
   - 關閉 **AirPlay Receiver**
   - 重新啟動 Flask

2. **使用便捷腳本**
   ```bash
   ./run_dev.sh
   ```
   腳本會自動偵測端口衝突並提示解決方案

3. **查看完整說明**
   ```bash
   # 詳細的端口衝突解決方案
   cat docs/MACOS_PORT_5000_FIX.md
   ```

#### 2.5 驗證後端運行

```bash
# 開啟新的終端視窗

# 測試健康檢查
curl http://localhost:5001/health

# 預期回應:
# {
#   "status": "healthy",
#   "services": {
#     "redis": "connected",
#     "finmind": "connected"
#   }
# }

# 測試 API 端點
curl http://localhost:5001/api/v1/etf/etfs?limit=5 | jq

# 查看 Swagger API 文件（正確路徑）
open http://localhost:5001/api/v1/
# 注意：Swagger 文件在 /api/v1/ 而不是 /docs/
```

---

## 🐳 Docker 容器化

### 為什麼使用 Docker?

- ✅ 環境一致性 (開發 = 生產)
- ✅ 簡化部署流程
- ✅ 隔離依賴
- ✅ 易於擴展

### 使用 Docker Compose (推薦)

#### 1. 確認 Docker 已安裝

```bash
docker --version
docker-compose --version
```

#### 2. 查看專案的 Docker 配置

**Dockerfile** (已包含在專案中):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "backend.main:app"]
```

**docker-compose.yml** (已包含在專案中):
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=development
      - REDIS_URL=redis://redis:6379/0
      - FINMIND_TOKEN=${FINMIND_TOKEN}
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

#### 3. 啟動 Docker 容器

```bash
# 建置並啟動所有服務
docker-compose up -d

# 查看運行狀態
docker-compose ps

# 預期輸出:
# NAME                COMMAND                  SERVICE     STATUS      PORTS
# twetfholdings-backend-1   "gunicorn..."      backend     Up          0.0.0.0:5000->5000/tcp
# twetfholdings-redis-1     "redis-server"     redis       Up          0.0.0.0:6379->6379/tcp

# 查看日誌
docker-compose logs -f backend

# 測試
curl http://localhost:5001/health
```

#### 4. Docker 常用命令

```bash
# 停止所有容器
docker-compose down

# 停止並刪除所有資料
docker-compose down -v

# 重新建置
docker-compose build

# 重啟服務
docker-compose restart

# 進入容器內部
docker-compose exec backend bash

# 查看容器日誌
docker-compose logs -f
```

---

## 🧪 本地測試

### 1. 測試 FinMind API

```bash
# 進入 examples 目錄
cd examples

# 執行測試腳本
python finmind_example.py

# 預期輸出:
# ✅ 找到 300+ 個 ETF
# ✅ 取得 0050 持股明細
# ✅ 取得 2330 股價
```

### 2. 測試後端 API

#### 使用 curl

```bash
# 1. 健康檢查
curl http://localhost:5001/health | jq

# 2. 取得 ETF 列表
curl http://localhost:5001/api/v1/etf/etfs?limit=10 | jq

# 3. 取得 ETF 詳情
curl http://localhost:5001/api/v1/etf/etf/0050 | jq

# 4. 取得 ETF 持股
curl "http://localhost:5001/api/v1/etf/etf/0050/holdings?enrich_prices=true" | jq

# 5. 取得個股價格
curl http://localhost:5001/api/v1/stock/2330 | jq

# 6. 搜尋
curl "http://localhost:5001/api/v1/search?q=台積電" | jq
```

#### 使用 Python

```python
# test_api.py
import requests

BASE_URL = "http://localhost:5001/api/v1"

# 1. 測試 ETF 列表
response = requests.get(f"{BASE_URL}/etf/etfs", params={"limit": 5})
print("ETF 列表:", response.json())

# 2. 測試 ETF 詳情
response = requests.get(f"{BASE_URL}/etf/etf/0050")
print("0050 詳情:", response.json())

# 3. 測試持股
response = requests.get(
    f"{BASE_URL}/etf/etf/0050/holdings",
    params={"enrich_prices": True}
)
print("0050 持股:", response.json())
```

#### 使用 Postman

1. 下載 Postman: https://www.postman.com/downloads/
2. 導入 API Collection (可以自己建立或使用 Swagger)
3. 設定 Base URL: `http://localhost:5001/api/v1`
4. 測試各個端點

### 3. 測試快取功能

```bash
# 第一次請求 (會呼叫 FinMind API)
time curl http://localhost:5001/api/v1/etf/etf/0050

# 第二次請求 (應該從快取返回，速度更快)
time curl http://localhost:5001/api/v1/etf/etf/0050

# 查看 Redis 快取
redis-cli
> KEYS *
> GET etf_detail_0050
> TTL etf_detail_0050  # 查看剩餘過期時間
```

### 4. 測試定時任務

```bash
# 手動觸發定時任務
python -c "from backend.tasks.scheduler import update_etf_list; update_etf_list()"

# 查看日誌
# 應該看到類似輸出:
# [定時任務] 開始更新 ETF 清單
# [定時任務] ETF 清單更新完成: 300+ 個
```

---

## 📊 部署方案完整比較

### 方案總覽

| 平台 | 免費額度 | 價格 | 適合場景 | 多APP共用 | 推薦度 |
|------|---------|------|---------|----------|--------|
| **Railway** | $5/月 | $20+/月 | 個人專案 | ✅ 優秀 | ⭐⭐⭐⭐⭐ |
| **Render** | 完全免費 | $7+/月 | 測試/學習 | ⚠️ 有限 | ⭐⭐⭐⭐ |
| **Fly.io** | $0 | $10+/月 | 高效能 | ✅ 優秀 | ⭐⭐⭐⭐ |
| **Heroku** | $0 | $25+/月 | 企業級 | ✅ 優秀 | ⭐⭐⭐ |
| **Google Cloud Run** | $0 | 按量計費 | 彈性擴展 | ✅ 最佳 | ⭐⭐⭐⭐⭐ |
| **AWS Elastic Beanstalk** | 12個月 | $20+/月 | 企業級 | ✅ 最佳 | ⭐⭐⭐ |
| **Vercel** | 免費 | $20+/月 | 前端優先 | ⚠️ 不適合 | ⭐⭐ |

---

### 1️⃣ Railway (最推薦)

#### 優點
- ✅ **$5/月免費額度** (500 小時/月)
- ✅ **簡單易用** - GitHub 整合，自動部署
- ✅ **完整服務** - 包含 Redis、PostgreSQL
- ✅ **多專案支援** - 一個帳號可以跑多個 APP
- ✅ **即時日誌** - 方便除錯
- ✅ **自訂網域** - 免費 SSL

#### 缺點
- ❌ 免費額度有限 (500 小時 ≈ 20.8 天)
- ❌ 超過免費額度後按量計費

#### 成本計算

| 資源 | 用量 | 費用 |
|------|------|------|
| **後端 (1個)** | 24/7 運行 | $5/月 (免費額度) |
| **Redis** | 25MB | $0/月 (免費額度) |
| **總計** | - | **$0-5/月** |

**如果有多個 APP**:
- APP 1: 台股 ETF (500 小時免費)
- APP 2: 其他專案 (需付費，約 $5-10/月)
- **總計**: $5-15/月

#### 部署步驟

```bash
# 1. 註冊 Railway
open https://railway.app/

# 2. 連接 GitHub
# 在 Railway Dashboard 點擊 "New Project" → "Deploy from GitHub repo"

# 3. 選擇專案
# 選擇 twETFHoldings 專案

# 4. 配置環境變數
# 在 Railway Dashboard 設定:
FINMIND_TOKEN=your_token_here
REDIS_URL=<Railway 會自動提供>

# 5. 部署
# Railway 會自動偵測 Dockerfile 並部署

# 6. 查看 URL
# 部署完成後，Railway 會提供一個 URL
# 例如: https://twetfholdings.up.railway.app
```

---

### 2️⃣ Render (完全免費)

#### 優點
- ✅ **完全免費** - 無需信用卡
- ✅ **簡單易用** - GitHub 整合
- ✅ **免費 SSL** - HTTPS 支援
- ✅ **PostgreSQL** - 免費 90 天

#### 缺點
- ❌ **會休眠** - 15 分鐘無請求後休眠
- ❌ **冷啟動慢** - 休眠後首次請求需要 30-60 秒
- ❌ **效能較差** - 免費方案資源有限
- ❌ **多 APP 不方便** - 每個 APP 需要獨立部署

#### 成本計算

| 資源 | 用量 | 費用 |
|------|------|------|
| **後端** | 自動休眠 | **$0/月** |
| **Redis** | 需付費 | $7/月起 |
| **PostgreSQL** | 免費 90 天 | $0/月 (之後 $7/月) |

**如果有多個 APP**:
- 每個 APP 都可以免費部署
- 但需要共用 Redis (付費)
- **總計**: $0-7/月 (不含 Redis)

#### 適合場景
- ✅ 測試環境
- ✅ 學習專案
- ✅ 低流量個人專案
- ❌ 生產環境 (因為會休眠)

---

### 3️⃣ Fly.io (高效能)

#### 優點
- ✅ **全球 CDN** - 自動部署到最近的節點
- ✅ **效能優秀** - 接近 VPS 的效能
- ✅ **免費額度** - 3 個共享 CPU VM
- ✅ **多 APP 支援** - 方便管理多個專案

#### 缺點
- ❌ **配置複雜** - 需要學習 fly.toml
- ❌ **帳單不透明** - 容易超過免費額度

#### 成本計算

| 資源 | 免費額度 | 超過後 |
|------|---------|--------|
| **VM** | 3 個 shared-cpu-1x | $1.94/月起 |
| **流量** | 100GB/月 | $0.02/GB |
| **總計** | $0/月 | $10-20/月 |

**多 APP**:
- 可以部署多個 APP
- 但共用 3 個免費 VM 配額
- **總計**: $0-30/月

#### 部署步驟

```bash
# 1. 安裝 Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. 登入
fly auth login

# 3. 初始化專案
fly launch

# 4. 部署
fly deploy

# 5. 設定環境變數
fly secrets set FINMIND_TOKEN=your_token_here

# 6. 查看狀態
fly status
```

---

### 4️⃣ Google Cloud Run (彈性擴展)

#### 優點
- ✅ **按量計費** - 只在有請求時收費
- ✅ **自動擴展** - 0 到 N 個實例
- ✅ **免費額度** - 200萬請求/月
- ✅ **GCP 生態系** - 整合其他 Google 服務
- ✅ **多 APP 完美** - 每個 APP 獨立計費

#### 缺點
- ❌ **冷啟動** - 首次請求較慢
- ❌ **配置複雜** - 需要學習 GCP
- ❌ **需要信用卡** - 即使使用免費額度

#### 成本計算

| 資源 | 免費額度 | 超過後 |
|------|---------|--------|
| **請求數** | 200萬/月 | $0.40/百萬 |
| **CPU 時間** | 18萬 vCPU-秒/月 | $0.00002400/vCPU-秒 |
| **記憶體** | 36萬 GiB-秒/月 | $0.00000250/GiB-秒 |
| **總計** | $0/月 | $5-20/月 |

**多 APP**:
- 完美支援多個 APP
- 每個 APP 獨立計費
- 共用免費額度
- **總計**: $0-50/月 (取決於流量)

#### 部署步驟

```bash
# 1. 安裝 gcloud CLI
# 參考: https://cloud.google.com/sdk/docs/install

# 2. 初始化
gcloud init

# 3. 設定專案
gcloud config set project YOUR_PROJECT_ID

# 4. 部署
gcloud run deploy twetf-api \
  --source . \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars FINMIND_TOKEN=your_token_here

# 5. 查看 URL
gcloud run services describe twetf-api --region asia-east1
```

---

### 🏆 最終推薦

#### 場景 1: 個人專案 (< 100 用戶/天)

**推薦**: Railway

- 成本: $0-5/月
- 優點: 簡單、穩定、足夠用
- 多 APP: 可以跑 1-2 個 APP

#### 場景 2: 測試/學習

**推薦**: Render

- 成本: $0/月
- 優點: 完全免費
- 缺點: 會休眠，不適合生產

#### 場景 3: 多個 APP (2-5 個)

**推薦**: Google Cloud Run

- 成本: $0-30/月
- 優點: 按量計費，自動擴展
- 完美支援多 APP

#### 場景 4: 高流量 (> 1000 用戶/天)

**推薦**: Fly.io 或 Google Cloud Run

- 成本: $20-50/月
- 優點: 效能好，自動擴展
- 適合生產環境

---

## 🚀 生產部署 (Railway 示範)

### 1. 準備部署

```bash
# 1. 確保所有變更已提交
git status
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. 檢查 Docker 配置
docker-compose build
docker-compose up -d
curl http://localhost:5001/health

# 3. 停止本地容器
docker-compose down
```

### 2. 部署到 Railway

#### 步驟 1: 建立專案

1. 前往 https://railway.app/
2. 點擊 "New Project"
3. 選擇 "Deploy from GitHub repo"
4. 授權 Railway 存取您的 GitHub
5. 選擇 `twETFHoldings` 專案

#### 步驟 2: 添加 Redis

1. 在專案中點擊 "New"
2. 選擇 "Database" → "Redis"
3. Railway 會自動建立 Redis 實例
4. 複製 `REDIS_URL`

#### 步驟 3: 配置環境變數

在 Railway Dashboard 的 Variables 標籤：

```bash
FINMIND_TOKEN=your_token_here
REDIS_URL=<Railway 自動提供>
FLASK_ENV=production
SECRET_KEY=<生成一個強密碼>
SCHEDULER_ENABLED=true
```

生成強密碼：
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### 步驟 4: 部署

Railway 會自動：
1. 偵測 Dockerfile
2. 建置 Docker 映像
3. 部署到雲端
4. 提供 HTTPS URL

#### 步驟 5: 驗證部署

```bash
# 取得部署 URL (例如: https://twetfholdings.up.railway.app)
DEPLOY_URL="https://your-app.up.railway.app"

# 測試健康檢查
curl $DEPLOY_URL/health | jq

# 測試 API
curl "$DEPLOY_URL/api/v1/etf/etfs?limit=5" | jq
```

#### 步驟 6: 設定自訂網域 (選填)

1. 在 Railway Dashboard 點擊 "Settings"
2. 找到 "Domains" 區塊
3. 點擊 "Add Domain"
4. 輸入您的網域 (例如: api.yourdomain.com)
5. 設定 DNS CNAME 記錄
6. 等待 SSL 證書生成

---

## 📱 Mobile App 開發

### 1. 安裝 Expo CLI

```bash
npm install -g expo-cli
```

### 2. 進入 Mobile 專案

```bash
cd mobile/tw-etf-app
```

### 3. 安裝依賴

```bash
npm install
```

### 4. 設定 API 端點

編輯 `services/api.ts`:

```typescript
const API_CONFIG = {
  DEV_URL: 'http://localhost:5001/api/v1',
  PROD_URL: 'https://your-app.up.railway.app/api/v1',  // 替換為您的 Railway URL
};
```

或使用環境變數：

```bash
# .env
EXPO_PUBLIC_API_URL=https://your-app.up.railway.app/api/v1
```

### 5. 啟動開發

```bash
npx expo start
```

### 6. 測試

- 按 `i` 開啟 iOS Simulator
- 按 `a` 開啟 Android Emulator
- 掃描 QR Code 在實體手機上測試

---

## ❓ 常見問題

### Q1: FinMind API 呼叫失敗怎麼辦？

```bash
# 檢查 Token 是否正確
echo $FINMIND_TOKEN

# 測試 API 連接
curl "https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockInfo"

# 查看後端日誌
docker-compose logs backend | grep FinMind
```

### Q2: Redis 連接失敗？

```bash
# 檢查 Redis 是否運行
docker ps | grep redis

# 測試 Redis 連接
redis-cli ping  # 應該返回 PONG

# 重啟 Redis
docker-compose restart redis
```

### Q3: 部署後 API 回應慢？

可能原因：
1. **FinMind API 速率限制** - 檢查是否超過 600 req/hour
2. **快取未命中** - 等待快取預熱
3. **冷啟動** - Render 免費方案會休眠

解決方案：
```bash
# 1. 增加快取時間
# 編輯 backend/config.py
CACHE_TTL = {
    'ETF_LIST': 86400,      # 24 小時
    'STOCK_PRICE': 3600,    # 1 小時
}

# 2. 使用定時任務預載資料
# 已經實作在 backend/tasks/scheduler.py

# 3. 升級到付費方案 (Render: $7/月)
```

### Q4: 如何監控 API 使用量？

```python
# 添加到 backend/services/finmind.py

class FinMindRateLimiter:
    def log_usage(self):
        logger.info(f"今日 API 使用量: {len(self.requests)}")

        # 儲存到檔案
        with open('api_usage.log', 'a') as f:
            f.write(f"{datetime.now()}: {len(self.requests)} requests\n")
```

### Q5: 如何備份資料？

```bash
# Redis 備份
docker exec redis redis-cli SAVE
docker cp redis:/data/dump.rdb ./backup/

# 還原
docker cp ./backup/dump.rdb redis:/data/
docker restart redis
```

### Q6: Mobile App 無法連接後端？

檢查清單：
- [ ] 後端是否正在運行？
- [ ] API URL 是否正確？
- [ ] CORS 是否已啟用？
- [ ] 防火牆是否阻擋？

```bash
# 測試連接
curl https://your-api.com/health

# 檢查 CORS
# backend/extensions.py 應該有:
cors = CORS(origins=["*"])  # 開發環境
# cors = CORS(origins=["https://yourdomain.com"])  # 生產環境
```

---

## 📚 下一步

- [ ] 閱讀 [FinMind 額度分析](./FINMIND_QUOTA_ANALYSIS.md)
- [ ] 參考 [Mobile App 開發指南](./MOBILE_APP_GUIDE.md)
- [ ] 查看 [架構設計文件](./ARCHITECTURE_DESIGN.md)
- [ ] 學習 [部署指南](./DEPLOYMENT_GUIDE.md)

---

**最後更新**: 2025-11-10
**適用版本**: v2.0.0+
