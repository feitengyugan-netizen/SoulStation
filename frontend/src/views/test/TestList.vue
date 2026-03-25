<template>
  <div class="test-list-page">
    <PageHeader />

    <div class="container">
      <!-- 页面标题 -->
      <div class="page-header">
        <h1>心理测试</h1>
        <p>专业科学的测评，了解真实的自己</p>
      </div>

      <!-- Tab切换 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="test-tabs">
        <el-tab-pane label="全部测试" name="all">
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
                <el-icon><User /></el-icon>
                <span class="meta-text">{{ formatNumber(test.participants) }}人参与</span>
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
        </el-tab-pane>

        <el-tab-pane label="我的测试" name="history">
          <!-- 我的测试历史 -->
          <el-card v-loading="historyLoading" class="history-card">
            <el-skeleton v-if="historyLoading && history.length === 0" :rows="5" animated />
            <el-empty v-else-if="!historyLoading && history.length === 0" description="您还没有测试记录">
              <el-button type="primary" @click="goToAllTests">去做测试</el-button>
            </el-empty>

            <div v-else class="history-list">
              <div
                v-for="item in history"
                :key="item.id"
                class="history-item"
                @click="viewResult(item.id)"
              >
                <div class="history-info">
                  <h3 class="history-title">{{ item.test_title }}</h3>
                  <div class="history-meta">
                    <span class="meta-item">
                      <el-icon><Clock /></el-icon>
                      {{ formatDate(item.created_at) }}
                    </span>
                    <el-tag
                      :type="getLevelType(item.result_level)"
                      size="small"
                      class="level-tag"
                    >
                      {{ getLevelText(item.result_level) }}
                    </el-tag>
                  </div>
                  <p v-if="item.result_title" class="result-title">{{ item.result_title }}</p>
                </div>
                <div class="history-action">
                  <el-button type="primary" :icon="ArrowRight" circle />
                </div>
              </div>
            </div>

            <!-- 历史记录分页 -->
            <div v-if="historyTotal > 0" class="pagination">
              <el-pagination
                v-model:current-page="historyPagination.page"
                v-model:page-size="historyPagination.pageSize"
                :total="historyTotal"
                :page-sizes="[10, 20, 50]"
                layout="total, prev, pager, next"
                @size-change="handleHistorySizeChange"
                @current-change="handleHistoryPageChange"
              />
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HotWater, DocumentCopy, Clock, User, ArrowRight } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getTestList, getTestHistory } from '@/api/test'
import { useUserStore } from '@/stores/user'
import { formatNumber } from '@/utils/format'

const router = useRouter()
const userStore = useUserStore()

// 当前激活的tab
const activeTab = ref('all')

// 加载状态
const loading = ref(false)
const historyLoading = ref(false)

// 测试列表
const tests = ref([])
const total = ref(0)

// 历史记录
const history = ref([])
const historyTotal = ref(0)

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

// 历史记录分页
const historyPagination = reactive({
  page: 1,
  pageSize: 10
})

