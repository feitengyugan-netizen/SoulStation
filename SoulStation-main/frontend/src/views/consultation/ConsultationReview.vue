<template>
  <div class="consultation-review">
    <PageHeader />

    <div v-loading="loading" class="review-container">
      <!-- 成功提示 -->
      <el-alert
        v-if="submitted"
        type="success"
        title="评价提交成功！"
        description="感谢您的评价，这将帮助我们改进服务质量。"
        :closable="false"
        show-icon
      />

      <!-- 评价表单 -->
      <el-card v-else class="review-card" shadow="never">
        <template #header>
          <div class="card-header">
            <h3>咨询评价</h3>
            <p>请对本此咨询进行评价，帮助我们改进服务质量</p>
          </div>
        </template>

        <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
          <!-- 评分 -->
          <el-form-item label="总体评分" prop="rating" required>
            <div class="rating-section">
              <el-rate
                v-model="form.rating"
                :texts="['非常差', '较差', '一般', '满意', '非常满意']"
                show-text
                size="large"
                :colors="['#F56C6C', '#E6A23C', '#409EFF', '#409EFF', '#67C23A']"
              />
            </div>
          </el-form-item>

          <!-- 评价标签 -->
          <el-form-item label="评价标签">
            <div class="tags-section">
              <el-checkbox-group v-model="form.tags">
                <el-checkbox-button
                  v-for="tag in availableTags"
                  :key="tag.value"
                  :label="tag.value"
                >
                  {{ tag.label }}
                </el-checkbox-button>
              </el-checkbox-group>
            </div>
          </el-form-item>

          <!-- 详细评价 -->
          <el-form-item label="详细评价">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="6"
              placeholder="请详细描述您的咨询体验，您的反馈对我们非常重要..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>

          <!-- 匿名选项 -->
          <el-form-item label="匿名显示">
            <el-switch v-model="form.isAnonymous" active-text="是" inactive-text="否" />
            <span class="anonymous-hint">选择匿名后，您的评价将不显示真实姓名</span>
          </el-form-item>

          <!-- 提交按钮 -->
          <el-form-item>
            <el-button type="primary" size="large" @click="submitReview" :loading="submitting">
              提交评价
            </el-button>
            <el-button size="large" @click="goBack">
              返回
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/PageHeader.vue'
import { submitReview, getReview } from '@/api/review'

const route = useRoute()
const router = useRouter()

const appointmentId = ref(route.params.appointmentId || route.query.appointmentId)
const loading = ref(true)
const submitting = ref(false)
const submitted = ref(false)
const formRef = ref(null)

const form = reactive({
  rating: 5,
  tags: [],
  content: '',
  isAnonymous: true
})

const availableTags = [
  { label: '专业', value: '专业' },
  { label: '耐心', value: '耐心' },
  { label: '有效', value: '有效' },
  { label: '温暖', value: '温暖' },
  { label: '及时', value: '及时' },
  { label: '清晰', value: '清晰' },
  { label: '有用', value: '有用' },
  { label: '满意', value: '满意' }
]

const rules = {
  rating: [
    { required: true, message: '请选择评分', trigger: 'change' }
  ]
}

// 检查是否已评价
const checkExistingReview = async () => {
  if (!appointmentId.value) {
    ElMessage.error('预约ID不存在')
    goBack()
    return
  }

  try {
    loading.value = true
    const res = await getReview(appointmentId.value)

    if (res.data && res.data.status === 'completed') {
      // 已评价
      submitted.value = true
    }
  } catch (error) {
    console.error('检查评价失败:', error)
  } finally {
    loading.value = false
  }
}

// 提交评价
const submitReview = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    submitting.value = true

    await submitReview(appointmentId.value, {
      rating: form.rating,
      tags: form.tags,
      content: form.content || undefined,
      is_anonymous: form.isAnonymous
    })

    submitted.value = true
    ElMessage.success('评价提交成功！')

    // 3秒后返回
    setTimeout(() => {
      goBack()
    }, 3000)
  } catch (error) {
    console.error('提交评价失败:', error)
    ElMessage.error(error.response?.data?.detail || '提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.push('/profile/orders')
}

onMounted(() => {
  if (appointmentId.value) {
    checkExistingReview()
  }
})
</script>

<style scoped>
.consultation-review {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  padding: 20px;
}

.review-container {
  max-width: 800px;
  margin: 40px auto;
}

.review-card {
  border-radius: 16px;
  overflow: hidden;
}

.card-header {
  text-align: center;
}

.card-header h3 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #2c3e50;
}

.card-header p {
  margin: 0;
  font-size: 14px;
  color: #606266;
}

.rating-section {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.anonymous-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #909399;
}

:deep(.el-checkbox-button) {
  margin-right: 0;
}

:deep(.el-checkbox-button__inner) {
  border-radius: 20px;
  padding: 12px 20px;
}
</style>
