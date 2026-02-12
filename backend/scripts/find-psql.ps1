# 查找 PostgreSQL psql 命令的位置
# 使用方法: .\find-psql.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔍 查找 PostgreSQL psql 命令" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$found = $false

# 方法1: 检查 PATH
Write-Host "1. 检查 PATH 环境变量..." -ForegroundColor Yellow
$psqlInPath = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlInPath) {
    Write-Host "   ✅ 找到: $($psqlInPath.Source)" -ForegroundColor Green
    $found = $true
} else {
    Write-Host "   ❌ 未在 PATH 中找到" -ForegroundColor Red
}
Write-Host ""

# 方法2: 检查常见安装路径
Write-Host "2. 检查常见安装路径..." -ForegroundColor Yellow
$searchPaths = @(
    "C:\Program Files\PostgreSQL",
    "C:\Program Files (x86)\PostgreSQL",
    "$env:ProgramFiles\PostgreSQL",
    "${env:ProgramFiles(x86)}\PostgreSQL"
)

$foundPaths = @()
foreach ($basePath in $searchPaths) {
    if (Test-Path $basePath) {
        Write-Host "   检查: $basePath" -ForegroundColor Gray
        $versions = Get-ChildItem -Path $basePath -Directory -ErrorAction SilentlyContinue | 
                    Sort-Object Name -Descending
        foreach ($version in $versions) {
            $psqlPath = Join-Path $version.FullName "bin\psql.exe"
            if (Test-Path $psqlPath) {
                Write-Host "   ✅ 找到: $psqlPath" -ForegroundColor Green
                $foundPaths += $psqlPath
                $found = $true
            }
        }
    }
}

if (-not $foundPaths) {
    Write-Host "   ❌ 未在常见路径中找到" -ForegroundColor Red
}
Write-Host ""

# 方法3: 检查注册表
Write-Host "3. 检查注册表..." -ForegroundColor Yellow
try {
    $regPath = "HKLM:\SOFTWARE\PostgreSQL\Installations"
    if (Test-Path $regPath) {
        $installations = Get-ChildItem -Path $regPath -ErrorAction SilentlyContinue
        foreach ($inst in $installations) {
            $baseDir = (Get-ItemProperty -Path $inst.PSPath -Name "Base Directory" -ErrorAction SilentlyContinue).'Base Directory'
            if ($baseDir) {
                $psqlPath = Join-Path $baseDir "bin\psql.exe"
                if (Test-Path $psqlPath) {
                    Write-Host "   ✅ 从注册表找到: $psqlPath" -ForegroundColor Green
                    $foundPaths += $psqlPath
                    $found = $true
                }
            }
        }
    } else {
        Write-Host "   ❌ 注册表中未找到安装信息" -ForegroundColor Red
    }
} catch {
    Write-Host "   ⚠️  无法访问注册表: $_" -ForegroundColor Yellow
}
Write-Host ""

# 总结
Write-Host "========================================" -ForegroundColor Cyan
if ($found) {
    Write-Host "✅ 找到 PostgreSQL 安装" -ForegroundColor Green
    Write-Host ""
    Write-Host "找到的 psql 路径:" -ForegroundColor Cyan
    $uniquePaths = $foundPaths | Select-Object -Unique
    foreach ($path in $uniquePaths) {
        Write-Host "  $path" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "使用方法:" -ForegroundColor Cyan
    Write-Host "  使用完整路径运行 psql:" -ForegroundColor White
    Write-Host "    `"$($uniquePaths[0])`" -h 127.0.0.1 -p 5432 -U postgres -d MootAI" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  或者添加到 PATH 环境变量:" -ForegroundColor White
    $binDir = Split-Path -Parent $uniquePaths[0]
    Write-Host "    $binDir" -ForegroundColor Gray
} else {
    Write-Host "❌ 未找到 PostgreSQL 安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "建议:" -ForegroundColor Yellow
    Write-Host "  1. 确认 PostgreSQL 已安装" -ForegroundColor White
    Write-Host "  2. 或者直接启动应用测试连接（应用会自动测试）" -ForegroundColor White
    Write-Host "  3. 或者使用 pgAdmin 图形界面工具" -ForegroundColor White
}
Write-Host "========================================" -ForegroundColor Cyan



