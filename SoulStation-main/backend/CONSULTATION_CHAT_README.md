# 咨询对话模块使用指南

## 概述

咨询对话模块已完成开发，提供完整的咨询师与用户实时对话功能。

## 功能特性

### 1. 订单管理
- ✅ 咨询师查看订单列表
- ✅ 咨询师处理订单（同意/拒绝）
- ✅ 订单状态流转

### 2. 实时对话
- ✅ 发送文本消息
- ✅ 发送文件消息
- ✅ 增量获取消息
- ✅ 消息已读标记

### 3. 文件管理
- ✅ 上传文件（图片、文档、音频）
- ✅ 文件大小限制（10MB）
- ✅ 文件类型验证

### 4. 咨询管理
- ✅ 结束咨询
- ✅ 添加咨询备注
- ✅ 系统消息通知

## API接口清单

| 接口路径 | 方法 | 功能描述 | 权限 |
|----------|------|----------|------|
| `/api/consultation/counselor/orders` | GET | 获取咨询师订单列表 | 咨询师 |
| `/api/consultation/order/{id}/handle` | POST | 处理预约订单 | 咨询师 |
| `/api/consultation/{id}/messages` | GET | 获取对话消息 | 双方 |
| `/api/consultation/{id}/message` | POST | 发送消息 | 双方 |
| `/api/consultation/upload` | POST | 上传文件 | 双方 |
| `/api/consultation/{id}/end` | POST | 结束咨询 | 双方 |
| `/api/consultation/{id}/note` | POST | 添加咨询备注 | 咨询师 |

## 数据库表结构

### ConsultationMessage（咨询消息表）

```python
id                      # 消息ID
appointment_id          # 预约ID
sender_id               # 发送者ID
sender_type             # 发送者类型 (user/counselor)
message_type            # 消息类型 (text/image/file/system)
content                 # 消息内容
file_url                # 文件URL
file_name               # 文件名
file_size               # 文件大小（字节）
is_read                 # 是否已读
read_at                 # 读取时间
created_at              # 发送时间
```

## 业务流程

### 1. 预约流程

```
用户创建预约 → pending（待确认）
    ↓
咨询师处理 → agree → confirmed（已确认）
              reject → cancelled（已取消）
    ↓
开始对话 → in_progress（进行中）
    ↓
结束咨询 → completed（已完成）
```

### 2. 对话流程

1. **用户创建预约**
   - 状态：pending
   - 等待咨询师确认

2. **咨询师确认预约**
   - 操作：同意或拒绝
   - 发送系统通知

3. **开始对话**
   - 发送第一条消息时自动进入 in_progress 状态
   - 双方可发送文本和文件消息

4. **消息同步**
   - 支持增量获取（通过 last_id 参数）
   - 自动标记对方消息为已读

5. **结束咨询**
   - 咨询师或用户均可发起
   - 状态变更为 completed
   - 发送系统通知

## 消息类型

### 文本消息（text）
```json
{
  "content": "你好，我想咨询一下",
  "message_type": "text"
}
```

### 图片消息（image）
```json
{
  "message_type": "image",
  "file_url": "/uploads/consultation/xxx.jpg",
  "content": "这是我之前拍的图片"
}
```

### 文件消息（file）
```json
{
  "message_type": "file",
  "file_url": "/uploads/consultation/xxx.pdf",
  "content": "这是我的检查报告"
}
```

### 系统消息（system）
```json
{
  "message_type": "system",
  "content": "咨询师已确认您的预约"
}
```

## 文件上传

### 支持的文件类型

| 类型 | MIME类型 | 说明 |
|------|----------|------|
| 图片 | image/jpeg, image/png, image/gif | JPG、PNG、GIF |
| 文档 | application/pdf, application/msword | PDF、DOC、DOCX |
| 音频 | audio/mpeg, audio/wav | MP3、WAV |

### 文件大小限制
- 最大：10MB
- 超出限制会返回错误

### 上传流程

1. 客户端调用 `/api/consultation/upload` 上传文件
2. 服务器返回文件URL
3. 客户端发送消息时附带 file_url

## API使用示例

### 获取咨询师订单列表

```bash
curl -X GET "http://localhost:8000/api/consultation/counselor/orders?status=pending&page=1" \
  -H "Authorization: Bearer COUNSELOR_TOKEN"
```

### 咨询师同意预约

```bash
curl -X POST "http://localhost:8000/api/consultation/order/123/handle" \
  -H "Authorization: Bearer COUNSELOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "agree"
  }'
```

### 咨询师拒绝预约

```bash
curl -X POST "http://localhost:8000/api/consultation/order/123/handle" \
  -H "Authorization: Bearer COUNSELOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "reject",
    "reason": "该时段已有其他预约"
  }'
```

### 获取对话消息

```bash
# 首次获取
curl -X GET "http://localhost:8000/api/consultation/123/messages?limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 增量获取（获取最后一条消息之后的新消息）
curl -X GET "http://localhost:8000/api/consultation/123/messages?last_id=456&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 发送文本消息

```bash
curl -X POST "http://localhost:8000/api/consultation/123/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "你好，我想咨询一下关于焦虑的问题",
    "message_type": "text"
  }'
