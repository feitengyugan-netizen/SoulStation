<template>
  <div class="knowledge-detail-page">
    <PageHeader />

    <!-- 面包屑导航 -->
    <div class="breadcrumb-container">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/knowledge' }">
            <el-icon><HomeFilled /></el-icon>
            心理知识库
          </el-breadcrumb-item>
          <el-breadcrumb-item>{{ article.title || '文章详情' }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>

    <div class="container" v-loading="loading">
      <!-- 文章主体 -->
      <article class="article-main">
        <!-- 文章头部 -->
        <header class="article-header">
          <div class="category-tag">
            <el-tag :type="getCategoryTagType(article.category)" size="large" effect="dark">
              {{ getCategoryName(article.category) }}
            </el-tag>
          </div>

          <h1 class="article-title">{{ article.title }}</h1>

          <div class="article-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>{{ formatDate(article.created_at) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><View /></el-icon>
              <span>{{ article.view_count || 0 }} 阅读</span>
            </div>
            <div class="meta-item">
              <el-icon><Clock /></el-icon>
              <span>5-8分钟阅读</span>
            </div>
          </div>

          <div class="author-info" v-if="article.author">
            <el-avatar :size="40" :src="article.author_avatar">
              <el-icon><User /></el-icon>
            </el-avatar>
            <div class="author-details">
              <span class="author-name">{{ article.author }}</span>
              <span class="author-title">{{ article.author_title || '心理咨询师' }}</span>
            </div>
          </div>
        </header>

        <!-- 文章摘要 -->
        <div class="article-summary" v-if="article.summary">
          <div class="summary-content">
            <el-icon class="summary-icon"><InfoFilled /></el-icon>
            <p>{{ article.summary }}</p>
          </div>
        </div>

        <!-- 文章内容 -->
        <div class="article-content">
          <div v-html="article.content" class="content-html"></div>
        </div>

        <!-- 文章标签 -->
        <div class="article-tags" v-if="article.tags && article.tags.length > 0">
          <el-icon><PriceTag /></el-icon>
          <div class="tags-list">
            <el-tag
              v-for="tag in article.tags"
              :key="tag"
              size="small"
              type="info"
              effect="plain"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </article>

      <!-- 分隔线 -->
      <el-divider />

      <!-- 相关推荐 -->
      <section class="related-section" v-if="recommendations.length > 0">
        <h2 class="section-title">
          <el-icon><Connection /></el-icon>
          相关阅读
        </h2>
        <div class="related-grid">
          <div
            v-for="item in recommendations"
            :key="item.id"
            class="related-card"
            @click="goToArticle(item.id)"
          >
            <div class="related-header">
              <el-tag :type="getCategoryTagType(item.category)" size="small">
                {{ getCategoryName(item.category) }}
              </el-tag>
            </div>
            <h3 class="related-title">{{ item.title }}</h3>
            <p class="related-summary">{{ item.summary }}</p>
            <div class="related-footer">
              <span class="read-time">
                <el-icon><Clock /></el-icon>
                5-8分钟
              </span>
              <span class="view-count">
                <el-icon><View /></el-icon>
                {{ item.view_count || 0 }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 返回按钮 -->
      <div class="back-section">
        <el-button size="large" @click="goBack" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回知识库
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  HomeFilled, Calendar, View, Clock, User, InfoFilled, PriceTag,
  Connection, ArrowLeft
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getKnowledgeDetail, getRecommendedKnowledge } from '@/api/knowledge'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const article = ref({})
const recommendations = ref([])

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

const formatDate = (dateString) => {
  if (!dateString) return '暂无日期'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const loadArticle = async () => {
  try {
    loading.value = true
    const res = await getKnowledgeDetail(route.params.id)
    if (res && res.data) {
      article.value = res.data
      // 增加阅读次数
      article.value.view_count = (article.value.view_count || 0) + 1
    }
  } catch (error) {
    console.error('加载文章失败:', error)
  } finally {
    loading.value = false
  }
}

const loadRecommend = async () => {
  try {
    const res = await getRecommendedKnowledge(route.params.id)
    if (res && res.data) {
      recommendations.value = res.data || []
    }
  } catch (error) {
    console.error('加载推荐失败:', error)
  }
}

const goToArticle = (id) => {
  router.push(`/knowledge/${id}`)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const goBack = () => {
  router.push('/knowledge')
}

onMounted(() => {
  loadArticle()
  loadRecommend()
})
</script>

<style scoped>
.knowledge-detail-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
}

/* 面包屑 */
.breadcrumb-container {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e4e7ed;
  padding: 16px 0;
  position: sticky;
  top: 60px;
  z-index: 10;
}

/* 主容器 */
.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 20px 60px;
}

/* 文章主体 */
.article-main {
  background: white;
  border-radius: 20px;
  padding: 48px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 32px;
}

/* 文章头部 */
.article-header {
  text-align: center;
  margin-bottom: 40px;
}

.category-tag {
  margin-bottom: 24px;
}

.article-title {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.4;
  color: #303133;
  margin-bottom: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.article-meta {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 14px;
}

.meta-item .el-icon {
  font-size: 18px;
}

.author-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
}

.author-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.author-name {
  font-weight: 600;
  color: #303133;
}

.author-title {
  font-size: 12px;
  color: #909399;
}

/* 文章摘要 */
.article-summary {
  margin-bottom: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f4fd 100%);
  border-left: 4px solid #0ea5e9;
  border-radius: 12px;
}

