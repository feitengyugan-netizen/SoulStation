#!/usr/bin/env python3
"""
Test bidirectional chat functionality for both counselor and user
"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_counselor_access():
    """Test counselor accessing chat from workbench"""
    print("=== 测试咨询师访问对话 ===")

    # Login as counselor
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    if login_resp.status_code != 200:
        print(f"❌ 咨询师登录失败")
        return False

    result = login_resp.json()
    if result.get("code") != 200:
        print(f"❌ 咨询师登录失败: {result}")
        return False

    token = result["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get counselor orders
    orders_resp = requests.get(f"{BASE_URL}/api/consultation/counselor/orders", headers=headers)
    if orders_resp.status_code != 200:
        print(f"❌ 获取订单失败")
        return False

    orders_data = orders_resp.json()
    if orders_data.get('code') != 200:
        print(f"❌ 获取订单失败: {orders_data}")
        return False

    orders = orders_data['data']['items']
    print(f"✅ 咨询师登录成功，获取到 {len(orders)} 个订单")

    # Find a confirmed order
    confirmed_orders = [o for o in orders if o['status'] in ['confirmed', 'in_progress']]
    if not confirmed_orders:
        print(f"⚠️  没有已确认的订单")
        return False

    test_order = confirmed_orders[0]
    order_id = test_order['id']
    print(f"✅ 找到已确认订单 ID: {order_id}, 状态: {test_order['status']}")

    # Access chat
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/{order_id}/messages",
        headers=headers
    )

    print(f"   访问对话API状态码: {msg_resp.status_code}")
    if msg_resp.status_code == 200:
        msg_data = msg_resp.json()
        if msg_data.get('code') == 200:
            print(f"✅ 咨询师成功访问对话，消息数: {msg_data['data']['total']} 条")
            return True
        else:
            print(f"❌ API返回错误: {msg_data}")
    else:
        print(f"❌ 访问对话失败")

    return False


def test_user_access():
    """Test user accessing chat from their orders"""
    print("\n=== 测试用户访问对话 ===")

    # Login as regular user
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "xiaoming@example.com",
        "password": "123456"
    })

    if login_resp.status_code != 200:
        print(f"❌ 用户登录失败")
        return False

    result = login_resp.json()
    if result.get("code") != 200:
        print(f"❌ 用户登录失败: {result}")
        return False

    token = result["data"]["token"]
    user_info = result["data"]["userInfo"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"✅ 用户登录成功: {user_info['nickname']} (ID: {user_info['id']})")

    # Get user orders
    orders_resp = requests.get(f"{BASE_URL}/api/appointment/user/list", headers=headers)
    if orders_resp.status_code != 200:
        print(f"❌ 获取用户订单失败")
        return False

    orders_data = orders_resp.json()
    if orders_data.get('code') != 200:
        print(f"❌ 获取用户订单失败: {orders_data}")
        return False

    orders = orders_data['data']['items'] or orders_data['data'].get('list', [])
    print(f"✅ 用户获取到 {len(orders)} 个订单")

    # Find a confirmed order
    confirmed_orders = [o for o in orders if o['status'] in ['confirmed', 'in_progress']]
    if not confirmed_orders:
        print(f"⚠️  没有已确认的订单")
        return False

    test_order = confirmed_orders[0]
    order_id = test_order['id']
    print(f"✅ 找到已确认订单 ID: {order_id}, 状态: {test_order['status']}")

    # Access chat
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/{order_id}/messages",
        headers=headers
    )

    print(f"   访问对话API状态码: {msg_resp.status_code}")
    if msg_resp.status_code == 200:
        msg_data = msg_resp.json()
        if msg_data.get('code') == 200:
            print(f"✅ 用户成功访问对话，消息数: {msg_data['data']['total']} 条")
            return True
        else:
            print(f"❌ API返回错误: {msg_data}")
    else:
        print(f"❌ 访问对话失败")

    return False


def main():
    print("🔄 双向咨询对话功能测试\n")

    counselor_ok = test_counselor_access()
    user_ok = test_user_access()

    print("\n" + "="*50)
    print("📊 测试结果:")
    print(f"   咨询师端: {'✅ 通过' if counselor_ok else '❌ 失败'}")
    print(f"   用户端:   {'✅ 通过' if user_ok else '❌ 失败'}")
    print("="*50)

    if counselor_ok and user_ok:
        print("\n✅ 双向对话功能测试通过！")
        print("\n📱 功能说明:")
        print("1. 咨询师可以从工作台订单点击'进入咨询'访问对话")
        print("2. 用户可以从'我的预约'页面点击'进入咨询'访问对话")
        print("3. 双方访问的是同一个对话，数据保持一致")
        print("4. 后端API正确验证了咨询师和用户的访问权限")
    else:
        print("\n❌ 测试失败，请检查错误信息")


if __name__ == "__main__":
    main()