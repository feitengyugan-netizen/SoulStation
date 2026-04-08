<template>
  <div class="counselor-detail">
    <PageHeader />
    <div class="container">
      <el-button :icon="ArrowLeft" @click="goBack" class="back-btn">返回列表</el-button>

      <el-card v-loading="loading" class="detail-card">
        <!-- 头部信息 -->
        <div class="counselor-header">
          <el-avatar :size="120" :src="counselor.avatar">
            <el-icon :size="60"><User /></el-icon>
          </el-avatar>
          <div class="header-info">
            <h1>{{ counselor.name }}</h1>
            <p class="title">{{ counselor.title }}</p>
            <div class="rating-section">
              <el-rate v-model="counselor.rating" disabled show-score />
              <span class="stats">{{ counselor.reviewCount }}条评价 | {{ counselor.consultationCount }}次咨询</span>
            </div>
          </div>
          <el-button type="primary" size="large" @click="goToAppointment">
            立即预约
          </el-button>
        </div>

        <el-divider />

        <!-- 基本信息 -->
        <div class="info-section">
          <h3><el-icon><InfoFilled /></el-icon> 基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">性别:</span>
              <span class="value">{{ genderText }}</span>
            </div>
            <div class="info-item">
              <span class="label">从业年限:</span>
              <span class="value">{{ counselor.experienceYears }}年</span>
            </div>
            <div class="info-item">
              <span class="label">学历:</span>
              <span class="value">{{ counselor.education }}</span>
            </div>
            <div class="info-item">
              <span class="label">资质:</span>
              <span class="value">{{ counselor.qualifications }}</span>
            </div>
          </div>
        </div>

        <!-- 擅长领域 -->
        <div class="info-section">
          <h3><el-icon><Star /></el-icon> 擅长领域</h3>
          <div class="tags-container">
            <el-tag
              v-for="specialty in counselor.specialtiesList"
              :key="specialty"
              type="success"
              size="large"
            >
              {{ specialty }}
            </el-tag>
          </div>
        </div>

        <!-- 咨询方式 -->
        <div class="info-section">
          <h3><el-icon><ChatDotRound /></el-icon> 咨询方式</h3>
          <div class="consultation-types">
            <div class="type-item" v-if="counselor.types?.includes('video')">
              <el-icon><VideoCamera /></el-icon>
              <span>视频咨询</span>
              <span class="price">¥{{ counselor.priceVideo }}/小时</span>
            </div>
            <div class="type-item" v-if="counselor.types?.includes('voice')">
              <el-icon><Phone /></el-icon>
              <span>语音咨询</span>
              <span class="price">¥{{ counselor.priceVoice }}/小时</span>
            </div>
            <div class="type-item" v-if="counselor.types?.includes('offline')">
              <el-icon><Location /></el-icon>
              <span>线下咨询</span>
              <span class="price">¥{{ counselor.priceOffline }}/小时</span>
            </div>
          </div>
        </div>

        <!-- 个人简介 -->
        <div class="info-section" v-if="counselor.bio">
          <h3><el-icon><Document /></el-icon> 个人简介</h3>
          <p class="bio-text">{{ counselor.bio }}</p>
        </div>

        <!-- 咨询流派 -->
        <div class="info-section" v-if="counselor.approach">
          <h3><el-icon><Compass /></el-icon> 咨询流派</h3>
          <p>{{ counselor.approach }}</p>
        </div>

        <!-- 成就荣誉 -->
        <div class="info-section" v-if="counselor.achievements">
          <h3><el-icon><Trophy /></el-icon> 成就荣誉</h3>
          <p>{{ counselor.achievements }}</p>
        </div>
      </el-card>

      <!-- 评价区域 -->
      <el-card class="reviews-card">
        <template #header>
          <div class="card-header">
            <h3>用户评价</h3>
            <el-button link @click="loadReviews">查看全部</el-button>
          </div>
        </template>
        <div v-loading="loadingReviews">
          <div v-if="reviews.length > 0">
            <div v-for="review in reviews" :key="review.id" class="review-item">
              <div class="review-header">
                <span class="reviewer-name">{{ review.isAnonymous ? '匿名用户' : review.userName }}</span>
                <el-rate v-model="review.rating" disabled size="small" />
                <span class="review-date">{{ review.createdAt }}</span>
              </div>
              <p v-if="review.content" class="review-content">{{ review.content }}</p>
              <div v-if="review.tags && review.tags.length > 0" class="review-tags">
                <el-tag v-for="tag in review.tags" :key="tag" size="small">{{ tag }}</el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无评价" />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  ArrowLeft, User, InfoFilled, Star, ChatDotRound,
  VideoCamera, Phone, Location, Document, Compass, Trophy
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorDetail, getCounselorReviews } from '@/api/counselor'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const loadingReviews = ref(false)
const counselor = ref({})
const reviews = ref([])

