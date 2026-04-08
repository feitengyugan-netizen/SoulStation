#!/usr/bin/env python3
"""
Complete test for counselor dashboard and consultation functionality
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    print("=== 咨询师工作台完整功能测试 ===\n")

    # 1. Login as counselor
    print("1. 咨询师登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    if login_resp.status_code != 200:
        print(f"❌ 登录失败: {login_resp.status_code}")
        return

    result = login_resp.json()
    if result.get("code") != 200:
        print(f"❌ 登录失败: {result}")
        return

    token = result["data"]["token"]
    user_info = result["data"]["userInfo"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"✅ 登录成功: {user_info['nickname']} (角色: {user_info['role']})")

    # 2. Get counselor info
    print("\n2. 获取咨询师信息...")
    status_resp = requests.get(f"{BASE_URL}/api/counselor/application/status", headers=headers)
    if status_resp.status_code == 200:
        status_data = status_resp.json()
        if status_data.get('code') == 200:
            counselor_id = status_data['data']['counselor_id']
            print(f"✅ 咨询师ID: {counselor_id}")
    else:
        print(f"❌ 获取咨询师信息失败")
        return

    # 3. Get orders
    print("\n3. 获取咨询师订单...")
    orders_resp = requests.get(f"{BASE_URL}/api/consultation/counselor/orders", headers=headers)
    if orders_resp.status_code == 200:
        orders_data = orders_resp.json()
        if orders_data.get('code') == 200:
            orders = orders_data['data']['items']
            print(f"✅ 订单数量: {orders_data['data']['total']} 个")

            # 4. Test messages API for confirmed orders
            print("\n4. 测试咨询对话API...")
            confirmed_orders = [o for o in orders if o['status'] == 'confirmed']
            if confirmed_orders:
                test_order = confirmed_orders[0]
                order_id = test_order['id']
                print(f"测试订单 ID: {order_id}")

                msg_resp = requests.get(
                    f"{BASE_URL}/api/consultation/{order_id}/messages",
                    headers=headers
                )

                print(f"   API状态码: {msg_resp.status_code}")
                if msg_resp.status_code == 200:
                    msg_data = msg_resp.json()
                    if msg_data.get('code') == 200:
                        messages = msg_data['data']['items']
                        print(f"✅ 成功获取消息: {len(messages)} 条")
                        print(f"   总消息数: {msg_data['data']['total']}")
                    else:
                        print(f"❌ API错误: {msg_data}")
                else:
                    error_data = msg_resp.json()
                    print(f"❌ API失败: {error_data.get('detail', 'Unknown error')}")
            else:
                print("⚠️  没有已确认的订单可测试")
    else:
        print(f"❌ 获取订单失败: {orders_resp.status_code}")

    print("\n=== 测试完成 ===")
    print("\n📱 前端测试步骤:")
    print("1. 访问: http://localhost:5177/login")
    print("2. 使用咨询师账号登录: teacher_wang@example.com / 123456")
    print("3. 访问订单管理: http://localhost:5177/consultation/counselor/orders")
    print("4. 点击已确认订单的'进入咨询'按钮")
    print("5. 应该能正常打开对话页面")

if __name__ == "__main__":
    test_complete_workflow()
