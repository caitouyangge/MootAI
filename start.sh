#!/bin/bash
# MootAI 一键启动脚本 (Linux/Mac)
# 功能：自动启动后端和前端服务

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 输出函数
print_success() { echo -e "${GREEN}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }
print_warning() { echo -e "${YELLOW}$1${NC}"; }
print_info() { echo -e "${CYAN}$1${NC}"; }

# 显示帮助信息
show_help() {
    print_info "MootAI 一键启动脚本"
    echo ""
    echo "用法:"
    echo "    ./start.sh                  # 启动后端和前端"
    echo "    ./start.sh --skip-backend    # 只启动前端（后端已运行）"
    echo "    ./start.sh --skip-frontend   # 只启动后端"
    echo "    ./start.sh --help            # 显示帮助信息"
    echo ""
    exit 0
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查后端是否已运行
check_backend_running() {
    curl -s http://localhost:8080/actuator/health >/dev/null 2>&1
    return $?
}

# 等待后端启动
wait_backend_start() {
    print_info "等待后端服务启动..."
    local max_attempts=60
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        sleep 2
        attempt=$((attempt + 1))
        
        if check_backend_running; then
            print_success "✅ 后端服务已启动！"
            return 0
        fi
        
        echo -n "."
    done
    
    echo ""
    print_warning "⚠️  后端服务启动超时，但将继续启动前端..."
    return 1
}

# 启动后端
start_backend() {
    print_info "=========================================="
    print_info "🚀 启动后端服务..."
    print_info "=========================================="
    
    # 检查 Java
    if ! command_exists java; then
        print_error "❌ 未找到 Java，请先安装 Java 17"
        exit 1
    fi
    
    # 检查 Maven
    if ! command_exists mvn; then
        print_error "❌ 未找到 Maven，请先安装 Maven"
        exit 1
    fi
    
    # 检查后端目录
    if [ ! -d "backend" ]; then
        print_error "❌ 未找到 backend 目录"
        exit 1
    fi
    
    # 检查配置文件
    if [ ! -f "backend/src/main/resources/application-local.yml" ]; then
        print_warning "⚠️  未找到 application-local.yml，将使用默认配置"
        print_info "提示：可以复制 application-local.yml.example 创建本地配置"
    fi
    
    # 启动后端（在后台）
    print_info "正在启动后端服务（端口：8080）..."
    cd backend || exit 1
    
    # 使用 nohup 在后台运行，并重定向输出到日志文件
    nohup mvn spring-boot:run > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    
    cd ..
    
    # 等待后端启动
    wait_backend_start
}

# 启动前端
start_frontend() {
    print_info "=========================================="
    print_info "🚀 启动前端服务..."
    print_info "=========================================="
    
    # 检查 Node.js
    if ! command_exists node; then
        print_error "❌ 未找到 Node.js，请先安装 Node.js"
        exit 1
    fi
    
    # 检查 npm
    if ! command_exists npm; then
        print_error "❌ 未找到 npm，请先安装 npm"
        exit 1
    fi
    
    # 检查前端目录
    if [ ! -d "frontend" ]; then
        print_error "❌ 未找到 frontend 目录"
        exit 1
    fi
    
    # 创建日志目录
    mkdir -p logs
    
    # 检查 node_modules
    if [ ! -d "frontend/node_modules" ]; then
        print_warning "⚠️  未找到 node_modules，正在安装依赖..."
        cd frontend || exit 1
        npm install
        cd ..
    fi
    
    # 启动前端（在后台）
    print_info "正在启动前端服务（端口：3000）..."
    cd frontend || exit 1
    
    # 使用 nohup 在后台运行，并重定向输出到日志文件
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    
    cd ..
}

# 清理函数（捕获退出信号）
cleanup() {
    print_info ""
    print_warning "正在停止服务..."
    
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID 2>/dev/null
            print_info "已停止后端服务 (PID: $BACKEND_PID)"
        fi
        rm -f logs/backend.pid
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID 2>/dev/null
            print_info "已停止前端服务 (PID: $FRONTEND_PID)"
        fi
        rm -f logs/frontend.pid
    fi
    
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM

# 主流程
print_info "=========================================="
print_info "🎯 MootAI 一键启动脚本"
print_info "=========================================="
echo ""

# 创建日志目录
mkdir -p logs

# 解析参数
SKIP_BACKEND=false
SKIP_FRONTEND=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-backend)
            SKIP_BACKEND=true
            shift
            ;;
        --skip-frontend)
            SKIP_FRONTEND=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "未知参数: $1"
            show_help
            ;;
    esac
done

# 启动后端
if [ "$SKIP_BACKEND" = false ]; then
    start_backend
    echo ""
fi

# 启动前端
if [ "$SKIP_FRONTEND" = false ]; then
    start_frontend
    echo ""
fi

# 显示启动信息
print_success "=========================================="
print_success "✅ 启动完成！"
print_success "=========================================="
print_info ""
print_info "📱 前端地址: http://localhost:3000"
print_info "🔧 后端地址: http://localhost:8080"
print_info ""
print_info "💡 提示："
print_info "   - 服务已在后台运行"
print_info "   - 日志文件: logs/backend.log 和 logs/frontend.log"
print_info "   - 按 Ctrl+C 停止所有服务"
print_info ""

# 保持脚本运行，等待用户中断
print_info "按 Ctrl+C 停止所有服务..."
while true; do
    sleep 1
done



