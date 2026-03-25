# 后台管理模块使用指南

## 概述

后台管理模块已完成开发，提供完整的系统管理功能。

## 功能特性

### 1. 管理员认证
- ✅ 管理员登录
- ✅ Token验证
- ✅ 角色权限管理

### 2. 仪表盘
- ✅ 实时统计数据
- ✅ 多维度图表展示
- ✅ 关键指标监控

### 3. 咨询师审核
- ✅ 待审核列表
- ✅ 审核操作（通过/拒绝）
- ✅ 审核理由记录

### 4. 知识管理
- ✅ 文章列表管理
- ✅ 创建/更新文章
- ✅ 删除文章

### 5. 用户管理
- ✅ 用户列表查询
- ✅ 封禁/解封用户
- ✅ 用户统计信息

### 6. 订单管理
- ✅ 订单列表查询
- ✅ 订单数据导出

## API接口清单

| 接口路径 | 方法 | 功能描述 | 权限 |
|----------|------|----------|------|
| `/api/admin/login` | POST | 管理员登录 | 公开 |
| `/api/admin/dashboard/stats` | GET | 获取仪表盘统计数据 | 管理员 |
| `/api/admin/dashboard/chart` | GET | 获取图表数据 | 管理员 |
| `/api/admin/counselors/pending` | GET | 获取待审核咨询师 | 管理员 |
| `/api/admin/counselor/{id}/review` | POST | 审核咨询师 | 管理员 |
| `/api/admin/knowledge/list` | GET | 获取知识文章列表 | 管理员 |
| `/api/admin/knowledge/save` | POST | 保存知识文章 | 管理员 |
| `/api/admin/knowledge/{id}` | DELETE | 删除知识文章 | 管理员 |
| `/api/admin/users` | GET | 获取用户列表 | 管理员 |
| `/api/admin/user/{id}/ban` | POST | 封禁/解封用户 | 管理员 |
| `/api/admin/orders` | GET | 获取订单列表 | 管理员 |
| `/api/admin/orders/export` | GET | 导出订单数据 | 管理员 |

## 数据库表结构

### Admin（管理员表）

```python
id                      # 管理员ID
username                # 用户名（唯一）
password_hash           # 密码哈希
real_name               # 真实姓名
email                   # 邮箱
role                    # 角色（super_admin/admin/editor）
permissions             # 权限列表（JSON格式）
is_active               # 是否激活
last_login_at           # 最后登录时间
last_login_ip           # 最后登录IP
created_at              # 创建时间
updated_at              # 更新时间
deleted_at              # 删除时间
```

## 角色权限说明

### 角色类型

| 角色 | 说明 | 权限 |
|------|------|------|
| super_admin | 超级管理员 | 所有权限 |
| admin | 普通管理员 | 大部分管理权限 |
| editor | 编辑员 | 内容管理权限 |

### 权限说明

**超级管理员**：
- 所有权限
- 管理员账号管理
- 系统配置管理

**普通管理员**：
- 仪表盘查看
- 咨询师审核
- 知识管理
- 用户管理
- 订单管理

**编辑员**：
- 知识文章管理
- 基础数据查看

## 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── admin.py              # 管理员模型（新增）
│   ├── schemas/
│   │   └── admin.py              # 管理员schemas（新增）
│   ├── services/
│   │   └── admin_service.py      # 管理员服务层（新增）
│   └── api/
│       └── admin/
│           └── __init__.py       # 管理员API路由（新增）
└── init_admin.py               # 初始化管理员（新增）
```

## 快速开始

### 1. 初始化数据库

```bash
cd backend

# 创建数据库表
python -c "from app.core.database import engine; from app.models.admin import Base; Base.metadata.create_all(bind=engine)"

# 初始化管理员账号
python init_admin.py
```

初始化后会创建默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`
- 角色：`super_admin`

⚠️ **重要提示**：请在首次登录后修改默认密码！

### 2. 重置管理员密码

```bash
# 重置为默认密码
python init_admin.py reset-password admin

# 重置为新密码
python init_admin.py reset-password admin "新密码"
```

### 3. 启动后端服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 测试接口

```bash
# 运行测试脚本
python test_admin_apis.py
```

### 5. 访问前端页面

- 管理员登录：`/admin/login`
- 后台仪表盘：`/admin/dashboard`
- 咨询师审核：`/admin/counselor-review`
- 知识管理：`/admin/knowledge`
- 用户管理：`/admin/user`
- 订单管理：`/admin/order`

## API使用示例

### 管理员登录

```bash
curl -X POST "http://localhost:8000/api/admin/login?username=admin&password=admin123"
```

### 获取仪表盘统计数据

