<template>
  <div class="counselor-list-page">
    <PageHeader />

    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-content">
          <h1 class="page-title">
            <el-icon class="title-icon"><User /></el-icon>
            找咨询师
          </h1>
          <p class="page-subtitle">专业的心理咨询师，为您提供一对一服务</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-number">{{ total }}</span>
            <span class="stat-label">位咨询师</span>
          </div>
        </div>
      </div>

      <!-- 筛选卡片 -->
      <el-card class="filter-card" shadow="never">
        <div class="search-section">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索咨询师姓名、擅长领域..."
            clearable
            size="large"
            @keyup.enter="handleFilterChange"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="filter-section">
          <div class="filter-row">
            <span class="label">擅长领域:</span>
            <el-checkbox-group v-model="filters.specialties">
              <el-checkbox label="anxiety">焦虑抑郁</el-checkbox>
              <el-checkbox label="emotion">情感问题</el-checkbox>
              <el-checkbox label="family">家庭关系</el-checkbox>
              <el-checkbox label="career">职场压力</el-checkbox>
            </el-checkbox-group>
          </div>

          <div class="filter-row">
            <span class="label">咨询方式:</span>
            <el-checkbox-group v-model="filters.types">
              <el-checkbox label="video">视频咨询</el-checkbox>
              <el-checkbox label="voice">语音咨询</el-checkbox>
              <el-checkbox label="offline">线下咨询</el-checkbox>
            </el-checkbox-group>
          </div>

          <div class="filter-row">
            <span class="label">价格范围:</span>
            <el-radio-group v-model="filters.priceRange">
              <el-radio label="">全部</el-radio>
              <el-radio label="0-200">¥0-200</el-radio>
              <el-radio label="200-500">¥200-500</el-radio>
              <el-radio label="500+">¥500+</el-radio>
            </el-radio-group>
          </div>

          <div class="filter-row actions">
            <div class="label">排序:</div>
            <el-select v-model="filters.sort" placeholder="选择排序方式" style="width: 140px">
              <el-option label="综合排序" value="default" />
              <el-option label="评分最高" value="rating" />
              <el-option label="咨询最多" value="orders" />
              <el-option label="价格最低" value="price-asc" />
            </el-select>
          </div>
        </div>
      </el-card>

      <!-- 咨询师列表 -->
      <div v-loading="loading" class="counselor-grid">
        <el-skeleton v-if="loading && counselors.length === 0" :rows="3" animated />

        <el-empty v-else-if="!loading && counselors.length === 0" description="暂无符合条件的咨询师">
          <el-button type="primary" @click="resetFilters">重置筛选</el-button>
        </el-empty>

        <el-card
          v-for="counselor in counselors"
          :key="counselor.id"
          class="counselor-card"
          shadow="hover"
        >
          <div class="card-content">
            <!-- 咨询师头像 -->
            <div class="counselor-avatar">
              <el-avatar :size="100" :src="counselor.avatar">
                <el-icon :size="50"><User /></el-icon>
              </el-avatar>
              <el-tag v-if="counselor.is_verified" type="success" size="small" effect="plain">
                <el-icon style="margin-right: 4px;"><CircleCheck /></el-icon>
                已认证
              </el-tag>
            </div>

            <!-- 咨询师信息 -->
            <div class="counselor-info">
              <div class="info-header">
                <h3 class="counselor-name">{{ counselor.name }}</h3>
                <el-tag type="info" size="small">{{ counselor.title || '心理咨询师' }}</el-tag>
              </div>

              <div class="rating-row">
                <el-rate
                  v-model="counselor.rating"
                  disabled
                  show-score
                  score-template="{value} 分"
                  :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
                />
                <span class="review-count">{{ counselor.reviewCount || 0 }}条评价</span>
              </div>

              <div class="details-row">
                <div class="detail-item">
                  <el-icon class="detail-icon"><Medal /></el-icon>
                  <span>{{ counselor.experience_years || 0 }}年经验</span>
                </div>
                <div class="detail-item">
                  <el-icon class="detail-icon"><Reading /></el-icon>
                  <span>{{ counselor.education || '学历未知' }}</span>
                </div>
              </div>

              <div class="specialties-row">
                <span class="label">擅长:</span>
                <div class="specialties-tags">
                  <el-tag
                    v-for="(specialty, index) in counselor.specialties"
                    :key="index"
                    size="small"
                    type="warning"
                    effect="plain"
                  >
                    {{ getSpecialtyText(specialty) }}
                  </el-tag>
                </div>
              </div>

              <div class="types-row">
                <span class="label">方式:</span>
                <div class="type-tags">
                  <span v-if="counselor.types.includes('video')" class="type-badge video">
                    <el-icon><VideoCamera /></el-icon> 视频
                  </span>
                  <span v-if="counselor.types.includes('voice')" class="type-badge voice">
                    <el-icon><Phone /></el-icon> 语音
                  </span>
                  <span v-if="counselor.types.includes('offline')" class="type-badge offline">
                    <el-icon><Location /></el-icon> 线下
                  </span>
                </div>
              </div>

              <div class="price-section">
                <div class="price-item">
                  <span class="price-label">视频</span>
                  <span class="price-value">¥{{ counselor.price_video }}</span>
                </div>
                <div class="price-item">
                  <span class="price-label">语音</span>
                  <span class="price-value">¥{{ counselor.price_voice }}</span>
                </div>
                <div v-if="counselor.price_offline" class="price-item">
                  <span class="price-label">线下</span>
                  <span class="price-value">¥{{ counselor.price_offline }}</span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="card-actions">
              <el-button @click="viewDetail(counselor.id)" plain>
                <el-icon><InfoFilled /></el-icon>
                查看详情
              </el-button>
              <el-button type="primary" @click="goToAppointment(counselor.id)">
                <el-icon><Calendar /></el-icon>
                立即预约
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="total"
          :page-sizes="[12, 24, 36]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Search, User, CircleCheck, Medal, Reading, VideoCamera,
  Phone, Location, InfoFilled, Calendar
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorList } from '@/api/counselor'

