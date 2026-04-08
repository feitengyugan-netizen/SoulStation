<template>
  <div class="knowledge-page">
    <PageHeader />

    <!-- 顶部横幅 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">心理知识库</h1>
        <p class="hero-subtitle">探索心理学知识，关注心理健康</p>
        <p class="hero-description">专业的心理学文章，帮助您更好地了解自己和他人</p>
      </div>
    </div>

    <div class="container">
      <!-- 搜索和筛选区域 -->
      <div class="search-section">
        <div class="search-bar">
          <el-input
            v-model="keyword"
            placeholder="搜索感兴趣的知识"
            clearable
            @keyup.enter="loadArticles"
            class="search-input"
            size="large"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="filter-tabs">
          <div
            v-for="cat in categories"
            :key="cat.value"
            class="filter-tab"
            :class="{ active: category === cat.value }"
            @click="selectCategory(cat.value)"
          >
            <el-icon v-if="cat.icon">
              <component :is="cat.icon" />
            </el-icon>
            {{ cat.label }}
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        center
        class="error-alert"
      />

      <!-- 文章列表 -->
      <div v-loading="loading" class="articles-section">
        <!-- 精选文章 -->
        <div v-if="featuredArticles.length > 0" class="featured-section">
          <h2 class="section-title">
            <el-icon><Star /></el-icon>
            精选推荐
          </h2>
          <div class="featured-grid">
            <div
              v-for="article in featuredArticles"
              :key="article.id"
              class="featured-card"
              @click="goToDetail(article.id)"
            >
              <div class="featured-image">
                <el-icon class="placeholder-icon"><Document /></el-icon>
              </div>
              <div class="featured-content">
                <div class="featured-category">
                  <el-tag size="small">{{ getCategoryName(article.category) }}</el-tag>
                </div>
                <h3 class="featured-title">{{ article.title }}</h3>
                <p class="featured-summary">{{ article.summary }}</p>
                <div class="featured-meta">
                  <span class="read-time">
                    <el-icon><Clock /></el-icon>
                    阅读时间 5-8 分钟
                  </span>
                  <span class="view-count">
                    <el-icon><View /></el-icon>
                    {{ article.view_count || 0 }} 阅读
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 普通文章列表 -->
        <div class="regular-section">
          <h2 v-if="category" class="section-title">
            <el-icon><FolderOpened /></el-icon>
            {{ getCategoryName(category) }}
          </h2>
          <h2 v-else class="section-title">
            <el-icon><Reading /></el-icon>
            全部文章
          </h2>

          <div v-if="!loading && articles.length === 0" class="empty-state">
            <el-empty description="暂无相关文章">
              <template #image>
                <el-icon :size="80" color="#909399"><DocumentDelete /></el-icon>
              </template>
            </el-empty>
          </div>

          <div v-else class="article-grid">
            <div
              v-for="article in articles"
              :key="article.id"
              class="article-card"
              @click="goToDetail(article.id)"
            >
              <div class="card-header">
                <el-tag :type="getCategoryTagType(article.category)" size="small">
                  {{ getCategoryName(article.category) }}
                </el-tag>
                <span class="read-time">
                  <el-icon><Clock /></el-icon>
                  5-8 分钟
                </span>
              </div>

              <div class="card-content">
                <h3 class="article-title">{{ article.title }}</h3>
                <p class="article-summary">{{ article.summary }}</p>

                <div class="card-footer">
                  <div class="article-meta">
                    <span class="meta-item">
                      <el-icon><View /></el-icon>
                      {{ article.view_count || 0 }}
                    </span>
                    <span class="meta-item">
                      <el-icon><Calendar /></el-icon>
                      {{ formatDate(article.created_at) }}
                    </span>
                  </div>
                  <div class="read-more">
                    阅读更多
                    <el-icon><ArrowRight /></el-icon>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="!loading && articles.length > 0" class="pagination-section">
          <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :total="totalArticles"
            layout="prev, pager, next, total"
            @current-change="handlePageChange"
            class="custom-pagination"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, Star, Document, Clock, View, FolderOpened,
  Reading, DocumentDelete, Calendar, ArrowRight
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getKnowledgeList } from '@/api/knowledge'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const keyword = ref('')
const category = ref('')
const currentPage = ref(1)
const pageSize = ref(12)
const totalArticles = ref(0)
const errorMessage = ref('')

