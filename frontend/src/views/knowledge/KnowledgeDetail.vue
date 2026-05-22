<template>
<<<<<<< Updated upstream
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
=======
  <div class="knowledge-detail">
    <div class="container">
      <el-button :icon="ArrowLeft" class="back-btn" round @click="goBack">返回知识列表</el-button>

      <el-card v-loading="loading" class="article-card">
        <!-- 封面图 -->
        <div v-if="article.coverImage || article.cover_image" class="cover-wrap">
          <img :src="article.coverImage || article.cover_image" :alt="article.title" />
        </div>

        <!-- 标签 -->
        <div class="category-row">
          <el-tag v-if="article.category" type="warning" round size="small">{{ article.category }}</el-tag>
          <el-tag
            v-for="tag in tagList"
            :key="tag"
            size="small"
            round
            class="tag-item"
          >{{ tag }}</el-tag>
        </div>

        <!-- 标题 -->
        <h1>{{ article.title }}</h1>

        <!-- 元信息 -->
        <div class="meta-bar">
          <span class="meta-item"><el-icon><User /></el-icon> {{ article.author_name || article.authorName || '心灵驿站' }}</span>
          <span class="meta-item"><el-icon><View /></el-icon> {{ article.view_count || article.viewCount || 0 }} 阅读</span>
          <span class="meta-item"><el-icon><ChatDotSquare /></el-icon> {{ article.comment_count || article.commentCount || 0 }} 评论</span>
          <span class="meta-item">{{ formatDate(article.published_at || article.publishedAt || article.created_at || article.createdAt) }}</span>
        </div>

        <el-divider />

        <!-- 正文 -->
        <div class="content" v-html="article.content"></div>

        <!-- 底部互动栏 -->
        <div class="interact-bar">
          <div class="interact-left">
            <el-button
              :type="article.is_liked !== undefined ? (article.is_liked ? 'danger' : 'default') : (article.isLiked ? 'danger' : 'default')"
              :icon="StarFilled"
              round
              @click="toggleLike"
              class="interact-btn"
            >
              点赞 {{ article.like_count || article.likeCount || 0 }}
            </el-button>
            <el-button
              :type="article.is_favorited !== undefined ? (article.is_favorited ? 'warning' : 'default') : (article.isFavorited ? 'warning' : 'default')"
              :icon="FolderChecked"
              round
              @click="toggleFavorite"
              class="interact-btn"
            >
              收藏 {{ article.favorite_count || article.favoriteCount || 0 }}
            </el-button>
            <el-button :icon="Share" round class="interact-btn" @click="handleShare">分享</el-button>
          </div>
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
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
=======
        <!-- 评论区 -->
        <div class="comment-section">
          <h3 class="section-title">评论 ({{ totalComments }})</h3>

          <!-- 评论输入框 -->
          <div class="comment-input-wrap">
            <el-avatar :size="40" :src="userAvatar" class="comment-avatar">
              <el-icon :size="24"><User /></el-icon>
            </el-avatar>
            <div class="comment-input-area">
              <el-input
                v-model="commentText"
                type="textarea"
                :rows="3"
                placeholder="写下你的评论..."
                maxlength="500"
                show-word-limit
              />
              <el-button
                type="primary"
                round
                :loading="submitting"
                :disabled="!commentText.trim()"
                @click="submitCommentFn"
                class="submit-comment-btn"
              >发表评论</el-button>
