<template>
  <div class="counselor-list-page">
    <PageHeader />

    <!-- 顶部横幅 -->
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="title-icon">🧠</span>
            找到适合您的心咨询师
            <span class="title-icon">💚</span>
          </h1>
          <p class="hero-subtitle">专业心理团队 • 科学咨询方法 • 隐私保护保障</p>
        </div>
        <div class="hero-stats">
          <div class="stat-item">
            <div class="stat-number">89+</div>
            <div class="stat-label">专业咨询师</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">5000+</div>
            <div class="stat-label">成功案例</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">98%</div>
            <div class="stat-label">满意度</div>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <div class="search-bar">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索咨询师姓名、擅长领域..."
            prefix-icon="Search"
            clearable
            size="large"
            class="search-input"
            @keyup.enter="handleFilterChange"
          >
            <template #prefix>
              <el-icon class="search-icon"><component :is="icons.Search" /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="filter-cards">
          <div class="filter-card">
            <div class="filter-header">
              <span class="filter-icon">📊</span>
              <span class="filter-title">排序方式</span>
            </div>
            <el-select v-model="filters.sort" class="filter-select" placeholder="选择排序">
              <el-option label="🌟 综合" value="default" />
              <el-option label="⭐ 评分最高" value="rating" />
              <el-option label="🔥 销量最高" value="orders" />
              <el-option label="💵 价格最低" value="price-asc" />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 咨询师列表 -->
      <div v-loading="loading" class="counselor-section">
        <!-- 结果统计 -->
        <div v-if="!loading && total > 0" class="result-header">
          <span class="result-count">为您找到 <strong>{{ total }}</strong> 位专业咨询师</span>
        </div>

        <el-skeleton v-if="loading && counselors.length === 0" :rows="3" animated />
        <el-empty v-else-if="!loading && counselors.length === 0" description="暂无符合条件的咨询师" />

        <div class="counselor-grid">
          <div
            v-for="(counselor, index) in counselors"
            :key="counselor.id"
            class="counselor-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <!-- 卡片头部 -->
            <div class="card-header">
              <div class="avatar-wrapper">
                <el-avatar :size="100" :src="counselor.avatar" class="counselor-avatar">
                  <el-icon :size="50"><component :is="icons.User" /></el-icon>
                </el-avatar>
                <div class="online-indicator"></div>
              </div>
              <div class="counselor-title">
                <h3 class="counselor-name">{{ counselor.name }}</h3>
                <p class="counselor-title-text">{{ counselor.title || '心理咨询师' }}</p>
              </div>
            </div>

            <!-- 评分区域 -->
            <div class="rating-section">
              <div class="rating-info">
                <el-rate
                  v-model="counselor.rating"
                  disabled
                  show-score
                  text-color="#ff9900"
                  :score-template="counselor.rating.toFixed(1)"
                />
                <span class="review-count">{{ counselor.reviewCount }}条评价</span>
              </div>
            </div>

            <!-- 标签区域 -->
            <div class="tags-section">
              <div class="specialty-tags">
                <span v-for="specialty in counselor.specialties?.slice(0, 3)" :key="specialty" class="specialty-tag">
                  {{ specialty }}
                </span>
              </div>
              <div class="type-tags">
                <span v-if="counselor.types?.includes('video')" class="type-tag video">📹</span>
                <span v-if="counselor.types?.includes('voice')" class="type-tag voice">📞</span>
                <span v-if="counselor.types?.includes('offline')" class="type-tag offline">📍</span>
              </div>
            </div>

            <!-- 详细信息 -->
            <div class="info-section">
              <div v-if="counselor.experienceYears" class="info-item">
                <span class="info-icon">🎓</span>
                <span class="info-text">{{ counselor.experienceYears }}年经验</span>
              </div>
              <div v-if="counselor.education" class="info-item">
                <span class="info-icon">📚</span>
                <span class="info-text">{{ counselor.education }}</span>
              </div>
            </div>

            <!-- 价格区域 -->
            <div class="price-section">
              <div class="price-info">
                <span class="price-amount">¥{{ counselor.price }}</span>
                <span class="price-unit">/小时</span>
              </div>
              <div class="price-badge">专业认证</div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-section">
              <el-button class="detail-btn" @click="viewDetail(counselor.id)">
                <span class="btn-icon">👋</span>
                了解更多
              </el-button>
              <el-button type="primary" class="appointment-btn" @click="goToAppointment(counselor.id)">
                <span class="btn-icon">📅</span>
                立即预约
              </el-button>
            </div>

            <!-- 装饰元素 -->
            <div class="card-decoration"></div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="total > 0" class="pagination-section">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="total"
            :page-sizes="[12, 24, 36]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- 底部装饰 -->
    <div class="footer-decoration">
      <div class="decoration-circle"></div>
      <div class="decoration-circle"></div>
      <div class="decoration-circle"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, markRaw, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, User } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getCounselorList } from '@/api/counselor'

