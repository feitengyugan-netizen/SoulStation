"""
创建语音通话测试数据
"""
import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine
from app.models.user import User
from app.models.counselor import Counselor, Appointment
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_test_data():
    """创建测试数据"""

    # 创建数据库会话
    with Session(engine) as db:
        print("=== 创建语音通话测试数据 ===\n")

        # 1. 创建测试用户
        print("1. 创建测试用户...")
        test_users = []

        for i in range(1, 6):
            email = f"user{i}@test.com"
            existing_user = db.query(User).filter(User.email == email).first()

            if not existing_user:
                user = User(
                    email=email,
                    password_hash=pwd_context.hash("password123"),
                    nickname=f"测试用户{i}",
                    gender='male' if i % 2 == 0 else 'female',
                    status='active',
                    role='user',
                    is_verified=True
                )
                db.add(user)
                db.flush()
                test_users.append(user)
                print(f"   - 创建用户: {email}")
            else:
                test_users.append(existing_user)
                print(f"   - 用户已存在: {email}")

        # 2. 创建测试咨询师
        print("\n2. 创建测试咨询师...")
        test_counselors = []

        counselor_names = ["张医生", "李医生", "王医生", "孙医生", "赵医生"]
        specializations = ["焦虑症治疗", "抑郁症咨询", "婚姻家庭治疗", "儿童心理", "职业压力"]

        for i, (name, specialty) in enumerate(zip(counselor_names, specializations), 1):
            # 先为咨询师创建用户账号
            email = f"counselor{i}@test.com"
            user = db.query(User).filter(User.email == email).first()

            if not user:
                user = User(
                    email=email,
                    password_hash=pwd_context.hash("password123"),
                    nickname=name,
                    gender='male' if i % 2 == 0 else 'female',
                    status='active',
                    role='counselor',
                    is_verified=True
                )
                db.add(user)
                db.flush()

            existing_counselor = db.query(Counselor).filter(Counselor.user_id == user.id).first()

            if not existing_counselor:
                counselor = Counselor(
                    user_id=user.id,
                    name=name,
                    title=f"心理咨询师{i}级",
                    specialties=specialty,
                    consultation_types="video,voice",
                    experience_years=random.randint(3, 15),
                    education="心理学硕士",
                    qualifications="国家二级心理咨询师",
                    price_video=random.randint(200, 500),
                    price_voice=random.randint(150, 400),
                    rating=round(random.uniform(4.0, 5.0), 1),
                    review_count=random.randint(10, 100),
                    consultation_count=random.randint(50, 200),
                    bio=f"专业{specialty}，拥有{random.randint(3, 15)}年临床经验。",
                    status='active',
                    is_verified=True
                )
                db.add(counselor)
                db.flush()
                test_counselors.append(counselor)
                print(f"   - 创建咨询师: {name}")
            else:
                test_counselors.append(existing_counselor)
                print(f"   - 咨询师已存在: {name}")

        # 3. 创建测试预约
        print("\n3. 创建测试预约...")
        test_appointments = []

        appointment_statuses = ['confirmed', 'in_progress', 'completed']
        consultation_types = ['video', 'voice', 'offline']

        for i in range(10):
            user = random.choice(test_users)
            counselor = random.choice(test_counselors)

            # 生成未来几天的预约时间
            appointment_date = datetime.now() + timedelta(days=random.randint(1, 30))
            appointment_date = appointment_date.replace(hour=random.randint(9, 17), minute=0, second=0, microsecond=0)

            appointment_no = f"APT{datetime.now().strftime('%Y%m%d%H%M%S')}{i:03d}"

            # 根据咨询类型设置价格
            consultation_type = random.choice(consultation_types)
            if consultation_type == 'video':
                price = counselor.price_video
            elif consultation_type == 'voice':
                price = counselor.price_voice
            else:
                price = counselor.price_offline if hasattr(counselor, 'price_offline') and counselor.price_offline else 300

            appointment = Appointment(
                user_id=user.id,
                counselor_id=counselor.id,
                appointment_no=appointment_no,
                consultation_type=consultation_type,
                appointment_date=appointment_date,
                duration=60,  # 1小时
                user_name=user.nickname,
                user_contact=user.phone or "13800138000",
                problem_description=f"测试咨询问题{i}",
                price=price,
                paid_amount=price,  # 假设已支付
                status=random.choice(appointment_statuses),
                call_enabled=True,  # 启用通话功能
                call_count=0
            )

            db.add(appointment)
            db.flush()
            test_appointments.append(appointment)
            print(f"   - 创建预约: {appointment_no} ({consultation_type}) - {user.nickname} -> {counselor.name}")

        # 提交所有更改
        db.commit()

        print(f"\n✅ 测试数据创建完成!")
        print(f"   - 用户数量: {len(test_users)}")
        print(f"   - 咨询师数量: {len(test_counselors)}")
        print(f"   - 预约数量: {len(test_appointments)}")

        # 显示一些测试账号信息
        print(f"\n📝 测试账号信息:")
        print(f"   普通用户账号:")
        for user in test_users[:3]:
            print(f"   - 邮箱: {user.email}, 密码: password123")

        print(f"\n   咨询师账号:")
        for counselor in test_counselors[:3]:
            counselor_user = db.query(User).filter(User.id == counselor.user_id).first()
            print(f"   - 姓名: {counselor.name}, 邮箱: {counselor_user.email}, 密码: password123")

        print("\n=== 语音通话测试数据创建完成 ===")


if __name__ == "__main__":
    create_test_data()