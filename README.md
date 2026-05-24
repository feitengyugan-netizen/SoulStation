# SoulStation - 心理咨询服务平台

> 心灵驿站，守护您的心理健康

## 项目简介

这是一个基于 **Vue 3 + FastAPI** 的心理咨询服务平台，提供智能心理问答、心理测试、在线咨询预约等功能。

## 核心功能

- 🤖 **智能心理问答** - 基于 RAG 检索增强生成的 AI 心理咨询
- 🎤 **语音转文字** - 集成豆包语音识别，支持语音输入
- 📝 **心理测试** - 9套专业心理测试量表（159题）
- 👨‍⚕️ **在线咨询** - 专业咨询师预约与实时对话
- 📚 **心理知识** - 心理健康文章与科普
- 🔐 **安全认证** - JWT Token + 邮箱验证

## 技术栈

### 前端
- **框架**: Vue 3.4.15 + Vite 5.0.11
- **UI库**: Element Plus 2.4.4 + @element-plus/icons-vue 2.3.1
- **状态管理**: Pinia 2.1.7
- **路由**: Vue Router 4.2.5
- **HTTP**: Axios 1.6.5
- **图表**: ECharts 5.4.3 + vue-echarts 6.6.4
- **工具**: Day.js 1.11.10
- **样式**: Sass 1.70.0

### 后端
- **框架**: FastAPI 0.109.0 + Uvicorn 0.27.0
- **数据库**: MySQL + SQLAlchemy 2.0.25 + PyMySQL 1.1.0
- **缓存**: Redis 5.0.1
- **认证**: JWT (python-jose) + Passlib + Bcrypt
- **邮件**: FastAPI Mail 1.4.1
- **AI服务**:
  - 豆包录音文件识别模型2.0 (volc.seedasr.auc)
  - OpenAI API (用于RAG)
  - LangChain + ChromaDB
- **工具**: httpx, aiofiles, python-docx

## 团队分工

### 开发人员 A - 前端 + 后端
**核心模块**: 基础层 + 用户核心服务
1. 登录注册模块 (`auth`)
2. 智能心理问答模块 (`chat`) - RAG
3. 心理测试模块 (`test`)
4. 个人中心模块 (`profile`)

### 开发人员 B - 前端 + 后端
**核心模块**: 服务对接 + 平台管理
1. 咨询师对接与预约模块 (`consultation`)
2. 咨询对话模块 (`dialogue`)
3. 后台管理模块 (`admin`)
4. 公共信息模块 (`public`)

## 项目结构

