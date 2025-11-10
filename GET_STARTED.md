# 🚀 快速開始指南

## 歡迎使用台股 ETF App 完整解決方案！

這是一個從零開始的完整教學，幫助你建立一個專業的 React Native iOS App + Flask 後端系統。

---

## 📚 文件導航

### 🎯 新手必讀（按順序閱讀）

1. **[QUICK_START.md](./QUICK_START.md)** ⭐ 最先看
   - 5 分鐘快速測試
   - 專案概覽
   - 決策點

2. **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** ⭐ 第二看
   - 完整測試教學（從零開始）
   - 環境準備
   - 本地測試
   - API 測試

3. **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** ⭐ 第三看
   - 三種部署方案比較
   - Railway 部署（推薦）
   - Render 免費部署
   - 成本對比

4. **[EXPO_INTEGRATION.md](./EXPO_INTEGRATION.md)** ⭐ 最後看
   - React Native Expo 整合
   - API 服務層建立
   - 核心功能實作
   - 打包發布

### 📖 進階文件

- **[ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md)**
  - 完整架構設計
  - 三層架構圖
  - 快取策略
  - API 規範

- **[REFACTOR_ROADMAP.md](./REFACTOR_ROADMAP.md)**
  - 重構路線圖
  - 分階段計劃
  - 風險評估

- **[SOLUTION_PROPOSAL.md](./SOLUTION_PROPOSAL.md)**
  - 技術方案說明
  - 新舊對比
  - 實作步驟

---

## 🎯 三步驟開始

### Step 1: 測試 FinMind API（2 分鐘）

```bash
# 1. 註冊 FinMind
open https://finmindtrade.com/

# 2. 取得 Token 後測試
export FINMIND_TOKEN="your_token"
python finmind_example.py

# 預期輸出：
# ✅ 找到 300+ 個 ETF
# ✅ 取得 0050 持股明細
```

### Step 2: 本地測試後端（10 分鐘）

```bash
# 1. 安裝依賴
pip install -r requirements.txt
pip install -r requirements_new.txt

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 FINMIND_TOKEN

# 3. 啟動 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 4. 啟動後端
python3 -m flask --app app.main_new run

# 5. 測試 API
curl http://localhost:5000/health | jq
```

### Step 3: 部署到雲端（15 分鐘）

```bash
# 選擇一個部署平台：

# 選項 A: Railway（推薦，$5 免費額度）
# 1. 前往 https://railway.app/
# 2. 連接 GitHub
# 3. 一鍵部署

# 選項 B: Render（完全免費）
# 1. 前往 https://render.com/
# 2. 連接 GitHub
# 3. 使用 render.yaml 自動部署
```

---

## 🗂️ 專案結構

```
twETFHoldings/
├── 📚 文件
│   ├── GET_STARTED.md          ← 你在這裡
│   ├── QUICK_START.md          ← 快速開始
│   ├── TESTING_GUIDE.md        ← 測試教學
│   ├── DEPLOYMENT_GUIDE.md     ← 部署教學
│   ├── EXPO_INTEGRATION.md     ← Expo 整合
│   └── ARCHITECTURE_DESIGN.md  ← 架構設計
│
├── 🔧 後端實作
│   ├── app/
│   │   ├── main_new.py         ← Flask 主程式
│   │   ├── config.py           ← 配置管理
│   │   ├── extensions.py       ← Flask 擴展
│   │   ├── services/
│   │   │   ├── finmind.py      ← FinMind API 客戶端
│   │   │   └── cache.py        ← Redis 快取管理
│   │   ├── tasks/
│   │   │   └── scheduler.py    ← 定時任務
│   │   └── api/v1/
│   │       ├── etf.py          ← ETF API
│   │       ├── stock.py        ← 股票 API
│   │       ├── search.py       ← 搜尋 API
│   │       └── stats.py        ← 統計 API
│   │
│   ├── requirements.txt         ← 原有套件
│   ├── requirements_new.txt     ← 新增套件
│   └── .env.example            ← 環境變數範例
│
├── 🐳 部署配置
│   ├── Dockerfile              ← Docker 映像
│   ├── docker-compose.yml      ← Docker Compose
│   ├── railway.json            ← Railway 配置
│   └── render.yaml             ← Render 配置
│
└── 📱 範例程式
    ├── finmind_example.py      ← FinMind 使用範例
    ├── test_new_approach.py    ← 測試腳本
    └── (未來) mobile/          ← React Native App
```

---

## 💡 核心概念

### 資料流

```
React Native App (Expo)
        ↓ HTTP/REST API
Flask Backend (Railway/Render)
        ↓ with Redis Cache
FinMind API (免費)
```

### 快取策略

```
1. App 本地快取 (SQLite)     → 離線可用
2. 後端 Redis 快取 (24h)      → 快速回應
3. FinMind API              → 每日更新
```

### 定時任務

```
每日 14:00 → 更新 ETF 清單
每日 14:30 → 更新所有 ETF 持股
每日 14:30 → 更新熱門股價
每週日 02:00 → 清理快取
```

---

