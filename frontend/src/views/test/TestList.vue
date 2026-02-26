<template>
  <div class="test-list-page">
    <PageHeader />

    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>心理测试</h1>
        <p>专业科学的测评，了解真实的自己</p>
      </div>

      <!-- 筛选栏 -->
      <el-card class="filter-card">
        <div class="filter-row">
          <!-- 分类筛选 -->
          <div class="filter-item">
            <span class="label">分类：</span>
            <el-radio-group v-model="filters.category" @change="handleFilterChange">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="anxiety">焦虑</el-radio-button>
              <el-radio-button label="depression">抑郁</el-radio-button>
              <el-radio-button label="personality">性格</el-radio-button>
              <el-radio-button label="career">职业</el-radio-button>
              <el-radio-button label="emotion">情感</el-radio-button>
            </el-radio-group>
          </div>

          <!-- 排序方式 -->
          <div class="filter-item">
            <span class="label">排序：</span>
            <el-select v-model="filters.sort" @change="handleFilterChange" style="width: 120px">
              <el-option label="热门" value="hot" />
              <el-option label="最新" value="latest" />
              <el-option label="评分" value="rating" />
            </el-select>
          </div>

          <!-- 搜索框 -->
          <div class="filter-item search">
            <el-input
              v-model="filters.keyword"
              placeholder="搜索测试名称"
              prefix-icon="Search"
              clearable
              @clear="handleFilterChange"
              @keyup.enter="handleFilterChange"
            />
          </div>
        </div>
      </el-card>

      <!-- 测试列表 -->
      <div v-loading="loading" class="test-grid">
        <el-skeleton v-if="loading && tests.length === 0" :rows="3" animated />

        <el-empty v-else-if="!loading && tests.length === 0" description="暂无测试" />

        <div
          v-for="test in tests"
          :key="test.id"
          class="test-card"
          @click="viewTestDetail(test.id)"
        >
          <!-- 测试封面 -->
          <div class="test-cover">
            <img :src="test.coverImage" :alt="test.title" />
            <div v-if="test.isHot" class="hot-badge">
              <el-icon><HotWater /></el-icon>
              热门
            </div>
          </div>

          <!-- 测试信息 -->
          <div class="test-info">
            <h3 class="test-title">{{ test.title }}</h3>
            <p class="test-description">{{ test.description }}</p>

            <div class="test-meta">
              <div class="meta-item">
                <el-rate
                  v-model="test.rating"
                  disabled
                  show-score
                  text-color="#ff9900"
                  score-template="{value}"
                  size="small"
                />
                <span class="meta-text">({{ formatNumber(test.participants) }}人参与)</span>
              </div>

              <div class="meta-item">
                <el-icon><DocumentCopy /></el-icon>
                <span>{{ test.questionCount }}题</span>
              </div>

              <div class="meta-item">
                <el-icon><Clock /></el-icon>
                <span>{{ test.duration }}分钟</span>
              </div>
            </div>

            <el-button type="primary" class="start-btn" @click.stop="startTest(test.id)">
              开始测试
            </el-button>
          </div>
        </div>
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
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HotWater, DocumentCopy, Clock } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getTestList } from '@/api/test'
import { useUserStore } from '@/stores/user'
import { formatNumber } from '@/utils/format'

const router = useRouter()
const userStore = useUserStore()

// 加载状态
const loading = ref(false)

// 测试列表
const tests = ref([])
const total = ref(0)

// 筛选条件
const filters = reactive({
  category: '',
  sort: 'hot',
  keyword: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 12
})

// 加载测试列表
const loadTests = async () => {
  try {
    loading.value = true
    const params = {
      ...filters,
      ...pagination
    }
    const res = await getTestList(params)
    tests.value = res.data.list || []
    total.value = res.data.total || 0
  } catch (error) {
    console.error('加载测试列表失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 筛选变化
const handleFilterChange = () => {
  pagination.page = 1
  loadTests()
}

// 分页大小变化
const handleSizeChange = () => {
  pagination.page = 1
  loadTests()
}

// 页码变化
const handlePageChange = () => {
  loadTests()
}

// 查看测试详情
const viewTestDetail = (id) => {
  router.push(`/test/${id}`)
}

// 开始测试
const startTest = (id) => {
  // 检查登录状态
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  router.push(`/test/${id}/taking`)
}

// 组件挂载
onMounted(() => {
  loadTests()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.test-list-page {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.page-header {
  text-align: center;
  margin-bottom: $spacing-xl;

  h1 {
    font-size: 36px;
    margin-bottom: $spacing-sm;
    color: $text-primary;
  }

  p {
    font-size: $font-size-base;
    color: $text-secondary;
  }
}

.filter-card {
  margin-bottom: $spacing-lg;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-lg;
  align-items: center;

  .filter-item {
    display: flex;
    align-items: center;
    gap: $spacing-sm;

    .label {
      font-weight: 500;
      color: $text-primary;
    }

    &.search {
      margin-left: auto;
    }
  }
}

.test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.test-card {
  background: $bg-white;
  border-radius: $border-radius-lg;
  overflow: hidden;
  cursor: pointer;
  transition: $transition-base;
  box-shadow: $box-shadow-base;

  &:hover {
    transform: translateY(-8px);
    box-shadow: $box-shadow-dark;

    .test-cover img {
      transform: scale(1.05);
    }
  }
}

.test-cover {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: $transition-base;
  }

  .hot-badge {
    position: absolute;
    top: $spacing-md;
    left: $spacing-md;
    padding: $spacing-xs $spacing-sm;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    border-radius: $border-radius-sm;
    font-size: $font-size-small;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.test-info {
  padding: $spacing-md;

  .test-title {
    font-size: $font-size-large;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: $spacing-sm;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .test-description {
    font-size: $font-size-base;
    color: $text-secondary;
    margin-bottom: $spacing-md;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
    overflow: hidden;
    text-overflow: ellipsis;
    min-height: 44px;
  }

  .test-meta {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-md;
    margin-bottom: $spacing-md;
    padding-bottom: $spacing-md;
    border-bottom: 1px solid $border-lighter;

    .meta-item {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: $font-size-small;
      color: $text-secondary;

      .meta-text {
        margin-left: 4px;
      }
    }
  }

  .start-btn {
    width: 100%;
  }
}

.pagination {
  display: flex;
  justify-content: center;
}

// 响应式
@media (max-width: $breakpoint-md) {
  .test-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;

    .filter-item.search {
      margin-left: 0;
    }

    .el-radio-group {
      display: flex;
      flex-wrap: wrap;
    }
  }
}

@media (max-width: $breakpoint-sm) {
  .test-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 28px;
  }
}
</style>
