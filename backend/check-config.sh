#!/bin/bash
# 检查配置文件是否被正确忽略

echo "检查敏感配置文件是否在 .gitignore 中..."
echo ""

if git check-ignore -q backend/src/main/resources/application-local.yml 2>/dev/null; then
    echo "✅ application-local.yml 已被正确忽略"
else
    echo "❌ application-local.yml 未被忽略，请检查 .gitignore"
fi

if [ -f "backend/src/main/resources/application-local.yml" ]; then
    echo "✅ application-local.yml 文件存在（本地配置）"
else
    echo "⚠️  application-local.yml 文件不存在，请从 example 文件复制"
fi

if [ -f "backend/src/main/resources/application-local.yml.example" ]; then
    echo "✅ application-local.yml.example 文件存在（示例文件）"
else
    echo "❌ application-local.yml.example 文件不存在"
fi

