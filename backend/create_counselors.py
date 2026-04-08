"""
创建专业咨询师账号和档案
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.counselor import Counselor


def create_counselor_accounts():
    """创建咨询师账号和完整档案"""
    print("\n" + "="*60)
    print("创建专业咨询师账号...")
    print("="*60)

    db = SessionLocal()
    try:
        # 咨询师数据
        counselors_data = [
            {
                "email": "counselor_li@example.com",
                "password": "123456",
                "nickname": "李静怡",
                "gender": "female",
                "phone": "13900001001",
                # 咨询师信息
                "name": "李静怡",
                "title": "资深心理咨询师",
                "specialties": "焦虑抑郁,婚恋家庭,情绪管理,个人成长",
                "consultation_types": "video,voice,offline",
                "experience_years": 12,
                "education": "北京师范大学心理学博士",
                "qualifications": "国家二级心理咨询师,注册心理师,婚姻家庭咨询师",
                "price_video": 500,
                "price_voice": 300,
                "price_offline": 800,
                "bio": "拥有12年心理咨询经验，累计咨询时长超过5000小时。擅长认知行为疗法、情绪聚焦疗法和婚姻家庭治疗。 warm专业的工作风格帮助众多来访者走出心理困境。",
                "approach": "认知行为疗法(CBT)、情绪聚焦疗法(EFT)、沙盘游戏治疗",
                "achievements": "2023年度最佳咨询师奖、出版心理咨询相关专著3部"
            },
            {
                "email": "counselor_zhang@example.com",
                "password": "123456",
                "nickname": "张雅婷",
                "gender": "female",
                "phone": "13900001002",
                "name": "张雅婷",
                "title": "儿童心理专家",
                "specialties": "儿童心理,学习障碍,多动症,自闭症",
                "consultation_types": "video,offline",
                "experience_years": 8,
                "education": "华东师范大学心理学硕士",
                "qualifications": "国家二级心理咨询师,游戏治疗师,沙盘游戏师",
                "price_video": 450,
                "price_voice": 280,
                "price_offline": 700,
                "bio": "专注于儿童和青少年心理健康，擅长运用游戏治疗、艺术治疗和沙盘游戏与孩子工作。与孩子建立信任关系，让孩子在玩乐中表达内心世界。",
                "approach": "游戏治疗、艺术治疗、沙盘游戏、认知行为疗法",
                "achievements": "帮助300+儿童克服心理困难，获得家长一致好评"
            },
            {
                "email": "counselor_chen@example.com",
                "password": "123456",
                "nickname": "陈刚",
                "gender": "male",
                "phone": "13900001003",
                "name": "陈刚",
                "title": "EAP企业咨询师",
                "specialties": "职场压力,职业规划,团队建设,领导力发展",
                "consultation_types": "video,voice,offline",
                "experience_years": 15,
                "education": "清华大学MBA、中科院心理所硕士",
                "qualifications": "国际EAP协会认证咨询师、国家二级心理咨询师、ICF认证教练",
                "price_video": 600,
                "price_voice": 400,
                "price_offline": 1000,
                "bio": "15年企业EAP服务经验，服务过100+家知名企业。擅长帮助企业解决员工心理问题、提升团队凝聚力、促进组织健康发展。",
                "approach": "短期焦点解决、教练技术、团体辅导、危机干预",
                "achievements": "中国EAP行业年度人物、出版《职场心理健康指南》"
            },
            {
                "email": "counselor_liu@example.com",
                "password": "123456",
                "nickname": "刘雪",
                "gender": "female",
                "phone": "13900001004",
                "name": "刘雪",
                "title": "临床心理专家",
                "specialties": "抑郁症,焦虑症,创伤后应激障碍,强迫症",
                "consultation_types": "video,voice",
                "experience_years": 10,
                "education": "复旦大学心理学博士",
                "qualifications": "注册心理师、国家二级心理咨询师、认知治疗师",
                "price_video": 550,
                "price_voice": 350,
                "price_offline": None,
                "bio": "临床心理学博士，专攻抑郁、焦虑等情绪障碍的治疗。采用循证治疗方法，结合药物治疗和心理治疗，为来访者提供专业的心理帮助。",
                "approach": "认知行为疗法、正念疗法、药物治疗管理",
                "achievements": "发表SCI论文20余篇，参与多项国家级心理研究项目"
            },
            {
                "email": "counselor_wang@example.com",
                "password": "123456",
                "nickname": "王芳",
                "gender": "female",
                "phone": "13900001005",
                "name": "王芳",
                "title": "婚姻家庭咨询师",
                "specialties": "婚姻咨询,情感问题,亲子关系,家庭治疗",
                "consultation_types": "video,voice,offline",
                "experience_years": 6,
                "education": "上海交通大学心理学硕士",
                "qualifications": "国家二级心理咨询师、婚姻家庭咨询师、家庭治疗师",
                "price_video": 400,
                "price_voice": 250,
                "price_offline": 600,
                "bio": "专注于婚姻家庭咨询，擅长夫妻关系修复、情感困扰疏导、亲子关系改善。帮助众多家庭重建和谐关系，找回幸福。",
                "approach": "情绪聚焦疗法(EFT)、叙事疗法、家庭治疗、系统性家庭治疗",
                "achievements": "上海市心理咨询行业先进个人、成功处理100+婚姻家庭案例"
            },
            {
                "email": "counselor_zhao@example.com",
                "password": "123456",
                "nickname": "赵明",
                "gender": "male",
                "phone": "13900001006",
                "name": "赵明",
                "title": "青少年心理专家",
                "specialties": "青少年心理,学习压力,网络成瘾,厌学问题",
                "consultation_types": "video,voice,offline",
                "experience_years": 9,
                "education": "北京大学心理学博士",
                "qualifications": "注册心理师、国家二级心理咨询师、游戏治疗师",
                "price_video": 480,
                "price_voice": 320,
                "price_offline": 750,
                "bio": "专注青少年心理健康9年，深入理解青少年的心理特点和成长需求。擅长帮助青少年解决学习压力、网络成瘾、人际困扰等问题，是青少年信赖的心理伙伴。",
                "approach": " motivational interviewing、认知行为疗法、家庭治疗、沙盘游戏",
                "achievements": "帮助500+青少年走出心理困境，出版《青少年心理成长指南》"
            },
            {
                "email": "counselor_sun@example.com",
                "password": "123456",
                "nickname": "孙莉",
                "gender": "female",
                "phone": "13900001007",
                "name": "孙莉",
                "title": "情绪管理专家",
                "specialties": "情绪管理,压力应对,自我提升,人际关系",
                "consultation_types": "video,voice",
                "experience_years": 7,
                "education": "浙江大学心理学硕士",
                "qualifications": "国家二级心理咨询师、正念减压指导师",
                "price_video": 420,
                "price_voice": 280,
                "price_offline": None,
                "bio": "情绪管理专家，擅长帮助人们认识和管理自己的情绪，建立健康的情绪表达方式。采用正念、情绪聚焦等方法，让来访者重获情绪自由。",
                "approach": "正念疗法、情绪聚焦疗法、接纳承诺疗法(ACT)",
                "achievements": "开发实用情绪管理工具，帮助1000+来访者提升情商"
            }
        ]

        created_count = 0
        for counselor_data in counselors_data:
            # 检查用户是否已存在
            existing_user = db.query(User).filter(
                User.email == counselor_data["email"]
            ).first()

            user_id = None
            if existing_user:
                print(f"用户 {counselor_data['email']} 已存在，更新为咨询师角色")
                # 更新为咨询师角色
                existing_user.role = "counselor"
                user_id = existing_user.id
            else:
                # 创建新用户
                user = User(
                    email=counselor_data["email"],
                    password_hash=get_password_hash(counselor_data["password"]),
                    nickname=counselor_data["nickname"],
                    gender=counselor_data["gender"],
                    phone=counselor_data["phone"],
                    role="counselor",
                    status="active",
                    is_verified=True
                )
                db.add(user)
                db.flush()
                user_id = user.id
                print(f"创建用户: {counselor_data['email']}")

            # 检查咨询师档案是否已存在
            existing_counselor = db.query(Counselor).filter(
                Counselor.user_id == user_id
            ).first()

            if existing_counselor:
                print(f"咨询师 {counselor_data['name']} 的档案已存在，更新信息")
                # 更新咨询师信息
                for key, value in counselor_data.items():
                    if key not in ["email", "password", "nickname", "gender", "phone"]:
                        setattr(existing_counselor, key, value)
                existing_counselor.status = "active"
                existing_counselor.is_verified = True
                existing_counselor.application_status = "approved"
                existing_counselor.rating = round(random.uniform(4.0, 5.0), 1)
                existing_counselor.review_count = random.randint(10, 100)
                existing_counselor.consultation_count = random.randint(50, 200)
            else:
                # 创建咨询师档案
                counselor = Counselor(
                    user_id=user_id,
                    name=counselor_data["name"],
                    gender=counselor_data["gender"],
                    title=counselor_data["title"],
                    specialties=counselor_data["specialties"],
                    consultation_types=counselor_data["consultation_types"],
                    experience_years=counselor_data["experience_years"],
                    education=counselor_data["education"],
                    qualifications=counselor_data["qualifications"],
                    price_video=counselor_data["price_video"],
                    price_voice=counselor_data["price_voice"],
                    price_offline=counselor_data.get("price_offline"),
                    bio=counselor_data["bio"],
                    approach=counselor_data["approach"],
                    achievements=counselor_data["achievements"],
                    status="active",
                    is_verified=True,
                    application_status="approved",
                    rating=round(random.uniform(4.0, 5.0), 1),
                    review_count=random.randint(10, 100),
                    consultation_count=random.randint(50, 200)
                )
                db.add(counselor)
                created_count += 1
                print(f"创建咨询师档案: {counselor_data['name']}")

        db.commit()
        print(f"\n成功创建/更新 {len(counselors_data)} 个咨询师账号")

        # 显示所有活跃咨询师
        print("\n所有活跃咨询师列表:")
        active_counselors = db.query(Counselor).filter(
            Counselor.status == "active",
            Counselor.is_verified == True
        ).all()

        for i, counselor in enumerate(active_counselors, 1):
            print(f"{i}. {counselor.name} - {counselor.title}")
            print(f"   邮箱: {counselor.user.email if counselor.user else 'N/A'}")
            print(f"   专长: {counselor.specialties}")
            print(f"   价格: 视频{counselor.price_video}元/小时, 语音{counselor.price_voice}元/小时")
            print(f"   评分: {counselor.rating}⭐ ({counselor.review_count}条评价)")
            print()

        return True

    except Exception as e:
        print(f"创建咨询师失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    create_counselor_accounts()