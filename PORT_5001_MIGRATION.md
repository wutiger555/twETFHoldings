# 🔄 端口遷移至 5001 完成

> **更新日期**: 2025-11-16
> **版本**: v2.0.2
> **重大變更**: 所有配置已從 5000 端口遷移至 5001

---

## 📋 變更原因

### 問題
macOS Monterey (12.0+) 的 **AirPlay Receiver** 預設佔用 5000 端口，導致：
- Flask 應用無法正常啟動
- 訪問 localhost:5000 返回 403 Forbidden
- 需要每次手動關閉 AirPlay 或調整設定

### 解決方案
**統一使用 5001 端口**，避免與 macOS 系統服務衝突。

---

## ✅ 已完成的變更

### 1. 配置文件

| 文件 | 變更內容 |
|------|---------|
| **.env.example** | `PORT=5000` → `PORT=5001` |
| **.env** | `PORT=5000` → `PORT=5001` (如果存在) |
| **backend/main.py** | 預設端口 5000 → 5001 |
| **backend/config.py** | 無需修改（使用環境變數） |

### 2. Docker 配置

| 文件 | 變更內容 |
|------|---------|
| **Dockerfile** | `EXPOSE 5000` → `EXPOSE 5001` |
| **Dockerfile** | 健康檢查 URL 更新 |
| **Dockerfile** | gunicorn 綁定端口更新 |
| **docker-compose.yml** | 端口映射 `5000:5000` → `5001:5001` |

### 3. Mobile App

| 文件 | 變更內容 |
|------|---------|
| **mobile/tw-etf-app/services/api.ts** | API URL localhost:5000 → localhost:5001 |

### 4. 啟動腳本

| 文件 | 變更內容 |
|------|---------|
| **run_dev.sh** | 預設端口 5000 → 5001 |
| **run_dev.sh** | 更新端口衝突檢測邏輯 |
| **test_api.sh** | 自動偵測端口（支援 5001） |

### 5. 文檔更新

所有文檔中的端口參考已更新：

| 文檔 | 狀態 |
|------|------|
| **README.md** | ✅ 已更新 |
| **CHANGES_SUMMARY.md** | ✅ 已更新 |
| **docs/COMPLETE_SETUP_GUIDE.md** | ✅ 已更新 |
| **docs/SETUP_SUMMARY.md** | ✅ 已更新 |
| **docs/QUICK_START.md** | ✅ 已更新 |
| **docs/TESTING_GUIDE.md** | ✅ 已更新 |
| **docs/DEPLOYMENT_GUIDE.md** | ✅ 已更新 |
| **docs/MOBILE_APP_GUIDE.md** | ✅ 已更新 |
| **docs/MACOS_PORT_5000_FIX.md** | ✅ 已更新 |
| **mobile/README.md** | ✅ 已更新 |

---

## 🚀 立即使用

### 如果您已經在運行 Flask

1. **停止當前的伺服器** （按 Ctrl+C）

2. **重新啟動**
   ```bash
   ./run_dev.sh
   ```
   腳本會自動使用 5001 端口

3. **訪問新的 URL**
   - Swagger: http://localhost:5001/api/v1/
   - 健康檢查: http://localhost:5001/health
   - API 首頁: http://localhost:5001/

### 新安裝

```bash
# 1. Clone 專案
git clone https://github.com/your-username/twETFHoldings.git
cd twETFHoldings

# 2. 設定環境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 複製環境變數（已預設為 5001）
cp .env.example .env

# 4. 啟動 Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 5. 啟動服務
./run_dev.sh

# 完成！服務運行在 http://localhost:5001
```

---

## 📖 重要 URL 變更對照

### 本地開發

