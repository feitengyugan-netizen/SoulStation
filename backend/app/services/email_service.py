"""
邮件服务
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """邮件服务类"""

    @staticmethod
    def create_smtp_connection():
        """创建SMTP连接"""
        try:
            if settings.MAIL_TLS:
                server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)
                server.starttls()
            elif settings.MAIL_SSL:
                server = smtplib.SMTP_SSL(settings.MAIL_SERVER, settings.MAIL_PORT)
            else:
                server = smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT)

            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            return server
        except Exception as e:
            logger.error(f"创建SMTP连接失败: {e}")
            raise

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: 邮件内容（HTML格式）

        Returns:
            bool: 是否发送成功
        """
        try:
            # 创建邮件对象
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
            message["To"] = to_email

            # 添加HTML内容
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # 发送邮件
            with EmailService.create_smtp_connection() as server:
                server.sendmail(settings.MAIL_FROM, to_email, message.as_string())

            logger.info(f"邮件发送成功: {to_email}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            raise

    @staticmethod
    def send_verification_code(email: str, code: str) -> bool:
        """
        发送验证码邮件

        Args:
            email: 收件人邮箱
            code: 验证码

        Returns:
            bool: 是否发送成功
        """
        subject = "【SoulStation】邮箱验证码"

        # 邮件HTML内容
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    text-align: center;
                    padding: 20px;
                    background-color: #f0f0f0;
                    border-radius: 8px;
                    margin: 20px 0;
                    letter-spacing: 5px;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
                .warning {{
                    color: #e74c3c;
                    font-size: 14px;
                    margin-top: 15px;
                    padding: 10px;
                    background-color: #fee;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🧠 SoulStation 心理咨询平台</div>
                </div>
                <div class="content">
                    <h2>邮箱验证码</h2>
                    <p>您好！</p>
                    <p>您正在进行邮箱验证，验证码如下：</p>
                    <div class="code">{code}</div>
                    <p><strong>有效期：5分钟</strong></p>
                    <div class="warning">
                        ⚠️ 请勿将验证码告知他人，以确保您的账户安全。
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)

    @staticmethod
    def send_welcome_email(email: str, nickname: str) -> bool:
        """
        发送欢迎邮件

        Args:
            email: 收件人邮箱
            nickname: 用户昵称

        Returns:
            bool: 是否发送成功
        """
        subject = "欢迎加入 SoulStation 心理咨询平台"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .container {{
                    background-color: #f9f9f9;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #667eea;
                }}
                .content {{
                    background-color: #fff;
                    padding: 30px;
                    border-radius: 8px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🧠 SoulStation</div>
                </div>
                <div class="content">
                    <h2>欢迎加入！</h2>
                    <p>亲爱的 <strong>{nickname}</strong>：</p>
                    <p>欢迎您注册 SoulStation 心理咨询平台！</p>
                    <p>我们致力于为您提供专业的心理咨询服务，帮助您解决心理困扰，提升心理健康水平。</p>
                    <p>在平台上，您可以：</p>
                    <ul>
                        <li>🧠 进行专业心理测试</li>
                        <li>💬 与智能AI助手对话</li>
                        <li>👨‍⚕️ 预约专业咨询师</li>
                        <li>📚 阅读心理知识文章</li>
                    </ul>
                    <div style="text-align: center;">
                        <a href="{settings.FRONTEND_URL}" class="button">立即开始</a>
                    </div>
                </div>
                <div class="footer">
                    <p>此邮件由系统自动发送，请勿回复</p>
                    <p>© 2026 SoulStation. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(email, subject, html_content)
