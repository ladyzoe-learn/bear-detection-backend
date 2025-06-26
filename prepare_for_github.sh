#!/bin/bash

# 台灣黑熊檢測系統 - 專案打包腳本
# 此腳本幫助準備專案檔案以上傳到 GitHub

echo "🐻 台灣黑熊檢測系統 - 專案打包準備"
echo "=================================="

# 檢查當前目錄
if [ ! -f "src/main.py" ]; then
    echo "❌ 錯誤：請在專案根目錄執行此腳本"
    exit 1
fi

echo "✅ 檢查專案結構..."

# 檢查必要檔案
required_files=(
    "src/main.py"
    "src/models/detection.py"
    "src/routes/detection.py"
    "src/services/bear_detection.py"
    "requirements.txt"
    "README.md"
    "DEPLOYMENT.md"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ 缺少必要檔案："
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

echo "✅ 所有必要檔案存在"

# 檢查虛擬環境
if [ -d "venv" ]; then
    echo "✅ 虛擬環境目錄存在"
else
    echo "⚠️  警告：未找到虛擬環境目錄"
fi

# 檢查模型檔案
if [ -f "models/best.pt" ]; then
    echo "✅ 找到自定義模型檔案 (models/best.pt)"
    model_size=$(du -h "models/best.pt" | cut -f1)
    echo "   模型檔案大小: $model_size"
    
    # 檢查檔案大小 (GitHub 有 100MB 限制)
    size_bytes=$(stat -f%z "models/best.pt" 2>/dev/null || stat -c%s "models/best.pt" 2>/dev/null)
    if [ "$size_bytes" -gt 104857600 ]; then  # 100MB
        echo "⚠️  警告：模型檔案超過 100MB，建議使用 Git LFS"
        echo "   或考慮模型壓縮/量化"
    fi
else
    echo "ℹ️  未找到自定義模型檔案，將使用預設 YOLOv8 模型"
fi

# 檢查依賴檔案
echo "✅ 檢查 requirements.txt..."
if pip freeze > temp_requirements.txt 2>/dev/null; then
    echo "   當前環境依賴已更新到 requirements.txt"
    mv temp_requirements.txt requirements.txt
else
    echo "⚠️  無法更新 requirements.txt，請手動檢查"
fi

# 清理臨時檔案
echo "🧹 清理臨時檔案..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.log" -delete 2>/dev/null || true

# 檢查 .gitignore
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore 檔案存在"
else
    echo "⚠️  警告：未找到 .gitignore 檔案"
fi

# 創建專案摘要
echo ""
echo "📋 專案摘要"
echo "============"
echo "專案名稱: 台灣黑熊檢測系統後端API"
echo "主要檔案:"
find src -name "*.py" | wc -l | xargs echo "  Python 檔案數量:"
echo "  API 端點: $(grep -r "@.*_bp.route" src/ | wc -l)"
echo "  數據模型: $(find src/models -name "*.py" | grep -v __init__ | wc -l)"

# Git 準備建議
echo ""
echo "🚀 GitHub 上傳準備"
echo "=================="
echo "建議的 Git 命令："
echo ""
echo "# 1. 初始化 Git 倉庫 (如果尚未初始化)"
echo "git init"
echo ""
echo "# 2. 添加所有檔案"
echo "git add ."
echo ""
echo "# 3. 創建初始提交"
echo "git commit -m \"Initial commit: 台灣黑熊檢測系統後端API\""
echo ""
echo "# 4. 添加遠程倉庫 (替換為您的 GitHub 倉庫 URL)"
echo "git remote add origin https://github.com/YOUR_USERNAME/bear-detection-backend.git"
echo ""
echo "# 5. 推送到 GitHub"
echo "git push -u origin main"

# 部署建議
echo ""
echo "☁️  部署建議"
echo "============"
echo "推薦的部署平台："
echo "1. Render.com (免費，易用)"
echo "2. Railway (簡單部署)"
echo "3. Heroku (功能豐富)"
echo "4. DigitalOcean App Platform"
echo ""
echo "詳細部署說明請參考 DEPLOYMENT.md"

# 檢查清單
echo ""
echo "✅ 上傳前檢查清單"
echo "=================="
echo "□ 已測試本地開發環境"
echo "□ 已更新 requirements.txt"
echo "□ 已放置 best.pt 模型檔案 (或準備使用預設模型)"
echo "□ 已檢查 .gitignore 設置"
echo "□ 已閱讀 README.md 和 DEPLOYMENT.md"
echo "□ 已創建 GitHub 倉庫"
echo "□ 已準備部署到雲端平台"

echo ""
echo "🎉 專案打包準備完成！"
echo "現在您可以將專案上傳到 GitHub 並進行部署。"
echo ""
echo "如有問題，請參考專案文檔或創建 GitHub Issue。"

