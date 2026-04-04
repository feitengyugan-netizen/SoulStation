# 管理员登录测试说明

## ✅ 已修复的问题

**问题**: 管理员账号无法通过邮箱登录

**原因**: `AuthService.login()` 只查询 `User` 表，没有查询 `Admin` 表

**解决方案**: 修改了登录逻辑，现在支持：
1. 先尝试在 `User` 表中查找（普通用户/咨询师）
2. 如果找不到，再在 `Admin` 表中查找
3. 管理员可以使用邮箱或用户名登录

## 🔧 修改的文件

- [backend/app/services/auth_service.py](backend/app/services/auth_service.py) - 登录服务逻辑

## 🧪 测试步骤

### 1. 确保后端服务正在运行

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问登录页面

打开浏览器访问: http://localhost:5175/login

### 3. 测试管理员登录

#### 方式1: 使用邮箱登录
```
邮箱: admin@soulstation.com
密码: admin123
```

#### 方式2: 使用用户名登录
```
邮箱: admin
密码: admin123
```

### 4. 验证登录成功

登录成功后应该：
- ✅ 显示"登录成功"提示
- ✅ 自动跳转到 `/admin/dashboard`
- ✅ 左侧显示管理后台导航菜单
- ✅ 右上角显示管理员名称

### 5. 测试其他功能

在管理后台测试：
- 用户管理
- 咨询师审核
- 订单管理
- 知识管理
- 测试管理
- 对话管理
- 系统设置

## 📊 测试账号汇总

### 管理员（2种登录方式）
```bash
# 邮箱登录
邮箱: admin@soulstation.com
密码: admin123

# 用户名登录
邮箱: admin
密码: admin123
```

### 普通用户（只能用邮箱）
```bash
邮箱: test@example.com
密码: 123456
```

### 咨询师（只能用邮箱）
```bash
邮箱: test@example.com
密码: 123456
```

## 🔍 登录逻辑说明

```
1. 用户输入邮箱/密码
   ↓
2. 先在 User 表中查找
   ├─ 找到 → 验证密码 → 返回用户信息
   │   ├─ role = 'user'    → 跳转到首页
   │   ├─ role = 'counselor' → 跳转到咨询师工作台
   │   └─ role = 'admin'   → 跳转到管理后台
   │
   └─ 未找到 → 在 Admin 表中查找
       ├─ 找到 → 验证密码 → 返回管理员信息
       │   └─ 跳转到 /admin/dashboard
       │
       └─ 未找到 → 返回"邮箱或密码错误"
```

## 🐛 常见问题

### Q: 提示"邮箱或密码错误"
**A**: 检查以下几点：
1. 确认使用的是 `admin@soulstation.com` 或 `admin`
2. 密码是 `admin123`
3. 数据库中是否有管理员记录
4. 管理员的 `is_active` 字段是否为 `True`

### Q: 登录成功但没有跳转到管理后台
**A**: 检查：
1. 前端是否正确接收并设置了 `userRole`
2. 路由守卫是否正确判断角色
3. 浏览器控制台是否有错误

### Q: 跳转到了管理后台但显示404
**A**: 确认：
1. `/admin/dashboard` 路由是否存在
2. AdminLayout 组件是否正确加载

## 📝 相关文件

- [backend/app/services/auth_service.py](backend/app/services/auth_service.py) - 登录服务
- [backend/app/models/admin.py](backend/app/models/admin.py) - 管理员模型
- [frontend/src/views/auth/Login.vue](frontend/src/views/auth/Login.vue) - 登录页面
- [frontend/src/layouts/AdminLayout.vue](frontend/src/layouts/AdminLayout.vue) - 管理后台布局

## ✨ 后续优化建议

1. **统一用户表**: 考虑将管理员和普通用户合并到同一个表
2. **添加登录日志**: 记录管理员的登录行为
3. **双因素认证**: 为管理员账号添加2FA
4. **会话管理**: 实现强制退出功能

---

**测试完成时间**: 2026-04-04
**修复状态**: ✅ 已完成
