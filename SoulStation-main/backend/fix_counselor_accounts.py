#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复咨询师账号：设置密码并建立关联
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor
from app.core.security import get_password_hash

def fix_counselor_accounts():
    """修复咨询师账号"""
    db = SessionLocal()

    try:
        # 咨询师账号映射 - 使用新邮箱避免冲突
        counselor_accounts = [
            {
                "email": "wangfang@example.com",
                "password": "123456",
                "nickname": "王芳",
                "counselor_name": "王芳",
                "old_email": "counselor1@example.com"
            },
            {
                "email": "liming@example.com",
                "password": "123456",
                "nickname": "李明",
                "counselor_name": "李明",
                "old_email": "counselor2@example.com"
            },
            {
                "email": "zhangjing@example.com",
                "password": "123456",
                "nickname": "张静",
                "counselor_name": "张静",
                "old_email": "counselor3@example.com"
            },
            {
                "email": "chengang@example.com",
                "password": "123456",
                "nickname": "陈刚",
                "counselor_name": "陈刚",
                "old_email": "counselor4@example.com"
            },
            {
                "email": "liuxue@example.com",
                "password": "123456",
                "nickname": "刘雪",
                "counselor_name": "刘雪",
                "old_email": "counselor5@example.com"
            }
        ]

        for account_info in counselor_accounts:
            print(f"\n处理咨询师: {account_info['counselor_name']}")

            # 查找咨询师
            counselor = db.query(Counselor).filter(
                Counselor.name == account_info['counselor_name']
            ).first()

            if not counselor:
                print(f"  [跳过] 咨询师'{account_info['counselor_name']}'不存在")
                continue

            # 查找旧账号
            old_user = db.query(User).filter(
                User.email == account_info['old_email']
            ).first()

            if old_user:
                # 更新旧账号的邮箱
                old_user.email = account_info['email']
                old_user.password_hash = get_password_hash(account_info['password'])
                old_user.nickname = account_info['nickname']
                old_user.role = "counselor"
                old_user.status = "active"
                user = old_user
                print(f"  [更新] 用户账号: {account_info['email']}")
            else:
                # 创建新用户
                user = User(
                    email=account_info['email'],
                    password_hash=get_password_hash(account_info['password']),
                    nickname=account_info['nickname'],
                    role="counselor",
                    status="active"
                )
                db.add(user)
                db.flush()
                print(f"  [创建] 用户账号: {account_info['email']}")

            # 建立关联
            if counselor.user_id != user.id:
                counselor.user_id = user.id
                print(f"  [关联] 咨询师(ID:{counselor.id}) <-> 用户(ID:{user.id})")
            else:
                print(f"  [OK] 已关联")

        db.commit()

        print("\n[成功] 所有咨询师账号已修复！")
        print("\n咨询师登录账号列表：")
        print("-" * 50)
        for account_info in counselor_accounts:
            print(f"  {account_info['counselor_name']}:")
            print(f"    邮箱: {account_info['email']}")
            print(f"    密码: {account_info['password']}")
            print()

    except Exception as e:
        print(f"[错误] 修复失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_counselor_accounts()
