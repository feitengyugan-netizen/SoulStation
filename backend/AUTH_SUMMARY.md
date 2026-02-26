# 认证功能总结

## ✅ 已完成的功能

### 1. 用户登录
- **接口**: `POST /api/auth/login`
- **功能**: 邮箱+密码登录
- **返回**: JWT Token + 用户信息
- **测试账户**: test@example.com / 123456

### 2. 用户注册
- **接口**: `POST /api/auth/register`
- **功能**: 邮箱+验证码+密码注册
- **流程**:
  1. 发送验证码到邮箱
  2. 验证码验证
  3. 创建账户
  4. 自动发送欢迎邮件

### 3. 发送验证码
- **接口**: `POST /api/auth/send-code`
- **功能**: 发送6位数字验证码到邮箱
- **特性**:
  - 5分钟有效期
  - 60秒冷却时间（防刷）
  - 开发环境控制台显示
  - 精美HTML邮件模板

### 4. 忘记密码 - 验证邮箱
- **接口**: `POST /api/auth/verify-email-reset`
- **功能**: 验证邮箱和验证码（重置密码前）
- **流程**:
  1. 用户输入邮箱
  2. 发送验证码
  3. 验证通过后允许重置密码

### 5. 重置密码
- **接口**: `POST /api/auth/reset-password`
- **功能**: 重置用户密码
- **参数**: 邮箱 + 新密码
- **安全**: 需要先通过邮箱验证

### 6. 获取用户信息
- **接口**: `GET /api/auth/user-info`
- **功能**: 获取当前登录用户信息
- **认证**: 需要Bearer Token

### 7. 退出登录
- **接口**: `POST /api/auth/logout`
- **功能**: 退出登录（前端清除Token）

## 📧 邮件功能

### 验证码邮件
- 6位大号数字显示
- 有效期说明
- 安全警告提示

### 欢迎邮件
- 用户注册成功后自动发送
- 平台功能介绍
- 快速开始链接

## 🔐 安全特性

1. **密码加密**: Bcrypt哈希算法
2. **JWT认证**: 30天有效期
3. **验证码机制**:
   - 5分钟过期
   - 60秒冷却
   - 自动清理
4. **防刷保护**: 频繁发送限制
5. **邮箱验证**: 注册和重置密码都需要验证

## 📝 API 响应格式

所有接口统一返回格式：

```json
{
  "code": 200,
  "message": "成功信息",
  "data": {}
}
```

错误时：
```json
{
  "code": 400,
  "message": "错误信息"
}
```

## 🧪 测试

### 测试登录功能
```bash
python test_login.py
```

### 测试邮件功能
```bash
python test_email.py
```

### 测试账户
- **邮箱**: test@example.com
- **密码**: 123456

## 🔄 完整流程示例

### 注册流程
1. 用户输入邮箱
2. 调用 `/api/auth/send-code` 发送验证码
3. 用户输入验证码和新密码
4. 调用 `/api/auth/register` 完成注册
5. 系统自动发送欢迎邮件

### 登录流程
1. 用户输入邮箱和密码
2. 调用 `/api/auth/login`
3. 返回Token和用户信息
4. 前端保存Token到localStorage

### 忘记密码流程
1. 用户输入邮箱
2. 调用 `/api/auth/send-code` 发送验证码
3. 用户输入验证码
4. 调用 `/api/auth/verify-email-reset` 验证邮箱
5. 用户输入新密码
6. 调用 `/api/auth/reset-password` 重置密码
7. 使用新密码登录

## 📁 相关文件

### 后端
- `app/api/auth/router.py` - 认证路由
- `app/services/auth_service.py` - 认证服务
- `app/services/email_service.py` - 邮件服务
- `app/services/verification_service.py` - 验证码服务
- `app/schemas/auth.py` - 认证数据模型
- `app/models/user.py` - 用户数据模型

### 前端
- `src/api/auth.js` - 认证API
- `src/stores/user.js` - 用户状态管理
- `src/views/auth/Login.vue` - 登录页面
- `src/views/auth/Register.vue` - 注册页面
- `src/views/auth/ForgotPassword.vue` - 忘记密码页面

## ⚙️ 配置

### 邮箱配置
当前使用QQ邮箱：
```env
MAIL_USERNAME=1748618129@qq.com
MAIL_PASSWORD=buxydgasahfwdfgj  # QQ邮箱授权码
MAIL_FROM=1748618129@qq.com
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_TLS=True
```

### JWT配置
```env
SECRET_KEY=soulstation-secret-key-2024
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30天
```

## 🎯 下一步

所有基础认证功能已完成！可以继续开发：
- 用户个人资料编辑
- 头像上传
- 密码修改（已登录状态）
- 第三方登录（微信/QQ）
- 手机号绑定