```
SoulStation/
├── frontend/                   # 前端 Vue 项目
│   ├── src/
│   │   ├── api/               # API 接口封装
│   │   ├── assets/            # 静态资源
│   │   │   ├── images/        # 图片
│   │   │   ├── icons/         # 图标
│   │   │   └── styles/        # 样式文件
│   │   ├── components/        # 组件
│   │   │   ├── auth/          # 登录注册组件
│   │   │   ├── chat/          # 智能问答组件 (RAG)
│   │   │   ├── test/          # 心理测试组件
│   │   │   ├── profile/       # 个人中心组件
│   │   │   ├── consultation/  # 咨询预约组件
│   │   │   ├── dialogue/      # 咨询对话组件
│   │   │   ├── admin/         # 后台管理组件
│   │   │   ├── counselor/     # 咨询师相关组件
│   │   │   ├── public/        # 公共信息组件
│   │   │   ├── common/        # 通用组件
│   │   │   └── right-sidebar/ # 右侧边栏组件
│   │   ├── router/            # 路由配置
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── utils/             # 工具函数
│   │   └── views/             # 页面视图
│   │       ├── home/          # 首页
│   │       ├── auth/          # 登录注册页
│   │       ├── chat/          # 智能问答页
│   │       ├── test/          # 心理测试页
│   │       ├── profile/       # 个人中心页
│   │       ├── consultation/  # 咨询预约页
│   │       ├── dialogue/      # 咨询对话页
│   │       ├── counselor/     # 咨询师相关页
│   │       ├── knowledge/     # 知识库页
│   │       ├── admin/         # 后台管理页
│   │       └── public/        # 公共信息页
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── backend/                    # 后端 FastAPI 项目
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth/          # 登录注册接口
│   │   │   ├── chat/          # 智能问答接口 (RAG)
│   │   │   ├── test/          # 心理测试接口
│   │   │   ├── consultation/  # 咨询预约接口
│   │   │   ├── counselor/     # 咨询师接口
│   │   │   ├── knowledge/     # 知识库接口
│   │   │   ├── user/          # 用户接口
│   │   │   └── admin/         # 后台管理接口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置文件
│   │   │   ├── security.py    # 安全相关
│   │   │   ├── deps.py        # 依赖注入
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── auth_service.py        # 认证服务
│   │   │   ├── email_service.py       # 邮件服务
│   │   │   ├── speech_service.py      # 语音识别服务
│   │   │   ├── ai_service.py          # AI 服务
│   │   │   ├── chat_service.py        # 聊天服务
│   │   │   ├── test_service.py        # 测试服务
│   │   │   ├── counselor_service.py   # 咨询师服务
│   │   │   ├── knowledge_service.py   # 知识库服务
│   │   │   ├── user_service.py        # 用户服务
│   │   │   ├── admin_service.py       # 管理服务
│   │   │   ├── rag/                   # RAG 服务
│   │   │   ├── email/                 # 邮件相关
│   │   │   └── storage/               # 存储服务
│   │   ├── utils/             # 工具函数
│   │   ├── middleware/        # 中间件
│   │   ├── static/            # 静态文件
│   │   └── main.py            # 应用入口
│   ├── seeds/                 # 测试数据种子
│   ├── uploads/               # 上传文件目录
│   ├── init_database.py       # 数据库初始化脚本
│   ├── send_appointment_reminders.py  # 预约提醒定时任务
│   ├── requirements.txt       # 依赖
│   └── .env.example           # 环境变量示例
│
├── database/                   # 数据库相关
│   ├── docs/                  # 数据库文档
│   │   ├── ER图.md
│   │   └── 表结构.md
│   ├── migrations/            # 迁移脚本
│   ├── seeds/                 # 种子数据
│   └── backups/               # 备份文件
│
├── docs/                       # 项目文档
│   ├── design/                # 设计文档
│   ├── member-a/              # 开发人员 A 的文档
│   ├── member-b/              # 开发人员 B 的文档
│   └── meeting/               # 会议记录
│
├── shared/                     # 共享资源
│   └── assets/                # 共享素材
│
├── DATABASE_SETUP.md           # 数据库初始化指南
├── SPEECH_README.md            # 语音识别集成指南
├── SETUP_PUBLIC_URL.md         # 公网URL配置指南
├── PROJECT_CLEANUP_SUMMARY.md  # 项目整理总结
├── TROUBLESHOOTING.md          # 故障排查指南
└── README.md                   # 项目说明
```

## 数据库表

### 用户相关
- `users` - 用户表（普通用户/咨询师）
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

## 开发规范

### 接口命名规范
- 后端路由前缀: `/api`
- 各模块路由:
  - `/api/auth` - 登录注册
  - `/api/chat` - 智能问答 (RAG + 语音识别)
  - `/api/test` - 心理测试
  - `/api/consultation` - 咨询预约
  - `/api/counselor` - 咨询师管理
  - `/api/knowledge` - 知识库
  - `/api/user` - 用户管理
  - `/api/admin` - 后台管理

### 代码规范
- 前端组件命名: PascalCase
- 后端路由命名: snake_case
- 统一代码风格

## 模块说明

### 登录注册模块 (auth)
- 邮箱验证码发送
- 用户注册/登录
- 忘记密码
- JWT Token 认证

### 智能问答模块 (chat)
- **RAG 检索增强问答** - 基于知识库的智能回复
- **语音转文字** - 集成豆包语音识别API
- 对话记录管理
- 对话标签管理
- 流式/非流式响应支持

