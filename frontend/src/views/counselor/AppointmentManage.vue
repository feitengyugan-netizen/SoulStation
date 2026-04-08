<template>
  <div class="appointment-manage">
    <PageHeader />
    <div class="container">
      <div class="page-header">
        <h2>我的预约</h2>
        <el-button type="primary" @click="goToBook">预约咨询师</el-button>
      </div>

      <el-tabs v-model="activeTab" @tab-change="loadOrders">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待确认" name="pending" />
        <el-tab-pane label="已确认" name="confirmed" />
        <el-tab-pane label="进行中" name="in_progress" />
        <el-tab-pane label="已完成" name="completed" />
        <el-tab-pane label="已取消" name="cancelled" />
      </el-tabs>

      <div v-loading="loading" class="order-list">
        <el-card v-for="order in orders" :key="order.id" class="order-card">
          <div class="order-header">
            <div class="order-info">
              <span class="order-no">预约号: {{ order.appointmentNo || `APT${order.id}` }}</span>
              <span class="order-date">{{ formatDateTime(order.appointmentDate) }}</span>
            </div>
            <el-tag :type="getStatusType(order.status)" size="large">
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>

          <div class="order-content">
            <div class="counselor-section">
              <el-avatar :size="60" :src="order.counselorAvatar">
                <el-icon :size="30"><User /></el-icon>
              </el-avatar>
              <div class="counselor-info">
                <h3>{{ order.counselorName }}</h3>
                <p class="title">{{ order.counselorTitle || '心理咨询师' }}</p>
              </div>
            </div>

            <el-divider />

            <div class="order-details">
              <div class="detail-row">
                <span class="label">咨询方式:</span>
                <el-tag size="small">{{ getConsultationTypeText(order.consultationType) }}</el-tag>
              </div>
              <div class="detail-row">
                <span class="label">咨询费用:</span>
                <span class="price">¥{{ order.price }}</span>
              </div>
              <div class="detail-row" v-if="order.userName">
                <span class="label">预约人:</span>
                <span>{{ order.userName }}</span>
              </div>
              <div class="detail-row" v-if="order.userContact">
                <span class="label">联系方式:</span>
                <span>{{ order.userContact }}</span>
              </div>
              <div class="detail-row" v-if="order.problemDescription">
                <span class="label">问题描述:</span>
                <span class="description">{{ order.problemDescription }}</span>
              </div>
            </div>
          </div>

          <div class="order-actions">
            <template v-if="order.status === 'pending' || order.status === 'confirmed'">
              <el-button type="danger" plain @click="cancelOrder(order.id)">
                取消预约
              </el-button>
            </template>
            <template v-if="order.status === 'confirmed' || order.status === 'in_progress'">
              <el-button type="primary" @click="startConsultation(order)">
                进入咨询
              </el-button>
            </template>
            <template v-if="order.status === 'completed' && !order.hasReview">
              <el-button type="warning" plain @click="goToReview(order.id)">
                写评价
              </el-button>
            </template>
            <template v-if="order.status === 'completed' && order.hasReview">
              <el-button type="success" plain @click="viewReview(order)">
                查看评价
              </el-button>
            </template>
          </div>
        </el-card>

        <el-empty v-if="!loading && orders.length === 0" description="暂无预约记录" />
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadOrders"
          @current-change="loadOrders"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getUserAppointments, cancelAppointment } from '@/api/counselor'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('all')
const orders = ref([])
const total = ref(0)

const pagination = reactive({
  page: 1,
  pageSize: 10
})