.summary-content {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.summary-icon {
  font-size: 24px;
  color: #0ea5e9;
  flex-shrink: 0;
  margin-top: 2px;
}

.summary-content p {
  margin: 0;
  font-size: 16px;
  line-height: 1.6;
  color: #0369a1;
}

/* 文章内容 */
.article-content {
  font-size: 18px;
  line-height: 1.8;
  color: #303133;
}

.content-html :deep(h2) {
  font-size: 28px;
  font-weight: 600;
  margin-top: 48px;
  margin-bottom: 24px;
  color: #303133;
  padding-bottom: 12px;
  border-bottom: 2px solid #e4e7ed;
}

.content-html :deep(h3) {
  font-size: 22px;
  font-weight: 600;
  margin-top: 32px;
  margin-bottom: 16px;
  color: #303133;
}

.content-html :deep(p) {
  margin-bottom: 20px;
  text-align: justify;
}

.content-html :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 12px;
  margin: 24px 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.content-html :deep(ul),
.content-html :deep(ol) {
  margin-bottom: 20px;
  padding-left: 24px;
}

.content-html :deep(li) {
  margin-bottom: 8px;
}

.content-html :deep(blockquote) {
  margin: 24px 0;
  padding: 16px 24px;
  background: #f8f9fa;
  border-left: 4px solid #667eea;
  border-radius: 8px;
  font-style: italic;
  color: #606266;
}

/* 文章标签 */
.article-tags {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid #e4e7ed;
  flex-wrap: wrap;
}

.article-tags .el-icon {
  font-size: 20px;
  color: #909399;
}

.tags-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* 相关推荐 */
.related-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title .el-icon {
  color: #667eea;
  font-size: 28px;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.related-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  border: 2px solid transparent;
}

.related-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #667eea;
}

.related-header {
  margin-bottom: 12px;
}

.related-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.related-summary {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}

.related-footer {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.read-time,
.view-count {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 返回按钮 */
.back-section {
  text-align: center;
}

.back-button {
  padding: 14px 32px;
  font-size: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  transition: all 0.3s ease;
}

.back-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .article-main {
    padding: 24px 16px;
  }

  .article-title {
    font-size: 28px;
  }

  .article-meta {
    flex-direction: column;
    gap: 12px;
  }

  .article-content {
    font-size: 16px;
  }

  .related-grid {
    grid-template-columns: 1fr;
  }
}
</style>
