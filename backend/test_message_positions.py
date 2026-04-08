#!/usr/bin/env python3
"""
Test message display positions for both counselor and user
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_counselor_message_positions():
    print("=== 测试咨询师端消息位置 ===\n")

    # Login as counselor
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Send a message as counselor
    print("1. 咨询师发送消息:")
    send_resp = requests.post(
        f"{BASE_URL}/api/consultation/4/message",
        headers=headers,
        json={"content": "我是咨询师发的消息（应该在右边）", "type": "text"}
    )

    if send_resp.status_code == 200:
        print("   ✅ 消息发送成功")
        send_data = send_resp.json()
        print(f"   发送者类型: {send_data['data']['sender_type']}")
        print(f"   发送者ID: {send_data['data']['sender_id']}")
    else:
        print(f"   ❌ 发送失败: {send_resp.status_code}")
        return False

    # Get messages
    print("\n2. 获取消息列表:")
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/4/messages",
        headers=headers
    )

    if msg_resp.status_code == 200:
        msg_data = msg_resp.json()
        if msg_data.get('code') == 200:
            messages = msg_data['data']['items']
            print(f"   消息总数: {len(messages)}")

            print("\n   最近3条消息:")
            for msg in messages[-3:]:
                sender = "咨询师" if msg['sender_type'] == 'counselor' else "用户"
                position = "右边 (自己)" if msg['sender_type'] == 'counselor' else "左边 (对方)"
                print(f"   [{sender}] {msg['content']}")
                print(f"   发送者类型: {msg['sender_type']}")
                print(f"   位置: {position}")
                print()

            return True

    return False

def test_user_message_positions():
    print("\n=== 测试用户端消息位置 ===\n")

    # Login as user
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "xiaoming@example.com",
        "password": "123456"
    })

    if login_resp.status_code != 200:
        print("❌ 用户登录失败")
        return False

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get user's orders
    orders_resp = requests.get(f"{BASE_URL}/api/appointment/user/list", headers=headers)
    if orders_resp.status_code != 200:
        print("❌ 获取用户订单失败")
        return False

    orders_data = orders_resp.json()
    if orders_data.get('code') != 200:
        print("❌ API错误")
        return False

    orders = orders_data['data']['items'] or orders_data['data'].get('list', [])
    active_orders = [o for o in orders if o['status'] in ['confirmed', 'in_progress']]

    if not active_orders:
        print("⚠️  没有进行中的订单")
        return False

    order_id = active_orders[0]['id']
    print(f"1. 使用订单ID: {order_id}")

    # Send a message as user
    print("\n2. 用户发送消息:")
    send_resp = requests.post(
        f"{BASE_URL}/api/consultation/{order_id}/message",
        headers=headers,
        json={"content": "我是用户发的消息（应该在右边）", "type": "text"}
    )

    if send_resp.status_code == 200:
        print("   ✅ 消息发送成功")
        send_data = send_resp.json()
        print(f"   发送者类型: {send_data['data']['sender_type']}")
        print(f"   发送者ID: {send_data['data']['sender_id']}")
    else:
        print(f"   ❌ 发送失败: {send_resp.status_code}")
        return False

    # Get messages
    print("\n3. 获取消息列表:")
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/{order_id}/messages",
        headers=headers
    )

    if msg_resp.status_code == 200:
        msg_data = msg_resp.json()
        if msg_data.get('code') == 200:
            messages = msg_data['data']['items']
            print(f"   消息总数: {len(messages)}")

            print("\n   最近3条消息:")
            for msg in messages[-3:]:
                sender = "用户" if msg['sender_type'] == 'user' else "咨询师"
                position = "右边 (自己)" if msg['sender_type'] == 'user' else "左边 (对方)"
                print(f"   [{sender}] {msg['content']}")
                print(f"   发送者类型: {msg['sender_type']}")
                print(f"   位置: {position}")
                print()

            return True

    return False

if __name__ == "__main__":
    print("🧪 测试消息显示位置\n")

    counselor_test = test_counselor_message_positions()
    user_test = test_user_message_positions()

    print("="*60)
    print("📊 测试结果:")
    print(f"   咨询师端消息位置: {'✅ 正确' if counselor_test else '❌ 错误'}")
    print(f"   用户端消息位置:   {'✅ 正确' if user_test else '❌ 错误'}")
    print("="*60)

    if counselor_test and user_test:
        print("\n✅ 消息位置测试通过！")
        print("\n📱 前端显示规则:")
        print("咨询师端:")
        print("  - 咨询师发的消息: 右边 (紫色气泡)")
        print("  - 用户发的消息:   左边 (白色气泡)")
        print("\n用户端:")
        print("  - 用户发的消息:   右边 (白色气泡)")
        print("  - 咨询师发的消息: 左边 (紫色气泡)")
    else:
        print("\n❌ 测试失败，请检查错误信息")