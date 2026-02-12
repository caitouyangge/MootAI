# AI模拟法庭服务

## 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量（可选）
export ADAPTER_DIR="court_debate_model"
export LOAD_IN_4BIT="true"
export GPU_ID="0"
export PORT="5000"

# 启动服务
python app.py
```

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

