# SoulStation 测试数据摘要

## 📋 测试账号信息

### 普通用户账号
| 邮箱 | 密码 | 昵称 | 角色 |
|------|------|------|------|
| xiaoming@example.com | 123456 | 小明同学 | 用户 |
| xiaohong@example.com | 123456 | 小红同学 | 用户 |
| david@example.com | 123456 | David | 用户 |
| lucy@example.com | 123456 | Lucy | 用户 |

### 咨询师账号
| 邮箱 | 密码 | 昵称 | 角色 | 专业领域 |
|------|------|------|------|----------|
| teacher_wang@example.com | 123456 | 王老师 | 咨询师 | 青少年心理,学习压力 |

### 管理员账号
| 邮箱 | 密码 | 角色 |
|------|------|------|
| admin@soulstation.com | admin123 | 超级管理员 |

## 📊 测试数据统计

### 用户数据 (5个用户)
- 4个普通用户
- 1个咨询师用户
- 所有用户密码统一为：`123456`

### 咨询师数据 (1个咨询师)
- **王老师** - 资深心理咨询师
  - 专业领域：青少年心理、学习压力
  - 咨询方式：视频、语音、线下
  - 从业年限：15年
  - 学历：北京大学心理学博士
  - 价格：视频400元/小时，语音250元/小时，线下700元/小时
  - 评分：5.0 (37评价)

### 知识文章 (3篇)
1. **如何缓解工作压力？**
   - 分类：压力管理
   - 标签：压力管理、职场健康、自我调节

2. **认识焦虑：当你感到焦虑时该怎么办**
   - 分类：焦虑
   - 标签：焦虑、情绪管理、心理健康

3. **建立健康的人际关系**
   - 分类：人际关系
   - 标签：人际关系、沟通技巧、心理健康

### 预约订单 (4个)
- 状态分布：已完成、已取消、已确认
- 咨询类型：视频、语音
- 价格范围：200-400元

## 🔍 数据库表结构

### 用户相关表
- `users` - 用户基础信息
- `counselors` - 咨询师详细信息
- `admins` - 管理员信息

### 心理测试相关表
- `psychological_tests` - 心理测试量表
- `test_questions` - 测试题目
- `test_results` - 测试结果
- `test_progress` - 答题进度

### 聊天相关表
- `chat_dialogues` - 对话记录
- `chat_messages` - 聊天消息
- `chat_tags` - 对话标签
- `chat_dialogue_tags` - 对话标签关联

### 咨询相关表
- `appointments` - 预约订单
- `consultation_reviews` - 咨询评价
- `consultation_messages` - 咨询对话消息

### 知识库相关表
- `knowledge_articles` - 知识文章
- `knowledge_comments` - 文章评论
- `knowledge_likes` - 文章点赞
- `knowledge_favorites` - 文章收藏

## 🚀 快速测试场景

### 1. 用户登录与浏览
1. 使用 `xiaoming@example.com` / `123456` 登录
2. 浏览知识文章
3. 查看咨询师列表
4. 查看心理测试

### 2. 咨询师预约
1. 选择咨询师（王老师）
2. 选择咨询类型（视频/语音）
3. 选择预约时间
4. 填写问题描述
5. 提交预约

### 3. 心理测试
1. 选择焦虑自评量表
2. 完成20道题目
3. 查看测试结果和建议

### 4. 智能问答
1. 进入聊天页面
2. 输入心理相关问题
3. 查看AI回复
4. 创建对话历史记录

### 5. 管理员功能
1. 使用 `admin@soulstation.com` / `admin123` 登录
2. 查看用户管理
3. 审核咨询师申请
4. 管理知识文章
5. 查看数据统计

## 📝 注意事项

1. **密码统一**：所有测试账号密码均为 `123456`（管理员除外为 `admin123`）
2. **数据库连接**：使用Docker MySQL (localhost:3307) 和Redis (localhost:6380)
3. **数据清理**：如需重置数据，可以运行 `python backend/init_database.py`
4. **API文档**：访问 http://localhost:8000/docs 查看完整API文档

## 🔧 数据维护命令

### 查看数据统计
```bash
cd backend
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.models.counselor import Counselor
from app.models.knowledge import KnowledgeArticle

db = SessionLocal()
print(f'Users: {db.query(User).count()}')
print(f'Counselors: {db.query(Counselor).count()}')
print(f'Articles: {db.query(KnowledgeArticle).count()}')
db.close()
"
```

### 添加新测试数据
```bash
cd backend
python create_test_data.py
```

### 重置数据库
```bash
cd backend
python init_database.py
```

---

**生成时间**: 2026-04-07
**数据版本**: 1.0
**系统状态**: 运行中