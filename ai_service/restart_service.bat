@echo off
chcp 65001 >nul
echo ========================================
echo 重启AI服务（Python Flask）
echo ========================================
echo.

REM 查找并终止运行在5000端口的Python进程
echo 正在查找运行在5000端口的Python进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo 找到进程ID: %%a
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo 无法终止进程 %%a，可能需要管理员权限
    ) else (
        echo 已终止进程 %%a
    )
)

echo.
echo 等待2秒...
timeout /t 2 /nobreak >nul

echo.
echo 启动AI服务...
echo.

REM 设置环境变量
set ADAPTER_DIR=court_debate_model
set LOAD_IN_4BIT=true
set GPU_ID=0
set PORT=5000

REM 启动服务
cd /d %~dp0
python app.py

pause


