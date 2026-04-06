<template>
  <div class="knowledge-list-page">
    <PageHeader />
    <div class="container">
      <h1>心理知识</h1>

      <el-card class="filter-card">
        <el-input v-model="keyword" placeholder="搜索..." clearable @keyup.enter="loadArticles" />
        <el-select v-model="category" placeholder="分类" @change="loadArticles">
          <el-option label="全部" value="" />
          <el-option label="焦虑症" value="anxiety" />
          <el-option label="抑郁症" value="depression" />
        </el-select>
      </el-card>

      <div v-loading="loading" class="article-grid">
        <el-card v-for="article in articles" :key="article.id" class="article-card" @click="goToDetail(article.id)">
          <img :src="article.coverImage" class="cover" />
          <div class="content">
            <el-tag size="small">{{ article.category }}</el-tag>
            <h3>{{ article.title }}</h3>
            <p class="summary">{{ article.summary }}</p>
            <div class="meta">
              <span>👁️ {{ article.views }}</span>
              <span>❤️ {{ article.favorites }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/PageHeader.vue'
import { getKnowledgeList } from '@/api/knowledge'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const keyword = ref('')
const category = ref('')

const loadArticles = async () => {
  loading.value = true
  const res = await getKnowledgeList({ keyword: keyword.value, category: category.value })
  articles.value = res.data.list || []
  loading.value = false
}

const goToDetail = (id) => router.push(`/knowledge/${id}`)

onMounted(() => loadArticles())
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.knowledge-list-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px $spacing-lg 40px;
}

.knowledge-list-page h1 {
  text-align: center;
  font-size: 36px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 40px;
}

.filter-card {
  margin-bottom: 32px;
  border-radius: 16px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;

  :deep(.el-card__body) {
    display: flex;
    gap: 16px;
    padding: 20px 24px;
    flex-wrap: wrap;
  }
}

.article-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.article-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;

  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 32px rgba(107,82,68,0.14) !important;
  }

  :deep(.el-card__body) {
    padding: 0;
  }

  .cover {
    width: 100%;
    height: 180px;
    object-fit: cover;
    display: block;
  }

  .content {
    padding: 18px 20px;

    h3 {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 10px 0 8px;
      line-height: 1.4;
    }

    .summary {
      font-size: 13px;
      color: $text-secondary;
      line-height: 1.6;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
      margin: 0 0 14px;
    }

    .meta {
      display: flex;
      gap: 14px;
      font-size: 13px;
      color: $text-secondary;
    }
  }
}
</style>
