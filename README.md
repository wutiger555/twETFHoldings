# 台股 ETF 資訊整合平台

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)](https://flask.palletsprojects.com/)
[![React Native](https://img.shields.io/badge/React_Native-Expo-purple.svg)](https://expo.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一個完整的台股 ETF 資訊查詢平台，提供 300+ ETF 持股明細、個股價格查詢、全文搜尋等功能。

**零維護成本** | **開箱即用** | **雲端部署** | **手機 App 支援**

---

## ✨ 核心特色

### 資料來源優化
- ✅ **零維護爬蟲**：使用 [FinMind API](https://finmindtrade.com/) 取代傳統網頁爬蟲
- ✅ **300+ ETF 覆蓋**：全台股 ETF 完整支援
- ✅ **即時價格**：個股即時價格與 K 線圖
- ✅ **免費使用**：600 req/hr 免費額度，足夠日常使用

### 技術架構
- 🚀 **Flask 後端**：RESTful API + Swagger 文件
- 💾 **Redis 快取**：多層快取策略，回應時間 < 500ms
- ⏰ **自動更新**：定時任務每日自動更新資料
- 📱 **React Native**：支援 iOS/Android App 開發
- ☁️ **雲端部署**：Railway/Render 一鍵部署

### 開發體驗
- 📦 **容器化部署**：Docker + Docker Compose
- 📚 **完整文件**：從測試到部署的完整教學
- 🧪 **測試友善**：包含完整的測試指南
- 🎯 **現代化架構**：清晰的目錄結構與模組化設計

---

## 🚀 5 分鐘快速開始

### 選項 1: 使用 Docker (推薦)

```bash
# 1. Clone 專案
git clone https://github.com/your-username/twETFHoldings.git
cd twETFHoldings

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 FINMIND_TOKEN (選填，免費使用也可以)

# 3. 啟動所有服務
docker-compose up -d

# 4. 測試 API
curl http://localhost:5001/health | jq

# 完成！🎉 後端已在 http://localhost:5001 運行
```

### 選項 2: 本地開發

```bash
# 1. 安裝 Python 依賴
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. 啟動 Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 3. 設定環境變數
cp .env.example .env

# 4. 啟動後端（使用便捷腳本，推薦）
./run_dev.sh

# 或手動啟動
python -m flask --app backend.main run

# 5. 測試
curl http://localhost:5001/health
# 查看 Swagger 文件: http://localhost:5001/api/v1/
```

#### ⚠️ macOS 用戶注意

如果遇到 **403 Forbidden** 錯誤，請參考 [macOS 端口衝突解決方案](docs/MACOS_PORT_5000_FIX.md)

**快速解決：**
- 使用腳本：`./run_dev.sh`（自動處理端口衝突）
- 或關閉 AirPlay Receiver（系統設定 → 通用 → AirDrop 與接續互通）

### 選項 3: 測試 FinMind API

```bash
# 不需要啟動任何服務，直接測試 API 連接
python examples/finmind_example.py

# 預期輸出：
# ✅ 找到 300+ 個 ETF
# ✅ 取得 0050 持股明細
# ✅ 取得 2330 股價
```

---

## 📁 專案結構

```
twETFHoldings/
├── 📚 docs/                      ← 所有文件集中在這裡
│   ├── GET_STARTED.md           ← 📖 完整教學入口
│   ├── QUICK_START.md           ← 🚀 5分鐘快速開始
│   ├── TESTING_GUIDE.md         ← 🧪 完整測試教學
│   ├── DEPLOYMENT_GUIDE.md      ← ☁️ 部署到雲端
│   ├── EXPO_INTEGRATION.md      ← 📱 React Native App
│   ├── ARCHITECTURE_DESIGN.md   ← 🏗️ 架構設計
│   └── archive/                 ← 舊文件歸檔
│
├── 🔧 backend/                   ← Flask 後端 (原 app/)
│   ├── main.py                  ← Flask 主程式
│   ├── config.py                ← 配置管理
│   ├── extensions.py            ← Flask 擴展
│   ├── services/                ← 服務層
│   │   ├── finmind.py          ← FinMind API 客戶端
│   │   └── cache.py            ← Redis 快取管理
│   ├── tasks/                   ← 定時任務
│   │   └── scheduler.py        ← APScheduler 排程
│   └── api/v1/                  ← RESTful API
│       ├── etf.py              ← ETF API
│       ├── stock.py            ← 股票 API
│       ├── search.py           ← 搜尋 API
│       └── stats.py            ← 統計 API
│
├── 📱 mobile/                    ← React Native App (Expo)
│   └── README.md               ← App 開發說明
│
├── 📋 examples/                  ← 範例程式
│   ├── finmind_example.py      ← FinMind 使用範例
│   └── test_new_approach.py    ← API 測試腳本
│
├── 📦 archive/                   ← 舊程式碼歸檔
│   ├── app/                    ← 舊版 Flask
│   ├── scripts/                ← 舊版爬蟲
│   ├── frontend/               ← 舊版 React 網頁
│   └── config.json             ← 舊版配置
│
├── 🐳 部署配置
│   ├── Dockerfile              ← Docker 映像
│   ├── docker-compose.yml      ← Docker Compose
│   ├── railway.json            ← Railway 配置
│   └── render.yaml             ← Render 配置
│
└── 📄 根目錄檔案
    ├── README.md               ← 你在這裡
    ├── CHANGELOG.md            ← 更新日誌
    ├── requirements.txt        ← Python 依賴
    ├── .env.example            ← 環境變數範例
    └── .gitignore
```

---

## 📖 完整文件導航

### 🎯 新手必讀（按順序閱讀）

1. **[🚀 COMPLETE_SETUP_GUIDE.md](./docs/COMPLETE_SETUP_GUIDE.md)** ⭐⭐⭐ 必讀
   - **從零到部署的完整指南**
   - 環境準備 (Python, Node.js, Redis)
   - Docker 容器化設定
   - 本地測試完整流程
   - **部署方案完整比較** (Railway, Render, Fly.io, Google Cloud Run)
   - 多 APP 共用分析
   - 常見問題解決

2. **[📊 FINMIND_QUOTA_ANALYSIS.md](./docs/FINMIND_QUOTA_ANALYSIS.md)** ⭐⭐ 重要
   - **FinMind 免費額度分析**
   - 實際使用量估算
   - 優化策略 (500人以下完全夠用)
   - 快取策略建議
   - 付費方案對比

3. **[📱 MOBILE_APP_GUIDE.md](./docs/MOBILE_APP_GUIDE.md)** ⭐⭐⭐ App 開發必讀
   - React Native + Expo 完整架構
   - 極簡現代風格設計
   - **wagmi-charts 股價圖表**
   - 圓餅圖持股分析
   - 個股影響力計算
   - 完整程式碼範例 (10,000+ 字)

4. **[🧪 TESTING_GUIDE.md](./docs/TESTING_GUIDE.md)**
   - API 測試教學
   - curl / Postman / Python 測試
   - 疑難排解

5. **[☁️ DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)**
   - Railway 一鍵部署
   - Render 免費方案
   - 成本對比

### 📚 進階文件

- **[🏗️ ARCHITECTURE_DESIGN.md](./docs/ARCHITECTURE_DESIGN.md)**
  - 完整架構設計
  - 三層架構圖
  - API 規範

- **[📖 GET_STARTED.md](./docs/GET_STARTED.md)**
  - 專案概覽
  - 學習路徑

- **[🚀 QUICK_START.md](./docs/QUICK_START.md)**
  - 快速開始指南

- **[🗺️ REFACTOR_ROADMAP.md](./docs/REFACTOR_ROADMAP.md)**
  - 重構路線圖

- **[📱 EXPO_INTEGRATION.md](./docs/EXPO_INTEGRATION.md)**
  - Expo 整合詳細說明

---

## 🛠️ 技術棧

### 後端
- **語言**: Python 3.11+
- **框架**: Flask 3.x
- **快取**: Redis 7.x
- **API 文件**: Flask-RESTX (Swagger)
- **定時任務**: APScheduler
- **資料來源**: FinMind API

### 前端 (Mobile)
- **框架**: React Native + Expo
- **語言**: TypeScript
- **狀態管理**: Zustand
- **API 請求**: Axios
- **本地儲存**: SQLite

### 部署
- **容器化**: Docker + Docker Compose
- **雲端平台**: Railway / Render / Fly.io
- **資料庫**: Redis (快取) + PostgreSQL (可選)
- **CI/CD**: 自動部署

---

## 🎯 使用場景

### 1. 本地開發測試
```bash
# 啟動 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 啟動 Flask 後端
python -m flask --app backend.main run

# 測試 API
curl http://localhost:5001/api/v1/etf/etfs
```

### 2. Docker 容器化
```bash
# 使用 Docker Compose
docker-compose up -d

# 查看服務狀態
docker-compose ps
```

### 3. 雲端部署
```bash
# Railway 部署（推薦）
1. Fork 此專案
2. 連接 Railway: https://railway.app/
3. 設定環境變數 FINMIND_TOKEN
4. 一鍵部署完成

# 詳細步驟請參考 docs/DEPLOYMENT_GUIDE.md
```

### 4. React Native App 開發
```bash
# 建立 Expo 專案
cd mobile/
npx create-expo-app@latest tw-etf-app

# 詳細步驟請參考 docs/EXPO_INTEGRATION.md
```

---

## 📊 API 端點預覽

| 端點 | 說明 | 範例 |
|------|------|------|
| `GET /health` | 健康檢查 | - |
| `GET /api/v1/etf/etfs` | ETF 列表 | `?page=1&limit=50` |
| `GET /api/v1/etf/etf/<code>` | ETF 詳情 | `/etf/0050` |
| `GET /api/v1/etf/etf/<code>/holdings` | ETF 持股 | `/etf/0050/holdings` |
| `GET /api/v1/stock/<code>` | 個股價格 | `/stock/2330` |
| `GET /api/v1/stock/<code>/history` | 個股歷史 | `/stock/2330/history?period=30d` |
| `GET /api/v1/search` | 搜尋 | `?q=台積電&type=STOCK` |
| `GET /api/v1/stats/popular` | 熱門股票 | `?limit=20` |

**完整 API 文件**: 啟動後端後訪問 `http://localhost:5001/docs/`

---

## 💰 成本估算與 FinMind 免費額度分析

### FinMind API 免費額度 ✅ 完全夠用

| 使用情境 | 每日 API 請求數 | 是否安全 |
|---------|----------------|---------|
| **優化後 (定時任務)** | ~450 次 | ✅ 極度安全 |
| **10 個活躍用戶** | ~211 次 | ✅ 極度安全 |
| **100 個活躍用戶** | ~751 次 | ✅ 安全 |
| **500 個活躍用戶** | ~3,151 次 | ✅ 安全 |
| **1,000 個活躍用戶** | ~6,151 次 | ⚠️ 接近上限 |

**關鍵策略**：
- ✅ 使用定時任務預先載入資料 (每日 ~150 次請求)
- ✅ 長時間快取 (ETF 資料 24hr, 股價 15min)
- ✅ 快取命中率 > 80%

**結論**: 在 **500 個活躍用戶**以下，免費額度綽綽有餘！

詳細分析請參考：[📊 FinMind 免費額度完整分析](./docs/FINMIND_QUOTA_ANALYSIS.md)

### 部署成本

| 平台 | 免費方案 | 付費方案 | 適合場景 | 多APP共用 |
|------|----------|----------|---------|----------|
| **Railway** | $5/月 | $20+/月 | 個人專案 | ✅ 優秀 |
| **Render** | 完全免費 | $7+/月 | 測試/學習 | ⚠️ 有限 |
| **Fly.io** | $0 | $10+/月 | 高效能 | ✅ 優秀 |
| **Google Cloud Run** | $0 | 按量計費 | 彈性擴展 | ✅ 最佳 |

**推薦方案**:
- 個人使用: Railway ($0-5/月)
- 測試環境: Render (完全免費)
- 多個 APP: Google Cloud Run ($0-30/月)

詳細比較請參考：[🚀 部署方案完整比較](./docs/COMPLETE_SETUP_GUIDE.md#部署方案完整比較)

### 總成本

| 項目 | 免費方案 | 付費方案 | 備註 |
|------|----------|----------|------|
| FinMind API | 600 req/hr | $99/月起 | **免費完全夠用** (< 500 用戶) |
| 雲端部署 | $0-5/月 | $20+/月 | Railway 或 Render |
| Redis | 免費 25MB | - | 平台提供 |
| **總計** | **$0-5/月** | - | **幾乎免費！** |

---

## 🤝 貢獻指南

歡迎提交 Issue 或 Pull Request！

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

## 📝 更新日誌

查看 [CHANGELOG.md](./CHANGELOG.md) 了解版本更新歷史。

### 最新版本 (v2.0.0 - 重大重構)

- ✅ 使用 FinMind API 取代所有爬蟲
- ✅ 完整後端重構 (app/ → backend/)
- ✅ Redis 多層快取策略
- ✅ 定時任務自動更新
- ✅ 完整部署文件
- ✅ React Native App 架構
- ✅ 專案結構現代化

---

## 📞 支援與資源

### 官方文件
- **FinMind**: https://finmindtrade.com/
- **Flask**: https://flask.palletsprojects.com/
- **Expo**: https://docs.expo.dev/
- **Railway**: https://docs.railway.app/

### 問題回報
- GitHub Issues: https://github.com/your-repo/issues

---

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案

---

## 🎉 開始使用

### 推薦學習路徑

#### 🎯 新手路徑 (從零開始)

1. **[🚀 COMPLETE_SETUP_GUIDE.md](./docs/COMPLETE_SETUP_GUIDE.md)** - 開始這裡！
   - 環境準備 (Python, Node.js, Docker)
   - 本地開發設定
   - Docker 容器化
   - 完整測試流程
   - 部署方案比較

2. **[📊 FINMIND_QUOTA_ANALYSIS.md](./docs/FINMIND_QUOTA_ANALYSIS.md)** - 了解限制
   - 免費額度夠不夠用？
   - 優化策略
   - 成本估算

3. **[☁️ DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)** - 部署到雲端
   - Railway 一鍵部署
   - 或 Render 免費方案

4. **[📱 MOBILE_APP_GUIDE.md](./docs/MOBILE_APP_GUIDE.md)** - 開發 App
   - React Native 架構
   - wagmi-charts 圖表
   - 完整實作指南

#### 🚀 快速路徑 (有經驗)

1. **Docker 啟動**: `docker-compose up -d`
2. **測試 API**: `curl http://localhost:5001/health`
3. **部署**: 參考 [DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)
4. **開發 App**: 參考 [MOBILE_APP_GUIDE.md](./docs/MOBILE_APP_GUIDE.md)

---

**祝您使用愉快！** 🚀

有問題請參考 [常見問題](./docs/COMPLETE_SETUP_GUIDE.md#常見問題)

---

**專案維護者**: [Your Name]
**最後更新**: 2025-11-10
**版本**: 2.0.0
