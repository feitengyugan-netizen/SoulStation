# -*- coding: utf-8 -*-
"""
检查咨询师账号的角色是否正确
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor

def main():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("检查咨询师账号角色")
        print("=" * 80)

        # 查询所有角色为counselor的用户
        counselor_users = db.query(User).filter(User.role == 'counselor').all()

        print(f"\n找到 {len(counselor_users)} 个角色为 counselor 的用户:\n")
        print("-" * 80)
        for user in counselor_users:
            print(f"ID: {user.id}")
            print(f"  邮箱: {user.email}")
            print(f"  昵称: {user.nickname}")
            print(f"  角色: {user.role}")
            print(f"  状态: {user.status}")

            # 查找关联的咨询师档案
            counselor = db.query(Counselor).filter(Counselor.user_id == user.id).first()
            if counselor:
                print(f"  关联档案: {counselor.name} (ID: {counselor.id})")
            else:
                print(f"  关联档案: 未找到!")
            print()

        # 验证特定账号
        test_emails = [
            "counselor1@soulstation.com",
            "counselor2@soulstation.com",
            "counselor3@soulstation.com",
            "counselor4@soulstation.com",
            "counselor5@soulstation.com",
            "counselor6@soulstation.com"
        ]

        print("\n验证特定账号:")
        print("-" * 80)
        for email in test_emails:
            user = db.query(User).filter(User.email == email).first()
            if user:
                print(f"{email:40s} | 角色: {user.role:10s} | 状态: {user.status}")
            else:
                print(f"{email:40s} | 不存在!")
        print("-" * 80)

        print(f"\n总计: {len(counselor_users)} 个咨询师账号")

    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
