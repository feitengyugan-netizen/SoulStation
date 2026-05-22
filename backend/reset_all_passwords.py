import pymysql
import bcrypt

connection = pymysql.connect(
    host='localhost',
    port=3307,
    user='root',
    password='123456',
    database='soulstation'
)

try:
    with connection.cursor() as cursor:
        # 设置统一密码：123456
        default_password = "123456"
        password_bytes = default_password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        password_hash = hashed.decode('utf-8')

        # 更新所有用户密码
        update_sql = "UPDATE users SET password_hash = %s"
        cursor.execute(update_sql, (password_hash,))
        affected_rows = cursor.rowcount

        connection.commit()
        print(f"Successfully updated passwords for {affected_rows} users")
        print(f"New password: {default_password}")

        # 显示用户列表
        cursor.execute('SELECT id, email, role FROM users ORDER BY id')
        users = cursor.fetchall()

        print("\nUser Accounts:")
        for user in users:
            print(f"ID: {user[0]:2d} | Email: {user[1]:30s} | Role: {user[2]}")

finally:
    connection.close()
