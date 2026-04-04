# -*- coding: utf-8 -*-
"""
Update test user role to counselor
Usage: conda activate soulstation && python fix_counselor_role.py
"""
import pymysql
import sys

# Database configuration (Docker MySQL)
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'soulstation',
    'charset': 'utf8mb4'
}


def update_counselor_role():
    """Update test user role to counselor"""
    connection = None
    try:
        print("="*60)
        print("Update test user role to counselor")
        print("="*60)

        # Connect to database
        print("\nConnecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Query current user info
        print("\nQuerying current user info...")
        cursor.execute(
            "SELECT id, email, nickname, role, status FROM users WHERE email = %s",
            ("test@example.com",)
        )
        result = cursor.fetchone()

        if not result:
            print("[ERROR] Test user test@example.com not found")
            print("\nAvailable users:")
            cursor.execute("SELECT id, email, nickname, role FROM users LIMIT 10")
            users = cursor.fetchall()
            if users:
                for user in users:
                    print(f"  ID: {user[0]}, Email: {user[1]}, Nickname: {user[2]}, Role: {user[3]}")
            return False

        user_id, email, nickname, role, status = result
        print(f"\nCurrent user info:")
        print(f"  ID: {user_id}")
        print(f"  Email: {email}")
        print(f"  Nickname: {nickname}")
        print(f"  Current role: {role}")
        print(f"  Status: {status}")

        if role == "counselor":
            print(f"\n[OK] User role is already counselor, no update needed")
            return True

        # Update role
        print(f"\nUpdating user role...")
        cursor.execute(
            "UPDATE users SET role = %s WHERE email = %s",
            ("counselor", "test@example.com")
        )
        connection.commit()

        print(f"\n[OK] User role updated to: counselor")

        # Verify update
        cursor.execute(
            "SELECT role FROM users WHERE email = %s",
            ("test@example.com",)
        )
        new_role = cursor.fetchone()[0]
        print(f"Verify: New role is {new_role}")

        print("\n" + "="*60)
        print("SUCCESS! Fix completed!")
        print("="*60)
        print("\nNow you can login with counselor account:")
        print("  Email: test@example.com")
        print("  Password: 123456")
        print("  Login URL: http://localhost:5173/login")
        print("\nWill redirect to counselor dashboard automatically")

        return True

    except pymysql.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        print("\nPlease check:")
        print("  1. Docker MySQL container is running")
        print("  2. Database config is correct (host, port, user, password)")
        print("  3. Database soulstation exists")
        return False

    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if connection:
            connection.close()
            print("\nDatabase connection closed")


def check_database_connection():
    """Check database connection"""
    try:
        print("Checking database connection...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"[OK] Database connected! MySQL version: {version[0]}")
        connection.close()
        return True
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        print("\nPlease check:")
        print("  1. Docker MySQL container is running: docker ps")
        print("  2. Port mapping is correct: default 3306")
        print("  3. Username and password are correct")
        return False


if __name__ == "__main__":
    # Check database connection
    if not check_database_connection():
        sys.exit(1)

    # Execute update
    success = update_counselor_role()

    sys.exit(0 if success else 1)
