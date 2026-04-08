"""
SoulStation 测试数据生成脚本
创建各种测试数据以展示系统功能
"""
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.counselor import Counselor, Appointment, ConsultationReview
from app.models.knowledge import KnowledgeArticle, KnowledgeComment, KnowledgeLike, KnowledgeFavorite
from app.models.chat import ChatDialogue, ChatMessage, ChatTag, ChatDialogueTag
from app.models.test import PsychologicalTest, TestResult


def create_users():
    """创建测试用户"""
    print("\n" + "="*60)
    print("正在创建测试用户...")
    print("="*60)

    db = SessionLocal()
    try:
        users_data = [
            {
                "email": "xiaoming@example.com",
                "nickname": "小明同学",
                "gender": "secret",
                "role": "user",
                "phone": "13800138001"
            },
            {
                "email": "xiaohong@example.com",
                "nickname": "小红同学",
                "gender": "female",
                "role": "user",
                "phone": "13800138002"
            },
            {
                "email": "david@example.com",
                "nickname": "David",
                "gender": "male",
                "role": "user",
                "phone": "13800138003"
            },
            {
                "email": "lucy@example.com",
                "nickname": "Lucy",
                "gender": "female",
                "role": "user",
                "phone": "13800138004"
            },
            {
                "email": "teacher_wang@example.com",
                "nickname": "王老师",
                "gender": "male",
                "role": "counselor",
                "phone": "13800138005"
            }
        ]

        created_count = 0
        for user_data in users_data:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    password_hash=get_password_hash("123456"),
                    nickname=user_data["nickname"],
                    gender=user_data["gender"],
                    role=user_data["role"],
                    phone=user_data["phone"],
                    status="active",
                    is_verified=True
                )
                db.add(user)
                created_count += 1

        db.commit()
        print(f"[SUCCESS] Created {created_count} new users")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create users: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_counselors():
    """创建更多咨询师数据"""
    print("\n" + "="*60)
    print("正在创建咨询师数据...")
    print("="*60)

    db = SessionLocal()
    try:
        # 获取有咨询师角色的用户
        counselor_users = db.query(User).filter(User.role == "counselor").all()

        if not counselor_users:
            print("没有找到咨询师角色用户，跳过")
            return True

        created_count = 0
        for user in counselor_users:
            existing = db.query(Counselor).filter(Counselor.user_id == user.id).first()
            if not existing:
                counselor = Counselor(
                    user_id=user.id,
                    name=user.nickname,
                    gender=random.choice(["male", "female"]),
                    title=random.choice(["资深心理咨询师", "婚姻家庭咨询师", "青少年心理专家", "EAP企业咨询师"]),
                    specialties=random.choice(["焦虑抑郁,情绪管理", "婚姻咨询,情感问题", "青少年心理,学习压力", "职场压力,职业规划"]),
                    consultation_types=random.choice(["video,voice", "video,voice,offline"]),
                    experience_years=random.randint(5, 15),
                    education=random.choice(["北京师范大学心理学硕士", "北京大学心理学博士", "华东师范大学心理学硕士", "复旦大学心理学博士"]),
                    qualifications="国家二级心理咨询师",
                    price_video=random.choice([300, 400, 500, 600]),
                    price_voice=random.choice([200, 250, 300, 400]),
                    price_offline=random.choice([500, 600, 700, 800, 1000]),
                    rating=round(random.uniform(4.0, 5.0), 1),
                    review_count=random.randint(0, 50),
                    consultation_count=random.randint(0, 100),
                    bio=f"{user.nickname}拥有丰富的心理咨询经验，擅长帮助来访者解决心理困扰。",
                    approach="认知行为疗法、人本主义疗法",
                    achievements="年度优秀咨询师",
                    status="active",
                    is_verified=True,
                    application_status="approved"
                )
                db.add(counselor)
                created_count += 1

        db.commit()
        print(f"[SUCCESS] Created {created_count} new counselors")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create counselors: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_knowledge_articles():
    """创建心理知识文章"""
    print("\n" + "="*60)
    print("正在创建心理知识文章...")
    print("="*60)

    db = SessionLocal()
    try:
        articles_data = [
            {
                "title": "如何缓解工作压力？",
                "summary": "工作压力是现代人常见的问题，本文将介绍几种有效的压力缓解方法。",
                "content": """
# 如何缓解工作压力？

工作压力是现代人常见的问题，长期的工作压力可能导致焦虑、抑郁等心理问题。以下是一些有效的压力缓解方法：

## 1. 时间管理
- 制定合理的工作计划
- 学会优先处理重要任务
- 避免过度承诺

## 2. 放松技巧
- 深呼吸练习
- 渐进性肌肉放松
- 正念冥想

## 3. 生活方式调整
- 保持规律作息
- 适量运动
- 健康饮食

## 4. 寻求支持
- 与家人朋友沟通
- 寻求专业心理咨询
- 参加支持小组

如果压力严重影响生活质量，建议及时寻求专业心理咨询师的帮助。
                """,
                "category": "stress",
                "tags": ["压力管理", "职场健康", "自我调节"],
                "cover_image": None,
                "author_id": 1,
                "is_published": True,
                "view_count": random.randint(100, 1000),
                "like_count": random.randint(10, 100)
            },
            {
                "title": "认识焦虑：当你感到焦虑时该怎么办",
                "summary": "焦虑是一种正常的情绪反应，但过度焦虑可能影响生活质量。了解焦虑的成因和应对方法。",
                "content": """
# 认识焦虑：当你感到焦虑时该怎么办

焦虑是一种正常的情绪反应，适度的焦虑有助于我们应对挑战。但当焦虑过度时，可能会影响生活质量。

## 什么是焦虑症？
焦虑症是一种常见的心理障碍，主要表现为：
- 过度担忧
- 肌肉紧张
- 注意力难以集中
- 睡眠问题

## 如何应对焦虑？

### 1. 认知重构
挑战负面思维，培养积极的思维模式。

### 2. 放松训练
练习深呼吸、渐进性肌肉放松等技巧。

### 3. 生活方式
- 规律运动
- 充足睡眠
- 减少咖啡因摄入

### 4. 寻求专业帮助
如果焦虑症状严重，建议及时寻求心理咨询师的帮助。
                """,
                "category": "anxiety",
                "tags": ["焦虑", "情绪管理", "心理健康"],
                "cover_image": None,
                "author_id": 1,
                "is_published": True,
                "view_count": random.randint(100, 1000),
                "like_count": random.randint(10, 100)
            },
            {
                "title": "建立健康的人际关系",
                "summary": "良好的人际关系对心理健康至关重要。学习如何建立和维护健康的人际关系。",
                "content": """
# 建立健康的人际关系

良好的人际关系对心理健康至关重要。健康的人际关系能带来支持感和归属感。

## 健康人际关系的特征
- 相互尊重
- 诚实沟通
- 边界清晰
- 互相支持

## 如何建立健康的人际关系？

### 1. 提升沟通技巧
- 学会倾听
- 表达清晰
- 保持同理心

### 2. 设定健康边界
- 明确自己的需求
- 学会说不
- 尊重他人的边界

### 3. 培养信任
- 言行一致
- 保持诚实
- 给予支持

良好的人际关系需要时间和努力来建立，但带来的心理健康益处是值得的。
                """,
                "category": "relationship",
                "tags": ["人际关系", "沟通技巧", "心理健康"],
                "cover_image": None,
                "author_id": 1,
                "is_published": True,
                "view_count": random.randint(100, 1000),
                "like_count": random.randint(10, 100)
            }
        ]

        created_count = 0
        for article_data in articles_data:
            existing = db.query(KnowledgeArticle).filter(KnowledgeArticle.title == article_data["title"]).first()
            if not existing:
                article = KnowledgeArticle(
                    title=article_data["title"],
                    summary=article_data["summary"],
                    content=article_data["content"],
                    category=article_data["category"],
                    tags=",".join(article_data["tags"]),
                    cover_image=article_data["cover_image"],
                    author_id=article_data["author_id"],
                    status="published" if article_data["is_published"] else "draft",
                    view_count=article_data["view_count"],
                    like_count=article_data["like_count"],
                    comment_count=0,
                    favorite_count=0
                )
                db.add(article)
                created_count += 1

        db.commit()
        print(f"[SUCCESS] Created {created_count} knowledge articles")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create knowledge articles: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_appointments():
    """创建预约订单"""
    print("\n" + "="*60)
    print("正在创建预约订单...")
    print("="*60)

    db = SessionLocal()
    try:
        # 获取用户和咨询师
        users = db.query(User).filter(User.role == "user").limit(5).all()
        counselors = db.query(Counselor).filter(Counselor.status == "active").all()[:3]

        if not users or not counselors:
            print("用户或咨询师数据不足，跳过")
            return True

        created_count = 0
        statuses = ["completed", "cancelled", "confirmed"]

        for user in users:
            for counselor in counselors[:2]:  # 每个用户预约2个咨询师
                # 检查是否已存在预约
                existing = db.query(Appointment).filter(
                    Appointment.user_id == user.id,
                    Appointment.counselor_id == counselor.id
                ).first()

                if not existing:
                    appointment_time = datetime.now() + timedelta(days=random.randint(1, 30))
                    appointment = Appointment(
                        user_id=user.id,
                        counselor_id=counselor.id,
                        appointment_date=appointment_time,
                        consultation_type=random.choice(["video", "voice"]),
                        duration=60,
                        status=random.choice(statuses),
                        price=counselor.price_video if random.choice([True, False]) else counselor.price_voice,
                        problem_description="希望咨询关于情绪管理的问题"
                    )
                    db.add(appointment)
                    created_count += 1

        db.commit()
        print(f"[SUCCESS] Created {created_count} appointments")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create appointments: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_reviews():
    """创建咨询评价"""
    print("\n" + "="*60)
    print("正在创建咨询评价...")
    print("="*60)

    db = SessionLocal()
    try:
        # 获取已完成的预约
        completed_appointments = db.query(Appointment).filter(
            Appointment.status == "completed"
        ).all()

        if not completed_appointments:
            print("没有已完成的预约，跳过创建评价")
            return True

        review_texts = [
            "非常专业的咨询，帮助我理清了思路。",
            "咨询师很有耐心，让我感到很舒服。",
            "咨询效果很好，问题得到了明显改善。",
            "专业、温暖、有效，强烈推荐！",
            "感谢咨询师的帮助，我现在感觉好多了。"
        ]

        created_count = 0
        for appointment in completed_appointments:
            # 检查是否已存在评价
            existing = db.query(ConsultationReview).filter(
                ConsultationReview.appointment_id == appointment.id
            ).first()

            if not existing:
                review = ConsultationReview(
                    appointment_id=appointment.id,
                    user_id=appointment.user_id,
                    counselor_id=appointment.counselor_id,
                    rating=random.randint(4, 5),
                    content=random.choice(review_texts),
                    tags="专业,耐心,有效",
                    is_anonymous=random.choice([True, False])
                )
                db.add(review)

                # 更新咨询师评价数
                counselor = db.query(Counselor).get(appointment.counselor_id)
                if counselor:
                    counselor.review_count += 1
                    counselor.rating = round((counselor.rating * (counselor.review_count - 1) + review.rating) / counselor.review_count, 1)

                created_count += 1

        db.commit()
        print(f"[SUCCESS] Created {created_count} reviews")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create reviews: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_chat_dialogues():
    """创建聊天对话记录"""
    print("\n" + "="*60)
    print("正在创建聊天对话记录...")
    print("="*60)

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.role == "user").limit(3).all()

        if not users:
            print("用户数据不足，跳过")
            return True

        # 创建一些对话标签
        tags_data = ["情绪困扰", "工作压力", "人际关系", "自我成长"]
        created_tags = []

        for tag_name in tags_data:
            existing_tag = db.query(ChatTag).filter(
                ChatTag.name == tag_name,
                ChatTag.user_id == users[0].id
            ).first()
            if not existing_tag:
                tag = ChatTag(user_id=users[0].id, name=tag_name, color=random.choice(["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"]))
                db.add(tag)
                created_tags.append(tag)

        db.commit()

        # 为每个用户创建对话
        created_count = 0
        for user in users:
            # 创建对话
            dialogue = ChatDialogue(
                user_id=user.id,
                title=random.choice(["关于工作压力的咨询", "情绪困扰咨询", "人际关系问题", "自我探索"]),
                is_anonymous=random.choice([True, False]),
                message_count=random.randint(5, 20)
            )
            db.add(dialogue)
            db.flush()

            # 创建消息
            messages = [
                "您好，我最近感到很焦虑，特别是工作方面。",
                "我理解你的感受。能具体说说是什么让你感到焦虑吗？",
                "主要是工作压力太大，领导要求很高，我感觉自己做得不够好。",
                "这种感受很常见。你觉得这种压力主要来自哪里？",
                "可能是我对自己的要求太高，总想做到完美。",
                "能够意识到这一点已经是很好的开始了。完美主义确实会给我们带来很大压力。"
            ]

            for i, content in enumerate(messages):
                is_user = i % 2 == 0
                message = ChatMessage(
                    dialogue_id=dialogue.id,
                    role="user" if is_user else "assistant",
                    content=content,
                    is_voice=False,
                    voice_duration=None
                )
                db.add(message)

            # 添加标签
            if created_tags:
                dialogue_tag = ChatDialogueTag(
                    dialogue_id=dialogue.id,
                    tag_id=random.choice(created_tags).id
                )
                db.add(dialogue_tag)

            created_count += 1

        db.commit()
        print(f"[SUCCESS] Created {created_count} chat dialogues")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create chat dialogues: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_test_results():
    """创建心理测试结果"""
    print("\n" + "="*60)
    print("正在创建心理测试结果...")
    print("="*60)

    db = SessionLocal()
    try:
        users = db.query(User).filter(User.role == "user").limit(3).all()
        tests = db.query(PsychologicalTest).filter(PsychologicalTest.is_active == True).all()[:3]

        if not users or not tests:
            print("用户或测试数据不足，跳过")
            return True

        created_count = 0
        for user in users:
            for test in tests:
                # 检查是否已存在测试结果
                existing = db.query(TestResult).filter(
                    TestResult.user_id == user.id,
                    TestResult.test_id == test.id
                ).first()

                if not existing:
                    # 模拟测试结果
                    total_score = random.randint(30, 70)

                    result = TestResult(
                        user_id=user.id,
                        test_id=test.id,
                        total_score=total_score,
                        dimension_scores={},
                        result_level=random.choice(["mild", "moderate", "severe"]),
                        result_detail="根据您的作答情况，建议您关注心理健康。",
                        answers={},
                        completion_time=random.randint(300, 900),
                        is_anonymous=random.choice([True, False])
                    )
                    db.add(result)
                    created_count += 1

        db.commit()
        print(f"[SUCCESS] Created {created_count} test results")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create test results: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """主函数"""
    print("\n" + "="*60)
    print("SoulStation 测试数据生成")
    print("="*60)

    functions = [
        ("创建用户", create_users),
        ("创建咨询师", create_counselors),
        ("创建知识文章", create_knowledge_articles),
        ("创建预约订单", create_appointments),
        ("创建咨询评价", create_reviews),
        ("创建聊天记录", create_chat_dialogues),
        ("创建测试结果", create_test_results)
    ]

    success_count = 0
    for name, func in functions:
        try:
            if func():
                success_count += 1
        except Exception as e:
            print(f"[ERROR] Error in {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print(f"测试数据生成完成！成功: {success_count}/{len(functions)}")
    print("="*60)

    print("\n测试账号信息:")
    print("-" * 40)
    print("普通用户:")
    for email in ["xiaoming@example.com", "xiaohong@example.com", "david@example.com"]:
        print(f"  邮箱: {email}")
        print(f"  密码: 123456")
    print("\n咨询师:")
    print(f"  邮箱: teacher_wang@example.com")
    print(f"  密码: 123456")
    print("-" * 40)


if __name__ == "__main__":
    main()