const categories = [
  { label: '全部', value: '', icon: 'Reading' },
  { label: '焦虑', value: 'anxiety', icon: 'HelpFilled' },
  { label: '抑郁', value: 'depression', icon: 'Moon' },
  { label: '情绪', value: 'emotion', icon: 'Sunny' },
  { label: '压力', value: 'stress', icon: 'Lightning' },
  { label: '职业', value: 'career', icon: 'Briefcase' },
  { label: '家庭', value: 'family', icon: 'HomeFilled' }
]

const featuredArticles = computed(() => {
  return articles.value.filter(article => article.is_featured).slice(0, 3)
})

const regularArticles = computed(() => {
  return articles.value.filter(article => !article.is_featured)
})

const getCategoryName = (category) => {
  const categoryMap = {
    'anxiety': '焦虑',
    'depression': '抑郁',
    'emotion': '情绪',
    'career': '职业',
    'family': '家庭',
    'stress': '压力管理'
  }
  return categoryMap[category] || category
}

const getCategoryTagType = (category) => {
  const typeMap = {
    'anxiety': 'danger',
    'depression': 'warning',
    'emotion': 'success',
    'career': 'primary',
    'family': 'info',
    'stress': 'warning'
  }
  return typeMap[category] || 'info'
}

const selectCategory = (value) => {
  category.value = value
  currentPage.value = 1
  loadArticles()
}

const loadArticles = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const res = await getKnowledgeList({
      keyword: keyword.value,
      category: category.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })

    if (res && res.data && res.data.items) {
      articles.value = res.data.items
      totalArticles.value = res.data.total || 0
    } else {
      errorMessage.value = '加载失败，请稍后重试'
      articles.value = []
    }
  } catch (error) {
    console.error('加载文章失败:', error)
    errorMessage.value = '加载失败，请稍后重试'
    articles.value = []
  } finally {
    loading.value = false
  }
}

const goToDetail = (id) => {
  router.push(`/knowledge/${id}`)
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadArticles()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDate = (dateString) => {
  if (!dateString) return '暂无日期'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(() => {
  loadArticles()
})
</script>

<style scoped>
.knowledge-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 60px 20px 80px;
  text-align: center;
  color: white;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.4;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.hero-subtitle {
  font-size: 24px;
  margin-bottom: 12px;
  opacity: 0.95;
}

.hero-description {
  font-size: 16px;
  opacity: 0.9;
}

.container {
  max-width: 1400px;
  margin: -40px auto 0;
  padding: 0 20px 40px;
  position: relative;
  z-index: 2;
}

.search-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
}

.search-bar {
  margin-bottom: 24px;
}

.search-input {
  width: 100%;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-tab {
  padding: 10px 20px;
  border-radius: 20px;
  background: #f5f7fa;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  border: 2px solid transparent;
}

.filter-tab:hover {
  background: #e8ecf1;
  transform: translateY(-2px);
}

.filter-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.articles-section {
  min-height: 400px;
}

.error-alert {
  margin-bottom: 24px;
  border-radius: 12px;
}

.featured-section {
  margin-bottom: 48px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 24px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title .el-icon {
  color: #667eea;
  font-size: 32px;
}

.featured-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.featured-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border: 2px solid transparent;
  display: flex;
  height: 200px;
}

.featured-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.featured-image {
  width: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.placeholder-icon {
  font-size: 64px;
  color: rgba(255, 255, 255, 0.3);
}

.featured-content {
  flex: 1;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.featured-category {
  margin-bottom: 12px;
}

.featured-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.featured-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
  flex: 1;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.featured-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.featured-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.regular-section {
  margin-bottom: 32px;
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.article-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.article-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.12);
  border-color: #667eea;
}

.card-header {
  padding: 16px 20px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.read-time {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.card-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.article-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.article-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
  flex: 1;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.article-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.read-more {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #667eea;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

.article-card:hover .read-more {
  transform: translateX(4px);
}

.empty-state {
  background: white;
  border-radius: 16px;
  padding: 60px 20px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.pagination-section {
  display: flex;
  justify-content: center;
  padding: 32px 0;
}

.custom-pagination {
  background: white;
  padding: 8px 16px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.custom-pagination :deep(.el-pager li) {
  border-radius: 8px;
  margin: 0 2px;
}

.custom-pagination :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 18px;
  }

  .hero-description {
    font-size: 14px;
  }

  .featured-grid {
    grid-template-columns: 1fr;
  }

  .featured-card {
    height: auto;
    flex-direction: column;
  }

  .featured-image {
    width: 100%;
    height: 150px;
  }

  .article-grid {
    grid-template-columns: 1fr;
  }

  .filter-tabs {
    overflow-x: auto;
    padding-bottom: 8px;
  }

  .filter-tab {
    flex-shrink: 0;
  }
}
</style>
