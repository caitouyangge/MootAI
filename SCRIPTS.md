# 📜 脚本使用说明

## 启动脚本

### Windows

#### start.ps1 (PowerShell - 推荐)

功能最完整的启动脚本，支持参数和智能检测。

**使用方法**
```powershell
# 启动后端和前端
.\start.ps1

# 只启动前端（后端已运行）
.\start.ps1 -SkipBackend

# 只启动后端
.\start.ps1 -SkipFrontend

# 显示帮助
.\start.ps1 -Help
```

**特性**
- ✅ 自动检测 Java、Maven、Node.js、npm
- ✅ 自动等待后端启动完成
- ✅ 在新窗口中启动服务，便于查看日志
- ✅ 自动检查配置文件
- ✅ 彩色输出，易于阅读

**如果遇到执行策略错误**
```powershell
# 临时允许执行（推荐）
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 或直接运行
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

#### start.bat (批处理文件)

简单的批处理脚本，兼容性最好。

**使用方法**
```cmd
# 启动后端和前端
start.bat

# 只启动前端
start.bat --skip-backend

# 只启动后端
start.bat --skip-frontend

# 显示帮助
start.bat --help
```

**特性**
- ✅ 无需修改执行策略
- ✅ 兼容所有 Windows 版本
- ✅ 在新窗口中启动服务

### Linux/Mac

#### start.sh (Bash 脚本)

功能完整的启动脚本，支持后台运行和日志记录。

**首次使用**
```bash
# 添加执行权限
chmod +x start.sh stop.sh
```

**使用方法**
```bash
# 启动后端和前端（后台运行）
./start.sh

# 只启动前端
./start.sh --skip-backend

# 只启动后端
./start.sh --skip-frontend

# 显示帮助
./start.sh --help
```

**特性**
- ✅ 后台运行服务
- ✅ 日志文件：`logs/backend.log` 和 `logs/frontend.log`
- ✅ PID 文件：`logs/backend.pid` 和 `logs/frontend.pid`
- ✅ 支持 Ctrl+C 优雅停止
- ✅ 自动检测服务是否已启动

**查看日志**
```bash
# 查看后端日志
tail -f logs/backend.log

# 查看前端日志
tail -f logs/frontend.log
```

## 停止脚本

### Windows

#### stop.ps1

通过端口查找并停止服务。

```powershell
.\stop.ps1
```

### Linux/Mac

#### stop.sh

通过 PID 文件和端口查找并停止服务。

```bash
./stop.sh
```

## 脚本对比

| 特性 | start.ps1 | start.bat | start.sh |
|------|-----------|-----------|----------|
| 平台 | Windows | Windows | Linux/Mac |
| 智能检测 | ✅ | ❌ | ✅ |
| 等待后端启动 | ✅ | ⚠️ 简单等待 | ✅ |
| 后台运行 | ❌ (新窗口) | ❌ (新窗口) | ✅ |
| 日志文件 | ❌ | ❌ | ✅ |
| 参数支持 | ✅ | ⚠️ 基础 | ✅ |
| 彩色输出 | ✅ | ❌ | ✅ |

## 故障排除

### PowerShell 执行策略错误

**错误信息**
```
无法加载文件，因为在此系统上禁止运行脚本
```

**解决方法**
```powershell
# 方法1：临时允许（推荐）
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

# 方法2：直接运行（无需修改策略）
powershell -ExecutionPolicy Bypass -File .\start.ps1

# 方法3：使用批处理文件
start.bat
```

### 脚本无法找到命令

**问题**：脚本提示找不到 `java`、`mvn`、`node` 等命令

**解决方法**
1. 检查环境变量 PATH 是否包含这些工具的路径
2. 重新安装相关软件
3. 重启终端/命令行窗口

### Linux/Mac 权限错误

**错误信息**
```
Permission denied
```

**解决方法**
```bash
chmod +x start.sh stop.sh
```

### 端口被占用

**Windows**
```powershell
# 查找占用端口的进程
netstat -ano | findstr :8080
netstat -ano | findstr :3000

# 停止进程
taskkill /PID <进程ID> /F
```

**Linux/Mac**
```bash
# 查找并停止占用端口的进程
lsof -ti:8080 | xargs kill
lsof -ti:3000 | xargs kill
```

## 高级用法

### 自定义启动

如果需要自定义启动参数，可以：

1. **修改脚本**：编辑对应的启动脚本
2. **手动启动**：参考 README.md 中的手动启动说明
3. **使用 IDE**：在 IDE 中配置运行配置

### 开发模式

启动脚本会自动检测开发环境：
- 自动安装缺失的依赖
- 使用开发配置
- 启用热重载

### 生产模式

生产环境建议：
- 使用环境变量配置
- 使用进程管理器（如 PM2、systemd）
- 配置反向代理（如 Nginx）



