# 配置文件说明

## 配置文件结构

本项目使用 Spring Boot 的配置文件机制，支持多环境配置。

### 主配置文件
- `application.yml` - 主配置文件，包含公共配置，**会提交到 Git**
- `application-local.yml` - 本地开发环境配置，**不会提交到 Git**（包含敏感信息）

### 配置优先级
Spring Boot 会按以下顺序加载配置：
1. `application.yml`（基础配置）
2. `application-local.yml`（本地配置，会覆盖基础配置）

## 本地开发配置步骤

### 1. 创建本地配置文件

复制示例文件：
```bash
cp src/main/resources/application-local.yml.example src/main/resources/application-local.yml
```

### 2. 修改本地配置

编辑 `application-local.yml`，填入你的本地配置：

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/mootai
    username: postgres
    password: your-local-database-password  # 修改为你的数据库密码
    driver-class-name: org.postgresql.Driver

jwt:
  secret: your-local-jwt-secret-key  # 修改为你的 JWT 密钥
  expiration: 86400000
```

### 3. 使用环境变量（推荐）

你也可以使用环境变量来配置敏感信息，这样更安全：

#### Windows (PowerShell)
```powershell
$env:DB_PASSWORD="your-password"
$env:JWT_SECRET="your-jwt-secret"
```

#### Windows (CMD)
```cmd
set DB_PASSWORD=your-password
set JWT_SECRET=your-jwt-secret
```

#### Linux/Mac
```bash
export DB_PASSWORD=your-password
export JWT_SECRET=your-jwt-secret
```

#### 使用 .env 文件（需要额外插件）

如果你使用 IDE 插件支持 `.env` 文件，可以创建 `backend/.env`：

```
DB_URL=jdbc:postgresql://localhost:5432/mootai
DB_USERNAME=postgres
DB_PASSWORD=your-password
JWT_SECRET=your-jwt-secret
JWT_EXPIRATION=86400000
```

## 安全注意事项

⚠️ **重要**：
- ❌ **不要**将 `application-local.yml` 提交到 Git
- ❌ **不要**在 `application.yml` 中硬编码密码
- ✅ 使用环境变量或本地配置文件
- ✅ 生产环境使用环境变量或配置中心

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DB_URL` | 数据库连接URL | `jdbc:postgresql://localhost:5432/mootai` |
| `DB_USERNAME` | 数据库用户名 | `postgres` |
| `DB_PASSWORD` | 数据库密码 | 无（必须配置） |
| `JWT_SECRET` | JWT 密钥 | `your-secret-key-change-this-in-production` |
| `JWT_EXPIRATION` | JWT 过期时间（毫秒） | `86400000` |

