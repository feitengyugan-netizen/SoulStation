<template>
  <div class="user-orders">
    <PageHeader />

    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">
          <el-icon class="title-icon"><Calendar /></el-icon>
          我的预约
        </h1>
        <p class="page-subtitle">管理您的咨询预约</p>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <el-card class="stat-card" shadow="hover" @click="activeTab = 'pending'">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">待确认</p>
              <p class="stat-value">{{ stats.pending || 0 }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card" shadow="hover" @click="activeTab = 'confirmed'">
          <div class="stat-content">
            <div class="stat-icon confirmed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">已确认</p>
              <p class="stat-value">{{ stats.confirmed || 0 }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card" shadow="hover" @click="activeTab = 'in_progress'">
          <div class="stat-content">
            <div class="stat-icon inprogress">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">进行中</p>
              <p class="stat-value">{{ stats.in_progress || 0 }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card" shadow="hover" @click="activeTab = 'completed'">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon><CircleCheckFilled /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">已完成</p>
              <p class="stat-value">{{ stats.completed || 0 }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 快速预约按钮 -->
      <div class="quick-actions">
        <el-button type="primary" size="large" @click="goToBooking">
          <el-icon><Plus /></el-icon>
          预约咨询师
        </el-button>
      </div>

      <!-- 订单列表 -->
      <el-card class="orders-card" shadow="never">
        <el-tabs v-model="activeTab" @tab-change="loadOrders" class="order-tabs">
          <el-tab-pane name="pending">
            <template #label>
              <span class="tab-label">
                <el-icon><Clock /></el-icon>
                待确认
                <el-badge v-if="stats.pending" :value="stats.pending" class="tab-badge" />
              </span>
            </template>
          </el-tab-pane>

          <el-tab-pane name="confirmed">
            <template #label>
              <span class="tab-label">
                <el-icon><CircleCheck /></el-icon>
                已确认
                <el-badge v-if="stats.confirmed" :value="stats.confirmed" class="tab-badge" />
              </span>
            </template>
          </el-tab-pane>

          <el-tab-pane name="in_progress">
            <template #label>
              <span class="tab-label">
                <el-icon><ChatDotRound /></el-icon>
                进行中
                <el-badge v-if="stats.in_progress" :value="stats.in_progress" class="tab-badge" />
              </span>
            </template>
          </el-tab-pane>

          <el-tab-pane name="completed">
            <template #label>
              <span class="tab-label">
                <el-icon><CircleCheckFilled /></el-icon>
                已完成
                <el-badge v-if="stats.completed" :value="stats.completed" class="tab-badge" />
              </span>
            </template>
          </el-tab-pane>

          <el-tab-pane name="cancelled">
            <template #label>
              <span class="tab-label">
                <el-icon><Close /></el-icon>
                已取消
              </span>
            </template>
          </el-tab-pane>
        </el-tabs>

        <div v-loading="loading" class="order-list">
          <div v-for="order in orders" :key="order.id" class="order-item">
            <el-card class="order-card" shadow="hover">
              <div class="order-card-content">
                <!-- 左侧：订单信息 -->
                <div class="order-main">
                  <div class="order-top">
                    <div class="order-time">
                      <el-icon class="time-icon"><Calendar /></el-icon>
                      <span class="time-text">{{ formatDate(order.appointment_date) }}</span>
                    </div>
                    <el-tag :type="getStatusType(order.status)" size="large">
                      {{ getStatusText(order.status) }}
                    </el-tag>
                  </div>

                  <div class="order-divider"></div>

                  <!-- 咨询师信息 -->
                  <div class="counselor-info">
                    <div class="counselor-avatar">
                      <el-avatar :size="50" :src="order.counselorAvatar">
                        <el-icon><User /></el-icon>
                      </el-avatar>
                    </div>
                    <div class="counselor-details">
                      <h3 class="counselor-name">{{ order.counselorName }}</h3>
                      <p class="counselor-title">{{ order.counselorTitle || '心理咨询师' }}</p>
                    </div>
                  </div>

                  <div class="problem-section">
                    <p class="problem-label">
                      <el-icon><Document /></el-icon>
                      咨询问题
                    </p>
                    <p class="problem-text">{{ order.problem_description || '暂无描述' }}</p>
                  </div>

                  <div class="order-meta">
                    <div class="meta-item">
                      <el-icon class="meta-icon">
                        <VideoCamera v-if="order.consultation_type === 'video'" />
                        <Phone v-else-if="order.consultation_type === 'voice'" />
                        <Location v-else />
                      </el-icon>
                      <span>{{ getTypeText(order.consultation_type) }}</span>
                    </div>
                    <div class="meta-item">
                      <el-icon class="meta-icon"><Money /></el-icon>
                      <span class="price">¥{{ order.price }}</span>
                    </div>
                  </div>
                </div>

                <!-- 右侧：操作按钮 -->
                <div class="order-actions">
                  <template v-if="order.status === 'pending'">
                    <el-button type="danger" size="large" @click="cancelOrder(order)" plain>
                      <el-icon><Close /></el-icon>
                      取消预约
                    </el-button>
                  </template>

                  <template v-else-if="order.status === 'confirmed' || order.status === 'in_progress'">
                    <el-button type="primary" size="large" @click="startChat(order)">
                      <el-icon><ChatDotRound /></el-icon>
                      进入咨询
                    </el-button>
                  </template>

                  <template v-else-if="order.status === 'completed'">
                    <el-button
                      v-if="!order.reviewed"
                      type="warning"
                      size="large"
                      @click="goToReview(order)"
                      plain
                    >
                      <el-icon><Star /></el-icon>
                      评价咨询
                    </el-button>
                    <el-button v-else size="large" disabled plain>
                      <el-icon><Check /></el-icon>
                      已评价
                    </el-button>
                  </template>
                </div>
              </div>
            </el-card>
          </div>

          <el-empty v-if="!loading && orders.length === 0" description="暂无订单" :image-size="200">
            <template #description>
              <p class="empty-text">该分类下暂无订单</p>
              <el-button type="primary" @click="goToBooking">立即预约</el-button>
            </template>
          </el-empty>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Calendar, Clock, CircleCheck, ChatDotRound, CircleCheckFilled,
  Close, Document, VideoCamera, Phone, Location, Money,
  User, Plus, Star, Check
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getUserOrders, cancelAppointment } from '@/api/userOrders'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('in_progress')
const orders = ref([])
const stats = ref({})

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getUserOrders({ status: activeTab.value })
    orders.value = res.data.list || []
    Object.assign(stats.value, res.data.stats || {})
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败')
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getTypeText = (type) => ({
  video: '视频咨询',
  voice: '语音咨询',
  offline: '线下咨询'
})[type] || type

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'primary',
    completed: 'info',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待确认',
    confirmed: '已确认',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const startChat = (order) => {
  router.push(`/consultation/user/${order.id}`)
}

const cancelOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消与${order.counselorName}的预约吗？`,
      '取消预约',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '再想想',
        type: 'warning'
      }
    )

    await cancelAppointment(order.id)
    ElMessage.success('预约已取消')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

const goToReview = (order) => {
  router.push({
    path: '/consultation/review',
    query: { appointmentId: order.id }
  })
}

const goToBooking = () => {
  router.push('/counselor')
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.user-orders {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  text-align: center;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  color: #409eff;
}

.page-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.pending {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
}

.stat-icon.confirmed {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
}

.stat-icon.inprogress {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
}

.stat-icon.completed {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 0 0 4px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.quick-actions {
  text-align: center;
  margin-bottom: 20px;
}

.orders-card {
  border-radius: 16px;
  overflow: hidden;
}

.order-tabs {
  padding: 0 20px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.order-list {
  padding: 20px;
  min-height: 400px;
}

.order-item {
  margin-bottom: 20px;
}

.order-item:last-child {
  margin-bottom: 0;
}

.order-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.order-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
}

.order-card-content {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.order-main {
  flex: 1;
}

.order-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.time-icon {
  font-size: 18px;
  color: #409eff;
}

.time-text {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.order-divider {
  height: 1px;
  background: linear-gradient(to right, transparent, #e4e7ed, transparent);
  margin: 16px 0;
}

.counselor-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.counselor-name {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.counselor-title {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.problem-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
}

.problem-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin: 0 0 8px 0;
}

.problem-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.order-meta {
  display: flex;
  gap: 24px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #606266;
}

.meta-icon {
  font-size: 16px;
  color: #409eff;
}

.price {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}

.order-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 140px;
}

.order-actions .el-button {
  width: 100%;
}

.empty-text {
  font-size: 16px;
  color: #909399;
  margin: 16px 0;
}

@media (max-width: 768px) {
  .container {
    padding: 12px;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .order-card-content {
    flex-direction: column;
  }

  .order-actions {
    flex-direction: row;
    width: 100%;
  }
}
</style>
