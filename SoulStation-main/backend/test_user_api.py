#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用户预约API
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Appointment
from app.services.counselor_service import AppointmentService

def test_user_appointments():
    """测试用户预约API"""
    db = SessionLocal()

    try:
        # 获取测试用户
        user = db.query(User).filter(User.email == 'test@example.com').first()
        if not user:
            print('[ERROR] 测试用户不存在')
            return

        print(f'[用户] ID: {user.id}, 邮箱: {user.email}')

        # 测试获取预约列表
        print('\n[测试] 获取用户预约列表（无状态筛选）')
        result = AppointmentService.get_user_appointments(
            db, user.id, status_filter=None, page=1, page_size=10
        )

        print(f'[返回] 总数: {result.get("total", 0)}')
        print(f'[返回] 订单数: {len(result.get("list", []))}')

        for i, order in enumerate(result.get("list", [])[:3], 1):
            print(f'\n订单 {i}:')
            print(f'  ID: {order.get("id")}')
            print(f'  日期: {order.get("date")} {order.get("timeSlot")}')
            print(f'  咨询师: {order.get("counselorName")}')
            print(f'  状态: {order.get("status")}')
            print(f'  类型: {order.get("type")}')
            print(f'  价格: {order.get("price")}')

    finally:
        db.close()

if __name__ == '__main__':
    test_user_appointments()
