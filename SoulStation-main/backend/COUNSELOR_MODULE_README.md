# 咨询师预约模块使用指南

## 概述

咨询师预约模块已完成开发，提供完整的咨询师查询、预约管理、评价等功能。

## 功能特性

### 1. 咨询师管理
- ✅ 咨询师列表查询（支持多维度筛选）
- ✅ 咨询师详情查看
- ✅ 可预约时段查询
- ✅ 咨询师评价列表

### 2. 预约管理
- ✅ 创建预约订单
- ✅ 用户预约列表
- ✅ 取消预约
- ✅ 提交咨询评价

### 3. 数据统计
- ✅ 咨询师评分统计
- ✅ 预约数量统计
- ✅ 评价数量统计

## API接口清单

### 咨询师相关

| 接口路径 | 方法 | 功能描述 |
|----------|------|----------|
| `/api/counselor/list` | GET | 获取咨询师列表 |
| `/api/counselor/{id}` | GET | 获取咨询师详情 |
| `/api/counselor/{id}/slots` | GET | 获取可预约时段 |
| `/api/counselor/{id}/reviews` | GET | 获取咨询师评价列表 |

### 预约相关

| 接口路径 | 方法 | 功能描述 |
|----------|------|----------|
| `/api/appointment/create` | POST | 创建预约订单 |
| `/api/appointment/user/list` | GET | 获取用户预约列表 |
| `/api/appointment/{id}/cancel` | POST | 取消预约 |
| `/api/appointment/{id}/review` | POST | 提交咨询评价 |

## 数据库表结构

### Counselor（咨询师表）

```python
id                      # 咨询师ID
user_id                 # 关联用户ID
name                    # 姓名
avatar                  # 头像URL
gender                  # 性别 (male/female/secret)
title                   # 职称
specialties             # 擅长领域（逗号分隔）
consultation_types      # 咨询方式（video/voice/offline）
experience_years        # 从业年限
education               # 学历背景
qualifications          # 资质证书
price_video             # 视频咨询价格
price_voice             # 语音咨询价格
price_offline           # 线下咨询价格
rating                  # 评分（0-5）
review_count            # 评价数量
consultation_count      # 咨询次数
bio                     # 个人简介
approach                # 咨询流派/方法
achievements            # 成就荣誉
status                  # 状态 (active/inactive/suspended)
is_verified             # 是否认证
```

### Appointment（预约订单表）

```python
id                      # 预约ID
user_id                 # 用户ID
counselor_id            # 咨询师ID
appointment_no          # 预约编号
consultation_type       # 咨询方式 (video/voice/offline)
appointment_date        # 预约日期时间
duration                # 咨询时长（分钟）
user_name               # 预约人姓名
user_contact            # 联系方式
problem_description     # 问题描述
price                   # 咨询费用
paid_amount             # 已付金额
status                  # 订单状态
cancel_reason           # 取消原因
counselor_notes         # 咨询师备注
created_at              # 创建时间
confirmed_at            # 确认时间
completed_at            # 完成时间
cancelled_at            # 取消时间
```

### ConsultationReview（咨询评价表）

```python
id                      # 评价ID
appointment_id          # 预约ID
user_id                 # 用户ID
counselor_id            # 咨询师ID
rating                  # 评分（1-5）
tags                    # 评价标签（逗号分隔）
content                 # 评价内容
is_anonymous            # 是否匿名
counselor_reply         # 咨询师回复
replied_at              # 回复时间
created_at              # 创建时间
```

## 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── counselor.py         # 咨询师和预约模型（新增）
│   ├── schemas/
│   │   └── counselor.py         # 咨询师和预约schemas（新增）
│   ├── services/
│   │   └── counselor_service.py # 咨询师预约服务层（新增）
│   └── api/
│       └── counselor/
│           └── __init__.py      # 咨询师预约API路由（新增）
└── init_counselor_data.py       # 初始化测试数据（新增）
```

## 快速开始

### 1. 初始化数据库

```bash
cd backend

# 创建数据库表
python -c "from app.core.database import engine; from app.models.counselor import Base; Base.metadata.create_all(bind=engine)"

