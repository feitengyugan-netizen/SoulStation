"""
SoulStation 数据库统一初始化脚本
整合所有数据库表的创建和初始数据的导入
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_all_tables():
    """创建所有数据库表"""
    print("\n" + "="*60)
    print("正在创建数据库表...")
    print("="*60)

    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)

        print("✓ 数据库表创建完成")
        print("\n已创建的表：")
        print("  - users (用户表)")
        print("  - admins (管理员表)")
        print("  - psychological_tests (心理测试表)")
        print("  - test_questions (测试题目表)")
        print("  - test_results (测试结果表)")
        print("  - test_progress (答题进度表)")
        print("  - chat_dialogues (对话记录表)")
        print("  - chat_messages (聊天消息表)")
        print("  - chat_tags (对话标签表)")
        print("  - chat_dialogue_tags (对话标签关联表)")
        print("  - counselors (咨询师表)")
        print("  - appointments (预约订单表)")
        print("  - consultation_reviews (咨询评价表)")
        print("  - consultation_messages (咨询对话消息表)")
        print("  - knowledge_articles (知识文章表)")
        print("  - knowledge_comments (知识评论表)")
        print("  - knowledge_favorites (知识收藏表)")
        print("  - knowledge_likes (知识点赞表)")
        return True
    except Exception as e:
        print(f"✗ 创建表失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_test_user():
    """创建测试用户"""
    print("\n" + "="*60)
    print("正在创建测试用户...")
    print("="*60)

    from app.models.user import User

    db = SessionLocal()
    try:
        # 检查是否已存在测试用户
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print("  测试用户已存在，跳过")
            return True

        # 创建测试用户
        test_user = User(
            email="test@example.com",
            password_hash=get_password_hash("123456"),
            nickname="测试用户",
            role="user",
            is_active=True,
            status="active"
        )
        db.add(test_user)
        db.commit()

        print("✓ 测试用户创建成功")
        print("\n测试用户登录信息:")
        print("  邮箱: test@example.com")
        print("  密码: 123456")
        return True
    except Exception as e:
        print(f"✗ 创建测试用户失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_admin_user():
    """创建管理员账号"""
    print("\n" + "="*60)
    print("正在创建管理员账号...")
    print("="*60)

    from app.models.admin import Admin

    db = SessionLocal()
    try:
        # 检查是否已有管理员
        existing = db.query(Admin).count()
        if existing > 0:
            print(f"  数据库中已有 {existing} 位管理员，跳过初始化")
            return True

        # 创建默认管理员
        default_admin = Admin(
            username="admin",
            password_hash=pwd_context.hash("admin123"),
            real_name="超级管理员",
            email="admin@soulstation.com",
            role="super_admin",
            is_active=True
        )

        db.add(default_admin)
        db.commit()

        print("✓ 管理员账号创建成功")
        print("\n管理员登录信息:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("  角色: super_admin")
        print("\n⚠️  重要提示：请在首次登录后修改默认密码！")
        return True
    except Exception as e:
        print(f"✗ 创建管理员失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_test_counselors():
    """创建测试咨询师数据"""
    print("\n" + "="*60)
    print("正在创建测试咨询师数据...")
    print("="*60)

    from app.models.counselor import Counselor
    from app.models.user import User

    db = SessionLocal()
    try:
        # 检查是否已有咨询师数据
        existing = db.query(Counselor).count()
        if existing > 0:
            print(f"  数据库中已有 {existing} 位咨询师，跳过初始化")
            return True

        # 获取第一个用户ID作为关联
        user = db.query(User).first()
        if not user:
            print("  未找到用户，请先创建用户")
            return False

        # 创建测试咨询师数据
        counselors = [
            Counselor(
                user_id=user.id,
                name="王静怡",
                gender="female",
                title="资深心理咨询师",
                specialties="anxiety,depression,emotion",
                consultation_types="video,voice",
                experience_years=10,
                education="北京大学心理学博士",
                qualifications="国家二级心理咨询师,注册心理师",
                price_video=500,
                price_voice=400,
                rating=4.9,
                review_count=128,
                consultation_count=256,
                bio="专注心理健康领域10年，擅长认知行为疗法，帮助来访者解决焦虑、抑郁等情绪问题。",
                approach="认知行为疗法(CBT)、正念疗法",
                achievements="2023年度最佳咨询师奖",
                status="active",
                is_verified=True
            ),
            Counselor(
                user_id=user.id,
                name="李明远",
                gender="male",
                title="婚姻家庭咨询师",
                specialties="emotion,family,career",
                consultation_types="video,voice,offline",
                experience_years=15,
                education="清华大学应用心理学硕士",
                qualifications="国家一级心理咨询师,家庭治疗师",
                price_video=600,
                price_voice=500,
                price_offline=800,
                rating=4.8,
                review_count=95,
                consultation_count=180,
                bio="15年婚姻家庭咨询经验，擅长夫妻关系、亲子关系等家庭问题。",
                approach="家庭系统疗法、情绪聚焦疗法(EFT)",
                achievements="出版《家庭关系重建指南》",
                status="active",
                is_verified=True
            ),
            Counselor(
                user_id=user.id,
                name="张雅婷",
                gender="female",
                title="青少年心理咨询师",
                specialties="anxiety,career,emotion",
                consultation_types="video,voice",
                experience_years=8,
                education="华东师范大学心理学硕士",
                qualifications="国家二级心理咨询师,沙盘治疗师",
                price_video=450,
                price_voice=350,
                rating=4.7,
                review_count=86,
                consultation_count=150,
                bio="专注于青少年心理咨询，擅长学业压力、人际关系、职业规划等问题。",
                approach="沙盘游戏疗法、艺术治疗",
                achievements="青少年心理危机干预专家",
                status="active",
                is_verified=True
            ),
        ]

        # 添加到数据库
        for counselor in counselors:
            db.add(counselor)

        db.commit()
        print(f"✓ 成功创建 {len(counselors)} 位测试咨询师")
        return True
    except Exception as e:
        print(f"✗ 创建咨询师数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_test_knowledge():
    """创建测试心理知识数据"""
    print("\n" + "="*60)
    print("正在创建测试心理知识数据...")
    print("="*60)

    from app.models.knowledge import KnowledgeArticle
    from app.models.user import User

    db = SessionLocal()
    try:
        # 检查是否已有知识数据
        existing = db.query(KnowledgeArticle).count()
        if existing > 0:
            print(f"  数据库中已有 {existing} 篇知识文章，跳过初始化")
            return True

        # 获取第一个用户ID作为作者
        user = db.query(User).first()
        if not user:
            print("  未找到用户，请先创建用户")
            return False

        # 创建测试知识文章
        articles = [
            KnowledgeArticle(
                title="如何应对焦虑情绪？",
                summary="焦虑是现代人常见的心理状态，本文介绍几种简单有效的应对方法",
                cover_image="/uploads/covers/anxiety.jpg",
                content="# 如何应对焦虑情绪？\n\n焦虑是现代人常见的心理状态...",
                content_type="markdown",
                category="anxiety",
                tags="焦虑,情绪管理,心理健康",
                author_id=user.id,
                author_name="心理专家",
                view_count=1523,
                like_count=89,
                favorite_count=56,
                comment_count=12,
                status="published",
                is_featured=True,
                seo_keywords="焦虑,应对焦虑,心理健康",
                seo_description="介绍几种简单有效的应对焦虑情绪的方法",
                published_at=datetime.now()
            ),
            KnowledgeArticle(
                title="抑郁症的早期识别与干预",
                summary="了解抑郁症的早期信号，及时采取干预措施至关重要",
                cover_image="/uploads/covers/depression.jpg",
                content="# 抑郁症的早期识别与干预\n\n抑郁症是一种常见的心理疾病...",
                content_type="markdown",
                category="depression",
                tags="抑郁,心理健康,疾病预防",
                author_id=user.id,
                author_name="心理医生",
                view_count=2341,
                like_count=156,
                favorite_count=89,
                comment_count=23,
                status="published",
                is_featured=True,
                seo_keywords="抑郁症,心理疾病,早期干预",
                seo_description="抑郁症的早期症状识别和干预措施",
                published_at=datetime.now()
            ),
        ]

        # 添加到数据库
        for article in articles:
            db.add(article)

        db.commit()
        print(f"✓ 成功创建 {len(articles)} 篇测试知识文章")
        return True
    except Exception as e:
        print(f"✗ 创建知识数据失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def init_psychological_tests():
    """初始化心理测试数据"""
    print("\n" + "="*60)
    print("正在初始化心理测试数据...")
    print("="*60)

    try:
        # 导入测试数据初始化函数
        from seeds.init_test_data import (
            init_sas_test, init_sds_test, init_big5_test, init_stress_test
        )
        from seeds.init_extended_tests import (
            init_ses_test, init_lsas_test, init_emotional_stability_test,
            init_burnout_test, init_sleep_test
        )
        from app.models.test import PsychologicalTest

        db = SessionLocal()

        # 检查是否已有数据
        existing = db.query(PsychologicalTest).count()
        if existing >= 9:
            print(f"  数据库中已有 {existing} 套测试，跳过初始化")
            db.close()
            return True

        # 初始化基础测试（4套）
        init_sas_test(db)
        init_sds_test(db)
        init_big5_test(db)
        init_stress_test(db)

        # 初始化扩展测试（5套）
        init_ses_test(db)
        init_lsas_test(db)
        init_emotional_stability_test(db)
        init_burnout_test(db)
        init_sleep_test(db)

        db.commit()
        db.close()

        print("✓ 心理测试数据初始化完成（9套，共159题）")
        print("\n可用测试列表：")
        print("  1. 焦虑自评量表 (SAS-20)")
        print("  2. 抑郁自评量表 (SDS-20)")
        print("  3. 大五人格简版量表 (BIG5-20)")
        print("  4. 工作生活压力量表 (STRESS-20)")
        print("  5. 自尊量表 (SES-10)")
        print("  6. 社交焦虑量表 (LSAS-20)")
        print("  7. 情绪稳定性量表 (ES-15)")
        print("  8. 职业倦怠量表 (MBI-15)")
        print("  9. 匹茨堡睡眠质量指数 (PSQI-19)")
        return True
    except Exception as e:
        print(f"✗ 心理测试数据初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary():
    """打印初始化总结"""
    print("\n" + "="*60)
    print("🎉 数据库初始化完成！")
    print("="*60)

    print("\n后续步骤：")
    print("  1. 启动后端服务:")
    print("     cd backend")
    print("     python -m uvicorn app.main:app --reload")
    print("\n  2. 启动前端服务:")
    print("     cd frontend")
    print("     npm run dev")
    print("\n  3. 访问应用:")
    print("     前端: http://localhost:5173")
    print("     API文档: http://localhost:8000/docs")
    print("="*60)


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           SoulStation 数据库初始化工具                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    success = True

    # 创建所有表
    if not create_all_tables():
        return False

    # 创建测试用户
    if not create_test_user():
        success = False

    # 创建管理员
    if not create_admin_user():
        success = False

    # 创建测试咨询师
    if not create_test_counselors():
        success = False

    # 创建测试知识文章
    if not create_test_knowledge():
        success = False

    # 初始化心理测试数据
    if not init_psychological_tests():
        success = False

    if success:
        print_summary()
    else:
        print("\n⚠️  部分数据初始化失败，请查看上方错误信息")

    return success


if __name__ == "__main__":
    main()
