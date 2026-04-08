#!/usr/bin/env python3
"""
Test message structure and fix display issues
"""
import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def test_message_structure():
    print("=== 检查消息API结构 ===\n")

    # Login as counselor
    login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "teacher_wang@example.com",
        "password": "123456"
    })

    token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Send a message
    print("1. 发送测试消息...")
    send_resp = requests.post(
        f"{BASE_URL}/api/consultation/4/message",
        headers=headers,
        json={"content": "测试消息 - 咨询师", "type": "text"}
    )

    print(f"   发送状态码: {send_resp.status_code}")
    if send_resp.status_code == 200:
        send_data = send_resp.json()
        print(f"   发送响应: {json.dumps(send_data, ensure_ascii=False, indent=2)}")

    # Get messages
    print("\n2. 获取消息列表...")
    msg_resp = requests.get(
        f"{BASE_URL}/api/consultation/4/messages",
        headers=headers
    )

    print(f"   获取状态码: {msg_resp.status_code}")
    if msg_resp.status_code == 200:
        msg_data = msg_resp.json()
        print(f"   完整响应: {json.dumps(msg_data, ensure_ascii=False, indent=2)}")

        if msg_data.get('code') == 200:
            messages = msg_data['data']['items']
            print(f"\n3. 消息数量: {len(messages)}")

            for msg in messages:
                print(f"\n   消息ID: {msg.get('id')}")
                print(f"   发送者ID: {msg.get('sender_id')}")
                print(f"   发送者类型: {msg.get('sender_type')}")
                print(f"   内容: {msg.get('content')}")
                print(f"   类型: {msg.get('type')}")
                print(f"   创建时间: {msg.get('created_at')}")

if __name__ == "__main__":
    test_message_structure()