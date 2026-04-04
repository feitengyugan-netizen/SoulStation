#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
删除演示订单
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, ConsultationMessage, ConsultationReview

def delete_demo_orders():
    """删除演示订单"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("删除演示订单")
        print("=" * 70)

        # 1. 查找所有演示订单
        print("\n[1] 查找演示订单...")
        demo_orders = db.query(Appointment).filter(
            Appointment.appointment_no.like('DEMO%')
        ).all()

        if not demo_orders:
            print("[提示] 没有找到演示订单")
            return

        print(f"[找到] {len(demo_orders)} 个演示订单:")
        for order in demo_orders:
            print(f"  - {order.appointment_no} (状态: {order.status})")

        # 2. 删除关联的咨询消息
        print("\n[2] 删除关联的咨询消息...")
        total_messages = 0
        for order in demo_orders:
            messages = db.query(ConsultationMessage).filter(
                ConsultationMessage.appointment_id == order.id
            ).all()
            count = len(messages)
            total_messages += count
            for msg in messages:
                db.delete(msg)
            if count > 0:
                print(f"  - 订单 {order.appointment_no}: 删除 {count} 条消息")

        print(f"[完成] 共删除 {total_messages} 条咨询消息")

        # 3. 删除关联的评价
        print("\n[3] 删除关联的评价...")
        total_reviews = 0
        for order in demo_orders:
            reviews = db.query(ConsultationReview).filter(
                ConsultationReview.appointment_id == order.id
            ).all()
            count = len(reviews)
            total_reviews += count
            for review in reviews:
                db.delete(review)
            if count > 0:
                print(f"  - 订单 {order.appointment_no}: 删除 {count} 条评价")

        print(f"[完成] 共删除 {total_reviews} 条评价")

        # 4. 删除订单本身
        print("\n[4] 删除订单...")
        for order in demo_orders:
            print(f"  - 删除订单: {order.appointment_no}")
            db.delete(order)

        db.commit()

        print("\n" + "=" * 70)
        print("[完成] 演示订单删除成功！")
        print("=" * 70)

        # 5. 验证删除结果
        print("\n[验证] 检查剩余订单...")
        remaining_orders = db.query(Appointment).filter(
            Appointment.appointment_no.like('DEMO%')
        ).count()
        print(f"剩余演示订单数量: {remaining_orders}")

        if remaining_orders == 0:
            print("[成功] 所有演示订单已完全删除")
        else:
            print("[警告] 仍有演示订单未删除")

    except Exception as e:
        print(f"\n[错误] 删除失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    delete_demo_orders()
