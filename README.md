# AI模拟法庭项目

## 项目简介

AI模拟法庭是一个基于Vue 3和Spring Boot的全栈项目，用于模拟法庭场景的AI应用。

## 技术栈

### 前端技术栈

- **核心框架**
  - Vue 3.4+：使用 Composition API
  - Vite 5.1+：构建工具，提供快速开发服务器和构建

- **路由与状态管理**
  - Vue Router 4.3+：单页应用路由，支持路由守卫
  - Pinia 2.1+：状态管理

- **HTTP 与 UI**
  - Axios 1.6+：HTTP 客户端，处理 API 请求
  - Element Plus 2.5+：桌面端 UI 组件库
  - Vant 4.8+：移动端 UI 组件库
  - @vant/touch-emulator：桌面端模拟移动端触摸事件

- **样式与适配**
  - PostCSS：CSS 后处理
  - postcss-px-to-viewport：px 转 vw/vh，移动端适配
  - Autoprefixer：自动添加 CSS 前缀

- **开发工具**
  - ESLint：代码检查
  - Prettier：代码格式化

### 后端技术栈

- **核心框架**
  - Spring Boot 3.2.0：Java 应用框架
  - Java 17：JDK 版本

- **安全与认证**
  - Spring Security：安全框架
  - JWT (io.jsonwebtoken 0.12.3)：无状态认证

- **数据访问**
  - Spring Data JPA：ORM 数据访问
  - Hibernate：JPA 实现
  - PostgreSQL：关系型数据库

- **工具库**
  - Lombok：简化 Java 代码（减少样板代码）
  - Apache Commons IO：文件操作工具
  - Spring Boot Validation：数据验证

- **日志**
  - Logback：日志框架，支持文件滚动和归档

- **构建工具**
  - Maven：依赖管理与构建
  - Spotless Maven Plugin：代码格式化（Google Java Format）

## 项目结构

```
MootAI/
├── frontend/          # 前端项目
│   ├── src/
│   │   ├── router/    # 路由配置
│   │   ├── stores/    # Pinia状态管理
│   │   ├── utils/     # 工具函数
│   │   └── views/     # 页面组件
│   ├── vite.config.js # Vite配置
│   └── package.json
│
└── backend/           # 后端项目
    ├── src/
    │   └── main/
    │       ├── java/com/mootai/
    │       │   ├── config/    # 配置类
    │       │   ├── util/      # 工具类
    │       │   └── MootAiApplication.java
    │       └── resources/
    │           ├── application.yml
    │           └── logback-spring.xml
    └── pom.xml
```

## 快速开始

### 🚀 一键启动（推荐）

项目提供了便捷的一键启动脚本，自动按正确顺序启动后端和前端服务。

#### Windows

**方法一：PowerShell（推荐）**
```powershell
.\start.ps1
```

**方法二：批处理文件**
```cmd
start.bat
```

**停止服务**
```powershell
.\stop.ps1
```

#### Linux/Mac

```bash
# 添加执行权限（首次使用）
chmod +x start.sh stop.sh

# 启动服务
./start.sh

# 停止服务（按 Ctrl+C 或运行）
./stop.sh
```

**脚本参数**
- `--skip-backend` - 只启动前端（后端已运行）
- `--skip-frontend` - 只启动后端
- `--help` - 显示帮助信息

**示例**
```bash
# 只启动前端
./start.sh --skip-backend

# 只启动后端
./start.sh --skip-frontend
```

### ⚠️ 运行顺序说明

**重要：必须先启动后端，再启动前端！**

