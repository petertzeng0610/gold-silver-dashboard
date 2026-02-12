#!/bin/bash

# 獲取腳本所在目錄的絕對路徑
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 正在啟動台灣金銀價格追蹤系統..."

# 1. 啟動後端 (使用 uvicorn)
echo "📦 正在啟動後端服務..."
cd "$PROJECT_ROOT/backend"
# 檢查虛擬環境是否存在 (依據專案情況，這裡假設直接運行 uvicorn)
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# 2. 啟動前端 (使用 vite)
echo "🌐 正在啟動前端界面..."
cd "$PROJECT_ROOT/frontend"
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# 3. 等待幾秒確保服務啟動
echo "⏳ 等待系統初始化..."
sleep 5

# 4. 在瀏覽器中開啟
echo "🖥️  正在開啟瀏覽器..."
open "http://localhost:5173"

echo "------------------------------------------------"
echo "✅ 系統已成功啟動！"
echo "後端 PID: $BACKEND_PID (日誌: backend/backend.log)"
echo "前端 PID: $FRONTEND_PID (日誌: frontend/frontend.log)"
echo "請使用瀏覽器訪問 http://localhost:5173"
echo "------------------------------------------------"
echo "⚠️  若要關閉系統，請運行：kill $BACKEND_PID $FRONTEND_PID"
