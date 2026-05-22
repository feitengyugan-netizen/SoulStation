"""
创建测试预约
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.counselor import Appointment, Counselor
from datetime import datetime, timedelta

def create_test_appointment():
    """创建测试预约"""
    with Session(engine) as db:
        print("=== 创建测试预约 ===\n")

        # 查找用户ID=1 和 咨询师ID=9（孙医生）
        user_id = 1
        counselor_id = 9

        # 检查是否已有合适的预约
        existing = db.query(Appointment).filter(
            Appointment.user_id == user_id,
            Appointment.counselor_id == counselor_id,
            Appointment.status.in_(['confirmed', 'in_progress'])
        ).first()

        if existing:
            print(f"已存在合适的预约:")
            print(f"  预约ID: {existing.id}")
            print(f"  状态: {existing.status}")
            print(f"  类型: {existing.consultation_type}")
            print(f"  通话启用: {existing.call_enabled}")
            return existing.id

        # 创建新预约
        from app.core.config import settings
        import uuid

        appointment_no = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}{999}"
        appointment_date = datetime.now() + timedelta(hours=1)

        appointment = Appointment(
            user_id=user_id,
            counselor_id=counselor_id,
            appointment_no=appointment_no,
            consultation_type='video',
            appointment_date=appointment_date,
            duration=60,
            user_name='测试用户1',
            user_contact='user1@test.com',
            problem_description='视频通话测试',
            price=400,
            paid_amount=400,
            status='confirmed',
            call_enabled=True,
            call_count=0
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        print(f"创建成功:")
        print(f"  预约ID: {appointment.id}")
        print(f"  预约号: {appointment.appointment_no}")
        print(f"  用户ID: {user_id}")
        print(f"  咨询师ID: {counselor_id}")
        print(f"  状态: {appointment.status}")
        print(f"  类型: {appointment.consultation_type}")
        print(f"  通话启用: {appointment.call_enabled}")

        return appointment.id

if __name__ == "__main__":
    appointment_id = create_test_appointment()
    print(f"\n可以用于测试的预约ID: {appointment_id}")