const loadOrders = async () => {
  try {
    loading.value = true
    const params = {
      status: activeTab.value === 'all' ? '' : activeTab.value,
      page: pagination.page,
      pageSize: pagination.pageSize
    }

    const res = await getUserAppointments(params)

    // 处理API响应数据结构
    if (res.code === 200 && res.data) {
      const items = res.data.items || res.data.list || []

      // 转换数据格式
      orders.value = items.map(order => ({
        id: order.id,
        appointmentNo: order.appointment_no,
        appointmentDate: order.appointment_date,
        consultationType: order.consultation_type,
        price: order.price || 0,
        status: order.status,
        userName: order.user_name,
        userContact: order.user_contact,
        problemDescription: order.problem_description,
        counselorId: order.counselor_id,
        counselorName: order.counselor?.name || '咨询师',
        counselorTitle: order.counselor?.title || '心理咨询师',
        counselorAvatar: order.counselor?.avatar,
        hasReview: !!order.review,
        review: order.review
      }))

      total.value = res.data.total || items.length
    } else {
      orders.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('加载预约列表失败:', error)
    ElMessage.error('加载预约列表失败')
    orders.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    confirmed: 'primary',
    in_progress: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '待确认',
    confirmed: '已确认',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return texts[status] || status
}

const getConsultationTypeText = (type) => {
  const types = {
    video: '视频咨询',
    voice: '语音咨询',
    offline: '线下咨询'
  }
  return types[type] || type
}

const formatDateTime = (dateStr) => {
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

const cancelOrder = async (id) => {
  try {
    await ElMessageBox.confirm(
      '取消预约后可能需要重新排队，确定要取消吗？',
      '取消预约',
      {
        type: 'warning',
        confirmButtonText: '确定取消',
        cancelButtonText: '再想想'
      }
    )

    const reason = await ElMessageBox.prompt(
      '请输入取消原因（可选）',
      '取消原因',
      {
        inputType: 'textarea',
        inputPlaceholder: '如因临时有事、时间冲突等'
      }
    ).then(({ value }) => value || '用户主动取消').catch(() => '用户主动取消')

    await cancelAppointment(id, reason)
    ElMessage.success('预约已取消')
    loadOrders()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消预约失败:', error)
      ElMessage.error('取消预约失败，请重试')
    }
  }
}

const startConsultation = (order) => {
  router.push(`/consultation/user/${order.id}`)
}

const goToReview = (appointmentId) => {
  router.push(`/counselor/review/${appointmentId}`)
}

const viewReview = (order) => {
  const review = order.review
  ElMessageBox.alert(
    `
    <div style="text-align: left;">
      <p><strong>评分：</strong>${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</p>
      ${review.content ? `<p><strong>评价内容：</strong>${review.content}</p>` : ''}
      ${review.tags && review.tags.length > 0 ? `<p><strong>标签：</strong>${review.tags.join('、')}</p>` : ''}
      ${review.counselorReply ? `<p><strong>咨询师回复：</strong>${review.counselorReply}</p>` : ''}
    </div>
    `,
    '评价详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭'
    }
  )
}

const goToBook = () => {
  router.push('/counselor')
}

onMounted(() => loadOrders())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;

.appointment-manage {
  min-height: 100vh;
  background: $bg-color;
  padding-bottom: 40px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-xl;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: $text-primary;
}

.order-list {
  margin-top: $spacing-xl;
}

.order-card {
  margin-bottom: $spacing-lg;
  border-radius: 8px;
  overflow: hidden;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-md $spacing-lg;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.order-no {
  font-size: 12px;
  opacity: 0.8;
}

.order-date {
  font-size: 16px;
  font-weight: 600;
}

.order-content {
  padding: $spacing-lg;
}

.counselor-section {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
}

.counselor-info h3 {
  margin: 0 0 $spacing-xs 0;
  font-size: 18px;
  color: $text-primary;
}

.counselor-info .title {
  margin: 0;
  color: $text-secondary;
  font-size: 14px;
}

.order-details {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
}

.detail-row .label {
  font-weight: 500;
  color: $text-secondary;
  min-width: 80px;
}

.detail-row .price {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}

.detail-row .description {
  color: $text-primary;
  line-height: 1.5;
  flex: 1;
}

.order-actions {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-md $spacing-lg;
  background: #fafafa;
  border-top: 1px solid #f0f0f0;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: $spacing-xl;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .order-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-sm;
  }

  .counselor-section {
    flex-direction: column;
    text-align: center;
  }

  .order-actions {
    flex-direction: column;
  }

  .detail-row {
    flex-direction: column;
    gap: $spacing-xs;
  }

  .detail-row .label {
    min-width: auto;
  }
}
</style>
