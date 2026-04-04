#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建咨询师用户账号并关联到咨询师
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor
from app.core.security import get_password_hash

def create_counselor_user():
    """创建咨询师用户账号并关联"""
    db = SessionLocal()

    try:
        # 检查是否已存在咨询师用户
        counselor_user = db.query(User).filter(User.email == "counselor@test.com").first()

        if not counselor_user:
            print("[创建] 咨询师用户账号...")
            counselor_user = User(
                email="counselor@test.com",
                password_hash=get_password_hash("123456"),
                nickname="王芳咨询师",
                phone="13900000001",
                role="counselor",
                status="active"
            )
            db.add(counselor_user)
            db.flush()
            print("[OK] 咨询师用户创建成功")
        else:
            print(f"[OK] 咨询师用户已存在: {counselor_user.nickname}")

        # 获取第一个咨询师（王芳）
        counselor = db.query(Counselor).filter(Counselor.name == "王芳").first()

        if not counselor:
            print("[ERROR] 咨询师'王芳'不存在，请先创建咨询师")
            return

        # 将咨询师账号与用户关联
        if counselor.user_id != counselor_user.id:
            counselor.user_id = counselor_user.id
            print(f"[OK] 已将咨询师'王芳'与用户账号关联")
        else:
            print(f"[OK] 咨询师'王芳'已与用户账号关联")

        db.commit()

        print("\n[成功] 咨询师账号创建完成！")
        print("\n登录信息：")
        print(f"  邮箱: counselor@test.com")
        print(f"  密码: 123456")
        print(f"  角色: counselor")
        print(f"  姓名: 王芳")

        # 统计该咨询师的订单
        from sqlalchemy import func
        status_counts = db.query(
            Counselor.name,
            func.count(Appointment.id).label('total')
        ).join(Appointment, Counselor.id == Appointment.counselor_id).filter(
            Counselor.id == counselor.id
        ).group_by(Counselor.name).first()

        if status_counts:
            print(f"\n该咨询师共有 {status_counts.total} 个订单")

    except Exception as e:
        print(f"[错误] 创建失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # 导入Appointment模型
    from app.models.counselor import Appointment
    create_counselor_user()
