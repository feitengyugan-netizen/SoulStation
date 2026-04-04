#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证订单数据"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Appointment, Counselor

db = SessionLocal()
try:
    # 统计各状态订单
    from sqlalchemy import func
    status_counts = db.query(
        Appointment.status,
        func.count(Appointment.id)
    ).group_by(Appointment.status).all()

    print("=== 订单统计 ===")
    for status, count in status_counts:
        status_text = {
            "pending": "待处理",
            "confirmed": "已确认",
            "in_progress": "进行中",
            "completed": "已完成"
        }.get(status, status)
        print(f"{status_text}: {count}个")

    print("\n=== 最近创建的订单 ===")
    orders = db.query(Appointment).order_by(Appointment.created_at.desc()).limit(8).all()

    for order in orders:
        counselor = db.query(Counselor).filter(Counselor.id == order.counselor_id).first()
        status_text = {
            "pending": "[待处理]",
            "confirmed": "[已确认]",
            "in_progress": "[进行]",
            "completed": "[完成]"
        }.get(order.status, order.status)

        print(f"{status_text} {counselor.name if counselor else 'N/A'} - {order.appointment_date.strftime('%m-%d %H:%M')}")

finally:
    db.close()
