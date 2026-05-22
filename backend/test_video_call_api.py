"""
测试视频通话API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.counselor import Appointment

def check_appointments():
    """检查可用的预约"""
    with Session(engine) as db:
        print("=== 检查可用预约 ===\n")

        appointments = db.query(Appointment).all()

        if not appointments:
            print("没有预约数据，需要先创建预约")
            return

        print(f"找到 {len(appointments)} 个预约:\n")

        for apt in appointments:
            print(f"ID: {apt.id}")
            print(f"  状态: {apt.status}")
            print(f"  类型: {apt.consultation_type}")
            print(f"  用户ID: {apt.user_id}")
            print(f"  咨询师ID: {apt.counselor_id}")
            print(f"  通话启用: {apt.call_enabled}")
            print(f"  通话次数: {apt.call_count}")
            print()

        # 查找可以测试的预约（状态为confirmed或in_progress）
        testable = [apt for apt in appointments if apt.status in ['confirmed', 'in_progress']]

        if testable:
            print(f"可测试的预约（状态为confirmed/in_progress）: {len(testable)} 个")
            print("\n推荐测试预约:")
            for apt in testable[:3]:
                print(f"- 预约ID: {apt.id}, 状态: {apt.status}, 类型: {apt.consultation_type}")
        else:
            print("没有可测试的预约，需要先创建confirmed或in_progress状态的预约")

if __name__ == "__main__":
    check_appointments()