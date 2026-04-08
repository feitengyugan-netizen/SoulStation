#!/usr/bin/env python3
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

# Login
login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
    "email": "teacher_wang@example.com",
    "password": "123456"
})

if login_resp.status_code == 200:
    result = login_resp.json()
    token = result["data"]["token"]
    user_info = result["data"]["userInfo"]

    print("User ID:", user_info.get("id"))
    print("User Role:", user_info.get("role"))

    headers = {"Authorization": f"Bearer {token}"}

    # Get counselor ID
    status_resp = requests.get(f"{BASE_URL}/api/counselor/application/status", headers=headers)
    if status_resp.status_code == 200:
        status_data = status_resp.json()
        counselor_id = status_data["data"]["counselor_id"]
        print("Counselor ID from application status:", counselor_id)

    # Test with appointment_id=4 (confirmed order)
    print("\nTesting with appointment_id=4")
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/4/messages",
        headers=headers
    )
    print(f"Status: {msg_resp.status_code}")
    if msg_resp.status_code != 200:
        error = msg_resp.json()
        print(f"Error detail: {error['detail']}")
