# 心理知识模块使用指南

## 概述

心理知识模块已完成开发，提供完整的心理文章阅读、搜索、互动等功能。

## 功能特性

### 1. 知识文章管理
- ✅ 知识列表查询（支持搜索、分类、排序）
- ✅ 知识详情查看
- ✅ 推荐知识（基于分类和标签）
- ✅ 浏览次数统计

### 2. 用户交互功能
- ✅ 点赞/取消点赞
- ✅ 收藏/取消收藏
- ✅ 评论功能
- ✅ 用户收藏列表

### 3. 内容管理
- ✅ Markdown/HTML内容支持
- ✅ 分类和标签管理
- ✅ 封面图片
- ✅ SEO优化

## API接口清单

| 接口路径 | 方法 | 功能描述 | 权限 |
|----------|------|----------|------|
| `/api/knowledge/list` | GET | 获取知识列表 | 公开 |
| `/api/knowledge/{id}` | GET | 获取知识详情 | 公开 |
| `/api/knowledge/{id}/recommended` | GET | 获取推荐知识 | 公开 |
| `/api/knowledge/{id}/favorite` | POST | 收藏知识 | 登录用户 |
| `/api/knowledge/{id}/favorite` | DELETE | 取消收藏 | 登录用户 |
| `/api/knowledge/{id}/like` | POST | 点赞知识 | 登录用户 |
| `/api/knowledge/{id}/like` | DELETE | 取消点赞 | 登录用户 |
| `/api/knowledge/{id}/comments` | GET | 获取评论列表 | 公开 |
| `/api/knowledge/{id}/comment` | POST | 提交评论 | 登录用户 |
| `/api/knowledge/user/favorites` | GET | 获取用户收藏列表 | 登录用户 |

## 数据库表结构

### KnowledgeArticle（知识文章表）

```python
id                      # 文章ID
title                   # 文章标题
summary                 # 文章摘要
cover_image             # 封面图片URL
content                 # 文章内容（Markdown/HTML）
content_type            # 内容类型
category                # 分类
tags                    # 标签（逗号分隔）
author_id               # 作者ID
author_name             # 作者名称
view_count              # 浏览次数
like_count              # 点赞数
favorite_count          # 收藏数
comment_count           # 评论数
status                  # 状态
is_featured             # 是否精选
is_deleted              # 是否已删除
seo_keywords            # SEO关键词
seo_description         # SEO描述
created_at              # 创建时间
updated_at              # 更新时间
published_at            # 发布时间
```

### KnowledgeComment（知识评论表）

```python
id                      # 评论ID
article_id              # 文章ID
user_id                 # 用户ID
content                 # 评论内容
parent_id               # 父评论ID（回复功能）
is_visible              # 是否可见
is_deleted              # 是否已删除
like_count              # 点赞数
created_at              # 创建时间
```

### KnowledgeFavorite（知识收藏表）

```python
id                      # 收藏ID
article_id              # 文章ID
user_id                 # 用户ID
created_at              # 收藏时间
```

### KnowledgeLike（知识点赞表）

```python
id                      # 点赞ID
article_id              # 文章ID
user_id                 # 用户ID
created_at              # 点赞时间
```

## 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── knowledge.py         # 知识模型（新增）
│   ├── schemas/
│   │   └── knowledge.py         # 知识schemas（新增）
│   ├── services/
│   │   └── knowledge_service.py # 知识服务层（新增）
│   └── api/
│       └── knowledge/
│           └── __init__.py      # 知识API路由（新增）
└── init_knowledge_data.py       # 初始化测试数据（新增）
```

## 快速开始

### 1. 初始化数据库

```bash
cd backend

# 创建数据库表
python -c "from app.core.database import engine; from app.models.knowledge import Base; Base.metadata.create_all(bind=engine)"

# 初始化测试知识数据
python init_knowledge_data.py
```

### 2. 启动后端服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试API接口

```bash
# 运行测试脚本
python test_knowledge_apis.py
```

### 4. 访问前端页面

- 知识列表：`/knowledge`
- 知识详情：`/knowledge/{id}`

## API使用示例

### 获取知识列表

```bash
# 基本查询
curl -X GET "http://localhost:8000/api/knowledge/list?page=1&page_size=10"

# 搜索
curl -X GET "http://localhost:8000/api/knowledge/list?keyword=焦虑"

# 按分类筛选
curl -X GET "http://localhost:8000/api/knowledge/list?category=anxiety"

# 排序（latest/hot/popular）
curl -X GET "http://localhost:8000/api/knowledge/list?sort=hot"
```

### 获取知识详情

```bash
curl -X GET "http://localhost:8000/api/knowledge/1"
```

### 获取推荐知识

```bash
curl -X GET "http://localhost:8000/api/knowledge/1/recommended?limit=5"
```

### 收藏知识

```bash
curl -X POST "http://localhost:8000/api/knowledge/1/favorite" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 取消收藏

