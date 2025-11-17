#!/bin/bash

# 台股 ETF API 智能開發伺服器啟動腳本
# 自動處理 macOS AirPlay 端口衝突問題

set -e

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   台股 ETF API 開發伺服器 v2.0       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# ============================================================
# 1. 檢查虛擬環境
# ============================================================
echo -e "${BLUE}[1/5]${NC} 檢查 Python 虛擬環境..."
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠ 警告: 虛擬環境未啟動${NC}"
    echo -e "請先執行: ${GREEN}source venv/bin/activate${NC}\n"
    read -p "是否繼續？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ 虛擬環境已啟動: $VIRTUAL_ENV${NC}\n"
fi

# ============================================================
# 2. 檢查 Redis
# ============================================================
echo -e "${BLUE}[2/5]${NC} 檢查 Redis 連接..."
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓ Redis 正在運行 (redis-cli)${NC}\n"
elif docker ps 2>/dev/null | grep -q redis; then
    echo -e "${GREEN}✓ Redis 正在運行 (Docker)${NC}\n"
else
    echo -e "${YELLOW}⚠ Redis 未運行${NC}"
    echo "請先啟動 Redis："
    echo -e "  ${GREEN}方案 1:${NC} docker run -d -p 6379:6379 --name redis redis:7-alpine"
    echo -e "  ${GREEN}方案 2:${NC} brew services start redis\n"
    read -p "是否繼續（不建議）？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ============================================================
# 3. 檢查 .env 檔案
# ============================================================
echo -e "${BLUE}[3/5]${NC} 檢查環境配置..."
if [[ ! -f .env ]]; then
    echo -e "${RED}✗ .env 檔案不存在${NC}"
    echo -e "請先複製範本: ${GREEN}cp .env.example .env${NC}"
    exit 1
else
    echo -e "${GREEN}✓ .env 檔案存在${NC}\n"
fi

# ============================================================
# 4. 智能端口選擇（處理 macOS AirPlay 衝突）
# ============================================================
echo -e "${BLUE}[4/5]${NC} 檢測端口可用性..."

# 從 .env 讀取端口設定（如果有）
if [[ -f .env ]]; then
    ENV_PORT=$(grep -E "^PORT=" .env 2>/dev/null | cut -d '=' -f2 | tr -d ' \r\n' || echo "")
fi

# 優先使用 .env 中的 PORT，否則使用 5001
PREFERRED_PORT=${ENV_PORT:-5001}
PORT=$PREFERRED_PORT

# 檢查端口是否被佔用
check_port() {
    local port=$1
    if lsof -i :$port &> /dev/null; then
        local process=$(lsof -i :$port 2>/dev/null | grep LISTEN | awk '{print $1}' | head -n 1)
        echo "$process"
        return 1
    fi
    return 0
}

# 檢查偏好端口
if ! check_port $PORT > /dev/null 2>&1; then
    BLOCKING_PROCESS=$(check_port $PORT 2>/dev/null || echo "Unknown")

    # 檢查是否被 macOS ControlCenter (AirPlay) 或其他程式佔用
    echo -e "${RED}✗ 端口 $PORT 被 $BLOCKING_PROCESS 佔用${NC}\n"

    if [[ "$BLOCKING_PROCESS" == "ControlCe" ]] || [[ "$BLOCKING_PROCESS" == "ControlCenter" ]]; then
        echo -e "${YELLOW}說明: macOS AirPlay Receiver 佔用了端口 $PORT${NC}"
        echo -e "${YELLOW}本專案預設使用 5001 端口以避免此衝突${NC}\n"
        echo -e "${BLUE}請檢查：${NC}"
        echo -e "  1. 您的 .env 檔案中 PORT 設定是否為 5001"
        echo -e "  2. 確認沒有手動指定其他端口\n"
    else
        echo -e "${BLUE}請先停止佔用端口 $PORT 的程式：${NC}"
        echo -e "  ${GREEN}lsof -ti:$PORT | xargs kill -9${NC}\n"
    fi
    exit 1
else
    echo -e "${GREEN}✓ 端口 $PORT 可用${NC}\n"
fi

# ============================================================
# 5. 啟動 Flask 開發伺服器
# ============================================================
echo -e "${BLUE}[5/5]${NC} 啟動 Flask 開發伺服器...\n"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  端口:${NC} $PORT"
echo -e "${GREEN}  模式:${NC} 開發模式 (熱重載)"
echo -e "${GREEN}  環境:${NC} $(grep FLASK_ENV .env 2>/dev/null | cut -d '=' -f2 || echo 'development')"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${BLUE}📖 API 文件:${NC}"
echo -e "   • Swagger UI: ${BLUE}http://localhost:$PORT/api/v1/${NC}"
echo -e "   • 健康檢查:   ${BLUE}http://localhost:$PORT/health${NC}"
echo -e "   • 首頁:       ${BLUE}http://localhost:$PORT/${NC}\n"

echo -e "${YELLOW}按 Ctrl+C 停止伺服器${NC}\n"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 啟動 Flask
export FLASK_APP=backend.main
export FLASK_ENV=development

python -m flask run --port $PORT --reload

# 如果伺服器停止
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}伺服器已停止${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
