# MootAI 一键启动脚本 (PowerShell)
# 功能：自动启动后端和前端服务

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$Help
)

# 显示帮助信息
if ($Help) {
    Write-Host @"
MootAI 一键启动脚本

用法:
    .\start.ps1                  # 启动后端和前端
    .\start.ps1 -SkipBackend     # 只启动前端（后端已运行）
    .\start.ps1 -SkipFrontend    # 只启动后端
    .\start.ps1 -Help            # 显示帮助信息

"@ -ForegroundColor Cyan
    exit 0
}

# 颜色输出函数
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message) Write-ColorOutput $Message "Green" }
function Write-Error { param([string]$Message) Write-ColorOutput $Message "Red" }
function Write-Warning { param([string]$Message) Write-ColorOutput $Message "Yellow" }
function Write-Info { param([string]$Message) Write-ColorOutput $Message "Cyan" }

# 检查命令是否存在
function Test-Command {
    param([string]$Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# 检查后端是否已运行
function Test-BackendRunning {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/actuator/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# 等待后端启动
function Wait-BackendStart {
    Write-Info "等待后端服务启动..."
    $maxAttempts = 60
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 2
        $attempt++
        
        if (Test-BackendRunning) {
            Write-Success "✅ 后端服务已启动！"
            return $true
        }
        
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    Write-Warning "⚠️  后端服务启动超时，但将继续启动前端..."
    return $false
}

# 启动后端
function Start-Backend {
    Write-Info "=========================================="
    Write-Info "🚀 启动后端服务..."
    Write-Info "=========================================="
    
    # 检查 Java
    if (-not (Test-Command "java")) {
        Write-Error "❌ 未找到 Java，请先安装 Java 17"
        exit 1
    }
    
    # 检查 Maven
    if (-not (Test-Command "mvn")) {
        Write-Error "❌ 未找到 Maven，请先安装 Maven"
        exit 1
    }
    
    # 检查后端目录
    if (-not (Test-Path "backend")) {
        Write-Error "❌ 未找到 backend 目录"
        exit 1
    }
    
    # 检查配置文件
    if (-not (Test-Path "backend/src/main/resources/application-local.yml")) {
        Write-Warning "⚠️  未找到 application-local.yml，将使用默认配置"
        Write-Info "提示：可以复制 application-local.yml.example 创建本地配置"
    }
    
    # 启动后端（在新窗口中）
    Write-Info "正在启动后端服务（端口：8080）..."
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$PWD\backend'; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '🚀 MootAI 后端服务' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; mvn spring-boot:run"
    ) -WindowStyle Normal
    
    # 等待后端启动
    Wait-BackendStart
}

# 启动前端
function Start-Frontend {
    Write-Info "=========================================="
    Write-Info "🚀 启动前端服务..."
    Write-Info "=========================================="
    
    # 检查 Node.js
    if (-not (Test-Command "node")) {
        Write-Error "❌ 未找到 Node.js，请先安装 Node.js"
        exit 1
    }
    
    # 检查 npm
    if (-not (Test-Command "npm")) {
        Write-Error "❌ 未找到 npm，请先安装 npm"
        exit 1
    }
    
    # 检查前端目录
    if (-not (Test-Path "frontend")) {
        Write-Error "❌ 未找到 frontend 目录"
        exit 1
    }
    
    # 检查 node_modules
    if (-not (Test-Path "frontend/node_modules")) {
        Write-Warning "⚠️  未找到 node_modules，正在安装依赖..."
        Set-Location frontend
        npm install
        Set-Location ..
    }
    
    # 启动前端（在新窗口中）
    Write-Info "正在启动前端服务（端口：3000）..."
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$PWD\frontend'; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '🚀 MootAI 前端服务' -ForegroundColor Cyan; Write-Host '========================================' -ForegroundColor Cyan; npm run dev"
    ) -WindowStyle Normal
}

# 主流程
Write-Info "=========================================="
Write-Info "🎯 MootAI 一键启动脚本"
Write-Info "=========================================="
Write-Host ""

# 启动后端
if (-not $SkipBackend) {
    Start-Backend
    Write-Host ""
}

# 启动前端
if (-not $SkipFrontend) {
    Start-Frontend
    Write-Host ""
}

# 显示启动信息
Write-Success "=========================================="
Write-Success "✅ 启动完成！"
Write-Success "=========================================="
Write-Info ""
Write-Info "📱 前端地址: http://localhost:3000"
Write-Info "🔧 后端地址: http://localhost:8080"
Write-Info ""
Write-Info "💡 提示："
Write-Info "   - 后端和前端服务已在独立窗口中运行"
Write-Info "   - 关闭窗口即可停止对应服务"
Write-Info "   - 如需停止所有服务，请关闭所有相关窗口"
Write-Info ""




