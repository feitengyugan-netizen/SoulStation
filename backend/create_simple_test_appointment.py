"""
创建简单测试预约
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.counselor import Appointment
from datetime import datetime, timedelta

def create_test_appointment():
    """创建测试预约"""
    with Session(engine) as db:
        print("=== 创建测试预约 ===\n")

        # 使用现有的预约ID 11（用户ID=1，咨询师ID=4，状态confirmed，类型video）
        # 只需要更新call_enabled字段

        appointment = db.query(Appointment).filter(Appointment.id == 11).first()

        if appointment:
            print(f"找到现有预约:")
            print(f"  预约ID: {appointment.id}")
            print(f"  用户ID: {appointment.user_id}")
            print(f"  咨询师ID: {appointment.counselor_id}")
            print(f"  状态: {appointment.status}")
            print(f"  类型: {appointment.consultation_type}")
            print(f"  通话启用: {appointment.call_enabled}")

            # 更新call_enabled
            appointment.call_enabled = True
            db.commit()

            print(f"\n已更新call_enabled字段")
            print(f"\n现在可以使用预约ID {appointment.id} 进行视频通话测试")

            return appointment.id
        else:
            print("未找到ID=11的预约")
            return None

if __name__ == "__main__":
    appointment_id = create_test_appointment()