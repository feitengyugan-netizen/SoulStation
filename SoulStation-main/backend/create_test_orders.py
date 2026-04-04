#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试预约订单
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Appointment, Counselor

def create_test_orders():
    """创建测试预约订单"""
    db = SessionLocal()

    try:
        # 获取测试用户和咨询师
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        counselors = db.query(Counselor).filter(Counselor.status == "active").all()

        if not test_user:
            print("[ERROR] Test user not found. Please create test user first.")
            return

        if not counselors:
            print("[ERROR] No active counselors found.")
            return

        print(f"Found {len(counselors)} counselors")
        print(f"Test user: {test_user.email}")

        # 生成订单号
        def generate_order_no():
            return f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

        # 当前时间
        now = datetime.now()

        # 测试订单数据
        test_orders = [
            # 待处理订单（未来时间）
            {
                "status": "pending",
                "appointment_date": now + timedelta(hours=24),
                "problem_description": "最近工作压力很大，经常失眠，希望能得到帮助。",
                "consultation_type": "video",
                "counselor_index": 0  # 王芳
            },
            {
                "status": "pending",
                "appointment_date": now + timedelta(hours=48),
                "problem_description": "孩子最近不愿意去学校，行为有些反常，很担心。",
                "consultation_type": "voice",
                "counselor_index": 1  # 李明
            },
            # 已确认订单
            {
                "status": "confirmed",
                "appointment_date": now + timedelta(hours=3),
                "problem_description": "夫妻关系出现问题，经常吵架，想寻求专业建议。",
                "consultation_type": "video",
                "counselor_index": 2,
                "confirmed_at": now
            },
            {
                "status": "confirmed",
                "appointment_date": now + timedelta(hours=6),
                "problem_description": "职场人际关系紧张，不知道如何处理。",
                "consultation_type": "voice",
                "counselor_index": 3,
                "confirmed_at": now
            },
            # 进行中订单
            {
                "status": "in_progress",
                "appointment_date": now - timedelta(minutes=30),
                "problem_description": "情绪低落已经持续两个月了，希望得到专业帮助。",
                "consultation_type": "video",
                "counselor_index": 0,
                "confirmed_at": now - timedelta(hours=2)
            },
            # 已完成订单
            {
                "status": "completed",
                "appointment_date": now - timedelta(days=1),
                "problem_description": "学习压力很大，考试焦虑明显。",
                "consultation_type": "voice",
                "counselor_index": 1,
                "confirmed_at": now - timedelta(days=1, hours=2),
                "completed_at": now - timedelta(days=1),
                "rating": 5,
                "review": "咨询师很专业，给了我很多有用的建议，感觉好多了！"
            },
            {
                "status": "completed",
                "appointment_date": now - timedelta(days=3),
                "problem_description": "对未来感到迷茫，不知道职业发展方向。",
                "consultation_type": "video",
                "counselor_index": 2,
                "confirmed_at": now - timedelta(days=3, hours=1),
                "completed_at": now - timedelta(days=3),
                "rating": 4,
                "review": "咨询过程很顺畅，老师很有耐心，希望能有更多交流。"
            },
            {
                "status": "completed",
                "appointment_date": now - timedelta(days=5),
                "problem_description": "家庭关系紧张，与父母沟通困难。",
                "consultation_type": "offline",
                "counselor_index": 3,
                "confirmed_at": now - timedelta(days=5, hours=3),
                "completed_at": now - timedelta(days=5),
                "rating": 5,
                "review": "非常感谢咨询师的帮助，现在和父母的关系改善了很多。"
            }
        ]

        created_count = 0

        for order_data in test_orders:
            counselor_index = order_data.pop("counselor_index")
            counselor = counselors[counselor_index] if counselor_index < len(counselors) else counselors[0]

            # 检查是否已存在该用户的类似订单
            existing = db.query(Appointment).filter(
                Appointment.user_id == test_user.id,
                Appointment.counselor_id == counselor.id,
                Appointment.appointment_date == order_data["appointment_date"]
            ).first()

            if existing:
                print(f"[SKIP] Order already exists for {counselor.name} at {order_data['appointment_date']}")
                continue

            # 获取价格
            if order_data["consultation_type"] == "video":
                price = counselor.price_video or 300
            elif order_data["consultation_type"] == "voice":
                price = counselor.price_voice or 200
            else:
                price = counselor.price_offline or 500

            # 创建订单
            appointment = Appointment(
                appointment_no=generate_order_no(),
                user_id=test_user.id,
                user_name=test_user.nickname or "测试用户",
                user_contact=test_user.phone or "13800138000",
                counselor_id=counselor.id,
                appointment_date=order_data["appointment_date"],
                consultation_type=order_data["consultation_type"],
                duration=60,  # 60分钟
                problem_description=order_data["problem_description"],
                price=price,
                paid_amount=price,
                status=order_data["status"],
                confirmed_at=order_data.get("confirmed_at"),
                completed_at=order_data.get("completed_at"),
                rating=order_data.get("rating"),
                review=order_data.get("review"),
                reminder_sent=False
            )

            db.add(appointment)
            created_count += 1

            # 更新咨询师统计
            if order_data["status"] == "completed":
                counselor.consultation_count = (counselor.consultation_count or 0) + 1
                if order_data.get("rating"):
                    # 更新评分
                    total_rating = (counselor.rating or 5.0) * (counselor.review_count or 0)
                    counselor.review_count = (counselor.review_count or 0) + 1
                    counselor.rating = (total_rating + order_data["rating"]) / counselor.review_count

            status_text = {
                "pending": "待处理",
                "confirmed": "已确认",
                "in_progress": "进行中",
                "completed": "已完成"
            }.get(order_data["status"], order_data["status"])

            print(f"[OK] 创建订单: {counselor.name} - {status_text} - {order_data['appointment_date'].strftime('%Y-%m-%d %H:%M')}")

        db.commit()

        print(f"\n成功创建 {created_count} 个测试订单！")
        print("\n订单统计：")
        print(f"- 待处理: {sum(1 for o in test_orders if o['status'] == 'pending')}")
        print(f"- 已确认: {sum(1 for o in test_orders if o['status'] == 'confirmed')}")
        print(f"- 进行中: {sum(1 for o in test_orders if o['status'] == 'in_progress')}")
        print(f"- 已完成: {sum(1 for o in test_orders if o['status'] == 'completed')}")

    except Exception as e:
        print(f"创建失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_orders()
