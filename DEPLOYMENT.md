# 台灣黑熊檢測系統 - 部署指南

本指南將協助您將台灣黑熊檢測系統後端API部署到各種環境中。

## 部署前準備

### 1. 檢查清單

- [ ] Python 3.11+ 已安裝
- [ ] Git 已安裝
- [ ] 擁有訓練好的 `best.pt` YOLO模型檔案
- [ ] 已測試本地開發環境

### 2. 檔案準備

確保以下檔案存在：
- `requirements.txt` - Python依賴清單
- `src/main.py` - 主程式入口
- `models/best.pt` - YOLO模型檔案 (用戶提供)
- `README.md` - 專案說明

## 本地部署

### 開發環境設置

```bash
# 1. 克隆專案
git clone <your-repository-url>
cd bear-detection-backend

# 2. 創建虛擬環境
python -m venv venv

# 3. 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 放置模型檔案
# 將 best.pt 複製到 models/ 目錄

# 6. 啟動服務
python src/main.py
```

### 生產環境設置

```bash
# 使用 Gunicorn 作為 WSGI 服務器
pip install gunicorn

# 啟動生產服務器
gunicorn --bind 0.0.0.0:5000 --workers 4 src.main:app
```

## 雲端部署

### 1. Render.com 部署

Render.com 是推薦的免費雲端部署平台。

#### 步驟：

1. **準備 GitHub 倉庫**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **創建 Render 服務**
   - 訪問 [render.com](https://render.com)
   - 點擊 "New +" → "Web Service"
   - 連接您的 GitHub 倉庫

3. **配置設置**
   - **Name**: `bear-detection-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`
   - **Instance Type**: `Free` (或根據需求選擇)

4. **環境變數設置**
   ```
   FLASK_ENV=production
   PYTHONPATH=/opt/render/project/src
   ```

5. **部署**
   - 點擊 "Create Web Service"
   - 等待部署完成 (約5-10分鐘)

#### 注意事項：
- 免費方案有使用限制
- 服務會在無活動時休眠
- 檔案系統是臨時的，重啟後上傳的檔案會消失

### 2. Heroku 部署

#### 準備檔案

創建 `Procfile`：
```
web: python src/main.py
```

創建 `runtime.txt`：
```
python-3.11.0
```

#### 部署步驟

```bash
# 1. 安裝 Heroku CLI
# 下載並安裝：https://devcenter.heroku.com/articles/heroku-cli

# 2. 登入 Heroku
heroku login

# 3. 創建應用
heroku create your-app-name

# 4. 設置環境變數
heroku config:set FLASK_ENV=production

# 5. 部署
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# 6. 開啟應用
heroku open
```

### 3. Railway 部署

Railway 是另一個簡單的部署選項。

#### 步驟：

1. 訪問 [railway.app](https://railway.app)
2. 點擊 "Start a New Project"
3. 選擇 "Deploy from GitHub repo"
4. 選擇您的倉庫
5. Railway 會自動檢測 Python 專案並部署

### 4. DigitalOcean App Platform

#### 步驟：

1. 創建 `app.yaml`：
```yaml
name: bear-detection-backend
services:
- name: api
  source_dir: /
  github:
    repo: your-username/bear-detection-backend
    branch: main
  run_command: python src/main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: production
```

2. 使用 DigitalOcean CLI 或 Web 界面部署

## Docker 部署

### 創建 Dockerfile

```dockerfile
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
RUN mkdir -p src/static/uploads src/database

# 暴露端口
EXPOSE 5000

# 設置環境變數
ENV FLASK_ENV=production
ENV PYTHONPATH=/app/src

# 啟動命令
CMD ["python", "src/main.py"]
```

### 創建 docker-compose.yml

```yaml
version: '3.8'

services:
  bear-detection-api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./models:/app/models
      - ./uploads:/app/src/static/uploads
      - ./database:/app/src/database
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

### Docker 部署命令

```bash
# 構建映像
docker build -t bear-detection-backend .

# 運行容器
docker run -d \
  --name bear-detection \
  -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/uploads:/app/src/static/uploads \
  bear-detection-backend

# 或使用 docker-compose
docker-compose up -d
```

## 環境配置

### 環境變數

| 變數名 | 描述 | 預設值 |
|--------|------|--------|
| `FLASK_ENV` | Flask 環境 | `development` |
| `DATABASE_URL` | 數據庫 URL | SQLite 本地檔案 |
| `MODEL_PATH` | YOLO 模型路徑 | 自動搜尋 |
| `UPLOAD_FOLDER` | 上傳檔案目錄 | `src/static/uploads` |
| `MAX_CONTENT_LENGTH` | 最大檔案大小 | `16MB` |

### 生產環境建議

1. **使用 HTTPS**
   - 配置 SSL 憑證
   - 使用反向代理 (Nginx)

2. **數據庫**
   - 考慮使用 PostgreSQL 替代 SQLite
   - 設置數據庫備份

3. **檔案存儲**
   - 使用雲端存儲 (AWS S3, Google Cloud Storage)
   - 配置 CDN 加速

4. **監控和日誌**
   - 設置應用監控
   - 配置日誌收集

## 故障排除

### 常見部署問題

1. **依賴安裝失敗**
   ```bash
   # 更新 pip
   pip install --upgrade pip
   
   # 清除快取
   pip cache purge
   ```

2. **模型檔案過大**
   - 使用 Git LFS 管理大檔案
   - 考慮模型壓縮

3. **記憶體不足**
   - 增加服務器記憶體
   - 優化模型載入

4. **端口衝突**
   ```bash
   # 檢查端口使用
   netstat -tulpn | grep :5000
   
   # 殺死佔用進程
   sudo kill -9 <PID>
   ```

### 性能優化

1. **使用 Gunicorn**
   ```bash
   gunicorn --workers 4 --bind 0.0.0.0:5000 src.main:app
   ```

2. **啟用快取**
   - 實施 Redis 快取
   - 配置 HTTP 快取標頭

3. **數據庫優化**
   - 添加適當索引
   - 實施連接池

## 維護指南

### 定期維護任務

1. **更新依賴**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

2. **清理日誌**
   ```bash
   # 清理舊日誌檔案
   find /var/log -name "*.log" -mtime +30 -delete
   ```

3. **數據庫維護**
   ```bash
   # SQLite 數據庫優化
   sqlite3 src/database/app.db "VACUUM;"
   ```

### 備份策略

1. **數據庫備份**
   ```bash
   # 每日備份
   cp src/database/app.db backups/app_$(date +%Y%m%d).db
   ```

2. **模型檔案備份**
   ```bash
   # 備份模型檔案
   cp models/best.pt backups/best_$(date +%Y%m%d).pt
   ```

## 安全考量

1. **API 安全**
   - 實施速率限制
   - 添加身份驗證

2. **檔案上傳安全**
   - 驗證檔案類型
   - 限制檔案大小
   - 掃描惡意軟體

3. **數據保護**
   - 加密敏感數據
   - 實施存取控制

---

如有部署問題，請參考 README.md 或創建 GitHub Issue 尋求協助。

