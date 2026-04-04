#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试前端API调用
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
import json

def test_frontend_api():
    """测试前端API"""
    base_url = "http://localhost:8000/api"

    print("=== 测试登录API ===")
    # 1. 登录获取token
    login_response = requests.post(
        f"{base_url}/auth/login",
        json={
            "email": "test@example.com",
            "password": "123456"
        }
    )

    print(f"登录状态码: {login_response.status_code}")
    if login_response.status_code == 200:
        login_data = login_response.json()
        print(f"登录响应: {json.dumps(login_data, indent=2, ensure_ascii=False)}")

        if login_data.get("code") == 200:
            token = login_data["data"]["token"]
            print(f"\n[成功] 获取到token: {token[:50]}...")

            # 2. 测试获取用户预约列表
            print("\n=== 测试用户预约列表API ===")
            headers = {"Authorization": f"Bearer {token}"}

            appointments_response = requests.get(
                f"{base_url}/appointment/user/list",
                headers=headers
            )

            print(f"API状态码: {appointments_response.status_code}")
            print(f"响应内容: {json.dumps(appointments_response.json(), indent=2, ensure_ascii=False)}")

            if appointments_response.status_code == 200:
                data = appointments_response.json()
                if data.get("code") == 200:
                    orders = data["data"].get("list", [])
                    print(f"\n[成功] 获取到 {len(orders)} 个订单")
                    for i, order in enumerate(orders[:3], 1):
                        print(f"  订单{i}: ID={order.get('id')}, 日期={order.get('date')}, 咨询师={order.get('counselorName')}")
                else:
                    print(f"[错误] API返回错误: {data.get('message')}")
    else:
        print(f"[错误] 登录失败: {login_response.text}")

if __name__ == "__main__":
    test_frontend_api()