// Mark icon components as raw to prevent reactivity warnings
const icons = markRaw({
  Search,
  User
})

const router = useRouter()

const loading = ref(false)
const counselors = ref([])
const total = ref(0)

const filters = reactive({
  keyword: '',
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
      keyword: filters.keyword,
      sort: filters.sort,
      page: pagination.page,
      page_size: pagination.pageSize
    }
    const res = await getCounselorList(params)

    // Transform API response to match frontend expectations
    const items = res.data.items || []
    counselors.value = items.map(counselor => ({
      id: counselor.id,
      name: counselor.name,
      avatar: counselor.avatar,
      title: counselor.title,
      rating: counselor.rating || 0,
      reviewCount: counselor.review_count || 0,
      specialties: counselor.specialties ? counselor.specialties.split(',') : [],
      types: counselor.consultation_types ? counselor.consultation_types.split(',') : [],
      price: counselor.price_video || 0,
      experienceYears: counselor.experience_years,
      education: counselor.education,
      bio: counselor.bio
    }))
    total.value = res.data.total || 0
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
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

// 监听排序变化
watch(
  () => filters.sort,
  () => {
    handleFilterChange()
  }
)

onMounted(() => {
  loadCounselors()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.counselor-list-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  position: relative;
  overflow-x: hidden;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 20px 40px;
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
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;

  .title-icon {
    font-size: 36px;
    animation: bounce 2s infinite;
  }
}

.hero-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin-bottom: 40px;
  letter-spacing: 1px;
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 60px;
  flex-wrap: wrap;

  .stat-item {
    text-align: center;

    .stat-number {
      font-size: 36px;
      font-weight: 700;
      margin-bottom: 5px;
    }

    .stat-label {
      font-size: 14px;
      opacity: 0.8;
    }
  }
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}

.filter-section {
  margin-bottom: 40px;
}

.search-bar {
  margin-bottom: 30px;

  .search-input {
    max-width: 600px;
    margin: 0 auto;
    display: block;
    border-radius: 50px;
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);

    :deep(.el-input__wrapper) {
      border-radius: 50px;
      padding: 12px 20px;
      box-shadow: none;
      border: 2px solid transparent;

      &:hover {
        border-color: #667eea;
      }

      &.is-focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
      }
    }

    .search-icon {
      color: #667eea;
      font-size: 18px;
    }
  }
}

