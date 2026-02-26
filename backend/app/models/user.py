"""
用户模型
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Text, Boolean, Enum, Date
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, comment="用户ID")
    email = Column(String(255), unique=True, index=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    nickname = Column(String(100), comment="昵称")
    avatar = Column(String(500), comment="头像URL")
    gender = Column(Enum('male', 'female', 'other'), comment="性别")
    birth_date = Column(Date, comment="出生日期")
    phone = Column(String(20), comment="手机号")
    status = Column(Enum('active', 'inactive', 'banned'), default='active', comment="状态")
    is_verified = Column(Boolean, default=False, comment="邮箱是否验证")

    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_login_at = Column(DateTime, comment="最后登录时间")

    @property
    def password(self):
        """为了兼容代码，提供password属性"""
        return self.password_hash

    @password.setter
    def password(self, value):
        """为了兼容代码，提供password设置"""
        self.password_hash = value

    @property
    def role(self):
        """兼容前端需要的role字段"""
        return "user"

    @property
    def is_active(self):
        """兼容前端需要的is_active字段"""
        return self.status == "active"

    @property
    def is_banned(self):
        """兼容前端需要的is_banned字段"""
        return self.status == "banned"

    @property
    def bio(self):
        """兼容前端需要的bio字段"""
        return None

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, status={self.status})>"

