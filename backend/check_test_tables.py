"""
检查心理测试表结构
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def check_table_structure():
    """检查表结构"""
    with engine.connect() as conn:
        print("=== 心理测试表结构检查 ===\n")

        # 检查 psychological_tests 表结构
        print("1. psychological_tests 表结构:")
        try:
            result = conn.execute(text("DESCRIBE psychological_tests"))
            for row in result:
                print(f"   {row[0]:20} {row[1]:20} {row[2]:10} {row[3]:10} {row[4]:10} {row[5] or ''}")
        except Exception as e:
            print(f"   错误: {e}")

        # 检查 test_questions 表结构
        print("\n2. test_questions 表结构:")
        try:
            result = conn.execute(text("DESCRIBE test_questions"))
            for row in result:
                print(f"   {row[0]:20} {row[1]:20} {row[2]:10} {row[3]:10} {row[4]:10} {row[5] or ''}")
        except Exception as e:
            print(f"   错误: {e}")

        # 检查 test_options 表结构
        print("\n3. test_options 表结构:")
        try:
            result = conn.execute(text("DESCRIBE test_options"))
            for row in result:
                print(f"   {row[0]:20} {row[1]:20} {row[2]:10} {row[3]:10} {row[4]:10} {row[5] or ''}")
        except Exception as e:
            print(f"   错误: {e}")

        print("\n=== 检查完成 ===")

if __name__ == "__main__":
    check_table_structure()