### 心理测试模块 (test)
- **9套专业心理测试**（共159题）
  - 焦虑自评量表 (SAS-20)
  - 抑郁自评量表 (SDS-20)
  - 大五人格简版量表 (BIG5-20)
  - 工作生活压力量表 (STRESS-20)
  - 自尊量表 (SES-10)
  - 社交焦虑量表 (LSAS-20)
  - 情绪稳定性量表 (ES-15)
  - 职业倦怠量表 (MBI-15)
  - 匹茨堡睡眠质量指数 (PSQI-19)
- 问卷查询与筛选
- 答题进度保存
- 结果计算与展示
- 测试统计分析

### 咨询预约模块 (consultation)
- 咨询师信息展示
- 预约订单管理
- 预约提醒邮件
- 咨询评价

### 咨询师管理 (counselor)
- 咨询师资质审核
- 咨询师档案管理
- 可预约时间管理
- 咨询统计

### 知识库模块 (knowledge)
- 心理知识文章展示
- 文章评论与点赞
- 文章收藏与分享
- 知识搜索与分类

### 咨询对话模块 (dialogue)
- 实时对话
- 消息轮询
- 对话历史记录
- 咨询结束处理

### 后台管理模块 (admin)
- 咨询师资质审核
- 心理知识管理
- 用户/订单管控
- 数据统计分析
- 系统配置管理

### 用户管理模块 (user)
- 用户信息管理
- 隐私设置
- 数据统计汇总
- 个人中心

## 快速开始

### 前置要求
- Node.js 16+
- Python 3.8+
- MySQL 5.7+ / MariaDB 10.3+
- Redis（可选，用于缓存）

### 1. 克隆项目
```bash
git clone <repository-url>
cd SoulStation
```

### 2. 数据库配置

#### 创建数据库
```bash
mysql -u root -p -e "CREATE DATABASE soulstation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

#### 配置环境变量
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接：
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/soulstation
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 邮件配置
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_FROM=your-email@example.com

# 豆包语音识别（可选）
DOUBAO_API_KEY=your-doubao-api-key-here
PUBLIC_URL=http://localhost:8000  # 生产环境使用公网URL
```

#### 初始化数据库
```bash
# 在项目根目录执行
python backend/init_database.py
```

这将自动创建所有表并初始化测试数据（9套心理测试，159道题目）。

### 3. 后端启动
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 5. 访问应用
- 前端地址: http://localhost:5173
- API文档: http://localhost:8000/docs
- 后台管理: http://localhost:5173/admin

### 默认账号

#### 🔑 管理员账号
```
邮箱/用户名: admin@soulstation.com 
密码: admin123
角色: 超级管理员
登录入口: http://localhost:5173/login
```
- 登录后自动跳转到管理后台
- 拥有所有管理权限
- **可以使用邮箱 `admin@soulstation.com` 或用户名 `admin` 登录**

#### 👥 普通用户账号

**测试用户1:**
```
邮箱: test@example.com
密码: 123456
昵称: 测试用户
```

**测试用户2:**
```
邮箱: user1@example.com
密码: 123456
昵称: 张三
```

**测试用户3:**
```
邮箱: user2@example.com
密码: 123456
昵称: 李四
```

**测试用户4:**
```
邮箱: user3@example.com
密码: 123456
昵称: 王五
```

**测试用户5 (焦虑测试):**
```
邮箱: anxiety@test.com
密码: 123456
昵称: 小明同学
```

**测试用户6 (抑郁测试):**
```
邮箱: depression@test.com
密码: 123456
昵称: 小红同学
```

#### 👨‍⚕️ 咨询师账号

每个咨询师都有独立的登录账号，登录后会根据角色自动跳转到咨询师工作台。

**咨询师1 - 王静怡 (焦虑与抑郁/青少年心理)**
```
邮箱: counselor1@soulstation.com
密码: 123456
专长: 焦虑与抑郁、青少年心理、情绪管理
职称: 国家二级心理咨询师
从业年限: 8年
```

