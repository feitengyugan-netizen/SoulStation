#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理测试订单数据
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment
from datetime import datetime, timedelta

def clean_test_orders():
    """清理测试订单"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("清理测试订单数据")
        print("=" * 70)

        # 1. 查询所有订单
        print("\n[查询] 获取所有订单...")
        all_appointments = db.query(Appointment).order_by(Appointment.created_at.desc()).all()

        print(f"[结果] 共有 {len(all_appointments)} 个订单")

        if len(all_appointments) == 0:
            print("[提示] 没有订单需要清理")
            return

        # 2. 显示订单列表
        print("\n订单列表（最近20个）：")
        print("-" * 70)
        for i, appt in enumerate(all_appointments[:20], 1):
            print(f"{i:2}. ID={appt.id:3} | {appt.appointment_no} | "
                  f"{appt.created_at.strftime('%Y-%m-%d %H:%M')} | "
                  f"状态={appt.status:10} | 用户={appt.user_name}")

        # 3. 选择清理方式
        print("\n" + "=" * 70)
        print("清理选项：")
        print("  1. 删除所有订单")
        print("  2. 只删除test@example.com用户的订单")
        print("  3. 只删除已完成/已取消的订单")
        print("  4. 只删除最近7天的测试订单")
        print("  0. 取消")
        print("=" * 70)

        choice = input("\n请选择清理方式 (0-4): ").strip()

        if choice == "0":
            print("[取消] 不进行清理")
            return

        # 4. 执行清理
        orders_to_delete = []

        if choice == "1":
            # 删除所有订单
            orders_to_delete = all_appointments

        elif choice == "2":
            # 只删除test@example.com用户的订单
            orders_to_delete = db.query(Appointment).filter(
                Appointment.user_id == 10  # test@example.com的user_id是10
            ).all()

        elif choice == "3":
            # 只删除已完成/已取消的订单
            orders_to_delete = db.query(Appointment).filter(
                Appointment.status.in_(['completed', 'cancelled', 'refunded'])
            ).all()

        elif choice == "4":
            # 只删除最近7天的订单
            seven_days_ago = datetime.now() - timedelta(days=7)
            orders_to_delete = db.query(Appointment).filter(
                Appointment.created_at >= seven_days_ago
            ).all()

        else:
            print("[错误] 无效的选择")
            return

        # 5. 显示将要删除的订单
        print(f"\n[确认] 将要删除 {len(orders_to_delete)} 个订单")
        if len(orders_to_delete) > 0:
            print("前10个订单：")
            for i, appt in enumerate(orders_to_delete[:10], 1):
                print(f"  {i}. {appt.appointment_no} | {appt.status} | {appt.user_name}")

        confirm = input("\n确认删除？(yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("[取消] 已取消删除操作")
            return

        # 6. 执行删除
        print("\n[删除] 正在删除订单...")
        for i, appt in enumerate(orders_to_delete, 1):
            db.delete(appt)
            if i % 10 == 0:
                print(f"  已删除 {i}/{len(orders_to_delete)}...")

        db.commit()

        print(f"\n[成功] 已删除 {len(orders_to_delete)} 个订单")

        # 7. 显示剩余订单
        remaining = db.query(Appointment).count()
        print(f"[剩余] 数据库中还有 {remaining} 个订单")

        print("\n" + "=" * 70)
        print("[完成] 清理操作已完成")
        print("=" * 70)

    except Exception as e:
        print(f"\n[错误] 清理失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    clean_test_orders()
