<template>
  <div class="counselor-detail-page">
    <PageHeader />

    <div class="container">
      <!-- 返回按钮 -->
      <div class="back-section">
        <el-button :icon="ArrowLeft" @click="goBack" size="large" plain>
          返回列表
        </el-button>
      </div>

      <div v-loading="loading" class="detail-content">
        <el-skeleton v-if="loading" :rows="8" animated />

        <template v-else-if="counselor.id">
          <!-- 咨询师基本信息卡片 -->
          <el-card class="profile-card" shadow="never">
            <div class="profile-content">
              <!-- 左侧头像 -->
              <div class="avatar-section">
                <el-avatar :size="140" :src="counselor.avatar">
                  <el-icon :size="70"><User /></el-icon>
                </el-avatar>
                <el-tag v-if="counselor.is_verified" type="success" size="large" effect="plain" class="verified-tag">
                  <el-icon style="margin-right: 4px;"><CircleCheck /></el-icon>
                  已认证
                </el-tag>
              </div>

              <!-- 右侧信息 -->
              <div class="info-section">
                <div class="info-header">
                  <h1 class="counselor-name">{{ counselor.name }}</h1>
                  <el-tag v-if="counselor.title" type="info" size="large" effect="plain">
                    {{ counselor.title }}
                  </el-tag>
                </div>

                <!-- 评分和统计 -->
                <div class="rating-stats">
                  <div class="stat-item">
                    <el-rate
                      v-model="counselor.rating"
                      disabled
                      show-score
                      score-template="{value}"
                      :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                    />
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <span class="stat-label">咨询次数</span>
                    <span class="stat-value">{{ counselor.consultation_count || 0 }}次</span>
                  </div>
                  <div class="stat-divider"></div>
                  <div class="stat-item">
                    <span class="stat-label">用户评价</span>
                    <span class="stat-value">{{ counselor.review_count || 0 }}条</span>
                  </div>
                </div>

                <!-- 快速信息 -->
                <div class="quick-info">
                  <div class="info-item" v-if="counselor.experience_years">
                    <el-icon class="info-icon"><Medal /></el-icon>
                    <span>{{ counselor.experience_years }}年从业经验</span>
                  </div>
                  <div class="info-item" v-if="counselor.education">
                    <el-icon class="info-icon"><Reading /></el-icon>
                    <span>{{ counselor.education }}</span>
                  </div>
                  <div class="info-item">
                    <el-icon class="info-icon"><Location /></el-icon>
                    <span>{{ counselor.status === 'active' ? '在线可约' : '暂不可约' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 详细信息网格 -->
          <div class="detail-grid">
            <!-- 左侧：专业信息 -->
            <div class="left-column">
              <!-- 擅长领域 -->
              <el-card class="info-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon class="header-icon"><Star /></el-icon>
                    <span class="header-title">擅长领域</span>
                  </div>
                </template>
                <div class="specialties-list">
                  <el-tag
                    v-for="(specialty, index) in specialtiesList"
                    :key="index"
                    type="warning"
                    effect="plain"
                    size="large"
                  >
                    {{ getSpecialtyText(specialty) }}
                  </el-tag>
                </div>
              </el-card>

              <!-- 咨询方式 -->
              <el-card class="info-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon class="header-icon"><VideoCamera /></el-icon>
                    <span class="header-title">咨询方式</span>
                  </div>
                </template>
                <div class="types-list">
                  <div v-if="typesList.includes('video')" class="type-item">
                    <el-icon class="type-icon video"><VideoCamera /></el-icon>
                    <span class="type-name">视频咨询</span>
                    <el-tag type="success" effect="plain">支持</el-tag>
                  </div>
                  <div v-if="typesList.includes('voice')" class="type-item">
                    <el-icon class="type-icon voice"><Phone /></el-icon>
                    <span class="type-name">语音咨询</span>
                    <el-tag type="success" effect="plain">支持</el-tag>
                  </div>
                  <div v-if="typesList.includes('offline')" class="type-item">
                    <el-icon class="type-icon offline"><Location /></el-icon>
                    <span class="type-name">线下咨询</span>
                    <el-tag type="success" effect="plain">支持</el-tag>
                  </div>
                </div>
              </el-card>

              <!-- 收费标准 -->
              <el-card class="info-card price-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon class="header-icon"><Money /></el-icon>
                    <span class="header-title">收费标准</span>
                  </div>
                </template>
                <div class="price-list">
                  <div class="price-item">
                    <div class="price-label">
                      <el-icon><VideoCamera /></el-icon>
                      <span>视频咨询</span>
                    </div>
                    <div class="price-value">
                      <span class="currency">¥</span>
                      <span class="amount">{{ counselor.price_video || '-' }}</span>
                      <span class="unit">/小时</span>
                    </div>
                  </div>
                  <div class="price-item">
                    <div class="price-label">
                      <el-icon><Phone /></el-icon>
                      <span>语音咨询</span>
                    </div>
                    <div class="price-value">
                      <span class="currency">¥</span>
                      <span class="amount">{{ counselor.price_voice || '-' }}</span>
                      <span class="unit">/小时</span>
                    </div>
                  </div>
                  <div v-if="counselor.price_offline" class="price-item">
                    <div class="price-label">
                      <el-icon><Location /></el-icon>
                      <span>线下咨询</span>
                    </div>
                    <div class="price-value">
                      <span class="currency">¥</span>
                      <span class="amount">{{ counselor.price_offline }}</span>
                      <span class="unit">/小时</span>
                    </div>
                  </div>
                </div>
              </el-card>
            </div>

            <!-- 右侧：详细介绍 -->
            <div class="right-column">
              <!-- 个人简介 -->
              <el-card v-if="counselor.bio" class="info-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon class="header-icon"><Document /></el-icon>
                    <span class="header-title">个人简介</span>
                  </div>
                </template>
                <div class="bio-content">
                  {{ counselor.bio }}
                </div>
              </el-card>

              <!-- 咨询流派 -->
              <el-card v-if="counselor.approach" class="info-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon class="header-icon"><Compass /></el-icon>
                    <span class="header-title">咨询流派</span>
                  </div>
                </template>
                <div class="approach-content">
                  {{ counselor.approach }}
                </div>
              </el-card>

              <!-- 资质证书 -->
              <el-card v-if="counselor.qualifications" class="info-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon class="header-icon"><Trophy /></el-icon>
                    <span class="header-title">资质证书</span>
                  </div>
                </template>
                <div class="qualifications-content">
                  {{ counselor.qualifications }}
                </div>
              </el-card>

              <!-- 成就荣誉 -->
              <el-card v-if="counselor.achievements" class="info-card" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <el-icon class="header-icon"><Medal /></el-icon>
                    <span class="header-title">成就荣誉</span>
                  </div>
                </template>
                <div class="achievements-content">
                  {{ counselor.achievements }}
                </div>
              </el-card>
            </div>
          </div>

          <!-- 预约按钮 -->
          <div class="action-section">
            <el-button type="primary" size="large" @click="goToAppointment" class="book-button">
              <el-icon><Calendar /></el-icon>
              立即预约
            </el-button>
          </div>
        </template>

        <el-empty v-else description="咨询师不存在或已被删除" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, User, CircleCheck, Medal, Reading, Location, Star,
  VideoCamera, Phone, Money, Document, Compass, Trophy, Calendar
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorDetail } from '@/api/counselor'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const counselor = ref({})

// 计算属性：将字符串转换为数组
const specialtiesList = computed(() => {
  if (!counselor.value.specialties) return []
  if (Array.isArray(counselor.value.specialties)) return counselor.value.specialties
  return counselor.value.specialties.split(',').map(s => s.trim())
})

const typesList = computed(() => {
  if (!counselor.value.consultation_types) return []
  if (Array.isArray(counselor.value.consultation_types)) return counselor.value.consultation_types
  return counselor.value.consultation_types.split(',').map(t => t.trim())
})

const loadDetail = async () => {
  try {
    loading.value = true
    const res = await getCounselorDetail(route.params.id)
    counselor.value = res.data
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载咨询师详情失败')
  } finally {
    loading.value = false
  }
}

const getSpecialtyText = (specialty) => {
  const map = {
    'anxiety': '焦虑抑郁',
    'depression': '焦虑抑郁',
    'emotion': '情感问题',
    'family': '家庭关系',
    'career': '职场压力'
  }
  return map[specialty] || specialty
}

const goBack = () => router.push('/counselor')

const goToAppointment = () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push({ path: '/counselor/appointment', query: { counselorId: route.params.id } })
}

