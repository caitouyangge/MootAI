$ps1Content = @'
# PowerShell 脚本：修复 PostgreSQL 密码认证问题
# 使用方法: .\fix-postgres-password.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔧 PostgreSQL 密码修复工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 确定 backend 目录路径
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Split-Path -Parent $scriptDir
$configPath = Join-Path $backendDir "src\main\resources\application-local.yml"

# 从配置文件读取当前配置
$dbHost = "127.0.0.1"
$dbPort = "5432"
$dbName = "MootAI"
$dbUsername = "postgres"
$currentPassword = $null

if (Test-Path $configPath) {
    $content = Get-Content $configPath -Raw -Encoding UTF8
    if ($content -match '(?m)^\s+url:\s*jdbc:postgresql://([^:]+):(\d+)/(.+)$') {
        $dbHost = $matches[1].Trim()
        $dbPort = $matches[2].Trim()
        $dbName = $matches[3].Trim()
    }
    if ($content -match '(?m)^\s+username:\s*(.+)$') {
        $dbUsername = $matches[1].Trim()
    }
    if ($content -match '(?m)^\s+password:\s*(.+)$') {
        $currentPassword = $matches[1].Trim()
    }
}

Write-Host "当前配置:" -ForegroundColor Yellow
Write-Host "  主机: $dbHost" -ForegroundColor White
Write-Host "  端口: $dbPort" -ForegroundColor White
Write-Host "  数据库: $dbName" -ForegroundColor White
Write-Host "  用户名: $dbUsername" -ForegroundColor White
Write-Host "  配置中的密码: $(if ($currentPassword) { '*' * $currentPassword.Length } else { '(未设置)' })" -ForegroundColor White
Write-Host ""

# 查找 psql
$psqlPath = $null

# 方法1: 检查 PATH
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlPath) {
    $psqlPath = $psqlPath.Source
}

# 方法2: 检查注册表
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
                        break
                    }
                }
            }
        }
    } catch {
        # 忽略错误
    }
}

if (-not $psqlPath) {
    Write-Host "❌ 未找到 psql 命令" -ForegroundColor Red
    Write-Host "   请确保 PostgreSQL 已正确安装" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 找到 psql: $psqlPath" -ForegroundColor Green
Write-Host ""

# 交互式密码测试
Write-Host "请尝试输入正确的 PostgreSQL 密码:" -ForegroundColor Yellow
Write-Host "（如果不知道密码，可以尝试重置密码，见下方选项）" -ForegroundColor Gray
Write-Host ""

$maxAttempts = 3
$success = $false
$correctPassword = $null

for ($i = 1; $i -le $maxAttempts; $i++) {
    Write-Host "尝试 $i/$maxAttempts" -ForegroundColor Cyan
    $password = Read-Host "请输入密码" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
    $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    
    # 测试连接
    $env:PGPASSWORD = $plainPassword
    $result = & $psqlPath -h $dbHost -p $dbPort -U $dbUsername -d postgres -c "SELECT version();" 2>&1
    $env:PGPASSWORD = $null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 密码正确！连接成功！" -ForegroundColor Green
        $correctPassword = $plainPassword
        $success = $true
        break
    } else {
        Write-Host "❌ 密码错误" -ForegroundColor Red
        if ($i -lt $maxAttempts) {
            Write-Host ""
        }
    }
}

if (-not $success) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 所有尝试都失败了" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "您可以选择以下方案之一:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "方案 1: 重置 PostgreSQL 密码" -ForegroundColor Green
    Write-Host "  1. 找到 PostgreSQL 数据目录（通常在安装目录的 data 文件夹）" -ForegroundColor White
    Write-Host "  2. 编辑 pg_hba.conf 文件" -ForegroundColor White
    Write-Host "  3. 找到包含 '127.0.0.1' 的行，将 'md5' 或 'scram-sha-256' 改为 'trust'" -ForegroundColor White
    Write-Host "  4. 重启 PostgreSQL 服务" -ForegroundColor White
    Write-Host "  5. 运行: psql -U postgres -h 127.0.0.1 -p 5432" -ForegroundColor White
    Write-Host "  6. 在 psql 中执行: ALTER USER postgres WITH PASSWORD '新密码';" -ForegroundColor White
    Write-Host "  7. 恢复 pg_hba.conf 文件（改回 'md5' 或 'scram-sha-256'）" -ForegroundColor White
    Write-Host "  8. 重启 PostgreSQL 服务" -ForegroundColor White
    Write-Host ""
    Write-Host "方案 2: 使用 pgAdmin 图形界面重置密码" -ForegroundColor Green
    Write-Host "  1. 打开 pgAdmin" -ForegroundColor White
    Write-Host "  2. 连接到服务器" -ForegroundColor White
    Write-Host "  3. 右键点击 postgres 用户 -> Properties -> Definition" -ForegroundColor White
    Write-Host "  4. 修改密码并保存" -ForegroundColor White
    Write-Host ""
    Write-Host "方案 3: 使用 Windows 服务账户（如果使用 Windows 身份验证）" -ForegroundColor Green
    Write-Host "  修改 pg_hba.conf 使用 'ident' 或 'peer' 认证方式" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "密码验证成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 询问是否更新配置文件
if ($currentPassword -ne $correctPassword) {
    Write-Host "检测到配置文件中的密码与正确密码不一致" -ForegroundColor Yellow
    $update = Read-Host "是否更新配置文件中的密码？(Y/N)"
    
    if ($update -eq 'Y' -or $update -eq 'y') {
        try {
            $content = Get-Content $configPath -Raw -Encoding UTF8
            $newContent = $content -replace "(?m)^(\s+password:\s*).+$", "`$1$correctPassword"
            
            # 使用 UTF8 编码保存（无 BOM）
            $utf8NoBom = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($configPath, $newContent, $utf8NoBom)
            
            Write-Host "✅ 配置文件已更新！" -ForegroundColor Green
            Write-Host "   文件路径: $configPath" -ForegroundColor Gray
        } catch {
            Write-Host "❌ 更新配置文件失败: $_" -ForegroundColor Red
            Write-Host "   请手动更新配置文件中的密码为: $correctPassword" -ForegroundColor Yellow
        }
    } else {
        Write-Host "跳过配置文件更新" -ForegroundColor Yellow
        Write-Host "   请手动更新配置文件中的密码为: $correctPassword" -ForegroundColor Yellow
    }
} else {
    Write-Host "配置文件中的密码已经是正确的" -ForegroundColor Green
}

Write-Host ""
Write-Host "现在可以运行 test-db-connection.bat 来验证连接" -ForegroundColor Cyan
Write-Host ""
'@

$batContent = @'
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
'@

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("fix-postgres-password.ps1", $ps1Content, $utf8NoBom)
[System.IO.File]::WriteAllText("fix-postgres-password.bat", $batContent, $utf8NoBom)

Write-Host "文件已创建！" -ForegroundColor Green
Write-Host "PS1 文件大小: $((Get-Item 'fix-postgres-password.ps1').Length) 字节" -ForegroundColor Yellow
Write-Host "BAT 文件大小: $((Get-Item 'fix-postgres-password.bat').Length) 字节" -ForegroundColor Yellow



