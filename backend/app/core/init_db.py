"""
数据库初始化脚本
"""
from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


def init_db():
    """初始化数据库表"""
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成！")


def create_test_user():
    """创建测试用户"""
    db = SessionLocal()
    try:
        # 检查是否已存在测试用户
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("测试用户已存在")
            return

        # 创建测试用户
        test_user = User(
            email="test@example.com",
            password=get_password_hash("123456"),
            nickname="测试用户",
            role="user",
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print("测试用户创建成功！")
        print("邮箱: test@example.com")
        print("密码: 123456")
    except Exception as e:
        print(f"创建测试用户失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    create_test_user()
