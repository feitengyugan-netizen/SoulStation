#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证咨询师数据一致性
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
import json

BASE_URL = "http://localhost:8000/api"

def verify_counselor_data():
    """验证数据库和API返回的咨询师数据"""
    print("=" * 70)
    print("验证咨询师数据一致性")
    print("=" * 70)

    # 1. 从数据库获取数据
    print("\n[1] 从数据库获取咨询师数据...")
    from app.core.database import SessionLocal
    from app.models.counselor import Counselor

    db = SessionLocal()
    try:
        db_counselors = db.query(Counselor).filter(
            Counselor.is_deleted == False,
            Counselor.status == 'active'
        ).all()

        print(f"数据库中咨询师数量: {len(db_counselors)}")

        db_data = []
        for c in db_counselors:
            db_data.append({
                'id': c.id,
                'name': c.name,
                'title': c.title,
                'specialties': c.specialties,
                'consultation_types': c.consultation_types,
                'rating': float(c.rating) if c.rating else 0,
                'price_voice': float(c.price_voice) if c.price_voice else 0,
                'status': c.status,
                'is_verified': c.is_verified
            })

    finally:
        db.close()

    # 2. 从API获取数据
    print("\n[2] 从API获取咨询师数据...")
    try:
        response = requests.get(f"{BASE_URL}/counselor/list")
        if response.status_code != 200:
            print(f"[错误] API请求失败: HTTP {response.status_code}")
            return

        result = response.json()
        if result.get("code") != 200:
            print(f"[错误] API返回错误: {result.get('message')}")
            return

        api_items = result.get("data", {}).get("items", [])
        print(f"API返回咨询师数量: {len(api_items)}")

        api_data = []
        for item in api_items:
            api_data.append({
                'id': item.get('id'),
                'name': item.get('name'),
                'title': item.get('title'),
                'specialties': item.get('specialties'),
                'consultation_types': item.get('consultation_types'),
                'rating': item.get('rating', 0),
                'price_voice': item.get('price_voice', 0),
                'status': item.get('status'),
                'is_verified': item.get('is_verified', False)
            })

    except Exception as e:
        print(f"[错误] 获取API数据失败: {e}")
        return

    # 3. 对比数据
    print("\n[3] 对比数据库和API数据...")
    print("-" * 70)

    if len(db_data) != len(api_data):
        print(f"[警告] 数据数量不一致: 数据库{len(db_data)} vs API{len(api_data)}")

    # 按ID匹配
    db_dict = {item['id']: item for item in db_data}
    api_dict = {item['id']: item for item in api_data}

    all_ids = sorted(set(list(db_dict.keys()) + list(api_dict.keys())))

    inconsistencies = []

    for cid in all_ids:
        db_item = db_dict.get(cid)
        api_item = api_dict.get(cid)

        print(f"\n咨询师 ID={cid}:")
        print("-" * 70)

        if db_item and api_item:
            # 检查各字段是否一致
            checks = [
                ('姓名', db_item['name'], api_item['name']),
                ('职称', db_item['title'], api_item['title']),
                ('擅长领域', db_item['specialties'], api_item['specialties']),
                ('咨询方式', db_item['consultation_types'], api_item['consultation_types']),
                ('评分', db_item['rating'], api_item['rating']),
                ('语音价格', db_item['price_voice'], api_item['price_voice']),
                ('状态', db_item['status'], api_item['status']),
                ('认证', db_item['is_verified'], api_item['is_verified'])
            ]

            all_match = True
            for field_name, db_val, api_val in checks:
                match = db_val == api_val
                symbol = "[OK]" if match else "[X]"
                print(f"  {symbol} {field_name}: {db_val} | {api_val}")
                if not match:
                    all_match = False
                    inconsistencies.append(f"ID={cid} {field_name}不一致")

            if not all_match:
                print(f"  [警告] 该咨询师数据存在不一致")
        elif db_item:
            print(f"  [警告] 仅存在于数据库: {db_item['name']}")
            inconsistencies.append(f"ID={cid} 仅存在于数据库")
        elif api_item:
            print(f"  [警告] 仅存在于API: {api_item['name']}")
            inconsistencies.append(f"ID={cid} 仅存在于API")

    # 4. 总结
    print("\n" + "=" * 70)
    print("[验证完成]")
    print("=" * 70)

    if inconsistencies:
        print(f"\n发现 {len(inconsistencies)} 处不一致:")
        for issue in inconsistencies:
            print(f"  - {issue}")
    else:
        print("\n[OK] 数据库和API数据完全一致")

    print("\n详细数据:")
    print("-" * 70)
    print("\n数据库中的咨询师:")
    for item in db_data:
        print(f"  ID={item['id']}: {item['name']} - {item['title']}")

    print("\nAPI返回的咨询师:")
    for item in api_data:
        print(f"  ID={item['id']}: {item['name']} - {item['title']}")

if __name__ == "__main__":
    verify_counselor_data()
