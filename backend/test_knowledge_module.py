"""
心理知识模块端到端测试
验证登录和知识文章API是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_knowledge_module():
    print("=" * 60)
    print("心理知识模块端到端测试")
    print("=" * 60)

    # 1. 测试登录
    print("\n1. 测试用户登录...")
    login_data = {
        "email": "xiaoming@example.com",
        "password": "123456"
    }

    try:
        login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        login_response.raise_for_status()

        result = login_response.json()
        if result.get("code") == 200 and result.get("data", {}).get("token"):
            token = result["data"]["token"]
            print("✅ 登录成功")
            print(f"   用户: {result['data']['userInfo']['nickname']}")
            print(f"   Token: {token[:30]}...")
        else:
            print("❌ 登录失败:", result)
            return False
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return False

    # 2. 测试获取知识列表
    print("\n2. 测试获取知识列表...")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        knowledge_response = requests.get(
            f"{BASE_URL}/knowledge/list",
            headers=headers,
            params={"page": 1, "page_size": 5}
        )
        knowledge_response.raise_for_status()

        result = knowledge_response.json()
        if result.get("code") == 200:
            articles = result.get("data", {}).get("items", [])
            total = result.get("data", {}).get("total", 0)
            print("✅ 获取知识列表成功")
            print(f"   总文章数: {total}")
            print(f"   返回文章数: {len(articles)}")

            if articles:
                print("\n   前3篇文章:")
                for i, article in enumerate(articles[:3], 1):
                    print(f"   {i}. {article.get('title', 'N/A')}")
                    print(f"      分类: {article.get('category', 'N/A')}")
                    print(f"      浏览: {article.get('view_count', 0)}")
                    print(f"      点赞: {article.get('like_count', 0)}")
                    print(f"      收藏: {article.get('favorite_count', 0)}")
            else:
                print("⚠️  没有找到文章")
        else:
            print("❌ 获取知识列表失败:", result)
            return False
    except Exception as e:
        print(f"❌ API请求失败: {e}")
        return False

    # 3. 测试按分类筛选
    print("\n3. 测试按分类筛选...")
    try:
        anxiety_response = requests.get(
            f"{BASE_URL}/knowledge/list",
            headers=headers,
            params={"category": "anxiety", "page": 1, "page_size": 5}
        )
        anxiety_response.raise_for_status()

        result = anxiety_response.json()
        if result.get("code") == 200:
            anxiety_articles = result.get("data", {}).get("items", [])
            print("✅ 分类筛选成功")
            print(f"   焦虑类文章数: {len(anxiety_articles)}")
            if anxiety_articles:
                print(f"   文章标题: {anxiety_articles[0].get('title', 'N/A')}")
        else:
            print("❌ 分类筛选失败:", result)
            return False
    except Exception as e:
        print(f"❌ 分类筛选请求失败: {e}")
        return False

    # 4. 检查数据库中的文章数据
    print("\n4. 检查数据库数据...")
    try:
        from app.core.database import SessionLocal
        from app.models.knowledge import KnowledgeArticle

        db = SessionLocal()
        total_articles = db.query(KnowledgeArticle).count()
        published_articles = db.query(KnowledgeArticle).filter(
            KnowledgeArticle.status == "published"
        ).count()

        print("✅ 数据库检查完成")
        print(f"   数据库总文章数: {total_articles}")
        print(f"   已发布文章数: {published_articles}")

        # 按分类统计
        categories = {}
        for article in db.query(KnowledgeArticle).filter(KnowledgeArticle.status == "published").all():
            cat = article.category or "未分类"
            categories[cat] = categories.get(cat, 0) + 1

        print("   文章分类统计:")
        for category, count in categories.items():
            print(f"     {category}: {count}篇")

        db.close()
    except Exception as e:
        print(f"❌ 数据库检查失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ 心理知识模块测试完成！")
    print("=" * 60)

    print("\n📱 测试步骤：")
    print("1. 打开浏览器访问: http://localhost:5174")
    print("2. 使用测试账号登录: xiaoming@example.com / 123456")
    print("3. 点击导航栏的'心理知识'链接")
    print("4. 应该能看到8篇文章")

    return True

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "d:\\86188\\College\\毕设\\zou\\SoulStation\\backend")
    test_knowledge_module()