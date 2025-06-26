# 台灣黑熊檢測系統 - 後端API

這是一個基於YOLO模型的台灣黑熊檢測系統後端API服務，提供圖片上傳、檢測分析和結果管理功能。

## 功能特色

- 🐻 **YOLO模型整合**: 支援自定義訓練的best.pt模型或預設YOLOv8模型
- 📸 **圖片檢測**: 上傳圖片進行台灣黑熊檢測分析
- 📊 **統計資料**: 提供檢測統計和歷史記錄
- 🌐 **RESTful API**: 完整的REST API接口
- 💾 **數據持久化**: SQLite數據庫存儲檢測記錄
- 🔧 **CORS支援**: 支援跨域請求，可與前端應用整合

## 技術架構

- **後端框架**: Flask
- **AI模型**: YOLO (Ultralytics)
- **數據庫**: SQLite
- **圖像處理**: OpenCV, PIL
- **部署**: 支援本地開發和雲端部署

## API端點

### 健康檢查
```
GET /api/health
```

### 統計資料
```
GET /api/statistics
```

### 圖片檢測
```
POST /api/detect
Content-Type: multipart/form-data

參數:
- image: 圖片檔案
- camera_id: 相機ID (可選)
- location: 位置資訊 (可選)
```

### 最近檢測記錄
```
GET /api/recent-detections?limit=10
```

### 模型資訊
```
GET /api/model-info
```

### 設定信心度閾值
```
POST /api/set-confidence
Content-Type: application/json

{
  "threshold": 0.5
}
```

### 檔案存取
```
GET /api/uploads/{filename}
```

## 快速開始

### 1. 環境需求

- Python 3.11+
- pip
- 虛擬環境 (建議)

### 2. 安裝依賴

```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
```

### 3. 模型設置

將您訓練好的YOLO模型檔案 `best.pt` 放置在以下任一位置：
- `/models/best.pt`
- `/best.pt`
- 專案根目錄

如果沒有自定義模型，系統會自動下載並使用預設的YOLOv8模型。

### 4. 啟動服務

```bash
python src/main.py
```

服務將在 `http://localhost:5000` 啟動。

## 專案結構

```
bear-detection-backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # 用戶模型
│   │   └── detection.py     # 檢測記錄模型
│   ├── routes/
│   │   ├── user.py          # 用戶路由
│   │   └── detection.py     # 檢測API路由
│   ├── services/
│   │   ├── __init__.py
│   │   └── bear_detection.py # YOLO檢測服務
│   ├── static/
│   │   └── uploads/         # 上傳檔案目錄
│   ├── database/
│   │   └── app.db          # SQLite數據庫
│   └── main.py             # 主程式入口
├── models/
│   └── best.pt             # YOLO模型檔案 (需要用戶提供)
├── venv/                   # 虛擬環境
├── requirements.txt        # Python依賴
└── README.md              # 專案說明
```

## 部署指南

### 本地開發

1. 按照「快速開始」步驟設置環境
2. 啟動開發服務器：`python src/main.py`
3. API將在 `http://localhost:5000` 可用

### 雲端部署

#### Render.com 部署

1. 將專案推送到GitHub
2. 在Render.com創建新的Web Service
3. 連接GitHub倉庫
4. 設置以下配置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`
   - **Environment**: Python 3.11

#### Heroku 部署

1. 安裝Heroku CLI
2. 創建Heroku應用：`heroku create your-app-name`
3. 推送代碼：`git push heroku main`

#### Docker 部署

創建 `Dockerfile`：
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "src/main.py"]
```

## 環境變數

可以通過環境變數配置以下選項：

- `FLASK_ENV`: 設置為 `production` 用於生產環境
- `DATABASE_URL`: 自定義數據庫URL (可選)
- `MODEL_PATH`: 自定義模型檔案路徑 (可選)

## 開發說明

### 添加新的API端點

1. 在 `src/routes/detection.py` 中添加新的路由函數
2. 使用 `@detection_bp.route()` 裝飾器定義端點
3. 重啟服務器測試新功能

### 自定義檢測邏輯

修改 `src/services/bear_detection.py` 中的 `BearDetectionService` 類來自定義檢測邏輯。

### 數據庫遷移

如需修改數據庫結構：
1. 更新 `src/models/` 中的模型定義
2. 刪除 `src/database/app.db`
3. 重啟服務器自動重建數據庫

## 故障排除

### 常見問題

1. **模型載入失敗**
   - 確保 `best.pt` 檔案存在且可讀
   - 檢查檔案路徑是否正確

2. **數據庫錯誤**
   - 確保 `src/database/` 目錄存在
   - 檢查檔案權限

3. **CORS錯誤**
   - 確保已安裝 `flask-cors`
   - 檢查CORS配置

### 日誌查看

開發模式下，詳細日誌會顯示在控制台。生產環境建議配置適當的日誌記錄。

## 貢獻指南

1. Fork 專案
2. 創建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 創建Pull Request

## 授權

本專案採用 MIT 授權條款。

## 聯絡資訊

如有問題或建議，請通過以下方式聯絡：
- 創建GitHub Issue
- 發送郵件至專案維護者

---

**注意**: 請確保您有合法權限使用和分發YOLO模型檔案。