```bash
curl -X DELETE "http://localhost:8000/api/knowledge/1/favorite" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 点赞知识

```bash
curl -X POST "http://localhost:8000/api/knowledge/1/like" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 取消点赞

```bash
curl -X DELETE "http://localhost:8000/api/knowledge/1/like" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 获取评论列表

```bash
curl -X GET "http://localhost:8000/api/knowledge/1/comments?page=1&page_size=10"
```

### 提交评论

```bash
curl -X POST "http://localhost:8000/api/knowledge/1/comment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "这篇文章很有帮助！"
  }'
```

### 回复评论

```bash
curl -X POST "http://localhost:8000/api/knowledge/1/comment" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我也这么觉得",
    "parent_id": 123
  }'
```

### 获取用户收藏列表

```bash
curl -X GET "http://localhost:8000/api/knowledge/user/favorites?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 内容分类

### 支持的分类

| 分类 | 说明 |
|------|------|
| anxiety | 焦虑相关 |
| depression | 抑郁相关 |
| emotion | 情感相关 |
| career | 职场相关 |
| family | 家庭相关 |

### 文章状态

| 状态 | 说明 |
|------|------|
| draft | 草稿 |
| published | 已发布 |
| archived | 已归档 |

## 业务规则

### 1. 浏览统计
- 每次访问详情页自动增加浏览次数
- 支持重复浏览统计

### 2. 点赞功能
- 同一用户对同一文章只能点赞一次
- 重复点赞操作会被忽略（幂等性）
- 点赞后自动更新文章的点赞数

### 3. 收藏功能
- 同一用户对同一文章只能收藏一次
- 重复收藏操作会被忽略（幂等性）
- 收藏后自动更新文章的收藏数

### 4. 评论功能
- 评论内容1-1000字符
- 支持回复评论（通过parent_id）
- 删除文章时不会删除评论（软删除）
- 评论数量自动更新

### 5. 推荐算法
- 基于文章分类推荐
- 优先推荐同分类的文章
- 按浏览量和点赞数排序
- 排除当前文章

## 测试数据

初始化脚本会创建5篇测试知识文章：

| 标题 | 分类 | 标签 |
|------|------|------|
| 如何应对焦虑情绪？ | anxiety | 焦虑,情绪管理,心理健康 |
| 抑郁症的早期识别与干预 | depression | 抑郁,心理健康,疾病预防 |
| 建立健康的亲密关系 | emotion | 亲密关系,沟通,情感 |
| 职场压力管理指南 | career | 职场压力,压力管理,工作 |
| 改善家庭沟通的技巧 | family | 家庭沟通,家庭关系,代沟 |

## 内容格式

### Markdown示例

```markdown
# 标题

## 二级标题

段落文本。

### 列表
- 项目1
- 项目2

**粗体** 和 *斜体*
```

### HTML示例

```html
<h1>标题</h1>
<p>段落文本</p>
<ul>
  <li>项目1</li>
  <li>项目2</li>
</ul>
```

## SEO优化

### 文章SEO字段

- **seo_keywords**: 关键词（逗号分隔）
- **seo_description**: 描述（150字符以内）
- **title**: 标题（包含关键词）
- **summary**: 摘要（吸引点击）

### 搜索优化

- 标题、摘要、内容、标签都支持全文搜索
- 分类筛选提高检索效率
- 多维度排序满足不同需求

## 注意事项

### 1. 内容安全
- 过滤恶意内容
- 验证HTML内容（如使用）
- 防止XSS攻击

### 2. 性能优化
- 列表查询使用分页
- 详情内容可能较长，考虑分页或懒加载
- 评论列表支持分页

### 3. 数据一致性
- 点赞/收藏/评论操作使用事务
- 统计数据实时更新
- 软删除保留数据

### 4. 权限控制
- 点赞/收藏/评论需要登录
- 评论可以设置为公开或仅登录可见
- 用户只能管理自己的评论

## 扩展功能建议

未来可以考虑添加的功能：
1. 文章编辑器（富文本/Markdown）
2. 图片上传和管理
3. 文章版本控制
4. 相关文章推荐优化
5. 评论点赞功能
6. 文章分享功能
7. 阅读进度记录
8. 专题管理
9. 文章标签云
10. 热门文章榜

## 问题排查

### 文章列表为空
- 确认数据库中有文章数据
- 检查文章状态是否为 published
- 验证分类筛选是否正确

### 点赞/收藏失败
- 确认用户已登录
- 检查文章是否存在
- 验证是否已操作过

### 评论提交失败
- 确认用户已登录
- 检查文章是否存在
- 验证评论内容长度
- 确认父评论ID有效

### 搜索无结果
- 检查关键词是否正确
- 尝试使用更通用的关键词
- 确认数据库中有相关内容

## 联系支持

如有问题，请查看：
- 项目TODO.md
- API文档：http://localhost:8000/docs
- 测试脚本：test_knowledge_apis.py
