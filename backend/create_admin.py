import pymysql
import bcrypt

# Database connection
connection = pymysql.connect(
    host='localhost',
    port=3307,
    user='root',
    password='123456',
    database='soulstation'
)

try:
    with connection.cursor() as cursor:
        # Hash the password
        password = "admin123"
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        password_hash = hashed.decode('utf-8')

        # Insert using correct column names from the actual schema
        sql = """
            INSERT INTO users (email, password_hash, nickname, role, is_verified, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            'admin@soulstation.com',
            password_hash,
            'Super Admin',
            'admin',
            1,  # is_verified
            'active'
        ))

        connection.commit()
        print("Admin account created successfully!")
        print("Email: admin@soulstation.com")
        print("Password: admin123")
        print("User ID:", cursor.lastrowid)

finally:
    connection.close()
