# -*- coding: utf-8 -*-
"""
修复 admins 表结构 - 添加缺失的字段
使用方法: conda activate soulstation && python fix_admin_table.py
"""
import pymysql
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'soulstation',
    'charset': 'utf8mb4'
}


def fix_admin_table():
    """添加 admins 表缺失的字段"""
    connection = None
    try:
        print("="*60)
        print("Fix Admins Table - Add Missing Columns")
        print("="*60)

        # Connect to database
        print("\nConnecting to database...")
        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Check current table structure
        print("\nChecking current table structure...")
        cursor.execute("DESCRIBE admins")
        columns = cursor.fetchall()
        print("\nCurrent columns:")
        column_names = []
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
            column_names.append(col[0])

        # Check and add real_name column
        if 'real_name' not in column_names:
            print("\n[INFO] Adding real_name column...")
            cursor.execute("""
                ALTER TABLE admins
                ADD COLUMN real_name VARCHAR(100) COMMENT 'Real name' AFTER password_hash
            """)
            connection.commit()
            print("[OK] real_name column added")
        else:
            print("\n[OK] real_name column already exists")

        # Check and add permissions column
        if 'permissions' not in column_names:
            print("\n[INFO] Adding permissions column...")
            cursor.execute("""
                ALTER TABLE admins
                ADD COLUMN permissions TEXT COMMENT 'Permission list (JSON format)' AFTER role
            """)
            connection.commit()
            print("[OK] permissions column added")
        else:
            print("\n[OK] permissions column already exists")

        # Check and add last_login_ip column
        if 'last_login_ip' not in column_names:
            print("\n[INFO] Adding last_login_ip column...")
            cursor.execute("""
                ALTER TABLE admins
                ADD COLUMN last_login_ip VARCHAR(50) COMMENT 'Last login IP' AFTER last_login_at
            """)
            connection.commit()
            print("[OK] last_login_ip column added")
        else:
            print("\n[OK] last_login_ip column already exists")

        # Check and add deleted_at column
        if 'deleted_at' not in column_names:
            print("\n[INFO] Adding deleted_at column...")
            cursor.execute("""
                ALTER TABLE admins
                ADD COLUMN deleted_at DATETIME COMMENT 'Deleted at' AFTER updated_at
            """)
            connection.commit()
            print("[OK] deleted_at column added")
        else:
            print("\n[OK] deleted_at column already exists")

        # Verify the update
        print("\nVerifying table structure...")
        cursor.execute("DESCRIBE admins")
        updated_columns = cursor.fetchall()
        print("\nUpdated columns:")
        for col in updated_columns:
            print(f"  - {col[0]} ({col[1]})")

        # Check if admin user exists
        print("\n" + "="*60)
        print("Checking admin accounts...")
        cursor.execute("SELECT id, username, email, role, status FROM admins")
        admins = cursor.fetchall()

        if admins:
            print(f"\nFound {len(admins)} admin account(s):")
            for admin in admins:
                print(f"  ID: {admin[0]}, Username: {admin[1]}, Email: {admin[2]}, Role: {admin[3]}, Status: {admin[4]}")
        else:
            print("\n[WARNING] No admin accounts found")
            print("You may need to create an admin account")

        print("\n" + "="*60)
        print("SUCCESS! Admins table fixed!")
        print("="*60)

        return True

    except pymysql.Error as e:
        print(f"\n[ERROR] Database error: {e}")
        import traceback
        traceback.print_exc()
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


if __name__ == "__main__":
    success = fix_admin_table()
    sys.exit(0 if success else 1)
