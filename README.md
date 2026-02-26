# SoulStation - 心理咨询服务平台

> 心灵驿站，守护您的心理健康

## 项目简介

这是一个基于 **Vue 3 + FastAPI** 的心理咨询服务平台，提供智能心理问答、心理测试、在线咨询预约等功能。

## 技术栈

- **前端**: Vue 3 + Element Plus + Pinia + Axios + ECharts
- **后端**: FastAPI + SQLAlchemy + MySQL
- **认证**: JWT Token
- **AI**: RAG 检索增强生成

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
│   │   │   └── public/        # 公共信息组件
│   │   ├── router/            # 路由配置
│   │   ├── store/             # Pinia 状态管理
│   │   ├── utils/             # 工具函数
│   │   └── views/             # 页面视图
│   │       ├── home/          # 首页
│   │       ├── auth/          # 登录注册页
│   │       ├── chat/          # 智能问答页
│   │       ├── test/          # 心理测试页
│   │       ├── profile/       # 个人中心页
│   │       ├── consultation/  # 咨询预约页
│   │       ├── dialogue/      # 咨询对话页
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
│   │   │   ├── profile/       # 个人中心接口
│   │   │   ├── consultation/  # 咨询预约接口
│   │   │   ├── dialogue/      # 咨询对话接口
│   │   │   ├── admin/         # 后台管理接口
│   │   │   └── public/        # 公共信息接口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py     # 配置文件
│   │   │   ├── security.py   # 安全相关
│   │   │   └── deps.py       # 依赖注入
│   │   ├── models/            # 数据库模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── rag/          # RAG 服务
│   │   │   ├── email/        # 邮件服务
│   │   │   ├── storage/      # 存储服务
│   │   │   └── auth/         # 认证服务
│   │   ├── utils/             # 工具函数
│   │   │   ├── database/     # 数据库工具
│   │   │   ├── security/     # 安全工具
│   │   │   ├── validators/   # 验证器
│   │   │   └── helpers/      # 辅助函数
│   │   ├── middleware/        # 中间件
│   │   ├── static/            # 静态文件
│   │   └── main.py           # 应用入口
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试
│   ├── requirements.txt      # 依赖
│   └── .env.example          # 环境变量示例
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
│   │   ├── database/          # 数据库设计
│   │   ├── api/               # API 设计
│   │   └── ui/                # UI 设计
│   ├── member-a/              # 开发人员 A 的文档
│   │   ├── 功能设计.md
│   │   ├── 接口文档.md
│   │   └── 实现章节.md
│   ├── member-b/              # 开发人员 B 的文档
│   │   ├── 功能设计.md
│   │   ├── 接口文档.md
│   │   └── 实现章节.md
│   └── meeting/               # 会议记录
│
├── shared/                     # 共享资源
│   └── assets/                # 共享素材
│
└── README.md                   # 项目说明
```

## 数据库表

- 用户表 (普通用户 / 咨询师)
- 管理员表
- 心理测试问卷表
- 测试结果表
- 预约订单表
- 对话记录表
- 心理知识表

## 开发规范

### 接口命名规范
- 后端路由前缀: `/api/v1`
- 各模块路由:
  - `/api/v1/auth` - 登录注册
  - `/api/v1/chat` - 智能问答 (RAG)
  - `/api/v1/test` - 心理测试
  - `/api/v1/profile` - 个人中心
  - `/api/v1/consultation` - 咨询预约
  - `/api/v1/dialogue` - 咨询对话
  - `/api/v1/admin` - 后台管理
  - `/api/v1/public` - 公共信息

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
- RAG 检索增强问答
- 对话记录管理
- 语音转文字
- 对话标签管理

### 心理测试模块 (test)
- 问卷查询与筛选
- 答题进度保存
- 结果计算与展示
- 测试统计分析

### 个人中心模块 (profile)
- 用户信息管理
- 隐私设置
- 数据统计汇总

### 咨询预约模块 (consultation)
- 咨询师信息展示
- 预约订单管理
- 预约提醒
- 咨询评价

### 咨询对话模块 (dialogue)
- 实时对话
- 消息轮询
- 对话加密存储
- 咨询结束处理

### 后台管理模块 (admin)
- 咨询师资质审核
- 心理知识管理
- 用户/订单管控
- 数据统计分析

### 公共信息模块 (public)
- 心理知识展示
- 咨询师推荐
- 信息收藏分享

## 快速开始

### 前端
```bash
cd frontend
npm install
npm run dev
```

### 后端
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 配置 .env 文件中的数据库和邮件等信息
uvicorn app.main:app --reload
```

### 数据库
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE soulstation CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行迁移
cd backend
alembic upgrade head
```

## 许可证

MIT License
