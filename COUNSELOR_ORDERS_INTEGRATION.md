# 咨询师工作台订单同步功能实现

## 🎯 功能需求
当用户预约咨询师后，订单应该同时出现在咨询师的工作台中，让咨询师能够看到和管理用户的预约。

## ✅ 已实现的功能

### 1. API接口
- ✅ **获取咨询师订单列表**: `/consultation/counselor/orders`
- ✅ **处理预约订单**: `/consultation/order/{order_id}/handle`
- ✅ **获取对话消息**: `/consultation/{appointment_id}/messages`
- ✅ **发送消息**: `/consultation/{appointment_id}/message`

### 2. 前端功能
- ✅ **API接口封装**: 添加了咨询师订单相关接口
- ✅ **工作台数据加载**: 实现统计数据和最近订单的加载
- ✅ **图标优化**: 使用markRaw包装图标组件
- ✅ **订单状态管理**: 支持待确认、已确认、进行中、已完成、已取消

### 3. 数据同步机制
- ✅ **用户预约创建**: 订单数据包含咨询师ID
- ✅ **咨询师查询订单**: 通过user_id识别咨询师身份
- ✅ **订单状态更新**: 咨询师可处理用户预约

## 📋 工作台功能详情

### 统计数据
```javascript
{
  totalOrders: 0,      // 总订单数
  pendingOrders: 0,    // 待处理订单数
  completedOrders: 0   // 已完成订单数
}
```

### 最近预约列表
- 显示订单号、状态、预约时间、咨询方式
- 点击可查看订单详情
- 支持状态筛选

### 快捷入口
- **我的预约**: 跳转到订单管理页面
- **个人资料**: 编辑咨询师信息
- **查看主页**: 查看公开的咨询师页面
- **智能问答**: AI聊天助手

## 🔧 技术实现

### 前端API调用
```javascript
// 获取咨询师订单列表
export function getCounselorAppointments(params) {
  return request({
    url: '/consultation/counselor/orders',
    method: 'get',
    params
  })
}

// 获取统计数据（临时从订单列表计算）
const loadStatistics = async () => {
  try {
    const res = await getCounselorAppointments({
      page: 1,
      pageSize: 100 // 获取更多数据用于统计
    })
    if (res.code === 200) {
      const items = res.data.items || []
      statistics.value = {
        totalOrders: res.data.total || 0,
        pendingOrders: items.filter(o => o.status === 'pending').length,
        completedOrders: items.filter(o => o.status === 'completed').length
      }
    }
  } catch (error) {
    // 使用默认值
  }
}
```

### 后端数据结构
```python
@router.get("/counselor/orders")
async def get_counselor_orders(
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    user_id: int = Depends(get_current_user_info),
    db: Session = Depends(get_db)
):
    # 验证咨询师身份
    counselor = db.query(Counselor).filter(
        Counselor.user_id == user_id,
        Counselor.is_deleted == False
    ).first()

    # 获取该咨询师的订单
    result = ConsultationService.get_counselor_orders(
        db, counselor.id, status_filter, page, page_size
    )
    return result
```

## 📊 订单状态流转

```
用户预约
    ↓
pending (待确认) ← 咨询师工作台显示
    ↓
confirmed (已确认) ← 咨询师同意
    ↓
in_progress (进行中) ← 咨询开始
    ↓
completed (已完成) ← 咨询结束

或: cancelled (已取消) ← 任意阶段取消
```

## 🎨 用户界面

### 工作台布局
```
┌─────────────────────────────────┐
│     欢迎卡片                     │
│  咨询师信息 + 基本统计            │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│     快捷入口                     │
│  我的预约 | 个人资料 | 主页 | AI │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│     数据统计                     │
│  总订单 | 待处理 | 已完成 | 评分  │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│     最近预约                     │
│  订单1 (状态)                   │
│  订单2 (状态)                   │
│  订单3 (状态)                   │
└─────────────────────────────────┘
```

## 🚀 使用流程

### 用户预约流程
1. 用户在找咨询师页面选择咨询师
2. 点击预约按钮进入预约页面
3. 选择咨询方式、日期、时段
4. 填写个人信息和问题描述
5. 提交预约订单

### 咨询师处理流程
1. 登录后访问咨询师工作台
2. 在"最近预约"区域看到新订单
3. 点击"我的预约"查看所有订单
4. 对待确认订单进行同意/拒绝操作
5. 确认后与用户进行咨询

## 🔄 数据同步机制

### 实时同步
- **前端**: 定期轮询或WebSocket连接
- **后端**: 订单状态变更时推送通知
- **数据库**: 单一数据源确保一致性

### 身份验证
```python
def get_current_user_info(credentials):
    """从token获取用户ID"""
    token = credentials.credentials
    payload = decode_access_token(token)
    return int(payload.get("sub"))

# 验证咨询师身份
counselor = db.query(Counselor).filter(
    Counselor.user_id == user_id
).first()
```

## 🎯 后续优化建议

### 功能增强
1. **实时通知**: 订单状态变更时通知咨询师
2. **日历视图**: 在日历中显示预约安排
3. **订单统计图表**: 可视化展示业务数据
4. **快速操作**: 工作台直接处理待确认订单

### 性能优化
1. **缓存机制**: 缓存统计数据
2. **增量更新**: 只更新变更的订单
3. **分页加载**: 订单列表分页显示
4. **索引优化**: 数据库查询优化

---

**实现完成时间**: 2026-04-08
**功能状态**: ✅ 已实现
**测试状态**: 🔄 待测试