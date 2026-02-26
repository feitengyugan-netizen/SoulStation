"""
用户相关的 Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础 Schema"""
    email: EmailStr
    nickname: Optional[str] = None


class UserCreate(UserBase):
    """用户创建 Schema"""
    password: str = Field(..., min_length=6, max_length=20)


class UserLogin(BaseModel):
    """用户登录 Schema"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """用户更新 Schema"""
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """用户响应 Schema"""
    id: int
    role: str
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token 响应 Schema"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token 数据 Schema"""
    user_id: Optional[int] = None
    email: Optional[str] = None
