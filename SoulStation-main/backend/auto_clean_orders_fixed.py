#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动清理test@example.com用户的所有订单（先删除评价）
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, ConsultationReview

def auto_clean_orders():
    """自动清理test用户的所有订单"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("自动清理test@example.com用户的所有订单")
        print("=" * 70)

        # 1. 查询test@example.com用户的所有订单
        print("\n[查询] 获取test@example.com用户的所有订单...")
        test_orders = db.query(Appointment).filter(
            Appointment.user_id == 10  # test@example.com的user_id是10
        ).all()

        print(f"[结果] 找到 {len(test_orders)} 个订单")

        if len(test_orders) == 0:
            print("[提示] 没有订单需要清理")
            return

        # 2. 显示订单列表
        print("\n订单列表：")
        print("-" * 70)
        for i, appt in enumerate(test_orders, 1):
            print(f"{i:2}. {appt.appointment_no} | {appt.status:10} | "
                  f"{appt.created_at.strftime('%Y-%m-%d %H:%M')}")

        # 3. 先删除关联的评价记录
        print(f"\n[步骤1] 删除关联的评价记录...")
        appointment_ids = [appt.id for appt in test_orders]
        reviews = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id.in_(appointment_ids)
        ).all()

        print(f"  找到 {len(reviews)} 条评价记录")
        for review in reviews:
            db.delete(review)

        print(f"  已删除 {len(reviews)} 条评价记录")

        # 4. 再删除订单
        print(f"\n[步骤2] 删除订单...")
        for i, appt in enumerate(test_orders, 1):
            db.delete(appt)
            if i % 5 == 0:
                print(f"  已删除 {i}/{len(test_orders)}...")

        db.commit()

        print(f"\n[成功] 已删除 {len(test_orders)} 个订单及其评价")

        # 5. 显示剩余订单
        remaining = db.query(Appointment).count()
        print(f"[剩余] 数据库中还有 {remaining} 个订单")

        # 6. 显示各用户的订单统计
        print("\n[统计] 各用户订单数量：")
        from sqlalchemy import func
        user_counts = db.query(
            Appointment.user_id,
            Appointment.user_name,
            func.count(Appointment.id)
        ).group_by(Appointment.user_id, Appointment.user_name).all()

        if user_counts:
            for user_id, user_name, count in user_counts:
                print(f"  用户ID={user_id} | {user_name or 'None':15} | {count}个订单")
        else:
            print("  (无订单)")

        print("\n" + "=" * 70)
        print("[完成] 清理操作已完成，test@example.com用户的所有订单已删除")
        print("=" * 70)

    except Exception as e:
        print(f"\n[错误] 清理失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    auto_clean_orders()
