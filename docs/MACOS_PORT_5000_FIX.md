# macOS 端口 5000 衝突解決方案

## 問題說明

在 macOS Monterey (12.0) 及以上版本，Apple 的 **AirPlay Receiver** 服務會佔用 5000 端口，導致 Flask 應用無法正常綁定該端口。

### 現象
- Flask 顯示啟動成功，但訪問 `http://localhost:5001` 會返回 **403 Forbidden**
- 錯誤訊息：`Server: AirTunes/920.10.1`

---

## 解決方案

### 🏆 方案 1：關閉 AirPlay Receiver（推薦）

這是最簡單且不影響開發體驗的方案。

#### 步驟

1. **打開系統設定**
   - 點擊左上角  圖示 → **系統設定** (System Settings)

2. **前往 AirDrop 設定**
   - 選擇 **通用** (General) → **AirDrop 與接續互通** (AirDrop & Handoff)
   - 或直接搜尋 "AirPlay"

3. **關閉 AirPlay Receiver**
   - 找到 **AirPlay Receiver** 選項
   - 將其設為 **關閉** (Off)

4. **驗證端口已釋放**
   ```bash
   # 檢查 5000 端口是否還在使用
   lsof -i :5000

   # 如果沒有輸出，表示端口已釋放
   ```

5. **重新啟動 Flask**
   ```bash
   python -m flask --app backend.main run
   ```

6. **測試**
   ```bash
   curl http://localhost:5001/health
   # 應該返回：{"status": "healthy", ...}
   ```

#### 優點
- ✅ 保持使用標準的 5000 端口
- ✅ 所有文檔和腳本無需修改
- ✅ 符合開發慣例

#### 缺點
- ❌ 如果需要使用 AirPlay 接收功能，需要重新開啟

---

### 方案 2：使用其他端口

如果您需要保留 AirPlay Receiver，可以使用其他端口。

#### 選擇 5001 端口（次要推薦）

```bash
# 啟動時指定端口
python -m flask --app backend.main run --port 5001
```

或在 `.env` 檔案中設定：

```env
PORT=5001
```

然後修改 `backend/main.py`：

```python
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
```

#### 需要修改的地方

1. **Mobile App 配置** - `mobile/tw-etf-app/services/api.ts`
   ```typescript
   const API_CONFIG = {
     DEV_URL: 'http://localhost:5001/api/v1',  // 改為 5001
   };
   ```

2. **所有測試腳本和文檔中的 URL**

---

### 方案 3：臨時關閉 AirPlay（快速測試）

如果只是臨時測試，可以使用命令行關閉：

```bash
# 關閉 AirPlay Receiver (需要 sudo)
sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.AirPlayXPCHelper.plist 2>/dev/null

# 啟動 Flask
python -m flask --app backend.main run

# 測試完成後重新啟用
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.AirPlayXPCHelper.plist 2>/dev/null
```

⚠️ **注意**：這個方法在新版 macOS 上可能無效，建議使用方案 1。

---

## 檢查與驗證

### 1. 檢查端口佔用情況

```bash
# 查看 5000 端口被誰佔用
lsof -i :5000

# 預期輸出（如果被 AirPlay 佔用）：
# COMMAND     PID      USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
# ControlCe   1274  username   10u  IPv4 0x...                TCP *:commplex-main (LISTEN)
```

### 2. 識別佔用進程

```bash
# 如果看到 "ControlCe" 或 "ControlCenter"，表示是 AirPlay
# 如果看到 "python"，表示是您的 Flask 應用
```

### 3. 測試 Flask 運行狀態

```bash
# 健康檢查
curl http://localhost:5001/health

# 預期輸出：
# {"status":"healthy","services":{"redis":"connected","finmind":"connected"}}

# 如果返回 403 或 "Server: AirTunes"，表示仍被 AirPlay 佔用
```

---

## 常見問題

### Q1: 我關閉了 AirPlay，但仍然 403？

可能是：
1. 設定未生效，需要重啟電腦
2. 有其他程式佔用 5000 端口

檢查方法：
```bash
lsof -i :5000
# 查看是什麼程式在使用
```

### Q2: 我需要用 AirPlay，但也要開發怎麼辦？

使用方案 2，改用 5001 端口，並使用我們提供的便捷腳本 `./run_dev.sh`

### Q3: 每次都要手動關閉 AirPlay 很麻煩？

可以創建一個啟動腳本自動處理（見下方）。

---

## 自動化腳本

我們已經為您創建了便捷腳本：

### `run_dev.sh` - 智能啟動腳本

```bash
./run_dev.sh
```

功能：
- ✅ 自動檢測端口佔用
- ✅ 如果 5000 被佔用，自動使用 5001
- ✅ 檢查 Redis 連接
- ✅ 檢查虛擬環境
- ✅ 啟用熱重載

---

## 推薦配置

### 開發環境（個人 Mac）
**使用方案 1** - 關閉 AirPlay Receiver
- 大部分開發者不常使用 AirPlay 接收功能
- 保持標準 5000 端口，文檔一致

### 需要 AirPlay 的情況
**使用方案 2** - 改用 5001 端口
- 使用便捷腳本 `./run_dev.sh`
- 在 `.env` 設定 `PORT=5001`

---

## 參考資料

- [Apple Developer Forums - Port 5000 Issue](https://developer.apple.com/forums/thread/682332)
- [Flask Documentation - Quickstart](https://flask.palletsprojects.com/en/latest/quickstart/)

---

**更新時間**: 2025-11-16
**適用系統**: macOS Monterey (12.0) 及以上
