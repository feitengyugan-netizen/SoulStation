"""
获取可用账户列表（简化版）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def get_available_accounts():
    """获取可用账户"""
    with engine.connect() as conn:
        print("=== 可用账户列表 ===\n")

        # 查询用户账户
        print("=== 用户账户 (前5个) ===")
        users = conn.execute(text("""
            SELECT id, email, nickname, role, status
            FROM users
            WHERE is_deleted = 0
            LIMIT 5
        """)).fetchall()

        if users:
            for user in users:
                print(f"   ID: {user[0]}")
                print(f"   邮箱: {user[1]}")
                print(f"   昵称: {user[2]}")
                print(f"   角色: {user[3]}")
                print(f"   状态: {user[4]}")
                print(f"   密码: 123456 (默认密码)")
                print()
        else:
            print("   暂无用户账户")

        # 查询咨询师账户
        print("=== 咨询师账户 ===")
        counselors = conn.execute(text("""
            SELECT c.id, c.name, c.title, c.specialty,
                   c.experience_years, c.consultation_fee,
                   u.email, c.is_verified
            FROM counselors c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.is_deleted = 0
            ORDER BY c.id
            LIMIT 5
        """)).fetchall()

        if counselors:
            for counselor in counselors:
                print(f"   ID: {counselor[0]}")
                print(f"   姓名: {counselor[1]}")
                print(f"   职称: {counselor[2]}")
                print(f"   专长: {counselor[3]}")
                print(f"   经验年限: {counselor[4]}年")
                print(f"   咨询费用: {counselor[5]}元/次")
                print(f"   关联邮箱: {counselor[6]}")
                print(f"   认证状态: {'已认证' if counselor[7] else '未认证'}")
                print(f"   密码: 123456 (默认密码)")
                print()
        else:
            print("   暂无咨询师账户")

        # 查询管理员账户
        print("=== 管理员账户 ===")
        admins = conn.execute(text("""
            SELECT id, username, email, role
            FROM admins
            LIMIT 5
        """)).fetchall()

        if admins:
            for admin in admins:
                print(f"   ID: {admin[0]}")
                print(f"   用户名: {admin[1]}")
                print(f"   邮箱: {admin[2]}")
                print(f"   角色: {admin[3]}")
                print(f"   密码: admin123 (默认密码)")
                print()
        else:
            print("   暂无管理员账户")

        # 统计信息
        print("=== 账户统计 ===")
        stats = conn.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM users WHERE is_deleted = 0) as user_count,
                (SELECT COUNT(*) FROM counselors WHERE is_deleted = 0) as counselor_count,
                (SELECT COUNT(*) FROM admins) as admin_count
        """)).fetchone()

        print(f"   用户总数: {stats[0]}")
        print(f"   咨询师总数: {stats[1]}")
        print(f"   管理员总数: {stats[2]}")

        print("\n=== 默认登录信息 ===")
        print("用户账户: 邮箱 + 密码(123456)")
        print("咨询师账户: 邮箱 + 密码(123456)")
        print("管理员账户: 用户名 + 密码(admin123)")
        print("=== 账户列表完成 ===")

if __name__ == "__main__":
    get_available_accounts()
