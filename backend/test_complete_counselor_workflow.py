#!/usr/bin/env python3
"""
Complete test for counselor workflow: login → get orders → access chat → send message
"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_complete_counselor_workflow():
    print("=== 咨询师完整工作流程测试 ===\n")

    # 1. 咨询师登录
    print("1. 咨询师登录...")
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    if login_resp.status_code != 200:
        print(f"❌ 登录失败")
        return False

    result = login_resp.json()
    if result.get("code") != 200:
        print(f"❌ 登录失败: {result}")
        return False

    token = result["data"]["token"]
    user_info = result["data"]["userInfo"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"✅ 登录成功: {user_info['nickname']} (ID: {user_info['id']}, 角色: {user_info['role']})")

    # 2. 获取咨询师ID
    status_resp = requests.get(f"{BASE_URL}/api/counselor/application/status", headers=headers)
    if status_resp.status_code == 200:
        status_data = status_resp.json()
        counselor_id = status_data["data"]["counselor_id"]
        print(f"✅ 咨询师ID: {counselor_id}")
    else:
        print(f"❌ 获取咨询师ID失败")
        return False

    # 3. 获取已确认订单
    print("\n2. 获取已确认订单...")
    orders_resp = requests.get(
        f"{BASE_URL}/api/consultation/counselor/orders",
        headers=headers,
        params={"status_filter": "confirmed", "page": 1, "pageSize": 10}
    )

    if orders_resp.status_code != 200:
        print(f"❌ 获取订单失败: {orders_resp.status_code}")
        return False

    orders_data = orders_resp.json()
    if orders_data.get('code') != 200:
        print(f"❌ 获取订单失败: {orders_data}")
        return False

    orders = orders_data['data']['items']
    print(f"✅ 已确认订单数量: {len(orders)}")

    if not orders:
        print("⚠️  没有已确认的订单")
        return False

    # 显示订单列表
    for order in orders:
        print(f"   订单ID: {order['id']}, 用户: {order.get('user_name', 'N/A')}, 状态: {order['status']}")

    # 4. 访问第一个订单的聊天
    test_order = orders[0]
    order_id = test_order['id']
    print(f"\n3. 访问订单 {order_id} 的聊天...")

    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/{order_id}/messages",
        headers=headers
    )

    print(f"   API状态码: {msg_resp.status_code}")
    if msg_resp.status_code != 200:
        error = msg_resp.json()
        print(f"❌ 访问失败: {error.get('detail', 'Unknown error')}")
        return False

    msg_data = msg_resp.json()
    if msg_data.get('code') != 200:
        print(f"❌ API错误: {msg_data}")
        return False

    print(f"✅ 成功访问对话，当前消息数: {msg_data['data']['total']}")

    # 5. 发送测试消息
    print(f"\n4. 发送测试消息...")
    send_resp = requests.post(
        f"{BASE_URL}/api/consultation/{order_id}/message",
        headers=headers,
        json={"content": "你好，我是咨询师，准备开始咨询。", "type": "text"}
    )

    print(f"   API状态码: {send_resp.status_code}")
    if send_resp.status_code != 200:
        error = send_resp.json()
        print(f"❌ 发送失败: {error.get('detail', 'Unknown error')}")
        return False

    send_data = send_resp.json()
    if send_data.get('code') != 200:
        print(f"❌ 发送失败: {send_data}")
        return False

    print(f"✅ 消息发送成功")

    # 6. 再次获取消息验证
    print(f"\n5. 验证消息已保存...")
    msg_resp2 = requests.get(
        f"{BASE_URL}/api/consultation/{order_id}/messages",
        headers=headers
    )

    if msg_resp2.status_code == 200:
        msg_data2 = msg_resp2.json()
        if msg_data2.get('code') == 200:
            new_total = msg_data2['data']['total']
            print(f"✅ 消息总数: {new_total}")
            if new_total > 0:
                print(f"✅ 消息已成功保存")

    print("\n" + "="*50)
    print("✅ 咨询师完整工作流程测试通过！")
    print("="*50)
    print("\n📱 前端操作指南:")
    print(f"1. 访问: http://localhost:5177/login")
    print("2. 使用咨询师账号登录: teacher_wang@example.com / 123456")
    print("3. 进入工作台: http://localhost:5177/consultation/counselor/orders")
    print("4. 点击'已确认'标签页")
    print(f"5. 应该看到订单ID: {order_id}，用户: {test_order.get('user_name', 'N/A')}")
    print("6. 点击'进入咨询'按钮")
    print("7. 应该能正常打开聊天并发送消息")

    return True

if __name__ == "__main__":
    success = test_complete_counselor_workflow()
    if not success:
        print("\n❌ 测试失败，请检查错误信息")
        sys.exit(1)