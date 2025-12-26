# PowerShell 脚本：检查配置文件是否被正确忽略

Write-Host "检查敏感配置文件是否在 .gitignore 中..." -ForegroundColor Cyan
Write-Host ""

$localConfig = "src/main/resources/application-local.yml"
$exampleConfig = "src/main/resources/application-local.yml.example"

# 检查文件是否在 gitignore 中（需要先初始化 git 仓库）
if (Test-Path ".git") {
    $gitCheck = git check-ignore -q $localConfig 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ application-local.yml 已被正确忽略" -ForegroundColor Green
    } else {
        Write-Host "⚠️  无法验证 gitignore（可能未初始化 git 仓库）" -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ️  未检测到 .git 目录，跳过 gitignore 检查" -ForegroundColor Yellow
}

# 检查文件是否存在
if (Test-Path $localConfig) {
    Write-Host "✅ application-local.yml 文件存在（本地配置）" -ForegroundColor Green
} else {
    Write-Host "⚠️  application-local.yml 文件不存在，请从 example 文件复制" -ForegroundColor Yellow
    Write-Host "   运行: Copy-Item $exampleConfig $localConfig" -ForegroundColor Gray
}

if (Test-Path $exampleConfig) {
    Write-Host "✅ application-local.yml.example 文件存在（示例文件）" -ForegroundColor Green
} else {
    Write-Host "❌ application-local.yml.example 文件不存在" -ForegroundColor Red
}

Write-Host ""
Write-Host "提示：application-local.yml 包含敏感信息，不应提交到 Git" -ForegroundColor Cyan

