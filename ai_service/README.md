# AI模拟法庭服务

## 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量（可选）
export ADAPTER_DIR="court_debate_model"  # 模型目录路径（相对路径或绝对路径）
export LOAD_IN_4BIT="true"
export GPU_ID="0"
export PORT="5000"

# 启动服务
python app.py
```

## 模型路径配置

模型路径支持以下方式：

1. **相对路径**（推荐）：系统会自动在以下位置查找：
   - 当前工作目录
   - `ai_service` 目录
   - 项目根目录

2. **绝对路径**：直接指定完整的模型目录路径

示例：
```bash
# Windows
set ADAPTER_DIR=D:\models\court_debate_model

# Linux/Mac
export ADAPTER_DIR=/path/to/court_debate_model
```

**注意**：模型目录必须包含 `adapter_config.json` 文件。

## API接口

### 1. 健康检查
```
GET /health
```

### 2. 单次生成
```
POST /api/generate
Body: {
  "prompt": "审判员：请公诉人开始陈述指控事实。",
  "max_new_tokens": 512,
  "temperature": 0.6,
  "system_prompt": "可选",
  "assistant_role": "可选"
}
```

### 3. 对话生成
```
POST /api/chat
Body: {
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "max_new_tokens": 512,
  "temperature": 0.6
}
```

### 4. 法庭辩论生成（推荐）

支持两种输入格式：

#### 格式A：训练数据格式（推荐，与训练数据格式一致）
```
POST /api/debate/generate
Body: {
  "agent_role": "审判员",        // 当前要回复的角色：审判员、公诉人、辩护人、原告、被告
  "background": "...",           // 案件背景
  "context": "审判员: 现在开庭...\n公诉人: 根据起诉书...",  // 对话历史（用\n分隔）
  "role_to_reply": "辩护人",     // 要回复的角色（可选，默认与agent_role相同）
  "instruction": "作为审判员，你需要：\n1. 保持中立..."  // 角色指令（可选）
}
```

示例：
```json
{
  "agent_role": "审判员",
  "background": "2025年6月间，被告人艾某某在新疆维吾尔自治区阿克苏市，多次于夜间趁无人之机，潜入某通信基站内，使用工具盗割通信电缆。",
  "context": "审判员: 现在进入法庭辩论阶段。请公诉人发表公诉意见。\n公诉人: 审判员，本案事实清楚，证据确实充分...\n辩护人: 审判员，我方对指控罪名及基本事实无异议...",
  "instruction": "作为审判员，你需要：\n1. 保持中立、客观、公正的立场\n2. 引导庭审程序有序进行，控制庭审节奏\n3. 对争议焦点进行归纳和总结"
}
```

#### 格式B：旧格式（向后兼容）
```
POST /api/debate/generate
Body: {
  "user_identity": "plaintiff",  // 用户身份：plaintiff 或 defendant
  "current_role": "judge",       // 当前角色：judge, plaintiff, defendant
  "messages": [...],              // 对话历史
  "judge_type": "neutral",        // 法官类型
  "case_description": "..."       // 案件描述
}
```

