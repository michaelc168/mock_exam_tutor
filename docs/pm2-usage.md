# 使用 PM2 管理服務

## 前置

1. **安裝 PM2**（二擇一）：
   ```bash
   npm install -g pm2
   # 或專案內
   npm install --save-dev pm2
   ```

2. **後端虛擬環境與依賴**（首次或尚未做過時）：
   ```bash
   python3 -m venv backend/venv
   backend/venv/bin/pip install -r backend/requirements.txt
   ```

3. **前端依賴**（首次或尚未做過時）：
   ```bash
   cd frontend && npm install && cd ..
   ```

## 指令

| 指令 | 說明 |
|------|------|
| `pm2 start ecosystem.config.cjs` | 啟動後端 + 前端 |
| `pm2 stop ecosystem.config.cjs` | 停止全部 |
| `pm2 restart ecosystem.config.cjs` | 重啟全部 |
| `pm2 restart mock-exam-backend` | 只重啟後端 |
| `pm2 restart mock-exam-frontend` | 只重啟前端 |
| `pm2 logs` | 看所有日誌 |
| `pm2 logs mock-exam-backend` | 只看後端日誌 |
| `pm2 status` | 看進程狀態 |

或使用 npm scripts（需先有 PM2）：

```bash
npm run pm2:start    # 啟動
npm run pm2:stop     # 停止
npm run pm2:restart  # 重啟
npm run pm2:logs     # 日誌
npm run pm2:status   # 狀態
```

## 應用名稱

- **mock-exam-backend**：FastAPI，port 8000  
- **mock-exam-frontend**：Next.js，port 3000  

## 開機自啟（選用）

```bash
pm2 startup   # 依提示執行輸出的指令
pm2 save      # 儲存目前列表，重開機後會自動啟動
```

## 與 start-dev.sh 的差異

- **start-dev.sh**：用 shell 背景執行，日誌寫入 `logs/`，用 `stop-dev.sh` 停止。  
- **PM2**：統一管理、可看日誌與狀態、可只重啟單一服務、可設開機自啟。

若要用 PM2，建議先 `./stop-dev.sh` 停掉舊流程，再 `pm2 start ecosystem.config.cjs`。
