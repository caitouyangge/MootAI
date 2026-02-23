# MootAI 停止脚本 (PowerShell)
# 功能：停止所有运行中的服务

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🛑 停止 MootAI 服务" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 停止占用端口的进程
function Stop-Port {
    param([int]$Port, [string]$ServiceName)
    
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($processes) {
        foreach ($pid in $processes) {
            try {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "✅ 已停止 $ServiceName (PID: $pid)" -ForegroundColor Green
            } catch {
                Write-Host "⚠️  无法停止 $ServiceName (PID: $pid)" -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host "ℹ️  $ServiceName 未运行" -ForegroundColor Gray
    }
}

# 停止后端（端口 8080）
Write-Host "正在停止后端服务（端口：8080）..."
Stop-Port -Port 8080 -ServiceName "后端服务"

# 停止前端（端口 3000）
Write-Host "正在停止前端服务（端口：3000）..."
Stop-Port -Port 3000 -ServiceName "前端服务"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ 所有服务已停止" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""





