@echo off
REM 测试 PostgreSQL 数据库连接
REM 使用方法: test-db-connection.bat

cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "test-db-connection.ps1"

pause





