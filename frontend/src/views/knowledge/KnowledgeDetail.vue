<template>
  <div class="knowledge-detail">
    <div class="container">
      <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>

      <el-card v-loading="loading">
        <h1>{{ article.title }}</h1>

        <div class="meta">
          <el-tag>{{ article.category }}</el-tag>
          <span>👁️ {{ article.views }}</span>
          <span>❤️ {{ article.favorites }}</span>
          <span>{{ formatDate(article.createdAt) }}</span>
        </div>

        <el-divider />

        <div class="content" v-html="article.content"></div>

        <el-divider />

        <div class="actions">
          <el-button @click="toggleFavorite">
            <el-icon><Star /></el-icon> {{ article.isFavorited ? '已收藏' : '收藏' }}
          </el-button>
        </div>

        <el-divider />

        <div class="recommend" v-if="recommendations.length">
          <h3>相关推荐</h3>
          <div class="recommend-list">
            <div v-for="item in recommendations" :key="item.id" @click="goTo(item.id)">
              <img :src="item.coverImage" />
              <h4>{{ item.title }}</h4>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Star } from '@element-plus/icons-vue'
import { getKnowledgeDetail, getRecommendedKnowledge, favoriteKnowledge, unfavoriteKnowledge } from '@/api/knowledge'
import { formatDate } from '@/utils/format'

const router = useRouter()
const route = useRoute()
const loading = ref(true)
const article = ref({})
const recommendations = ref([])

const loadArticle = async () => {
  const res = await getKnowledgeDetail(route.params.id)
  article.value = res.data
  loading.value = false
}

const loadRecommend = async () => {
  const res = await getRecommendedKnowledge(route.params.id)
  recommendations.value = res.data || []
}

const toggleFavorite = async () => {
  if (article.value.isFavorited) {
    await unfavoriteKnowledge(route.params.id)
    article.value.isFavorited = false
  } else {
    await favoriteKnowledge(route.params.id)
    article.value.isFavorited = true
  }
}

const goTo = (id) => router.push(`/knowledge/${id}`)
const goBack = () => router.push('/knowledge')

onMounted(() => {
  loadArticle()
  loadRecommend()
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.knowledge-detail {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px $spacing-lg;
}

:deep(.el-card) {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;

  .el-card__body {
    padding: 40px;
  }
}

.knowledge-detail h1 {
  font-size: 30px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 20px;
  line-height: 1.4;
}

.meta {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  color: $text-secondary;
  font-size: 14px;
  align-items: center;
  flex-wrap: wrap;
}

.content {
  font-size: 16px;
  line-height: 1.9;
  color: $text-regular;
  margin-bottom: $spacing-xl;

  :deep(img) {
    max-width: 100%;
    border-radius: 12px;
  }

  :deep(h2), :deep(h3) {
    color: $text-primary;
    margin: 24px 0 12px;
  }

  :deep(blockquote) {
    border-left: 4px solid $primary-color;
    padding-left: 16px;
    color: $text-secondary;
    background: rgba(232,132,90,0.05);
    border-radius: 0 8px 8px 0;
    margin: 16px 0;
    padding: 12px 16px;
  }
}

.actions {
  margin-bottom: $spacing-xl;
}

.recommend-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;

  > div {
    cursor: pointer;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid $border-lighter;
    transition: transform 0.2s, box-shadow 0.2s;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(107,82,68,0.12);
    }
  }

  img {
    width: 100%;
    height: 120px;
    object-fit: cover;
    display: block;
  }

  h4 {
    margin: 10px 12px;
    font-size: 14px;
    color: $text-primary;
    font-weight: 600;
  }
}
</style>