| 服務 | 舊 URL (5000) | 新 URL (5001) |
|------|--------------|---------------|
| **Swagger** | ~~localhost:5000/api/v1/~~ | **localhost:5001/api/v1/** |
| **健康檢查** | ~~localhost:5000/health~~ | **localhost:5001/health** |
| **API 首頁** | ~~localhost:5000/~~ | **localhost:5001/** |
| **ETF 列表** | ~~localhost:5000/api/v1/etf/etfs~~ | **localhost:5001/api/v1/etf/etfs** |

### Docker

```bash
# 舊配置
docker-compose up -d
curl http://localhost:5000/health

# 新配置
docker-compose up -d
curl http://localhost:5001/health
```

---

## 🔧 驗證變更

### 檢查配置

```bash
# 1. 檢查 .env 檔案
grep "^PORT=" .env
# 應該顯示: PORT=5001

# 2. 檢查環境變數範本
grep "^PORT=" .env.example
# 應該顯示: PORT=5001
```

### 測試運行

```bash
# 1. 啟動服務
./run_dev.sh

# 2. 在新終端測試
./test_api.sh

# 3. 手動測試
curl http://localhost:5001/health
# 應返回: {"status":"healthy",...}

# 4. 在瀏覽器打開
open http://localhost:5001/api/v1/
```

---

## 📱 Mobile App 開發者注意

### API 端點已更新

```typescript
// mobile/tw-etf-app/services/api.ts

const API_CONFIG = {
  DEV_URL: 'http://localhost:5001/api/v1',  // 已更新
  PROD_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:5001/api/v1',
};
```

### 如果使用模擬器/實體機

**iOS 模擬器**:
```typescript
DEV_URL: 'http://localhost:5001/api/v1'  // ✅ 正確
```

**Android 模擬器**:
```typescript
DEV_URL: 'http://10.0.2.2:5001/api/v1'   // ✅ 正確
```

**實體設備**:
```typescript
DEV_URL: 'http://YOUR_IP:5001/api/v1'   // 替換 YOUR_IP
```

---

## 🐳 Docker 部署

### Docker Compose

```yaml
# docker-compose.yml (已更新)

services:
  backend:
    build: .
    ports:
      - "5001:5001"  # 已更新
```

```bash
# 啟動
docker-compose up -d

# 測試
curl http://localhost:5001/health
```

### Dockerfile

```dockerfile
# Dockerfile (已更新)

EXPOSE 5001

HEALTHCHECK CMD python -c "import requests; requests.get('http://localhost:5001/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "120", "backend.main:app"]
```

---

## ☁️ 雲端部署注意事項

### Railway / Render / Fly.io

這些平台通常會：
1. 自動設定 `PORT` 環境變數
2. 或使用預設的 5000 端口

### 建議配置

在部署平台的環境變數設定：
```env
PORT=5001
```

或者使用平台提供的 PORT（通常是動態分配）：
```python
# backend/main.py 已支援
port = int(os.getenv('PORT', 5001))
```

---

## 🔍 故障排除

### Q1: 啟動後仍然是 5000 端口？

**檢查清單**:
```bash
# 1. 確認 .env 檔案
grep "^PORT=" .env

# 2. 確認沒有手動指定端口
ps aux | grep flask

# 3. 重新啟動
./run_dev.sh
```

### Q2: 5001 端口也被佔用？

```bash
# 查看佔用端口的程式
lsof -i :5001

# 停止佔用的程式
lsof -ti:5001 | xargs kill -9

# 重新啟動
./run_dev.sh
```

### Q3: Docker 容器啟動失敗？

```bash
# 重新建置
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 查看日誌
docker-compose logs -f backend
```

### Q4: Mobile App 無法連接？

```bash
# 1. 確認後端運行在 5001
curl http://localhost:5001/health

# 2. 檢查 Mobile App 配置
grep "DEV_URL" mobile/tw-etf-app/services/api.ts

# 3. 清除 Mobile App 快取
# 在 Expo: Ctrl+C → 按 c (clear cache)
```

---

## 📊 變更統計

| 類別 | 變更數量 |
|------|---------|
| **配置文件** | 5 個 |
| **Docker 文件** | 2 個 |
| **程式碼文件** | 2 個 |
| **啟動腳本** | 2 個 |
| **文檔文件** | 10+ 個 |
| **總計** | 21+ 個文件 |

---

## ✨ 優勢總結

### 使用 5001 端口的好處

1. **✅ 避免 macOS 衝突**
   - 不再需要關閉 AirPlay Receiver
   - 不受系統服務影響

2. **✅ 統一開發環境**
   - 所有開發者使用相同端口
   - 文檔和範例保持一致

3. **✅ 簡化設定流程**
   - 開箱即用
   - 減少故障排除時間

4. **✅ 靈活部署**
   - 本地開發使用 5001
   - 生產環境可自訂 PORT

---

## 🎯 下一步

### 立即使用

```bash
# 啟動開發伺服器
./run_dev.sh

# 在瀏覽器打開
open http://localhost:5001/api/v1/
```

### 開始開發

1. **查看 Swagger 文件**: http://localhost:5001/api/v1/
2. **測試 API**: `./test_api.sh`
3. **開發 Mobile App**: 更新 API URL 後重新啟動

---

## 📚 相關文檔

- [完整設定指南](docs/COMPLETE_SETUP_GUIDE.md)
- [設定總結](docs/SETUP_SUMMARY.md)
- [macOS 端口修復](docs/MACOS_PORT_5000_FIX.md)
- [變更總結](CHANGES_SUMMARY.md)

---

**🎉 恭喜！端口遷移已完成**

現在您可以：
- 保持 macOS AirPlay 功能
- 無需手動配置端口
- 使用統一的 5001 端口進行開發

**祝您開發愉快！** 🚀
