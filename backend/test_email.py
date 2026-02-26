"""
测试邮件发送功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.email_service import EmailService
from app.services.verification_service import VerificationCodeService
from app.services.auth_service import AuthService


def test_send_verification_code():
    """测试发送验证码"""
    print("=" * 60)
    print("测试发送验证码功能")
    print("=" * 60)

    # 测试邮箱
    test_email = input("\n请输入接收验证码的邮箱地址: ").strip()

    if not test_email:
        print("使用默认测试邮箱: 1748618129@qq.com")
        test_email = "1748618129@qq.com"

    print(f"\n发送验证码到: {test_email}")

    success, message, remaining = AuthService.send_verification_code(test_email)

    if success:
        print(f"\n✓ {message}")
        print(f"验证码有效期: 5分钟")

        # 获取剩余时间
        remaining_time = VerificationCodeService.get_remaining_time(test_email)
        if remaining_time:
            print(f"剩余时间: {remaining_time} 秒")

    else:
        print(f"\n✗ {message}")
        if remaining > 0:
            print(f"请等待 {remaining} 秒后再试")


def test_verify_code():
    """测试验证验证码"""
    print("\n" + "=" * 60)
    print("测试验证验证码功能")
    print("=" * 60)

    test_email = input("\n请输入邮箱地址: ").strip()
    code = input("请输入验证码: ").strip()

    if AuthService.verify_code(test_email, code):
        print("\n✓ 验证码正确!")
    else:
        print("\n✗ 验证码错误或已过期")


def test_send_welcome_email():
    """测试发送欢迎邮件"""
    print("\n" + "=" * 60)
    print("测试发送欢迎邮件")
    print("=" * 60)

    test_email = input("\n请输入接收邮件的邮箱地址: ").strip()

    if not test_email:
        print("使用默认测试邮箱: 1748618129@qq.com")
        test_email = "1748618129@qq.com"

    nickname = test_email.split('@')[0]

    print(f"\n发送欢迎邮件到: {test_email}")

    try:
        EmailService.send_welcome_email(test_email, nickname)
        print("\n✓ 欢迎邮件发送成功!")
    except Exception as e:
        print(f"\n✗ 发送失败: {e}")


def check_remaining_time():
    """检查验证码剩余时间"""
    print("\n" + "=" * 60)
    print("检查验证码剩余时间")
    print("=" * 60)

    test_email = input("\n请输入邮箱地址: ").strip()

    remaining = VerificationCodeService.get_remaining_time(test_email)
    if remaining is not None:
        print(f"\n验证码剩余时间: {remaining} 秒")
    else:
        print("\n该邮箱没有有效的验证码")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SoulStation 邮件服务测试")
    print("=" * 60)
    print("\n确保 .env 文件中已正确配置邮件服务")
    print("\n当前配置:")
    from app.core.config import settings
    print(f"  SMTP服务器: {settings.MAIL_SERVER}")
    print(f"  SMTP端口: {settings.MAIL_PORT}")
    print(f"  发件邮箱: {settings.MAIL_FROM}")
    print(f"  发件人: {settings.MAIL_FROM_NAME}")

    while True:
        print("\n" + "=" * 60)
        print("请选择测试项目:")
        print("1. 发送验证码")
        print("2. 验证验证码")
        print("3. 发送欢迎邮件")
        print("4. 检查验证码剩余时间")
        print("0. 退出")
        print("=" * 60)

        choice = input("\n请输入选项 (0-4): ").strip()

        if choice == "1":
            test_send_verification_code()
        elif choice == "2":
            test_verify_code()
        elif choice == "3":
            test_send_welcome_email()
        elif choice == "4":
            check_remaining_time()
        elif choice == "0":
            print("\n退出测试")
            break
        else:
            print("\n无效的选项")