## 🎁 你將獲得什麼

### 功能

- ✅ 300+ 台股 ETF 即時資訊
- ✅ ETF 持股明細查詢
- ✅ 個股價格與 K 線圖
- ✅ 全文搜尋功能
- ✅ 自選清單
- ✅ 離線瀏覽

### 技術

- ✅ 完整的 RESTful API
- ✅ 多層快取架構
- ✅ 自動定時更新
- ✅ React Native App
- ✅ 零維護爬蟲
- ✅ 雲端部署（免費）

### 成本

- ✅ FinMind API: 免費
- ✅ 後端部署: $0-5/月
- ✅ Redis: 免費
- ✅ 總計: **幾乎免費！**

---

## 🔧 技術棧

### 後端

```
語言: Python 3.11+
框架: Flask 3.x
快取: Redis 7.x
API 文件: Flask-RESTX (Swagger)
定時任務: APScheduler
資料來源: FinMind API
```

### 前端

```
框架: React Native + Expo
語言: TypeScript
狀態管理: Zustand
API 請求: Axios
本地儲存: AsyncStorage + SQLite
圖表: react-native-chart-kit
```

### 開發工具

```
版本控制: Git + GitHub
API 測試: Postman / curl
容器化: Docker
CI/CD: Railway / Render (自動部署)
監控: UptimeRobot (免費)
```

---

## 📊 效能指標

| 指標 | 目標 | 備註 |
|------|------|------|
| API 回應時間 | < 500ms | 有快取時 |
| App 啟動時間 | < 3s | 冷啟動 |
| ETF 覆蓋率 | 300+ 個 | 全台股 ETF |
| API 請求量 | ~450/天 | 遠低於 600/hr 限制 |
| 快取命中率 | > 80% | Redis 快取 |
| 部署成本 | $0-5/月 | Railway 免費額度 |

---

## 🎓 學習路徑

### 初學者（第 1-3 天）

```
Day 1:
□ 閱讀 QUICK_START.md
□ 測試 FinMind API
□ 本地測試後端

Day 2:
□ 閱讀 TESTING_GUIDE.md
□ 完整測試所有 API
□ 理解快取機制

Day 3:
□ 閱讀 DEPLOYMENT_GUIDE.md
□ 部署到 Railway/Render
□ 驗證部署成功
```

### 進階（第 4-7 天）

```
Day 4:
□ 閱讀 EXPO_INTEGRATION.md
□ 建立 Expo 專案
□ 整合 API

Day 5-6:
□ 實作 ETF 列表頁
□ 實作 ETF 詳情頁
□ 實作搜尋功能

Day 7:
□ 實作自選清單
□ 測試與優化
□ 打包發布
```

---

## ❓ 常見問題

### Q: 我需要什麼基礎知識？

**A**: 基本的 Python 和 JavaScript/TypeScript 知識即可。所有步驟都有詳細教學。

### Q: 完全免費嗎？

**A**:
- FinMind API: 免費（600 req/hr）
- Railway: $5 免費額度（通常用不完）
- Render: 完全免費（會休眠）
- **總結**: 可以完全免費使用

### Q: 需要多久才能完成？

**A**:
- 後端測試: 1-2 小時
- 後端部署: 15-30 分鐘
- React Native App: 3-5 天（包含學習）

### Q: 如果遇到問題怎麼辦？

**A**:
1. 查看對應的教學文件
2. 查看 `常見問題` 章節
3. 檢查日誌輸出
4. Google 錯誤訊息
5. 查看 GitHub Issues

---

## 🎯 下一步行動

### 現在就開始！

```bash
# 1. 快速測試（2 分鐘）
python finmind_example.py

# 2. 如果成功，開始完整測試
# 閱讀並執行 TESTING_GUIDE.md

# 3. 部署到雲端
# 閱讀並執行 DEPLOYMENT_GUIDE.md

# 4. 建立 React Native App
# 閱讀並執行 EXPO_INTEGRATION.md
```

---

## 📞 支援與資源

### 官方文件

- **FinMind**: https://finmind.github.io/
- **Flask**: https://flask.palletsprojects.com/
- **Expo**: https://docs.expo.dev/
- **Railway**: https://docs.railway.app/
- **Render**: https://render.com/docs

### 社群資源

- GitHub Issues: 回報問題
- Stack Overflow: 技術問題
- Expo Forums: React Native 問題

---

## 🎉 準備好了嗎？

**選擇你的起點：**

1. 🚀 **我想快速開始** → [QUICK_START.md](./QUICK_START.md)
2. 🧪 **我想完整測試** → [TESTING_GUIDE.md](./TESTING_GUIDE.md)
3. ☁️ **我想直接部署** → [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
4. 📱 **我想開發 App** → [EXPO_INTEGRATION.md](./EXPO_INTEGRATION.md)
5. 📖 **我想理解架構** → [ARCHITECTURE_DESIGN.md](./ARCHITECTURE_DESIGN.md)

---

**讓我們開始吧！** 🚀

> 💡 提示：建議從 QUICK_START.md 開始，按順序閱讀所有文件。