// 性别文本映射
const genderText = computed(() => {
  const genderMap = {
    'male': '男',
    'female': '女',
    'secret': '保密'
  }
  return genderMap[counselor.value.gender] || '保密'
})

// 加载咨询师详情
const loadDetail = async () => {
  try {
    loading.value = true
    const res = await getCounselorDetail(route.params.id)

    // 转换API数据为前端需要的格式
    const data = res.data
    counselor.value = {
      id: data.id,
      name: data.name,
      avatar: data.avatar,
      gender: data.gender,
      title: data.title,
      rating: data.rating || 5.0,
      reviewCount: data.review_count || 0,
      consultationCount: data.consultation_count || 0,
      specialtiesList: data.specialties ? data.specialties.split(',') : [],
      types: data.consultation_types ? data.consultation_types.split(',') : [],
      experienceYears: data.experience_years || 0,
      education: data.education || '',
      qualifications: data.qualifications || '',
      priceVideo: data.price_video || 0,
      priceVoice: data.price_voice || 0,
      priceOffline: data.price_offline || 0,
      bio: data.bio || '',
      approach: data.approach || '',
      achievements: data.achievements || ''
    }

    // 加载评价
    loadReviews()
  } catch (error) {
    console.error('加载咨询师详情失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载评价列表
const loadReviews = async () => {
  try {
    loadingReviews.value = true
    const res = await getCounselorReviews(route.params.id, { page: 1, page_size: 3 })
    if (res.data && res.data.items) {
      reviews.value = res.data.items.map(review => ({
        id: review.id,
        rating: review.rating,
        content: review.content,
        tags: review.tags || [],
        isAnonymous: review.is_anonymous || false,
        userName: review.user_name || '用户',
        createdAt: review.created_at ? new Date(review.created_at).toLocaleDateString() : ''
      }))
    }
  } catch (error) {
    console.error('加载评价失败:', error)
  } finally {
    loadingReviews.value = false
  }
}

const goBack = () => router.push('/counselor')
const goToAppointment = () => {
  router.push({
    path: '/counselor/appointment',
    query: {
      counselorId: route.params.id,
      counselorName: counselor.value.name
    }
  })
}

onMounted(() => loadDetail())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;

.counselor-detail {
  min-height: 100vh;
  background: $bg-color;
  padding-bottom: 40px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.back-btn {
  margin-bottom: $spacing-lg;
}

.detail-card {
  margin-bottom: $spacing-lg;
}

.counselor-header {
  display: flex;
  align-items: center;
  gap: $spacing-xl;
  margin-bottom: $spacing-xl;
}

.header-info {
  flex: 1;
}

.header-info h1 {
  margin: 0 0 $spacing-sm 0;
  font-size: 28px;
  color: $text-primary;
}

.title {
  margin: 0 0 $spacing-md 0;
  color: $text-secondary;
  font-size: 16px;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.stats {
  color: $text-secondary;
  font-size: 14px;
}

.info-section {
  margin: $spacing-xl 0;
  padding: $spacing-lg;
  background: #fafafa;
  border-radius: 8px;
}

.info-section h3 {
  margin: 0 0 $spacing-lg 0;
  font-size: 18px;
  color: $text-primary;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-md;
}

.info-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.info-item .label {
  font-weight: 500;
  color: $text-secondary;
  min-width: 80px;
}

.info-item .value {
  color: $text-primary;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
}

.consultation-types {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-md;
}

.type-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-md;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.type-item .price {
  margin-left: auto;
  font-weight: 500;
  color: #f56c6c;
}

.bio-text {
  line-height: 1.8;
  color: $text-primary;
  white-space: pre-wrap;
}

.reviews-card {
  margin-top: $spacing-lg;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
}

.review-item {
  padding: $spacing-lg 0;
  border-bottom: 1px solid #f0f0f0;
}

.review-item:last-child {
  border-bottom: none;
}

.review-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-sm;
}

.reviewer-name {
  font-weight: 500;
  color: $text-primary;
}

.review-date {
  margin-left: auto;
  color: $text-secondary;
  font-size: 14px;
}

.review-content {
  margin: $spacing-sm 0;
  line-height: 1.6;
  color: $text-primary;
}

.review-tags {
  display: flex;
  gap: $spacing-xs;
  margin-top: $spacing-sm;
}
</style>