1. ✅ **先启动后端服务** - 等待看到"启动成功"提示后再启动前端
2. ✅ **再启动前端服务** - 前端通过代理连接到后端API (http://localhost:8080)
3. 🔄 如果后端未启动，前端API请求会失败

**使用一键启动脚本会自动处理启动顺序，无需手动操作！**

### 前端开发

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 启动开发服务器
```bash
npm run dev
```

4. 代码检查
```bash
npm run lint
```

5. 代码格式化
```bash
npm run format
```

### 后端开发

1. 确保已安装 Java 17 和 Maven

2. 配置数据库
   - 安装 PostgreSQL（确保服务正在运行）
   - 创建数据库 `MootAI`（主机：127.0.0.1，端口：5432）
   - 使用提供的脚本创建数据库（见下方数据库配置说明）
   - **重要**：配置本地数据库密码（见下方配置说明）

3. 配置本地环境
   ```bash
   cd backend
   # 复制示例配置文件
   cp src/main/resources/application-local.yml.example src/main/resources/application-local.yml
   # 编辑 application-local.yml，填入你的数据库密码和 JWT 密钥
   ```

4. 进入后端目录
```bash
cd backend
```

5. 编译项目
```bash
mvn clean compile
```

6. 运行项目
```bash
mvn spring-boot:run
```

   **⚠️ 如果启动失败，常见原因：**
   - 数据库 "MootAI" 未创建 → 运行 `backend/scripts/create-database.ps1` (Windows)
   - PostgreSQL 服务未运行 → 启动 PostgreSQL 服务
   - 数据库密码错误 → 检查 `application.yml` 配置
   - 详细故障排除：查看 `backend/TROUBLESHOOTING.md`

   启动成功后，控制台会显示：
   ```
   =========================================
   ✅ 数据库连接成功！
   ...
   =========================================
   ✅ MootAI 后端服务启动成功！
   =========================================
   🌐 服务地址: http://localhost:8080
   ...
   ```
   
   **重要**：看到"启动成功"提示后，再启动前端服务

7. 代码格式化
```bash
mvn spotless:apply
```

### 配置说明

⚠️ **安全提示**：数据库密码等敏感信息不会提交到 Git。

**配置方式（三选一）**：

1. **使用本地配置文件（推荐开发环境）**
   - 复制 `backend/src/main/resources/application-local.yml.example` 为 `application-local.yml`
   - 编辑 `application-local.yml`，填入你的数据库密码和 JWT 密钥
   - 该文件已在 `.gitignore` 中，不会被提交

2. **使用环境变量（推荐生产环境）**
   ```bash
   # Windows PowerShell
   $env:DB_PASSWORD="your-password"
   $env:JWT_SECRET="your-jwt-secret"
   
   # Linux/Mac
   export DB_PASSWORD=your-password
   export JWT_SECRET=your-jwt-secret
   ```

3. **查看详细配置说明**
   - 参考 `backend/CONFIG.md` 文件

详细配置说明请查看 `backend/CONFIG.md`

## 配置说明

### 前端配置

- **Vite代理**：已配置 `/api` 代理到 `http://localhost:8080`
- **PostCSS**：已配置移动端适配，设计稿宽度375px
- **ESLint & Prettier**：已配置代码检查和格式化规则

### 后端配置

- **端口**：8080
- **数据库**：PostgreSQL（主机：127.0.0.1，端口：5432，数据库名：MootAI）
- **JWT密钥**：需要在 `application.yml` 中修改生产环境的密钥
- **CORS**：已配置允许 `http://localhost:3000` 跨域访问

### 数据库配置

#### 创建数据库

项目使用 PostgreSQL 数据库，数据库名称为 `MootAI`。

**方法一：使用提供的脚本（推荐）**

- **Windows (PowerShell)**:
  ```powershell
  cd backend/scripts
  .\create-database.ps1
  ```

- **Linux/Mac**:
  ```bash
  cd backend/scripts
  chmod +x create-database.sh
  ./create-database.sh
  ```

- **使用 SQL 脚本**:
  ```bash
  psql -U postgres -h 127.0.0.1 -p 5432 -f backend/scripts/create-database.sql
  ```

**方法二：手动创建**

1. 连接到 PostgreSQL：
   ```bash
   psql -U postgres -h 127.0.0.1 -p 5432
   ```

2. 创建数据库：
   ```sql
   CREATE DATABASE "MootAI" WITH ENCODING 'UTF8';
   ```

3. 退出：
   ```sql
   \q
   ```

#### 数据库连接配置

数据库连接配置在 `application.yml` 中：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://127.0.0.1:5432/MootAI
    username: postgres
    password: 123456  # 请修改为你的实际密码
```

#### 表结构自动创建

项目使用 Spring Data JPA，配置了 `ddl-auto: update`：
- 应用启动时会自动创建表结构
- 如果表已存在，会根据 Entity 定义自动更新表结构
- 不会删除已存在的数据

详细说明请查看 `backend/src/main/resources/db/README.md`

## 开发注意事项

1. 前端使用 Composition API 进行开发
2. 后端使用 JWT 进行无状态认证
3. 数据库表结构由 JPA 自动生成（ddl-auto: update）
4. 生产环境需要修改 JWT 密钥和数据库密码

## 许可证

MIT

