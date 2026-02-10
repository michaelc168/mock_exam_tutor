#!/bin/bash

# Mock Exam Tutor - 開發環境啟動腳本

echo "🚀 啟動 Mock Exam Tutor 開發環境"
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 找不到 Python3，請先安裝${NC}"
    exit 1
fi

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ 找不到 Node.js，請先安裝${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python3 已安裝: $(python3 --version)${NC}"
echo -e "${GREEN}✓ Node.js 已安裝: $(node --version)${NC}"
echo ""

# 檢查後端依賴
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ 找不到 backend/main.py${NC}"
    exit 1
fi

# 建立虛擬環境（如果不存在）
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}📦 建立 Python 虛擬環境...${NC}"
    python3 -m venv backend/venv
fi

# 啟動虛擬環境並安裝依賴
echo -e "${YELLOW}📦 檢查 Python 依賴...${NC}"
source backend/venv/bin/activate
pip install -q -r backend/requirements.txt

# 檢查前端依賴
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 安裝前端依賴...${NC}"
    cd frontend
    if command -v pnpm &> /dev/null; then
        pnpm install
    else
        npm install
    fi
    cd ..
fi

echo ""
echo -e "${GREEN}✓ 所有依賴已就緒${NC}"
echo ""

# 建立日誌資料夾
mkdir -p logs

# 啟動後端
echo -e "${YELLOW}🔧 啟動後端 (FastAPI)...${NC}"
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo -e "${GREEN}✓ 後端已啟動 (PID: $BACKEND_PID)${NC}"
echo -e "  URL: ${GREEN}http://localhost:8000${NC}"
echo -e "  API 文檔: ${GREEN}http://localhost:8000/docs${NC}"
echo ""

# 等待後端啟動
sleep 2

# 啟動前端
echo -e "${YELLOW}🎨 啟動前端 (Next.js)...${NC}"
cd frontend
if command -v pnpm &> /dev/null; then
    pnpm dev > ../logs/frontend.log 2>&1 &
else
    npm run dev > ../logs/frontend.log 2>&1 &
fi
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✓ 前端已啟動 (PID: $FRONTEND_PID)${NC}"
echo -e "  URL: ${GREEN}http://localhost:3000${NC}"
echo ""

# 儲存 PID
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}✨ Mock Exam Tutor 已成功啟動！${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "前端：${GREEN}http://localhost:3000${NC}"
echo -e "後端：${GREEN}http://localhost:8000${NC}"
echo -e "API 文檔：${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "日誌檔案："
echo -e "  - logs/backend.log"
echo -e "  - logs/frontend.log"
echo ""
echo -e "停止服務："
echo -e "  ${YELLOW}./stop-dev.sh${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 不會停止服務（服務在背景執行）${NC}"
echo ""

# 等待一下讓服務完全啟動
sleep 3

# 嘗試開啟瀏覽器
if command -v open &> /dev/null; then
    echo -e "${GREEN}🌐 正在開啟瀏覽器...${NC}"
    open http://localhost:3000
fi
