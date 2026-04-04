# 个人中心模块使用指南

## 概述

个人中心模块已完成开发，提供完整的用户资料管理、隐私设置、数据统计等功能。

## 功能特性

### 1. 用户资料管理
- ✅ 查看用户资料
- ✅ 更新用户资料（昵称、手机号、出生日期、性别、个人简介）
- ✅ 上传头像（支持JPG、PNG、GIF，最大2MB）

### 2. 隐私设置
- ✅ 对话隐私控制（保存历史、AI分析、可见性）
- ✅ 测试隐私控制（保存记录、可见性、趋势分析）

### 3. 数据管理
- ✅ 清除对话记录
- ✅ 清除测试记录
- ✅ 注销账户

### 4. 数据统计
- ✅ 用户活动统计（测试、对话、预约、收藏）
- ✅ 活动趋势分析（7/30/90天）
- ✅ 测试分类分布
- ✅ 对话主题分布

## API接口清单

| 接口路径 | 方法 | 功能描述 |
|----------|------|----------|
| `/api/user/profile` | GET | 获取用户资料 |
| `/api/user/profile` | PUT | 更新用户资料 |
| `/api/user/avatar` | POST | 上传头像 |
| `/api/user/privacy` | GET | 获取隐私设置 |
| `/api/user/privacy` | PUT | 更新隐私设置 |
| `/api/user/chat-history` | DELETE | 清除对话记录 |
| `/api/user/test-records` | DELETE | 清除测试记录 |
| `/api/user/statistics` | GET | 获取用户数据统计 |
| `/api/user/activity-trend` | GET | 获取活动趋势数据 |
| `/api/user/test-distribution` | GET | 获取测试分类分布 |
| `/api/user/chat-distribution` | GET | 获取对话主题分布 |
| `/api/user/delete-account` | POST | 注销账户 |

## 数据库变更

### User模型扩展字段

```python
# 新增字段
bio = Column(Text, comment="个人简介")

# 隐私设置字段
save_chat_history = Column(Boolean, default=True)
allow_ai_analysis = Column(Boolean, default=False)
chat_only_visible = Column(Boolean, default=False)
save_test_records = Column(Boolean, default=True)
test_only_visible = Column(Boolean, default=False)
allow_trend_analysis = Column(Boolean, default=True)
```

### 数据库迁移

如果需要更新现有数据库，请执行：

```bash
cd backend
python -c "from app.core.database import engine; from app.models.user import Base; Base.metadata.create_all(bind=engine)"
```

## 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── user.py              # 用户模型（已扩展）
│   ├── schemas/
│   │   └── user.py              # 用户schemas（已更新）
│   ├── services/
│   │   └── user_service.py      # 用户服务层（新增）
│   └── api/
│       └── user/
│           └── __init__.py      # 用户API路由（已扩展）
├── uploads/
│   └── avatars/                 # 头像存储目录（自动创建）
└── test_user_apis.py            # API测试脚本（新增）
```

## 快速开始

### 1. 启动后端服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 测试API接口

```bash
# 运行测试脚本
python test_user_apis.py
```

测试前请确保：
- 后端服务正在运行
- 数据库中存在测试用户（test@example.com / test123456）
- 或修改测试脚本中的用户凭证

### 3. 前端集成

前端已经完全集成，无需修改。直接访问前端页面即可：
- 个人中心主页：`/profile`
- 编辑资料：`/profile/edit`
- 隐私设置：`/profile/privacy`
- 数据统计：`/profile/statistics`

## API使用示例

### 获取用户资料

```bash
curl -X GET "http://localhost:8000/api/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 更新用户资料

```bash
curl -X PUT "http://localhost:8000/api/user/profile" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "新昵称",
    "phone": "13800138000",
    "gender": "male",
    "bio": "这是我的个人简介"
  }'
```

### 上传头像

```bash
curl -X POST "http://localhost:8000/api/user/avatar" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/avatar.jpg"
```

### 获取数据统计

```bash
curl -X GET "http://localhost:8000/api/user/statistics?timeRange=30days" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 注意事项

### 1. 文件上传
- 支持的格式：JPG、PNG、GIF
- 文件大小限制：2MB
- 存储路径：`uploads/avatars/`
- 访问URL：`/uploads/avatars/{filename}`

### 2. 隐私设置
- 所有隐私设置默认为安全状态
- 用户可随时修改设置
- 设置会影响数据存储和分析行为

### 3. 数据清除
- 清除操作不可恢复
- 清除对话记录会删除所有对话和消息
- 清除测试记录会删除所有测试结果和进度

### 4. 账户注销
- 注销操作不可恢复
- 所有用户数据将被清除或匿名化
- 邮箱会被标记为已删除但可复用

## 扩展功能建议

未来可以考虑添加的功能：
1. 账户安全设置（修改密码、两步验证）
2. 消息通知设置
3. 数据导出功能
4. 账号绑定/解绑
5. 个性化主题设置
6. 更多统计数据维度

## 问题排查

### 头像上传失败
- 检查文件格式是否支持
- 检查文件大小是否超限
- 确保 `uploads/avatars/` 目录存在且有写入权限

### 数据统计不显示
- 确认用户有相应的测试或对话记录
- 检查时间范围参数是否正确

### API返回401错误
- 检查token是否有效
- 确认请求头包含正确的Authorization字段

## 联系支持

如有问题，请查看：
- 项目TODO.md
- API文档：http://localhost:8000/docs
- 测试脚本：test_user_apis.py
