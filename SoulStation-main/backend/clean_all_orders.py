#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整清理test@example.com用户的所有订单及关联数据
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, ConsultationReview, ConsultationMessage

def auto_clean_orders():
    """完整清理test用户的所有订单"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("完整清理test@example.com用户的所有订单")
        print("=" * 70)

        # 1. 查询test@example.com用户的所有订单
        print("\n[查询] 获取test@example.com用户的所有订单...")
        test_orders = db.query(Appointment).filter(
            Appointment.user_id == 10
        ).all()

        print(f"[结果] 找到 {len(test_orders)} 个订单")

        if len(test_orders) == 0:
            print("[提示] 没有订单需要清理")
            return

        # 2. 显示订单列表
        print("\n订单列表（前10个）：")
        print("-" * 70)
        for i, appt in enumerate(test_orders[:10], 1):
            print(f"{i:2}. {appt.appointment_no} | {appt.status:10} | "
                  f"{appt.created_at.strftime('%Y-%m-%d %H:%M')}")

        appointment_ids = [appt.id for appt in test_orders]

        # 3. 删除关联的咨询消息
        print(f"\n[步骤1] 删除关联的咨询消息...")
        messages = db.query(ConsultationMessage).filter(
            ConsultationMessage.appointment_id.in_(appointment_ids)
        ).all()
        print(f"  找到 {len(messages)} 条消息")
        for msg in messages:
            db.delete(msg)
        print(f"  已删除 {len(messages)} 条消息")

        # 4. 删除关联的评价记录
        print(f"\n[步骤2] 删除关联的评价记录...")
        reviews = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id.in_(appointment_ids)
        ).all()
        print(f"  找到 {len(reviews)} 条评价")
        for review in reviews:
            db.delete(review)
        print(f"  已删除 {len(reviews)} 条评价")

        # 5. 删除订单
        print(f"\n[步骤3] 删除订单...")
        for i, appt in enumerate(test_orders, 1):
            db.delete(appt)
            if i % 5 == 0:
                print(f"  已删除 {i}/{len(test_orders)}...")

        db.commit()

        print(f"\n[成功] 已删除 {len(test_orders)} 个订单及所有关联数据")

        # 6. 显示剩余数据统计
        remaining_orders = db.query(Appointment).count()
        remaining_messages = db.query(ConsultationMessage).count()
        remaining_reviews = db.query(ConsultationReview).count()

        print(f"\n[剩余数据统计]")
        print(f"  订单: {remaining_orders} 个")
        print(f"  消息: {remaining_messages} 条")
        print(f"  评价: {remaining_reviews} 条")

        # 7. 显示各用户的订单统计
        print("\n[统计] 各用户订单数量：")
        from sqlalchemy import func
        user_counts = db.query(
            Appointment.user_id,
            func.count(Appointment.id)
        ).group_by(Appointment.user_id).all()

        if user_counts:
            for user_id, count in user_counts:
                print(f"  用户ID={user_id}: {count}个订单")
        else:
            print("  (无订单)")

        print("\n" + "=" * 70)
        print("[完成] test@example.com用户的所有订单已完整清理")
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
