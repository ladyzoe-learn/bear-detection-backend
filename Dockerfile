# Dockerfile for Render Backend (bear-detection-backend)

# 使用 Python 3.9 映像作為基礎映像，與 Hugging Face Space 保持一致
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 並安裝 Python 依賴
# Render 後端只需要 FastAPI, Uvicorn, httpx (用於呼叫 HF Space API)
# Pillow 和 numpy 在 main.py 中用於處理圖片內容，即使不直接推論也可能有用，可以保留
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有應用程式程式碼到工作目錄
# 這會包含您的 main.py 檔案
COPY . .

# 定義應用程式啟動命令
# Render 會自動設置 PORT 環境變數，讓您的應用程式監聽該端口
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]


