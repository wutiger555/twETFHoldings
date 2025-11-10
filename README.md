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

### 1. 測試 FinMind API（2 分鐘）

```bash
# 1. 註冊 FinMind 帳號並取得 Token
open https://finmindtrade.com/

# 2. 設定環境變數
export FINMIND_TOKEN="your_token_here"

# 3. 執行範例程式
python examples/finmind_example.py

# 預期輸出：
# ✅ 找到 300+ 個 ETF
# ✅ 取得 0050 持股明細
```

### 2. 啟動本地後端（3 分鐘）

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 FINMIND_TOKEN

# 3. 啟動 Redis (使用 Docker)
docker run -d -p 6379:6379 redis:7-alpine

# 4. 啟動 Flask 後端
python -m flask --app backend.main run

# 5. 測試 API
curl http://localhost:5000/health | jq
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

1. **[📖 GET_STARTED.md](./docs/GET_STARTED.md)** ⭐ 最先看
   - 完整專案概覽
   - 學習路徑
   - 常見問題

2. **[🚀 QUICK_START.md](./docs/QUICK_START.md)**
   - 5 分鐘快速測試
   - 專案概覽
   - 決策點

3. **[🧪 TESTING_GUIDE.md](./docs/TESTING_GUIDE.md)**
   - 完整測試教學（從零開始）
   - 環境準備
   - API 測試
   - 疑難排解

4. **[☁️ DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)**
   - Railway 部署（推薦）
   - Render 免費部署
   - 成本對比

5. **[📱 EXPO_INTEGRATION.md](./docs/EXPO_INTEGRATION.md)**
   - React Native Expo 整合
   - App 開發完整流程
   - 打包發布

### 📚 進階文件

- **[🏗️ ARCHITECTURE_DESIGN.md](./docs/ARCHITECTURE_DESIGN.md)**
  - 完整架構設計
  - 三層架構圖
  - 快取策略
  - API 規範

- **[🗺️ REFACTOR_ROADMAP.md](./docs/REFACTOR_ROADMAP.md)**
  - 重構路線圖
  - 新舊對比
  - 遷移計劃

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
curl http://localhost:5000/api/v1/etf/etfs
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

**完整 API 文件**: 啟動後端後訪問 `http://localhost:5000/docs/`

---

## 💰 成本估算

| 項目 | 免費方案 | 付費方案 | 備註 |
|------|----------|----------|------|
| FinMind API | 600 req/hr | 無限制 | 免費足夠使用 |
| Railway | $5/月 | $20+/月 | 免費額度通常用不完 |
| Render | 完全免費 | $7+/月 | 會休眠但可接受 |
| Redis | 免費 25MB | - | Railway/Render 提供 |
| **總計** | **$0-5/月** | - | 幾乎免費！ |

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

**推薦學習路徑**：

1. 📖 閱讀 [GET_STARTED.md](./docs/GET_STARTED.md) 了解專案全貌
2. 🚀 跟著 [QUICK_START.md](./docs/QUICK_START.md) 快速測試
3. 🧪 使用 [TESTING_GUIDE.md](./docs/TESTING_GUIDE.md) 完整測試
4. ☁️ 參考 [DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md) 部署到雲端
5. 📱 查看 [EXPO_INTEGRATION.md](./docs/EXPO_INTEGRATION.md) 開發 App

**祝您使用愉快！** 🚀

---

**專案維護者**: [Your Name]
**最後更新**: 2025-11-10
**版本**: 2.0.0
