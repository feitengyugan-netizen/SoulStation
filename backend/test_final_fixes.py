#!/usr/bin/env python3
"""
Final test for all fixes
"""
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_counselor_workflow():
    print("=== 测试咨询师工作流程 ===\n")

    # Login as counselor
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("1. 获取咨询师所有订单:")
    all_resp = requests.get(
        f"{BASE_URL}/api/consultation/counselor/orders",
        headers=headers,
        params={"page": 1, "pageSize": 20}
    )

    if all_resp.status_code == 200:
        data = all_resp.json()
        if data.get('code') == 200:
            all_orders = data['data']['items']
            print(f"   总订单数: {len(all_orders)}")

            confirmed = [o for o in all_orders if o['status'] == 'confirmed']
            in_progress = [o for o in all_orders if o['status'] == 'in_progress']

            print(f"   已确认订单: {len(confirmed)}个")
            print(f"   进行中订单: {len(in_progress)}个")
            print(f"   咨询中总计: {len(confirmed) + len(in_progress)}个")

    print("\n2. 模拟点击'进入咨询':")
    if confirmed or in_progress:
        test_order = confirmed[0] if confirmed else in_progress[0]
        order_id = test_order['id']

        print(f"   选择订单ID: {order_id}, 状态: {test_order['status']}")

        # 访问聊天
        msg_resp = requests.get(
            f"{BASE_URL}/api/consultation/{order_id}/messages",
            headers=headers
        )

        print(f"   访问聊天状态码: {msg_resp.status_code}")

        if msg_resp.status_code == 200:
            print("   ✅ 成功访问聊天")

            # 发送消息
            send_resp = requests.post(
                f"{BASE_URL}/api/consultation/{order_id}/message",
                headers=headers,
                json={"content": "测试消息 - 咨询师端", "type": "text"}
            )

            if send_resp.status_code == 200:
                print("   ✅ 消息发送成功")

                # 再次获取订单
                print(f"\n3. 访问聊天后再次获取订单:")

                # 获取confirmed订单
                confirmed_resp = requests.get(
                    f"{BASE_URL}/api/consultation/counselor/orders",
                    headers=headers,
                    params={"status_filter": "confirmed", "page": 1, "pageSize": 10}
                )

                # 获取in_progress订单
                progress_resp = requests.get(
                    f"{BASE_URL}/api/consultation/counselor/orders",
                    headers=headers,
                    params={"status_filter": "in_progress", "page": 1, "pageSize": 10}
                )

                if confirmed_resp.status_code == 200 and progress_resp.status_code == 200:
                    confirmed_data = confirmed_resp.json()
                    progress_data = progress_resp.json()

                    confirmed_orders = confirmed_data['data']['items'] if confirmed_data.get('code') == 200 else []
                    progress_orders = progress_data['data']['items'] if progress_data.get('code') == 200 else []

                    total_active = len(confirmed_orders) + len(progress_orders)

                    print(f"   咨询中订单总数: {total_active}")

                    # 检查原订单是否还在
                    still_in_confirmed = any(o['id'] == order_id for o in confirmed_orders)
                    still_in_progress = any(o['id'] == order_id for o in progress_orders)

                    if still_in_confirmed or still_in_progress:
                        new_status = "confirmed" if still_in_confirmed else "in_progress"
                        print(f"   ✅ 订单{order_id}仍在咨询中列表（状态: {new_status}）")
                        return True
                    else:
                        print(f"   ❌ 订单{order_id}从列表中消失")
                        return False

    return False

if __name__ == "__main__":
    print("🧪 最终测试\n")
    success = test_counselor_workflow()

    print("\n" + "="*50)
    if success:
        print("✅ 所有测试通过！")
        print("\n📱 前端使用说明:")
        print("1. 咨询师工作台现在显示'咨询中'标签")
        print("2. 该标签同时显示已确认和进行中的订单")
        print("3. 点击'进入咨询'或'继续咨询'都能正常打开聊天")
        print("4. 访问聊天后订单仍在列表中，不会消失")
        print("5. 聊天界面已重新设计，采用现代化UI")
    else:
        print("❌ 测试失败，请检查错误信息")
    print("="*50)