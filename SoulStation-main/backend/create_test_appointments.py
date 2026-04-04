#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通过API创建测试预约订单
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000/api"

def login(email, password):
    """登录获取token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            return data["data"]["token"]
    return None

def create_appointment(token, appointment_data):
    """创建预约"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/appointment/create",
        headers=headers,
        json=appointment_data
    )
    return response

def get_counselors():
    """获取咨询师列表"""
    response = requests.get(f"{BASE_URL}/counselor/list")
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 200:
            return data["data"]["items"]
    return []

def main():
    print("=== 通过API创建测试预约订单 ===\n")

    # 1. 获取咨询师列表
    print("1. 获取咨询师列表...")
    counselors = get_counselors()
    if not counselors:
        print("[错误] 无法获取咨询师列表")
        return

    print(f"[成功] 获取到 {len(counselors)} 位咨询师")
    for c in counselors[:3]:
        print(f"   - {c['name']} (ID: {c['id']})")

    # 2. 用户登录
    print("\n2. 用户登录...")
    user_token = login("test@example.com", "123456")
    if not user_token:
        print("[错误] 用户登录失败")
        return
    print("[成功] 用户登录成功")

    # 3. 创建多个测试预约
    print("\n3. 创建测试预约订单...")
    print("-" * 60)

    # 预约配置
    appointments_config = [
        {
            "counselor_id": 1,  # 胡医生
            "consultation_type": "video",
            "days_from_now": 1,
            "hour": 10,
            "problem": "最近工作压力很大，经常失眠，希望能得到专业建议。"
        },
        {
            "counselor_id": 2,  # 王芳
            "consultation_type": "voice",
            "days_from_now": 1,
            "hour": 14,
            "problem": "孩子不愿意去上学，每次送到学校就哭闹，家长很焦虑。"
        },
        {
            "counselor_id": 3,  # 李明
            "consultation_type": "offline",
            "days_from_now": 2,
            "hour": 9,
            "problem": "夫妻关系紧张，经常因为小事争吵，希望改善沟通方式。"
        },
        {
            "counselor_id": 1,  # 胡医生
            "consultation_type": "video",
            "days_from_now": 2,
            "hour": 15,
            "problem": "已经确诊抑郁症，正在服药，想咨询心理疏导。"
        },
        {
            "counselor_id": 2,  # 王芳
            "consultation_type": "voice",
            "days_from_now": 3,
            "hour": 10,
            "problem": "学习压力特别大，考试前会失眠焦虑，影响发挥。"
        },
        {
            "counselor_id": 4,  # 陈刚
            "consultation_type": "video",
            "days_from_now": 3,
            "hour": 16,
            "problem": "职场人际关系困扰，与同事和上司相处困难。"
        },
        {
            "counselor_id": 3,  # 李明
            "consultation_type": "offline",
            "days_from_now": 4,
            "hour": 14,
            "problem": "婚前恐惧，对即将到来的婚姻生活感到不安。"
        },
        {
            "counselor_id": 1,  # 胡医生
            "consultation_type": "voice",
            "days_from_now": 5,
            "hour": 11,
            "problem": "童年创伤影响现在的亲密关系，希望进行心理治疗。"
        }
    ]

    success_count = 0
    for i, config in enumerate(appointments_config, 1):
        # 计算预约时间
        appointment_date = datetime.now() + timedelta(days=config["days_from_now"])
        appointment_date = appointment_date.replace(hour=config["hour"], minute=0, second=0, microsecond=0)

        # 准备预约数据
        appointment_data = {
            "counselor_id": config["counselor_id"],
            "consultation_type": config["consultation_type"],
            "appointment_date": appointment_date.strftime("%Y-%m-%d %H:%M"),
            "duration": 60,
            "problem_description": config["problem"]
        }

        # 获取咨询师信息
        counselor = next((c for c in counselors if c["id"] == config["counselor_id"]), None)
        counselor_name = counselor["name"] if counselor else f"咨询师{config['counselor_id']}"

        # 创建预约
        print(f"\n预约 {i}:")
        print(f"  咨询师: {counselor_name}")
        print(f"  类型: {config['consultation_type']}")
        print(f"  时间: {appointment_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"  问题: {config['problem'][:30]}...")

        response = create_appointment(user_token, appointment_data)

        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                # API直接返回appointment对象在data字段中
                appointment_data = result.get("data", {})
                appointment_no = appointment_data.get("appointmentNo", "未知")
                print(f"  [成功] 订单号: {appointment_no}")
                success_count += 1
            else:
                print(f"  [失败] {result.get('message')}")
        else:
            print(f"  [失败] HTTP {response.status_code}: {response.text[:200]}")

    print("\n" + "=" * 60)
    print(f"[完成] 成功创建 {success_count}/{len(appointments_config)} 个测试预约")
    print("\n这些预约将会：")
    print("  1. 显示在用户的'我的预约'界面中")
    print("  2. 显示在对应咨询师的'工作台'订单列表中")
    print("\n测试账号：")
    print("  用户: test@example.com / 123456")
    print("  咨询师: wangfang@example.com / 123456 (王芳)")
    print("  咨询师: liming@example.com / 123456 (李明)")
    print("  咨询师: chengang@example.com / 123456 (陈刚)")

if __name__ == "__main__":
    main()
