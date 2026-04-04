"""
数据库初始化脚本（简化版，用于向后兼容）
请使用 backend/init_database.py 进行完整的数据库初始化
"""
from app.core.database import engine, Base


def init_db():
    """初始化数据库表"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")
    print("\n提示：请使用 'python backend/init_database.py' 进行完整的数据库初始化")


if __name__ == "__main__":
    init_db()
