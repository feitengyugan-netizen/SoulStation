# -*- coding: utf-8 -*-
"""
Check and fix counselor data
"""
import pymysql
import sys

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'soulstation',
    'charset': 'utf8mb4'
}


def check_and_fix_counselor():
    """Check and fix counselor data"""
    connection = None
    try:
        print("="*60)
        print("Check and Fix Counselor Data")
        print("="*60)

        connection = pymysql.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Check users table
        print("\nChecking users table...")
        cursor.execute("SELECT id, email, nickname, role FROM users")
        users = cursor.fetchall()
        print(f"\nFound {len(users)} users:")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Nickname: {user[2]}, Role: {user[3]}")

        # Check counselors table
        print("\n" + "="*60)
        print("Checking counselors table...")
        cursor.execute("SELECT id, user_id, name, is_deleted, status FROM counselors")
        counselors = cursor.fetchall()
        print(f"\nFound {len(counselors)} counselors:")
        for counselor in counselors:
            print(f"  ID: {counselor[0]}, User ID: {counselor[1]}, Name: {counselor[2]}, Deleted: {counselor[3]}, Status: {counselor[4]}")

        # Find counselor for user_id=3
        print("\n" + "="*60)
        print("Looking for counselor records for user_id=3...")
        cursor.execute(
            "SELECT id, user_id, name, is_deleted FROM counselors WHERE user_id = 3"
        )
        counselor_for_user3 = cursor.fetchall()

        if counselor_for_user3:
            print(f"\nFound {len(counselor_for_user3)} counselor record(s) for user_id=3:")
            for c in counselor_for_user3:
                print(f"  ID: {c[0]}, User ID: {c[1]}, Name: {c[2]}, Deleted: {c[3]}")
        else:
            print("\n[WARNING] No counselor record found for user_id=3")
            print("\nThis is why you're getting '仅咨询师可访问' error!")
            print("\nLet me check if there are counselors with different user_id...")

            # Get first user's counselor records
            cursor.execute("SELECT id, user_id, name FROM counselors LIMIT 3")
            existing_counselors = cursor.fetchall()
            if existing_counselors:
                print(f"\nExisting counselors (first 3):")
                for c in existing_counselors:
                    print(f"  Counselor ID: {c[0]}, linked to User ID: {c[1]}, Name: {c[2]}")

                print("\n" + "="*60)
                print("FIX: Creating counselor record for user_id=3...")
                print("="*60)

                # Get counselor data from existing records
                cursor.execute("SELECT * FROM counselors WHERE user_id = (SELECT MIN(user_id) FROM counselors) LIMIT 1")
                template = cursor.fetchone()
                if template:
                    # Get column names
                    cursor.execute("DESCRIBE counselors")
                    columns = [col[0] for col in cursor.fetchall()]

                    # Build INSERT statement, excluding auto-increment id
                    insert_cols = [c for c in columns if c != 'id']
                    insert_stmt = f"INSERT INTO counselors ({', '.join(insert_cols)}) VALUES ("

                    # Get template values
                    cursor.execute(f"SELECT {', '.join(insert_cols)} FROM counselors WHERE user_id = (SELECT MIN(user_id) FROM counselors) LIMIT 1")
                    values = cursor.fetchone()

                    # Update user_id to 3
                    values_list = list(values)
                    user_id_idx = insert_cols.index('user_id')
                    values_list[user_id_idx] = 3

                    # Create placeholders
                    placeholders = ', '.join(['%s'] * len(values_list))
                    insert_stmt += placeholders + ")"

                    cursor.execute(insert_stmt, tuple(values_list))
                    connection.commit()

                    print("\n[OK] Created counselor record for user_id=3")

                    # Verify
                    cursor.execute("SELECT id, user_id, name FROM counselors WHERE user_id = 3")
                    new_counselor = cursor.fetchone()
                    print(f"\nNew counselor record:")
                    print(f"  ID: {new_counselor[0]}, User ID: {new_counselor[1]}, Name: {new_counselor[2]}")
                else:
                    print("[ERROR] No template counselor found")
                    return False

        print("\n" + "="*60)
        print("Check completed!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    success = check_and_fix_counselor()
    sys.exit(0 if success else 1)
