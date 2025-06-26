FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 創建必要目錄
RUN mkdir -p src/static/uploads src/database models

# 暴露端口
EXPOSE 5000

# 設置環境變數
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/src

# 啟動命令
CMD ["python", "src/main.py"]

