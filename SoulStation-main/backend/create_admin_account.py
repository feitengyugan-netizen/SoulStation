#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建管理员账号
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.admin import Admin
from app.core.security import get_password_hash
from datetime import datetime

def create_admin_account():
    """创建管理员账号"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("创建管理员账号")
        print("=" * 70)

        # 检查是否已存在管理员
        existing_admin = db.query(Admin).filter(
            Admin.username == "admin",
            Admin.deleted_at.is_(None)
        ).first()

        if existing_admin:
            print("[提示] 管理员账号已存在")
            print(f"  用户名: {existing_admin.username}")
            print(f"  真实姓名: {existing_admin.real_name or '未设置'}")
            print(f"  角色: {existing_admin.role}")
            print(f"  状态: {'激活' if existing_admin.is_active else '禁用'}")

            # 更新密码
            print("\n是否要更新密码？(y/n): ", end='')
            # 自动选择不更新
            print("n")
            return

        # 创建管理员
        admin = Admin(
            username="admin",
            password_hash=get_password_hash("admin123"),
            real_name="系统管理员",
            email="admin@soulstation.com",
            role="super_admin",
            is_active=True
        )

        db.add(admin)
        db.commit()

        print("[成功] 管理员账号创建成功！")
        print("\n登录信息：")
        print("-" * 70)
        print("  用户名: admin")
        print("  密码: admin123")
        print("  角色: 超级管理员")
        print("\n登录地址：")
        print("  后台地址: http://localhost:3003/admin")
        print("  API地址: http://localhost:8000/api/admin")

        print("\n" + "=" * 70)
        print("[提示] 请在生产环境中修改默认密码！")
        print("=" * 70)

    except Exception as e:
        print(f"\n[错误] 创建失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_account()
