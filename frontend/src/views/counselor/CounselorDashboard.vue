<template>
  <div class="counselor-dashboard-page">
    <PageHeader />

    <div class="container">
      <!-- 欢迎卡片 -->
      <el-card class="welcome-card">
        <div class="welcome-content">
          <div class="avatar-section">
            <el-avatar :size="80" :src="counselorInfo?.avatar">
              <el-icon :size="40"><component :is="icons.User" /></el-icon>
            </el-avatar>
          </div>
          <div class="info-section">
            <h2>欢迎，{{ counselorInfo?.name || '咨询师' }}</h2>
            <p class="subtitle">咨询师工作台</p>
            <div class="stats">
              <div class="stat-item">
                <span class="label">评分：</span>
                <el-rate :model-value="counselorInfo?.rating || 0" disabled show-score text-color="#ff9900" />
              </div>
              <div class="stat-item">
                <span class="label">咨询次数：</span>
                <span class="value">{{ counselorInfo?.consultation_count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="label">状态：</span>
                <el-tag :type="statusType">{{ statusText }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 快捷入口 -->
      <el-card class="quick-access-card">
        <template #header>
          <span>快捷入口</span>
        </template>

        <div class="quick-access-grid">
          <div class="access-item" @click="navigateTo('/consultation/counselor/orders')">
            <div class="access-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <el-icon :size="32"><component :is="icons.Calendar" /></el-icon>
            </div>
            <span>我的预约</span>
          </div>

          <div class="access-item" @click="navigateTo('/profile')">
            <div class="access-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <el-icon :size="32"><component :is="icons.User" /></el-icon>
            </div>
            <span>个人资料</span>
          </div>

          <div class="access-item" @click="navigateTo('/counselor')">
            <div class="access-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <el-icon :size="32"><component :is="icons.View" /></el-icon>
            </div>
            <span>查看主页</span>
          </div>

          <div class="access-item" @click="navigateTo('/chat')">
            <div class="access-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
              <el-icon :size="32"><component :is="icons.ChatDotSquare" /></el-icon>
            </div>
            <span>智能问答</span>
          </div>
        </div>
      </el-card>

      <!-- 数据统计 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
                <el-icon :size="28"><component :is="icons.Calendar" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.totalOrders || 0 }}</div>
                <div class="stat-label">总订单数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
                <el-icon :size="28"><component :is="icons.Clock" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.pendingOrders || 0 }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
                <el-icon :size="28"><component :is="icons.ChatDotRound" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ statistics.completedOrders || 0 }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
                <el-icon :size="28"><component :is="icons.Star" /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ counselorInfo?.rating || 5.0 }}</div>
                <div class="stat-label">平均评分</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 最近预约 -->
      <el-card class="recent-orders-card">
        <template #header>
          <div class="card-header">
            <span>最近预约</span>
            <el-button type="primary" link @click="navigateTo('/consultation/counselor/orders')">
              查看全部
            </el-button>
          </div>
        </template>

        <el-empty v-if="!recentOrders || recentOrders.length === 0" description="暂无预约" />
        <div v-else class="orders-list">
          <div
            v-for="order in recentOrders"
            :key="order.id"
            class="order-item"
            @click="viewOrder(order)"
          >
            <div class="order-info">
              <div class="order-title">
                <el-tag :type="getOrderStatusType(order.status)" size="small">
                  {{ getOrderStatusText(order.status) }}
                </el-tag>
                <span class="order-no">{{ order.appointment_no }}</span>
              </div>
              <div class="order-detail">
                <span>{{ formatDate(order.appointment_date) }}</span>
                <span>{{ order.consultation_type === 'video' ? '视频' : order.consultation_type === 'voice' ? '语音' : '线下' }}</span>
              </div>
            </div>
            <el-icon :size="20"><component :is="icons.ArrowRight" /></el-icon>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import {
  User,
  Calendar,
  ChatDotSquare,
  View,
  Clock,
  ChatDotRound,
  Star,
  ArrowRight
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getApplicationStatus, getCounselorAppointments } from '@/api/counselor'
import dayjs from 'dayjs'

// Mark icons as raw to prevent reactivity warnings
const icons = markRaw({
  User,
  Calendar,
  ChatDotSquare,
  View,
  Clock,
  ChatDotRound,
  Star,
  ArrowRight
})

const router = useRouter()

// 咨询师信息
const counselorInfo = ref(null)

// 统计数据
const statistics = ref({
  totalOrders: 0,
  pendingOrders: 0,
  completedOrders: 0
})

// 最近预约
const recentOrders = ref([])

// 状态计算
const statusType = computed(() => {
  const status = counselorInfo.value?.status
  if (status === 'active') return 'success'
  if (status === 'pending_review') return 'warning'
  if (status === 'inactive') return 'info'
  return 'danger'
})

