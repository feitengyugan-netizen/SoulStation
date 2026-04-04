#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证咨询师数据"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor

db = SessionLocal()
try:
    # 查询所有咨询师
    counselors = db.query(Counselor).all()

    print(f"Total counselors: {len(counselors)}")
    print()

    for c in counselors:
        # 获取关联的用户信息
        user = db.query(User).filter(User.id == c.user_id).first()
        print(f"Name: {c.name}")
        print(f"Email: {user.email if user else 'N/A'}")
        print(f"Title: {c.title}")
        print(f"Specialties: {c.specialties}")
        print(f"Price: Video={c.price_video}, Voice={c.price_voice}, Offline={c.price_offline}")
        print(f"Status: {c.status}, Verified: {c.is_verified}")
        print("---")
finally:
    db.close()
