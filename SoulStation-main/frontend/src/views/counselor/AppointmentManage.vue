<template>
  <div class="appointment-manage-page">
    <PageHeader />

    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">
          <el-icon class="title-icon"><Calendar /></el-icon>
          我的预约
        </h1>
        <p class="page-subtitle">管理您的咨询预约记录</p>
      </div>

      <!-- 统计卡片 -->
      <div class="stats-grid">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon pending">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">待确认</p>
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
          <el-tab-pane name="all">
            <template #label>
              <span class="tab-label">
                <el-icon><List /></el-icon>
                全部预约
              </span>
            </template>
          </el-tab-pane>
          <el-tab-pane name="pending">
            <template #label>
              <span class="tab-label">
                <el-icon><Clock /></el-icon>
                待确认
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
          <el-tab-pane name="cancelled">
            <template #label>
              <span class="tab-label">
                <el-icon><Close /></el-icon>
                已取消
                <el-badge v-if="counts.cancelled" :value="counts.cancelled" class="tab-badge" />
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

                  <div class="counselor-info">
                    <div class="counselor-avatar">
                      <el-avatar :size="50" :src="order.counselor?.avatar">
                        <el-icon :size="25"><User /></el-icon>
                      </el-avatar>
                    </div>
                    <div class="counselor-details">
                      <h3 class="counselor-name">{{ order.counselorName }}</h3>
                      <div class="counselor-rating" v-if="order.counselor">
                        <el-rate
                          v-model="order.counselor.rating"
                          disabled
                          show-score
                          score-template="{value}"
                          :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                        />
                      </div>
                    </div>
                  </div>

                  <div class="problem-section" v-if="order.description">
                    <p class="problem-label">
                      <el-icon><Document /></el-icon>
                      问题描述
                    </p>
                    <p class="problem-text">{{ order.description }}</p>
                  </div>

                  <div class="order-meta">
                    <div class="meta-item">
                      <el-icon class="meta-icon">
                        <VideoCamera v-if="order.type === 'video'" />
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
                    <el-button type="danger" size="large" @click="cancelOrder(order.id)" plain>
                      <el-icon><Close /></el-icon>
                      取消预约
                    </el-button>
                  </template>
                  <template v-else-if="order.status === 'confirmed' || order.status === 'inprogress'">
                    <el-button type="primary" size="large" disabled>
                      <el-icon><Clock /></el-icon>
                      等待咨询
                    </el-button>
                  </template>
                  <template v-else-if="order.status === 'completed'">
                    <el-button
                      v-if="!order.rating"
                      type="success"
                      size="large"
                      @click="goToReview(order.id)"
                      plain
                    >
                      <el-icon><Edit /></el-icon>
                      写评价
                    </el-button>
                    <el-button v-else type="info" size="large" disabled>
                      <el-icon><CircleCheckFilled /></el-icon>
                      已评价
                    </el-button>
                    <!-- 已完成订单显示删除按钮 -->
                    <el-button
                      type="danger"
                      size="large"
                      @click="deleteOrder(order.id)"
                      plain
                      style="margin-top: 8px;"
                    >
                      <el-icon><Delete /></el-icon>
                      删除订单
                    </el-button>
                  </template>
                  <template v-else-if="order.status === 'cancelled'">
                    <!-- 已取消订单显示删除按钮 -->
                    <el-button
                      type="danger"
                      size="large"
                      @click="deleteOrder(order.id)"
                      plain
                    >
                      <el-icon><Delete /></el-icon>
                      删除订单
                    </el-button>
                  </template>
                </div>
              </div>
            </el-card>
          </div>

          <el-empty v-if="!loading && orders.length === 0" description="暂无预约记录" :image-size="200">
            <template #description>
              <p class="empty-text">该分类下暂无预约记录</p>
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
  List, VideoCamera, Phone, Location, Money, Document, User,
  Close, Edit, Delete
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getUserAppointments, cancelAppointment, deleteAppointment } from '@/api/counselor'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('all')
const orders = ref([])
const counts = ref({})

const loadOrders = async () => {
  loading.value = true
  try {
    const status = activeTab.value === 'all' ? '' : activeTab.value
    const res = await getUserAppointments({ status })
    orders.value = res.data.list || []

    // 计算各状态数量
    if (activeTab.value === 'all') {
      counts.value = orders.value.reduce((acc, order) => {
        acc[order.status] = (acc[order.status] || 0) + 1
        return acc
      }, {})
    }
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载预约列表失败')
  } finally {
    loading.value = false
  }
}

const getTypeText = (type) => ({
  video: '视频咨询',
  voice: '语音咨询',
  offline: '线下咨询'
}[type] || type)

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    confirmed: 'success',
    inprogress: 'primary',
    completed: 'info',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待确认',
    confirmed: '已确认',
    inprogress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const cancelOrder = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要取消此预约吗？取消后无法恢复。',
      '取消预约',
      {
        confirmButtonText: '确认取消',
        cancelButtonText: '再想想',
        type: 'warning'
      }
    )
    await cancelAppointment(id)
    ElMessage.success('预约已取消')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消失败:', error)
      ElMessage.error('取消失败，请稍后重试')
    }
  }
}

const goToReview = (id) => {
  router.push(`/counselor/review/${id}`)
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

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.appointment-manage-page {
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
  text-align: center;
  margin-bottom: $spacing-xl;
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

/* 咨询师信息 */
.counselor-info {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.counselor-avatar {
  flex-shrink: 0;
}

.counselor-details {
  flex: 1;
}

.counselor-name {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 $spacing-xs 0;
}

.counselor-rating {
  :deep(.el-rate) {
    .el-rate__icon {
      font-size: 16px;
    }
  }
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
