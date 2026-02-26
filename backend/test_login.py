"""
测试后端登录功能
"""
import requests

BASE_URL = "http://localhost:8000/api"

def test_login():
    """测试登录接口"""
    print("=" * 50)
    print("测试登录接口")
    print("=" * 50)

    # 测试数据
    login_data = {
        "email": "test@example.com",
        "password": "123456"
    }

    print(f"\n发送登录请求: {login_data}")

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

        print(f"\n状态码: {response.status_code}")
        print(f"响应内容:")
        print(response.json())

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                token = data["data"]["token"]
                print(f"\n✓ 登录成功!")
                print(f"Token: {token[:50]}...")
                return token
            else:
                print(f"\n✗ 登录失败: {data.get('message')}")
        else:
            print(f"\n✗ 请求失败: {response.text}")

    except Exception as e:
        print(f"\n✗ 错误: {e}")

    return None


def test_get_user_info(token):
    """测试获取用户信息接口"""
    print("\n" + "=" * 50)
    print("测试获取用户信息接口")
    print("=" * 50)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(f"{BASE_URL}/auth/user-info", headers=headers)

        print(f"\n状态码: {response.status_code}")
        print(f"响应内容:")
        print(response.json())

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print(f"\n✓ 获取用户信息成功!")
                print(f"用户: {data['data']['nickname']} ({data['data']['email']})")
            else:
                print(f"\n✗ 获取失败: {data.get('message')}")
        else:
            print(f"\n✗ 请求失败: {response.text}")

    except Exception as e:
        print(f"\n✗ 错误: {e}")


def test_send_code():
    """测试发送验证码接口"""
    print("\n" + "=" * 50)
    print("测试发送验证码接口")
    print("=" * 50)

    data = {
        "email": "test@example.com"
    }

    print(f"\n发送验证码请求: {data}")

    try:
        response = requests.post(f"{BASE_URL}/auth/send-code", json=data)

        print(f"\n状态码: {response.status_code}")
        print(f"响应内容:")
        print(response.json())

        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                print(f"\n✓ 验证码已发送!")
                if "code" in data.get("data", {}):
                    print(f"验证码: {data['data']['code']} (开发环境)")
            else:
                print(f"\n✗ 发送失败: {data.get('message')}")
        else:
            print(f"\n✗ 请求失败: {response.text}")

    except Exception as e:
        print(f"\n✗ 错误: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("SoulStation 后端登录功能测试")
    print("=" * 50)
    print(f"\n后端地址: {BASE_URL}")
    print("\n确保后端服务正在运行！")
    print("\n按回车键开始测试...")
    input()

    # 测试登录
    token = test_login()

    # 如果登录成功，测试获取用户信息
    if token:
        test_get_user_info(token)

    # 测试发送验证码
    test_send_code()

    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
