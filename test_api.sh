#!/bin/bash

# API 測試腳本 - 自動偵測端口

# 顏色定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢測運行中的 Flask 端口
detect_port() {
    # 檢查 5000
    if curl -s http://localhost:5000/health &> /dev/null; then
        echo "5000"
        return 0
    fi
    # 檢查 5001
    if curl -s http://localhost:5001/health &> /dev/null; then
        echo "5001"
        return 0
    fi
    return 1
}

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   台股 ETF API 測試工具              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

# 偵測端口
PORT=$(detect_port)
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ 找不到運行中的 Flask 伺服器${NC}"
    echo -e "\n請先啟動伺服器："
    echo -e "  ${GREEN}./run_dev.sh${NC}"
    echo -e "  或"
    echo -e "  ${GREEN}python -m flask --app backend.main run${NC}\n"
    exit 1
fi

BASE_URL="http://localhost:$PORT"

echo -e "${GREEN}✓ 偵測到伺服器運行在端口: $PORT${NC}\n"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# 測試計數
PASSED=0
FAILED=0

# 測試函數
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3

    echo -e "${BLUE}測試:${NC} $name"
    echo -e "${YELLOW}URL:${NC} $url"

    response=$(curl -s "$url" 2>&1)

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ 通過${NC}\n"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失敗${NC}"
        echo -e "${RED}回應:${NC} ${response:0:100}...\n"
        ((FAILED++))
        return 1
    fi
}

# 1. 健康檢查
test_endpoint \
    "健康檢查" \
    "$BASE_URL/health" \
    "healthy"

# 2. 首頁
test_endpoint \
    "API 首頁" \
    "$BASE_URL/" \
    "台股 ETF API"

# 3. ETF 列表
test_endpoint \
    "ETF 列表 (前 5 筆)" \
    "$BASE_URL/api/v1/etf/etfs?limit=5" \
    '"success":true'

# 4. ETF 詳情
test_endpoint \
    "ETF 詳情 (0050)" \
    "$BASE_URL/api/v1/etf/etf/0050" \
    "元大台灣50"

# 5. 搜尋功能
test_endpoint \
    "搜尋功能 (台積電)" \
    "$BASE_URL/api/v1/search?q=台積電" \
    "2330"

# 6. Swagger 文件
echo -e "${BLUE}測試:${NC} Swagger API 文件"
echo -e "${YELLOW}URL:${NC} $BASE_URL/api/v1/"

if curl -s "$BASE_URL/api/v1/" | grep -qi "swagger\|api documentation"; then
    echo -e "${GREEN}✓ 通過${NC}\n"
    ((PASSED++))
else
    # Swagger 可能返回 HTML，用不同方式檢查
    if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/" | grep -q "200"; then
        echo -e "${GREEN}✓ 通過 (HTTP 200)${NC}\n"
        ((PASSED++))
    else
        echo -e "${RED}✗ 失敗${NC}\n"
        ((FAILED++))
    fi
fi

# 總結
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}測試總結${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "  ${GREEN}✓ 通過:${NC} $PASSED"
echo -e "  ${RED}✗ 失敗:${NC} $FAILED"
echo -e "  總計: $((PASSED + FAILED))\n"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有測試通過！${NC}\n"
else
    echo -e "${YELLOW}⚠ 部分測試失敗，請檢查上述輸出${NC}\n"
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}快速連結${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "  📖 Swagger 文件: ${BLUE}$BASE_URL/api/v1/${NC}"
echo -e "  🏠 API 首頁:     ${BLUE}$BASE_URL/${NC}"
echo -e "  💚 健康檢查:     ${BLUE}$BASE_URL/health${NC}\n"

echo -e "${YELLOW}提示: 在瀏覽器中打開 Swagger 文件以查看完整 API 說明${NC}\n"

exit $FAILED