# 初始化测试咨询师数据
python init_counselor_data.py
```

### 2. 启动后端服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试API接口

```bash
# 运行测试脚本
python test_counselor_apis.py
```

### 4. 访问前端页面

- 咨询师列表：`/counselor`
- 咨询师详情：`/counselor/{id}`
- 预约表单：`/counselor/appointment/{id}`
- 我的预约：`/counselor/orders`
- 评价表单：`/counselor/review/{id}`

## API使用示例

### 获取咨询师列表

```bash
curl -X GET "http://localhost:8000/api/counselor/list?page=1&page_size=10"
```

### 搜索咨询师

```bash
curl -X GET "http://localhost:8000/api/counselor/list?keyword=焦虑&specialty=anxiety&consultation_type=video&sort=rating"
```

### 获取咨询师详情

```bash
curl -X GET "http://localhost:8000/api/counselor/1"
```

### 获取可预约时段

```bash
curl -X GET "http://localhost:8000/api/counselor/1/slots?date=2024-03-20"
```

### 创建预约

```bash
curl -X POST "http://localhost:8000/api/appointment/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "counselor_id": 1,
    "consultation_type": "video",
    "appointment_date": "2024-03-20T10:00:00",
    "user_name": "张三",
    "user_contact": "13800138000",
    "problem_description": "最近感到焦虑，希望咨询"
  }'
```

### 获取用户预约列表

```bash
curl -X GET "http://localhost:8000/api/appointment/user/list?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 取消预约

```bash
curl -X POST "http://localhost:8000/api/appointment/1/cancel?reason=临时有事" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 提交评价

```bash
curl -X POST "http://localhost:8000/api/appointment/1/review" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5.0,
    "tags": ["专业", "耐心", "有效"],
    "content": "非常专业的咨询，帮助很大！",
    "is_anonymous": false
  }'
```

## 业务规则

### 预约规则

1. **时间限制**
   - 不能预约过去的时间
   - 预约时段为整点（09:00-18:00）
   - 每个时段默认60分钟

2. **状态管理**
   - `pending` - 待确认
   - `confirmed` - 已确认
   - `in_progress` - 进行中
   - `completed` - 已完成
   - `cancelled` - 已取消
   - `refunded` - 已退款

3. **取消规则**
   - pending/confirmed/in_progress 状态可以取消
   - completed/cancelled/refunded 状态不可取消

### 评价规则

1. **评价条件**
   - 只能评价状态为 completed 的预约
   - 每个预约只能评价一次

2. **评分范围**
   - 评分范围：1.0 - 5.0
   - 支持标签评价
   - 支持匿名评价

3. **统计更新**
   - 提交评价后自动更新咨询师评分
   - 重新计算平均分
   - 更新评价数量

### 价格管理

1. **定价方式**
   - 不同咨询方式不同价格
   - video: 视频咨询
   - voice: 语音咨询
   - offline: 线下咨询

2. **价格示例**
   - 视频咨询：400-800元/小时
   - 语音咨询：300-500元/小时
   - 线下咨询：600-1000元/小时

## 测试数据

初始化脚本会创建8位测试咨询师：

| 姓名 | 职称 | 擅长领域 | 参考价格 |
|------|------|----------|----------|
| 王静怡 | 资深心理咨询师 | 焦虑、抑郁、情感 | 500元/小时 |
| 李明远 | 婚姻家庭咨询师 | 情感、家庭、职场 | 600元/小时 |
| 张雅婷 | 青少年心理咨询师 | 焦虑、职场、情感 | 450元/小时 |
| 刘志强 | 职业规划咨询师 | 职场、焦虑、家庭 | 550元/小时 |
| 陈思雨 | 情绪管理咨询师 | 抑郁、情感 | 400元/小时 |
| 赵建国 | 创伤疗愈咨询师 | 焦虑、抑郁、情感 | 800元/小时 |
| 孙美玲 | 亲子关系咨询师 | 家庭、情感 | 480元/小时 |
| 周伟 | 社交焦虑咨询师 | 焦虑、职场 | 420元/小时 |

## 注意事项

### 1. 时段冲突检测
- 创建预约时会自动检测时段冲突
- 已被预约的时段不可重复预约

### 2. 状态转换
- 预约创建后状态为 pending
- 咨询师确认后变为 confirmed
- 开始咨询后变为 in_progress
- 完成咨询后变为 completed

### 3. 评价限制
- 只能评价已完成的咨询
- 评价后不可修改或删除
- 匿名评价不显示用户信息

## 扩展功能建议

未来可以考虑添加的功能：
1. 在线支付功能
2. 预约提醒通知
3. 咨询室视频通话
4. 咨询记录管理
5. 咨询师排班管理
6. 优惠券/折扣系统
7. 会员体系
8. 咨询师排行榜

## 问题排查

### 预约创建失败
- 检查咨询师是否存在且状态正常
- 确认预约时间格式正确
- 验证该时段未被预约
- 检查咨询师是否支持所选咨询方式

### 时段查询为空
- 确认日期格式为 YYYY-MM-DD
- 检查咨询师状态是否为 active
- 验证咨询师设置了相应咨询方式的价格

### 评价提交失败
- 确认预约状态为 completed
- 检查是否已经评价过
- 验证评分范围在 1.0-5.0 之间

## 联系支持

如有问题，请查看：
- 项目TODO.md
- API文档：http://localhost:8000/docs
- 测试脚本：test_counselor_apis.py
