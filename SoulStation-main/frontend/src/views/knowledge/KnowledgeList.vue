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

<style scoped>
@use '@/styles/variables.scss' as *;
.knowledge-list-page { min-height: 100vh; background: $bg-color; }
.container { max-width: 1200px; margin: 0 auto; padding: $spacing-lg; }
.knowledge-list-page h1 { text-align: center; font-size: 36px; margin-bottom: $spacing-xl; }
.filter-card { margin-bottom: $spacing-lg; padding: $spacing-lg; display: flex; gap: $spacing-md; }
.article-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: $spacing-lg; }
.article-card { cursor: pointer; transition: $transition-base; }
.article-card:hover { transform: translateY(-4px); }
.article-card .cover { width: 100%; height: 180px; object-fit: cover; }
.article-card .content { padding: $spacing-md; }
.article-card h3 { margin: $spacing-sm 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.summary { color: $text-secondary; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; height: 44px; }
.meta { display: flex; gap: $spacing-md; color: $text-secondary; font-size: $font-size-small; }
</style>
