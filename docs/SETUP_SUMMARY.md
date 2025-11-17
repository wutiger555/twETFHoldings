# 📋 設定總結與最佳實踐

> **最後更新**: 2025-11-16
> **適用版本**: v2.0.0+

---

## 🎯 核心要點

### 1. Swagger API 文件位置

**正確路徑**: `http://localhost:5001/api/v1/`

❌ ~~`http://localhost:5001/docs/`~~ （錯誤）
✅ `http://localhost:5001/api/v1/` （正確）

**原因**: Flask-RESTX 的配置中，`prefix='/api/v1'` 會影響所有路由包括文件路徑。

### 2. macOS 端口 5000 衝突

**問題**: macOS Monterey (12.0+) 的 AirPlay Receiver 佔用 5000 端口

**解決方案** (推薦順序):

1. **使用智能啟動腳本** (最簡單)
   ```bash
   ./run_dev.sh
   ```
   - 自動偵測端口衝突
   - 自動檢查依賴
   - 提供友善提示

2. **關閉 AirPlay Receiver** (保持 5000 端口)
   - 系統設定 → 通用 → AirDrop 與接續互通
   - 關閉 **AirPlay Receiver**

3. **使用其他端口**
   ```bash
   python -m flask --app backend.main run --port 5001
   ```

詳細說明: [docs/MACOS_PORT_5000_FIX.md](MACOS_PORT_5000_FIX.md)

---

## 🚀 推薦的開發流程

### 初次設定

```bash
# 1. Clone 專案
git clone https://github.com/your-username/twETFHoldings.git
cd twETFHoldings

# 2. 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 啟動 Redis (Docker)
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 5. 設定環境變數
cp .env.example .env
# 編輯 .env，填入 FINMIND_TOKEN (可選)

# 6. 啟動開發伺服器
./run_dev.sh
```

### 日常開發

```bash
# 1. 啟動虛擬環境
source venv/bin/activate

# 2. 確認 Redis 運行中
docker ps | grep redis

# 3. 啟動開發伺服器
./run_dev.sh

# 4. 開始開發！
# - Swagger 文件: http://localhost:5001/api/v1/
# - 健康檢查: http://localhost:5001/health
```

---

## 📖 重要 URL 清單

### 本地開發 (預設 5000 端口)

| 用途 | URL | 說明 |
|------|-----|------|
| **Swagger API 文件** | http://localhost:5001/api/v1/ | 完整 API 文件與測試介面 |
| **首頁** | http://localhost:5001/ | API 資訊與端點列表 |
| **健康檢查** | http://localhost:5001/health | 檢查服務狀態 |
| **ETF 列表** | http://localhost:5001/api/v1/etf/etfs | 取得所有 ETF |
| **ETF 詳情** | http://localhost:5001/api/v1/etf/etf/0050 | 查詢單一 ETF |
| **ETF 持股** | http://localhost:5001/api/v1/etf/etf/0050/holdings | 取得持股明細 |
| **個股價格** | http://localhost:5001/api/v1/stock/2330 | 查詢股價 |
| **搜尋** | http://localhost:5001/api/v1/search?q=台積電 | 全文搜尋 |

### 如果使用 5001 端口

將上述 URL 中的 `5000` 改為 `5001`

---

## 🧪 測試檢查清單

### 環境檢查

- [ ] Python 3.11+ 已安裝
- [ ] 虛擬環境已啟動 (`(venv)` 前綴)
- [ ] Redis 正在運行 (`docker ps` 或 `redis-cli ping`)
- [ ] .env 檔案已建立

### 功能測試

```bash
# 1. 健康檢查
curl http://localhost:5001/health
# 預期: {"status":"healthy",...}

# 2. 首頁
curl http://localhost:5001/
# 預期: {"message":"台股 ETF API",...}

# 3. API 端點
curl "http://localhost:5001/api/v1/etf/etfs?limit=5"
# 預期: {"data":[...],...}

# 4. Swagger 文件
curl http://localhost:5001/api/v1/ | grep -q "Swagger"
# 預期: 無輸出表示成功
```

### 使用測試腳本

```bash
# 自動化測試
./test_api.sh

# 預期輸出:
# ✅ 健康檢查通過
# ✅ API 端點正常
# ✅ Swagger 文件可訪問
```

---

## 🔧 常用指令速查

### 開發指令

```bash
# 啟動開發伺服器（推薦）
./run_dev.sh

# 手動啟動（標準方式）
python -m flask --app backend.main run

# 啟用熱重載
python -m flask --app backend.main run --reload

# 指定端口
python -m flask --app backend.main run --port 5001

# 檢查端口佔用
lsof -i :5000

# 查看運行中的 Flask
ps aux | grep flask
```