// 加载测试列表
const loadTests = async () => {
  try {
    loading.value = true
    const params = {
      keyword: filters.keyword,
      category: filters.category,
      sort: filters.sort,
      page: pagination.page,
      page_size: pagination.pageSize
    }
    const res = await getTestList(params)

    // 调试日志
    console.log('API返回的数据:', res)

    // 修复数据结构匹配
    tests.value = (res.data?.items || []).map(test => {
      // 根据测试代码选择合适的封面图片
      const coverImages = {
        'SAS20': 'https://images.unsplash.com/photo-1493836512294-502baa1986e2?w=800&h=400&fit=crop', // 焦虑 - 自然平静
        'SDS20': 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&h=400&fit=crop', // 抑郁 - 山脉星空
        'SCL90': 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&h=400&fit=crop', // 症状自评 - 人物思考
        'BIG5_44': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=400&fit=crop', // 大五人格 - 人物肖像
        'PSS10': 'https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=800&h=400&fit=crop', // 压力 - 日落海滩
        'ES20': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=400&fit=crop', // 情绪稳定 - 平静湖面
        'PHQ9': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&h=400&fit=crop', // PHQ-9 - 晨雾树林
        'GAD7': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=400&fit=crop', // GAD-7 - 阳光森林
        // 默认图片
        'default': 'https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=800&h=400&fit=crop'
      }

      return {
        ...test,
        // 使用后端返回的真实数据
        questionCount: test.total_questions || 0,
        coverImage: coverImages[test.test_code] || coverImages['default'],
        isHot: (test.hot_value || 0) > 80,
        // 参与人数：使用后端返回的真实数据
        participants: test.participant_count || 0,
        // 完成时长：使用后端返回的平均时长
        duration: test.avg_duration || Math.floor(test.total_questions * 0.5)
      }
    })

    total.value = res.data?.total || 0

    console.log('处理后的测试数据:', tests.value)
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

// 加载测试历史
const loadHistory = async () => {
  try {
    historyLoading.value = true
    const params = {
      page: historyPagination.page,
      page_size: historyPagination.pageSize
    }
    const res = await getTestHistory(params)

    history.value = res.data?.items || []
    historyTotal.value = res.data?.total || 0

    console.log('历史记录:', history.value)
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载历史记录失败')
  } finally {
    historyLoading.value = false
  }
}

// Tab切换
const handleTabChange = (tabName) => {
  if (tabName === 'history' && !userStore.isLoggedIn) {
    ElMessage.warning('请先登录')
    activeTab.value = 'all'
    router.push('/login')
    return
  }

  if (tabName === 'history') {
    loadHistory()
  }
}

// 历史记录分页大小变化
const handleHistorySizeChange = () => {
  historyPagination.page = 1
  loadHistory()
}

// 历史记录页码变化
const handleHistoryPageChange = () => {
  loadHistory()
}

// 查看结果
const viewResult = (resultId) => {
  router.push(`/test/${resultId}/result`)
}

// 跳转到全部测试
const goToAllTests = () => {
  activeTab.value = 'all'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 7) {
    return date.toLocaleDateString('zh-CN')
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else {
    return '刚刚'
  }
}

// 获取等级文本
const getLevelText = (level) => {
  const levelMap = {
    'none': '无',
    'mild': '轻度',
    'moderate': '中度',
    'severe': '重度'
  }
  return levelMap[level] || level
}

// 获取等级标签类型
const getLevelType = (level) => {
  const typeMap = {
    'none': 'success',
    'mild': 'warning',
    'moderate': 'warning',
    'severe': 'danger'
  }
  return typeMap[level] || 'info'
}

// 查看测试详情
const viewTestDetail = (id) => {
  router.push(`/test/${id}/taking`)
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
@use '@/styles/variables.scss' as *;

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

.test-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: $spacing-lg;
  }

  :deep(.el-tabs__item) {
    font-size: $font-size-large;
    padding: 0 $spacing-xl;
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
  margin-top: $spacing-lg;
}

.history-card {
  .history-list {
    .history-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: $spacing-md;
      border: 1px solid $border-lighter;
      border-radius: $border-radius-md;
      margin-bottom: $spacing-sm;
      cursor: pointer;
      transition: $transition-base;

      &:hover {
        border-color: $primary-color;
        background: rgba($primary-color, 0.05);
      }

      .history-info {
        flex: 1;

        .history-title {
          font-size: $font-size-large;
          font-weight: 600;
          color: $text-primary;
          margin: 0 0 $spacing-xs 0;
        }

        .history-meta {
          display: flex;
          align-items: center;
          gap: $spacing-md;
          margin-bottom: $spacing-xs;

          .meta-item {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: $font-size-small;
            color: $text-secondary;
          }

          .level-tag {
            margin-left: auto;
          }
        }

        .result-title {
          font-size: $font-size-base;
          color: $text-secondary;
          margin: 0;
        }
      }

      .history-action {
        margin-left: $spacing-md;
      }
    }
  }
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