const router = useRouter()

const loading = ref(false)
const counselors = ref([])
const total = ref(0)

const filters = reactive({
  keyword: '',
  specialties: [],
  types: [],
  priceRange: '',
  sort: 'default'
})

const pagination = reactive({
  page: 1,
  pageSize: 12
})

const loadCounselors = async () => {
  try {
    loading.value = true
    const params = {
      keyword: filters.keyword || undefined,
      specialty: filters.specialties.length > 0 ? filters.specialties.join(',') : undefined,
      consultation_type: filters.types.length > 0 ? filters.types.join(',') : undefined,
      price_min: filters.priceRange ? (() => {
        if (filters.priceRange === '0-200') return 0
        if (filters.priceRange === '200-500') return 200
        if (filters.priceRange === '500+') return 500
        return undefined
      })() : undefined,
      price_max: filters.priceRange ? (() => {
        if (filters.priceRange === '0-200') return 200
        if (filters.priceRange === '200-500') return 500
        return undefined
      })() : undefined,
      sort: filters.sort,
      page: pagination.page,
      page_size: pagination.pageSize
    }

    // 移除undefined的参数
    Object.keys(params).forEach(key => {
      if (params[key] === undefined) {
        delete params[key]
      }
    })

    const res = await getCounselorList(params)

    // 处理返回的数据
    if (res.data && res.data.items) {
      counselors.value = res.data.items.map(counselor => ({
        ...counselor,
        // 将逗号分隔的字符串转换为数组
        specialties: counselor.specialties ? counselor.specialties.split(',').map(s => s.trim()) : [],
        types: counselor.consultation_types ? counselor.consultation_types.split(',').map(t => t.trim()) : []
      }))
      total.value = res.data.total || 0
    } else {
      counselors.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  pagination.page = 1
  loadCounselors()
}

const resetFilters = () => {
  filters.keyword = ''
  filters.specialties = []
  filters.types = []
  filters.priceRange = ''
  filters.sort = 'default'
  pagination.page = 1
  loadCounselors()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadCounselors()
}

const handlePageChange = () => {
  loadCounselors()
}

const viewDetail = (id) => {
  router.push(`/counselor/${id}`)
}

const goToAppointment = (id) => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }
  router.push({ path: '/counselor/appointment', query: { counselorId: id } })
}

