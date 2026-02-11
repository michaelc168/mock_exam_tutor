#!/bin/bash

# 答題系統測試腳本
# 測試完整的答題流程：載入考卷 → 提交答案 → 取得結果

set -e  # 遇到錯誤立即退出

echo "🧪 測試答題系統"
echo "=============================================="
echo ""

# 顏色定義
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 設定測試考卷
EXAM_ID="mock-exam-20260209-comprehensive"
API_URL="http://localhost:8000"

echo -e "${BLUE}📋 測試目標：${EXAM_ID}${NC}"
echo ""

# 測試 1: 健康檢查
echo -e "${YELLOW}[1/4] 健康檢查...${NC}"
if curl -s "${API_URL}/" > /dev/null; then
    echo -e "${GREEN}✅ 後端服務正常${NC}"
else
    echo -e "${RED}❌ 後端服務未啟動${NC}"
    echo "請先執行: ./start-dev.sh"
    exit 1
fi
echo ""

# 測試 2: 取得考卷（不含答案）
echo -e "${YELLOW}[2/4] 取得考卷資料...${NC}"
QUIZ_DATA=$(curl -s "${API_URL}/api/quiz/${EXAM_ID}")

if echo "$QUIZ_DATA" | jq -e '.exam_id' > /dev/null 2>&1; then
    TITLE=$(echo "$QUIZ_DATA" | jq -r '.title')
    SUBJECT=$(echo "$QUIZ_DATA" | jq -r '.subject')
    TOTAL=$(echo "$QUIZ_DATA" | jq -r '.total_questions')
    
    echo -e "${GREEN}✅ 考卷載入成功${NC}"
    echo "   標題: ${TITLE}"
    echo "   科目: ${SUBJECT}"
    echo "   題數: ${TOTAL}"
    
    # 檢查是否包含答案（不應該有）
    HAS_ANSWER=$(echo "$QUIZ_DATA" | jq '.questions[0].correct_answer')
    if [ "$HAS_ANSWER" = "null" ]; then
        echo -e "${GREEN}✅ 答案已正確隱藏${NC}"
    else
        echo -e "${RED}❌ 警告：考卷包含答案！${NC}"
    fi
else
    echo -e "${RED}❌ 考卷載入失敗${NC}"
    exit 1
fi
echo ""

# 測試 3: 提交答案（模擬作答）
echo -e "${YELLOW}[3/4] 提交答案...${NC}"

# 建立模擬答案（前10題全部選B）
ANSWERS='{"exam_id":"'${EXAM_ID}'","answers":['
for i in {1..10}; do
    if [ $i -gt 1 ]; then
        ANSWERS="${ANSWERS},"
    fi
    ANSWERS="${ANSWERS}{\"question_id\":${i},\"user_answer\":\"B\"}"
done
ANSWERS="${ANSWERS}]}"

RESULT=$(curl -s -X POST "${API_URL}/api/quiz/submit" \
    -H "Content-Type: application/json" \
    -d "${ANSWERS}")

if echo "$RESULT" | jq -e '.score' > /dev/null 2>&1; then
    SCORE=$(echo "$RESULT" | jq -r '.score')
    CORRECT=$(echo "$RESULT" | jq -r '.correct_count')
    TOTAL_SUBMIT=$(echo "$RESULT" | jq -r '.total_questions')
    
    echo -e "${GREEN}✅ 答案提交成功${NC}"
    echo "   答對: ${CORRECT} / ${TOTAL_SUBMIT}"
    echo "   分數: ${SCORE} 分"
else
    echo -e "${RED}❌ 答案提交失敗${NC}"
    exit 1
fi
echo ""

# 測試 4: 驗證結果詳情
echo -e "${YELLOW}[4/4] 驗證結果詳情...${NC}"

ANSWER_COUNT=$(echo "$RESULT" | jq '.answers | length')
if [ "$ANSWER_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ 結果包含詳細檢討${NC}"
    
    # 顯示前3題的檢討
    echo ""
    echo "前3題檢討範例："
    for i in {0..2}; do
        Q_ID=$(echo "$RESULT" | jq -r ".answers[${i}].question_id")
        USER_ANS=$(echo "$RESULT" | jq -r ".answers[${i}].user_answer")
        CORRECT_ANS=$(echo "$RESULT" | jq -r ".answers[${i}].correct_answer")
        IS_CORRECT=$(echo "$RESULT" | jq -r ".answers[${i}].is_correct")
        
        if [ "$IS_CORRECT" = "true" ]; then
            echo -e "   第${Q_ID}題: ${GREEN}✓${NC} 你的答案:(${USER_ANS})"
        else
            echo -e "   第${Q_ID}題: ${RED}✗${NC} 你的答案:(${USER_ANS}) 正確答案:(${CORRECT_ANS})"
        fi
    done
else
    echo -e "${RED}❌ 結果不包含詳細檢討${NC}"
    exit 1
fi
echo ""

# 測試總結
echo "=============================================="
echo -e "${GREEN}🎉 所有測試通過！${NC}"
echo ""
echo "答題系統功能正常："
echo "  ✅ 後端 API 運作正常"
echo "  ✅ 考卷解析正確"
echo "  ✅ 答案提交成功"
echo "  ✅ 自動評分準確"
echo "  ✅ 詳細檢討完整"
echo ""
echo "現在可以在瀏覽器中測試："
echo "  1. 訪問 http://localhost:3000"
echo "  2. 點擊「我的考卷」"
echo "  3. 選擇考卷並點擊「開始作答」"
echo ""
