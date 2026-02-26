<template>
  <div class="test-result">
    <PageHeader />

    <div class="container">
      <!-- 顶部操作栏 -->
      <div class="result-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>测试结果报告</h2>
        <el-dropdown :icon="Share" @command="handleShare">
          <el-button circle />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="link">
                <el-icon><Link /></el-icon>
                复制链接
              </el-dropdown-item>
              <el-dropdown-item command="image">
                <el-icon><Picture /></el-icon>
                生成长图
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 结果卡片 -->
      <el-card v-loading="loading" class="result-card">
        <el-skeleton v-if="loading" :rows="8" animated />

        <div v-else class="result-content">
          <!-- 测试标题 -->
          <div class="test-title">
            <h1>{{ resultData.testName }} - 测试结果</h1>
          </div>

          <!-- 总分展示 -->
          <div class="score-section">
            <div class="score-display">
              <div class="score-number">
                <span class="score">{{ resultData.score }}</span>
                <span class="divider">/</span>
                <span class="max-score">{{ resultData.maxScore }}</span>
              </div>
              <div class="score-label">总分</div>
            </div>

            <!-- 结果等级 -->
            <div class="result-level" :class="resultData.levelClass">
              <el-icon :size="48">
                <component :is="resultData.levelIcon" />
              </el-icon>
              <div class="level-text">
                <div class="level-label">您的程度</div>
                <div class="level-name">{{ resultData.level }}</div>
              </div>
            </div>
          </div>

          <!-- 维度分析 -->
          <div v-if="resultData.dimensions && resultData.dimensions.length > 0" class="dimensions-section">
            <h3>各维度得分</h3>
            <div class="dimensions-list">
              <div
                v-for="dimension in resultData.dimensions"
                :key="dimension.name"
                class="dimension-item"
              >
                <div class="dimension-info">
                  <span class="dimension-name">{{ dimension.name }}</span>
                  <span class="dimension-score">{{ dimension.score }}/{{ dimension.maxScore }}</span>
                </div>
                <el-progress
                  :percentage="getDimensionPercentage(dimension)"
                  :color="getDimensionColor(dimension)"
                />
              </div>
            </div>
          </div>

          <!-- 建议 -->
          <div v-if="resultData.suggestions && resultData.suggestions.length > 0" class="suggestions-section">
            <h3>
              <el-icon><CircleCheck /></el-icon>
              建议
            </h3>
            <div class="suggestions-list">
              <div
                v-for="(suggestion, index) in resultData.suggestions"
                :key="index"
                class="suggestion-item"
              >
                <span class="suggestion-number">{{ index + 1 }}</span>
                <span class="suggestion-text">{{ suggestion }}</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button :icon="TrendCharts" @click="viewTrend">
              查看详细分析
            </el-button>
            <el-button
              :type="resultData.isFavorited ? 'primary' : 'default'"
              :icon="resultData.isFavorited ? StarFilled : Star"
              @click="toggleFavorite"
            >
              {{ resultData.isFavorited ? '已收藏' : '收藏' }}
            </el-button>
            <el-button :icon="RefreshRight" @click="retakeTest">
              重新测试
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 相关推荐 -->
      <el-card v-if="recommendations.length > 0" class="recommendations-card">
        <template #header>
          <span>相关推荐测试</span>
        </template>

        <div class="recommendations-list">
          <div
            v-for="test in recommendations"
            :key="test.id"
            class="recommendation-item"
            @click="goToTest(test.id)"
          >
            <img :src="test.coverImage" :alt="test.title" class="recommendation-cover" />
            <div class="recommendation-info">
              <h4>{{ test.title }}</h4>
              <p>{{ test.description }}</p>
            </div>
            <el-button type="primary" :icon="ArrowRight" circle />
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Share,
  Link,
  Picture,
  TrendCharts,
  Star,
  StarFilled,
  RefreshRight,
  ArrowRight,
  CircleCheck,
  WarningFilled,
  InfoFilled
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getTestResult, favoriteResult, unfavoriteResult } from '@/api/test'

const router = useRouter()
const route = useRoute()

// 结果ID
const resultId = route.params.id

// 加载状态
const loading = ref(true)

// 结果数据
const resultData = ref({
  testName: '',
  score: 0,
  maxScore: 0,
  level: '',
  levelClass: '',
  levelIcon: '',
  dimensions: [],
  suggestions: [],
  isFavorited: false
})

// 推荐测试
const recommendations = ref([])

// 计算等级样式
const levelConfig = {
  '无': { class: 'level-none', icon: InfoFilled },
  '轻度': { class: 'level-mild', icon: WarningFilled },
  '中度': { class: 'level-moderate', icon: WarningFilled },
  '重度': { class: 'level-severe', icon: WarningFilled }
}

// 获取维度百分比
const getDimensionPercentage = (dimension) => {
  return Math.round((dimension.score / dimension.maxScore) * 100)
}

// 获取维度颜色
const getDimensionColor = (dimension) => {
  const percentage = getDimensionPercentage(dimension)
  if (percentage >= 75) return '#67C23A'
  if (percentage >= 50) return '#E6A23C'
  return '#F56C6C'
}

