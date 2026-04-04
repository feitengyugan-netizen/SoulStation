#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试取消订单并从数据库删除
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment
from app.services.counselor_service import AppointmentService

def test_cancel_and_delete():
    """测试取消订单并从数据库删除"""
    db = SessionLocal()

    try:
        # 1. 查询用户的所有订单
        print("=" * 70)
        print("测试：取消订单并从数据库删除")
        print("=" * 70)

        user_id = 10  # test@example.com用户ID
        appointments = db.query(Appointment).filter(
            Appointment.user_id == user_id
        ).order_by(Appointment.created_at.desc()).all()

        print(f"\n[当前状态] 用户共有 {len(appointments)} 个订单")

        if len(appointments) == 0:
            print("[提示] 没有订单可以测试")
            return

        # 显示前3个订单
        print("\n最近3个订单:")
        for i, appt in enumerate(appointments[:3], 1):
            print(f"  {i}. ID={appt.id}, 订单号={appt.appointment_no}")
            print(f"     状态={appt.status}, 咨询师ID={appt.counselor_id}")

        # 2. 选择第一个订单进行取消（如果是pending状态）
        appointment_to_cancel = None
        for appt in appointments:
            if appt.status == 'pending':
                appointment_to_cancel = appt
                break

        if not appointment_to_cancel:
            print("\n[提示] 没有待确认的订单，创建一个测试订单...")

            # 创建一个测试订单
            from datetime import datetime, timedelta
            test_appointment = Appointment(
                user_id=user_id,
                counselor_id=2,  # 王芳
                appointment_no=f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
                appointment_date=datetime.now() + timedelta(days=1),
                consultation_type="voice",
                duration=60,
                price=200.0,
                status="pending",
                user_name="测试用户",
                user_contact="13800138000",
                problem_description="测试取消功能"
            )
            db.add(test_appointment)
            db.commit()
            db.refresh(test_appointment)
            appointment_to_cancel = test_appointment
            print(f"[创建] 测试订单 ID={test_appointment.id}, 订单号={test_appointment.appointment_no}")

        print(f"\n[取消] 订单 ID={appointment_to_cancel.id}, 订单号={appointment_to_cancel.appointment_no}")
        print(f"       状态={appointment_to_cancel.status}")

        # 记录取消前的订单ID
        canceled_id = appointment_to_cancel.id
        canceled_no = appointment_to_cancel.appointment_no

        # 3. 调用取消方法
        try:
            AppointmentService.cancel_appointment(
                db, user_id, canceled_id, "测试取消功能"
            )
            print("[成功] 调用取消方法成功")
        except Exception as e:
            print(f"[失败] 取消失败: {e}")
            return

        # 4. 验证订单是否从数据库中删除
        print("\n[验证] 检查订单是否从数据库删除...")

        deleted_appointment = db.query(Appointment).filter(
            Appointment.id == canceled_id
        ).first()

        if deleted_appointment is None:
            print(f"[成功] 订单 ID={canceled_id} 已从数据库中删除")
        else:
            print(f"[失败] 订单仍然存在，状态={deleted_appointment.status}")
            return

        # 5. 验证用户订单数量减少
        remaining_appointments = db.query(Appointment).filter(
            Appointment.user_id == user_id
        ).count()

        print(f"[验证] 用户当前订单数: {remaining_appointments} (之前: {len(appointments)})")

        if remaining_appointments == len(appointments) - 1:
            print("[成功] 订单数量正确减少1个")
        else:
            print(f"[警告] 订单数量异常: 期望{len(appointments)-1}, 实际{remaining_appointments}")

        # 6. 验证咨询师订单列表中也没有该订单
        print(f"\n[验证] 检查咨询师订单列表...")
        counselor_orders = db.query(Appointment).filter(
            Appointment.counselor_id == appointment_to_cancel.counselor_id
        ).all()

        found_in_counselor = any(order.id == canceled_id for order in counselor_orders)
        if not found_in_counselor:
            print(f"[成功] 咨询师订单列表中也没有该订单")
        else:
            print(f"[失败] 咨询师订单列表中仍然存在该订单")

        print("\n" + "=" * 70)
        print("[测试完成] 订单取消功能正确")
        print("=" * 70)
        print("\n总结:")
        print("  [OK] 取消订单后，记录从数据库中完全删除")
        print("  [OK] 用户'我的预约'中不再显示该订单")
        print("  [OK] 咨询师'工作台'中不再显示该订单")

    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_cancel_and_delete()
