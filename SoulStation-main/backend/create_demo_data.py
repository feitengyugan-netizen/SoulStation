#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
咨询对话模块使用示例
演示完整的咨询对话流程
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, Counselor
from app.models.user import User
from datetime import datetime, timedelta

def create_demo_data():
    """创建演示数据"""
    db = SessionLocal()

    try:
        print("=" * 70)
        print("创建咨询对话演示数据")
        print("=" * 70)

        # 1. 确认咨询师账号存在
        print("\n[1] 检查咨询师账号...")
        wangfang = db.query(Counselor).filter(Counselor.name == "王芳").first()
        if wangfang and wangfang.user_id:
            wangfang_user = db.query(User).filter(User.id == wangfang.user_id).first()
            print(f"  王芳: {wangfang_user.email if wangfang_user else '未关联'}")
        else:
            print("  [警告] 王芳咨询师账号未正确配置")

        # 2. 创建演示订单
        print("\n[2] 创建演示咨询订单...")

        # 删除旧的演示订单
        old_orders = db.query(Appointment).filter(
            Appointment.appointment_no.like('DEMO%')
        ).all()
        for order in old_orders:
            db.delete(order)
        db.commit()

        # 创建新的演示订单
        demo_orders = [
            {
                "status": "confirmed",
                "description": "这是一个已确认的订单，可以开始咨询"
            },
            {
                "status": "in_progress",
                "description": "这是一个进行中的订单，正在咨询"
            },
            {
                "status": "completed",
                "description": "这是一个已完成的订单，可以查看评价"
            }
        ]

        for i, order_info in enumerate(demo_orders, 1):
            appointment_date = datetime.now() + timedelta(hours=i)

            order = Appointment(
                user_id=10,  # test@example.com
                counselor_id=2,  # 王芳
                appointment_no=f"DEMO{i:02d}{datetime.now().strftime('%Y%m%d%H%M%S')}",
                appointment_date=appointment_date,
                consultation_type="voice",
                duration=60,
                price=200.0,
                status=order_info["status"],
                user_name="测试用户",
                user_contact="13800138000",
                problem_description=f"演示订单{i} - {order_info['description']}"
            )

            if order_info["status"] in ["confirmed", "in_progress", "completed"]:
                order.confirmed_at = appointment_date - timedelta(minutes=30)

            if order_info["status"] == "in_progress":
                order.appointment_date = datetime.now() - timedelta(minutes=30)
            elif order_info["status"] == "completed":
                order.appointment_date = datetime.now() - timedelta(hours=1)
                order.completed_at = datetime.now() - timedelta(minutes=30)

            db.add(order)

        db.commit()

        print(f"  [创建] {len(demo_orders)} 个演示订单")

        # 3. 为进行中的订单添加对话消息
        print("\n[3] 为进行中的订单添加演示消息...")
        in_progress_order = db.query(Appointment).filter(
            Appointment.status == 'in_progress',
            Appointment.appointment_no.like('DEMO%')
        ).first()

        if in_progress_order:
            from app.models.counselor import ConsultationMessage
            from app.schemas.counselor import SendMessageRequest

            demo_messages = [
                {
                    "sender_type": "user",
                    "content": "王老师您好，我最近总是感到焦虑，睡不着觉"
                },
                {
                    "sender_type": "counselor",
                    "content": "你好！我是王芳咨询师，很高兴能为你提供帮助。能详细说说你的情况吗？"
                },
                {
                    "sender_type": "user",
                    "content": "主要是工作压力很大，经常担心完不成任务，晚上就睡不着"
                },
                {
                    "sender_type": "counselor",
                    "content": "我理解你的感受。工作焦虑是很常见的问题。这种焦虑持续多长时间了？"
                }
            ]

            for i, msg_info in enumerate(demo_messages):
                # 确定发送者ID
                if msg_info["sender_type"] == "user":
                    sender_id = 10  # test@example.com
                else:
                    sender_id = 4  # 王芳的用户ID

                message = ConsultationMessage(
                    appointment_id=in_progress_order.id,
                    sender_id=sender_id,
                    sender_type=msg_info["sender_type"],
                    message_type="text",
                    content=msg_info["content"],
                    is_read=(i < len(demo_messages) - 1)  # 前面的消息标记为已读
                )
                db.add(message)

            db.commit()

            print(f"  [创建] {len(demo_messages)} 条演示对话消息")

        print("\n" + "=" * 70)
        print("[完成] 演示数据创建成功！")
        print("=" * 70)

        print("\n测试账号：")
        print("-" * 70)
        print("用户端：")
        print("  邮箱: test@example.com")
        print("  密码: 123456")
        print("")
        print("咨询师端（王芳）：")
        print("  邮箱: wangfang@example.com")
        print("  密码: 123456")

        print("\n演示订单：")
        print("-" * 70)
        all_demo_orders = db.query(Appointment).filter(
            Appointment.appointment_no.like('DEMO%')
        ).order_by(Appointment.created_at.asc()).all()

        for order in all_demo_orders:
            status_text = {
                "confirmed": "已确认",
                "in_progress": "进行中",
                "completed": "已完成"
            }.get(order.status, order.status)

            print(f"订单 {order.appointment_no}")
            print(f"  状态: {status_text}")
            print(f"  说明: {order.problem_description}")

        print("\n测试流程：")
        print("-" * 70)
        print("1. 登录 test@example.com")
        print("2. 点击某个订单的'进入咨询'按钮")
        print("3. 查看演示对话消息")
        print("4. 发送新消息测试功能")
        print("")
        print("咨询师端：")
        print("1. 登录 wangfang@example.com")
        print("2. 进入工作台查看订单")
        print("3. 处理待确认订单（同意/拒绝）")
        print("4. 对已确认订单点击'进入咨询'")

    except Exception as e:
        print(f"\n[错误] 创建失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()
