# 邮件服务配置指南

## 概述

本项目已集成完整的邮件通知系统，包括：

### 1. 预约邮件提醒
- ✅ 预约成功通知（用户）
- ✅ 预约成功通知（咨询师）
- ✅ 临近咨询提醒（提前1小时）
- ✅ 预约取消通知

### 2. 审核通知邮件
- ✅ 咨询师审核通过通知
- ✅ 咨询师审核拒绝通知（含理由）

### 3. 其他邮件
- ✅ 注册验证码邮件
- ✅ 欢迎邮件

## 快速配置

### 步骤1：配置邮箱服务器

编辑 `backend/app/core/config.py` 文件，配置以下参数：

```python
# 邮件配置
MAIL_USERNAME: str = "your_email@qq.com"  # 你的邮箱
MAIL_PASSWORD: str = "your_password"       # 邮箱授权码（不是登录密码）
MAIL_FROM: str = "your_email@qq.com"      # 发件人邮箱
MAIL_FROM_NAME: str = "SoulStation"       # 发件人名称
MAIL_PORT: int = 587                      # SMTP端口
MAIL_SERVER: str = "smtp.qq.com"          # SMTP服务器地址
MAIL_TLS: bool = True                     # 使用TLS
MAIL_SSL: bool = False                    # 不使用SSL
```

### 步骤2：获取邮箱授权码

#### QQ邮箱配置示例

```python
MAIL_SERVER = "smtp.qq.com"
MAIL_PORT = 587
MAIL_TLS = True
MAIL_SSL = False
```

**获取授权码步骤：**
1. 登录QQ邮箱网页版
2. 点击"设置" → "账户"
3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启"IMAP/SMTP服务"
5. 生成授权码（不是QQ密码）
6. 复制授权码到 `MAIL_PASSWORD`

#### 163邮箱配置示例

```python
MAIL_SERVER = "smtp.163.com"
MAIL_PORT = 465
MAIL_TLS = False
MAIL_SSL = True
```

#### Gmail配置示例

```python
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_TLS = True
MAIL_SSL = False
```

**注意：** Gmail需要开启"允许不够安全的应用访问"或使用应用专用密码。

### 步骤3：运行数据库迁移

添加预约提醒相关字段：

```bash
cd backend
python add_reminder_fields.py
```

### 步骤4：配置定时任务

#### Windows系统

**方法1：手动运行（测试）**
```bash
cd backend
run_reminder_task.bat
```

**方法2：Windows任务计划程序**
1. 打开"任务计划程序"（taskschd.msc）
2. 创建基本任务
3. 设置触发器：每10分钟运行一次
4. 操作：启动程序
   - 程序：`C:\path\to\backend\run_reminder_task.bat`
5. 完成

#### Linux系统

**方法1：手动运行（测试）**
```bash
cd /path/to/backend
python send_appointment_reminders.py
```

**方法2：使用crontab**
```bash
# 编辑crontab
crontab -e

# 添加以下行（每10分钟运行一次）
*/10 * * * * cd /path/to/backend && /usr/bin/python3 send_appointment_reminders.py >> /var/log/soulstation/reminders.log 2>&1
```

#### 使用Celery（推荐用于生产环境）

如果项目使用Celery，可以配置Celery Beat：

```python
# backend/app/celery_app.py
from celery import Celery
from celery.schedules import crontab

celery_app = Celery('soulstation')

@celery_app.task
def send_appointment_reminders():
    from send_appointment_reminders import check_and_send_reminders
    check_and_send_reminders()

# 配置定时任务
celery_app.conf.beat_schedule = {
    'send-appointment-reminders-every-10-minutes': {
        'task': 'send_appointment_reminders',
        'schedule': crontab(minute='*/10'),
    },
}
```

启动Celery Beat：
```bash
celery -A app.celery_app beat --loglevel=info
```

## 测试邮件功能

### 测试脚本

创建测试脚本 `backend/test_email.py`：

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email_service import EmailService

