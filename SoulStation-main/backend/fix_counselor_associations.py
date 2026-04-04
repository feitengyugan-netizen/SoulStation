#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复咨询师账号关联：为每个咨询师创建独立的用户账号
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Counselor
from app.models.user import User
from app.core.security import get_password_hash

def fix_counselor_associations():
    """修复咨询师账号关联"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("修复咨询师账号关联")
        print("=" * 70)

        # 咨询师账号配置
        counselor_config = [
            {
                "counselor_id": 1,
                "counselor_name": "胡医生",
                "email": "huyisheng@example.com",
                "password": "123456",
                "nickname": "胡医生"
            },
            {
                "counselor_id": 2,
                "counselor_name": "王芳",
                "email": "wangfang@example.com",
                "password": "123456",
                "nickname": "王芳"
            },
            {
                "counselor_id": 3,
                "counselor_name": "李明",
                "email": "liming@example.com",
                "password": "123456",
                "nickname": "李明"
            },
            {
                "counselor_id": 4,
                "counselor_name": "张静",
                "email": "zhangjing@example.com",
                "password": "123456",
                "nickname": "张静"
            },
            {
                "counselor_id": 5,
                "counselor_name": "陈刚",
                "email": "chengang@example.com",
                "password": "123456",
                "nickname": "陈刚"
            },
            {
                "counselor_id": 6,
                "counselor_name": "刘雪",
                "email": "liuxue@example.com",
                "password": "123456",
                "nickname": "刘雪"
            }
        ]

        for config in counselor_config:
            print(f"\n处理咨询师: {config['counselor_name']} (ID={config['counselor_id']})")

            # 查找咨询师
            counselor = db.query(Counselor).filter(
                Counselor.id == config["counselor_id"]
            ).first()

            if not counselor:
                print(f"  [跳过] 咨询师不存在")
                continue

            # 查找或创建用户
            user = db.query(User).filter(User.email == config["email"]).first()

            if user:
                # 更新现有用户
                user.password_hash = get_password_hash(config["password"])
                user.nickname = config["nickname"]
                user.role = "counselor"
                user.status = "active"
                print(f"  [更新] 用户账号: {user.email}")
            else:
                # 创建新用户
                user = User(
                    email=config["email"],
                    password_hash=get_password_hash(config["password"]),
                    nickname=config["nickname"],
                    role="counselor",
                    status="active"
                )
                db.add(user)
                db.flush()
                print(f"  [创建] 用户账号: {user.email} (ID={user.id})")

            # 更新咨询师的user_id关联
            if counselor.user_id != user.id:
                old_user_id = counselor.user_id
                counselor.user_id = user.id
                print(f"  [关联] 咨询师(ID={counselor.id}) -> 用户(ID={user.id})")
                if old_user_id and old_user_id != user.id:
                    print(f"  [修改] 旧的user_id={old_user_id} -> 新的user_id={user.id}")
            else:
                print(f"  [OK] 已正确关联到用户(ID={user.id})")

        db.commit()

        # 验证结果
        print("\n" + "=" * 70)
        print("[验证] 检查修复结果")
        print("=" * 70)

        for config in counselor_config:
            counselor = db.query(Counselor).filter(
                Counselor.id == config["counselor_id"]
            ).first()

            if counselor and counselor.user_id:
                user = db.query(User).filter(User.id == counselor.user_id).first()
                if user:
                    print(f"{counselor.name} -> {user.email} (ID={user.id})")
                else:
                    print(f"{counselor.name} -> 用户不存在 (user_id={counselor.user_id})")

        print("\n[成功] 咨询师账号关联修复完成！")
        print("\n咨询师登录账号列表：")
        print("-" * 70)
        for config in counselor_config:
            print(f"  {config['counselor_name']}:")
            print(f"    邮箱: {config['email']}")
            print(f"    密码: {config['password']}")
            print()

    except Exception as e:
        print(f"\n[错误] 修复失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    fix_counselor_associations()