onMounted(() => loadDetail())
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-detail-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-xl;
}

.back-section {
  margin-bottom: $spacing-lg;
}

/* 个人资料卡片 */
.profile-card {
  border-radius: 16px;
  margin-bottom: $spacing-xl;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.profile-content {
  display: flex;
  gap: $spacing-xl;
  align-items: flex-start;
}

.avatar-section {
  text-align: center;
  flex-shrink: 0;

  :deep(.el-avatar) {
    border: 4px solid #fff;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }
}

.verified-tag {
  margin-top: $spacing-md;
}

.info-section {
  flex: 1;
}

.info-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
  flex-wrap: wrap;
}

.counselor-name {
  font-size: 32px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

/* 评分统计 */
.rating-stats {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  padding: $spacing-lg 0;
  border-top: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: $spacing-lg;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: #e4e7ed;
}

/* 快速信息 */
.quick-info {
  display: flex;
  gap: $spacing-xl;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 14px;
  color: #606266;
}

.info-icon {
  font-size: 16px;
  color: #409eff;
}

/* 详细信息网格 */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
}

/* 信息卡片 */
.info-card {
  border-radius: 12px;
  margin-bottom: $spacing-lg;
  border: 1px solid #ebeef5;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
    transform: translateY(-2px);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.header-icon {
  font-size: 18px;
  color: #409eff;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

/* 擅长领域 */
.specialties-list {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

/* 咨询方式 */
.types-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.type-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md;
  background: #f8f9fa;
  border-radius: 8px;
}

.type-icon {
  font-size: 24px;
  margin-right: $spacing-md;
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

.type-name {
  flex: 1;
  font-size: 15px;
  font-weight: 500;
  color: #2c3e50;
}

/* 价格列表 */
.price-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.price-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
}

.price-label {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: 15px;
  color: #606266;

  .el-icon {
    font-size: 20px;
    color: #409eff;
  }
}

.price-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.currency {
  font-size: 16px;
  color: #f56c6c;
}

.amount {
  font-size: 28px;
  font-weight: 600;
  color: #f56c6c;
}

.unit {
  font-size: 14px;
  color: #909399;
}

/* 文本内容 */
.bio-content,
.approach-content,
.qualifications-content,
.achievements-content {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

/* 操作区域 */
.action-section {
  text-align: center;
  padding: $spacing-xl 0;
}

.book-button {
  min-width: 200px;
  font-size: 16px;
  padding: 14px 40px;
  border-radius: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;

  &:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .container {
    padding: $spacing-md;
  }

  .profile-content {
    flex-direction: column;
    align-items: center;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .counselor-name {
    font-size: 24px;
  }

  .rating-stats {
    flex-wrap: wrap;
    gap: $spacing-md;
  }

  .stat-divider {
    display: none;
  }

  .quick-info {
    flex-direction: column;
    gap: $spacing-sm;
  }
}
</style>
