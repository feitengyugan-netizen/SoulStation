<template>
  <div class="counselor-orders">
    <PageHeader />
    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">
          <el-icon class="title-icon"><User /></el-icon>
          咨询师工作台
        </h1>
        <p class="page-subtitle">管理您的预约订单和咨询服务</p>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">待处理</p>
              <p class="stat-value">{{ counts.pending || 0 }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon confirmed">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">已确认</p>
              <p class="stat-value">{{ counts.confirmed || 0 }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon inprogress">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">进行中</p>
              <p class="stat-value">{{ counts.inprogress || 0 }}</p>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon completed">
              <el-icon><CircleCheckFilled /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">已完成</p>
              <p class="stat-value">{{ counts.completed || 0 }}</p>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 订单标签页 -->
      <el-card class="tabs-card" shadow="never">
        <el-tabs v-model="activeTab" @tab-change="loadOrders" class="order-tabs">
          <el-tab-pane name="pending">
            <template #label>
              <span class="tab-label">
                <el-icon><Clock /></el-icon>
                待处理
                <el-badge v-if="counts.pending" :value="counts.pending" class="tab-badge" />
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane name="confirmed">
            <template #label>
              <span class="tab-label">
                <el-icon><CircleCheck /></el-icon>
                已确认
                <el-badge v-if="counts.confirmed" :value="counts.confirmed" class="tab-badge" />
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane name="inprogress">
            <template #label>
              <span class="tab-label">
                <el-icon><ChatDotRound /></el-icon>
                进行中
                <el-badge v-if="counts.inprogress" :value="counts.inprogress" class="tab-badge" />
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane name="completed">
            <template #label>
              <span class="tab-label">
                <el-icon><CircleCheckFilled /></el-icon>
                已完成
                <el-badge v-if="counts.completed" :value="counts.completed" class="tab-badge" />
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
                      <span class="time-text">{{ order.date }} {{ order.timeSlot }}</span>
                    </div>
                    <el-tag :type="getStatusType(order.status)" size="large" effect="plain">
                      {{ getStatusText(order.status) }}
                    </el-tag>
                  </div>

                  <div class="order-divider"></div>

                  <div class="user-info">
                    <div class="user-avatar">
                      <el-icon class="avatar-icon"><User /></el-icon>
                    </div>
                    <div class="user-details">
                      <h3 class="user-name">{{ order.userName }}</h3>
                      <p class="order-id">订单号 #{{ order.id }}</p>
                    </div>
                  </div>

                  <div class="problem-section">
                    <p class="problem-label">
                      <el-icon><Document /></el-icon>
                      问题描述
                    </p>
                    <p class="problem-text">{{ order.description || '暂无描述' }}</p>
                  </div>

                  <div class="order-meta">
                    <div class="meta-item">
                      <el-icon class="meta-icon"><VideoCamera v-if="order.type === 'video'" />
                        <Phone v-else-if="order.type === 'voice'" />
                        <Location v-else />
                      </el-icon>
                      <span>{{ getTypeText(order.type) }}</span>
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
                    <el-button type="success" size="large" @click="agreeOrder(order)" plain>
                      <el-icon><Select /></el-icon>
                      同意预约
                    </el-button>
                    <el-button type="danger" size="large" @click="rejectOrder(order)" plain>
                      <el-icon><Close /></el-icon>
                      拒绝预约
                    </el-button>
                  </template>
                  <template v-else-if="order.status === 'confirmed' || order.status === 'inprogress'">
                    <el-button type="primary" size="large" @click="startChat(order)">
                      <el-icon><ChatDotRound /></el-icon>
                      进入咨询
                    </el-button>
                  </template>
                  <template v-else-if="order.status === 'completed'">
                    <el-button size="large" @click="viewReview(order)" plain>
                      <el-icon><View /></el-icon>
                      查看评价
                    </el-button>
                    <el-button type="danger" size="large" @click="deleteOrder(order.id)" plain style="margin-top: 8px;">
                      <el-icon><Delete /></el-icon>
                      删除订单
                    </el-button>
                  </template>
                  <template v-else-if="order.status === 'cancelled'">
                    <el-button type="danger" size="large" @click="deleteOrder(order.id)" plain>
                      <el-icon><Delete /></el-icon>
                      删除订单
                    </el-button>
                  </template>
                </div>
              </div>
            </el-card>
          </div>

          <el-empty v-if="!loading && orders.length === 0" description="暂无订单" :image-size="200">
            <template #description>
              <p class="empty-text">该分类下暂无订单</p>
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
  User, Clock, CircleCheck, ChatDotRound, CircleCheckFilled,
  Calendar, Document, VideoCamera, Phone, Location, Money,
  Select, Close, View, Delete
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorOrders, handleOrder, deleteAppointment } from '@/api/consultation'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('pending')
const orders = ref([])
const counts = ref({})

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getCounselorOrders({ status: activeTab.value })
    orders.value = res.data.list || []
    Object.assign(counts.value, res.data.counts || {})
  } finally {
    loading.value = false
  }
}

