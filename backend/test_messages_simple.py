#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

# Login
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "teacher_wang@example.com",
    "password": "123456"
})

if login_resp.status_code == 200:
    result = login_resp.json()
    if result.get("code") == 200:
        token = result["data"]["token"]
        user_info = result["data"]["userInfo"]

        print("User ID:", user_info.get("id"))
        print("User Role:", user_info.get("role"))

        headers = {"Authorization": f"Bearer {token}"}

        # Get counselor info
        status_resp = requests.get(f"{BASE_URL}/api/counselor/application/status", headers=headers)
        if status_resp.status_code == 200:
            status_data = status_resp.json()
            counselor_id = status_data["data"]["counselor_id"]
            print("Counselor ID:", counselor_id)

        # Get orders
        orders_resp = requests.get(f"{BASE_URL}/api/consultation/counselor/orders", headers=headers)
        if orders_resp.status_code == 200:
            orders_data = orders_resp.json()
            orders = orders_data["data"]["items"]
            print("Orders:", len(orders))

            for order in orders[:2]:
                order_id = order["id"]
                print(f"\nTesting Order ID: {order_id}")
                print(f"Counselor ID: {order['counselor_id']}")

                # Get messages
                msg_resp = requests.get(
                    f"{BASE_URL}/api/consultation/{order_id}/messages",
                    headers=headers
                )

                print(f"Status: {msg_resp.status_code}")
                if msg_resp.status_code != 200:
                    error = msg_resp.json()
                    print(f"Error: {error['detail']}")
