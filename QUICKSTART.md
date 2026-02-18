# 🚀 快速开始指南

## 前置要求

### 必需软件
- ✅ **Java 17+** - 后端运行环境
- ✅ **Maven 3.6+** - 后端构建工具
- ✅ **Node.js 16+** - 前端运行环境
- ✅ **npm 或 yarn** - 前端包管理器
- ✅ **PostgreSQL 12+** - 数据库

### 检查安装

**Windows (PowerShell)**
```powershell
java -version
mvn -version
node -v
npm -v
psql --version
```

**Linux/Mac**
```bash
java -version
mvn -version
node -v
npm -v
psql --version
```

## 快速启动（3步）

### 1️⃣ 配置数据库

**创建数据库**
```bash
# Windows
cd backend/scripts
.\create-database.ps1

# Linux/Mac
cd backend/scripts
chmod +x create-database.sh
./create-database.sh
```

**配置数据库密码**
- 编辑 `backend/src/main/resources/application-local.yml`
- 修改数据库密码（如果使用默认配置，密码为 `123456`）

### 2️⃣ 一键启动

**Windows**
```powershell
# PowerShell（推荐）
.\start.ps1

# 或批处理文件
start.bat
```

**Linux/Mac**
```bash
# 首次使用需要添加执行权限
chmod +x start.sh stop.sh

# 启动服务
./start.sh
```

### 3️⃣ 访问应用

- 🌐 **前端地址**: http://localhost:3000
- 🔧 **后端地址**: http://localhost:8080

## 停止服务

**Windows**
```powershell
.\stop.ps1
```

**Linux/Mac**
```bash
# 如果使用 start.sh 启动，按 Ctrl+C
# 或使用停止脚本
./stop.sh
```

## 常见问题

### ❌ 后端启动失败

**问题：数据库连接失败**
- ✅ 检查 PostgreSQL 服务是否运行
- ✅ 检查数据库 `MootAI` 是否已创建
- ✅ 检查 `application-local.yml` 中的数据库密码是否正确

**问题：端口 8080 被占用**
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -ti:8080 | xargs kill
```

### ❌ 前端启动失败

**问题：端口 3000 被占用**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <进程ID> /F

# Linux/Mac
lsof -ti:3000 | xargs kill
```

**问题：node_modules 缺失**
```bash
cd frontend
npm install
```

### ❌ 前端无法连接后端

- ✅ 确保后端服务已启动（访问 http://localhost:8080 测试）
- ✅ 检查后端控制台是否有错误
- ✅ 检查浏览器控制台的网络请求错误

## 手动启动（不使用脚本）

如果一键启动脚本无法使用，可以手动启动：

### 启动后端

```bash
cd backend
mvn spring-boot:run
```

等待看到 "启动成功" 提示后，再启动前端。

### 启动前端

**新开一个终端窗口**
```bash
cd frontend
npm install  # 首次使用
npm run dev
```

## 开发模式说明

### 后端热重载
- Spring Boot DevTools 已配置
- 修改 Java 代码后会自动重启（首次编译较慢）

### 前端热重载
- Vite 已配置热模块替换（HMR）
- 修改 Vue 代码后立即生效，无需刷新页面

## 下一步

- 📖 查看 [README.md](README.md) 了解项目详情
- 🔧 查看 [backend/CONFIG.md](backend/CONFIG.md) 了解配置说明
- 🐛 查看 [backend/TROUBLESHOOTING.md](backend/TROUBLESHOOTING.md) 了解故障排除