**咨询师2 - 李明远 (婚姻家庭/职场压力)**
```
邮箱: counselor2@soulstation.com
密码: 123456
专长: 婚姻家庭、职场压力、个人成长
职称: 资深心理治疗师
从业年限: 12年
```

**咨询师3 - 张雅婷 (儿童心理/亲子关系)**
```
邮箱: counselor3@soulstation.com
密码: 123456
专长: 儿童心理、学习障碍、亲子关系
职称: 儿童心理专家
从业年限: 10年
```

**咨询师4 - 赵晓敏 (情绪管理/创伤疗愈)**
```
邮箱: counselor4@soulstation.com
密码: 123456
专长: 抑郁与焦虑、情绪障碍、创伤疗愈
职称: 情绪管理专家
从业年限: 6年
```

**咨询师5 - 陈建国 (成瘾行为/强迫症)**
```
邮箱: counselor5@soulstation.com
密码: 123456
专长: 成瘾行为、强迫症、睡眠障碍
职称: 成瘾心理专家
从业年限: 15年
```

**咨询师6 - 刘思雨 (婚恋情感/亲密关系)**
```
邮箱: counselor6@soulstation.com
密码: 123456
专长: 婚恋情感、失恋疗愈、亲密关系
职称: 婚恋情感专家
从业年限: 7年
```

⚠️ **重要提示**:
1. 所有测试账号的默认密码均为 `123456`（管理员为 `admin123`）
2. 首次登录后建议修改默认密码
3. 所有角色使用统一的登录入口：`http://localhost:5173/login`
4. 系统会根据用户角色自动跳转到对应页面（管理员→后台，咨询师→工作台，用户→首页）

## 高级配置

### 语音识别功能

项目已集成豆包语音识别API，支持语音转文字功能。

**配置步骤**：

1. 获取豆包API密钥
   - 访问[火山引擎控制台](https://console.volcengine.com/)
   - 开通"语音技术-音频自训练"服务
   - 获取 API Key

2. 配置后端环境变量（已在上面步骤中说明）

3. 配置公网URL（开发环境）
   - 语音识别需要公网可访问的音频URL
   - 开发环境使用内网穿透工具（ngrok、CloudFlare Tunnel等）
   - 详细配置见 [SETUP_PUBLIC_URL.md](SETUP_PUBLIC_URL.md)

**使用说明**：
- 进入聊天页面点击麦克风按钮
- 允许浏览器访问麦克风
- 开始录音（最长60秒）
- 自动识别并填充到输入框

详细文档：[SPEECH_README.md](SPEECH_README.md)

### 定时任务

项目包含预约提醒邮件定时任务：

```bash
# Linux/Mac (crontab)
*/10 * * * * cd /path/to/SoulStation/backend && python send_appointment_reminders.py

# Windows (任务计划程序)
# 创建基本任务，每10分钟运行一次
python C:\path\to\SoulStation\backend\send_appointment_reminders.py
```

## 常见问题

### 1. 数据库连接失败？
- 检查MySQL服务是否启动
- 确认 `.env` 文件中数据库配置正确
- 确保数据库已创建

### 2. 语音识别不工作？
- 确保配置了 `DOUBAO_API_KEY`
- 开发环境需要配置 `PUBLIC_URL`（使用内网穿透）
- 详见 [SPEECH_README.md](SPEECH_README.md)

### 3. 邮件发送失败？
- 检查 `.env` 中的邮件配置
- 某些邮箱需要开启"应用专用密码"
- 确认网络连接正常

### 4. 前端API请求失败？
- 确保后端服务正在运行（http://localhost:8000）
- 检查 `frontend/.env` 中的 `VITE_API_BASE_URL` 配置
- 查看浏览器控制台错误信息

更多问题请查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 技术支持

如有问题或建议，请：
- 提交 Issue
- 查看项目文档
- 联系开发团队

## 许可证

MIT License
