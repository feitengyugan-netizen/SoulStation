#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库数据"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.test import PsychologicalTest, TestQuestion

db = SessionLocal()
try:
    # 检查用户
    user_count = db.query(User).count()
    print(f"Users: {user_count}")

    # 检查管理员
    try:
        from app.models.admin import Admin
        admin_count = db.query(Admin).count()
        print(f"Admins: {admin_count}")
    except:
        print(f"Admins: N/A")

    # 检查测试
    test_count = db.query(PsychologicalTest).count()
    print(f"Tests: {test_count}")

    # 检查题目
    question_count = db.query(TestQuestion).count()
    print(f"Questions: {question_count}")

    if user_count > 0 or admin_count > 0:
        print("\nDatabase initialized successfully!")
    else:
        print("\nDatabase tables exist but no data found.")

finally:
    db.close()
