<template>
  <div class="counselor-orders">
    <PageHeader />
    <div class="container">
      <h2>咨询师工作台</h2>

      <el-tabs v-model="activeTab" @tab-change="loadOrders">
        <el-tab-pane label="待处理" name="pending">
          <span class="badge">({{ counts.pending || 0 }})</span>
        </el-tab-pane>
        <el-tab-pane label="已确认" name="confirmed">
          <span class="badge">({{ counts.confirmed || 0 }})</span>
        </el-tab-pane>
        <el-tab-pane label="进行中" name="inprogress">
          <span class="badge">({{ counts.inprogress || 0 }})</span>
        </el-tab-pane>
        <el-tab-pane label="已完成" name="completed">
          <span class="badge">({{ counts.completed || 0 }})</span>
        </el-tab-pane>
      </el-tabs>

      <div v-loading="loading" class="order-list">
        <el-card v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-header">
            <span class="time">{{ formatDate(order.appointment_date) }}</span>
            <span class="id">#{{ order.appointment_no }}</span>
          </div>

          <div class="info">
            <h3>用户: {{ order.user_name || '未知' }}</h3>
            <p class="desc"><strong>问题描述:</strong> {{ order.problem_description || '无' }}</p>
            <div class="details">
              <p><strong>方式:</strong> {{ getTypeText(order.consultation_type) }}</p>
              <p><strong>费用:</strong> ¥{{ order.price }}</p>
            </div>
          </div>

          <div class="actions">
            <template v-if="order.status === 'pending'">
              <el-button type="success" @click="agreeOrder(order)">同意</el-button>
              <el-button type="danger" @click="rejectOrder(order)">拒绝</el-button>
            </template>
            <template v-else-if="order.status === 'confirmed' || order.status === 'in_progress'">
              <el-button type="primary" @click="startChat(order)">进入咨询</el-button>
            </template>
            <template v-else-if="order.status === 'completed'">
              <el-button @click="viewReview(order)">查看评价</el-button>
            </template>
          </div>
        </el-card>

        <el-empty v-if="!loading && orders.length === 0" description="暂无订单" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorOrders, handleOrder } from '@/api/consultation'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('pending')
const orders = ref([])
const counts = ref({})

const statusMap = { pending: 'pending', confirmed: 'confirmed', inprogress: 'in_progress', completed: 'completed' }

const loadOrders = async () => {
  loading.value = true
  try {
    const res = await getCounselorOrders({ status: statusMap[activeTab.value] || activeTab.value })
    orders.value = res.data.items || []
    // 加载各状态数量
    const countRes = await getCounselorOrders({ page_size: 100 })
    const all = countRes.data.items || []
    counts.value = {
      pending: all.filter(o => o.status === 'pending').length,
      confirmed: all.filter(o => o.status === 'confirmed').length,
      inprogress: all.filter(o => o.status === 'in_progress').length,
      completed: all.filter(o => o.status === 'completed').length
    }
  } finally {
    loading.value = false
  }
}

const getTypeText = (type) => ({ video: '视频', voice: '语音', offline: '线下' }[type] || type)

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

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
  } catch { if (error !== 'cancel') console.error(error) }
}

const startChat = (order) => {
  router.push(`/consultation/counselor/${order.id}`)
}

const viewReview = (order) => {
  ElMessageBox.alert(`用户评分: ${order.rating}⭐\n${order.review || '暂无评价'}`, '评价详情')
}

onMounted(() => loadOrders())
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.counselor-orders {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
  h2 { font-size: 28px; font-weight: 700; color: $text-primary; margin-bottom: 24px; }
}

.order-list { display: flex; flex-direction: column; gap: 16px; margin-top: 24px; }

.order-card {
  border-radius: 16px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;
  transition: box-shadow 0.2s ease;
  &:hover { box-shadow: 0 6px 24px rgba(107,82,68,0.12) !important; }
  :deep(.el-card__body) { padding: 20px 24px; }
}

.order-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid $border-lighter;
  .time { font-size: 15px; font-weight: 600; color: $text-primary; }
  .id { color: $text-secondary; font-size: 13px; }
}

.info {
  margin-bottom: 16px;
  h3 { margin: 0 0 8px; font-size: 16px; color: $text-primary; font-weight: 600; }
  .desc { color: $text-secondary; margin-bottom: 10px; font-size: 14px; line-height: 1.6; }
}

.details {
  display: flex; gap: 20px;
  p { margin: 0; color: $text-secondary; font-size: 13px; }
}

.actions { display: flex; gap: 12px; padding-top: 16px; border-top: 1px solid $border-lighter; }
.badge { margin-left: 4px; font-size: 12px; color: $primary-color; font-weight: 600; }
</style>
