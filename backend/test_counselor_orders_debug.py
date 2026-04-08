#!/usr/bin/env python3
"""
Test to verify counselor orders and debug the issue
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_counselor_orders():
    print("=== 检查咨询师王老师的订单 ===\n")

    # Login as counselor Wang
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    if login_resp.status_code != 200:
        print(f"❌ 登录失败")
        return

    result = login_resp.json()
    token = result["data"]["token"]
    user_info = result["data"]["userInfo"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"✅ 登录成功: {user_info['nickname']} (ID: {user_info['id']}, 角色: {user_info['role']})")

    # Get counselor ID
    status_resp = requests.get(f"{BASE_URL}/api/counselor/application/status", headers=headers)
    if status_resp.status_code == 200:
        status_data = status_resp.json()
        counselor_id = status_data["data"]["counselor_id"]
        print(f"✅ 咨询师ID: {counselor_id}")

    # Test different status filters
    for status_filter in ["pending", "confirmed", "in_progress", "completed"]:
        print(f"\n--- 状态: {status_filter} ---")
        orders_resp = requests.get(
            f"{BASE_URL}/api/consultation/counselor/orders",
            headers=headers,
            params={"status_filter": status_filter, "page": 1, "pageSize": 10}
        )

        if orders_resp.status_code == 200:
            data = orders_resp.json()
            if data.get('code') == 200:
                orders = data['data']['items']
                print(f"✅ 订单数量: {len(orders)}")
                for order in orders:
                    print(f"   订单ID: {order['id']}, 状态: {order['status']}, 用户: {order.get('user_name', 'N/A')}")
            else:
                print(f"❌ API错误: {data}")
        else:
            print(f"❌ HTTP错误: {orders_resp.status_code}")

    # Test trying to access order 8 (which belongs to counselor 5)
    print(f"\n=== 测试访问订单8 (属于李雪咨询师) ===")
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/8/messages",
        headers=headers
    )
    print(f"访问订单8的状态码: {msg_resp.status_code}")
    if msg_resp.status_code != 200:
        error = msg_resp.json()
        print(f"错误信息: {error.get('detail', 'Unknown error')}")

    # Test accessing order 4 (which belongs to Wang)
    print(f"\n=== 测试访问订单4 (属于王老师) ===")
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/4/messages",
        headers=headers
    )
    print(f"访问订单4的状态码: {msg_resp.status_code}")
    if msg_resp.status_code == 200:
        data = msg_resp.json()
        if data.get('code') == 200:
            print(f"✅ 成功访问，消息数: {data['data']['total']}")
    else:
        error = msg_resp.json()
        print(f"❌ 错误信息: {error.get('detail', 'Unknown error')}")

if __name__ == "__main__":
    test_counselor_orders()