const statusText = computed(() => {
  const status = counselorInfo.value?.status
  if (status === 'active') return '已激活'
  if (status === 'pending_review') return '审核中'
  if (status === 'inactive') return '未激活'
  return '已封禁'
})

// 加载咨询师信息
const loadCounselorInfo = async () => {
  try {
    const res = await getApplicationStatus()
    console.log('咨询师申请状态响应:', res)

    if (res.code === 200 && res.data) {
      // 设置咨询师基本信息
      counselorInfo.value = {
        id: res.data.counselor_id,
        name: res.data.name || res.data.nickname,
        nickname: res.data.nickname,
        avatar: res.data.avatar,
        title: res.data.title,
        rating: res.data.rating || 0,
        consultation_count: res.data.consultation_count || 0,
        status: res.data.status,
        application_status: res.data.application_status,
        has_applied: res.data.has_applied
      }
      console.log('咨询师信息已设置:', counselorInfo.value)
    } else {
      console.error('获取咨询师信息失败:', res)
    }
  } catch (error) {
    console.error('加载咨询师信息异常:', error)
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    console.log('开始加载统计数据...')
    // 从订单列表API获取数据并计算统计
    const res = await getCounselorAppointments({
      page: 1,
      pageSize: 100 // 获取更多数据用于统计
    })
    console.log('统计数据响应:', res)

    if (res.code === 200 && res.data) {
      const items = res.data.items || []
      console.log('订单数据项数量:', items.length)

      statistics.value = {
        totalOrders: res.data.total || 0,
        pendingOrders: items.filter(o => o.status === 'pending').length,
        confirmedOrders: items.filter(o => o.status === 'confirmed').length,
        completedOrders: items.filter(o => o.status === 'completed').length,
        inProgressOrders: items.filter(o => o.status === 'in_progress').length
      }
      console.log('统计数据已更新:', statistics.value)
    } else {
      console.warn('统计数据响应格式异常:', res)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    // 使用默认值
    statistics.value = {
      totalOrders: 0,
      pendingOrders: 0,
      confirmedOrders: 0,
      completedOrders: 0,
      inProgressOrders: 0
    }
  }
}

// 加载最近预约
const loadRecentOrders = async () => {
  try {
    console.log('开始加载最近预约...')
    const res = await getCounselorAppointments({
      page: 1,
      pageSize: 5
    })
    console.log('最近预约响应:', res)

    if (res.code === 200 && res.data) {
      const items = res.data.items || []
      console.log('最近预约数据项数量:', items.length)

      recentOrders.value = items.map(order => ({
        id: order.id,
        appointment_no: order.appointment_no,
        appointment_date: order.appointment_date,
        consultation_type: order.consultation_type,
        status: order.status,
        user_name: order.user_name || '匿名用户',
        user_id: order.user_id
      }))
      console.log('最近预约已更新:', recentOrders.value)
    } else {
      console.warn('最近预约响应格式异常:', res)
    }
  } catch (error) {
    console.error('加载最近预约失败:', error)
    recentOrders.value = []
  }
}

// 导航
const navigateTo = (path) => {
  router.push(path)
}

// 查看订单
const viewOrder = (order) => {
  router.push(`/consultation/user/${order.id}`)
}

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 获取订单状态类型
const getOrderStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'primary',
    completed: 'info',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const textMap = {
    pending: '待确认',
    confirmed: '已确认',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

// 组件挂载
onMounted(() => {
  loadCounselorInfo()
  loadStatistics()
  loadRecentOrders()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-dashboard-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
  overflow: hidden;

  // 添加装饰性背景元素
  &::before {
    content: '';
    position: absolute;
    top: -10%;
    right: -5%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 20s infinite ease-in-out;
  }

  &::after {
    content: '';
    position: absolute;
    bottom: -10%;
    left: -5%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(118, 75, 162, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    animation: float 15s infinite ease-in-out reverse;
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 30px); }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-lg;
  position: relative;
  z-index: 1;
}

.welcome-card {
  margin-bottom: $spacing-lg;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.15);
  }

  :deep(.el-card__body) {
    padding: 40px;
  }

  .welcome-content {
    display: flex;
    align-items: center;
    gap: $spacing-xl;

    .avatar-section {
      position: relative;

      .el-avatar {
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;

        &:hover {
          transform: scale(1.05);
          box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
        }
      }

      &::after {
        content: '';
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        z-index: -1;
        opacity: 0.1;
        animation: pulse 3s infinite;
      }
    }

    @keyframes pulse {
      0%, 100% { opacity: 0.1; transform: scale(1); }
      50% { opacity: 0.2; transform: scale(1.05); }
    }

    .info-section {
      flex: 1;

      h2 {
        margin: 0 0 $spacing-xs;
        font-size: $font-size-extra-large;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
      }

      .subtitle {
        color: $text-secondary;
        margin-bottom: $spacing-md;
        font-size: $font-size-base;
        font-weight: 500;
      }

      .stats {
        display: flex;
        gap: $spacing-xl;
        flex-wrap: wrap;

        .stat-item {
          display: flex;
          align-items: center;
          gap: $spacing-sm;
          padding: 8px 16px;
          background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
          border-radius: 20px;
          transition: all 0.3s ease;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
          }

          .label {
            color: $text-secondary;
            font-size: $font-size-small;
            font-weight: 500;
          }

          .value {
            font-weight: 700;
            color: $text-primary;
            font-size: $font-size-base;
          }
        }
      }
    }
  }
}

