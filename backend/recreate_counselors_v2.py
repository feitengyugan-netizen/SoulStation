# -*- coding: utf-8 -*-
"""
重新创建咨询师账号 - 每个咨询师一个独立的登录账号
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor
from app.core.security import get_password_hash

# 咨询师数据 (每个咨询师一个独立账号)
COUNSELORS_DATA = [
    {
        "name": "王静怡",
        "email": "counselor1@soulstation.com",
        "password": "123456",
        "phone": "13800001001",
        "gender": "female",
        "title": "国家二级心理咨询师",
        "specialties": "焦虑与抑郁,青少年心理,情绪管理",
        "consultation_types": "video,voice",
        "experience_years": 8,
        "education": "北京师范大学心理学硕士",
        "qualifications": "国家二级心理咨询师,注册心理师(XX-XXXXX)",
        "price_video": 300,
        "price_voice": 200,
        "price_offline": 500,
        "bio": "专注青少年心理咨询8年,擅长认知行为疗法,帮助数百名青少年走出心理困境。",
        "approach": "认知行为疗法(CBT)结合人本主义心理治疗",
        "achievements": "2023年度优秀心理咨询师,发表心理学论文5篇"
    },
    {
        "name": "李明远",
        "email": "counselor2@soulstation.com",
        "password": "123456",
        "phone": "13800001002",
        "gender": "male",
        "title": "资深心理治疗师",
        "specialties": "婚姻家庭,职场压力,个人成长",
        "consultation_types": "video,voice,offline",
        "experience_years": 12,
        "education": "华东师范大学心理学博士",
        "qualifications": "中国心理学会注册心理师,国家二级心理咨询师",
        "price_video": 500,
        "price_voice": 300,
        "price_offline": 800,
        "bio": "从业12年,擅长婚姻家庭治疗和职场压力管理,累计咨询时长超过8000小时。",
        "approach": "系统式家庭治疗整合精神分析",
        "achievements": "中国心理学会优秀会员,出版心理咨询专著2部"
    },
    {
        "name": "张雅婷",
        "email": "counselor3@soulstation.com",
        "password": "123456",
        "phone": "13800001003",
        "gender": "female",
        "title": "儿童心理专家",
        "specialties": "儿童心理,学习障碍,亲子关系",
        "consultation_types": "video,offline",
        "experience_years": 10,
        "education": "中国科学院心理研究所硕士",
        "qualifications": "注册心理师,游戏治疗师,沙盘治疗师",
        "price_video": 400,
        "price_voice": None,
        "price_offline": 600,
        "bio": "专注于儿童青少年心理问题,擅长游戏治疗和沙盘治疗,帮助孩子建立健康的心理模式。",
        "approach": "游戏治疗整合认知行为疗法",
        "achievements": "儿童心理教育专家,市级优秀教育工作者"
    },
    {
        "name": "赵晓敏",
        "email": "counselor4@soulstation.com",
        "password": "123456",
        "phone": "13800001004",
        "gender": "female",
        "title": "情绪管理专家",
        "specialties": "抑郁与焦虑,情绪障碍,创伤疗愈",
        "consultation_types": "video,voice",
        "experience_years": 6,
        "education": "北京大学心理学硕士",
        "qualifications": "国家二级心理咨询师,EAP咨询师",
        "price_video": 350,
        "price_voice": 250,
        "price_offline": None,
        "bio": "擅长情绪管理和创伤疗愈,帮助来访者重建内在安全感,找回生活动力。",
        "approach": "EMDR眼动脱敏再加工结合正念疗法",
        "achievements": "疫情期间公益咨询超过500小时"
    },
    {
        "name": "陈建国",
        "email": "counselor5@soulstation.com",
        "password": "123456",
        "phone": "13800001005",
        "gender": "male",
        "title": "成瘾心理专家",
        "specialties": "成瘾行为,强迫症,睡眠障碍",
        "consultation_types": "video,voice,offline",
        "experience_years": 15,
        "education": "中南大学湘雅医学院博士",
        "qualifications": "精神科医师,国家二级心理咨询师",
        "price_video": 450,
        "price_voice": 350,
        "price_offline": 700,
        "bio": "医学背景的资深心理咨询师,擅长各类成瘾行为和强迫症的治疗,临床经验丰富。",
        "approach": "认知行为疗法结合药物治疗(如需要)",
        "achievements": "三甲医院心理科主任15年,主持省部级课题3项"
    },
    {
        "name": "刘思雨",
        "email": "counselor6@soulstation.com",
        "password": "123456",
        "phone": "13800001006",
        "gender": "female",
        "title": "婚恋情感专家",
        "specialties": "婚恋情感,失恋疗愈,亲密关系",
        "consultation_types": "video,voice",
        "experience_years": 7,
        "education": "复旦大学社会学系硕士",
        "qualifications": "国家二级心理咨询师,婚恋家庭指导师",
        "price_video": 380,
        "price_voice": 280,
        "price_offline": None,
        "bio": "专注于婚恋情感咨询,帮助来访者建立健康的亲密关系,找到属于自己的幸福。",
        "approach": "情绪取向疗法(EFT)结合萨提亚模式",
        "achievements": "知名婚恋平台签约专家,成功帮助上千对情侣"
    }
]

def main():
    db = SessionLocal()

    try:
        print("=" * 80)
        print("重新创建咨询师账号")
        print("=" * 80)

        # 1. 删除现有的咨询师记录
        print("\n[1/3] 删除现有咨询师记录...")
        existing_counselors = db.query(Counselor).all()
        deleted_count = len(existing_counselors)
        for counselor in existing_counselors:
            # 删除关联的用户账号(如果角色是counselor)
            if counselor.user_id:
                user = db.query(User).filter(User.id == counselor.user_id).first()
                if user and user.role == 'counselor':
                    db.delete(user)
            db.delete(counselor)

        db.commit()
        print(f"[OK] 已删除 {deleted_count} 个现有咨询师记录")

        # 2. 创建新的用户账号和咨询师档案
        print("\n[2/3] 创建新的咨询师账号...")
        created_count = 0
        for idx, counselor_data in enumerate(COUNSELORS_DATA, 1):
            # 提取账号信息
            email = counselor_data.pop("email")
            password = counselor_data.pop("password")
            phone = counselor_data.pop("phone")
            name = counselor_data["name"]

            # 创建用户账号
            user = User(
                email=email,
                password_hash=get_password_hash(password),
                nickname=name,
                phone=phone,
                gender=counselor_data["gender"],
                role="counselor",
                status="active",
                is_verified=True
            )
            db.add(user)
            db.flush()  # 获取user.id

            # 创建咨询师档案
            counselor = Counselor(
                user_id=user.id,
                **counselor_data,
                status="active",
                is_verified=True,
                application_status="approved",
                rating=5.0,
                review_count=0,
                consultation_count=0
            )
            db.add(counselor)

            created_count += 1
            print(f"  {created_count}. 创建咨询师: {name} ({email})")

        db.commit()
        print(f"\n[OK] 成功创建 {created_count} 个咨询师账号")

        # 3. 验证创建结果
        print("\n[3/3] 验证创建结果...")
        counselors = db.query(Counselor).filter(Counselor.is_deleted == False).all()
        print(f"\n当前数据库中的咨询师:")
        print("-" * 80)
        for c in counselors:
            user = db.query(User).filter(User.id == c.user_id).first()
            print(f"ID: {c.id:2d} | 姓名: {c.name:8s} | 邮箱: {user.email if user else 'N/A':30s} | 状态: {c.status}")
        print("-" * 80)
        print(f"总计: {len(counselors)} 个咨询师")

        print("\n" + "=" * 80)
        print("[OK] 咨询师账号创建完成!")
        print("=" * 80)
        print("\n咨询师登录信息:")
        print("-" * 80)
        for c in counselors:
            user = db.query(User).filter(User.id == c.user_id).first()
            print(f"姓名: {c.name:8s} | 邮箱: {user.email if user else 'N/A':30s} | 密码: 123456")
        print("-" * 80)
        print("\n提示: 所有咨询师的初始密码均为 '123456',首次登录后请及时修改")

    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
