#!/bin/bash
# 检查配置文件是否被正确忽略

echo "========================================"
echo "🔍 MootAI 配置检查"
echo "========================================"
echo ""

# 检查 .gitignore
echo "检查敏感配置文件是否在 .gitignore 中..."
if git check-ignore -q backend/src/main/resources/application-local.yml 2>/dev/null; then
    echo "✅ application-local.yml 已被正确忽略"
else
    echo "❌ application-local.yml 未被忽略，请检查 .gitignore"
fi
echo ""

# 检查配置文件存在性
echo "检查配置文件..."
if [ -f "backend/src/main/resources/application-local.yml" ]; then
    echo "✅ application-local.yml 文件存在（本地配置）"
    
    # 检查数据库配置
    echo ""
    echo "检查数据库配置..."
    
    # 读取数据库URL
    db_url=$(grep -E "^\s*url:" backend/src/main/resources/application-local.yml | sed 's/.*url:\s*//' | tr -d '"' | tr -d "'")
    db_username=$(grep -E "^\s*username:" backend/src/main/resources/application-local.yml | sed 's/.*username:\s*//' | tr -d '"' | tr -d "'")
    db_password=$(grep -E "^\s*password:" backend/src/main/resources/application-local.yml | sed 's/.*password:\s*//' | tr -d '"' | tr -d "'")
    
    if [ -n "$db_url" ]; then
        echo "  数据库URL: $db_url"
        
        # 检查数据库名称是否一致
        if echo "$db_url" | grep -qi "mootai"; then
            if echo "$db_url" | grep -q "MootAI"; then
                echo "  ✅ 数据库名称正确 (MootAI)"
            else
                echo "  ⚠️  数据库名称可能不一致，建议使用 'MootAI'（注意大小写）"
            fi
        fi
    fi
    
    if [ -n "$db_username" ]; then
        echo "  用户名: $db_username"
    fi
    
    if [ -n "$db_password" ]; then
        if [ "$db_password" = "your-local-database-password" ] || [ "$db_password" = "postgres" ]; then
            echo "  ⚠️  密码可能是默认值，请确保与实际数据库密码匹配"
        else
            echo "  ✅ 密码已配置"
        fi
    fi
else
    echo "⚠️  application-local.yml 文件不存在，请从 example 文件复制"
    echo "  运行: cp backend/src/main/resources/application-local.yml.example backend/src/main/resources/application-local.yml"
fi

if [ -f "backend/src/main/resources/application-local.yml.example" ]; then
    echo "✅ application-local.yml.example 文件存在（示例文件）"
else
    echo "❌ application-local.yml.example 文件不存在"
fi

echo ""
echo "========================================"
echo "💡 提示："
echo "  如果遇到数据库连接问题，请运行："
echo "    cd backend/scripts"
echo "    ./test-db-connection.ps1  (Windows)"
echo "    或"
echo "    psql -h 127.0.0.1 -p 5432 -U postgres -d MootAI"
echo "========================================"
