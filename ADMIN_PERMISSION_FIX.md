# 管理员权限问题修复说明

## 🐛 问题描述

管理员通过统一登录接口登录后，访问后台管理API时返回 **403 Forbidden** 错误。

## 🔍 问题原因

后台管理API的权限验证函数 `get_current_admin()` 要求JWT token中必须包含 `"type": "admin"` 字段：

```python
if not payload or payload.get("type") != "admin":
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的管理员令牌"
    )
```

但在 `auth_service.py` 中创建管理员token时，只设置了 `role` 字段，**没有设置 `type` 字段**：

```python
# 修复前
access_token = create_access_token(
    data={"sub": str(admin.id), "email": admin.email, "role": "admin"}
    # ❌ 缺少 "type": "admin"
)
```

## ✅ 修复方案

在创建管理员token时添加 `type` 字段：

```python
# 修复后
access_token = create_access_token(
    data={
        "sub": str(admin.id),
        "email": admin.email or admin.username,
        "role": "admin",
        "type": "admin"  # ✅ 添加type标识
    }
)
```

## 📝 修改的文件

- [backend/app/services/auth_service.py](backend/app/services/auth_service.py) - 第227行

## 🧪 测试步骤

### 1. 重启后端服务

```bash
# 停止当前运行的服务 (Ctrl+C)
# 重新启动
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 清除浏览器缓存

1. 打开浏览器开发者工具 (F12)
2. 进入 Application 标签
3. 在 Local Storage 中找到 `http://localhost:5175`
4. 删除以下项：
   - `token`
   - `userInfo`
   - `userRole`

### 3. 重新登录

访问 http://localhost:5175/login

使用管理员账号登录：
```
邮箱: admin@soulstation.com (或 admin)
密码: admin123
```

### 4. 验证Token内容

登录后，在浏览器控制台查看token：

```javascript
const token = localStorage.getItem('token')
// 复制token内容，使用 jwt.io 解码查看
// 应该包含: { "sub": "1", "email": "...", "role": "admin", "type": "admin" }
```

### 5. 测试后台管理API

登录后应该能正常访问以下接口：

- ✅ `/api/admin/dashboard/stats` - 获取统计数据
- ✅ `/api/admin/users` - 用户列表
- ✅ `/api/admin/counselors/pending` - 待审核咨询师
- ✅ `/api/admin/orders` - 订单列表
- ✅ `/api/admin/knowledge/list` - 知识文章列表

## 🔧 JWT Token 结构对比

### 普通用户Token
```json
{
  "sub": "123",
  "email": "user@example.com",
  "role": "user"
}
```

### 咨询师Token
```json
{
  "sub": "456",
  "email": "counselor@example.com",
  "role": "counselor"
}
```

### 管理员Token（修复后）
```json
{
  "sub": "1",
  "email": "admin@soulstation.com",
  "role": "admin",
  "type": "admin"  // ✅ 关键字段
}
```

## 📊 权限验证流程

```
用户登录
   ↓
创建Token（包含 type 字段）
   ↓
保存到 localStorage
   ↓
访问后台API时携带Token
   ↓
get_current_admin() 验证
   ├─ 检查 token 是否存在
   ├─ 检查 type == "admin"  ✅
   ├─ 检查管理员是否有效
   └─ 返回管理员信息
   ↓
允许访问后台管理API
```

## 🎯 相关API端点

### 后台管理API（需要 type="admin"）
- `/api/admin/dashboard/*` - 仪表盘
- `/api/admin/users` - 用户管理
- `/api/admin/counselors/*` - 咨询师审核
- `/api/admin/orders` - 订单管理
- `/api/admin/knowledge/*` - 知识管理

### 普通API（不需要type字段）
- `/api/auth/*` - 认证相关
- `/api/chat/*` - 聊天相关
- `/api/test/*` - 测试相关
- `/api/counselor/*` - 咨询师相关
- `/api/knowledge/*` - 知识库（公开）
- `/api/user/*` - 用户相关

## 🚨 常见错误及解决

### 401 Unauthorized
- **原因**: Token无效或已过期
- **解决**: 重新登录获取新Token

### 403 Forbidden
- **原因**: Token中没有 `type="admin"` 字段
- **解决**: 修复后重新登录

### 500 Internal Server Error
- **原因**: 服务器内部错误
- **解决**: 查看后端日志，检查数据库连接

## 📖 相关文档

- [JWT认证说明](https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/)
- [Token权限管理](./JWT_TOKEN_MANAGEMENT.md)
- [管理员登录测试](./ADMIN_LOGIN_TEST.md)

## ✨ 优化建议

1. **统一Token格式**: 考虑为所有角色的token都添加 `type` 字段
2. **Token刷新机制**: 实现refresh token机制
3. **权限细化**: 使用RBAC模型实现更细粒度的权限控制
4. **审计日志**: 记录管理员的敏感操作

---

**修复完成时间**: 2026-04-04
**修复状态**: ✅ 已完成
**影响范围**: 管理员登录后的后台API访问
