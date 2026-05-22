"""
查询心理测试内容
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def query_psychological_tests():
    """查询心理测试内容"""
    with engine.connect() as conn:
        print("=== 心理测试内容查询 ===\n")

        # 检查表是否存在
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]

        test_tables = ['psychological_tests', 'test_questions', 'test_options']
        print("1. 心理测试表检查:")
        for table in test_tables:
            if table in tables:
                print(f"   {table}: 存在")
            else:
                print(f"   {table}: 不存在")

        # 查询心理测试列表
        print("\n2. 心理测试列表:")
        if 'psychological_tests' in tables:
            tests = conn.execute(text("""
                SELECT id, title, description, category, question_count,
                       duration_minutes, is_active, created_at
                FROM psychological_tests
                ORDER BY id
            """)).fetchall()

            if tests:
                for test in tests:
                    print(f"   测试ID: {test[0]}")
                    print(f"   标题: {test[1]}")
                    print(f"   描述: {test[2]}")
                    print(f"   分类: {test[3]}")
                    print(f"   题目数量: {test[4]}")
                    print(f"   预计时长: {test[5]}分钟")
                    print(f"   状态: {'激活' if test[6] else '未激活'}")
                    print(f"   创建时间: {test[7]}")
                    print()
            else:
                print("   暂无心理测试数据")
        else:
            print("   psychological_tests 表不存在")

        # 查询测试题目详情
        print("\n3. 测试题目详情:")
        if 'test_questions' in tables:
            questions = conn.execute(text("""
                SELECT q.id, t.title as test_name, q.question_text,
                       q.question_type, q.order_index, q.score
                FROM test_questions q
                LEFT JOIN psychological_tests t ON q.test_id = t.id
                ORDER BY q.test_id, q.order_index
                LIMIT 10
            """)).fetchall()

            if questions:
                for q in questions:
                    print(f"   题目ID: {q[0]} | 测试: {q[1]}")
                    print(f"   题目: {q[2]}")
                    print(f"   类型: {q[3]} | 顺序: {q[4]} | 分值: {q[5]}")
                    print()
            else:
                print("   暂无测试题目数据")
        else:
            print("   test_questions 表不存在")

        # 查询选项详情
        print("\n4. 测试选项详情:")
        if 'test_options' in tables:
            options = conn.execute(text("""
                SELECT o.id, q.question_text, o.option_text, o.is_correct
                FROM test_options o
                LEFT JOIN test_questions q ON o.question_id = q.id
                ORDER BY o.question_id, o.order_index
                LIMIT 15
            """)).fetchall()

            if options:
                for o in options:
                    print(f"   选项ID: {o[0]} | 题目: {o[1][:50]}...")
                    print(f"   选项: {o[2]} | 正确答案: {'是' if o[3] else '否'}")
                    print()
            else:
                print("   暂无测试选项数据")
        else:
            print("   test_options 表不存在")

        # 统计信息
        print("\n5. 数据统计:")
        if all(table in tables for table in test_tables):
            stats = conn.execute(text("""
                SELECT
                    (SELECT COUNT(*) FROM psychological_tests) as test_count,
                    (SELECT COUNT(*) FROM test_questions) as question_count,
                    (SELECT COUNT(*) FROM test_options) as option_count
            """)).fetchone()

            print(f"   测试总数: {stats[0]}")
            print(f"   题目总数: {stats[1]}")
            print(f"   选项总数: {stats[2]}")

        print("\n=== 查询完成 ===")

if __name__ == "__main__":
    query_psychological_tests()