// 加载测试结果
const loadResult = async () => {
  try {
    loading.value = true
    const res = await getTestResult(resultId)

    const data = res.data
    const levelData = levelConfig[data.level] || levelConfig['无']

    resultData.value = {
      testName: data.testName,
      score: data.score,
      maxScore: data.maxScore,
      level: data.level,
      levelClass: levelData.class,
      levelIcon: levelData.icon,
      dimensions: data.dimensions || [],
      suggestions: data.suggestions || [],
      isFavorited: data.isFavorited || false
    }

    recommendations.value = data.recommendations || []
  } catch (error) {
    console.error('加载结果失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 切换收藏状态
const toggleFavorite = async () => {
  try {
    if (resultData.value.isFavorited) {
      await unfavoriteResult(resultId)
      resultData.value.isFavorited = false
      ElMessage.success('取消收藏')
    } else {
      await favoriteResult(resultId)
      resultData.value.isFavorited = true
      ElMessage.success('收藏成功')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

// 查看趋势
const viewTrend = () => {
  router.push('/test/trend?testId=' + resultData.value.testId)
}

// 重新测试
const retakeTest = () => {
  router.push(`/test/${resultData.value.testId}/taking`)
}

// 跳转到推荐测试
const goToTest = (testId) => {
  router.push(`/test/${testId}`)
}

// 返回
const goBack = () => {
  router.push('/test')
}

// 分享
const handleShare = (command) => {
  if (command === 'link') {
    // 复制链接
    const url = window.location.href
    navigator.clipboard.writeText(url).then(() => {
      ElMessage.success('链接已复制到剪贴板')
    }).catch(() => {
      ElMessage.error('复制失败')
    })
  } else if (command === 'image') {
    ElMessage.info('生成长图功能开发中...')
  }
}

// 组件挂载
onMounted(() => {
  loadResult()
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.test-result {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.result-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;

  h2 {
    flex: 1;
    margin: 0;
  }
}

.result-card {
  margin-bottom: $spacing-lg;
}

.result-content {
  .test-title {
    text-align: center;
    margin-bottom: $spacing-xl;

    h1 {
      font-size: $font-size-extra-large;
      margin: 0;
    }
  }

  .score-section {
    display: flex;
    justify-content: center;
    gap: $spacing-xl;
    margin-bottom: $spacing-xl;
    padding: $spacing-xl;
    background: $bg-color;
    border-radius: $border-radius-lg;

    .score-display {
      text-align: center;

      .score-number {
        font-size: 48px;
        font-weight: 600;
        color: $primary-color;

        .score {
          font-size: 64px;
        }

        .divider {
          margin: 0 $spacing-sm;
        }

        .max-score {
          font-size: 36px;
          color: $text-secondary;
        }
      }

      .score-label {
        margin-top: $spacing-sm;
        font-size: $font-size-base;
        color: $text-secondary;
      }
    }

    .result-level {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-lg;
      border-radius: $border-radius-lg;

      &.level-mild {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
      }

      &.level-moderate {
        background: linear-gradient(135deg, #fab1a0 0%, #e17055 100%);
      }

      &.level-severe {
        background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
      }

      .level-text {
        .level-label {
          font-size: $font-size-small;
          opacity: 0.9;
        }

        .level-name {
          font-size: $font-size-large;
          font-weight: 600;
        }
      }
    }
  }

  .dimensions-section,
  .suggestions-section {
    margin-bottom: $spacing-xl;

    h3 {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      font-size: $font-size-large;
      margin-bottom: $spacing-md;
    }
  }

  .dimensions-list {
    .dimension-item {
      margin-bottom: $spacing-md;

      .dimension-info {
        display: flex;
        justify-content: space-between;
        margin-bottom: $spacing-xs;

        .dimension-name {
          font-weight: 500;
        }

        .dimension-score {
          color: $text-secondary;
        }
      }
    }
  }

  .suggestions-list {
    .suggestion-item {
      display: flex;
      gap: $spacing-md;
      padding: $spacing-md;
      background: $bg-white;
      border: 1px solid $border-light;
      border-radius: $border-radius-md;
      margin-bottom: $spacing-sm;

      .suggestion-number {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: $primary-color;
        color: white;
        border-radius: 50%;
        font-weight: 600;
      }

      .suggestion-text {
        flex: 1;
        line-height: 1.8;
      }
    }
  }

  .action-buttons {
    display: flex;
    justify-content: center;
    gap: $spacing-md;
    flex-wrap: wrap;
  }
}

.recommendations-card {
  .recommendations-list {
    .recommendation-item {
      display: flex;
      align-items: center;
      gap: $spacing-md;
      padding: $spacing-md;
      border: 1px solid $border-lighter;
      border-radius: $border-radius-md;
      cursor: pointer;
      transition: $transition-base;

      &:hover {
        border-color: $primary-color;
        background: rgba($primary-color, 0.05);
      }

      .recommendation-cover {
        width: 80px;
        height: 60px;
        object-fit: cover;
        border-radius: $border-radius-sm;
      }

      .recommendation-info {
        flex: 1;

        h4 {
          margin: 0 0 $spacing-xs;
        }

        p {
          margin: 0;
          font-size: $font-size-small;
          color: $text-secondary;
        }
      }
    }
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .score-section {
    flex-direction: column !important;
  }

  .action-buttons {
    flex-direction: column !important;

    .el-button {
      width: 100%;
    }
  }
}
</style>