>>>>>>> Stashed changes
            </div>
          </div>

          <!-- 评论列表 -->
          <div v-loading="commentLoading" class="comment-list">
            <el-empty v-if="comments.length === 0 && !commentLoading" description="暂无评论，来说点什么吧" :image-size="80" />
            <div v-for="item in comments" :key="item.id" class="comment-item">
              <el-avatar :size="36" class="comment-avatar">
                <el-icon :size="20"><User /></el-icon>
              </el-avatar>
              <div class="comment-body">
                <div class="comment-header">
                  <span class="comment-user">{{ item.user_name || item.userName || '匿名用户' }}</span>
                  <span class="comment-time">{{ formatDate(item.created_at || item.createdAt) }}</span>
                </div>
                <p class="comment-text">{{ item.content }}</p>
                <div class="comment-actions">
                  <el-button text size="small" @click="replyTo(item)">
                    <el-icon><ChatDotSquare /></el-icon> 回复
                  </el-button>
                  <el-button text size="small">
                    <el-icon><StarFilled /></el-icon> {{ item.like_count || 0 }}
                  </el-button>
                </div>
                <!-- 回复框 -->
                <div v-if="replyTarget?.id === item.id" class="reply-input-wrap">
                  <el-input
                    v-model="replyText"
                    type="textarea"
                    :rows="2"
                    :placeholder="`回复 @${item.user_name || item.userName || '匿名用户'}`"
                    maxlength="300"
                  />
                  <div class="reply-actions">
                    <el-button text size="small" @click="replyTarget = null">取消</el-button>
                    <el-button type="primary" size="small" round @click="submitReply(item.id)">回复</el-button>
                  </div>
                </div>
                <!-- 子评论 -->
                <div v-if="item.replies?.length" class="sub-comments">
                  <div v-for="sub in item.replies" :key="sub.id" class="sub-comment">
                    <span class="sub-user">{{ sub.user_name || sub.userName || '匿名用户' }}</span>
                    <span class="sub-text">{{ sub.content }}</span>
                    <span class="sub-time">{{ formatDate(sub.created_at || sub.createdAt) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 评论分页 -->
          <div v-if="totalComments > commentPageSize" class="comment-pagination">
            <el-button text type="primary" @click="loadMoreComments" :loading="commentLoadingMore">
              加载更多评论
            </el-button>
          </div>
        </div>
<<<<<<< Updated upstream
      </section>

      <!-- 返回按钮 -->
      <div class="back-section">
        <el-button size="large" @click="goBack" class="back-button">
          <el-icon><ArrowLeft /></el-icon>
          返回知识库
        </el-button>
=======
      </el-card>

      <!-- 相关推荐 -->
      <div class="recommend-section" v-if="recommendations.length">
        <h3 class="section-title">相关推荐</h3>
        <div class="recommend-grid">
          <div
            v-for="item in recommendations"
            :key="item.id"
            class="recommend-card"
            @click="goTo(item.id)"
          >
            <img
              :src="item.coverImage || item.cover_image || ''"
              :alt="item.title"
              class="recommend-cover"
            />
            <div class="recommend-info">
              <h4>{{ item.title }}</h4>
              <span class="recommend-meta">{{ item.view_count || item.viewCount || 0 }} 阅读</span>
            </div>
          </div>
        </div>
>>>>>>> Stashed changes
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
<<<<<<< Updated upstream
import {
  HomeFilled, Calendar, View, Clock, User, InfoFilled, PriceTag,
  Connection, ArrowLeft
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getKnowledgeDetail, getRecommendedKnowledge } from '@/api/knowledge'
=======
import { ElMessage } from 'element-plus'
import {
  ArrowLeft, User, View, ChatDotSquare, StarFilled, FolderChecked, Share
} from '@element-plus/icons-vue'
import {
  getKnowledgeDetail,
  getRecommendedKnowledge,
  favoriteKnowledge,
  unfavoriteKnowledge,
  likeKnowledge,
  unlikeKnowledge,
  getComments,
  submitComment
} from '@/api/knowledge'
import { useUserStore } from '@/stores/user'
import { formatDate } from '@/utils/format'
>>>>>>> Stashed changes

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(true)
const article = ref({})
const recommendations = ref([])

<<<<<<< Updated upstream
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
=======
// 评论相关
const comments = ref([])
const commentText = ref('')
const replyText = ref('')
const replyTarget = ref(null)
const commentLoading = ref(false)
const commentLoadingMore = ref(false)
const submitting = ref(false)
const totalComments = ref(0)
const commentPage = ref(1)
const commentPageSize = ref(10)

const userAvatar = computed(() => userStore.userInfo?.avatar || '')

// 标签列表
const tagList = computed(() => {
  const tags = article.value.tags
  if (!tags) return []
  return typeof tags === 'string' ? tags.split(',').map(t => t.trim()).filter(Boolean) : tags
})

// 加载文章
const loadArticle = async (id) => {
  try {
    loading.value = true
    const res = await getKnowledgeDetail(id || route.params.id)
    article.value = res.data || {}
  } catch (e) {
    ElMessage.error('加载文章失败')
>>>>>>> Stashed changes
  } finally {
    loading.value = false
  }
}

<<<<<<< Updated upstream
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
=======
// 加载推荐
const loadRecommend = async (id) => {
  try {
    const res = await getRecommendedKnowledge(id || route.params.id)
    recommendations.value = res.data || []
  } catch {
    // silent
  }
}

// 加载评论
const loadComments = async (reset = true) => {
  try {
    if (reset) {
      commentLoading.value = true
      commentPage.value = 1
    } else {
      commentLoadingMore.value = true
    }
    const res = await getComments(route.params.id, {
      page: commentPage.value,
      page_size: commentPageSize.value
    })
    const data = res.data || {}
    if (reset) {
      comments.value = data.items || []
    } else {
      comments.value = [...comments.value, ...(data.items || [])]
    }
    totalComments.value = data.total || 0
  } catch {
    // silent
  } finally {
    commentLoading.value = false
    commentLoadingMore.value = false
  }
}

// 监听路由变化，切换文章时重新加载
watch(() => route.params.id, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadArticle(newId)
    loadRecommend(newId)
    loadComments(true)
    window.scrollTo({ top: 0 })
    replyTarget.value = null
    commentText.value = ''
  }
})

