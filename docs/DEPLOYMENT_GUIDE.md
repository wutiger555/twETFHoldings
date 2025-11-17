# 後端部署教學

最輕量、最現代化、最便宜的部署方案指南。

---

## 📋 目錄

1. [部署方案比較](#部署方案比較)
2. [方案 A: Railway (最推薦)](#方案-a-railway-最推薦)
3. [方案 B: Render](#方案-b-render)
4. [方案 C: Fly.io](#方案-c-flyio)
5. [部署後驗證](#部署後驗證)
6. [環境變數管理](#環境變數管理)
7. [常見問題](#常見問題)

---

## 部署方案比較

| 平台 | 免費額度 | 優點 | 缺點 | 推薦度 |
|------|---------|------|------|--------|
| **Railway** | $5 免費額度/月 | 最簡單、自動 HTTPS、支援 Redis | 需要信用卡 | ⭐⭐⭐⭐⭐ |
| **Render** | 完全免費 | 不需信用卡、自動部署 | 閒置會休眠、啟動慢 | ⭐⭐⭐⭐ |
| **Fly.io** | 3 個小型 VM 免費 | 效能好、全球節點 | 配置複雜 | ⭐⭐⭐ |
| **Heroku** | ❌ 已取消免費方案 | - | 需付費 | ❌ |

### 推薦選擇

- **個人開發/測試**: Railway（最簡單）
- **完全免費**: Render（可接受冷啟動）
- **需要效能**: Fly.io（需要一些技術知識）

---

## 方案 A: Railway (最推薦)

### 為什麼選擇 Railway？

- ✅ **超級簡單**: 只需點擊幾下
- ✅ **$5 免費額度**: 足夠小型專案使用一個月
- ✅ **內建 Redis**: 不需要額外設定
- ✅ **自動 HTTPS**: 免費 SSL 憑證
- ✅ **零配置部署**: 自動偵測 Dockerfile
- ✅ **即時日誌**: 方便除錯

### 成本估算

```
Flask 服務: ~$3/月 (512MB RAM)
Redis 服務: ~$1/月 (25MB)
總計: ~$4/月

免費額度: $5/月
✅ 完全免費！（有小額緩衝）
```

### 部署步驟

#### Step 1: 註冊 Railway

```bash
# 1. 前往 https://railway.app/
# 2. 點擊 "Start a New Project"
# 3. 使用 GitHub 登入（推薦）或 Email 註冊
# 4. 驗證 Email
```

#### Step 2: 連接 GitHub Repository

```bash
# 1. 推送程式碼到 GitHub
git add .
git commit -m "準備部署到 Railway"
git push origin main

# 2. 在 Railway 點擊 "Deploy from GitHub repo"
# 3. 選擇你的 repository: wutiger555/twETFHoldings
# 4. Railway 會自動偵測 Dockerfile
```

#### Step 3: 新增 Redis 服務

```bash
# 1. 在專案頁面點擊 "+ New"
# 2. 選擇 "Database" → "Add Redis"
# 3. Redis 會自動啟動並產生連接字串
# 4. Railway 會自動設定 REDIS_URL 環境變數
```

#### Step 4: 設定環境變數

在 Railway 專案設定中加入以下環境變數：

```bash
# Flask 設定
FLASK_ENV=production
FLASK_APP=app.main_new

# FinMind API
FINMIND_TOKEN=your_finmind_token_here

# Secret Key（產生方式見下方）
SECRET_KEY=your_secret_key_here

# 其他設定
SCHEDULER_ENABLED=true
LOG_LEVEL=INFO
```

**產生 SECRET_KEY**:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

#### Step 5: 部署

```bash
# Railway 會自動部署！
# 在部署設定中可以看到：
# 1. 建置 Docker 映像
# 2. 啟動容器
# 3. 執行健康檢查
# 4. 分配公開 URL

# 完成後會得到一個 URL：
# https://your-app-production.up.railway.app
```

#### Step 6: 設定自訂網域（可選）

```bash
# 1. 在 Railway 專案中點擊 "Settings"
# 2. 點擊 "Domains" → "Generate Domain"
# 3. 會得到免費的 railway.app 子網域

# 如果有自己的網域：
# 1. 點擊 "Custom Domain"
# 2. 輸入你的網域（如 api.yourapp.com）
# 3. 在 DNS 供應商加入 CNAME 記錄
# 4. 指向 Railway 提供的 URL
```

### Railway 特色功能

#### 1. 即時日誌

```bash
# 在 Railway Dashboard 中
# 點擊服務 → "Deploy Logs"
# 可以即時看到所有日誌
```

#### 2. 環境變數參照

```bash
# Redis URL 會自動注入
# 你可以參照其他服務的變數

# 例如：
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
```

#### 3. 自動重新部署

```bash
# 每次推送到 main 分支
# Railway 會自動重新部署

git add .
git commit -m "更新 API"
git push origin main
# 自動觸發部署！
```

---

## 方案 B: Render

### 為什麼選擇 Render？

- ✅ **完全免費**: 不需要信用卡
- ✅ **簡單易用**: Web 介面友善
- ✅ **自動 SSL**: 免費 HTTPS
- ✅ **自動部署**: Git 推送即部署
- ⚠️ **會休眠**: 15 分鐘無活動會休眠
- ⚠️ **啟動慢**: 冷啟動需要 30-60 秒

### 部署步驟

#### Step 1: 註冊 Render

```bash
# 1. 前往 https://render.com/
# 2. 點擊 "Get Started"
# 3. 使用 GitHub 登入
# 4. 授權 Render 存取你的 repositories
```

#### Step 2: 建立 Web Service

```bash
# 1. 在 Render Dashboard 點擊 "New +"
# 2. 選擇 "Web Service"
# 3. 連接你的 GitHub repository
# 4. 選擇 wutiger555/twETFHoldings
# 5. 填寫設定：
#    - Name: etf-api
#    - Region: Singapore (亞洲最近)
#    - Branch: main
#    - Runtime: Docker
#    - Plan: Free
```

#### Step 3: 建立 Redis

```bash
# 1. 回到 Dashboard，點擊 "New +"
# 2. 選擇 "Redis"
# 3. 填寫設定：
#    - Name: etf-redis
#    - Plan: Free (25MB)
# 4. 點擊 "Create Redis"
# 5. 複製 "Internal Redis URL"
```

#### Step 4: 設定環境變數

在 Web Service 的 "Environment" 頁面加入：

```bash
FLASK_ENV=production
FLASK_APP=app.main_new
FINMIND_TOKEN=your_token_here
SECRET_KEY=your_secret_key_here
REDIS_URL=redis://red-xxxxx:6379
SCHEDULER_ENABLED=true
```

#### Step 5: 部署

```bash
# Render 會自動開始部署
# 進度可在 "Events" 頁面查看

# 部署完成後會得到 URL：
# https://etf-api.onrender.com
```

### Render 注意事項

#### 免費方案限制

- ⚠️ **休眠機制**: 15 分鐘無請求會休眠
- ⚠️ **冷啟動**: 喚醒需要 30-60 秒
- ⚠️ **記憶體**: 512MB RAM
- ⚠️ **每月重啟**: 每月會強制重啟一次

#### 保持喚醒（可選）

使用免費的 Uptime 監控服務：

```bash
# 1. 註冊 UptimeRobot (https://uptimerobot.com)
# 2. 建立新監控
# 3. URL: https://your-app.onrender.com/health
# 4. 監控間隔: 5 分鐘
# 這樣你的服務就不會休眠！
```

#### 使用 render.yaml 自動部署

專案中已包含 `render.yaml`，可以一鍵部署：

```bash
# 1. 在 Render Dashboard 點擊 "New +"
# 2. 選擇 "Blueprint"
# 3. 連接 repository
# 4. Render 會自動讀取 render.yaml
# 5. 一次建立所有服務（Web + Redis）
```

---

## 方案 C: Fly.io

### 為什麼選擇 Fly.io？

- ✅ **效能好**: 真正的 VM，不會休眠
- ✅ **全球節點**: 可部署到多個區域
- ✅ **免費額度**: 3 個小型 VM
- ⚠️ **配置複雜**: 需要使用 CLI
- ⚠️ **需要信用卡**: 驗證身份用

### 快速部署

#### Step 1: 安裝 Fly CLI

```bash
# macOS/Linux
curl -L https://fly.io/install.sh | sh

# Windows (PowerShell)
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"

# 驗證安裝
flyctl version
```

#### Step 2: 登入 Fly.io

```bash
# 註冊或登入
flyctl auth signup  # 新用戶
flyctl auth login   # 現有用戶

# 驗證信用卡（不會扣款，只是驗證）
```

#### Step 3: 初始化專案

```bash
# 在專案目錄執行
flyctl launch

# CLI 會問你幾個問題：
# App name: etf-api（或自動產生）
# Region: Singapore (sin)
# PostgreSQL: No（我們不需要）
# Redis: Yes（選擇 Free plan）

# 會自動產生 fly.toml 配置檔
```

#### Step 4: 設定環境變數

```bash
# 設定 Secrets
flyctl secrets set FINMIND_TOKEN=your_token_here
flyctl secrets set SECRET_KEY=your_secret_key_here
flyctl secrets set FLASK_ENV=production

# Redis URL 會自動注入
```

#### Step 5: 部署

```bash
# 部署到 Fly.io
flyctl deploy

# 查看狀態
flyctl status

# 查看 URL
flyctl info
# 會得到：https://etf-api.fly.dev
```

#### Step 6: 管理

```bash
# 查看日誌
flyctl logs

# 擴展實例（免費可以有 3 個）
flyctl scale count 2

# 更改記憶體
flyctl scale memory 512  # MB

# SSH 進入容器
flyctl ssh console
```

---

## 部署後驗證

### 健康檢查

```bash
# 替換成你的 URL
curl https://your-app.railway.app/health | jq

# 預期回應
{
  "status": "healthy",
  "services": {
    "redis": "connected",
    "finmind": "connected"
  }
}
```

### API 測試

```bash
# 測試 ETF 清單
curl https://your-app.railway.app/api/v1/etf/etfs | jq

# 測試搜尋
curl "https://your-app.railway.app/api/v1/search?q=台積電" | jq

# 測試個股
curl https://your-app.railway.app/api/v1/stock/2330 | jq
```

### 效能測試

```bash
# 測試回應時間
time curl https://your-app.railway.app/health

# 第一次可能較慢（冷啟動）
# 之後應該 < 500ms
```

---

## 環境變數管理

### 必要環境變數

所有平台都需要以下變數：

```bash
# Flask
FLASK_ENV=production
FLASK_APP=app.main_new
SECRET_KEY=<random_secret>

# FinMind
FINMIND_TOKEN=<your_token>

# Redis
REDIS_URL=<auto_generated_or_custom>

# 可選
SCHEDULER_ENABLED=true
LOG_LEVEL=INFO
CORS_ORIGINS=*
```

### 產生 Secret Key

```bash
# Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32

# 線上工具
https://randomkeygen.com/
```

---

## 常見問題

### Q1: 哪個平台最便宜？

**答**: Render 完全免費，但有休眠限制。Railway $5/月額度通常用不完。

### Q2: 部署後 API 很慢？

**可能原因**:
1. Render 冷啟動（首次喚醒慢）
2. Redis 未連接（沒有快取）
3. FinMind API 延遲

**解決方法**:
```bash
# 1. 檢查 Redis
curl https://your-app/health | jq '.services.redis'

# 2. 設定 Uptime 監控（避免休眠）
# 3. 考慮升級到付費方案
```

### Q3: 如何查看日誌？

**Railway**:
```bash
# Web 介面: Dashboard → Service → Logs
# CLI: railway logs
```

**Render**:
```bash
# Web 介面: Dashboard → Service → Logs
```

**Fly.io**:
```bash
flyctl logs
```

### Q4: 如何更新部署？

**自動部署（推薦）**:
```bash
# 推送到 GitHub 會自動觸發
git add .
git commit -m "更新 API"
git push origin main
```

**手動部署**:
```bash
# Railway: 在 Dashboard 點擊 "Redeploy"
# Render: 點擊 "Manual Deploy"
# Fly.io: flyctl deploy
```

### Q5: 如何設定自訂網域？

**Railway**:
```
Settings → Domains → Custom Domain
```

**Render**:
```
Settings → Custom Domains → Add Custom Domain
```

**Fly.io**:
```bash
flyctl certs add yourdomain.com
```

然後在 DNS 供應商加入 CNAME 記錄。

### Q6: 資料庫怎麼辦？

**免費選項**:
1. **Railway PostgreSQL**: $5 額度內免費
2. **Supabase**: 500MB 免費
3. **PlanetScale**: 5GB 免費
4. **SQLite**: 用檔案儲存（簡單但有限制）

**推薦**: 先使用 SQLite，有需要再升級。

---

## 監控與維護

### 設定 Uptime 監控

使用 UptimeRobot (免費):

```bash
# 1. 註冊 https://uptimerobot.com
# 2. 建立新監控
#    - Monitor Type: HTTPS
#    - URL: https://your-app/health
#    - Monitoring Interval: 5 minutes
# 3. 設定通知（Email/Telegram）
```

### 設定錯誤追蹤

使用 Sentry (免費):

```bash
# 1. 註冊 https://sentry.io
# 2. 建立新專案
# 3. 取得 DSN
# 4. 安裝 SDK
pip install sentry-sdk[flask]

# 5. 在 app/main_new.py 加入
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

---

## 成本對比（月費）

| 方案 | Flask | Redis | 總計 | 備註 |
|------|-------|-------|------|------|
| **Railway** | $3 | $1 | **$4** | 有 $5 免費額度 ✅ |
| **Render** | $0 | $0 | **$0** | 會休眠 ⚠️ |
| **Fly.io** | $0 | $1 | **$1** | 需信用卡 |
| **Railway 付費** | $5 | $3 | **$8** | 更好的效能 |
| **Heroku** | $7 | $5 | **$12** | 不推薦 ❌ |

**推薦**:
- 預算 $0: Render
- 預算 $5: Railway（最佳選擇）
- 需要效能: Fly.io 或 Railway 付費

---

## 下一步

部署成功後：

1. ✅ 測試所有 API 端點
2. ✅ 設定 Uptime 監控
3. ✅ 閱讀 [EXPO_INTEGRATION.md](./EXPO_INTEGRATION.md)
4. ✅ 開始開發 React Native App！

---

## 附錄：部署檢查清單

```bash
# ✅ 部署前檢查
[ ] 程式碼已推送到 GitHub
[ ] .env.example 已建立
[ ] Dockerfile 可以正常建置
[ ] 本地測試通過

# ✅ 部署中檢查
[ ] 環境變數已設定
[ ] Redis 已連接
[ ] FinMind Token 有效
[ ] 建置成功

# ✅ 部署後檢查
[ ] /health 端點返回 healthy
[ ] API 文件可訪問 (/docs/)
[ ] ETF 清單可取得
[ ] 搜尋功能正常
[ ] 回應時間 < 2 秒

# ✅ 可選檢查
[ ] 自訂網域設定
[ ] Uptime 監控設定
[ ] Sentry 錯誤追蹤
[ ] SSL 憑證有效
```

---

**恭喜！你的後端已成功部署！** 🎉

接下來可以開始開發 React Native App 了。
