# 智能问答故障排查指南

## 问题：前端显示"消息发送失败"

### 快速解决方案

#### 方案1：确保后端服务正在运行

**步骤1**: 启动后端服务
```bash
conda activate soulstation
cd c:\Users\Jiang\Desktop\bs\SoulStation\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**步骤2**: 检查服务是否启动成功
打开浏览器访问: http://localhost:8000/docs

如果能看到API文档，说明服务启动成功。

#### 方案2：检查前端配置

**步骤1**: 检查环境变量文件
查看 `frontend/.env` 文件（如果没有则创建）：
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

**步骤2**: 重启前端开发服务器
```bash
cd frontend
npm run dev
```

#### 方案3：测试API连接

**测试1**: 登录
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'
```

期望返回：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "...",
    "userInfo": {...}
  }
}
```

**测试2**: 获取对话列表
```bash
# 先登录获取token，然后：
curl http://localhost:8000/api/chat/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 方案4：检查浏览器控制台

1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 查看错误信息

常见错误：
- `Network Error`: 后端服务未启动或URL错误
- `401 Unauthorized`: Token过期或无效
- `404 Not Found`: API路径错误
- `500 Internal Server Error`: 后端代码错误

#### 方案5：清除缓存

```bash
# 前端清除缓存
cd frontend
rm -rf node_modules/.vite
npm run dev
```

### 详细排查步骤

#### 1. 检查后端服务

```bash
# 检查8000端口是否被占用
netstat -ano | findstr :8000

# 如果被占用，停止进程或更换端口
# 更换端口：
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 然后修改前端 .env 文件：
# VITE_API_BASE_URL=http://localhost:8001/api
```

#### 2. 测试数据库连接

```bash
cd backend
python -c "from app.core.database import engine; print('数据库连接成功')"
```

#### 3. 检查对话是否存在

确保你有对话ID（dialogue_id）。如果没有，先创建一个：

```bash
# 使用curl创建对话
curl -X POST http://localhost:8000/api/chat/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"测试对话","tag_ids":[]}'
```

#### 4. 使用非流式端点（备用方案）

如果流式端点有问题，前端会自动降级到非流式端点。

非流式端点：`POST /api/chat/{dialogue_id}/message`

### 已修复的问题

✅ 1. 响应字段名不匹配 - 已修复
✅ 2. URL硬编码 - 已修复
✅ 3. AsyncOpenAI客户端配置 - 已修复
✅ 4. 前端降级机制 - 已添加

### 当前状态

- **非流式端点**: 完全可用，稳定
- **流式端点**: 已实现，可能需要调试

### 建议

1. **先使用非流式端点**: 确保基本功能可用
2. **逐步调试流式端点**: 后续可以优化

### 测试命令

```bash
# 完整测试流程
cd backend
python quick_test.py
```

### 联系支持

如果问题仍然存在，请提供：
1. 浏览器控制台错误信息
2. 后端服务器日志
3. 网络请求详情（F12 → Network标签）