```

### 上传文件

```bash
curl -X POST "http://localhost:8000/api/consultation/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/file.pdf"
```

### 发送文件消息

```bash
curl -X POST "http://localhost:8000/api/consultation/123/message" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "file",
    "file_url": "/uploads/consultation/abc123.pdf",
    "content": "这是我的检查报告"
  }'
```

### 结束咨询

```bash
curl -X POST "http://localhost:8000/api/consultation/123/end" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 添加咨询备注

```bash
curl -X POST "http://localhost:8000/api/consultation/123/note" \
  -H "Authorization: Bearer COUNSELOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "note": "用户表现出明显的焦虑症状，建议采用认知行为疗法"
  }'
```

## 权限说明

### 用户端功能
- ✅ 查看自己的预约
- ✅ 发送消息
- ✅ 上传文件
- ✅ 结束咨询
- ❌ 查看其他用户的预约
- ❌ 处理预约订单
- ❌ 添加咨询备注

### 咨询师端功能
- ✅ 查看分配给自己的订单
- ✅ 处理预约订单（同意/拒绝）
- ✅ 发送消息
- ✅ 上传文件
- ✅ 结束咨询
- ✅ 添加咨询备注
- ❌ 查看其他咨询师的订单

## 状态说明

### 预约状态（Appointment.status）

| 状态 | 说明 | 可执行操作 |
|------|------|------------|
| pending | 待确认 | 咨询师可同意/拒绝，用户可取消 |
| confirmed | 已确认 | 双方可发送消息 |
| in_progress | 进行中 | 双方可发送消息，可结束咨询 |
| completed | 已完成 | 可查看历史，可评价 |
| cancelled | 已取消 | 只读 |
| refunded | 已退款 | 只读 |

## 前端集成

### 用户端页面
- 预约管理：`/counselor/orders`
- 对话页面：`/consultation/user/{appointment_id}`

### 咨询师端页面
- 订单处理：`/consultation/counselor/orders`
- 对话页面：`/consultation/counselor/{appointment_id}`

## 实时通信方案

当前实现使用轮询机制：

```javascript
// 前端轮询示例
setInterval(async () => {
  const lastMessageId = getLastMessageId();
  const response = await getMessages(appointmentId, {
    lastId: lastMessageId,
    limit: 50
  });

  if (response.data.items.length > 0) {
    // 处理新消息
    handleNewMessages(response.data.items);
  }
}, 3000); // 每3秒轮询一次
```

### WebSocket升级建议

未来可升级为WebSocket实现真正的实时通信：

```javascript
// WebSocket示例
const ws = new WebSocket(`ws://localhost:8000/ws/consultation/${appointment_id}`);

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleNewMessage(message);
};
```

## 文件存储

### 目录结构
```
uploads/
└── consultation/
    ├── images/
    ├── documents/
    └── audio/
```

### 访问URL
```
/uploads/consultation/{filename}
```

### 清理策略
建议定期清理超过30天的未引用文件。

## 测试

### 运行测试脚本

```bash
cd backend
python test_consultation_apis.py
```

### 测试覆盖

测试脚本包含以下测试：
1. 创建测试预约
2. 咨询师处理订单
3. 获取对话消息
4. 发送文本消息
5. 上传文件
6. 发送文件消息
7. 添加咨询备注
8. 结束咨询
9. 验证消息历史

## 注意事项

### 1. 权限验证
- 所有接口都会验证用户身份
- 咨询师专属接口需要验证咨询师身份
- 用户只能访问自己的预约和消息

### 2. 状态检查
- 发送消息前检查预约状态
- 只能在 confirmed 或 in_progress 状态发送消息
- 只能结束 in_progress 状态的咨询

### 3. 文件安全
- 验证文件类型
- 限制文件大小
- 对上传文件进行病毒扫描（建议）

### 4. 消息存储
- 消息按创建时间排序
- 支持增量获取减少数据传输
- 已读状态实时更新

### 5. 系统消息
- 关键操作自动发送系统通知
- 系统消息不可删除
- 帮助用户了解当前状态

## 扩展功能建议

未来可以考虑添加的功能：
1. WebSocket实时通信
2. 消息加密存储
3. 消息撤回功能
4. 语音消息
5. 视频通话集成
6. 消息搜索功能
7. 消息转发功能
8. 咨询记录导出

## 问题排查

### 消息发送失败
- 检查预约状态是否允许发送
- 验证文件URL是否有效
- 确认用户权限

### 文件上传失败
- 检查文件类型是否支持
- 确认文件大小未超限
- 验证 uploads 目录权限

### 获取消息为空
- 确认预约ID正确
- 检查用户权限
- 验证 last_id 参数

## 联系支持

如有问题，请查看：
- 项目TODO.md
- API文档：http://localhost:8000/docs
- 测试脚本：test_consultation_apis.py
