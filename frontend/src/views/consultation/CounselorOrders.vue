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
            <span class="time">{{ order.date }} {{ order.timeSlot }}</span>
            <span class="id">#{{ order.id }}</span>
          </div>

          <div class="info">
            <h3>用户: {{ order.userName }}</h3>
            <p class="desc"><strong>问题描述:</strong> {{ order.description }}</p>
            <div class="details">
              <p><strong>方式:</strong> {{ getTypeText(order.type) }}</p>
              <p><strong>费用:</strong> ¥{{ order.price }}</p>
            </div>
          </div>

          <div class="actions">
            <template v-if="order.status === 'pending'">
              <el-button type="success" @click="agreeOrder(order)">同意</el-button>
              <el-button type="danger" @click="rejectOrder(order)">拒绝</el-button>
            </template>
            <template v-else-if="order.status === 'confirmed' || order.status === 'inprogress'">
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

<style scoped>
@use '@/styles/variables.scss' as *;
.counselor-orders { min-height: 100vh; background: $bg-color; }
.container { max-width: 1000px; margin: 0 auto; padding: $spacing-lg; }
.counselor-orders h2 { margin-bottom: $spacing-lg; }
.order-list { margin-top: $spacing-lg; }
.order-card { margin-bottom: $spacing-md; }
.order-header { display: flex; justify-content: space-between; margin-bottom: $spacing-md; }
.order-header .time { font-size: 16px; font-weight: 500; }
.order-header .id { color: $text-secondary; }
.info { margin-bottom: $spacing-md; }
.info h3 { margin: 0 0 $spacing-sm; }
.info .desc { color: $text-secondary; margin-bottom: $spacing-md; }
.details p { margin: $spacing-xs 0; color: $text-secondary; }
.actions { display: flex; gap: $spacing-md; }
.badge { margin-left: $spacing-sm; font-size: 12px; }
</style>
