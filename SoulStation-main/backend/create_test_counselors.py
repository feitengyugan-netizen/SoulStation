#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建测试咨询师账号
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor
from app.core.security import get_password_hash
from datetime import datetime

def create_test_counselors():
    """创建测试咨询师账号"""
    db = SessionLocal()

    try:
        # 测试咨询师数据
        counselors_data = [
            {
                "email": "counselor1@example.com",
                "password": "123456",
                "name": "王芳",
                "gender": "female",
                "title": "资深心理咨询师",
                "specialties": "焦虑抑郁,婚恋家庭,情绪管理",
                "consultation_types": "video,voice",
                "experience_years": 8,
                "education": "北京师范大学心理学硕士",
                "qualifications": "国家二级心理咨询师",
                "price_video": 300,
                "price_voice": 200,
                "price_offline": 500,
                "bio": "拥有8年心理咨询经验，擅长认知行为疗法，累计咨询时长超过3000小时。",
                "approach": "认知行为疗法(CBT)、人本主义疗法",
                "achievements": "2023年度优秀咨询师",
                "status": "active",
                "is_verified": True,
                "application_status": "approved"
            },
            {
                "email": "counselor2@example.com",
                "password": "123456",
                "name": "李明",
                "gender": "male",
                "title": "心理治疗师",
                "specialties": "青少年心理,学习压力,亲子关系",
                "consultation_types": "video,voice,offline",
                "experience_years": 12,
                "education": "北京大学心理学博士",
                "qualifications": "注册心理师、国家二级心理咨询师",
                "price_video": 500,
                "price_voice": 300,
                "price_offline": 800,
                "bio": "专注青少年心理健康12年，帮助数千个家庭重建亲子关系。",
                "approach": "家庭治疗、沙盘游戏治疗",
                "achievements": "出版专著《青少年心理成长指南》",
                "status": "active",
                "is_verified": True,
                "application_status": "approved"
            },
            {
                "email": "counselor3@example.com",
                "password": "123456",
                "name": "张静",
                "gender": "female",
                "title": "婚姻家庭咨询师",
                "specialties": "婚姻咨询,情感问题,人际关系",
                "consultation_types": "video,voice",
                "experience_years": 6,
                "education": "华东师范大学心理学硕士",
                "qualifications": "国家二级心理咨询师、婚姻家庭咨询师",
                "price_video": 400,
                "price_voice": 250,
                "price_offline": 600,
                "bio": "专注于婚姻家庭咨询，擅长夫妻关系修复和情感困扰疏导。",
                "approach": "情绪聚焦疗法(EFT)、叙事疗法",
                "achievements": "上海市心理咨询行业先进个人",
                "status": "active",
                "is_verified": True,
                "application_status": "approved"
            },
            {
                "email": "counselor4@example.com",
                "password": "123456",
                "name": "刘强",
                "gender": "male",
                "title": "EAP企业咨询师",
                "specialties": "职场压力,职业规划,团队建设",
                "consultation_types": "video,voice,offline",
                "experience_years": 15,
                "education": "清华大学MBA、中科院心理所硕士",
                "qualifications": "国际EAP协会认证咨询师、国家二级心理咨询师",
                "price_video": 600,
                "price_voice": 400,
                "price_offline": 1000,
                "bio": "15年企业EAP服务经验，服务过100+家知名企业。",
                "approach": "短期焦点解决、教练技术",
                "achievements": "中国EAP行业年度人物",
                "status": "active",
                "is_verified": True,
                "application_status": "approved"
            },
            {
                "email": "counselor5@example.com",
                "password": "123456",
                "name": "陈雪",
                "gender": "female",
                "title": "儿童心理专家",
                "specialties": "儿童心理,多动症,自闭症,学习障碍",
                "consultation_types": "video,offline",
                "experience_years": 10,
                "education": "复旦大学心理学博士",
                "qualifications": "注册心理师、游戏治疗师",
                "price_video": 450,
                "price_voice": 300,
                "price_offline": 700,
                "bio": "儿童心理治疗专家，擅长游戏治疗和艺术治疗。",
                "approach": "游戏治疗、艺术治疗、认知行为疗法",
                "achievements": "发表儿童心理相关论文20余篇",
                "status": "active",
                "is_verified": True,
                "application_status": "approved"
            }
        ]

        created_count = 0
        for data in counselors_data:
            email = data.pop("email")
            password = data.pop("password")

            # 检查邮箱是否已存在
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                print(f"跳过已存在的用户: {email}")
                continue

            # 创建用户账号（角色为counselor）
            user = User(
                email=email,
                password_hash=get_password_hash(password),
                nickname=data["name"],
                role="counselor",
                status="active"
            )
            db.add(user)
            db.flush()  # 获取user.id

            # 创建咨询师档案
            counselor = Counselor(
                user_id=user.id,
                **data
            )
            db.add(counselor)

            created_count += 1
            print(f"[OK] 创建咨询师: {data['name']} ({email})")

        db.commit()

        print(f"\n成功创建 {created_count} 个咨询师账号！")
        print("\n咨询师登录信息：")
        for i, data in enumerate(counselors_data, 1):
            print(f"{i}. {data['name']}")
            print(f"   邮箱: {data['email']}")
            print(f"   密码: 123456")
            print()

    except Exception as e:
        print(f"创建失败: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_counselors()