.quick-access-card {
  margin-bottom: $spacing-lg;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  }

  :deep(.el-card__header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-bottom: none;
    padding: 20px 30px;

    span {
      color: white;
      font-size: 18px;
      font-weight: 600;
    }
  }

  :deep(.el-card__body) {
    padding: 30px;
  }

  .quick-access-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: $spacing-lg;
  }

  .access-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: $spacing-xl;
    border-radius: 16px;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    border: 2px solid transparent;

    &:hover {
      transform: translateY(-8px) scale(1.02);
      border-color: rgba(102, 126, 234, 0.3);
      box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
    }

    &:active {
      transform: translateY(-4px) scale(0.98);
    }

    .access-icon {
      width: 70px;
      height: 70px;
      border-radius: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      margin-bottom: $spacing-md;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
      transition: all 0.3s ease;

      .access-item:hover & {
        transform: scale(1.1) rotate(5deg);
      }
    }

    span {
      font-size: $font-size-base;
      color: $text-primary;
      font-weight: 600;
      text-align: center;
    }
  }
}

.stat-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
  height: 100%;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }

  :deep(.el-card__body) {
    padding: 25px;
  }

  .stat-content {
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
      transition: all 0.3s ease;

      .stat-card:hover & {
        transform: scale(1.1) rotate(-5deg);
      }
    }

    .stat-info {
      flex: 1;

      .stat-number {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.2;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: $font-size-small;
        color: $text-secondary;
        font-weight: 500;
      }
    }
  }
}

.recent-orders-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  }

  :deep(.el-card__header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-bottom: none;
    padding: 20px 30px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: white;

      span {
        font-size: 18px;
        font-weight: 600;
      }

      .el-button {
        color: white;
        font-weight: 600;

        &:hover {
          color: rgba(255, 255, 255, 0.9);
        }
      }
    }
  }

  :deep(.el-card__body) {
    padding: 30px;
  }

  .orders-list {
    .order-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: $spacing-lg;
      border-radius: 16px;
      margin-bottom: $spacing-md;
      cursor: pointer;
      transition: all 0.3s ease;
      background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
      border: 2px solid transparent;

      &:hover {
        border-color: rgba(102, 126, 234, 0.3);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
      }

      &:last-child {
        margin-bottom: 0;
      }

      .order-info {
        flex: 1;

        .order-title {
          display: flex;
          align-items: center;
          gap: $spacing-sm;
          margin-bottom: $spacing-xs;
          flex-wrap: wrap;

          .order-no {
            font-weight: 600;
            color: $text-primary;
            font-size: $font-size-base;
          }

          .el-tag {
            font-weight: 600;
            border-radius: 12px;
            padding: 4px 12px;
            font-size: $font-size-small;
          }
        }

        .order-detail {
          display: flex;
          gap: $spacing-lg;
          font-size: $font-size-small;
          color: $text-secondary;
          font-weight: 500;

          span {
            display: flex;
            align-items: center;
            gap: 4px;

            &::before {
              content: '•';
              color: #667eea;
              font-weight: 700;
            }
          }
        }
      }

      .el-icon {
        color: #667eea;
        transition: all 0.3s ease;

        .order-item:hover & {
          transform: translateX(5px);
          color: #764ba2;
        }
      }
    }
  }
}

// 添加徽章样式
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-left: 8px;
}

// 响应式
@media (max-width: $breakpoint-md) {
  .container {
    padding: $spacing-md;
  }

  .welcome-content {
    flex-direction: column;
    text-align: center;

    .info-section {
      .stats {
        justify-content: center;
        flex-direction: column;
        gap: $spacing-sm;
      }
    }
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .order-item {
    flex-direction: column;
    align-items: flex-start !important;
    gap: $spacing-sm;

    .order-info {
      width: 100%;
    }
  }
}

// 添加加载动画
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-card,
.quick-access-card,
.stat-card,
.recent-orders-card {
  animation: fadeIn 0.6s ease-out forwards;

  &:nth-child(1) { animation-delay: 0.1s; }
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.3s; }
  &:nth-child(4) { animation-delay: 0.4s; }
}
</style>
