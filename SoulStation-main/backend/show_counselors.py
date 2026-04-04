#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.counselor import Counselor
import requests

db = SessionLocal()

try:
    print("=" * 80)
    print("数据库中的咨询师".center(80))
    print("=" * 80)

    counselors = db.query(Counselor).filter(
        Counselor.is_deleted == False,
        Counselor.status == 'active'
    ).order_by(Counselor.id).all()

    for c in counselors:
        print(f"ID={c.id}: {c.name:10s} - {c.title}")

    print("\n" + "=" * 80)
    print("API返回的咨询师".center(80))
    print("=" * 80)

    response = requests.get("http://localhost:8000/api/counselor/list")
    result = response.json()
    items = result.get('data', {}).get('items', [])

    # 按ID排序
    items_sorted = sorted(items, key=lambda x: x['id'])

    for item in items_sorted:
        print(f"ID={item['id']}: {item['name']:10s} - {item['title']}")

finally:
    db.close()
