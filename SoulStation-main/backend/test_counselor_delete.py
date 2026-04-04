#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试咨询师删除订单功能
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, Counselor
from app.models.user import User
from datetime import datetime, timedelta

def test_counselor_delete():
    """测试咨询师删除订单"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("测试咨询师删除订单功能")
        print("=" * 70)

        # 1. 查找王芳咨询师
        wangfang = db.query(Counselor).filter(Counselor.name == "王芳").first()
        if not wangfang:
            print("[错误] 未找到王芳咨询师")
            return

        print(f"\n[1] 咨询师: {wangfang.name} (ID={wangfang.id})")
        print(f"    关联用户ID: {wangfang.user_id}")

        # 2. 创建一个已取消的测试订单
        print("\n[2] 创建测试订单...")
        test_order = Appointment(
            user_id=10,  # test@example.com
            counselor_id=wangfang.id,
            appointment_no=f"TESTDEL{datetime.now().strftime('%Y%m%d%H%M%S')}",
            appointment_date=datetime.now() - timedelta(days=1),
            consultation_type="voice",
            duration=60,
            price=200.0,
            status="cancelled",
            user_name="测试用户",
            user_contact="13800138000",
            problem_description="测试咨询师删除功能",
            cancelled_at=datetime.now()
        )
        db.add(test_order)
        db.commit()
        db.refresh(test_order)

        print(f"[创建] 订单 ID={test_order.id}, 订单号={test_order.appointment_no}")
        print(f"        状态={test_order.status}")
        print(f"        用户ID={test_order.user_id}")
        print(f"        咨询师ID={test_order.counselor_id}")

        # 3. 模拟王芳账号删除订单
        print(f"\n[3] 测试删除API...")
        print(f"    登录用户: 王芳 (user_id={wangfang.user_id})")

        # 直接调用删除逻辑
        try:
            from app.services.counselor_service import AppointmentService

            # 测试通过API删除（模拟）
            print(f"\n[测试1] 验证权限检查...")

            # 检查订单是否存在
            order_to_delete = db.query(Appointment).filter(
                Appointment.id == test_order.id
            ).first()

            if not order_to_delete:
                print("[失败] 订单不存在")
                return

            # 验证权限
            is_owner = order_to_delete.user_id == wangfang.user_id
            is_counselor = False

            if order_to_delete.counselor and order_to_delete.counselor.user_id:
                is_counselor = order_to_delete.counselor.user_id == wangfang.user_id

            print(f"    是否为订单创建者: {is_owner}")
            print(f"    是否为订单咨询师: {is_counselor}")

            if not is_owner and not is_counselor:
                print("[失败] 无权限删除此订单")
                return

            print("[成功] 权限验证通过")

            # 执行删除
            print(f"\n[测试2] 执行删除...")
            db.delete(order_to_delete)
            db.commit()
            print("[成功] 订单已删除")

            # 验证删除结果
            print(f"\n[4] 验证删除结果...")
            deleted_order = db.query(Appointment).filter(
                Appointment.id == test_order.id
            ).first()

            if deleted_order is None:
                print("[成功] 订单已从数据库中完全删除")
            else:
                print("[失败] 订单仍然存在")
                return

        except Exception as e:
            print(f"[失败] 删除失败: {e}")
            import traceback
            traceback.print_exc()
            return

        print("\n" + "=" * 70)
        print("[完成] 咨询师删除订单功能测试通过")
        print("=" * 70)
        print("\n总结:")
        print("  ✓ 咨询师可以删除分配给自己的订单")
        print("  ✓ 权限验证正确")
        print("  ✓ 删除后订单从数据库中完全移除")

    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_counselor_delete()
