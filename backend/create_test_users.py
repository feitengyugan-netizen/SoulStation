"""
创建额外的测试用户账号
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_test_users():
    """创建多个测试用户"""
    db = SessionLocal()

    test_users = [
        {
            "email": "user1@example.com",
            "password": "123456",
            "nickname": "张三",
            "role": "user",
            "bio": "这是一个测试用户账号"
        },
        {
            "email": "user2@example.com",
            "password": "123456",
            "nickname": "李四",
            "role": "user",
            "bio": "第二个测试用户"
        },
        {
            "email": "user3@example.com",
            "password": "123456",
            "nickname": "王五",
            "role": "user",
            "bio": "第三个测试用户"
        },
        {
            "email": "anxiety@test.com",
            "password": "123456",
            "nickname": "小明同学",
            "role": "user",
            "bio": "我最近感到很焦虑"
        },
        {
            "email": "depression@test.com",
            "password": "123456",
            "nickname": "小红同学",
            "role": "user",
            "bio": "希望得到心理帮助"
        }
    ]

    print('\n' + '='*70)
    print('              创建测试用户账号')
    print('='*70)

    try:
        for user_data in test_users:
            # 检查是否已存在
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f'\n✓ 用户 {user_data["email"]} 已存在，跳过')
                continue

            # 创建新用户
            new_user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                nickname=user_data["nickname"],
                role=user_data["role"],
                bio=user_data.get("bio", ""),
                is_active=True,
                status="active"
            )
            db.add(new_user)
            db.commit()

            print(f'\n✓ 成功创建用户: {user_data["email"]}')
            print(f'  昵称: {user_data["nickname"]}')
            print(f'  密码: {user_data["password"]}')

        print('\n' + '='*70)
        print('              测试用户创建完成！')
        print('='*70)

        return True

    except Exception as e:
        print(f'\n✗ 创建失败: {e}')
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    create_test_users()