// 加载更多评论
const loadMoreComments = () => {
  commentPage.value++
  loadComments(false)
}

// 点赞/取消点赞
const toggleLike = async () => {
  try {
    const id = route.params.id
    const liked = article.value.is_liked ?? article.value.isLiked
    if (liked) {
      await unlikeKnowledge(id)
      article.value.is_liked = false
      article.value.like_count = Math.max(0, (article.value.like_count || 0) - 1)
    } else {
      await likeKnowledge(id)
      article.value.is_liked = true
      article.value.like_count = (article.value.like_count || 0) + 1
    }
    ElMessage.success(liked ? '已取消点赞' : '点赞成功')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 收藏/取消收藏
const toggleFavorite = async () => {
  try {
    const id = route.params.id
    const favorited = article.value.is_favorited ?? article.value.isFavorited
    if (favorited) {
      await unfavoriteKnowledge(id)
      article.value.is_favorited = false
      article.value.favorite_count = Math.max(0, (article.value.favorite_count || 0) - 1)
    } else {
      await favoriteKnowledge(id)
      article.value.is_favorited = true
      article.value.favorite_count = (article.value.favorite_count || 0) + 1
    }
    ElMessage.success(favorited ? '已取消收藏' : '收藏成功')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 提交评论
const submitCommentFn = async () => {
  const text = commentText.value.trim()
  if (!text) return
  try {
    submitting.value = true
    await submitComment(route.params.id, { content: text })
    ElMessage.success('评论成功')
    commentText.value = ''
    loadComments(true)
  } catch (e) {
    ElMessage.error('评论失败')
  } finally {
    submitting.value = false
  }
}

// 回复评论
const replyTo = (item) => {
  replyTarget.value = item
  replyText.value = ''
}

// 提交回复
const submitReply = async (parentId) => {
  const text = replyText.value.trim()
  if (!text) return
  try {
    await submitComment(route.params.id, { content: text, parent_id: parentId })
    ElMessage.success('回复成功')
    replyText.value = ''
    replyTarget.value = null
    loadComments(true)
  } catch (e) {
    ElMessage.error('回复失败')
  }
}

// 分享
const handleShare = () => {
  const url = window.location.href
  navigator.clipboard?.writeText(url).then(() => {
    ElMessage.success('链接已复制到剪贴板')
  }).catch(() => {
    ElMessage.info('分享链接：' + url)
  })
}

const goTo = (id) => {
  if (id != route.params.id) {
    router.push(`/knowledge/${id}`)
  }
}
const goBack = () => router.push('/knowledge')
>>>>>>> Stashed changes

onMounted(() => {
  loadArticle()
  loadRecommend()
  loadComments(true)
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
  max-width: 860px;
  margin: 0 auto;
<<<<<<< Updated upstream
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
=======
  padding: 32px $spacing-lg 60px;
}

.back-btn {
  margin-bottom: 20px;
  border-radius: $border-radius-full;
}

// ── 文章卡片 ──────────────────────────────────────────
.article-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 24px rgba(107,82,68,0.08) !important;

  :deep(.el-card__body) {
    padding: 0 44px 40px;
  }
}

// ── 封面图 ────────────────────────────────────────────
.cover-wrap {
  margin: 0 -44px 28px;
  border-radius: 20px 20px 0 0;
  overflow: hidden;
  max-height: 380px;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
}

// ── 分类标签 ──────────────────────────────────────────
.category-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;

  .tag-item {
    background: rgba(232,132,90,0.06);
    color: $primary-color;
    border-color: rgba(232,132,90,0.2);
  }
}

// ── 标题 ──────────────────────────────────────────────
h1 {
  font-size: 28px;
  font-weight: 700;
  color: $text-primary;
  line-height: 1.4;
  margin: 0 0 16px;
}

// ── 元信息栏 ──────────────────────────────────────────
.meta-bar {
  display: flex;
  gap: 24px;
>>>>>>> Stashed changes
  flex-wrap: wrap;
  color: $text-secondary;
  font-size: 13px;
  align-items: center;

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;

    .el-icon { font-size: 15px; }
  }
}

<<<<<<< Updated upstream
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
=======
// ── 正文 ──────────────────────────────────────────────
.content {
  font-size: 16px;
  line-height: 2;
  color: $text-regular;
  margin-bottom: 28px;

  :deep(img) {
    max-width: 100%;
    border-radius: 12px;
    margin: 16px 0;
  }

  :deep(h2), :deep(h3), :deep(h4) {
    color: $text-primary;
    margin: 28px 0 14px;
    font-weight: 700;
  }

  :deep(h2) { font-size: 22px; }
  :deep(h3) { font-size: 18px; }

  :deep(p) { margin: 12px 0; }

  :deep(blockquote) {
    border-left: 4px solid $primary-color;
    padding: 16px 20px;
    color: $text-secondary;
    background: rgba(232,132,90,0.04);
    border-radius: 0 10px 10px 0;
    margin: 20px 0;
  }

  :deep(pre) {
    background: #1e1e2e;
    color: #cdd6f4;
    border-radius: 12px;
    padding: 20px;
    overflow-x: auto;
    font-size: 14px;
    line-height: 1.6;
  }

  :deep(code) {
    font-family: 'SF Mono', 'Fira Code', monospace;
    font-size: 0.9em;
  }
}

// ── 互动栏 ────────────────────────────────────────────
.interact-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0 4px;
}

.interact-left {
  display: flex;
  gap: 12px;
}

.interact-btn {
  border-radius: $border-radius-full !important;
  font-weight: 500;
}

// ── 评论区 ────────────────────────────────────────────
.comment-section {
  .section-title {
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 20px;
  }
}

.comment-input-wrap {
  display: flex;
  gap: 14px;
  margin-bottom: 28px;

  .comment-avatar { flex-shrink: 0; }
}

.comment-input-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;

  :deep(.el-textarea__inner) {
    border-radius: 12px;
    resize: none;
  }

  .submit-comment-btn {
    align-self: flex-end;
    border-radius: $border-radius-full;
  }
}

