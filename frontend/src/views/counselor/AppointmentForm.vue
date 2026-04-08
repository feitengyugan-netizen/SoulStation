<template>
  <div class="appointment-form">
    <PageHeader />

    <!-- 顶部横幅 -->
    <div class="hero-banner">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="title-icon">📅</span>
            预约咨询
            <span class="title-icon">💚</span>
          </h1>
          <p class="hero-subtitle">{{ counselorName }} - 专业心理咨询服务</p>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- 返回按钮 -->
      <div class="back-button">
        <el-button :icon="arrowLeftIcon" @click="goBack" class="back-btn">
          <span class="btn-text">返回咨询师列表</span>
        </el-button>
      </div>

      <!-- 主卡片 -->
      <div v-loading="loading" class="appointment-card">
        <!-- 步骤指示器 -->
        <div class="steps-indicator">
          <div class="step-item" :class="{ active: currentStep === 0, completed: currentStep > 0 }">
            <div class="step-number">
              <span v-if="currentStep > 0">✓</span>
              <span v-else>1</span>
            </div>
            <div class="step-label">选择时间</div>
          </div>
          <div class="step-line" :class="{ active: currentStep > 0 }"></div>
          <div class="step-item" :class="{ active: currentStep === 1 }">
            <div class="step-number">
              <span v-if="currentStep > 1">✓</span>
              <span v-else>2</span>
            </div>
            <div class="step-label">填写信息</div>
          </div>
        </div>

        <!-- 步骤1: 选择时间 -->
        <div v-show="currentStep === 0" class="step-content">
          <!-- 咨询方式选择 -->
          <div class="section-block">
            <div class="section-header">
              <span class="section-icon">🎯</span>
              <div class="section-text">
                <h3 class="section-title">选择咨询方式</h3>
                <p class="section-desc">不同咨询方式价格不同，请根据您的需求选择</p>
              </div>
            </div>

            <div class="consultation-types">
              <div
                v-for="type in consultationTypes"
                :key="type.value"
                class="type-card"
                :class="{ selected: formData.type === type.value, disabled: type.disabled }"
                @click="selectType(type.value)"
              >
                <div class="type-icon">{{ type.icon }}</div>
                <div class="type-info">
                  <h4 class="type-name">{{ type.name }}</h4>
                  <p class="type-price">¥{{ type.price }}/小时</p>
                  <p class="type-desc">{{ type.description }}</p>
                </div>
                <div v-if="formData.type === type.value" class="selected-badge">✓</div>
              </div>
            </div>
          </div>

          <!-- 日期选择 -->
          <div class="section-block">
            <div class="section-header">
              <span class="section-icon">📆</span>
              <div class="section-text">
                <h3 class="section-title">选择咨询日期</h3>
                <p class="section-desc">请选择您方便的日期，我们将显示可用时段</p>
              </div>
            </div>

            <div class="calendar-wrapper">
              <el-calendar v-model="selectedDate" class="custom-calendar">
                <template #date-cell="{ data }">
                  <div
                    class="calendar-day"
                    :class="{
                      available: isAvailableDate(data),
                      selected: isSelectedDate(data),
                      disabled: !isAvailableDate(data),
                      today: isToday(data)
                    }"
                  >
                    <span class="day-number">{{ data.date.getDate() }}</span>
                    <span v-if="isToday(data)" class="today-badge">今天</span>
                  </div>
                </template>
              </el-calendar>
            </div>

            <!-- 时段选择 -->
            <div class="time-slots-section">
              <div class="slots-header">
                <h4 class="slots-title">{{ formatDateFriendly(selectedDate) }} - 可选时段</h4>
                <div class="slots-hint">💡 选择您方便的时间段</div>
              </div>

              <div v-if="loadingSlots" class="loading-slots">
                <el-skeleton :rows="3" animated />
              </div>

              <div v-else-if="availableSlots.length === 0" class="no-slots">
                <div class="no-slots-icon">📅</div>
                <h4>暂无可预约时段</h4>
                <p>当前日期没有可预约的时间段，请选择其他日期</p>
              </div>

              <div v-else class="slots-grid">
                <div
                  v-for="slot in availableSlots"
                  :key="slot"
                  class="slot-item"
                  :class="{ selected: formData.timeSlot === slot }"
                  @click="selectSlot(slot)"
                >
                  <div class="slot-time">{{ slot }}</div>
                  <div v-if="formData.timeSlot === slot" class="slot-check">✓</div>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-section">
            <el-button
              type="primary"
              size="large"
              class="next-btn"
              :disabled="!formData.timeSlot"
              @click="nextStep"
            >
              <span class="btn-icon">→</span>
              下一步：填写信息
            </el-button>
          </div>
        </div>

        <!-- 步骤2: 填写信息 -->
        <div v-show="currentStep === 1" class="step-content">
          <!-- 预约信息摘要 -->
          <div class="appointment-summary">
            <div class="summary-header">
              <span class="summary-icon">📋</span>
              <h3>预约信息确认</h3>
            </div>
            <div class="summary-content">
              <div class="summary-item">
                <span class="summary-label">咨询师</span>
                <span class="summary-value">{{ counselorName }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">咨询方式</span>
                <span class="summary-value">{{ getConsultationTypeText(formData.type) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">预约时间</span>
                <span class="summary-value">{{ formatDateFriendly(selectedDate) }} {{ formData.timeSlot }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">咨询费用</span>
                <span class="summary-value price-highlight">¥{{ price }}/小时</span>
              </div>
            </div>
          </div>

          <!-- 联系信息表单 -->
          <div class="section-block">
            <div class="section-header">
              <span class="section-icon">📝</span>
              <div class="section-text">
                <h3 class="section-title">填写联系信息</h3>
                <p class="section-desc">请填写真实信息，方便咨询师与您联系确认</p>
              </div>
            </div>

            <el-form
              ref="formRef"
              :model="formData"
              :rules="rules"
              label-position="top"
              class="appointment-form-custom"
            >
              <div class="form-grid">
                <el-form-item label="您的姓名" prop="userName">
                  <el-input
                    v-model="formData.userName"
                    placeholder="请输入真实姓名"
                    size="large"
                    class="custom-input"
                  >
                    <template #prefix>
                      <span class="input-icon">👤</span>
                    </template>
                  </el-input>
                </el-form-item>

                <el-form-item label="手机号码" prop="contact">
                  <el-input
                    v-model="formData.contact"
                    placeholder="请输入11位手机号"
                    size="large"
                    maxlength="11"
                    class="custom-input"
                  >
                    <template #prefix>
                      <span class="input-icon">📱</span>
                    </template>
                  </el-input>
                </el-form-item>
              </div>

              <el-form-item label="问题描述" prop="description">
                <el-input
                  v-model="formData.description"
                  type="textarea"
                  :rows="5"
                  placeholder="请简要描述您希望咨询的问题，帮助咨询师提前了解您的情况（如：情绪问题、人际关系、工作压力等）"
                  maxlength="500"
                  show-word-limit
                  class="custom-textarea"
                />
              </el-form-item>

              <div class="form-tips">
                <span class="tips-icon">💡</span>
                <span>详细描述您的问题有助于咨询师更好地为您提供服务</span>
              </div>
            </el-form>
          </div>

          <!-- 操作按钮 -->
          <div class="action-section">
            <el-button size="large" class="prev-btn" @click="currentStep--">
              <span class="btn-icon">←</span>
              上一步
            </el-button>
            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="submitting"
              @click="submitAppointment"
            >
              <span class="btn-icon">✓</span>
              确认预约
            </el-button>
          </div>
        </div>
      </div>

      <!-- 底部提示 -->
      <div class="footer-tips">
        <div class="tips-item">
          <span class="tips-icon">🔒</span>
          <span>您的信息将被严格保密</span>
        </div>
        <div class="tips-item">
          <span class="tips-icon">✅</span>
          <span>预约成功后咨询师将与您联系确认</span>
        </div>
        <div class="tips-item">
          <span class="tips-icon">💬</span>
          <span>如有疑问可联系客服咨询</span>
        </div>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="decoration-circle"></div>
      <div class="decoration-circle"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, markRaw, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorDetail, getAvailableSlots, createAppointment } from '@/api/counselor'

// Mark the ArrowLeft icon as raw to prevent reactivity warning
const arrowLeftIcon = markRaw(ArrowLeft)

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const loadingSlots = ref(false)
const currentStep = ref(0)
const submitting = ref(false)

const counselorId = route.query.counselorId
const counselorData = ref({})
const price = ref(0)
const counselorName = ref(route.query.counselorName || '咨询师')

const selectedDate = ref(new Date())
const availableSlots = ref([])

const formData = reactive({
  counselorId: parseInt(counselorId),
  type: 'video',
  date: '',
  timeSlot: '',
  userName: '',
  contact: '',
  description: ''
})

const formRef = ref(null)

// 咨询方式配置
const consultationTypes = computed(() => [
  {
    value: 'video',
    name: '视频咨询',
    icon: '📹',
    price: counselorData.value.priceVideo || 0,
    description: '面对面视频交流，体验更佳',
    disabled: false
  },
  {
    value: 'voice',
    name: '语音咨询',
    icon: '📞',
    price: counselorData.value.priceVoice || 0,
    description: '语音通话，保护隐私',
    disabled: false
  },
  {
    value: 'offline',
    name: '线下咨询',
    icon: '📍',
    price: counselorData.value.priceOffline || 0,
    description: '到店咨询，环境舒适',
    disabled: !counselorData.value.priceOffline
  }
])

const rules = {
  userName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  contact: [
    { required: true, message: '请输入联系方式', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  description: [{ required: true, message: '请输入问题描述', trigger: 'blur' }]
}

// 加载咨询师信息
const loadCounselor = async () => {
  try {
    loading.value = true
    const res = await getCounselorDetail(counselorId)

    // 转换API数据
    const data = res.data
    counselorData.value = {
      id: data.id,
      name: data.name,
      types: data.consultation_types ? data.consultation_types.split(',') : [],
      priceVideo: data.price_video || 0,
      priceVoice: data.price_voice || 0,
      priceOffline: data.price_offline || 0
    }

    counselorName.value = data.name

    // 设置默认的咨询方式（选择第一个支持的类型）
    if (counselorData.value.types.length > 0) {
      formData.type = counselorData.value.types[0]
    }

    updatePrice()
  } catch (error) {
    console.error('加载咨询师信息失败:', error)
    ElMessage.error('加载咨询师信息失败')
  } finally {
    loading.value = false
  }
}

// 更新价格
const updatePrice = () => {
  const priceMap = {
    'video': counselorData.value.priceVideo || 0,
    'voice': counselorData.value.priceVoice || 0,
    'offline': counselorData.value.priceOffline || 0
  }
  price.value = priceMap[formData.type] || 0
}

// 选择咨询方式
const selectType = (type) => {
  const typeConfig = consultationTypes.value.find(t => t.value === type)
  if (typeConfig && !typeConfig.disabled) {
    formData.type = type
    updatePrice()
    // 重置已选择的时段
    formData.timeSlot = ''
  }
}

// 判断是否是可选日期（工作日）
const isAvailableDate = (data) => {
  const date = data.date
  if (!date) return false

  const day = new Date(date).getDay()
  // 周一到周五可用，周末不可用
  return day >= 1 && day <= 5
}

// 判断是否是选中的日期
const isSelectedDate = (data) => {
  if (!selectedDate.value) return false
  const selected = new Date(selectedDate.value)
  const current = new Date(data.date)

  return selected.getDate() === current.getDate() &&
         selected.getMonth() === current.getMonth() &&
         selected.getFullYear() === current.getFullYear()
}

// 判断是否是今天
const isToday = (data) => {
  const today = new Date()
  const current = new Date(data.date)
  return today.getDate() === current.getDate() &&
         today.getMonth() === current.getMonth() &&
         today.getFullYear() === current.getFullYear()
}

// 格式化日期为 YYYY-MM-DD
const formatDate = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 格式化日期为友好显示
const formatDateFriendly = (date) => {
  if (!date) return '选择日期'
  const d = new Date(date)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  if (d.toDateString() === today.toDateString()) {
    return '今天'
  } else if (d.toDateString() === tomorrow.toDateString()) {
    return '明天'
  } else {
    return d.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' })
  }
}

// 获取咨询方式文本
const getConsultationTypeText = (type) => {
  const typeMap = {
    'video': '📹 视频咨询',
    'voice': '📞 语音咨询',
    'offline': '📍 线下咨询'
  }
  return typeMap[type] || type
}

// 加载可预约时段
const loadSlots = async () => {
  if (!selectedDate.value || !counselorId) return

  try {
    loadingSlots.value = true
    const dateStr = formatDate(selectedDate.value)
    const res = await getAvailableSlots(counselorId, dateStr)

    if (res.code === 200 && res.data) {
      // API直接返回数组
      const slots = Array.isArray(res.data) ? res.data : []

      // 过滤出可用时段
      availableSlots.value = slots
        .filter(slot => slot.available === true)
        .map(slot => slot.time)

      if (availableSlots.value.length === 0) {
        console.log('当前日期无可预约时段')
      }
    } else {
      availableSlots.value = []
    }
  } catch (error) {
    console.error('加载时段失败:', error)
    availableSlots.value = []
  } finally {
    loadingSlots.value = false
  }
}

// 选择时段
const selectSlot = (slot) => {
  formData.timeSlot = slot
}

// 监听咨询方式变化
watch(() => formData.type, () => {
  updatePrice()
  // 重置已选择的时段
  formData.timeSlot = ''
})

// 监听日期变化
watch(selectedDate, () => {
  formData.timeSlot = ''
  loadSlots()
})

const nextStep = () => {
  if (!formData.timeSlot) {
    ElMessage.warning('请选择时段')
    return
  }
  currentStep.value = 1
}

const submitAppointment = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    // 准备提交数据 - 字段名要匹配后端Schema
    const submitData = {
      counselor_id: parseInt(counselorId),
      consultation_type: formData.type,
      appointment_date: formatDate(selectedDate.value),
      user_name: formData.userName,
      user_contact: formData.contact,
      problem_description: formData.description
    }

    console.log('提交预约数据:', submitData)

    await createAppointment(submitData)
    ElMessage.success('预约成功！咨询师将与您联系')
    router.push('/counselor/orders')
  } catch (error) {
    console.error('预约失败:', error)
    if (error.response?.data?.detail) {
      ElMessage.error(error.response.data.detail)
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('预约失败，请重试')
    }
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push('/counselor')
}

onMounted(() => {
  if (!counselorId) {
    ElMessage.error('缺少咨询师信息')
    router.push('/counselor')
    return
  }
  loadCounselor()
  loadSlots()
})
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.appointment-form {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  position: relative;
  overflow-x: hidden;
  padding-bottom: 60px;
}

.hero-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
    opacity: 0.5;
  }
}

.hero-content {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  z-index: 1;
}

.hero-title {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;

  .title-icon {
    font-size: 32px;
    animation: bounce 2s infinite;
  }
}

.hero-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.back-button {
  margin: 20px 0;

  .back-btn {
    background: white;
    border: 2px solid #667eea;
    color: #667eea;
    border-radius: 25px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;

    &:hover {
      background: #667eea;
      color: white;
      transform: translateX(-5px);
    }

    .btn-text {
      margin-left: 5px;
    }
  }
}

.appointment-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.steps-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f5f7fa;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;

  .step-number {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #f5f7fa;
    color: #909399;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 20px;
    transition: all 0.3s ease;
  }

  .step-label {
    font-size: 14px;
    color: #909399;
    font-weight: 500;
  }

  &.active {
    .step-number {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      transform: scale(1.1);
    }

    .step-label {
      color: #667eea;
      font-weight: 600;
    }
  }

  &.completed {
    .step-number {
      background: #67c23a;
      color: white;
    }

    .step-label {
      color: #67c23a;
    }
  }
}

.step-line {
  width: 60px;
  height: 2px;
  background: #e8ecf1;
  transition: all 0.3s ease;

  &.active {
    background: linear-gradient(90deg, #67c23a 0%, #667eea 100%);
  }
}

.step-content {
  animation: fadeInUp 0.4s ease-out;
}

.section-block {
  margin-bottom: 40px;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;

  .section-icon {
    font-size: 32px;
  }

  .section-text {
    .section-title {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 5px 0;
    }

    .section-desc {
      color: #909399;
      font-size: 14px;
      margin: 0;
    }
  }
}

.consultation-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.type-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border: 2px solid transparent;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  display: flex;
  gap: 15px;

  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
  }

  &.selected {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-color: #667eea;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
  }

  &.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .type-icon {
    font-size: 40px;
    flex-shrink: 0;
  }

  .type-info {
    flex: 1;

    .type-name {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 5px 0;
    }

    .type-price {
      font-size: 24px;
      font-weight: 700;
      color: #667eea;
      margin: 0 0 5px 0;
    }

    .type-desc {
      font-size: 13px;
      color: #606266;
      margin: 0;
    }
  }

  .selected-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 24px;
    height: 24px;
    background: #67c23a;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
  }
}

