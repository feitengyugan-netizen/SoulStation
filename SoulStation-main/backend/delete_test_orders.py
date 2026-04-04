#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
删除测试订单
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, ConsultationMessage, ConsultationReview

def delete_test_orders():
    """删除测试订单"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("删除测试订单")
        print("=" * 70)

        # 1. 查找所有测试订单（TEST开头的）
        print("\n[1] 查找测试订单...")
        test_orders = db.query(Appointment).filter(
            Appointment.appointment_no.like('TEST%')
        ).all()

        if not test_orders:
            print("[提示] 没有找到TEST开头的测试订单")
        else:
            print(f"[找到] {len(test_orders)} 个TEST开头的测试订单")
            for order in test_orders:
                print(f"  - {order.appointment_no} (状态: {order.status})")

        # 2. 查找其他可能的测试订单（通过用户ID=10判断）
        print("\n[2] 查找测试用户的其他订单...")
        other_test_orders = db.query(Appointment).filter(
            Appointment.user_id == 10,
            ~Appointment.appointment_no.like('TEST%'),
            ~Appointment.appointment_no.like('DEMO%')
        ).all()

        if not other_test_orders:
            print("[提示] 没有找到其他测试订单")
        else:
            print(f"[找到] {len(other_test_orders)} 个其他测试订单")
            for order in other_test_orders:
                print(f"  - {order.appointment_no} (状态: {order.status})")

        # 合并所有需要删除的订单
        all_orders = list(set(test_orders + other_test_orders))

        if not all_orders:
            print("\n[提示] 没有需要删除的测试订单")
            return

        print(f"\n[总共] {len(all_orders)} 个测试订单需要删除")

        # 3. 删除关联的咨询消息
        print("\n[3] 删除关联的咨询消息...")
        total_messages = 0
        for order in all_orders:
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

        # 4. 删除关联的评价
        print("\n[4] 删除关联的评价...")
        total_reviews = 0
        for order in all_orders:
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

        # 5. 删除订单本身
        print("\n[5] 删除订单...")
        for order in all_orders:
            print(f"  - 删除订单: {order.appointment_no}")
            db.delete(order)

        db.commit()

        print("\n" + "=" * 70)
        print("[完成] 测试订单删除成功！")
        print("=" * 70)

        # 6. 验证删除结果
        print("\n[验证] 检查剩余测试订单...")
        remaining_test = db.query(Appointment).filter(
            Appointment.appointment_no.like('TEST%')
        ).count()
        remaining_user = db.query(Appointment).filter(
            Appointment.user_id == 10,
            ~Appointment.appointment_no.like('TEST%'),
            ~Appointment.appointment_no.like('DEMO%')
        ).count()

        print(f"剩余TEST开头订单: {remaining_test}")
        print(f"剩余测试用户订单: {remaining_user}")

        if remaining_test == 0 and remaining_user == 0:
            print("[成功] 所有测试订单已完全删除")
        else:
            print(f"[提示] 仍有 {remaining_test + remaining_user} 个测试订单未删除")

        # 7. 显示剩余的所有订单
        print("\n[统计] 数据库中剩余的所有订单...")
        all_remaining = db.query(Appointment).count()
        print(f"剩余订单总数: {all_remaining}")

        if all_remaining > 0:
            print("\n剩余订单列表:")
            remaining_orders = db.query(Appointment).order_by(Appointment.created_at.desc()).limit(10).all()
            for order in remaining_orders:
                print(f"  - {order.appointment_no} (用户ID: {order.user_id}, 状态: {order.status})")

    except Exception as e:
        print(f"\n[错误] 删除失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    delete_test_orders()
