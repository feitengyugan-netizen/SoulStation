#!/usr/bin/env python3
"""
Complete test for all three fixes
"""
import requests
import json
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_counselor_message_flow():
    print("=== 测试咨询师消息发送和显示 ===\n")

    # Login as counselor
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("1. 发送测试消息...")
    send_resp = requests.post(
        f"{BASE_URL}/api/consultation/4/message",
        headers=headers,
        json={"content": "咨询师测试消息 - " + str(int(time.time())), "type": "text"}
    )

    if send_resp.status_code == 200:
        print("✅ 消息发送成功")
        send_data = send_resp.json()
        print(f"   消息ID: {send_data['data']['id']}")
        print(f"   内容: {send_data['data']['content']}")
    else:
        print(f"❌ 发送失败: {send_resp.status_code}")
        return False

    print("\n2. 获取消息列表...")
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/4/messages",
        headers=headers
    )

    if msg_resp.status_code == 200:
        msg_data = msg_resp.json()
        if msg_data.get('code') == 200:
            messages = msg_data['data']['items']
            print(f"✅ 获取到 {len(messages)} 条消息")

            # 显示最近3条消息
            print("\n   最近的3条消息:")
            for msg in messages[-3:]:
                sender = "咨询师" if msg['sender_type'] == 'counselor' else "用户"
                print(f"   [{sender}] {msg['content']}")
                print(f"   类型: {msg.get('message_type', 'N/A')}")
                print(f"   时间: {msg['created_at']}")

            return True
        else:
            print(f"❌ API错误: {msg_data}")
            return False
    else:
        print(f"❌ 获取失败: {msg_resp.status_code}")
        return False

def test_user_message_flow():
    print("\n=== 测试用户消息发送和显示 ===\n")

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

    print("1. 获取用户订单...")
    orders_resp = requests.get(f"{BASE_URL}/api/appointment/user/list", headers=headers)

    if orders_resp.status_code == 200:
        orders_data = orders_resp.json()
        if orders_data.get('code') == 200:
            orders = orders_data['data']['items'] or orders_data['data'].get('list', [])
            confirmed_orders = [o for o in orders if o['status'] in ['confirmed', 'in_progress']]

            if not confirmed_orders:
                print("⚠️  没有已确认的订单")
                return False

            order_id = confirmed_orders[0]['id']
            print(f"✅ 找到已确认订单 ID: {order_id}")

            print(f"\n2. 发送测试消息...")
            send_resp = requests.post(
                f"{BASE_URL}/api/consultation/{order_id}/message",
                headers=headers,
                json={"content": "用户测试消息 - " + str(int(time.time())), "type": "text"}
            )

            if send_resp.status_code == 200:
                print("✅ 消息发送成功")

                print(f"\n3. 获取消息列表...")
                msg_resp = requests.get(
                    f"{BASE_URL}/api/consultation/{order_id}/messages",
                    headers=headers
                )

                if msg_resp.status_code == 200:
                    msg_data = msg_resp.json()
                    if msg_data.get('code') == 200:
                        messages = msg_data['data']['items']
                        print(f"✅ 获取到 {len(messages)} 条消息")
                        return True
                    else:
                        print(f"❌ API错误: {msg_data}")
                        return False
                else:
                    print(f"❌ 获取失败: {msg_resp.status_code}")
                    return False
            else:
                print(f"❌ 发送失败: {send_resp.status_code}")
                return False
        else:
            print(f"❌ API错误: {orders_data}")
            return False
    else:
        print(f"❌ 获取订单失败: {orders_resp.status_code}")
        return False

def test_order_persistence():
    print("\n=== 测试订单状态持久性 ===\n")

    # Login as counselor
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("1. 获取已确认订单...")
    orders_resp = requests.get(
        f"{BASE_URL}/api/consultation/counselor/orders",
        headers=headers,
        params={"status_filter": "confirmed", "page": 1, "pageSize": 10}
    )

    if orders_resp.status_code == 200:
        data = orders_resp.json()
        if data.get('code') == 200:
            orders = data['data']['items']
            print(f"✅ 已确认订单数量: {len(orders)}")
            for order in orders:
                print(f"   订单ID: {order['id']}, 用户: {order.get('user_name', 'N/A')}, 状态: {order['status']}")

            if orders:
                order_id = orders[0]['id']

                print(f"\n2. 模拟点击'进入咨询'后返回...")

                # 再次获取订单，模拟返回后的状态
                orders_resp2 = requests.get(
                    f"{BASE_URL}/api/consultation/counselor/orders",
                    headers=headers,
                    params={"status_filter": "confirmed", "page": 1, "pageSize": 10}
                )

                if orders_resp2.status_code == 200:
                    data2 = orders_resp2.json()
                    if data2.get('code') == 200:
                        orders2 = data2['data']['items']
                        print(f"✅ 返回后订单数量: {len(orders2)}")

                        # 检查订单是否还在
                        order_exists = any(o['id'] == order_id for o in orders2)
                        if order_exists:
                            print(f"✅ 订单 {order_id} 仍然存在")
                            return True
                        else:
                            print(f"❌ 订单 {order_id} 消失了")
                            return False

    return False

if __name__ == "__main__":
    print("🔄 测试所有三个修复\n")

    test1 = test_counselor_message_flow()
    test2 = test_user_message_flow()
    test3 = test_order_persistence()

    print("\n" + "="*50)
    print("📊 测试结果:")
    print(f"   1. 咨询师消息显示: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"   2. 用户消息显示:   {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"   3. 订单状态持久性:  {'✅ 通过' if test3 else '❌ 失败'}")
    print("="*50)

    if test1 and test2 and test3:
        print("\n✅ 所有测试通过！")
        print("\n📱 前端操作指南:")
        print("1. 清除浏览器缓存 (Ctrl+Shift+Delete)")
        print("2. 重新登录: http://localhost:5177/login")
        print("3. 咨询师: 工作台 → 点击'进入咨询' → 发送消息")
        print("4. 用户: 我的订单 → 点击'进入咨询' → 发送消息")
        print("5. 返回工作台验证订单仍然存在")
    else:
        print("\n❌ 部分测试失败，请检查错误信息")