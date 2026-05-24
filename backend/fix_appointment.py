# -*- coding: utf-8 -*-
"""
修复counselor_id为NULL的预约记录
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, Counselor

def main():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("修复预约记录")
        print("=" * 80)

        # 查找 counselor_id 为 NULL 的预约
        null_appointments = db.query(Appointment).filter(
            Appointment.counselor_id == None
        ).all()

        if not null_appointments:
            print("\n没有需要修复的预约记录")
            return

        print(f"\n找到 {len(null_appointments)} 条需要修复的预约记录")

        # 获取第一个可用的咨询师
        counselor = db.query(Counselor).filter(
            Counselor.is_deleted == False,
            Counselor.status == 'active'
        ).first()

        if not counselor:
            print("\n错误: 没有可用的咨询师")
            return

        print(f"\n将使用咨询师: {counselor.name} (ID: {counselor.id})")

        # 修复预约记录
        for appt in null_appointments:
            print(f"\n修复预约 ID: {appt.id}, 预约号: {appt.appointment_no}")
            print(f"  原counselor_id: {appt.counselor_id}")
            appt.counselor_id = counselor.id
            # 根据咨询师的支持类型设置价格
            if appt.consultation_type == 'video' and counselor.price_video:
                appt.price = counselor.price_video
            elif appt.consultation_type == 'voice' and counselor.price_voice:
                appt.price = counselor.price_voice
            elif appt.consultation_type == 'offline' and counselor.price_offline:
                appt.price = counselor.price_offline
            print(f"  新counselor_id: {appt.counselor_id}")
            print(f"  更新价格: {appt.price}")

        db.commit()
        print("\n[OK] 预约记录修复成功")

    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