.calendar-wrapper {
  margin-bottom: 30px;
}

.custom-calendar {
  border-radius: 12px;
  overflow: hidden;

  :deep(.el-calendar__header) {
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  }

  :deep(.el-calendar__body) {
    padding: 20px;
  }
}

.calendar-day {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  cursor: pointer;
  font-weight: 500;

  .day-number {
    font-size: 16px;
  }

  .today-badge {
    font-size: 10px;
    color: #409eff;
    margin-top: 2px;
  }

  &.available {
    background: rgba(64, 158, 255, 0.1);
    color: #409eff;

    &:hover {
      background: rgba(64, 158, 255, 0.2);
      transform: scale(1.05);
    }
  }

  &.selected {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: scale(1.05);
  }

  &.disabled {
    color: #c0c4cc;
    cursor: not-allowed;
    opacity: 0.5;
  }

  &.today .day-number {
    font-weight: 700;
  }
}

.time-slots-section {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 16px;
  padding: 30px;
}

.slots-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;

  .slots-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin: 0;
  }

  .slots-hint {
    font-size: 13px;
    color: #909399;
  }
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.slot-item {
  background: white;
  border: 2px solid #e8ecf1;
  border-radius: 12px;
  padding: 15px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
  }

  &.selected {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: #667eea;
    color: white;
    transform: scale(1.05);

    .slot-check {
      position: absolute;
      top: 5px;
      right: 5px;
      font-size: 12px;
    }
  }

  .slot-time {
    font-weight: 600;
    font-size: 16px;
  }
}

