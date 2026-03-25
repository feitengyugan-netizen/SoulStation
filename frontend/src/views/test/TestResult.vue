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

          <!-- 结果展示 -->
          <div class="score-section">
            <!-- 结果等级 -->
            <div class="result-level-large" :class="resultData.levelClass">
              <el-icon :size="64">
                <component :is="resultData.levelIcon" />
              </el-icon>
              <div class="level-content">
                <div class="level-label">测试结果</div>
                <div class="level-name">{{ resultData.level }}</div>
                <div class="level-description">{{ resultData.levelDescription }}</div>
              </div>
            </div>
          </div>

          <!-- AI建议卡片 -->
          <div v-if="resultData.aiSuggestion" class="ai-suggestion-card">
            <el-card>
              <template #header>
                <div class="card-header">
                  <div class="header-left">
                    <el-icon :size="20" color="#67C23A"><ChatDotRound /></el-icon>
                    <span class="card-title">AI智能建议</span>
                    <el-tag type="success" size="small">由AI生成</el-tag>
                  </div>
                </div>
              </template>

              <div class="ai-suggestion-content">
                <p>{{ resultData.aiSuggestion }}</p>
              </div>

              <template #footer>
                <div class="card-footer">
                  <el-button
                    type="primary"
                    :icon="ChatLineRound"
                    @click="startAIChat"
                  >
                    与AI咨询师深入交流
                  </el-button>
                  <el-alert
                    type="info"
                    :closable="false"
                    show-icon
                  >
                    AI建议仅供参考，不能替代专业心理咨询或医疗诊断
                  </el-alert>
                </div>
              </template>
            </el-card>
          </div>

          <!-- 结果描述 -->
          <div v-if="resultData.description" class="description-section">
            <h3>
              <el-icon><InfoFilled /></el-icon>
              结果说明
            </h3>
            <p class="description-text">{{ resultData.description }}</p>
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
  InfoFilled,
  ChatDotRound,
  ChatLineRound
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
  levelDescription: '',  // 新增：等级描述
  description: '',
  aiSuggestion: '',  // AI建议
  dimensions: [],
  suggestions: [],
  isFavorited: false
})

// 等级描述映射
const levelDescriptions = {
  '无': '您的心理状态良好，没有明显异常。请继续保持积极的生活方式和健康习惯。',
  '轻度': '检测到一些轻微的心理困扰，这在生活中很常见。建议通过运动、休息、社交等方式自我调节，一般能够自行缓解。',
  '中度': '您的心理状态需要关注。建议尝试放松技巧、规律作息，必要时可寻求专业心理咨询师的帮助。',
  '重度': '您的心理状态需要重视。建议尽快寻求专业心理咨询师或精神科医生的帮助，进行系统的评估和诊断。'
}

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

    // 处理等级配置 - 映射后端返回的等级到前端配置
    const levelMapping = {
      'none': '无',
      'mild': '轻度',
      'moderate': '中度',
      'severe': '重度'
    }
    const levelText = levelMapping[data.result_level] || '无'
    const levelData = levelConfig[levelText] || levelConfig['无']
    const levelDesc = levelDescriptions[levelText] || ''

    // 处理建议文本 - 转换为数组
    let suggestionsArray = []
    if (data.suggestions) {
      // 按句号或换行符分割建议
      suggestionsArray = data.suggestions
        .split(/[。\\n]/)
        .filter(s => s && s.trim())
        .map(s => s.trim())
    }

    // 处理维度得分 - 转换格式
    let dimensionsArray = []
    if (data.dimension_scores && Array.isArray(data.dimension_scores)) {
      dimensionsArray = data.dimension_scores.map(dim => ({
        name: dim.dimension,
        score: dim.score,
        maxScore: 80, // 默认最大分，可以根据实际调整
        level: dim.level
      }))
    }

    resultData.value = {
      testName: data.test_title || '测试',
      score: data.total_score || 0,  // 保留但不显示
      maxScore: 100,  // 保留但不显示
      level: levelText,
      levelClass: levelData.class,
      levelIcon: levelData.icon,
      levelDescription: levelDesc,  // ✅ 新增等级描述
      description: data.result_description || '',
      aiSuggestion: data.ai_suggestion || '',
      dimensions: dimensionsArray,
      suggestions: suggestionsArray,
      isFavorited: data.is_favorite || false
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

// 开始AI深度咨询
const startAIChat = () => {
  // 跳转到AI咨询页面，携带测试结果ID
  router.push({
    path: '/consultation/chat',
    query: {
      result_id: resultId,
      type: 'test_result'
    }
  })
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
@use '@/styles/variables.scss' as *;

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
    margin-bottom: $spacing-xl;
    padding: $spacing-xl;

    .result-level-large {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $spacing-lg;
      padding: $spacing-xl;
      border-radius: $border-radius-lg;
      width: 100%;
      max-width: 500px;
      text-align: center;

      &.level-none {
        background: linear-gradient(135deg, #a8e6cf 0%, #56ab91 100%);
        color: white;
      }

      &.level-mild {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        color: #2d3436;
      }

      &.level-moderate {
        background: linear-gradient(135deg, #fab1a0 0%, #e17055 100%);
        color: white;
      }

      &.level-severe {
        background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
        color: white;
      }

      .level-content {
        display: flex;
        flex-direction: column;
        gap: $spacing-sm;

        .level-label {
          font-size: $font-size-small;
          opacity: 0.9;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .level-name {
          font-size: 32px;
          font-weight: 700;
        }

        .level-description {
          font-size: $font-size-base;
          line-height: 1.6;
          opacity: 0.95;
          max-width: 400px;
          margin: 0 auto;
        }
      }
    }
  }

  .description-section {
    margin-bottom: $spacing-xl;
    padding: $spacing-lg;
    background: rgba($primary-color, 0.05);
    border-radius: $border-radius-md;

    h3 {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      font-size: $font-size-large;
      font-weight: 600;
      color: $text-primary;
      margin-bottom: $spacing-md;
    }

    .description-text {
      font-size: $font-size-base;
      line-height: 1.6;
      color: $text-secondary;
      margin: 0;
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

  .ai-suggestion-card {
    margin-bottom: $spacing-xl;

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .header-left {
        display: flex;
        align-items: center;
        gap: $spacing-sm;

        .card-title {
          font-size: $font-size-large;
          font-weight: 600;
          color: $text-primary;
        }
      }
    }

    .ai-suggestion-content {
      padding: $spacing-md 0;
      line-height: 1.8;

      p {
        font-size: $font-size-base;
        color: $text-primary;
        margin: 0;
        white-space: pre-wrap;
      }
    }

    .card-footer {
      display: flex;
      flex-direction: column;
      gap: $spacing-md;

      .el-alert {
        font-size: $font-size-small;
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
  .action-buttons {
    flex-direction: column !important;

    .el-button {
      width: 100%;
    }
  }

  .result-level-large {
    .level-content {
      .level-name {
        font-size: 28px;
      }

      .level-description {
        font-size: $font-size-small;
      }
    }
  }
}
</style>
