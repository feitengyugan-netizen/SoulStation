#!/usr/bin/env python3
"""
Test consultation messages API
"""
import requests
import json
import sys

# Set encoding
sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_counselor_messages():
    print("=== Test Counselor Messages API ===\n")

    # 1. Login as counselor
    print("1. Login as counselor...")
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

                print(f"Login successful!")
                print(f"User ID: {user_info.get('id')}")
                print(f"User Role: {user_info.get('role')}")

                # 2. Get counselor application status
                print("\n2. Get counselor application status...")
                headers = {"Authorization": f"Bearer {token}"}
                status_response = requests.get(f"{BASE_URL}/api/counselor/application/status", headers=headers)

                if status_response.status_code == 200:
                    status_result = status_response.json()
                    if status_result.get('code') == 200:
                        counselor_id = status_result['data'].get('counselor_id')
                        print(f"Counselor ID: {counselor_id}")

                        # 3. Get orders
                        print("\n3. Get counselor orders...")
                        orders_response = requests.get(f"{BASE_URL}/api/consultation/counselor/orders", headers=headers)

                        if orders_response.status_code == 200:
                            orders_result = orders_response.json()
                            orders = orders_result.get('data', {}).get('items', [])
                            print(f"Orders count: {len(orders)}")

                            # 4. Try to get messages for each order
                            for order in orders[:2]:  # Test first 2 orders
                                print(f"\n4. Testing messages for Order ID: {order.get('id')}")
                                print(f"   Order counselor_id: {order.get('counselor_id')}")
                                print(f"   Order status: {order.get('status')}")

                                messages_response = requests.get(
                                    f"{BASE_URL}/api/consultation/{order.get('id')}/messages",
                                    headers=headers
                                )

                                print(f"   Status Code: {messages_response.status_code}")
                                if messages_response.status_code == 200:
                                    messages_result = messages_response.json()
                                    print(f"   Messages: {len(messages_result.get('data', {}).get('list', []))} messages")
                                else:
                                    error_data = messages_response.json()
                                    print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                        else:
                            print(f"Get orders failed: {orders_response.status_code}")
                        else:
                            print(f"Application status failed: {status_response.status_code}")
                    else:
                        print(f"Login response format error: {result}")
                else:
                    print(f"Login failed: {response.status_code}")

    except Exception as e:
        print(f"Request failed: {str(e)}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_counselor_messages()
