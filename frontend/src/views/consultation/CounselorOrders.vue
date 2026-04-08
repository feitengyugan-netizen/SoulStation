<template>
  <div class="counselor-orders">
    <div class="container">
      <h2 class="page-title">咨询师工作台</h2>

      <el-tabs v-model="activeTab" @tab-change="loadOrders" class="custom-tabs">
        <el-tab-pane label="待处理" name="pending"></el-tab-pane>
        <el-tab-pane label="咨询中" name="active"></el-tab-pane>
        <el-tab-pane label="已完成" name="completed"></el-tab-pane>
        <el-tab-pane label="已取消" name="cancelled"></el-tab-pane>
      </el-tabs>

      <div v-loading="loading" class="order-list">
        <div v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-header">
            <div class="title-row">
              <span class="order-no">{{ order.appointment_no }}</span>
              <el-tag :type="getStatusType(order.status)" size="large" class="status-tag">
                {{ getStatusText(order.status) }}
              </el-tag>
            </div>
            <div class="order-time">{{ formatDate(order.appointment_date) }}</div>
          </div>

          <div class="order-body">
            <div class="user-info">
              <h3 class="user-name">{{ order.user_name || '未知用户' }}</h3>
              <p class="problem-desc">{{ order.problem_description || '暂无描述' }}</p>
            </div>

            <div class="order-details">
              <div class="detail-item">
                <span class="label">咨询方式</span>
                <span class="value">{{ getTypeText(order.consultation_type) }}</span>
              </div>
              <div class="detail-item">
                <span class="label">费用</span>
                <span class="value price">¥{{ order.price }}</span>
              </div>
              <div class="detail-item">
                <span class="label">时长</span>
                <span class="value">{{ order.duration }}分钟</span>
              </div>
            </div>
          </div>

          <div class="order-actions">
            <template v-if="order.status === 'pending'">
              <el-button type="success" size="large" @click="agreeOrder(order)">接受预约</el-button>
              <el-button type="danger" size="large" @click="rejectOrder(order)">拒绝预约</el-button>
            </template>
            <template v-else-if="order.status === 'confirmed' || order.status === 'in_progress'">
              <el-button type="primary" size="large" @click="startChat(order)">
                {{ order.status === 'in_progress' ? '继续咨询' : '进入咨询' }}
              </el-button>
            </template>
            <template v-else-if="order.status === 'completed'">
              <el-button size="large" @click="viewReview(order)">查看评价</el-button>
            </template>
          </div>
        </div>

        <div v-if="!loading && orders.length === 0" class="empty-state">
          <p>暂无订单</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCounselorOrders, handleOrder } from '@/api/consultation'
