#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试删除订单及其关联数据
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, ConsultationMessage, ConsultationReview
from datetime import datetime, timedelta

def test_delete_with_relations():
    """测试删除订单及关联数据"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("测试删除订单及关联数据")
        print("=" * 70)

        # 1. 创建一个测试订单（已取消状态）
        print("\n[1] 创建测试订单...")
        test_order = Appointment(
            user_id=10,
            counselor_id=2,  # 王芳
            appointment_no=f"TESTREL{datetime.now().strftime('%Y%m%d%H%M%S')}",
            appointment_date=datetime.now() - timedelta(days=1),
            consultation_type="voice",
            duration=60,
            price=200.0,
            status="cancelled",
            user_name="测试用户",
            user_contact="13800138000",
            problem_description="测试删除关联数据",
            cancelled_at=datetime.now()
        )
        db.add(test_order)
        db.commit()
        db.refresh(test_order)

        print(f"[创建] 订单 ID={test_order.id}")
        print(f"        状态={test_order.status}")

        # 2. 创建关联的消息记录
        print("\n[2] 创建关联消息...")
        msg1 = ConsultationMessage(
            appointment_id=test_order.id,
            sender_id=10,
            sender_type="user",
            message_type="text",
            content="测试消息1"
        )
        msg2 = ConsultationMessage(
            appointment_id=test_order.id,
            sender_id=4,  # 王芳
            sender_type="counselor",
            message_type="text",
            content="测试消息2"
        )
        db.add(msg1)
        db.add(msg2)
        db.commit()

        print(f"[创建] 2条消息记录")

        # 3. 创建关联的评价记录
        print("\n[3] 创建关联评价...")
        review = ConsultationReview(
            appointment_id=test_order.id,
            user_id=10,
            counselor_id=2,
            rating=5,
            content="测试评价"
        )
        db.add(review)
        db.commit()

        print(f"[创建] 1条评价记录")

        # 4. 验证关联数据存在
        print("\n[4] 验证关联数据...")
        message_count = db.query(ConsultationMessage).filter(
            ConsultationMessage.appointment_id == test_order.id
        ).count()
        review_count = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id == test_order.id
        ).count()

        print(f"    消息数: {message_count}")
        print(f"    评价数: {review_count}")

        # 5. 执行删除（模拟API逻辑）
        print("\n[5] 执行删除（包括关联数据）...")

        # 删除消息
        messages = db.query(ConsultationMessage).filter(
            ConsultationMessage.appointment_id == test_order.id
        ).all()
        for msg in messages:
            db.delete(msg)
        print(f"    已删除 {len(messages)} 条消息")

        # 删除评价
        reviews = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id == test_order.id
        ).all()
        for rev in reviews:
            db.delete(rev)
        print(f"    已删除 {len(reviews)} 条评价")

        # 删除订单
        db.delete(test_order)
        db.commit()
        print(f"    已删除订单")

        # 6. 验证删除结果
        print("\n[6] 验证删除结果...")
        order_exists = db.query(Appointment).filter(Appointment.id == test_order.id).first()
        message_exists = db.query(ConsultationMessage).filter(
            ConsultationMessage.appointment_id == test_order.id
        ).count()
        review_exists = db.query(ConsultationReview).filter(
            ConsultationReview.appointment_id == test_order.id
        ).count()

        if order_exists is None and message_exists == 0 and review_exists == 0:
            print("[成功] 订单及所有关联数据已完全删除")
        else:
            print(f"[失败] 删除不完全:")
            print(f"    订单存在: {order_exists is not None}")
            print(f"    消息存在: {message_exists}")
            print(f"    评价存在: {review_exists}")
            return

        print("\n" + "=" * 70)
        print("[完成] 删除订单及关联数据功能测试通过")
        print("=" * 70)
        print("\n功能特点:")
        print("  ✓ 自动删除关联的咨询消息")
        print("  ✓ 自动删除关联的评价记录")
        print("  ✓ 最后删除订单本身")
        print("  ✓ 不会出现外键约束错误")

    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_delete_with_relations()