### Redis 指令

```bash
# 啟動 Redis (Docker)
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 檢查 Redis 狀態
docker ps | grep redis
redis-cli ping  # 應返回 PONG

# 查看快取內容
redis-cli
> KEYS *
> GET etf_detail_0050
> TTL etf_detail_0050

# 清除所有快取
redis-cli FLUSHALL
```

### Docker 指令

```bash
# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f backend

# 停止服務
docker-compose down

# 重新建置
docker-compose build

# 進入容器
docker-compose exec backend bash
```

---

## 🐛 常見問題快速解答

### Q1: 訪問 localhost:5001 返回 403

**原因**: macOS AirPlay Receiver 佔用端口

**解決**:
```bash
# 方案 1: 使用腳本（推薦）
./run_dev.sh

# 方案 2: 關閉 AirPlay
# 系統設定 → 通用 → AirDrop 與接續互通 → 關閉 AirPlay Receiver
```

詳見: [docs/MACOS_PORT_5000_FIX.md](MACOS_PORT_5000_FIX.md)

### Q2: Swagger 文件 404

**錯誤 URL**: `http://localhost:5001/docs/`
**正確 URL**: `http://localhost:5001/api/v1/`

### Q3: Redis 連接失敗

```bash
# 檢查 Redis 是否運行
docker ps | grep redis

# 如果沒有，啟動 Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 測試連接
redis-cli ping
```

### Q4: FinMind API 呼叫失敗

```bash
# 檢查 Token 設定
grep FINMIND_TOKEN .env

# 測試 FinMind API
python examples/finmind_example.py

# 即使沒有 Token 也可以使用（有請求限制）
```

### Q5: 虛擬環境未啟動

```bash
# 確認是否有 (venv) 前綴
# 如果沒有，啟動虛擬環境

source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

---

## 📚 文件導航

### 快速入門
- [QUICK_START.md](QUICK_START.md) - 5 分鐘快速開始
- [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) - 完整設定指南
- [MACOS_PORT_5000_FIX.md](MACOS_PORT_5000_FIX.md) - macOS 端口衝突解決

### 進階主題
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - 測試指南
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
- [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md) - 架構設計
- [MOBILE_APP_GUIDE.md](MOBILE_APP_GUIDE.md) - Mobile App 開發

### API 相關
- [FINMIND_QUOTA_ANALYSIS.md](FINMIND_QUOTA_ANALYSIS.md) - FinMind API 額度分析

---

## ✅ 最佳實踐總結

### 開發環境

1. **使用便捷腳本**
   - `./run_dev.sh` - 自動化環境檢查
   - `./test_api.sh` - 快速測試 API

2. **保持依賴更新**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **使用 Docker Compose**
   - 環境一致性
   - 簡化 Redis 管理

### 開發習慣

1. **始終啟動虛擬環境**
   - 避免污染全局 Python 環境

2. **定期清理快取**
   ```bash
   redis-cli FLUSHALL  # 清除 Redis 快取
   ```

3. **查看日誌**
   - Flask 預設會顯示所有請求
   - Redis 錯誤會顯示在日誌中

4. **使用 Swagger 測試 API**
   - 訪問 `http://localhost:5001/api/v1/`
   - 直接在瀏覽器測試所有端點

### 端口管理

1. **macOS 用戶**
   - 優先使用 `./run_dev.sh`
   - 或一次性關閉 AirPlay Receiver

2. **團隊協作**
   - 統一使用 5000 端口
   - 在文檔中說明 macOS 端口衝突

---

## 🎓 學習路徑建議

### 新手 (第 1 天)
1. 閱讀 [QUICK_START.md](QUICK_START.md)
2. 執行 `./run_dev.sh`
3. 訪問 Swagger: `http://localhost:5001/api/v1/`
4. 測試幾個 API 端點

### 進階 (第 2-3 天)
1. 閱讀 [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
2. 理解 Redis 快取機制
3. 學習 FinMind API 使用
4. 測試完整功能

### 專家 (第 4-7 天)
1. 閱讀 [ARCHITECTURE_DESIGN.md](ARCHITECTURE_DESIGN.md)
2. 學習部署流程 ([DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))
3. 開發 Mobile App ([MOBILE_APP_GUIDE.md](MOBILE_APP_GUIDE.md))
4. 優化效能與快取策略

---

**需要幫助？**
- 查看 [常見問題](#-常見問題快速解答)
- 參考完整文檔: [docs/](.)
- 提交 Issue: [GitHub Issues](https://github.com/your-username/twETFHoldings/issues)

**祝開發愉快！** 🚀
