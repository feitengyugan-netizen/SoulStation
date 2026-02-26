@echo off
echo ====================================
echo SoulStation Backend Server
echo ====================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

REM 检查是否安装了依赖
if not exist "venv\" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

echo [信息] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [信息] 安装依赖...
pip install -r requirements.txt -q

echo.
echo [信息] 启动后端服务...
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
