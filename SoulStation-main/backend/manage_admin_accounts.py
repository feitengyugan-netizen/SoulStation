#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
管理员账号管理
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.admin import Admin
from app.core.security import get_password_hash

def list_admins():
    """列出所有管理员"""
    db = SessionLocal()
    try:
        admins = db.query(Admin).filter(Admin.deleted_at.is_(None)).all()

        print("=" * 70)
        print("当前管理员账号列表")
        print("=" * 70)

        if not admins:
            print("没有找到管理员账号")
        else:
            for admin in admins:
                status = "激活" if admin.is_active else "禁用"
                print(f"\nID={admin.id}: {admin.username}")
                print(f"  真实姓名: {admin.real_name or '未设置'}")
                print(f"  邮箱: {admin.email or '未设置'}")
                print(f"  角色: {admin.role}")
                print(f"  状态: {status}")
                print(f"  创建时间: {admin.created_at}")
                print(f"  最后登录: {admin.last_login_at or '从未登录'}")

    finally:
        db.close()

def create_admin(username, password, real_name="", email="", role="admin"):
    """创建新管理员"""
    db = SessionLocal()
    try:
        # 检查用户名是否已存在
        existing = db.query(Admin).filter(
            Admin.username == username,
            Admin.deleted_at.is_(None)
        ).first()

        if existing:
            print(f"[错误] 用户名 '{username}' 已存在")
            return False

        # 创建管理员
        admin = Admin(
            username=username,
            password_hash=get_password_hash(password),
            real_name=real_name,
            email=email,
            role=role,
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("[成功] 管理员账号创建成功！")
        print(f"  用户名: {username}")
        print(f"  密码: {password}")
        print(f"  真实姓名: {real_name or '未设置'}")
        print(f"  角色: {role}")

        return True

    except Exception as e:
        print(f"[错误] 创建失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="管理员账号管理")
    parser.add_argument("--list", action="store_true", help="列出所有管理员")
    parser.add_argument("--create", action="store_true", help="创建新管理员")
    parser.add_argument("--username", help="用户名")
    parser.add_argument("--password", help="密码", default="123456")
    parser.add_argument("--real-name", help="真实姓名")
    parser.add_argument("--email", help="邮箱")
    parser.add_argument("--role", help="角色", default="admin",
                       choices=["super_admin", "admin", "editor"])

    args = parser.parse_args()

    if args.list:
        list_admins()
    elif args.create:
        if not args.username:
            print("[错误] 请提供用户名 --username")
        else:
            create_admin(
                username=args.username,
                password=args.password,
                real_name=args.real_name or "",
                email=args.email or "",
                role=args.role
            )
    else:
        # 默认列出所有管理员
        list_admins()

        # 如果没有管理员，提示创建
        db = SessionLocal()
        count = db.query(Admin).filter(Admin.deleted_at.is_(None)).count()
        db.close()

        if count == 0:
            print("\n[提示] 系统中没有管理员账号")
            print("创建示例：")
            print("  python manage_admin_accounts.py --create --username admin --password admin123 --real-name 系统管理员 --role super_admin")
