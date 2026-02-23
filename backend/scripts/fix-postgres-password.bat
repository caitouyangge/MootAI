@echo off
REM 修复 PostgreSQL 密码认证问题
REM 使用方法: fix-postgres-password.bat

cd /d "%~dp0"
echo 正在启动 PowerShell 脚本...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix-postgres-password.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 脚本执行出错，错误代码: %ERRORLEVEL%
    echo 请检查 PowerShell 脚本是否有语法错误
)

echo.
pause