```bash
curl -X GET "http://localhost:8000/api/admin/dashboard/stats" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 获取图表数据

```bash
# 用户增长趋势
curl -X GET "http://localhost:8000/api/admin/dashboard/chart?type=user" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# 活动趋势
curl -X GET "http://localhost:8000/api/admin/dashboard/chart?type=trend" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 获取待审核咨询师

```bash
curl -X GET "http://localhost:8000/api/admin/counselors/pending?page=1&page_size=10" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 审核咨询师

```bash
# 通过
curl -X POST "http://localhost:8000/api/admin/counselor/1/review" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'

# 拒绝
curl -X POST "http://localhost:8000/api/admin/counselor/1/review" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "reject", "reason": "资料不完整"}'
```

### 保存文章

```bash
curl -X POST "http://localhost:8000/api/admin/knowledge/save" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新文章标题",
    "summary": "文章摘要",
    "content": "# 文章内容\n\n这是文章的详细内容。",
    "content_type": "markdown",
    "category": "anxiety",
    "tags": "焦虑,心理健康",
    "status": "published"
  }'
```

### 删除文章

```bash
curl -X DELETE "http://localhost:8000/api/admin/knowledge/1" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 获取用户列表

```bash
curl -X GET "http://localhost:8000/api/admin/users?page=1&page_size=10" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 封禁/解封用户

```bash
# 封禁
curl -X POST "http://localhost:8000/api/admin/user/1/ban" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"banned": true, "reason": "违规操作"}'

# 解封
curl -X POST "http://localhost:8000/api/admin/user/1/ban" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"banned": false}'
```

### 获取订单列表

```bash
curl -X GET "http://localhost:8000/api/admin/orders?status=completed&page=1&page_size=10" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 导出订单数据

```bash
curl -X GET "http://localhost:8000/api/admin/orders/export" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -o orders.csv
```

## 仪表盘数据说明

### 统计指标

| 指标 | 说明 |
|------|------|
| user_count | 用户总数 |
| counselor_count | 咨询师总数 |
| order_count | 订单总数 |
| article_count | 文章总数 |
| today_user_count | 今日新增用户 |
| today_order_count | 今日新增订单 |
| total_revenue | 总收入 |
| pending_counselor_count | 待审核咨询师数 |

### 图表类型

| 类型 | 数据范围 | 说明 |
|------|---------|------|
| user | 最近30天 | 用户增长趋势 |
| trend | 最近7天 | 综合活动趋势 |
| order | 最近30天 | 订单趋势 |
| revenue | 最近30天 | 收入趋势 |

## 安全注意事项

### 1. 密码管理
- ✅ 密码使用bcrypt加密存储
- ⚠️ 首次登录后请立即修改默认密码
- ⚠️ 定期更换密码
- ⚠️ 使用强密码（包含大小写字母、数字、特殊字符）

### 2. Token管理
- Token包含管理员类型和角色信息
- Token有过期时间
- 妥善保管Token，不要泄露
- 登出后应清除本地Token

### 3. 权限控制
- 所有管理接口需要验证管理员身份
- 不同角色有不同权限
- 敏感操作有日志记录

### 4. 操作审计
- 记录关键操作日志
- 定期审查操作记录
- 异常操作监控

## 数据导出格式

### CSV导出字段

订单导出包含以下字段：
- 预约编号
- 用户ID、用户姓名、联系方式
- 咨询师ID、咨询师姓名
- 咨询方式
- 预约时间
- 价格、已付金额
- 订单状态
- 创建时间、完成时间、取消时间

## 常见问题

### Q1: 忘记管理员密码怎么办？

使用重置密码命令：
```bash
python init_admin.py reset-password admin "新密码"
```

### Q2: 如何创建新的管理员？

目前需要直接在数据库中创建，或扩展init_admin.py脚本。

### Q3: 管理员接口返回401错误？

检查：
1. Token是否有效
2. Token类型是否为admin
3. 管理员账号是否被禁用

### Q4: 如何修改管理员权限？

管理员权限由角色决定，如需更细粒度的权限控制，建议：
1. 扩展permissions字段
2. 在API中验证具体权限
3. 实现权限管理界面

### Q5: 导出的订单数据乱码？

确保：
1. 使用Excel打开时选择UTF-8编码
2. 或使用文本编辑器打开查看

## 扩展功能建议

未来可以考虑添加的功能：
1. 操作日志记录和查看
2. 权限管理系统
3. 批量操作功能
4. 数据备份和恢复
5. 系统配置管理
6. 通知管理
7. 报表生成
8. 敏感词过滤管理

## 联系支持

如有问题，请查看：
- 项目TODO.md
- API文档：http://localhost:8000/docs
- 测试脚本：test_admin_apis.py
