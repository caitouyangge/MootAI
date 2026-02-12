@echo off
REM MootAI 一键启动脚本 (Windows 批处理)
REM 功能：自动启动后端和前端服务

chcp 65001 >nul
echo ==========================================
echo 🎯 MootAI 一键启动脚本
echo ==========================================
echo.

REM 检查参数
if "%1"=="--skip-backend" goto :start_frontend
if "%1"=="--skip-frontend" goto :start_backend
if "%1"=="--help" goto :show_help

:start_backend
echo ==========================================
echo 🚀 启动后端服务...
echo ==========================================

REM 检查 Java
where java >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Java，请先安装 Java 17
    pause
    exit /b 1
)

REM 检查 Maven
where mvn >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Maven，请先安装 Maven
    pause
    exit /b 1
)

REM 检查后端目录
if not exist "backend" (
    echo ❌ 未找到 backend 目录
    pause
    exit /b 1
)

REM 启动后端（在新窗口中）
echo 正在启动后端服务（端口：8080）...
start "MootAI 后端服务" cmd /k "cd /d %~dp0backend && echo ======================================== && echo 🚀 MootAI 后端服务 && echo ======================================== && mvn spring-boot:run"

REM 等待后端启动
echo 等待后端服务启动...
timeout /t 10 /nobreak >nul

:start_frontend
if "%1"=="--skip-backend" goto :skip_backend_check

:skip_backend_check
echo ==========================================
echo 🚀 启动前端服务...
echo ==========================================

REM 检查 Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

REM 检查 npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到 npm，请先安装 npm
    pause
    exit /b 1
)

REM 检查前端目录
if not exist "frontend" (
    echo ❌ 未找到 frontend 目录
    pause
    exit /b 1
)

REM 检查 node_modules
if not exist "frontend\node_modules" (
    echo ⚠️  未找到 node_modules，正在安装依赖...
    cd frontend
    call npm install
    cd ..
)

REM 启动前端（在新窗口中）
echo 正在启动前端服务（端口：3000）...
start "MootAI 前端服务" cmd /k "cd /d %~dp0frontend && echo ======================================== && echo 🚀 MootAI 前端服务 && echo ======================================== && npm run dev"

echo.
echo ==========================================
echo ✅ 启动完成！
echo ==========================================
echo.
echo 📱 前端地址: http://localhost:3000
echo 🔧 后端地址: http://localhost:8080
echo.
echo 💡 提示：
echo    - 后端和前端服务已在独立窗口中运行
echo    - 关闭窗口即可停止对应服务
echo.
pause
exit /b 0

:show_help
echo MootAI 一键启动脚本
echo.
echo 用法:
echo     start.bat                  # 启动后端和前端
echo     start.bat --skip-backend    # 只启动前端（后端已运行）
echo     start.bat --skip-frontend   # 只启动后端
echo     start.bat --help            # 显示帮助信息
echo.
pause
exit /b 0



