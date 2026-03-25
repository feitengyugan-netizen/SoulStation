# 智能问答功能实现说明

## 功能概述

已完成智能问答模块（chat）的后端API实现，包括：

### 1. 数据库模型
- `chat_dialogues` - 对话表
- `chat_messages` - 消息表
- `chat_tags` - 标签表
- `chat_dialogue_tags` - 对话标签关联表

### 2. API接口

#### 对话管理
- `GET /api/chat/list` - 获取对话历史列表
- `GET /api/chat/{id}` - 获取对话详情
- `POST /api/chat/create` - 创建新对话
- `DELETE /api/chat/{id}` - 删除对话
- `PUT /api/chat/{id}/title` - 更新对话标题

#### 消息管理
- `POST /api/chat/{id}/message` - 发送消息（集成豆包AI）

#### 标签管理
- `GET /api/chat/tags` - 获取所有标签
- `POST /api/chat/tag` - 创建自定义标签
- `DELETE /api/chat/tag/{id}` - 删除标签
- `POST /api/chat/{id}/tag` - 为对话添加标签

#### 其他功能
- `POST /api/chat/voice-to-text` - 语音转文字（待实现）

### 3. 核心文件

```
backend/app/
├── models/
│   └── chat.py              # 数据库模型
├── schemas/
│   └── chat.py              # Pydantic schemas
├── services/
│   ├── ai_service.py        # AI服务（豆包API集成）
│   └── chat_service.py      # 业务逻辑层
└── api/
    └── chat/
        ├── __init__.py
        └── router.py         # API路由
```

## 安装和运行步骤

### 1. 激活conda环境
```bash
conda activate soulstation
```

### 2. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3. 创建数据库表
```bash
python create_chat_tables.py
```

### 4. 启动服务
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API测试

### 1. 获取对话列表
```bash
curl -X GET "http://localhost:8000/api/chat/list" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 创建新对话
```bash
curl -X POST "http://localhost:8000/api/chat/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "心理咨询对话",
    "tag_ids": []
  }'
```

### 3. 发送消息
```bash
curl -X POST "http://localhost:8000/api/chat/1/message" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "你好，我最近感到很焦虑"
  }'
```

## AI配置

豆包API配置已添加到 `app/core/config.py`:
```python
DOUBAO_API_KEY: str = "4edcc3f5-e874-401f-b25b-ffcaff140645"
DOUBAO_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
DOUBAO_MODEL: str = "doubao-1-5-pro-32k-250115"
```

## 注意事项

1. **认证**: 所有接口都需要JWT token认证（在header中传入）
2. **软删除**: 删除对话和标签都是软删除，不会真正删除数据
3. **AI助手**: AI助手名称为"小宁"，具备专业的心理咨询知识
4. **上下文记忆**: 发送消息时会加载最近10条历史消息作为上下文

## 前端集成

前端已有完整的chat相关页面：
- `frontend/src/views/chat/ChatIndex.vue` - 对话列表
- `frontend/src/views/chat/ChatDetail.vue` - 对话详情
- `frontend/src/views/chat/TagManage.vue` - 标签管理
- `frontend/src/api/chat.js` - API封装

前端可直接调用后端API进行测试。

## 下一步

1. ✅ 数据库模型创建
2. ✅ API接口实现
3. ✅ AI服务集成
4. ⏳ 数据库表创建（需要运行脚本）
5. ⏳ 前后端联调测试
6. ⏳ 语音转文字功能（可选）
