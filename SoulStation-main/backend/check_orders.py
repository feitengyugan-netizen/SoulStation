#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查订单和咨询师数据
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, Counselor
from app.models.user import User

def check_data():
    """检查数据关联"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("检查订单和咨询师数据")
        print("=" * 70)

        # 1. 查看所有订单
        print("\n[1] 所有订单：")
        print("-" * 70)
        appointments = db.query(Appointment).all()
        print(f"共 {len(appointments)} 个订单\n")

        for appt in appointments:
            print(f"订单ID: {appt.id}")
            print(f"  订单号: {appt.appointment_no}")
            print(f"  咨询师ID: {appt.counselor_id}")
            print(f"  用户ID: {appt.user_id}")
            print(f"  状态: {appt.status}")
            print(f"  创建时间: {appt.created_at}")
            print()

        # 2. 查看所有咨询师
        print("\n[2] 所有咨询师：")
        print("-" * 70)
        counselors = db.query(Counselor).all()
        print(f"共 {len(counselors)} 位咨询师\n")

        for counselor in counselors:
            # 查找关联的用户
            user = None
            if counselor.user_id:
                user = db.query(User).filter(User.id == counselor.user_id).first()

            print(f"咨询师ID: {counselor.id}")
            print(f"  姓名: {counselor.name}")
            print(f"  关联用户ID: {counselor.user_id}")
            if user:
                print(f"  关联用户邮箱: {user.email}")
                print(f"  关联用户昵称: {user.nickname}")
                print(f"  关联用户角色: {user.role}")
            else:
                print(f"  关联用户: 无")
            print()

        # 3. 检查王芳的订单
        print("\n[3] 王芳的订单：")
        print("-" * 70)
        wangfang = db.query(Counselor).filter(Counselor.name == "王芳").first()

        if wangfang:
            print(f"王芳咨询师ID: {wangfang.id}")
            print(f"王芳user_id: {wangfang.user_id}")

            wangfang_orders = db.query(Appointment).filter(
                Appointment.counselor_id == wangfang.id
            ).all()

            print(f"王芳的订单数: {len(wangfang_orders)}")

            if len(wangfang_orders) > 0:
                print("\n订单列表：")
                for order in wangfang_orders:
                    print(f"  - {order.appointment_no} | {order.status} | {order.created_at}")
            else:
                print("  (无订单)")
        else:
            print("未找到王芳咨询师")

        # 4. 检查登录用户
        print("\n[4] 咨询师用户账号：")
        print("-" * 70)
        counselor_users = db.query(User).filter(User.role == "counselor").all()

        print(f"共 {len(counselor_users)} 个咨询师用户\n")

        for user in counselor_users:
            # 查找关联的咨询师记录
            counselor = db.query(Counselor).filter(Counselor.user_id == user.id).first()

            print(f"用户ID: {user.id}")
            print(f"  邮箱: {user.email}")
            print(f"  昵称: {user.nickname}")
            print(f"  关联咨询师ID: {counselor.id if counselor else '无'}")
            print(f"  关联咨询师姓名: {counselor.name if counselor else '无'}")
            print()

        # 5. 测试：查询王芳账号（wangfang@example.com）能看到的订单
        print("\n[5] 测试：王芳账号登录后能看到的订单")
        print("-" * 70)
        wangfang_user = db.query(User).filter(User.email == "wangfang@example.com").first()

        if wangfang_user:
            print(f"登录用户: {wangfang_user.email}")
            print(f"用户ID: {wangfang_user.id}")

            # 查找该用户关联的咨询师记录
            counselor = db.query(Counselor).filter(Counselor.user_id == wangfang_user.id).first()

            if counselor:
                print(f"关联咨询师: {counselor.name} (ID: {counselor.id})")

                # 查询该咨询师的订单
                counselor_orders = db.query(Appointment).filter(
                    Appointment.counselor_id == counselor.id
                ).all()

                print(f"可查看的订单数: {len(counselor_orders)}")

                if len(counselor_orders) > 0:
                    print("\n订单列表：")
                    for order in counselor_orders:
                        print(f"  - {order.appointment_no} | {order.status}")
                else:
                    print("  (无订单)")
            else:
                print("错误：该用户未关联任何咨询师记录")
        else:
            print("错误：未找到wangfang@example.com用户")

    except Exception as e:
        print(f"\n[错误] 检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
