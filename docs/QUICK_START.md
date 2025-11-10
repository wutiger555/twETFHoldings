# 快速開始指南

## 🎯 目標

將現有專案改造為 **React Native iOS App**，使用 FinMind API 取代多個爬蟲。

---

## ⚡ 5 分鐘快速測試

### 1. 註冊 FinMind（2 分鐘）

```bash
# 前往註冊
open https://finmindtrade.com/

# 註冊後取得 Token
# 將 Token 存到環境變數
export FINMIND_TOKEN="your_token_here"
```

### 2. 測試 FinMind API（2 分鐘）

```bash
# 測試 API 是否可用
python finmind_example.py
```

**預期結果**：
- ✅ 取得 300+ 個 ETF 清單
- ✅ 取得 0050 持股明細
- ✅ 取得台積電股價

### 3. 決策點（1 分鐘）

**如果測試成功** → 開始重構（預計 5 天）
**如果有問題** → 查看下方 Troubleshooting

---

## 📅 完整實作時程（5 天）

### Day 1: 後端核心（FinMind + Redis）

**目標**: 建立新的後端架構

```bash
# 1. 安裝套件
pip install redis APScheduler python-dotenv

# 2. 啟動 Redis
docker run -d -p 6379:6379 redis:7-alpine

# 3. 測試快取
python app/services/cache.py

# 4. 測試 FinMind 客戶端
python app/services/finmind.py
```

**完成標準**:
- [ ] Redis 運行正常
- [ ] FinMind API 可正常呼叫
- [ ] 快取機制運作正常

---

### Day 2: API 重構 + 定時任務

**目標**: 建立 RESTful API 和自動更新機制

```bash
# 1. 建立新的 API 路由
# 參考 app/api/v1/etf.py

# 2. 測試 API
flask --app app.main run
curl http://localhost:5000/api/v1/etfs

# 3. 設定定時任務
python app/tasks/scheduler.py
```

**完成標準**:
- [ ] API 可正常回應
- [ ] 定時任務正常執行
- [ ] 資料自動更新

---

### Day 3: React Native 專案建立

**目標**: 建立 React Native iOS 專案

```bash
# 1. 安裝 React Native CLI
npx react-native@latest init ETFApp

# 2. 啟動專案
cd ETFApp
npx react-native run-ios

# 3. 整合 Navigation
npm install @react-navigation/native @react-navigation/native-stack
```

**完成標準**:
- [ ] App 可在模擬器運行
- [ ] 路由導航正常
- [ ] 可呼叫後端 API

---

### Day 4: App 核心功能

**目標**: 實作 ETF 列表、詳情、個股頁面

**功能清單**:
- [ ] ETF 列表頁
- [ ] ETF 詳情頁（含持股）
- [ ] 個股詳情頁（含價格圖表）
- [ ] 搜尋功能
- [ ] 下拉刷新

---

### Day 5: 優化與測試

**目標**: 效能優化、測試、上線準備

**檢查清單**:
- [ ] App 啟動時間 < 3 秒
- [ ] 列表滾動流暢
- [ ] 快取機制正常
- [ ] 錯誤處理完善
- [ ] TestFlight 打包

---

## 🏗️ 目錄結構（最終）

```
twETFHoldings/
├── backend/                    # 後端
│   ├── app/
│   │   ├── api/v1/            # API 路由
│   │   ├── services/          # 業務邏輯
│   │   ├── tasks/             # 定時任務
│   │   └── main.py            # 入口
│   ├── requirements.txt
│   └── .env
│
├── mobile/                     # React Native App
│   ├── src/
│   │   ├── screens/           # 頁面
│   │   ├── components/        # 元件
│   │   ├── services/          # API 呼叫
│   │   └── store/             # 狀態管理
│   ├── ios/
│   ├── android/
│   └── package.json
│
├── docs/                       # 文件
│   ├── ARCHITECTURE_DESIGN.md
│   ├── REFACTOR_ROADMAP.md
│   └── API_DOCUMENTATION.md
│
└── scripts/                    # 工具腳本
    ├── finmind_example.py
    └── test_new_approach.py
```

---

## 🛠️ 開發工具推薦

### 必裝工具

1. **VS Code**
   - 延伸功能：Python, React Native Tools

2. **Postman**
   - 測試 API

3. **React Native Debugger**
   - 除錯 App

4. **Redis Insight**
   - 管理 Redis 快取

### 推薦但非必要

- Docker Desktop（容器化部署）
- TablePlus（資料庫管理）
- Charles Proxy（網路除錯）

---

## ❓ Troubleshooting

### 問題 1: FinMind API 回應 403

**原因**: Token 未設定或無效

**解決**:
```bash
# 檢查 Token
echo $FINMIND_TOKEN

# 重新設定
export FINMIND_TOKEN="your_actual_token"
```

### 問題 2: Redis 連接失敗

**原因**: Redis 未啟動

**解決**:
```bash
# 檢查 Redis 狀態
redis-cli ping

# 如果沒有回應，啟動 Redis
docker run -d -p 6379:6379 redis:7-alpine
```

### 問題 3: React Native 無法啟動

**原因**: 依賴未安裝

**解決**:
```bash
cd mobile

# iOS
cd ios && pod install && cd ..
npx react-native run-ios

# 清除快取
npx react-native start --reset-cache
```

### 問題 4: App 無法連接後端

**原因**: iOS 模擬器無法連接 localhost

**解決**:
```javascript
// 使用電腦的實際 IP
const API_BASE = "http://192.168.1.100:5000/api/v1";

// 或使用 ngrok
ngrok http 5000
```

---

## 📞 獲取協助

### 文件資源

1. **架構設計**: `ARCHITECTURE_DESIGN.md`
2. **重構路線**: `REFACTOR_ROADMAP.md`
3. **技術方案**: `SOLUTION_PROPOSAL.md`

### 範例程式

1. **FinMind 使用**: `finmind_example.py`
2. **快取管理**: `app/services/cache.py`
3. **定時任務**: `app/tasks/scheduler.py`
4. **API 路由**: `app/api/v1/etf.py`

### 社群資源

- **FinMind 文件**: https://finmind.github.io/
- **React Native 文件**: https://reactnative.dev/
- **Flask 文件**: https://flask.palletsprojects.com/

---

## 🎯 成功指標

完成後你應該達成：

### 功能面
- [  ] ✅ 支援 300+ 個 ETF
- [ ] ✅ 顯示即時股價
- [ ] ✅ 個股詳情頁
- [ ] ✅ 自選清單
- [ ] ✅ 離線瀏覽

### 技術面
- [ ] ✅ 零爬蟲維護
- [ ] ✅ API 回應 < 500ms
- [ ] ✅ App 啟動 < 3s
- [ ] ✅ 快取命中率 > 80%

### 成本面
- [ ] ✅ 完全免費方案
- [ ] ✅ 每日 API 請求 < 600

---

## 🚀 立即開始

```bash
# 1. 測試 FinMind
python finmind_example.py

# 2. 如果成功，開始 Day 1
pip install -r requirements_new.txt

# 3. 逐日完成任務
# 參考上方的 5 天計劃
```

**準備好了嗎？讓我們開始吧！** 🎉
