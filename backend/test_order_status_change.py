#!/usr/bin/env python3
"""
Debug order status change when entering chat
"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def debug_order_status():
    print("=== 调试订单状态变化 ===\n")

    # Login as counselor
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 初始状态：获取confirmed订单
    print("1. 初始状态 - 获取confirmed订单:")
    orders_resp = requests.get(
        f"{BASE_URL}/api/consultation/counselor/orders",
        headers=headers,
        params={"status_filter": "confirmed", "page": 1, "pageSize": 10}
    )

    if orders_resp.status_code == 200:
        data = orders_resp.json()
        if data.get('code') == 200:
            orders = data['data']['items']
            print(f"   Confirmed订单数量: {len(orders)}")
            for order in orders:
                print(f"   订单ID: {order['id']}, 状态: {order['status']}")

    # 2. 访问聊天界面（模拟点击进入咨询）
    if orders:
        order_id = orders[0]['id']
        print(f"\n2. 模拟点击'进入咨询'（订单ID: {order_id}）:")

        msg_resp = requests.get(
            f"{BASE_URL}/api/consultation/{order_id}/messages",
            headers=headers
        )

        print(f"   访问聊天状态码: {msg_resp.status_code}")

        # 3. 再次获取confirmed订单
        print(f"\n3. 访问聊天后 - 再次获取confirmed订单:")
        orders_resp2 = requests.get(
            f"{BASE_URL}/api/consultation/counselor/orders",
            headers=headers,
            params={"status_filter": "confirmed", "page": 1, "pageSize": 10}
        )

        if orders_resp2.status_code == 200:
            data2 = orders_resp2.json()
            if data2.get('code') == 200:
                orders2 = data2['data']['items']
                print(f"   Confirmed订单数量: {len(orders2)}")

                # 检查原来的订单是否还在
                still_exists = any(o['id'] == order_id for o in orders2)
                print(f"   订单{order_id}是否仍在confirmed列表: {still_exists}")

                if not still_exists:
                    print(f"\n4. 订单{order_id}消失了！检查它的当前状态:")

                    # 获取所有订单查找该订单
                    all_resp = requests.get(
                        f"{BASE_URL}/api/consultation/counselor/orders",
                        headers=headers,
                        params={"page": 1, "pageSize": 20}
                    )

                    if all_resp.status_code == 200:
                        all_data = all_resp.json()
                        if all_data.get('code') == 200:
                            all_orders = all_data['data']['items']
                            target_order = next((o for o in all_orders if o['id'] == order_id), None)
                            if target_order:
                                print(f"   找到订单！新状态: {target_order['status']}")
                                print(f"   原因: 订单状态从confirmed变成了{target_order['status']}")
                            else:
                                print(f"   订单完全消失（不应该发生）")

if __name__ == "__main__":
    debug_order_status()