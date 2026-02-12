# 使用 Python 3.11 輕量版
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴 (針對 psycopg2 等)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製其餘代碼
COPY . .

# 暴露預設端口
EXPOSE 8000

# 使用環境變數啟動，若無 PORT 變數則預設 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
