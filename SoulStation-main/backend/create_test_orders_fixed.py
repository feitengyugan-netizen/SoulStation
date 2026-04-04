# -*- coding: utf-8 -*-
from app.core.database import get_db
from app.models.counselor import Appointment
from datetime import datetime, timedelta
import random

db = next(get_db())

# 使用实际存在的用户ID
test_user_id = 10  # test@example.com
counselor_ids = [1, 3, 4, 5, 6]
test_name = '测试用户'
test_problems = [
    '最近感到压力很大，希望能咨询一下。',
    '情绪低落，需要心理支持。',
    '职场人际关系困扰，寻求建议。',
    '家庭矛盾需要调解。',
    '个人成长规划咨询。'
]

created_count = 0

for idx, counselor_id in enumerate(counselor_ids):
    appointment = Appointment(
        counselor_id=counselor_id,
        user_id=test_user_id,
        appointment_no=f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}{counselor_id}",
        consultation_type=random.choice(['video', 'voice', 'offline']),
        appointment_date=datetime.now() + timedelta(hours=2),
        duration=60,
        user_name=test_name,
        user_contact='13800138000',
        problem_description=random.choice(test_problems),
        price=random.choice([200, 300, 400]),
        paid_amount=0,
        status='confirmed',
        confirmed_at=datetime.now()
    )
    db.add(appointment)
    created_count += 1
    print(f"Created test appointment for counselor {counselor_id}")

try:
    db.commit()
    print(f"\nSuccessfully created {created_count} test appointments")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
