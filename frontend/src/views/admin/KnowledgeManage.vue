<template>
  <div class="knowledge-manage">
    <div class="page-header">
      <h2>知识管理</h2>
      <el-button type="primary" :icon="Plus" @click="createArticle">新建文章</el-button>
    </div>

    <el-card>
      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.keyword"
          placeholder="搜索标题或内容"
          style="width: 250px"
          clearable
        />
        <el-select v-model="filters.category" placeholder="全部分类" style="width: 150px" clearable>
          <el-option label="焦虑抑郁" value="anxiety" />
          <el-option label="人际关系" value="relationship" />
          <el-option label="职业发展" value="career" />
          <el-option label="家庭婚姻" value="family" />
          <el-option label="个人成长" value="growth" />
          <el-option label="情绪管理" value="emotion" />
          <el-option label="心理咨询" value="counseling" />
          <el-option label="正念冥想" value="meditation" />
          <el-option label="压力管理" value="stress" />
          <el-option label="睡眠健康" value="health" />
          <el-option label="创伤治疗" value="depression" />
        </el-select>
        <el-button type="primary" @click="loadArticles">查询</el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>

      <!-- 文章列表 -->
      <el-table v-loading="loading" :data="articles" stripe>
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            {{ getCategoryText(row.category) }}
          </template>
        </el-table-column>
        <el-table-column prop="author" label="作者" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
              {{ row.status === 'published' ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="views" label="浏览量" width="100" sortable />
        <el-table-column prop="likes" label="点赞数" width="100" sortable />
        <el-table-column prop="createdAt" label="发布时间" width="180" />
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
            <el-button type="primary" link @click="editArticle(row)">编辑</el-button>
            <el-button type="danger" link @click="deleteArticle(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadArticles"
          @current-change="loadArticles"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getKnowledgeArticles, deleteKnowledgeArticle } from '@/api/admin'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const filters = reactive({
  keyword: '',
  category: ''
})

const loadArticles = async () => {
  try {
    loading.value = true
    const res = await getKnowledgeArticles({
      keyword: filters.keyword,
      category: filters.category,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    // 映射后端字段到前端显示 (API返回items，前端用list)
    articles.value = (res.data.items || res.data.list || []).map(item => ({
      id: item.id,
      title: item.title,
      cover: item.cover_image || '',
      category: item.category,
      author: item.author_name || '',
      views: item.view_count || 0,
      likes: item.like_count || 0,
      favorites: item.favorite_count || 0,
      createdAt: item.published_at || item.created_at || '',
      status: item.status || 'draft',
      content: item.content || ''
    }))
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.keyword = ''
  filters.category = ''
  currentPage.value = 1
  loadArticles()
}

const getCategoryText = (category) => {
  const map = {
    anxiety: '焦虑抑郁',
    relationship: '人际关系',
    career: '职业发展',
    family: '家庭婚姻',
    growth: '个人成长',
    emotion: '情绪管理',
    counseling: '心理咨询',
    meditation: '正念冥想',
    stress: '压力管理',
    health: '睡眠健康',
    depression: '创伤治疗'
  }
  return map[category] || category
}

const createArticle = () => {
  router.push('/admin/knowledge/edit')
}

const editArticle = (row) => {
  router.push(`/admin/knowledge/edit/${row.id}`)
}

const deleteArticle = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除文章《${row.title}》吗？`, '提示', { type: 'warning' })
    await deleteKnowledgeArticle(row.id)
    ElMessage.success('删除成功')
    loadArticles()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

onMounted(() => loadArticles())
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.knowledge-manage { padding: $spacing-lg; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-lg; }
.page-header h2 { margin: 0; }

.filter-bar { display: flex; gap: $spacing-md; margin-bottom: $spacing-lg; }
.pagination { display: flex; justify-content: center; margin-top: $spacing-lg; }
</style>