.no-slots {
  text-align: center;
  padding: 40px 20px;

  .no-slots-icon {
    font-size: 48px;
    margin-bottom: 15px;
  }

  h4 {
    font-size: 18px;
    color: #303133;
    margin: 0 0 10px 0;
  }

  p {
    color: #606266;
    margin: 0;
  }
}

.appointment-summary {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border: 2px solid #667eea;
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 30px;

  .summary-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;

    .summary-icon {
      font-size: 24px;
    }

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .summary-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }

  .summary-item {
    background: white;
    padding: 15px;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    gap: 5px;

    .summary-label {
      font-size: 12px;
      color: #909399;
    }

    .summary-value {
      font-size: 16px;
      font-weight: 600;
      color: #303133;

      &.price-highlight {
        font-size: 20px;
        color: #667eea;
      }
    }
  }
}

.appointment-form-custom {
  :deep(.el-form-item__label) {
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .custom-input,
  .custom-textarea {
    :deep(.el-input__wrapper),
    :deep(.el-textarea__inner) {
      border-radius: 10px;
      border: 2px solid #e8ecf1;
      transition: all 0.3s ease;

      &:hover {
        border-color: #667eea;
      }

      &.is-focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
      }
    }

    .input-icon {
      font-size: 18px;
    }
  }

  .form-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
  }

  .form-tips {
    background: #f0f9ff;
    border-left: 4px solid #409eff;
    border-radius: 4px;
    padding: 12px 16px;
    font-size: 14px;
    color: #606266;
    display: flex;
    align-items: center;
    gap: 10px;

    .tips-icon {
      font-size: 16px;
    }
  }
}

