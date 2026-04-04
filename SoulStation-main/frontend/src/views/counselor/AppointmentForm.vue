<template>
  <div class="appointment-form-page">
    <PageHeader />

    <div class="container">
      <!-- 页面头部 -->
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="goBack" plain>返回</el-button>
        <div class="header-content">
          <h1 class="page-title">预约咨询</h1>
          <p class="page-subtitle">选择合适的时间，开启您的咨询之旅</p>
        </div>
      </div>

      <!-- 咨询师简要信息 -->
      <el-card v-if="counselor.id" class="counselor-info-card" shadow="never">
        <div class="counselor-brief">
          <el-avatar :size="80" :src="counselor.avatar">
            <el-icon :size="40"><User /></el-icon>
          </el-avatar>
          <div class="brief-info">
            <h3>{{ counselor.name }}</h3>
            <el-tag type="info" size="small">{{ counselor.title || '心理咨询师' }}</el-tag>
            <div class="rating">
              <el-rate v-model="counselor.rating" disabled show-score score-template="{value}" />
            </div>
          </div>
        </div>
      </el-card>

      <!-- 预约表单 -->
      <el-card v-loading="loading" class="form-card" shadow="never">
        <el-steps :active="currentStep" finish-status="success" align-center class="steps">
          <el-step title="选择时间" description="选择咨询方式和时段" />
          <el-step title="填写信息" description="完善预约信息" />
          <el-step title="确认预约" description="核对并提交" />
        </el-steps>

        <!-- 步骤1: 选择时间 -->
        <div v-show="currentStep === 0" class="step-content">
          <div class="section-title">
            <el-icon class="title-icon"><VideoCamera /></el-icon>
            <span>选择咨询方式</span>
          </div>

          <div class="consultation-types">
            <div
              v-for="type in consultationTypes"
              :key="type.value"
              class="type-card"
              :class="{ active: formData.consultation_type === type.value }"
              @click="selectConsultationType(type.value)"
            >
              <el-icon class="type-icon" :class="type.value">
                <component :is="type.icon" />
              </el-icon>
              <div class="type-info">
                <h4>{{ type.label }}</h4>
                <p class="type-price">¥{{ currentPrice }}/小时</p>
              </div>
              <el-icon v-if="formData.consultation_type === type.value" class="check-icon">
                <CircleCheck />
              </el-icon>
            </div>
          </div>

          <div class="section-title">
            <el-icon class="title-icon"><Calendar /></el-icon>
            <span>选择预约日期</span>
          </div>

          <el-date-picker
            v-model="selectedDate"
            type="date"
            placeholder="选择日期"
            :disabled-date="disabledDate"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="loadSlots"
            size="large"
            class="date-picker"
          />

          <div class="section-title">
            <el-icon class="title-icon"><Clock /></el-icon>
            <span>选择预约时段</span>
          </div>

          <div v-if="loadingSlots" v-loading="true" class="slots-loading"></div>

          <div v-else-if="availableSlots.length === 0" class="no-slots">
            <el-empty description="请先选择预约日期" :image-size="100" />
          </div>

          <div v-else class="time-slots">
            <div
              v-for="slot in availableSlots"
              :key="slot.time"
              class="slot-item"
              :class="{
                selected: formData.appointment_time === slot.time,
                disabled: !slot.available
              }"
              @click="selectSlot(slot)"
            >
              <div class="slot-time">{{ slot.time }}</div>
              <div class="slot-status">
                <el-tag v-if="!slot.available" type="info" size="small">已约满</el-tag>
                <el-tag v-else-if="formData.appointment_time === slot.time" type="success" size="small">
                  已选择
                </el-tag>
                <el-tag v-else type="success" effect="plain" size="small">可预约</el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤2: 填写信息 -->
        <div v-show="currentStep === 1" class="step-content">
          <div class="section-title">
            <el-icon class="title-icon"><Edit /></el-icon>
            <span>填写预约信息</span>
          </div>

          <el-form
            ref="formRef"
            :model="formData"
            :rules="rules"
            label-width="120px"
            class="appointment-form"
          >
            <el-form-item label="预约人姓名" prop="user_name">
              <el-input
                v-model="formData.user_name"
                placeholder="请输入您的真实姓名"
                size="large"
                clearable
              />
            </el-form-item>

            <el-form-item label="联系电话" prop="user_contact">
              <el-input
                v-model="formData.user_contact"
                placeholder="请输入11位手机号码"
                size="large"
                maxlength="11"
                clearable
              />
            </el-form-item>

            <el-form-item label="问题描述" prop="problem_description">
              <el-input
                v-model="formData.problem_description"
                type="textarea"
                :rows="6"
                placeholder="请简要描述您希望咨询的问题，有助于咨询师更好地为您服务（最多500字）"
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="预约信息">
              <div class="appointment-summary">
                <div class="summary-item">
                  <span class="label">咨询师：</span>
                  <span class="value">{{ counselor.name }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">咨询方式：</span>
                  <span class="value">{{ getConsultationTypeText(formData.consultation_type) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">预约时间：</span>
                  <span class="value">{{ formData.appointment_date }} {{ formData.appointment_time }}</span>
                </div>
                <div class="summary-item total">
                  <span class="label">咨询费用：</span>
                  <span class="value price">¥{{ currentPrice }}</span>
                </div>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 步骤3: 确认预约 -->
        <div v-show="currentStep === 2" class="step-content">
          <div class="section-title">
            <el-icon class="title-icon"><Document /></el-icon>
            <span>确认预约信息</span>
          </div>

          <div class="confirm-content">
            <el-descriptions :column="1" border class="confirm-descriptions">
              <el-descriptions-item label="咨询师">{{ counselor.name }}</el-descriptions-item>
              <el-descriptions-item label="咨询方式">
                {{ getConsultationTypeText(formData.consultation_type) }}
              </el-descriptions-item>
              <el-descriptions-item label="预约时间">
                {{ formData.appointment_date }} {{ formData.appointment_time }}
              </el-descriptions-item>
              <el-descriptions-item label="预约人">{{ formData.user_name }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{ formData.user_contact }}</el-descriptions-item>
              <el-descriptions-item label="问题描述">
                {{ formData.problem_description }}
              </el-descriptions-item>
              <el-descriptions-item label="咨询费用">
                <span class="confirm-price">¥{{ currentPrice }}</span>
              </el-descriptions-item>
            </el-descriptions>

            <el-alert
              title="温馨提示"
              type="info"
              :closable="false"
              show-icon
              class="tips-alert"
            >
              <ul class="tips-list">
                <li>预约成功后，请准时参加咨询</li>
                <li>如需取消或改期，请提前24小时联系客服</li>
                <li>首次咨询前，我们将通过电话与您确认具体安排</li>
              </ul>
            </el-alert>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button v-if="currentStep > 0" @click="prevStep" size="large">
            上一步
          </el-button>
          <el-button
            v-if="currentStep === 0"
            type="primary"
            size="large"
            :disabled="!canGoToNext"
            @click="nextStep"
          >
            下一步
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button
            v-if="currentStep === 1"
            type="primary"
            size="large"
            @click="nextStep"
          >
            确认信息
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button
            v-if="currentStep === 2"
            type="primary"
            size="large"
            :loading="submitting"
            @click="submitAppointment"
          >
            <el-icon class="el-icon--left"><Select /></el-icon>
            提交预约
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, ArrowRight, User, CircleCheck, VideoCamera, Phone, Location,
  Calendar, Clock, Edit, Document, Select
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorDetail, getAvailableSlots, createAppointment } from '@/api/counselor'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const loadingSlots = ref(false)
const currentStep = ref(0)
const submitting = ref(false)

const counselorId = route.query.counselorId
const counselor = ref({})

const selectedDate = ref('')
const availableSlots = ref([])

const formData = reactive({
  counselor_id: parseInt(counselorId),
  consultation_type: 'video',
  appointment_date: '',
  appointment_time: '',
  user_name: '',
  user_contact: '',
  problem_description: ''
})

const formRef = ref(null)

const consultationTypes = computed(() => [
  {
    value: 'video',
    label: '视频咨询',
    icon: VideoCamera,
    price: counselor.value.price_video || 300
  },
  {
    value: 'voice',
    label: '语音咨询',
    icon: Phone,
    price: counselor.value.price_voice || 200
  },
  {
    value: 'offline',
    label: '线下咨询',
    icon: Location,
    price: counselor.value.price_offline || 500
  }
])

const currentPrice = computed(() => {
  const type = consultationTypes.value.find(t => t.value === formData.consultation_type)
  return type ? type.price : 300
})

const canGoToNext = computed(() => {
  return currentStep.value === 0
    ? formData.appointment_date && formData.appointment_time
    : true
})

const rules = {
  user_name: [
    { required: true, message: '请输入您的姓名', trigger: 'blur' },
    { min: 2, max: 20, message: '姓名长度应为2-20个字符', trigger: 'blur' }
  ],
  user_contact: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: 'blur' }
  ],
  problem_description: [
    { required: true, message: '请填写问题描述', trigger: 'blur' },
    { min: 10, max: 500, message: '问题描述长度应为10-500个字符', trigger: 'blur' }
  ]
}

