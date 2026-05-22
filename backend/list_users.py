"""
查询用户账号列表
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User
from app.models.counselor import Counselor

def list_users():
    """查询所有用户账号"""

    with Session(engine) as db:
        print("=== 用户账号列表 ===\n")

        # 查询所有用户
        users = db.query(User).all()

        if not users:
            print("数据库中没有用户")
            return

        print(f"共找到 {len(users)} 个用户账号\n")

        # 表头
        print(f"{'ID':<5} {'邮箱':<25} {'昵称':<15} {'角色':<10} {'状态':<10} {'是否认证':<8}")
        print("-" * 90)

        # 用户列表
        for user in users:
            role = user.role or 'user'
            status = user.status or 'unknown'
            is_verified = 'Yes' if user.is_verified else 'No'
            is_deleted = ' (Deleted)' if user.is_deleted else ''

            print(f"{user.id:<5} {user.email:<25} {user.nickname or 'N/A':<15} {role:<10} {status:<10} {is_verified:<8}{is_deleted}")

        print("\n=== 角色统计 ===")

        # 按角色统计
        role_count = {}
        for user in users:
            role = user.role or 'user'
            role_count[role] = role_count.get(role, 0) + 1

        for role, count in role_count.items():
            print(f"{role}: {count} 个")

        print("\n=== 咨询师账号详情 ===")

        # 查询咨询师
        counselors = db.query(Counselor).all()
        if counselors:
            print(f"\n共找到 {len(counselors)} 个咨询师账号\n")

            print(f"{'ID':<5} {'姓名':<10} {'用户ID':<8} {'状态':<15} {'是否认证':<8}")
            print("-" * 60)

            for counselor in counselors:
                status = counselor.status or 'unknown'
                is_verified = 'Yes' if counselor.is_verified else 'No'
                is_deleted = ' (Deleted)' if counselor.is_deleted else ''

                print(f"{counselor.id:<5} {counselor.name:<10} {counselor.user_id or 'N/A':<8} {status:<15} {is_verified:<8}{is_deleted}")
        else:
            print("没有咨询师账号")

        print("\n=== 测试账号推荐 ===")

        # 推荐测试账号
        print("\n普通用户测试账号:")
        user_count = 0
        for user in users:
            if user.role == 'user' and not user.is_deleted:
                print(f"- 邮箱: {user.email}, 密码: password123")
                user_count += 1
                if user_count >= 3:
                    break

        print("\n咨询师测试账号:")
        counselor_count = 0
        for user in users:
            if user.role == 'counselor' and not user.is_deleted:
                # 查找对应的咨询师信息
                counselor = db.query(Counselor).filter(Counselor.user_id == user.id).first()
                if counselor:
                    print(f"- 姓名: {counselor.name}, 邮箱: {user.email}, 密码: password123")
                    counselor_count += 1
                    if counselor_count >= 5:
                        break

        print(f"\n总用户数: {len(users)}")
        print(f"总咨询师数: {len(counselors)}")
        print(f"活跃用户数: {len([u for u in users if not u.is_deleted])}")
        print(f"已认证用户数: {len([u for u in users if u.is_verified])}")

if __name__ == "__main__":
    list_users()