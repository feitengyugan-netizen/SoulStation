<template>
  <div class="appointment-manage">
    <PageHeader />
    <div class="container">
      <h2>我的预约</h2>

      <el-tabs v-model="activeTab" @tab-change="loadOrders">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待确认" name="pending" />
        <el-tab-pane label="已确认" name="confirmed" />
        <el-tab-pane label="已完成" name="completed" />
      </el-tabs>

      <div v-loading="loading" class="order-list">
        <el-card v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-header">
            <span class="order-date">{{ order.date }} {{ order.timeSlot }}</span>
            <el-tag :type="getStatusType(order.status)">{{ order.status }}</el-tag>
          </div>
          <div class="order-body">
            <p><strong>咨询师:</strong> {{ order.counselorName }}</p>
            <p><strong>方式:</strong> {{ order.type }}</p>
            <p><strong>费用:</strong> ¥{{ order.price }}</p>
          </div>
          <div class="order-actions">
            <el-button v-if="order.status !== 'completed'" type="danger" text @click="cancelOrder(order.id)">取消预约</el-button>
            <el-button v-if="order.status === 'completed'" type="primary" text @click="goToReview(order.id)">写评价</el-button>
          </div>
        </el-card>

        <el-empty v-if="!loading && orders.length === 0" description="暂无预约" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { getUserAppointments, cancelAppointment } from '@/api/counselor'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('all')
const orders = ref([])

const loadOrders = async () => {
  try {
    loading.value = true
    const res = await getUserAppointments({ status: activeTab.value === 'all' ? '' : activeTab.value })
    orders.value = res.data.list || []
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const types = { pending: 'warning', confirmed: 'primary', completed: 'success', cancelled: 'info' }
  return types[status] || ''
}

const cancelOrder = async (id) => {
  try {
    await ElMessageBox.confirm('确定要取消预约吗？', '提示', { type: 'warning' })
    await cancelAppointment(id)
    ElMessage.success('取消成功')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const goToReview = (id) => {
  router.push(`/counselor/review/${id}`)
}

onMounted(() => loadOrders())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.appointment-manage { min-height: 100vh; background: $bg-color; }
.container { max-width: 900px; margin: 0 auto; padding: $spacing-lg; }
.appointment-manage h2 { margin-bottom: $spacing-lg; }
.order-list { margin-top: $spacing-lg; }
.order-card { margin-bottom: $spacing-md; }
.order-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-md; }
.order-date { font-size: 16px; font-weight: 500; }
.order-body p { margin: $spacing-xs 0; color: $text-secondary; }
.order-actions { margin-top: $spacing-md; display: flex; gap: $spacing-md; }
</style>
