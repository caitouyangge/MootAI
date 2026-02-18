#!/bin/bash
# MootAI 停止脚本 (Linux/Mac)
# 功能：停止所有运行中的服务

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }
print_warning() { echo -e "${YELLOW}$1${NC}"; }
print_info() { echo -e "${CYAN}$1${NC}"; }

print_info "=========================================="
print_info "🛑 停止 MootAI 服务"
print_info "=========================================="
echo ""

# 停止后端
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null
        print_success "✅ 已停止后端服务 (PID: $BACKEND_PID)"
    else
        print_warning "⚠️  后端服务未运行"
    fi
    rm -f logs/backend.pid
else
    print_warning "⚠️  未找到后端 PID 文件"
fi

# 停止前端
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null
        print_success "✅ 已停止前端服务 (PID: $FRONTEND_PID)"
    else
        print_warning "⚠️  前端服务未运行"
    fi
    rm -f logs/frontend.pid
else
    print_warning "⚠️  未找到前端 PID 文件"
fi

# 尝试通过端口查找并停止进程
print_info "检查是否有残留进程..."

# 停止占用 8080 端口的进程（后端）
BACKEND_PORT=$(lsof -ti:8080 2>/dev/null)
if [ ! -z "$BACKEND_PORT" ]; then
    kill $BACKEND_PORT 2>/dev/null
    print_success "✅ 已停止占用 8080 端口的进程"
fi

# 停止占用 3000 端口的进程（前端）
FRONTEND_PORT=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT" ]; then
    kill $FRONTEND_PORT 2>/dev/null
    print_success "✅ 已停止占用 3000 端口的进程"
fi

echo ""
print_success "=========================================="
print_success "✅ 所有服务已停止"
print_success "=========================================="




