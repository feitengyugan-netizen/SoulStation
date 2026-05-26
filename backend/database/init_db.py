"""
SoulStation 数据库初始化脚本
用法:
    python database/init_db.py              # 创建表 + 种子数据（默认）
    python database/init_db.py --schema-only # 仅创建表
    python database/init_db.py --seed-only   # 仅插入种子数据
    python database/init_db.py --reset       # 删除所有表后重新创建（危险！）
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.counselor import Counselor

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD = "123456"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_tables(drop_first: bool = False):
    """创建所有表"""
    if drop_first:
        print("[WARN]  删除所有现有表...")
        Base.metadata.drop_all(bind=engine)
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表创建完成\n")


def seed_data(db: Session):
    """插入种子数据"""
    password_hash = hash_password(PASSWORD)

    # ── 普通用户 ──
    users_data = [
        {"email": "user1@test.com", "nickname": "小明", "gender": "male",
         "phone": "13800138001", "bio": "我是一名大学生，最近感到有些焦虑。",
         "role": "user"},
        {"email": "user2@test.com", "nickname": "小红", "gender": "female",
         "phone": "13800138002", "bio": "希望在这里找到专业的心理咨询师。",
         "role": "user"},
        {"email": "user3@test.com", "nickname": "小华", "gender": "secret",
         "phone": "13800138003", "bio": "想了解自己的心理健康状况。",
         "role": "user"},
    ]

    print("【普通用户】")
    for u in users_data:
        if db.query(User).filter(User.email == u["email"]).first():
            print(f"  [SKIP] {u['email']} 已存在，跳过")
            continue
        db.add(User(password=password_hash, is_verified=True, status="active",
                    **u))
        print(f"  [OK] {u['email']} ({u['nickname']})")

    # ── 管理员 ──
    admin_email = "admin@soulstation.com"
    if not db.query(User).filter(User.email == admin_email).first():
        db.add(User(email=admin_email, password=password_hash,
                    nickname="系统管理员", role="admin",
                    is_verified=True, status="active"))
        print(f"  [OK] {admin_email} (系统管理员)")
    else:
        print(f"  [SKIP] {admin_email} 已存在，跳过")

    # ── 咨询师 ──
    counselors_data = [
        {"email": "counselor1@test.com", "nickname": "李医生",
         "counselor": {"name": "李医生", "gender": "female",
                       "title": "心理咨询师",
                       "specialties": "焦虑,抑郁,情绪管理",
                       "consultation_types": "video,voice",
                       "experience_years": 8,
                       "education": "心理学硕士",
                       "qualifications": "国家二级心理咨询师",
                       "price_video": 300, "price_voice": 200, "price_offline": 500,
                       "rating": 4.8, "review_count": 120, "consultation_count": 200,
                       "bio": "拥有8年心理咨询经验，擅长焦虑、抑郁等情绪问题的咨询。",
                       "approach": "认知行为疗法(CBT)、人本主义疗法",
                       "achievements": "帮助超过200名来访者走出心理困境",
                       "status": "active", "is_verified": True}},
        {"email": "counselor2@test.com", "nickname": "王老师",
         "counselor": {"name": "王老师", "gender": "male",
                       "title": "高级心理咨询师",
                       "specialties": "婚恋家庭,亲子关系,职业规划",
                       "consultation_types": "video,voice,offline",
                       "experience_years": 12,
                       "education": "心理学博士",
                       "qualifications": "国家二级心理咨询师、婚姻家庭咨询师",
                       "price_video": 500, "price_voice": 300, "price_offline": 800,
                       "rating": 4.9, "review_count": 280, "consultation_count": 450,
                       "bio": "12年心理咨询经验，专注于婚恋家庭、亲子关系咨询。",
                       "approach": "家庭治疗、系统式家庭治疗、沙盘疗法",
                       "achievements": "出版心理学著作3部，举办讲座100余场",
                       "status": "active", "is_verified": True}},
        {"email": "counselor3@test.com", "nickname": "张医生",
         "counselor": {"name": "张医生", "gender": "male",
                       "title": "资深心理医生",
                       "specialties": "青少年心理,学习压力,网络成瘾",
                       "consultation_types": "video,voice",
                       "experience_years": 15,
                       "education": "精神医学硕士",
                       "qualifications": "精神科医师、国家二级心理咨询师",
                       "price_video": 400, "price_voice": 250, "price_offline": 600,
                       "rating": 4.7, "review_count": 180, "consultation_count": 320,
                       "bio": "15年青少年心理咨询经验。",
                       "approach": "认知行为疗法、家庭治疗、游戏治疗",
                       "achievements": "治疗成功案例超过500例",
                       "status": "active", "is_verified": True}},
        {"email": "counselor4@test.com", "nickname": "陈老师",
         "counselor": {"name": "陈老师", "gender": "female",
                       "title": "心理咨询师",
                       "specialties": "情绪管理,压力调节,自我成长",
                       "consultation_types": "video,voice",
                       "experience_years": 6,
                       "education": "应用心理学硕士",
                       "qualifications": "国家二级心理咨询师",
                       "price_video": 300, "price_voice": 200, "price_offline": 400,
                       "rating": 4.6, "review_count": 85, "consultation_count": 150,
                       "bio": "6年心理咨询经验，温暖专业，帮助来访者实现自我成长。",
                       "approach": "人本主义疗法、正念疗法",
                       "achievements": "获得'优秀心理咨询师'称号",
                       "status": "active", "is_verified": True}},
    ]

    print("\n【咨询师】")
    for c in counselors_data:
        if db.query(User).filter(User.email == c["email"]).first():
            print(f"  [SKIP] {c['email']} 已存在，跳过")
            continue
        user = User(email=c["email"], password=password_hash,
                    nickname=c["nickname"], role="counselor",
                    is_verified=True, status="active")
        db.add(user)
        db.flush()

        cd = c["counselor"].copy()
        cd["user_id"] = user.id
        cd["application_status"] = "approved"
        db.add(Counselor(**cd))
        print(f"  [OK] {c['email']} ({cd['name']})")

    db.commit()
    print("\n[OK] 种子数据插入完成\n")

    # 统计
    print(f"  用户总数: {db.query(User).count()}")
    print(f"  咨询师数: {db.query(Counselor).count()}")
    print(f"\n所有账号密码均为: {PASSWORD}")


def main():
    parser = argparse.ArgumentParser(description="SoulStation 数据库初始化")
    parser.add_argument("--schema-only", action="store_true", help="仅创建表结构")
    parser.add_argument("--seed-only", action="store_true", help="仅插入种子数据")
    parser.add_argument("--reset", action="store_true", help="删除所有表后重建（危险）")
    args = parser.parse_args()

    if args.reset:
        confirm = input("[WARN]  将删除所有数据！确认？(yes/no): ")
        if confirm.lower() != "yes":
            print("已取消")
            return

    if args.seed_only:
        db = SessionLocal()
        try:
            seed_data(db)
        finally:
            db.close()
        return

    # 默认：创建表 + 种子数据
    create_tables(drop_first=args.reset)

    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

    print("=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
