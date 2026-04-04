#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试数据库连接"""

import pymysql
import sys

# 测试不同的连接配置
configs = [
    {
        "name": "localhost with password 12345",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "12345"
    },
    {
        "name": "127.0.0.1 with password 12345",
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "12345"
    },
    {
        "name": "localhost with password 123456",
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "123456"
    },
    {
        "name": "127.0.0.1 with password 123456",
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "123456"
    }
]

print("=" * 60)
print("MySQL Connection Test")
print("=" * 60)

success = False
for config in configs:
    print(f"\nTesting: {config['name']}")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  User: {config['user']}")
    print(f"  Password: {'*' * len(config['password'])}")

    try:
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            connect_timeout=5
        )
        print(f"  [SUCCESS] Connected successfully!")

        # 尝试创建数据库
        cursor = connection.cursor()
        try:
            cursor.execute("CREATE DATABASE IF NOT EXISTS soulstation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"  [SUCCESS] Database 'soulstation' created/verified")
        except Exception as e:
            print(f"  [WARNING] Could not create database: {e}")

        connection.close()
        success = True
        print(f"\n*** This configuration works! ***")
        break

    except Exception as e:
        print(f"  [FAILED] {str(e)}")

print("\n" + "=" * 60)
if success:
    print("Please update .env with the working configuration")
else:
    print("None of the configurations worked.")
    print("\nSuggestions:")
    print("1. Verify MySQL is running")
    print("2. Check root user password")
    print("3. Try using MySQL Workbench to verify credentials")
    print("4. Consider using Docker MySQL instead")
print("=" * 60)
