#!/bin/bash

# 快速測試系統各組件是否正常

echo "🧪 測試 Mock Exam Tutor 系統"
echo ""

# 顏色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 測試計數
PASS=0
FAIL=0

# 測試函數
test_command() {
    if eval "$1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAIL++))
    fi
}

test_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAIL++))
    fi
}

test_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAIL++))
    fi
}

echo "=== 環境檢查 ==="
test_command "command -v python3" "Python3 已安裝"
test_command "command -v node" "Node.js 已安裝"
test_command "command -v npm" "npm 已安裝"
test_command "python3 -c 'import fastapi'" "FastAPI 已安裝（後端依賴）"

echo ""
echo "=== 檔案結構 ==="
test_dir "backend" "backend/ 資料夾"
test_file "backend/main.py" "backend/main.py"
test_file "backend/requirements.txt" "backend/requirements.txt"
test_dir "frontend" "frontend/ 資料夾"
test_file "frontend/package.json" "frontend/package.json"
test_file "frontend/app/page.tsx" "frontend/app/page.tsx"

echo ""
echo "=== 考題資料 ==="
test_dir "exams" "exams/ 資料夾"
test_dir "exams/bank" "exams/bank/ 資料夾"
test_dir "exams/generated" "exams/generated/ 資料夾"
test_file "exams/bank/chinese-gr6-bank.md" "國語題庫"
test_file "exams/bank/english-gr6-bank.md" "英語題庫"
test_file "exams/bank/math-gr6-bank.md" "數學題庫"

echo ""
echo "=== 腳本工具 ==="
test_file "scripts/convert-to-pdf.js" "PDF 轉換腳本"
test_file "start-dev.sh" "啟動腳本"
test_file "stop-dev.sh" "停止腳本"

echo ""
echo "=== 前端設定 ==="
test_file "frontend/.env.local" ".env.local 環境變數"
test_file "frontend/lib/api.ts" "API 客戶端"

echo ""
echo "=== 測試結果 ==="
echo -e "${GREEN}通過: $PASS${NC}"
echo -e "${RED}失敗: $FAIL${NC}"

if [ $FAIL -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 所有測試通過！系統已準備就緒${NC}"
    echo ""
    echo "執行以下指令啟動系統："
    echo -e "  ${YELLOW}./start-dev.sh${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ 有 $FAIL 項測試失敗，請檢查上方錯誤${NC}"
    exit 1
fi
