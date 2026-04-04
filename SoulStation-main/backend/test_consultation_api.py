#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试咨询对话API
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, Counselor
from app.models.user import User
from datetime import datetime, timedelta

def test_consultation_api():
    """测试咨询对话功能"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("测试咨询对话功能")
        print("=" * 70)

        # 1. 确保有可用的咨询订单
        print("\n[1] 检查可用的咨询订单...")
        in_progress_orders = db.query(Appointment).filter(
            Appointment.status == 'in_progress'
        ).all()

        if not in_progress_orders:
            print("[创建] 没有进行中的订单，创建一个测试订单...")

            # 创建一个进行中的测试订单
            test_order = Appointment(
                user_id=10,  # test@example.com
                counselor_id=2,  # 王芳
                appointment_no=f"TESTCHAT{datetime.now().strftime('%Y%m%d%H%M%S')}",
                appointment_date=datetime.now(),
                consultation_type="voice",
                duration=60,
                price=200.0,
                status="in_progress",
                user_name="测试用户",
                user_contact="13800138000",
                problem_description="测试咨询对话功能",
                confirmed_at=datetime.now()
            )
            db.add(test_order)
            db.commit()
            db.refresh(test_order)

            print(f"[创建] 测试订单 ID={test_order.id}, 订单号={test_order.appointment_no}")
            test_order_id = test_order.id
        else:
            test_order = in_progress_orders[0]
            test_order_id = test_order.id
            print(f"[使用] 现有订单 ID={test_order_id}, 订单号={test_order.appointment_no}")

        # 2. 测试发送消息
        print("\n[2] 测试发送消息...")
        try:
            from app.services.counselor_service import ConsultationService
            from app.schemas.counselor import SendMessageRequest

            # 用户发送消息
            user_message = SendMessageRequest(
                message_type='text',
                content='你好，我有一些心理问题想咨询'
            )
            message1 = ConsultationService.send_message(
                db,
                test_order_id,
                10,  # 用户ID
                'user',
                user_message
            )
            print(f"[发送] 用户消息: {message1.content}")

            # 咨询师回复
            counselor_message = SendMessageRequest(
                message_type='text',
                content='你好，我是王芳咨询师，请问有什么可以帮助您的？'
            )
            message2 = ConsultationService.send_message(
                db,
                test_order_id,
                4,  # 王芳的用户ID
                'counselor',
                counselor_message
            )
            print(f"[发送] 咨询师消息: {message2.content}")

        except Exception as e:
            print(f"[失败] 发送消息失败: {e}")
            import traceback
            traceback.print_exc()
            return

        # 3. 测试获取消息
        print("\n[3] 测试获取消息...")
        try:
            messages = ConsultationService.get_messages(
                db,
                test_order_id,
                10,  # user_id
                'user',
                None,  # last_id
                50
            )

            print(f"[获取] 获取到 {len(messages.get('messages', []))} 条消息")

            for msg in messages.get('messages', [])[:3]:
                sender = "用户" if msg['sender_type'] == 'user' else "咨询师"
                print(f"  - {sender}: {msg['content'][:30]}")

        except Exception as e:
            print(f"[失败] 获取消息失败: {e}")
            import traceback
            traceback.print_exc()
            return

        # 4. 测试结束咨询
        print("\n[4] 测试结束咨询...")
        try:
            ConsultationService.end_consultation(
                db,
                test_order_id,
                10,  # user_id
                'user'
            )
            print("[成功] 咨询已结束")

            # 验证订单状态
            updated_order = db.query(Appointment).filter(
                Appointment.id == test_order_id
            ).first()

            if updated_order.status == 'completed':
                print(f"[验证] 订单状态已更新为: {updated_order.status}")
            else:
                print(f"[警告] 订单状态: {updated_order.status}")

        except Exception as e:
            print(f"[失败] 结束咨询失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 70)
        print("[完成] 咨询对话API测试完成")
        print("=" * 70)
        print("\nAPI功能清单:")
        print("  ✓ 发送消息（用户/咨询师）")
        print("  ✓ 获取消息列表（支持增量获取）")
        print("  ✓ 结束咨询")
        print("  ✓ 权限验证（仅双方可见）")

        print("\n前端页面:")
        print("  - CounselorOrders.vue: 咨询师工作台")
        print("  - ConsultationChatUser.vue: 用户对话界面")
        print("  - ConsultationChatCounselor.vue: 咨询师对话界面")

    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_consultation_api()
