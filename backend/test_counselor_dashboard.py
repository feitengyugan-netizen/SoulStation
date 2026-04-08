#!/usr/bin/env python3
"""
测试咨询师工作台API访问
"""
import requests
import json
import sys

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_counselor_login():
    print("=== 测试咨询师账号登录和订单访问 ===\n")

    # 使用咨询师账号登录
    print("1. 使用咨询师账号登录...")
    login_data = {
        "email": "teacher_wang@example.com",
        "password": "123456"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 200:
                token = result["data"]["token"]
                user_info = result["data"]["userInfo"]
                print(f"[OK] 咨询师登录成功!")
                print(f"用户: {user_info.get('nickname')} (ID: {user_info.get('id')})")
                print(f"角色: {user_info.get('role')}")
                print()

                # 2. 测试获取咨询师申请状态
                print("2. 测试获取咨询师申请状态...")
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/api/counselor/application/status", headers=headers)

                if response.status_code == 200:
                    result = response.json()
                    print(f"[OK] 获取状态成功!")
                    data = result.get('data', {})
                    print(f"是否有申请: {data.get('has_applied')}")
                    print(f"申请状态: {data.get('application_status')}")
                    print()

                    # 3. 测试获取订单列表
                    print("3. 测试获取咨询师订单列表...")
                    response = requests.get(f"{BASE_URL}/api/consultation/counselor/orders", headers=headers)

                    if response.status_code == 200:
                        result = response.json()
                        print(f"[OK] 获取订单列表成功!")
                        data = result.get('data', {})
                        print(f"总订单数: {data.get('total', 0)}")

                        items = data.get('items', [])
                        print(f"返回订单数: {len(items)}")

                        if items:
                            print("\n最近的订单:")
                            for order in items[:5]:
                                print(f"  - 订单号: {order.get('appointment_no')}")
                                print(f"    用户: {order.get('user_name')}")
                                print(f"    咨询方式: {order.get('consultation_type')}")
                                print(f"    状态: {order.get('status')}")
                                print(f"    预约日期: {order.get('appointment_date')}")
                                print(f"    创建时间: {order.get('created_at')}")
                                print()
                        else:
                            print("[WARNING] 暂无订单数据")

                        # 4. 测试不同状态的筛选
                        print("4. 测试状态筛选...")
                        for status in ["pending", "confirmed", "completed"]:
                            response = requests.get(
                                f"{BASE_URL}/api/consultation/counselor/orders",
                                params={"status_filter": status, "page": 1, "page_size": 10},
                                headers=headers
                            )
                            if response.status_code == 200:
                                result = response.json()
                                count = result.get('data', {}).get('total', 0)
                                print(f"  {status}状态: {count}个订单")

                    else:
                        print(f"[ERROR] 获取订单列表失败: {response.status_code}")
                        print(f"错误信息: {response.text}")
                else:
                    print(f"[ERROR] 获取状态失败: {response.status_code}")
                    print(f"错误信息: {response.text}")
            else:
                print(f"[ERROR] 登录失败: {result}")
        else:
            print(f"[ERROR] 登录请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")

    except Exception as e:
        print(f"[ERROR] 请求失败: {str(e)}")

    print("\n=== 测试结果总结 ===")
    print("如果看到订单数据，说明API工作正常")
    print("前端应该能够正确显示咨询师工作台的订单")
    print("\n=== 前端使用说明 ===")
    print("1. 使用咨询师账号登录: teacher_wang@example.com / 123456")
    print("2. 访问咨询师工作台: http://localhost:5173/consultation/counselor/dashboard")
    print("3. 应该能看到统计数据和最近预约列表")

if __name__ == "__main__":
    test_counselor_login()