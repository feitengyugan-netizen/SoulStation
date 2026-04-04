# 管理员后台系统使用说明

## 🎉 新的管理员后台已完成！

参考网球场预约系统的设计风格，已为心理咨询平台创建了全新的管理员后台系统。

## 📋 功能模块

### 1. **首页 Dashboard** (`/admin/dashboard`)
- **统计卡片**: 用户总数、咨询师总数、订单总数、测试完成数
- **图表展示**:
  - 订单统计趋势图（折线图）
  - 热门心理测试分布（饼图）
- **公告列表**: 系统公告的发布和管理

### 2. **用户管理** (`/admin/users`)
- 用户列表查看
- 用户搜索和筛选
- 用户封禁/解封
- 用户行为记录

### 3. **咨询师审核** (`/admin/counselor-review`)
- 咨询师资质审核
- 审核通过/拒绝
- 咨询师档案管理

### 4. **订单管理** (`/admin/orders`)
- 订单列表查看
- 订单状态管理
- 订单数据导出

### 5. **知识管理** (`/admin/knowledge`)
- 心理知识文章管理
- 文章发布/编辑/删除
- 文章分类管理

### 6. **测试管理** (`/admin/tests`)
- 9套心理测试量表管理
- 测试题目管理
- 测试数据统计

### 7. **对话管理** (`/admin/dialogues`)
- AI对话记录查看
- 对话标签管理
- 对话数据分析

### 8. **文章编辑** (`/admin/article-editor`)
- 富文本编辑器
- 文章发布和编辑

### 9. **系统设置** (`/admin/system`)
- 网站基本设置
- 管理员账号管理
- 系统日志查看

## 🎨 设计特点

### 配色方案
- **主色调**: 深蓝色 (#1e3a8a) - 侧边栏
- **强调色**: 浅蓝色 (#3b82f6) - 激活状态
- **统计卡片**: 蓝、红、青、橙四色区分

### 布局结构
```
┌─────────────────────────────────────────────┐
│ Sidebar │  Top Navbar                       │
│ (Left)  ├────────────────────────────────────┤
│         │                                    │
│ Menu    │  Main Content Area                │
│ Items   │  - Dashboard Cards                 │
│         │  - Charts                          │
│         │  - Tables                          │
│         │  - Forms                           │
└─────────┴────────────────────────────────────┘
```

## 🚀 访问方式

### 登录入口
- **URL**: http://localhost:5174/admin/login
- **默认账号**: 根据数据库配置
- **默认密码**: 根据数据库配置

### 主要页面
- 首页: http://localhost:5174/admin/dashboard
- 用户管理: http://localhost:5174/admin/users
- 咨询师审核: http://localhost:5174/admin/counselor-review
- 订单管理: http://localhost:5174/admin/orders
- 知识管理: http://localhost:5174/admin/knowledge
- 测试管理: http://localhost:5174/admin/tests
- 对话管理: http://localhost:5174/admin/dialogues
- 文章编辑: http://localhost:5174/admin/article-editor
- 系统设置: http://localhost:5174/admin/system

## 📁 文件结构

```
frontend/src/
├── layouts/
│   └── AdminLayout.vue          # 管理员布局组件
├── views/admin/
│   ├── Dashboard.vue            # 首页Dashboard
│   ├── AdminLogin.vue           # 登录页（保留原样）
│   ├── UserManage.vue           # 用户管理
│   ├── CounselorReview.vue      # 咨询师审核
│   ├── OrderManage.vue          # 订单管理
│   ├── KnowledgeManage.vue      # 知识管理
│   ├── TestManage.vue           # 测试管理（新建）
│   ├── DialogueManage.vue       # 对话管理（新建）
│   ├── ArticleEditor.vue        # 文章编辑
│   └── SystemManage.vue         # 系统设置（新建）
└── router/
    └── index.js                  # 路由配置（已更新）
```

## ✨ 主要特性

### 1. 响应式设计
- 侧边栏可折叠
- 卡片式布局
- 移动端适配

### 2. 交互体验
- 左侧导航栏 + 顶部导航
- 面包屑导航
- 下拉菜单（用户信息、退出登录）
- 图表可视化

### 3. 权限管理
- 路由守卫（需要管理员权限）
- Token认证
- 自动跳转登录页

## 🔄 与原有系统的区别

### 原有系统
- 简单的Dashboard页面
- 没有统一的布局
- 管理页面分散

### 新系统
- 统一的左侧导航布局
- 参考专业管理后台设计
- 完整的功能模块
- 更好的用户体验

## 📝 待完善功能

以下页面已创建框架，功能待实现：

1. **TestManage.vue** - 测试管理
   - 添加/编辑测试
   - 题目管理
   - 数据统计

2. **DialogueManage.vue** - 对话管理
   - 对话记录查看
   - 数据导出
   - 标签管理

3. **SystemManage.vue** - 系统设置
   - 基本设置保存
   - 管理员管理
   - 日志查看

## 🎯 下一步建议

1. **连接后端API**
   - 将Dashboard中的模拟数据替换为真实API
   - 实现所有CRUD操作

2. **完善功能模块**
   - 实现测试管理的完整功能
   - 添加对话管理的详情查看
   - 完善系统设置的保存逻辑

3. **添加权限细化**
   - 不同管理员角色的权限控制
   - 操作日志记录

4. **性能优化**
   - 图表懒加载
   - 表格分页优化
   - 接口缓存策略

## 💡 使用提示

1. **登录后自动跳转**到Dashboard
2. **左侧菜单**可点击导航到各功能模块
3. **侧边栏折叠**：点击左上角的折叠图标
4. **退出登录**：点击右上角头像 → 退出登录

## 🐛 故障排查

### 问题1：无法访问管理页面
- 确认已登录且具有管理员权限
- 检查localStorage中的`userRole`是否为`admin`

### 问题2：图表不显示
- 检查echarts是否正确安装
- 确认DOM容器已渲染

### 问题3：路由跳转失败
- 检查路由配置是否正确
- 确认组件路径是否正确

## 📞 技术支持

如有问题，请查看：
- 项目README.md
- 前端代码注释
- 后端API文档

---

**开发完成时间**: 2026-04-04
**版本**: v2.0
**状态**: ✅ 已完成基础框架和UI设计
