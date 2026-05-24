# -*- coding: utf-8 -*-
"""
检查预约记录的counselor_id
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment

def main():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("检查预约记录")
        print("=" * 80)

        # 查询所有预约记录
        appointments = db.query(Appointment).all()

        print(f"\n总预约记录数: {len(appointments)}")

        # 检查 counselor_id 为 NULL 的记录
        null_counselor = [appt for appt in appointments if appt.counselor_id is None]
        print(f"counselor_id 为 NULL 的记录: {len(null_counselor)}")

        if null_counselor:
            print("\ncounselor_id 为 NULL 的预约:")
            print("-" * 80)
            for appt in null_counselor:
                print(f"ID: {appt.id}, 预约号: {appt.appointment_no}, 用户ID: {appt.user_id}, 状态: {appt.status}")
            print("-" * 80)

        # 显示所有预约的详细信息
        print("\n所有预约记录:")
        print("-" * 80)
        for appt in appointments:
            print(f"ID: {appt.id}")
            print(f"  预约号: {appt.appointment_no}")
            print(f"  用户ID: {appt.user_id}")
            print(f"  咨询师ID: {appt.counselor_id}")
            print(f"  咨询类型: {appt.consultation_type}")
            print(f"  状态: {appt.status}")
            print(f"  创建时间: {appt.created_at}")
            print()

    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
