# 咨询师工作台订单访问问题解决方案

## ✅ API测试结果

**好消息！后端API完全正常工作！**

测试结果显示：
- ✅ 咨询师账号登录成功
- ✅ 能正确获取订单列表：6个订单
- ✅ 订单状态分类：1个待确认、1个已确认、3个已完成
- ✅ 订单数据完整：用户名、订单号、状态、日期等

## 🔑 测试账号信息

**咨询师测试账号：**
```
邮箱: teacher_wang@example.com
密码: 123456
角色: counselor (咨询师)
对应咨询师ID: 1 (王老师)
```

**订单数据：**
- 总订单数: 6个
- 待确认: 1个 (士大夫，语音咨询)
- 已确认: 1个 (测试用户，视频咨询)
- 已完成: 3个 (小明同学、小红同学、David)

## 🎯 解决方案

### 方案1: 使用正确的咨询师账号登录

**步骤：**
1. 退出当前账号
2. 使用咨询师账号登录：`teacher_wang@example.com` / `123456`
3. 访问工作台：`http://localhost:5173/consultation/counselor/dashboard`
4. 应该能看到统计数据和订单列表

### 方案2: 检查用户角色设置

如果使用其他账号，需要确保该账号的角色是`counselor`：

```sql
-- 检查用户角色
SELECT id, email, nickname, role FROM users WHERE role = 'counselor';

-- 更新用户角色为咨询师
UPDATE users SET role = 'counselor' WHERE email = 'your_email@example.com';
```

### 方案3: 创建新的咨询师测试账号

```python
# 在后端目录执行
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()

# 创建咨询师账号
new_user = User(
    email='counselor_test@example.com',
    nickname='测试咨询师',
    password_hash=get_password_hash('123456'),
    role='counselor',
    status='active'
)
db.add(new_user)
db.commit()

print(f"创建账号成功: counselor_test@example.com / 123456")
```

## 🔧 前端调试步骤

### 1. 检查当前登录状态

在浏览器控制台执行：
```javascript
console.log('当前用户信息:')
console.log('Token:', localStorage.getItem('token'))
console.log('用户角色:', localStorage.getItem('userRole'))
```

### 2. 测试API调用

在浏览器控制台执行：
```javascript
// 测试获取咨询师订单
fetch('http://localhost:8000/api/consultation/counselor/orders', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(response => response.json())
.then(data => console.log('订单数据:', data))
```

### 3. 检查路由权限

确保前端路由配置正确：
- 路由路径: `/consultation/counselor/dashboard`
- 权限要求: `requiresCounselor: true`
- 用户角色: `counselor`

## 📋 完整测试流程

### 1. 后端API测试（已完成✅）
```bash
cd backend
python test_counselor_dashboard.py
```

### 2. 前端功能测试
```
1. 访问登录页面: http://localhost:5173/login
2. 使用咨询师账号登录: teacher_wang@example.com / 123456
3. 访问工作台: http://localhost:5173/consultation/counselor/dashboard
4. 检查统计数据和订单列表
```

### 3. 新用户预约测试
```
1. 普通用户登录: xiaoming@example.com / 123456
2. 访问找咨询师: http://localhost:5173/counselor
3. 选择咨询师（ID=1 王老师）
4. 完成预约流程
5. 退出登录，用咨询师账号登录查看新订单
```

## 🎯 预期结果

### 咨询师工作台应该显示：
- **统计数据卡片**:
  - 总订单数: 6
  - 待处理: 1
  - 已完成: 3
  - 平均评分: 4.9

- **最近预约列表**:
  - APT20260407235043ABEDE8 (待确认) - 士大夫
  - APT20260407112758B71E44 (已取消) - 测试用户
  - APT20260407A44B8E9C (已完成) - 小明同学
  - 等更多...

- **快捷功能**:
  - 我的预约: 查看所有订单
  - 个人资料: 编辑信息
  - 查看主页: 公开页面
  - 智能问答: AI助手

## 🐛 常见问题排查

### 问题1: 登录后看不到工作台菜单
**原因**: 用户角色不是counselor
**解决**: 使用teacher_wang@example.com登录，或更新用户角色

### 问题2: API调用401/403错误
**原因**: Token过期或权限不足
**解决**: 重新登录，确保使用咨询师账号

### 问题3: 工作台显示暂无数据
**原因**: API调用失败或数据格式问题
**解决**: 
1. 检查浏览器控制台网络请求
2. 确认后端服务正常运行
3. 查看API返回的错误信息

### 问题4: 路由跳转到登录页
**原因**: 权限验证失败
**解决**: 确保账号角色正确，Token有效

## 📱 访问地址

- **后端API**: http://localhost:8000/api
- **前端应用**: http://localhost:5173
- **咨询师工作台**: http://localhost:5173/consultation/counselor/dashboard
- **登录页面**: http://localhost:5173/login
- **找咨询师**: http://localhost:5173/counselor

## 🚀 立即测试

**快速测试步骤：**
1. 访问: http://localhost:5173/login
2. 使用咨询师账号登录: `teacher_wang@example.com` / `123456`
3. 访问工作台: http://localhost:5173/consultation/counselor/dashboard
4. 查看统计数据和最近预约列表

**应该能看到：**
- ✅ 欢迎卡片显示咨询师信息
- ✅ 统计数据显示正确的订单数量
- ✅ 最近预约列表显示6个订单
- ✅ 快捷入口可以正常使用

---

**总结**: 后端API工作正常，问题可能是前端登录用户角色不对。请使用提供的咨询师测试账号进行测试！