@echo off
REM 查找 PostgreSQL psql 命令的位置
REM 使用方法: find-psql.bat

cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "find-psql.ps1"

pause



