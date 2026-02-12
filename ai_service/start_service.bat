@echo off
chcp 65001 >nul
echo ========================================
echo 启动AI服务（Python Flask）
echo ========================================
echo.

REM 检查端口是否被占用
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% == 0 (
    echo 警告: 端口5000已被占用！
    echo 请先运行 restart_service.bat 来重启服务
    echo 或者手动终止占用5000端口的进程
    pause
    exit /b 1
)

REM 设置环境变量
set ADAPTER_DIR=court_debate_model
set LOAD_IN_4BIT=true
set GPU_ID=0
set PORT=5000

echo 环境变量已设置:
echo   ADAPTER_DIR=%ADAPTER_DIR%
echo   LOAD_IN_4BIT=%LOAD_IN_4BIT%
echo   GPU_ID=%GPU_ID%
echo   PORT=%PORT%
echo.

REM 启动服务
cd /d %~dp0
echo 正在启动服务...
python app.py

pause

