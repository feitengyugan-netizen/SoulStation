"""
查询心理测试表结构和内容
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def query_tests():
    """查询心理测试"""
    with engine.connect() as conn:
        print("=== 心理测试查询 ===\n")

        # 查看所有表
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"数据库表: {tables}\n")

        # 查询 psychological_tests 结构和数据
        if 'psychological_tests' in tables:
            print("1. psychological_tests 表结构:")
            try:
                result = conn.execute(text("DESCRIBE psychological_tests"))
                columns = result.fetchall()
                for col in columns:
                    print(f"   {col[0]} - {col[1]}")
            except Exception as e:
                print(f"   错误: {e}")

            print("\n2. psychological_tests 数据:")
            try:
                result = conn.execute(text("SELECT * FROM psychological_tests LIMIT 5"))
                rows = result.fetchall()
                if rows:
                    # 获取列名
                    col_names = conn.execute(text("DESCRIBE psychological_tests"))
                    col_names_list = [col[0] for col in col_names.fetchall()]

                    for row in rows:
                        print(f"   记录: {dict(zip(col_names_list, row))}")
                else:
                    print("   暂无数据")
            except Exception as e:
                print(f"   错误: {e}")

        # 查询 test_questions 结构和数据
        if 'test_questions' in tables:
            print("\n3. test_questions 表结构:")
            try:
                result = conn.execute(text("DESCRIBE test_questions"))
                columns = result.fetchall()
                for col in columns:
                    print(f"   {col[0]} - {col[1]}")
            except Exception as e:
                print(f"   错误: {e}")

            print("\n4. test_questions 数据:")
            try:
                result = conn.execute(text("SELECT * FROM test_questions LIMIT 10"))
                rows = result.fetchall()
                if rows:
                    # 获取列名
                    col_names = conn.execute(text("DESCRIBE test_questions"))
                    col_names_list = [col[0] for col in col_names.fetchall()]

                    for row in rows:
                        print(f"   记录: {dict(zip(col_names_list, row))}")
                else:
                    print("   暂无数据")
            except Exception as e:
                print(f"   错误: {e}")

        # 统计信息
        print("\n5. 数据统计:")
        try:
            result = conn.execute(text("""
                SELECT
                    (SELECT COUNT(*) FROM psychological_tests) as tests,
                    (SELECT COUNT(*) FROM test_questions) as questions
            """))
            stats = result.fetchone()
            print(f"   测试数量: {stats[0]}")
            print(f"   题目数量: {stats[1]}")
        except Exception as e:
            print(f"   统计错误: {e}")

        print("\n=== 查询完成 ===")

if __name__ == "__main__":
    query_tests()