.action-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  padding-top: 40px;
  border-top: 2px solid #f5f7fa;

  .el-button {
    min-width: 180px;
    height: 50px;
    border-radius: 25px;
    font-weight: 600;
    font-size: 16px;
    transition: all 0.3s ease;

    .btn-icon {
      margin-right: 8px;
    }
  }

  .prev-btn {
    background: white;
    border: 2px solid #667eea;
    color: #667eea;

    &:hover {
      background: #667eea;
      color: white;
    }
  }

  .next-btn,
  .submit-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    color: white;

    &:hover:not(:disabled) {
      opacity: 0.9;
      transform: scale(1.05);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.footer-tips {
  display: flex;
  justify-content: center;
  gap: 30px;
  flex-wrap: wrap;
  margin-top: 30px;

  .tips-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: #606266;
    background: white;
    padding: 12px 20px;
    border-radius: 25px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    .tips-icon {
      font-size: 16px;
    }
  }
}

.background-decoration {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  z-index: 100;
  pointer-events: none;

  .decoration-circle {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    opacity: 0.3;
    animation: float 3s infinite;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .hero-title {
    font-size: 28px;
  }

  .appointment-card {
    padding: 20px;
  }

  .consultation-types {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr !important;
  }

  .action-section {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }

  .footer-tips {
    flex-direction: column;
    align-items: center;
    gap: 15px;
  }

  .summary-content {
    grid-template-columns: 1fr !important;
  }
}
</style>