.comment-list {
  display: flex;
  flex-direction: column;
  min-height: 60px;
}

.comment-item {
  display: flex;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid $border-lighter;

  .comment-avatar { flex-shrink: 0; }
}

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;

  .comment-user {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
  }

  .comment-time {
    font-size: 12px;
    color: $text-placeholder;
  }
}

.comment-text {
  font-size: 14px;
  color: $text-regular;
  line-height: 1.6;
  margin: 0 0 8px;
  word-break: break-word;
}

.comment-actions {
  display: flex;
  gap: 4px;
  margin-bottom: 4px;
}

// ── 回复框 ────────────────────────────────────────────
.reply-input-wrap {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;

  :deep(.el-textarea__inner) {
    border-radius: 10px;
    resize: none;
    font-size: 13px;
  }

  .reply-actions {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
  }
}

// ── 子评论 ────────────────────────────────────────────
.sub-comments {
  margin-top: 8px;
  padding: 8px 0 0 16px;
  border-left: 2px solid $border-lighter;
}

.sub-comment {
  padding: 8px 0;
  font-size: 13px;
  line-height: 1.5;

  .sub-user {
    font-weight: 600;
    color: $primary-color;
    margin-right: 8px;
  }

  .sub-text {
    color: $text-regular;
  }

  .sub-time {
    display: block;
    color: $text-placeholder;
    font-size: 11px;
    margin-top: 2px;
  }
}

.comment-pagination {
  text-align: center;
  margin-top: 16px;
}

// ── 推荐区 ────────────────────────────────────────────
.recommend-section {
  margin-top: 32px;

  .section-title {
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 16px;
  }
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.recommend-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 12px rgba(107,82,68,0.05);
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 28px rgba(107,82,68,0.12);
  }

  .recommend-cover {
    width: 100%;
    height: 140px;
    object-fit: cover;
    display: block;
  }

  .recommend-info {
    padding: 12px 14px;

    h4 {
      margin: 0 0 4px;
      font-size: 14px;
      font-weight: 600;
      color: $text-primary;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .recommend-meta {
      font-size: 12px;
      color: $text-placeholder;
    }
>>>>>>> Stashed changes
  }
}

// ── 响应式 ────────────────────────────────────────────
@media (max-width: 768px) {
  .container { padding: 20px 16px 40px; }

  .article-card :deep(.el-card__body) { padding: 0 20px 28px; }

  .cover-wrap {
    margin: 0 -20px 20px;
    max-height: 220px;
    border-radius: 16px 16px 0 0;
  }

  h1 { font-size: 22px; }

  .meta-bar { gap: 14px; }

  .interact-left { flex-wrap: wrap; gap: 8px; }

  .recommend-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  .recommend-grid { grid-template-columns: 1fr; }
  .meta-bar { font-size: 12px; gap: 10px; }
}
</style>
