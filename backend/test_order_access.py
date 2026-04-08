#!/usr/bin/env python3
"""
Test that counselor can only access their own orders
"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

print("=== 测试咨询师订单访问权限 ===\n")

# Test counselor Wang (counselor_id=1)
print("1. 咨询师王老师登录...")
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "teacher_wang@example.com",
    "password": "123456"
})

if login_resp.status_code != 200:
    print(f"❌ 登录失败")
    sys.exit(1)

result = login_resp.json()
token = result["data"]["token"]
headers = {"Authorization": f"Bearer {token}"}

# Get Wang's confirmed orders
print("2. 获取王老师的已确认订单...")
orders_resp = requests.get(
    f"{BASE_URL}/api/consultation/counselor/orders",
    headers=headers,
    params={"status_filter": "confirmed", "page": 1, "pageSize": 10}
)

if orders_resp.status_code == 200:
    data = orders_resp.json()
    if data.get('code') == 200:
        orders = data['data']['items']
        print(f"✅ 王老师的已确认订单数量: {len(orders)}")
        for order in orders:
            print(f"   订单ID: {order['id']}, 用户: {order.get('user_name', 'N/A')}")

        if orders:
            test_order = orders[0]
            order_id = test_order['id']
            print(f"\n3. 测试访问王老师的订单 {order_id}...")

            # Try to access messages
            msg_resp = requests.get(
                f"{BASE_URL}/api/consultation/{order_id}/messages",
                headers=headers
            )

            print(f"   状态码: {msg_resp.status_code}")
            if msg_resp.status_code == 200:
                msg_data = msg_resp.json()
                if msg_data.get('code') == 200:
                    print(f"✅ 成功访问，消息数: {msg_data['data']['total']}")
                else:
                    print(f"❌ API错误: {msg_data}")
            else:
                error = msg_resp.json()
                print(f"❌ 访问失败: {error.get('detail', 'Unknown error')}")
        else:
            print("⚠️  王老师没有已确认的订单")
    else:
        print(f"❌ API错误: {data}")
else:
    print(f"❌ HTTP错误: {orders_resp.status_code}")

# Test trying to access order that belongs to another counselor
print(f"\n4. 测试访问其他咨询师的订单 (ID=8, 属于李雪)...")
msg_resp = requests.get(
    f"{BASE_URL}/api/consultation/8/messages",
    headers=headers
)
print(f"   状态码: {msg_resp.status_code}")
if msg_resp.status_code != 200:
    error = msg_resp.json()
    print(f"✅ 正确拒绝访问: {error.get('detail', 'Unknown error')}")
else:
    print(f"❌ 不应该允许访问其他咨询师的订单")

print("\n=== 测试完成 ===")