.filter-cards {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.filter-card {
  background: white;
  border-radius: 16px;
  padding: 24px 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  min-width: 300px;

  &:hover {
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
    transform: translateY(-2px);
  }

  .filter-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f5f7fa;

    .filter-icon {
      font-size: 24px;
    }

    .filter-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .filter-options {
    display: flex;
    flex-direction: column;
    gap: 12px;

    :deep(.el-checkbox),
    :deep(.el-radio) {
      margin-right: 0;
      height: auto;
      line-height: 1.5;
    }
  }

  .filter-select {
    width: 100%;
    min-width: 200px;
  }
}

.result-header {
  text-align: center;
  margin-bottom: 30px;
  font-size: 16px;
  color: #606266;

  .result-count strong {
    color: #667eea;
    font-size: 20px;
  }
}

.counselor-section {
  min-height: 400px;
}

.counselor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.counselor-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out backwards;

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.2);

    .card-decoration {
      opacity: 1;
    }
  }

  .card-decoration {
    position: absolute;
    top: -50px;
    right: -50px;
    width: 150px;
    height: 150px;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    border-radius: 50%;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  position: relative;
  z-index: 1;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;

  .counselor-avatar {
    border: 4px solid #fff;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

  .online-indicator {
    position: absolute;
    bottom: 5px;
    right: 5px;
    width: 18px;
    height: 18px;
    background: #67c23a;
    border: 3px solid white;
    border-radius: 50%;
    animation: pulse 2s infinite;
  }
}

.counselor-title {
  flex: 1;
  min-width: 0;

  .counselor-name {
    font-size: 22px;
    font-weight: 700;
    color: #303133;
    margin: 0 0 5px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .counselor-title-text {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }
}

.rating-section {
  margin-bottom: 20px;

  .rating-info {
    display: flex;
    align-items: center;
    gap: 10px;

    .review-count {
      color: #909399;
      font-size: 13px;
    }
  }
}

.tags-section {
  margin-bottom: 20px;

  .specialty-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;

    .specialty-tag {
      background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
      color: #606266;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.3s ease;

      &:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transform: scale(1.05);
      }
    }
  }

  .type-tags {
    display: flex;
    gap: 8px;

    .type-tag {
      font-size: 18px;
      padding: 4px 8px;
      border-radius: 8px;
      background: #f5f7fa;
      transition: all 0.3s ease;

      &:hover {
        transform: scale(1.1);
      }
    }
  }
}

.info-section {
  margin-bottom: 20px;

  .info-item {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
    color: #606266;
    font-size: 14px;

    &:last-child {
      margin-bottom: 0;
    }

    .info-icon {
      font-size: 16px;
    }

    .info-text {
      flex: 1;
    }
  }
}

.price-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  border-radius: 12px;
  margin-bottom: 20px;

  .price-info {
    .price-amount {
      font-size: 32px;
      font-weight: 700;
      color: #667eea;
    }

    .price-unit {
      color: #909399;
      font-size: 14px;
      margin-left: 5px;
    }
  }

  .price-badge {
    background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }
}

.action-section {
  display: flex;
  gap: 12px;

  .el-button {
    flex: 1;
    height: 44px;
    border-radius: 12px;
    font-weight: 600;
    transition: all 0.3s ease;

    .btn-icon {
      margin-right: 5px;
    }
  }

  .detail-btn {
    background: white;
    border: 2px solid #667eea;
    color: #667eea;

    &:hover {
      background: #667eea;
      color: white;
      border-color: #667eea;
    }
  }

  .appointment-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;

    &:hover {
      opacity: 0.9;
      transform: scale(1.05);
    }
  }
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.footer-decoration {
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

// 动画
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
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

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
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
@media (max-width: $breakpoint-lg) {
  .counselor-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-stats {
    gap: 30px;
  }
}

@media (max-width: $breakpoint-md) {
  .hero-section {
    padding: 40px 20px 30px;
  }

  .hero-title {
    font-size: 28px;
    flex-direction: column;
    gap: 10px;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .hero-stats {
    flex-direction: column;
    gap: 20px;
  }

  .filter-cards {
    grid-template-columns: 1fr;
  }

  .counselor-grid {
    grid-template-columns: 1fr;
  }

  .action-section {
    flex-direction: column;
  }

  .footer-decoration {
    display: none;
  }
}
</style>