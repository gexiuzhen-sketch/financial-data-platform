@echo off
chcp 65001 > nul

echo ========================================
echo 金融数据聚合平台 - 快速启动
echo ========================================
echo.

cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python未安装
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Node.js未安装
    echo 请先安装Node.js 18+
    pause
    exit /b 1
)

echo [1/6] 安装后端依赖...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
cd ..

echo [2/6] 初始化数据库...
cd backend
call venv\Scripts\activate.bat
if not exist data\database.db (
    python run.py init_db
    python run.py seed_data
)
cd ..

echo [3/6] 安装前端依赖...
cd frontend
if not exist node_modules (
    call npm install
)
cd ..

echo [4/6] 构建前端...
cd frontend
call npm run build
cd ..

echo [5/6] 启动后端服务...
cd backend
start "金融数据平台-后端" cmd /k "venv\Scripts\activate && python run.py"
cd ..

echo [6/6] 等待服务启动...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo [完成] 服务已启动！
echo ========================================
echo.
echo 访问地址:
echo   本地访问: http://localhost:5173
echo   API地址:  http://localhost:5000/api/v1
echo.
echo 按任意键关闭此窗口（服务将继续运行）...
pause >nul
