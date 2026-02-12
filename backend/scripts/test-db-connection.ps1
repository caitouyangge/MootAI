# 测试 PostgreSQL 数据库连接
# 用于诊断数据库连接问题

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 PostgreSQL 数据库连接测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 确定 backend 目录路径
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Split-Path -Parent $scriptDir

# 从配置文件读取数据库信息
$configPath = Join-Path $backendDir "src\main\resources\application-local.yml"
$defaultConfigPath = Join-Path $backendDir "src\main\resources\application.yml"

$dbUrl = $null
$dbUsername = $null
$dbPassword = $null

# 尝试从 application-local.yml 读取配置
if (Test-Path $configPath) {
    Write-Host "📄 读取配置文件: $configPath" -ForegroundColor Yellow
    $content = Get-Content $configPath -Raw -Encoding UTF8
    
    # 改进正则表达式以匹配 YAML 缩进格式
    if ($content -match '(?m)^\s+url:\s*(.+)$') {
        $dbUrl = $matches[1].Trim()
    }
    if ($content -match '(?m)^\s+username:\s*(.+)$') {
        $dbUsername = $matches[1].Trim()
    }
    if ($content -match '(?m)^\s+password:\s*(.+)$') {
        $dbPassword = $matches[1].Trim()
    }
    
    # 调试信息
    if (-not $dbUrl) {
        Write-Host "⚠️  未能从配置文件中解析 URL" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  配置文件不存在: $configPath" -ForegroundColor Yellow
}

# 如果本地配置不存在，从默认配置读取
if (-not $dbUrl -and (Test-Path $defaultConfigPath)) {
    Write-Host "📄 读取默认配置文件: $defaultConfigPath" -ForegroundColor Yellow
    $content = Get-Content $defaultConfigPath -Raw -Encoding UTF8
    
    # 匹配环境变量格式：${DB_URL:default-value}
    if ($content -match '(?m)^\s+url:\s*\$\{DB_URL:(.+)\}') {
        $dbUrl = $matches[1].Trim()
    }
    if ($content -match '(?m)^\s+username:\s*\$\{DB_USERNAME:(.+)\}') {
        $dbUsername = $matches[1].Trim()
    }
    if ($content -match '(?m)^\s+password:\s*\$\{DB_PASSWORD:(.+)\}') {
        $dbPassword = $matches[1].Trim()
    }
}

# 从环境变量读取（优先级最高）
if ($env:DB_URL) {
    $dbUrl = $env:DB_URL
    Write-Host "📄 使用环境变量 DB_URL" -ForegroundColor Green
}
if ($env:DB_USERNAME) {
    $dbUsername = $env:DB_USERNAME
    Write-Host "📄 使用环境变量 DB_USERNAME" -ForegroundColor Green
}
if ($env:DB_PASSWORD) {
    $dbPassword = $env:DB_PASSWORD
    Write-Host "📄 使用环境变量 DB_PASSWORD" -ForegroundColor Green
}

# 解析数据库连接信息
if ([string]::IsNullOrEmpty($dbUrl)) {
    Write-Host "❌ 数据库 URL 为空，无法解析" -ForegroundColor Red
    Write-Host "   请检查配置文件: $configPath" -ForegroundColor Yellow
    exit 1
}

if ($dbUrl -match 'jdbc:postgresql://([^:]+):(\d+)/(.+)') {
    $dbHost = $matches[1]
    $dbPort = $matches[2]
    $dbName = $matches[3]
} else {
    Write-Host "❌ 无法解析数据库 URL: $dbUrl" -ForegroundColor Red
    Write-Host "   期望格式: jdbc:postgresql://host:port/database" -ForegroundColor Yellow
    Write-Host "   实际格式: $dbUrl" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "数据库配置信息:" -ForegroundColor Cyan
Write-Host "  主机: $dbHost" -ForegroundColor White
Write-Host "  端口: $dbPort" -ForegroundColor White
Write-Host "  数据库: $dbName" -ForegroundColor White
Write-Host "  用户名: $dbUsername" -ForegroundColor White
Write-Host "  密码: $('*' * $dbPassword.Length)" -ForegroundColor White
Write-Host ""

# 检查 PostgreSQL 是否安装
Write-Host "检查 PostgreSQL 是否可用..." -ForegroundColor Yellow
$psqlPath = $null

# 方法1: 检查 PATH 环境变量
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlPath) {
    $psqlPath = $psqlPath.Source
    Write-Host "✅ 从 PATH 找到 psql: $psqlPath" -ForegroundColor Green
}

# 方法2: 检查常见安装路径
if (-not $psqlPath) {
    $searchPaths = @(
        "C:\Program Files\PostgreSQL",
        "C:\Program Files (x86)\PostgreSQL",
        "$env:ProgramFiles\PostgreSQL",
        "${env:ProgramFiles(x86)}\PostgreSQL",
        "$env:LOCALAPPDATA\PostgreSQL"
    )
    
    foreach ($basePath in $searchPaths) {
        if (Test-Path $basePath) {
            $versions = Get-ChildItem -Path $basePath -Directory -ErrorAction SilentlyContinue | 
                        Sort-Object Name -Descending
            foreach ($version in $versions) {
                $psqlCandidate = Join-Path $version.FullName "bin\psql.exe"
                if (Test-Path $psqlCandidate) {
                    $psqlPath = $psqlCandidate
                    Write-Host "✅ 找到 psql: $psqlPath" -ForegroundColor Green
                    break
                }
            }
            if ($psqlPath) { break }
        }
    }
}

# 方法3: 检查注册表（Windows）
if (-not $psqlPath) {
    try {
        $regPath = "HKLM:\SOFTWARE\PostgreSQL\Installations"
        if (Test-Path $regPath) {
            $installations = Get-ChildItem -Path $regPath -ErrorAction SilentlyContinue
            foreach ($inst in $installations) {
                $binPath = (Get-ItemProperty -Path $inst.PSPath -Name "Base Directory" -ErrorAction SilentlyContinue).'Base Directory'
                if ($binPath) {
                    $psqlCandidate = Join-Path $binPath "bin\psql.exe"
                    if (Test-Path $psqlCandidate) {
                        $psqlPath = $psqlCandidate
                        Write-Host "✅ 从注册表找到 psql: $psqlPath" -ForegroundColor Green
                        break
                    }
                }
            }
        }
    } catch {
        # 忽略注册表访问错误
    }
}

if (-not $psqlPath) {
    Write-Host "⚠️  未找到 psql 命令" -ForegroundColor Yellow
    Write-Host "   将尝试使用 Maven/Java 方式测试连接" -ForegroundColor Yellow
    $usePsql = $false
} else {
    $usePsql = $true
}

Write-Host ""

# 测试连接
Write-Host "测试数据库连接..." -ForegroundColor Yellow

if ($usePsql) {
    # 使用 psql 测试连接
    $env:PGPASSWORD = $dbPassword
    $result = & $psqlPath -h $dbHost -p $dbPort -U $dbUsername -d $dbName -c "SELECT version();" 2>&1
    $env:PGPASSWORD = $null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 数据库连接成功！" -ForegroundColor Green
        Write-Host ""
        Write-Host "PostgreSQL 版本信息:" -ForegroundColor Cyan
        $result | Where-Object { $_ -match "PostgreSQL" } | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
    } else {
        Write-Host "❌ 数据库连接失败！" -ForegroundColor Red
        Write-Host ""
        Write-Host "错误信息:" -ForegroundColor Red
        $result | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        Write-Host ""
        Write-Host "可能的解决方案:" -ForegroundColor Yellow
        Write-Host "  1. 检查 PostgreSQL 服务是否运行" -ForegroundColor White
        Write-Host "  2. 检查用户名和密码是否正确" -ForegroundColor White
        Write-Host "  3. 检查数据库是否存在（如果不存在，运行 create-database.ps1）" -ForegroundColor White
        Write-Host "  4. 检查 pg_hba.conf 配置（允许本地连接）" -ForegroundColor White
        exit 1
    }
} else {
    # 无法使用 psql，提供替代方案
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "⚠️  未找到 psql 命令" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "解决方案（选择其一）:" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "方案 1: 直接启动应用测试连接（推荐）" -ForegroundColor Green
    Write-Host "  应用启动时会自动测试数据库连接" -ForegroundColor White
    Write-Host "  运行以下命令:" -ForegroundColor White
    Write-Host "    cd $backendDir" -ForegroundColor Gray
    Write-Host "    mvn spring-boot:run" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "方案 2: 找到 psql 的完整路径" -ForegroundColor Green
    Write-Host "  PostgreSQL 通常安装在以下位置之一:" -ForegroundColor White
    Write-Host "    - C:\Program Files\PostgreSQL\[版本号]\bin\psql.exe" -ForegroundColor Gray
    Write-Host "    - C:\Program Files (x86)\PostgreSQL\[版本号]\bin\psql.exe" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  找到后使用完整路径运行:" -ForegroundColor White
    Write-Host "    `"C:\Program Files\PostgreSQL\15\bin\psql.exe`" -h $dbHost -p $dbPort -U $dbUsername -d $dbName" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "方案 3: 使用 pgAdmin（图形界面）" -ForegroundColor Green
    Write-Host "  如果安装了 pgAdmin，可以通过图形界面测试连接" -ForegroundColor White
    Write-Host ""
    
    Write-Host "方案 4: 检查 PostgreSQL 服务状态" -ForegroundColor Green
    Write-Host "  运行以下命令检查服务是否运行:" -ForegroundColor White
    Write-Host "    Get-Service -Name postgresql*" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "当前配置信息（用于手动测试）:" -ForegroundColor Cyan
    Write-Host "  主机: $dbHost" -ForegroundColor White
    Write-Host "  端口: $dbPort" -ForegroundColor White
    Write-Host "  数据库: $dbName" -ForegroundColor White
    Write-Host "  用户名: $dbUsername" -ForegroundColor White
    Write-Host "  密码: $('*' * $dbPassword.Length)" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