def test_send_email():
    """测试邮件发送"""
    try:
        # 测试基础邮件发送
        result = EmailService.send_email(
            to_email="your_test_email@example.com",
            subject="测试邮件",
            html_content="<h1>这是一封测试邮件</h1><p>如果收到此邮件，说明配置成功！</p>"
        )

        if result:
            print("✅ 邮件发送成功")
        else:
            print("❌ 邮件发送失败")

    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_send_email()
```

运行测试：
```bash
cd backend
python test_email.py
```

## 常见问题

### 1. 邮件发送失败

**问题：** 提示认证失败或连接超时

**解决方案：**
- 检查邮箱是否开启IMAP/SMTP服务
- 确认使用的是授权码而不是登录密码
- 检查SMTP服务器地址和端口是否正确
- 尝试切换TLS/SSL设置

### 2. 邮件进入垃圾箱

**问题：** 邮件成功发送但进入收件人垃圾箱

**解决方案：**
- 使用企业邮箱或域名邮箱
- 配置SPF、DKIM、DMARC记录
- 避免频繁发送相同内容
- 使用专业的邮件服务（如SendGrid、阿里云邮件推送）

### 3. 定时任务不执行

**问题：** 定时任务没有运行

**解决方案：**
- 检查定时任务配置是否正确
- 查看日志文件：`logs/appointment_reminders.log`
- 确认Python路径是否正确
- 检查数据库连接是否正常

## 邮件模板定制

所有邮件模板都在 `backend/app/services/email_service.py` 中。你可以根据需要修改：

### 修改邮件样式
编辑对应方法中的HTML `<style>` 部分

### 修改邮件内容
编辑HTML模板中的文字内容

### 添加新的邮件类型
在 `EmailService` 类中添加新方法，参考现有方法的结构。

## 监控和日志

### 查看日志

邮件发送日志位置：
- 邮件发送日志：查看应用日志
- 定时任务日志：`backend/logs/appointment_reminders.log`

### 监控指标

建议监控：
- 邮件发送成功率
- 邮件发送延迟
- 定时任务执行状态

## 安全建议

1. **不要在代码中硬编码邮箱密码**
   - 使用环境变量
   - 使用配置文件（.env）
   - 使用密钥管理服务

2. **环境变量配置**
   ```bash
   # .env 文件
   MAIL_USERNAME=your_email@qq.com
   MAIL_PASSWORD=your_authorization_code
   MAIL_FROM=your_email@qq.com
   ```

3. **限制邮件发送频率**
   - 添加限流机制
   - 防止被识别为垃圾邮件

## 生产环境部署建议

### 1. 使用专业邮件服务

推荐使用：
- **国内**：阿里云邮件推送、腾讯云邮件推送、SendCloud
- **国外**：SendGrid、Mailgun、AWS SES

### 2. 配置邮件队列

使用异步任务队列（如Celery）处理邮件发送：

```python
from celery import shared_task

@shared_task
def send_email_async(to_email, subject, html_content):
    EmailService.send_email(to_email, subject, html_content)

# 调用
send_email_async.delay(email, subject, content)
```

### 3. 错误处理和重试

```python
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def send_email_with_retry(to_email, subject, html_content):
    return EmailService.send_email(to_email, subject, html_content)
```

### 4. 监控和告警

- 邮件发送失败时发送告警
- 记录发送统计
- 定期检查邮件到达率

## 完成检查清单

- [ ] 配置邮箱服务器（config.py）
- [ ] 获取并配置邮箱授权码
- [ ] 运行数据库迁移（add_reminder_fields.py）
- [ ] 测试邮件发送（test_email.py）
- [ ] 配置定时任务
- [ ] 验证预约邮件正常发送
- [ ] 验证审核邮件正常发送
- [ ] 配置生产环境邮件服务

## 技术支持

如遇到问题，请检查：
1. 应用日志
2. 定时任务日志
3. 邮箱服务商文档
4. 防火墙和网络设置

---

**最后更新：** 2026-03-16
**版本：** 1.0.0
