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
   - 安装 PostgreSQL
   - 创建数据库 `mootai`
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
- **数据库**：PostgreSQL（默认localhost:5432）
- **JWT密钥**：需要在 `application.yml` 中修改生产环境的密钥
- **CORS**：已配置允许 `http://localhost:3000` 跨域访问

## 开发注意事项

1. 前端使用 Composition API 进行开发
2. 后端使用 JWT 进行无状态认证
3. 数据库表结构由 JPA 自动生成（ddl-auto: update）
4. 生产环境需要修改 JWT 密钥和数据库密码

## 许可证

MIT

