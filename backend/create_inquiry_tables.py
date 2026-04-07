"""创建 counselor_inquiries / inquiry_messages 表"""
import pymysql

conn = pymysql.connect(
    host='localhost', port=3306,
    user='root', password='123456',
    database='soulstation', charset='utf8mb4'
)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS counselor_inquiries (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT UNSIGNED NOT NULL,
  counselor_id BIGINT UNSIGNED NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_counselor (counselor_id),
  UNIQUE KEY uq_user_counselor (user_id, counselor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='咨询师预约前沟通会话'
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS inquiry_messages (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  inquiry_id BIGINT UNSIGNED NOT NULL,
  sender_id BIGINT UNSIGNED NOT NULL,
  sender_role ENUM('user','counselor') NOT NULL,
  content TEXT NOT NULL,
  msg_type VARCHAR(20) DEFAULT 'text',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_inquiry (inquiry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预约前沟通消息'
""")

conn.commit()
cur.execute("SHOW TABLES LIKE '%inquiry%'")
print("Created tables:", cur.fetchall())
conn.close()
