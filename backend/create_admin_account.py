"""
创建管理员账号
使用方法: conda activate soulstation && python create_admin_account.py
"""
from app.core.database import SessionLocal
from app.models.admin import Admin
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_account():
    """创建管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if existing_admin:
            logger.info(f"管理员账号已存在: {existing_admin.username}")
            logger.info(f"邮箱: {existing_admin.email}")
            logger.info(f"角色: {existing_admin.role}")
            logger.info(f"状态: {existing_admin.status}")
            return existing_admin

        # 创建新管理员
        admin = Admin(
            username="admin",
            password_hash=get_password_hash("123456"),  # 默认密码
            real_name="系统管理员",
            email="admin@soulstation.com",
            role="super_admin",
            status="active"
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        logger.info("✅ 管理员账号创建成功！")
        logger.info(f"用户名: {admin.username}")
        logger.info(f"密码: 123456")
        logger.info(f"邮箱: {admin.email}")
        logger.info(f"角色: {admin.role}")
        logger.info("\n⚠️  请尽快修改默认密码！")

        return admin

    except Exception as e:
        logger.error(f"❌ 创建管理员失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_account()
