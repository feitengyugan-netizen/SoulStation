"""
更新预约表的call_enabled字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.core.database import engine

def update_appointments():
    """更新预约表的call_enabled字段"""
    with engine.connect() as conn:
        print("=== 更新预约表字段 ===\n")

        # 更新所有预约的call_enabled为True
        result = conn.execute(text("UPDATE appointments SET call_enabled = TRUE WHERE call_enabled IS NULL OR call_enabled = FALSE"))
        conn.commit()

        print(f"已更新 {result.rowcount} 个预约记录的 call_enabled 字段")

        # 检查更新结果
        check_result = conn.execute(text("SELECT id, status, consultation_type, call_enabled, call_count FROM appointments LIMIT 5"))
        appointments = check_result.fetchall()

        print("\n预约数据示例:")
        for apt in appointments:
            print(f"ID: {apt[0]}, 状态: {apt[1]}, 类型: {apt[2]}, 通话启用: {apt[3]}, 通话次数: {apt[4]}")

        print("\n=== 完成 ===")

if __name__ == "__main__":
    update_appointments()