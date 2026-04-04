"""
更新测试用户的角色为咨询师
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User


def update_counselor_role():
    """更新测试用户的角色为咨询师"""
    db = SessionLocal()
    try:
        # 查找测试用户
        test_user = db.query(User).filter(User.email == "test@example.com").first()

        if not test_user:
            print("❌ 未找到测试用户 test@example.com")
            return False

        print(f"当前用户信息:")
        print(f"  邮箱: {test_user.email}")
        print(f"  昵称: {test_user.nickname}")
        print(f"  当前角色: {test_user.role}")

        # 更新角色为咨询师
        test_user.role = "counselor"
        db.commit()

        print(f"\n✅ 用户角色已更新为: {test_user.role}")
        print("\n现在可以使用以下账号登录咨询师工作台:")
        print("  邮箱: test@example.com")
        print("  密码: 123456")
        print("  登录入口: http://localhost:5173/login")

        return True

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("更新测试用户角色为咨询师")
    print("="*60)
    update_counselor_role()
