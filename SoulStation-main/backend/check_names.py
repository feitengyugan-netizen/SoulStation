#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查咨询师姓名
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Counselor
import json

db = SessionLocal()

print('数据库中的咨询师:')
print('=' * 70)
counselors = db.query(Counselor).filter(
    Counselor.is_deleted == False,
    Counselor.status == 'active'
).all()

for c in counselors:
    print(f"ID={c.id}: 姓名='{c.name}' | 职称='{c.title}'")

db.close()

# 同时检查API返回
import requests
response = requests.get("http://localhost:8000/api/counselor/list")
result = response.json()

print('\nAPI返回的咨询师:')
print('=' * 70)
items = result.get('data', {}).get('items', [])
for item in items:
    print(f"ID={item['id']}: 姓名='{item['name']}' | 职称='{item['title']}'")
