#!/bin/bash

# Mock Exam Tutor - 停止開發環境

echo "🛑 停止 Mock Exam Tutor 開發環境"
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 讀取 PID
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo -e "${GREEN}✓ 後端已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠ 後端未運行${NC}"
    fi
    rm logs/backend.pid
else
    echo -e "${YELLOW}⚠ 找不到後端 PID 檔案${NC}"
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ 前端已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠ 前端未運行${NC}"
    fi
    rm logs/frontend.pid
else
    echo -e "${YELLOW}⚠ 找不到前端 PID 檔案${NC}"
fi

# 額外清理：殺死可能殘留的 process
pkill -f "uvicorn main:app" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "node.*next" 2>/dev/null

echo ""
echo -e "${GREEN}✅ 開發環境已完全停止${NC}"
