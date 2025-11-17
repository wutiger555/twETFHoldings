# 🚀 快速參考卡

> **端口**: 5001 | **Python**: 3.11+ | **更新**: 2025-11-16

---

## ⚡ 快速啟動

```bash
# 1. 啟動 Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 2. 啟動虛擬環境
source venv/bin/activate

# 3. 啟動服務
./run_dev.sh

# 完成！訪問 http://localhost:5001/api/v1/
```

---

## 📌 重要 URL

| 服務 | URL |
|------|-----|
| **Swagger** | http://localhost:5001/api/v1/ |
| **健康檢查** | http://localhost:5001/health |
| **API 首頁** | http://localhost:5001/ |

---

## 🔧 常用指令

### 開發

```bash
# 啟動開發伺服器
./run_dev.sh

# 測試 API
./test_api.sh

# 手動啟動
python -m flask --app backend.main run
```

### Redis

```bash
# 啟動 Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 檢查狀態
docker ps | grep redis
redis-cli ping
```

### Docker

```bash
# 啟動所有服務
docker-compose up -d

# 查看日誌
docker-compose logs -f backend

# 停止
docker-compose down
```

---

## 🐛 常見問題

### 端口被佔用？

```bash
# 查看佔用
lsof -i :5001

# 停止佔用
lsof -ti:5001 | xargs kill -9
```

### Redis 連接失敗？

```bash
# 檢查 Redis
docker ps | grep redis

# 重啟 Redis
docker restart redis
```

### 虛擬環境未啟動？

```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

---

## 📁 專案結構

```
twETFHoldings/
├── backend/          # Flask 後端
├── mobile/           # React Native App
├── docs/             # 文檔
├── run_dev.sh        # 啟動腳本
├── test_api.sh       # 測試腳本
└── .env              # 環境配置 (PORT=5001)
```

---

## 📚 完整文檔

- [完整設定指南](docs/COMPLETE_SETUP_GUIDE.md)
- [設定總結](docs/SETUP_SUMMARY.md)
- [端口遷移說明](PORT_5001_MIGRATION.md)
- [測試指南](docs/TESTING_GUIDE.md)

---

**端口**: 5001 | **不要動 macOS AirPlay** ✅
