# 邮件发送功能说明

## 已实现的功能

### 1. 发送验证码邮件
- 自动生成6位数字验证码
- 发送到用户邮箱
- 验证码5分钟有效期
- 防止频繁发送（60秒冷却时间）
- 开发环境在控制台打印验证码

### 2. 发送欢迎邮件
- 用户注册成功后自动发送
- 精美的HTML邮件模板
- 包含平台介绍和功能说明

### 3. 验证码验证
- 验证用户输入的验证码
- 检查验证码是否过期
- 验证成功后自动删除

## 配置说明

当前配置（QQ邮箱）：

```env
MAIL_USERNAME=1748618129@qq.com
MAIL_PASSWORD=buxydgasahfwdfgj
MAIL_FROM=1748618129@qq.com
MAIL_FROM_NAME=SoulStation心理咨询平台
MAIL_PORT=587
MAIL_SERVER=smtp.qq.com
MAIL_TLS=True
MAIL_SSL=False
```

### 其他邮箱配置

#### Gmail
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password  # 需要生成应用专用密码
MAIL_FROM=your-email@gmail.com
MAIL_FROM_NAME=SoulStation
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_TLS=True
MAIL_SSL=False
```

#### 163邮箱
```env
MAIL_USERNAME=your-email@163.com
MAIL_PASSWORD=your-auth-code  # 需要使用授权码
MAIL_FROM=your-email@163.com
MAIL_FROM_NAME=SoulStation
MAIL_PORT=465
MAIL_SERVER=smtp.163.com
MAIL_TLS=False
MAIL_SSL=True
```

## 测试邮件功能

运行测试脚本：

```bash
python test_email.py
```

测试选项：
1. 发送验证码 - 测试发送验证码功能
2. 验证验证码 - 测试验证验证码功能
3. 发送欢迎邮件 - 测试发送欢迎邮件
4. 检查验证码剩余时间 - 查看验证码是否还有效

## API 接口

### 发送验证码

```http
POST /api/auth/send-code
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**响应：**

成功 (200):
```json
{
  "code": 200,
  "message": "验证码已发送",
  "data": {
    "expire_seconds": 300
  }
}
```

失败 (400):
```json
{
  "code": 400,
  "message": "请等待 45 秒后再试"
}
```

### 用户注册（使用验证码）

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "code": "123456",
  "password": "password123"
}
```

## 注意事项

1. **QQ邮箱授权码**：需要使用QQ邮箱的授权码，而不是QQ密码
   - 获取方式：QQ邮箱 → 设置 → 账户 → SMTP服务 → 生成授权码

2. **Gmail应用密码**：需要生成应用专用密码
   - 获取方式：Google账户 → 安全 → 应用专用密码

3. **163邮箱授权码**：需要使用授权码
   - 获取方式：163邮箱 → 设置 → POP3/SMTP/IMAP → 开启SMTP服务

4. **开发环境**：在DEBUG模式下，验证码会在控制台打印

5. **生产环境**：验证码不会在响应中返回，只能通过邮件获取

## 邮件模板

### 验证码邮件模板
- 包含6位大号验证码显示
- 有效期说明
- 安全警告

### 欢迎邮件模板
- 欢迎信息
- 平台功能介绍
- 快速开始按钮

## 故障排查

### 邮件发送失败

1. 检查SMTP配置是否正确
2. 确认授权码/密码是否正确
3. 检查网络连接
4. 查看后端日志错误信息

### 验证码验证失败

1. 确认验证码输入正确
2. 检查验证码是否过期（5分钟有效期）
3. 确认使用正确的邮箱

### 找不到邮件

1. 检查垃圾邮件文件夹
2. 确认邮箱地址输入正确
3. 等待几分钟后重试

## 技术实现

- **SMTP协议**：使用Python smtplib库
- **邮件格式**：HTML格式，支持富文本
- **验证码存储**：内存存储（可扩展到Redis）
- **防刷机制**：60秒冷却时间
- **过期清理**：自动清理过期验证码

## 文件结构

```
app/services/
├── email_service.py          # 邮件发送服务
├── verification_service.py   # 验证码存储服务
└── auth_service.py           # 认证服务（集成邮件功能）

app/api/auth/
└── router.py                 # 认证路由

test_email.py                 # 邮件功能测试脚本
```
