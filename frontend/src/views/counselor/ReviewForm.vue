<template>
  <div class="review-form">
    <PageHeader />
    <div class="container">
      <el-button :icon="icons.ArrowLeft" @click="goBack" class="back-btn">返回预约列表</el-button>

      <el-card v-loading="loading" class="form-card">
        <template #header>
          <div class="card-header">
            <h2>评价咨询</h2>
            <el-tag type="success">已完成</el-tag>
          </div>
        </template>

        <div class="appointment-info">
          <div class="counselor-section">
            <el-avatar :size="80" :src="appointment.counselorAvatar">
              <el-icon :size="40"><component :is="icons.User" /></el-icon>
            </el-avatar>
            <div class="counselor-details">
              <h3>{{ appointment.counselorName }}</h3>
              <p class="title">{{ appointment.counselorTitle || '心理咨询师' }}</p>
            </div>
          </div>

          <el-divider />

          <div class="consultation-info">
            <div class="info-item">
              <span class="label">咨询时间:</span>
              <span class="value">{{ formatDateTime(appointment.appointmentDate) }}</span>
            </div>
            <div class="info-item">
              <span class="label">咨询方式:</span>
              <span class="value">{{ getConsultationTypeText(appointment.consultationType) }}</span>
            </div>
            <div class="info-item">
              <span class="label">咨询费用:</span>
              <span class="value price">¥{{ appointment.price }}</span>
            </div>
          </div>
        </div>

        <el-divider />

        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="总体评分" prop="rating">
            <div class="rating-section">
              <el-rate
                v-model="form.rating"
                size="large"
                show-text
                :texts="['非常不满意', '不满意', '一般', '满意', '非常满意']"
              />
              <span class="rating-text">{{ getRatingText(form.rating) }}</span>
            </div>
          </el-form-item>

          <el-form-item label="您对本次咨询满意的方面" prop="tags">
            <el-checkbox-group v-model="form.tags" class="tags-group">
              <el-checkbox value="专业度高">专业度高</el-checkbox>
              <el-checkbox value="倾听耐心">倾听耐心</el-checkbox>
              <el-checkbox value="态度友善">态度友善</el-checkbox>
              <el-checkbox value="环境舒适">环境舒适</el-checkbox>
              <el-checkbox value="效果明显">效果明显</el-checkbox>
              <el-checkbox value="时间准时">时间准时</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="详细评价" prop="content">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="6"
              placeholder="请分享您的咨询体验，您的评价将帮助其他用户做出更好的选择（选填，最多500字）"
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="form.isAnonymous" size="large">
              <span class="anonymous-text">匿名评价（其他用户将看不到您的个人信息）</span>
            </el-checkbox>
          </el-form-item>

          <el-form-item>
            <div class="submit-section">
              <el-button type="primary" :loading="submitting" size="large" @click="submitReview">
                提交评价
              </el-button>
              <el-button size="large" @click="goBack">跳过</el-button>
            </div>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, markRaw } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, User } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { submitReview as submitReviewApi } from '@/api/counselor'

// Mark icon components as raw to prevent reactivity warnings
const icons = markRaw({
  ArrowLeft,
  User
})

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const submitting = ref(false)
const formRef = ref(null)
const appointmentId = route.params.id
const appointment = ref({
  counselorName: '',
  counselorTitle: '',
  counselorAvatar: '',
  appointmentDate: '',
  consultationType: '',
  price: 0
})

const form = reactive({
  rating: 5,
  tags: [],
  content: '',
  isAnonymous: false
})

const rules = {
  rating: [
    { required: true, message: '请选择评分', trigger: 'change' }
  ]
}

const loadAppointment = async () => {
  try {
    loading.value = true

    // 这里应该调用API获取预约详情
    // 暂时使用模拟数据，实际应该从API获取
    // const res = await getAppointmentDetail(appointmentId)

    appointment.value = {
      counselorName: '李静怡',
      counselorTitle: '资深心理咨询师',
      counselorAvatar: null,
      appointmentDate: new Date().toISOString(),
      consultationType: 'video',
      price: 500
    }

    // 实际应用中应该从API加载预约信息
    // appointment.value = res.data

  } catch (error) {
    console.error('加载预约信息失败:', error)
    ElMessage.error('加载预约信息失败')
  } finally {
    loading.value = false
  }
}

const getRatingText = (rating) => {
  const texts = {
    1: '非常不满意',
    2: '不满意',
    3: '一般',
    4: '满意',
    5: '非常满意'
  }
  return texts[rating] || ''
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

const submitReview = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    // 准备提交数据
    const reviewData = {
      rating: form.rating,
      tags: form.tags,
      content: form.content,
      is_anonymous: form.isAnonymous
    }

    // 调用API提交评价
    await submitReviewApi(appointmentId, reviewData)

    ElMessage.success({
      message: '评价提交成功！感谢您的反馈',
      duration: 3000
    })

    // 延迟跳转，让用户看到成功提示
    setTimeout(() => {
      goBack()
    }, 1500)

  } catch (error) {
    console.error('提交评价失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('提交评价失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/counselor/orders')
}

onMounted(() => {
  if (!appointmentId) {
    ElMessage.error('缺少预约信息')
    goBack()
    return
  }
  loadAppointment()
})
</script>

<style scoped>
@use '@/styles/variables.scss' as *;

.review-form {
  min-height: 100vh;
  background: $bg-color;
  padding-bottom: 40px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.back-btn {
  margin-bottom: $spacing-lg;
}

.form-card {
  margin-top: $spacing-lg;
  border-radius: 8px;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  color: $text-primary;
}

.appointment-info {
  padding: $spacing-lg;
  background: #fafafa;
  border-radius: 8px;
}

.counselor-section {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  margin-bottom: $spacing-lg;
}

.counselor-details h3 {
  margin: 0 0 $spacing-xs 0;
  font-size: 18px;
  color: $text-primary;
}

.counselor-details .title {
  margin: 0;
  color: $text-secondary;
  font-size: 14px;
}

.consultation-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-md;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.info-item .label {
  font-size: 12px;
  color: $text-secondary;
}

.info-item .value {
  font-size: 14px;
  font-weight: 500;
  color: $text-primary;
}

.info-item .price {
  font-size: 18px;
  font-weight: 600;
  color: #f56c6c;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
}

.rating-text {
  font-size: 16px;
  font-weight: 500;
  color: $text-primary;
}

.tags-group {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-md;
}

.tags-group :deep(.el-checkbox) {
  margin-right: 0;
}

.anonymous-text {
  font-size: 14px;
  color: $text-secondary;
}

.submit-section {
  display: flex;
  gap: $spacing-md;
  justify-content: center;
  width: 100%;
}

.submit-section .el-button {
  min-width: 150px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .counselor-section {
    flex-direction: column;
    text-align: center;
  }

  .consultation-info {
    grid-template-columns: 1fr;
  }

  .rating-section {
    flex-direction: column;
    align-items: flex-start;
  }

  .submit-section {
    flex-direction: column;
  }

  .submit-section .el-button {
    width: 100%;
  }
}
</style>
