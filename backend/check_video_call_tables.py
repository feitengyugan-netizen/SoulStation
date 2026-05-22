"""
检查视频通话相关表是否存在
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def check_tables():
    """检查视频通话表"""
    with engine.connect() as conn:
        # 查询所有表
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]

        print("=== 数据库表列表 ===")
        for table in sorted(tables):
            print(f"- {table}")

        print(f"\n共 {len(tables)} 个表")

        # 检查视频通话表
        print("\n=== 视频通话表检查 ===")
        video_tables = ['video_call_sessions', 'video_call_events']

        for table in video_tables:
            if table in tables:
                print(f"✓ {table} 表存在")

                # 查看表结构
                desc_result = conn.execute(text(f"DESCRIBE {table}"))
                columns = desc_result.fetchall()

                print(f"  字段:")
                for col in columns:
                    print(f"    - {col[0]}: {col[1]}")
            else:
                print(f"✗ {table} 表不存在")

        # 检查appointments表的字段
        print("\n=== Appointments表字段检查 ===")
        if 'appointments' in tables:
            desc_result = conn.execute(text("DESCRIBE appointments"))
            columns = desc_result.fetchall()

            required_fields = ['call_enabled', 'last_call_id', 'call_count']
            for field in required_fields:
                exists = any(col[0] == field for col in columns)
                status = "✓" if exists else "✗"
                print(f"{status} {field}: {'存在' if exists else '不存在'}")

if __name__ == "__main__":
    check_tables()