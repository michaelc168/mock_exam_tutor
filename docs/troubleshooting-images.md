# 圖片顯示問題排查

## 🔍 診斷步驟

### 1. 檢查 API 是否正常

```bash
# 測試圖片 API
curl -I http://localhost:8000/api/images/triangle-demo.png

# 應該返回 200 OK
```

### 2. 檢查考卷資料是否包含圖片

```bash
# 測試考卷 API
curl -s http://localhost:8000/api/quiz/math-exam-with-images | jq '.questions[0].question'

# 應該看到：![xxx](../images/xxx.png)
```

### 3. 在瀏覽器中測試

1. 打開 http://localhost:3000/exams
2. 找到 `math-exam-with-images`
3. 點擊「開始作答」
4. **按 F12 打開開發者工具**
5. 查看 Console 是否有錯誤
6. 查看 Network 標籤，檢查圖片是否成功載入

### 4. 檢查 LatexRenderer 組件

打開瀏覽器開發者工具，在 Console 執行：

```javascript
// 檢查圖片元素是否存在
document.querySelectorAll('img').length

// 列出所有圖片 src
Array.from(document.querySelectorAll('img')).map(img => img.src)
```

### 5. 手動測試圖片 URL

在瀏覽器位址列直接訪問：
```
http://localhost:8000/api/images/triangle-demo.png
```

應該看到三角形圖片。

## 🐛 常見問題

### 問題 1: 圖片不顯示

**檢查**：
1. 檢查 Console 是否有 CORS 錯誤
2. 檢查圖片 URL 是否正確
3. 檢查 Network 標籤，圖片請求狀態碼

**解決**：
- 確認後端 CORS 設定正確
- 確認 `NEXT_PUBLIC_API_URL` 環境變數

### 問題 2: 圖片顯示為 broken image

**檢查**：
```bash
# 檢查圖片文件是否存在
ls -la /Users/michael/mock_exam_tutor/exams/images/

# 測試圖片 API
curl http://localhost:8000/api/images/triangle-demo.png --output test.png
file test.png
```

### 問題 3: LatexRenderer 沒有處理圖片

**原因**：組件可能沒有正確掛載

**檢查**：
1. 打開開發者工具 React DevTools
2. 找到 `LatexRenderer` 組件
3. 查看 props.content 是否包含圖片 Markdown

## 🧪 測試頁面

已建立測試頁面：`test-image-render.html`

```bash
open /Users/michael/mock_exam_tutor/test-image-render.html
```

此頁面會測試：
- ✅ 純圖片渲染
- ✅ 圖片 + 文字
- ✅ 圖片 + LaTeX

## 📋 檢查清單

- [ ] 後端服務運行中 (`uvicorn` 進程存在)
- [ ] 前端服務運行中 (`next dev` 進程存在)
- [ ] 圖片文件存在於 `exams/images/`
- [ ] 圖片 API 可訪問 (200 OK)
- [ ] 考卷 API 包含圖片 Markdown
- [ ] LatexRenderer 組件已導入
- [ ] 瀏覽器 Console 無錯誤

## 🔧 快速修復

如果圖片仍然不顯示，嘗試：

```bash
# 1. 重啟後端
pkill -f uvicorn
cd backend && source venv/bin/activate && python -m uvicorn main:app --reload --port 8000 &

# 2. 重啟前端
pkill -f "next dev"
cd frontend && npm run dev &

# 3. 清除瀏覽器快取
# 在瀏覽器中按 Cmd+Shift+R 強制重新載入
```

## 📸 預期效果

圖片應該：
- ✅ 置中顯示
- ✅ 自適應寬度（max-width: 100%）
- ✅ 上下有適當邊距
- ✅ 與題目文字分離
- ✅ LaTeX 公式正常渲染

---

**建立時間**：2026-02-11  
**用途**：診斷圖片顯示問題
