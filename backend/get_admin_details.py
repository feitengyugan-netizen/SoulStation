"""
查询管理员账户详细信息
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def get_admin_details():
    """查询管理员账户详情"""
    with engine.connect() as conn:
        print("=== 管理员账户详细信息 ===\n")

        # 查询所有管理员
        admins = conn.execute(text("""
            SELECT id, username, email, role, created_at
            FROM admins
        """)).fetchall()

        if admins:
            for admin in admins:
                print(f"管理员ID: {admin[0]}")
                print(f"用户名: {admin[1]}")
                print(f"邮箱: {admin[2]}")
                print(f"角色: {admin[3]}")
                print(f"创建时间: {admin[4]}")
                print()
        else:
            print("没有找到管理员账户")

        # 检查是否有管理员角色的用户账户
        print("=== 检查用户表中的管理员 ===")
        admin_users = conn.execute(text("""
            SELECT id, email, nickname, role, status
            FROM users
            WHERE role = 'admin' AND is_deleted = 0
        """)).fetchall()

        if admin_users:
            for user in admin_users:
                print(f"用户ID: {user[0]}")
                print(f"邮箱: {user[1]}")
                print(f"昵称: {user[2]}")
                print(f"角色: {user[3]}")
                print(f"状态: {user[4]}")
                print()
        else:
            print("用户表中没有管理员角色的账户")

        print("=== 查询完成 ===")

if __name__ == "__main__":
    get_admin_details()