import dayjs from 'dayjs'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('active')  // 默认显示咨询中的订单
const orders = ref([])
const counts = ref({})

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const getStatusType = (status) => {
  const typeMap = {
    pending: 'warning',
    confirmed: 'success',
    in_progress: 'primary',
    completed: 'info',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '待处理',
    confirmed: '已确认',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return textMap[status] || status
}

const loadOrders = async () => {
  loading.value = true
  try {
    console.log('开始加载订单数据，状态:', activeTab.value)

    // 根据标签页状态获取相应的订单
    let statusFilter = activeTab.value
    let params = {
      page: 1,
      pageSize: 10
    }

    // 对于"咨询中"标签，需要同时获取confirmed和in_progress状态的订单
    if (activeTab.value === 'active') {
      // 获取confirmed状态
      const [confirmedResp, inProgressResp] = await Promise.all([
        getCounselorOrders({ ...params, status_filter: 'confirmed' }),
        getCounselorOrders({ ...params, status_filter: 'in_progress' })
      ])

      if (confirmedResp.code === 200 && inProgressResp.code === 200) {
        const confirmedOrders = confirmedResp.data.items || []
        const inProgressOrders = inProgressResp.data.items || []
        orders.value = [...confirmedOrders, ...inProgressOrders]

        console.log('咨询中订单（confirmed）:', confirmedOrders.length)
        console.log('咨询中订单（in_progress）:', inProgressOrders.length)
        console.log('总计:', orders.value.length)
      } else {
        orders.value = []
      }
    } else {
      // 其他状态正常获取
      params.status_filter = statusFilter
      const res = await getCounselorOrders(params)
      console.log('API响应:', res)

      if (res.code === 200 && res.data) {
        orders.value = res.data.items || []
      } else {
        orders.value = []
      }
    }

    // 验证订单列表
    console.log('当前咨询师订单列表:', orders.value.map(o => ({
      id: o.id,
      status: o.status,
      user_name: o.user_name
    })))

    // 更新统计（需要获取所有订单）
    const allResp = await getCounselorOrders({ page: 1, pageSize: 100 })
    if (allResp.code === 200) {
      const allOrders = allResp.data.items || []
      counts.value = {
        pending: allOrders.filter(o => o.status === 'pending').length,
        active: allOrders.filter(o => o.status === 'confirmed' || o.status === 'in_progress').length,
        completed: allOrders.filter(o => o.status === 'completed').length,
        cancelled: allOrders.filter(o => o.status === 'cancelled').length
      }
    }

    console.log('订单数据加载成功:', orders.value.length, '条')
    console.log('统计数据:', counts.value)
  } catch (error) {
    console.error('加载订单失败:', error)
    orders.value = []
  } finally {
    loading.value = false
  }
}

const getTypeText = (type) => ({ video: '视频', voice: '语音', offline: '线下' }[type] || type)

const agreeOrder = async (order) => {
  try {
    await ElMessageBox.confirm('确定接受此预约吗？', '提示')
    await handleOrder(order.id, { action: 'agree' })
    ElMessage.success('已接受')
    loadOrders()
  } catch (error) { if (error !== 'cancel') console.error(error) }
}

const rejectOrder = async (order) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝理由', '拒绝预约', {
      inputPattern: /.+/,
      inputErrorMessage: '请输入理由'
    })
    await handleOrder(order.id, { action: 'reject', reason: value })
    ElMessage.success('已拒绝')
    loadOrders()
  } catch (error) { if (error !== 'cancel') console.error(error) }
}

const startChat = (order) => {
  console.log('开始咨询，订单信息:', order)
  console.log('订单ID:', order.id)
  console.log('用户:', order.user_name)
  console.log('当前状态筛选:', activeTab.value)

  // 保存当前状态筛选，这样返回时能保持相同的标签页
  sessionStorage.setItem('counselorOrdersTab', activeTab.value)

  router.push(`/consultation/counselor/${order.id}`)
}

const viewReview = (order) => {
  ElMessageBox.alert(`用户评分: ${order.rating}星\n${order.review || '暂无评价'}`, '评价详情')
}

onMounted(() => {
  // 恢复之前保存的状态筛选
  const savedTab = sessionStorage.getItem('counselorOrdersTab')
  if (savedTab) {
    activeTab.value = savedTab
    console.log('恢复状态筛选:', savedTab)
  }
  loadOrders()
})
</script>

<style scoped>
.counselor-orders {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.custom-tabs {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
  overflow: hidden;
}

.order-list {
  margin-top: 20px;
}

.order-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.order-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  border-color: rgba(102, 126, 234, 0.2);
}

.order-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f5f7fa;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 12px;
  flex-wrap: wrap;
}

.order-no {
  font-size: 16px;
  font-weight: 700;
  color: #303133;
  font-family: 'Courier New', monospace;
}

.status-tag {
  font-weight: 600;
  border-radius: 12px;
  padding: 6px 16px;
}

.order-time {
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.order-body {
  margin-bottom: 16px;
}

.user-info {
  margin-bottom: 16px;
}

.user-name {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.problem-desc {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.order-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 8px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item .label {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.detail-item .value {
  font-size: 15px;
  color: #303133;
  font-weight: 600;
}

.detail-item .value.price {
  color: #ff6b6b;
  font-size: 16px;
}

.order-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 12px;
  border-top: 2px solid #f5f7fa;
}

.order-actions .el-button {
  border-radius: 10px;
  font-weight: 600;
  padding: 12px 24px;
  transition: all 0.3s ease;
}

.order-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #606266;
}

.empty-state p {
  font-size: 16px;
  margin: 0;
}

@media (max-width: 768px) {
  .container {
    padding: 12px;
  }

  .title-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .order-details {
    grid-template-columns: 1fr;
  }

  .order-actions {
    flex-direction: column;
  }

  .order-actions .el-button {
    width: 100%;
  }
}
</style>