const getTypeText = (type) => ({ video: '视频咨询', voice: '语音咨询', offline: '线下咨询' }[type] || type)

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    confirmed: 'success',
    inprogress: 'primary',
    completed: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    confirmed: '已确认',
    inprogress: '进行中',
    completed: '已完成'
  }
  return texts[status] || status
}

const agreeOrder = async (order) => {
  try {
    await ElMessageBox.confirm(
      `确定接受用户"${order.userName}"的预约吗？\\n预约时间：${order.date} ${order.timeSlot}`,
      '确认接受预约',
      {
        confirmButtonText: '接受',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    await handleOrder(order.id, { action: 'agree' })
    ElMessage.success('已成功接受预约')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const rejectOrder = async (order) => {
  try {
    const { value } = await ElMessageBox.prompt(
      `请输入拒绝用户"${order.userName}"预约的理由：`,
      '拒绝预约',
      {
        confirmButtonText: '确认拒绝',
        cancelButtonText: '取消',
        inputPattern: /.+/,
        inputErrorMessage: '请输入拒绝理由',
        type: 'warning'
      }
    )
    await handleOrder(order.id, { action: 'reject', reason: value })
    ElMessage.success('已拒绝该预约')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const startChat = (order) => {
  router.push(`/consultation/counselor/${order.id}`)
}

const viewReview = (order) => {
  ElMessageBox.alert(
    `用户评分：${order.rating || 5} 星\\n\\n评价内容：\\n${order.review || '用户暂未填写评价'}`,
    '评价详情',
    {
      confirmButtonText: '关闭',
      customClass: 'review-dialog'
    }
  )
}

const deleteOrder = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除此订单吗？删除后订单将从数据库中完全移除，无法恢复。',
      '删除订单',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: true
      }
    )
    await deleteAppointment(id)
    ElMessage.success('订单已删除')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

onMounted(() => loadOrders())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;

.counselor-orders {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-xl;
}

/* 页面头部 */
.page-header {
  margin-bottom: $spacing-xl;
  text-align: center;
}

.page-title {
  font-size: 32px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 $spacing-sm 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
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

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
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
  gap: $spacing-md;
  padding: $spacing-md;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
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

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin: 0 0 $spacing-xs 0;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

/* 标签卡片 */
.tabs-card {
  border-radius: 16px;
  overflow: hidden;
}

.order-tabs {
  padding: 0 $spacing-lg;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 15px;
}

.tab-badge {
  margin-left: $spacing-xs;
}

/* 订单列表 */
.order-list {
  padding: $spacing-lg;
  min-height: 400px;
}

.order-item {
  margin-bottom: $spacing-lg;
}

.order-item:last-child {
  margin-bottom: 0;
}

.order-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
}

.order-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
  transform: translateY(-2px);
}

.order-card-content {
  display: flex;
  justify-content: space-between;
  gap: $spacing-lg;
}

.order-main {
  flex: 1;
}

.order-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.order-time {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
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
  margin: $spacing-md 0;
}

/* 用户信息 */
.user-info {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.user-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  font-size: 24px;
  color: white;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 $spacing-xs 0;
}

.order-id {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

/* 问题描述 */
.problem-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
}

.problem-label {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin: 0 0 $spacing-xs 0;
}

.problem-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

/* 订单元信息 */
.order-meta {
  display: flex;
  gap: $spacing-xl;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
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

/* 操作按钮 */
.order-actions {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
  min-width: 140px;
}

.order-actions .el-button {
  width: 100%;
}

/* 空状态 */
.empty-text {
  font-size: 16px;
  color: #909399;
  margin-top: $spacing-md;
}

/* 响应式 */
@media (max-width: 768px) {
  .container {
    padding: $spacing-md;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: $spacing-md;
  }

  .order-card-content {
    flex-direction: column;
  }

  .order-actions {
    flex-direction: row;
    width: 100%;
  }

  .order-meta {
    flex-direction: column;
    gap: $spacing-sm;
  }
}
</style>
