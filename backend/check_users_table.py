"""
检查用户表结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def check_users_table():
    """检查用户表结构"""
    with engine.connect() as conn:
        print("=== 用户表结构检查 ===\n")

        # 检查 users 表结构
        print("users 表结构:")
        try:
            result = conn.execute(text("DESCRIBE users"))
            columns = result.fetchall()
            for col in columns:
                print(f"   {col[0]:20} {col[1]:20}")
        except Exception as e:
            print(f"   错误: {e}")

        # 查询一些用户数据
        print("\nusers 数据示例:")
        try:
            result = conn.execute(text("SELECT * FROM users LIMIT 3"))
            rows = result.fetchall()
            if rows:
                # 获取列名
                col_names = conn.execute(text("DESCRIBE users"))
                col_names_list = [col[0] for col in col_names.fetchall()]

                for row in rows:
                    print(f"   用户: {dict(zip(col_names_list, row))}")
            else:
                print("   暂无数据")
        except Exception as e:
            print(f"   错误: {e}")

        print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_users_table()
