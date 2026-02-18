@echo off
REM 创建 PostgreSQL 数据库脚本
REM 使用方法: create-database.bat

cd /d "%~dp0"

echo ========================================
echo 正在创建 PostgreSQL 数据库...
echo ========================================
echo.

set DB_HOST=127.0.0.1
set DB_PORT=5432
set DB_NAME=MootAI
set DB_USER=postgres
set DB_PASSWORD=123456

echo 数据库配置:
echo   主机: %DB_HOST%
echo   端口: %DB_PORT%
echo   数据库名: %DB_NAME%
echo   用户名: %DB_USER%
echo.

REM 检查 psql 是否可用，如果不在PATH中，尝试从注册表查找
set PSQL_PATH=
where psql >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PSQL_PATH=psql
) else (
    REM 尝试从注册表查找
    for /f "tokens=*" %%i in ('powershell -Command "try { $regPath = 'HKLM:\SOFTWARE\PostgreSQL\Installations'; if (Test-Path $regPath) { $inst = Get-ChildItem -Path $regPath | Select-Object -First 1; $baseDir = (Get-ItemProperty -Path $inst.PSPath -Name 'Base Directory' -ErrorAction SilentlyContinue).'Base Directory'; if ($baseDir) { $psqlPath = Join-Path $baseDir 'bin\psql.exe'; if (Test-Path $psqlPath) { Write-Output $psqlPath } } } } catch {}"') do set PSQL_PATH=%%i
    
    if not defined PSQL_PATH (
        echo [错误] 未找到 psql 命令
        echo 请确保 PostgreSQL 已安装并添加到 PATH 环境变量
        echo.
        echo 或者使用完整路径运行，例如:
        echo   "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -h 127.0.0.1 -p 5432
        echo.
        pause
        exit /b 1
    )
)

REM 设置密码环境变量
set PGPASSWORD=%DB_PASSWORD%

REM 检查数据库是否已存在
echo 检查数据库是否已存在...
"%PSQL_PATH%" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='%DB_NAME%'" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo 数据库 '%DB_NAME%' 已存在
    echo.
) else (
    echo 正在创建数据库 '%DB_NAME%'...
    "%PSQL_PATH%" -U %DB_USER% -h %DB_HOST% -p %DB_PORT% -d postgres -c "CREATE DATABASE \"%DB_NAME%\" WITH ENCODING 'UTF8';" 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [成功] 数据库 '%DB_NAME%' 创建成功！
        echo.
    ) else (
        echo.
        echo [错误] 创建数据库失败
        echo 请检查:
        echo   1. PostgreSQL 服务是否正在运行
        echo   2. 用户名和密码是否正确
        echo   3. 是否有创建数据库的权限
        echo.
        set PGPASSWORD=
        pause
        exit /b 1
    )
)

REM 清除密码环境变量
set PGPASSWORD=

echo ========================================
echo 数据库创建完成！
echo ========================================
echo.
pause

