<template>
  <div class="knowledge-detail">
    <PageHeader />
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
import PageHeader from '@/components/PageHeader.vue'
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

<style scoped>
@use '@/styles/variables.scss' as *;
.knowledge-detail { min-height: 100vh; background: $bg-color; }
.container { max-width: 900px; margin: 0 auto; padding: $spacing-lg; }
.knowledge-detail h1 { font-size: 32px; margin-bottom: $spacing-md; }
.meta { display: flex; gap: $spacing-lg; margin-bottom: $spacing-xl; color: $text-secondary; }
.content { font-size: 16px; line-height: 1.8; margin-bottom: $spacing-xl; }
.actions { margin-bottom: $spacing-xl; }
.recommend-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: $spacing-md; }
.recommend-list > div { cursor: pointer; }
.recommend-list img { width: 100%; height: 120px; object-fit: cover; border-radius: $border-radius-md; }
.recommend-list h4 { margin: $spacing-sm 0; }
</style>