const loadCounselor = async () => {
  try {
    loading.value = true
    const res = await getCounselorDetail(counselorId)
    counselor.value = res.data

    // 自动填充已登录用户信息
    const userInfo = localStorage.getItem('userInfo')
    if (userInfo) {
      const user = JSON.parse(userInfo)
      formData.user_name = user.nickname || ''
      formData.user_contact = user.phone || ''
    }
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载咨询师信息失败')
  } finally {
    loading.value = false
  }
}

const disabledDate = (time) => {
  // 禁用过去的日期
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

const loadSlots = async () => {
  if (!selectedDate.value) {
    availableSlots.value = []
    return
  }

  try {
    loadingSlots.value = true
    const res = await getAvailableSlots(counselorId, selectedDate.value)

    // 处理返回的时段数据
    if (res.data && Array.isArray(res.data)) {
      availableSlots.value = res.data
    } else if (res.data && res.data.slots) {
      availableSlots.value = res.data.slots
    } else {
      // 如果没有返回数据，生成默认时段
      availableSlots.value = generateDefaultSlots()
    }

    formData.appointment_date = selectedDate.value
  } catch (error) {
    console.error('加载时段失败:', error)
    ElMessage.error('加载可用时段失败')
    availableSlots.value = []
  } finally {
    loadingSlots.value = false
  }
}

const generateDefaultSlots = () => {
  const slots = []
  const times = [
    '09:00-10:00', '10:00-11:00', '11:00-12:00',
    '14:00-15:00', '15:00-16:00', '16:00-17:00',
    '17:00-18:00', '19:00-20:00', '20:00-21:00'
  ]
  times.forEach(time => {
    slots.push({ time, available: true, price: currentPrice.value })
  })
  return slots
}

const selectConsultationType = (type) => {
  formData.consultation_type = type
}

const selectSlot = (slot) => {
  if (!slot.available) return
  formData.appointment_time = slot.time
}

const getConsultationTypeText = (type) => {
  const map = {
    video: '视频咨询',
    voice: '语音咨询',
    offline: '线下咨询'
  }
  return map[type] || type
}

const nextStep = async () => {
  if (currentStep.value === 1) {
    // 验证表单
    if (!formRef.value) return
    try {
      await formRef.value.validate()
    } catch (error) {
      ElMessage.warning('请完善必填信息')
      return
    }
  }
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const submitAppointment = async () => {
  try {
    submitting.value = true

    // 组合完整的预约时间
    const appointmentDateTime = `${formData.appointment_date} ${formData.appointment_time.split('-')[0]}`

    const requestData = {
      counselor_id: formData.counselor_id,
      consultation_type: formData.consultation_type,
      appointment_date: appointmentDateTime,
      user_name: formData.user_name,
      user_contact: formData.user_contact,
      problem_description: formData.problem_description
    }

    await createAppointment(requestData)

    ElMessage.success('预约成功！我们将尽快与您联系确认')
    router.push('/counselor/orders')
  } catch (error) {
    console.error('预约失败:', error)
    ElMessage.error(error.response?.data?.detail || '预约失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadCounselor()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.appointment-form-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: $spacing-xl;
}

/* 页面头部 */
.page-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-xl;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 $spacing-xs 0;
}

.page-subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

/* 咨询师信息卡片 */
.counselor-info-card {
  border-radius: 12px;
  margin-bottom: $spacing-lg;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.counselor-brief {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.brief-info {
  flex: 1;
}

.brief-info h3 {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 $spacing-xs 0;
}

.brief-info .rating {
  margin-top: $spacing-xs;
}

/* 表单卡片 */
.form-card {
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.steps {
  margin: $spacing-xl 0 $spacing-xl;
}

/* 步骤内容 */
.step-content {
  margin-top: $spacing-xl;
}

.section-title {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: $spacing-lg;
}

.title-icon {
  font-size: 22px;
  color: #409eff;
}

/* 咨询方式选择 */
.consultation-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-md;
  margin-bottom: $spacing-xl;
}

.type-card {
  position: relative;
  padding: $spacing-lg;
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: $spacing-md;

  &:hover {
    border-color: #409eff;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  }

  &.active {
    border-color: #409eff;
    background: linear-gradient(135deg, rgba(64, 158, 255, 0.05) 0%, rgba(64, 158, 255, 0.1) 100%);
  }
}

.type-icon {
  font-size: 40px;
  opacity: 0.6;
}

.type-icon.video {
  color: #667eea;
}

.type-icon.voice {
  color: #84fab0;
}

.type-icon.offline {
  color: #a1c4fd;
}

.type-info {
  flex: 1;
}

.type-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 $spacing-xs 0;
}

.type-price {
  font-size: 14px;
  color: #f56c6c;
  font-weight: 600;
  margin: 0;
}

.check-icon {
  position: absolute;
  top: $spacing-sm;
  right: $spacing-sm;
  font-size: 20px;
  color: #67c23a;
}

/* 日期选择器 */
.date-picker {
  width: 100%;
  margin-bottom: $spacing-xl;
}

/* 时段选择 */
.slots-loading {
  height: 200px;
}

.time-slots {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: $spacing-md;
}

.slot-item {
  position: relative;
  padding: $spacing-md;
  background: #fff;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;

  &:hover:not(.disabled) {
    border-color: #409eff;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
  }

  &.selected {
    border-color: #67c23a;
    background: linear-gradient(135deg, rgba(103, 194, 58, 0.05) 0%, rgba(103, 194, 58, 0.1) 100%);
  }

  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #f5f7fa;
  }
}

.slot-time {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: $spacing-xs;
}

.slot-status {
  display: flex;
  justify-content: center;
}

/* 预约信息摘要 */
.appointment-summary {
  background: #f8f9fa;
  border-radius: 8px;
  padding: $spacing-lg;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: $spacing-sm 0;
  border-bottom: 1px dashed #e4e7ed;

  &:last-child {
    border-bottom: none;
  }

  &.total {
    margin-top: $spacing-sm;
    padding-top: $spacing-md;
    border-top: 2px solid #e4e7ed;
  }
}

.summary-item .label {
  font-weight: 500;
  color: #606266;
}

.summary-item .value {
  font-weight: 600;
  color: #2c3e50;
}

.summary-item.total .value.price {
  font-size: 24px;
  color: #f56c6c;
}

/* 确认页面 */
.confirm-content {
  max-width: 700px;
  margin: 0 auto;
}

.confirm-descriptions {
  margin-bottom: $spacing-xl;
}

.confirm-price {
  font-size: 24px;
  font-weight: 600;
  color: #f56c6c;
}

.tips-alert {
  margin-top: $spacing-xl;
}

.tips-list {
  margin: $spacing-sm 0 0 0;
  padding-left: $spacing-lg;
}

.tips-list li {
  margin-bottom: $spacing-xs;
  color: #606266;
  line-height: 1.6;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: $spacing-md;
  margin-top: $spacing-xl;
  padding-top: $spacing-xl;
  border-top: 1px solid #e4e7ed;
}

/* 响应式 */
@media (max-width: 768px) {
  .container {
    padding: $spacing-md;
  }

  .consultation-types {
    grid-template-columns: 1fr;
  }

  .time-slots {
    grid-template-columns: repeat(2, 1fr);
  }

  .counselor-brief {
    flex-direction: column;
    text-align: center;
  }
}
</style>