// 擅长领域文本映射
const getSpecialtyText = (specialty) => {
  const map = {
    'anxiety': '焦虑抑郁',
    'depression': '焦虑抑郁',
    'emotion': '情感问题',
    'family': '家庭关系'
  }
  return map[specialty] || specialty
}

onMounted(() => {
  loadCounselors()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-list-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-xl;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: $spacing-xl;
  padding: $spacing-xl 0;
}

.header-content {
  margin-bottom: $spacing-lg;
}

.page-title {
  font-size: 36px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 $spacing-sm 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
}

.title-icon {
  font-size: 40px;
  color: #409eff;
}

.page-subtitle {
  font-size: 16px;
  color: #606266;
  margin: 0;
}

.header-stats {
  display: flex;
  justify-content: center;
  gap: $spacing-xl;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 600;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 筛选卡片 */
.filter-card {
  border-radius: 16px;
  margin-bottom: $spacing-xl;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.search-section {
  margin-bottom: $spacing-lg;
}

.filter-section {
  .filter-row {
    display: flex;
    align-items: center;
    gap: $spacing-md;
    margin-bottom: $spacing-md;
    padding: $spacing-sm 0;

    &:last-child {
      margin-bottom: 0;
    }

    .label {
      font-weight: 500;
      min-width: 80px;
      color: #606266;
    }
  }

  .filter-row.actions {
    margin-top: $spacing-lg;
    padding-top: $spacing-md;
    border-top: 1px solid #e4e7ed;
  }
}

/* 咨询师网格 */
.counselor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: $spacing-xl;
  margin-bottom: $spacing-xl;
}

/* 咨询师卡片 */
.counselor-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
  height: 100%;

  &:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12) !important;
    transform: translateY(-6px);
  }
}

.card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 咨询师头像区域 */
.counselor-avatar {
  text-align: center;
  margin-bottom: $spacing-md;
  position: relative;
}

:deep(.el-avatar) {
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 咨询师信息 */
.counselor-info {
  flex: 1;
}

.info-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
  flex-wrap: wrap;
}

.counselor-name {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

/* 评分行 */
.rating-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;

  :deep(.el-rate) {
    .el-rate__icon {
      font-size: 18px;
    }
  }
}

.review-count {
  font-size: 13px;
  color: #909399;
}

/* 详情行 */
.details-row {
  display: flex;
  justify-content: center;
  gap: $spacing-lg;
  margin-bottom: $spacing-md;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 14px;
  color: #606266;
}

.detail-icon {
  font-size: 16px;
  color: #409eff;
}

/* 擅长领域 */
.specialties-row {
  display: flex;
  align-items: flex-start;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
  flex-wrap: wrap;
}

.specialties-row .label {
  font-weight: 500;
  color: #606266;
  min-width: auto;
}

.specialties-tags {
  display: flex;
  gap: $spacing-xs;
  flex-wrap: wrap;
  flex: 1;
}

/* 咨询方式 */
.types-row {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
  flex-wrap: wrap;
}

.types-row .label {
  font-weight: 500;
  color: #606266;
  min-width: auto;
}

.type-tags {
  display: flex;
  gap: $spacing-xs;
  flex-wrap: wrap;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

.type-badge.video {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.type-badge.voice {
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  color: white;
}

.type-badge.offline {
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  color: white;
}

/* 价格区域 */
.price-section {
  display: flex;
  justify-content: space-around;
  gap: $spacing-sm;
  margin: $spacing-md 0;
  padding: $spacing-md;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
}

.price-item {
  text-align: center;
  flex: 1;
}

.price-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.price-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #f56c6c;
}

/* 操作按钮 */
.card-actions {
  display: flex;
  gap: $spacing-sm;
  padding-top: $spacing-md;
  border-top: 1px solid #e4e7ed;
}

.card-actions .el-button {
  flex: 1;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  padding: $spacing-xl 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .container {
    padding: $spacing-md;
  }

  .counselor-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 28px;
  }

  .filter-section .filter-row {
    flex-wrap: wrap;

    .label {
      min-width: 100%;
      margin-bottom: $spacing-xs;
    }
  }

  .details-row {
    flex-direction: column;
    gap: $spacing-sm;
  }

  .card-actions {
    flex-direction: column;
  }
}
</style>
