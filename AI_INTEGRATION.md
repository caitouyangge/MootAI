# AI模拟法庭集成说明

## 📋 概述

已成功将AI接入模拟法庭系统，实现交互式庭审对话。用户可以选择公诉人或辩护人身份，AI将分别扮演对方律师和审判员角色。

## 🏗️ 架构说明

```
前端 (Vue) 
  ↓ HTTP请求
后端 (Spring Boot) 
  ↓ HTTP请求
AI服务 (Flask + Python SDK)
  ↓ 调用
AI模型 (court_debate_sdk)
```

## 🚀 启动步骤

### 1. 启动AI服务（Python）

```bash
# 进入AI服务目录
cd ai_service

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（可选）
export ADAPTER_DIR="court_debate_model"  # 模型目录路径
export LOAD_IN_4BIT="true"                # 是否使用4bit量化
export GPU_ID="0"                         # GPU设备ID
export PORT="5000"                         # 服务端口

# 启动服务
python app.py
```

**Windows PowerShell:**
```powershell
cd ai_service
pip install -r requirements.txt
$env:ADAPTER_DIR="court_debate_model"
$env:LOAD_IN_4BIT="true"
$env:GPU_ID="0"
$env:PORT="5000"
python app.py
```

服务启动后，应该看到：
```
[SDK] 开始加载模型...
[SDK] 模型加载完成！
启动AI服务，端口: 5000
```

### 2. 启动后端服务（Java）

```bash
cd backend
mvn spring-boot:run
```

确保后端配置中的AI服务地址正确（`application.yml`）：
```yaml
ai:
  service:
    url: http://localhost:5000
```

### 3. 启动前端服务（Vue）

```bash
cd frontend
npm install
npm run dev
```

## 📝 使用流程

1. **选择身份**：在案件创建页面选择"公诉人"或"辩护人"
2. **选择审判员类型**：在庭审页面选择审判员类型（专业型、强势型、偏袒型、中立型）
3. **开始庭审**：点击"开始庭审"按钮，审判员会宣布开庭
4. **交互对话**：
   - 在输入框中输入您的发言
   - 点击"发送"或按 `Ctrl+Enter`
   - AI会自动生成对方律师和审判员的回复
5. **结束庭审**：当审判员宣布休庭时，可以生成判决书

## 🔧 配置说明

### AI服务配置

在 `ai_service/app.py` 中可以通过环境变量配置：

- `ADAPTER_DIR`: 模型适配器目录（默认: `court_debate_model`）
- `LOAD_IN_4BIT`: 是否使用4bit量化（默认: `true`）
- `GPU_ID`: GPU设备ID（默认: `0`）
- `PORT`: 服务端口（默认: `5000`）

### 后端配置

在 `backend/src/main/resources/application.yml` 中配置：

```yaml
ai:
  service:
    url: http://localhost:5000  # AI服务地址
```

## 📡 API接口

### 后端接口

**生成辩论回复**
```
POST /api/debate/generate
Content-Type: application/json

{
  "user_identity": "plaintiff",  // 用户身份：plaintiff 或 defendant
  "current_role": "judge",        // 当前角色：judge, plaintiff, defendant
  "messages": [...],              // 对话历史
  "judge_type": "neutral",        // 审判员类型
  "case_description": "..."       // 案件描述
}
```

**健康检查**
```
GET /api/debate/health
```

### AI服务接口

**生成辩论回复**
```
POST http://localhost:5000/api/debate/generate
Content-Type: application/json

{
  "user_identity": "plaintiff",
  "current_role": "judge",
  "messages": [...],
  "judge_type": "neutral",
  "case_description": "..."
}
```

**健康检查**
```
GET http://localhost:5000/health
```

## 🐛 故障排除

### AI服务无法启动

1. **检查模型目录**：确保 `court_debate_model` 目录存在且包含模型文件
2. **检查GPU**：如果没有GPU，设置 `LOAD_IN_4BIT="false"` 或使用CPU（会很慢）
3. **检查依赖**：确保已安装所有Python依赖

### 后端无法连接AI服务

1. **检查AI服务是否运行**：访问 `http://localhost:5000/health`
2. **检查配置**：确认 `application.yml` 中的AI服务地址正确
3. **检查网络**：确保防火墙没有阻止端口5000

### API返回404错误

如果遇到 `/api/case/summarize` 或其他API返回404错误：

1. **重启AI服务**（最常见原因）：
   - Windows: 运行 `ai_service/restart_service.bat`
   - 或手动终止Python进程后重新运行 `python ai_service/app.py`
   
2. **验证路由**：运行 `python ai_service/test_api.py` 测试所有API

3. **检查代码版本**：确保运行的是最新版本的 `ai_service/app.py`

### 前端无法生成回复

1. **检查后端日志**：查看是否有错误信息
2. **检查AI服务日志**：查看AI服务是否有错误
3. **检查网络请求**：在浏览器开发者工具中查看网络请求

## 📚 代码结构

```
MootAI/
├── ai_service/              # AI服务（Python Flask）
│   ├── app.py              # Flask应用主文件
│   ├── requirements.txt    # Python依赖
│   └── README.md           # AI服务说明
├── backend/                # 后端服务（Spring Boot）
│   └── src/main/java/com/mootai/
│       ├── controller/
│       │   └── DebateController.java  # 辩论控制器
│       ├── service/
│       │   └── AiService.java         # AI服务调用
│       └── dto/
│           └── DebateRequest.java    # 辩论请求DTO
├── frontend/               # 前端（Vue 3）
│   └── src/components/
│       └── Debate.vue      # 辩论组件（已集成AI）
└── court_debate_sdk.py     # AI模型SDK
```

## ✅ 功能特性

- ✅ 用户可以选择公诉人或辩护人身份
- ✅ AI自动扮演对方律师角色
- ✅ AI自动扮演审判员角色（支持多种审判员类型）
- ✅ 交互式对话，实时生成回复
- ✅ 支持案件描述，AI根据案件背景生成回复
- ✅ 支持编辑已发送的消息
- ✅ 自动滚动到最新消息

## 🔮 未来改进

- [ ] 支持流式输出，实时显示AI生成内容
- [ ] 支持语音输入和输出
- [ ] 支持多轮对话历史管理
- [ ] 支持自定义提示词
- [ ] 支持案件文件上传和解析
- [ ] 支持庭审记录导出

