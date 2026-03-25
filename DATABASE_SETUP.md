# SoulStation 数据库初始化指南

## 快速开始

### 1. 配置数据库连接

确保 `backend/.env` 文件中的数据库配置正确：

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/soulstation
```

### 2. 运行数据库初始化

在项目根目录执行：

```bash
python backend/init_database.py
```

这个脚本会自动完成以下操作：

1. ✅ 创建所有数据库表
2. ✅ 创建测试用户账号
3. ✅ 创建管理员账号
4. ✅ 创建测试咨询师数据
5. ✅ 创建测试知识文章
6. ✅ 初始化9套心理测试数据（共159题）

### 3. 初始化完成后的默认账号

#### 测试用户
- 邮箱: `test@example.com`
- 密码: `123456`

#### 管理员
- 用户名: `admin`
- 密码: `admin123`
- 角色: super_admin

⚠️ **重要提示**：请在首次登录后修改默认密码！

## 数据库表结构

初始化后将创建以下数据库表：

### 用户相关
- `users` - 用户表
- `admins` - 管理员表

### 心理测试相关
- `psychological_tests` - 心理测试表
- `test_questions` - 测试题目表
- `test_results` - 测试结果表
- `test_progress` - 答题进度表

### 聊天相关
- `chat_dialogues` - 对话记录表
- `chat_messages` - 聊天消息表
- `chat_tags` - 对话标签表
- `chat_dialogue_tags` - 对话标签关联表

### 咨询师相关
- `counselors` - 咨询师表
- `appointments` - 预约订单表
- `consultation_reviews` - 咨询评价表
- `consultation_messages` - 咨询对话消息表

### 知识库相关
- `knowledge_articles` - 知识文章表
- `knowledge_comments` - 知识评论表
- `knowledge_favorites` - 知识收藏表
- `knowledge_likes` - 知识点赞表

## 可用的心理测试

初始化完成后，系统包含以下9套心理测试：

1. 焦虑自评量表 (SAS-20) - 20题
2. 抑郁自评量表 (SDS-20) - 20题
3. 大五人格简版量表 (BIG5-20) - 20题
4. 工作生活压力量表 (STRESS-20) - 20题
5. 自尊量表 (SES-10) - 10题
6. 社交焦虑量表 (LSAS-20) - 20题
7. 情绪稳定性量表 (ES-15) - 15题
8. 职业倦怠量表 (MBI-15) - 15题
9. 匹茨堡睡眠质量指数 (PSQI-19) - 19题

**共计：9套测试，159道题目**

## 仅创建表结构

如果只需要创建数据库表而不需要初始化数据：

```bash
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine); print('数据库表创建完成')"
```

## 后续步骤

数据库初始化完成后：

1. **启动后端服务**
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **启动前端服务**
   ```bash
   cd frontend
   npm run dev
   ```

3. **访问应用**
   - 前端: http://localhost:5173
   - API文档: http://localhost:8000/docs

## 定时任务

项目包含预约提醒邮件定时任务脚本：

**文件位置**: `backend/send_appointment_reminders.py`

### 设置定时任务

**Linux/Mac (crontab)**
```bash
# 每10分钟运行一次
*/10 * * * * cd /path/to/SoulStation/backend && python send_appointment_reminders.py
```

**Windows (任务计划程序)**
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置每10分钟运行一次
4. 运行程序: `python C:\path\to\SoulStation\backend\send_appointment_reminders.py`

## 故障排查

### 问题1：数据库连接失败

**错误信息**: `Can't connect to MySQL server`

**解决方案**:
1. 确保MySQL/MariaDB服务已启动
2. 检查 `backend/.env` 中的数据库配置
3. 确保数据库已创建

### 问题2：表已存在错误

**错误信息**: `Table 'xxx' already exists`

**解决方案**:
这是正常的，脚本会自动跳过已存在的表。如需重新创建，请手动删除数据库后重新初始化。

### 问题3：权限错误

**错误信息**: `Access denied for user`

**解决方案**:
检查数据库用户权限，确保用户有以下权限：
- CREATE
- ALTER
- INSERT
- UPDATE
- DELETE
- SELECT

## 技术支持

如遇到其他问题，请查看：
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查指南
- [README.md](README.md) - 项目总体说明
