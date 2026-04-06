<template>
  <div class="data-statistics">
    <PageHeader />

    <div class="container">
      <!-- 顶部导航 -->
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>我的数据统计</h2>
        <el-select
          v-model="timeRange"
          @change="handleTimeRangeChange"
          style="width: 130px"
        >
          <el-option label="最近7天" value="7days" />
          <el-option label="最近30天" value="30days" />
          <el-option label="最近90天" value="90days" />
        </el-select>
      </div>

      <!-- 总览数据 -->
      <div class="overview-grid">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f4a57a 0%, #e8845a 100%)">
              <el-icon :size="32"><DocumentCopy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.testCount || 0 }}</div>
              <div class="stat-label">心理测试</div>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #e8c4d8 0%, #9b8bb4 100%)">
              <el-icon :size="32"><ChatDotSquare /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.chatCount || 0 }}</div>
              <div class="stat-label">对话</div>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #a8e6cf 0%, #56ab91 100%)">
              <el-icon :size="32"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.appointmentCount || 0 }}</div>
              <div class="stat-label">预约</div>
            </div>
          </div>
        </el-card>

        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fde8d8 0%, #f4a57a 100%)">
              <el-icon :size="32"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ overviewData.favoriteCount || 0 }}</div>
              <div class="stat-label">收藏</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 活动趋势 -->
      <el-card v-loading="loading" class="chart-card">
        <template #header>
          <span>活动趋势</span>
        </template>

        <div class="chart-container" ref="activityChartRef"></div>
      </el-card>

      <div class="charts-row">
        <!-- 测试分类分布 -->
        <el-card v-loading="loading" class="chart-card">
          <template #header>
            <span>测试分类分布</span>
          </template>

          <div class="chart-container small" ref="testChartRef"></div>
        </el-card>

        <!-- 对话主题分布 -->
        <el-card v-loading="loading" class="chart-card">
          <template #header>
            <span>对话主题分布</span>
          </template>

          <div class="chart-container small" ref="chatChartRef"></div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, DocumentCopy, ChatDotSquare, Calendar, Star } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import PageHeader from '@/components/PageHeader.vue'
import {
  getUserStatistics,
  getActivityTrend,
  getTestDistribution,
  getChatDistribution
} from '@/api/user'

const router = useRouter()

// 图表引用
const activityChartRef = ref(null)
const testChartRef = ref(null)
const chatChartRef = ref(null)

let activityChart = null
let testChart = null
let chatChart = null

// 时间范围
const timeRange = ref('30days')

// 加载状态
const loading = ref(false)

// 总览数据
const overviewData = ref({
  testCount: 0,
  chatCount: 0,
  appointmentCount: 0,
  favoriteCount: 0
})

// 加载统计数据
const loadStatistics = async () => {
  try {
    loading.value = true
    const res = await getUserStatistics({ timeRange: timeRange.value })
    overviewData.value = res.data || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载活动趋势
const loadActivityTrend = async () => {
  try {
    const res = await getActivityTrend({ timeRange: timeRange.value })
    const data = res.data || []

    await nextTick()
    renderActivityChart(data)
  } catch (error) {
    console.error('加载活动趋势失败:', error)
  }
}

// 加载测试分类分布
const loadTestDistribution = async () => {
  try {
    const res = await getTestDistribution()
    const data = res.data || []

    await nextTick()
    renderTestChart(data)
  } catch (error) {
    console.error('加载测试分布失败:', error)
  }
}

// 加载对话主题分布
const loadChatDistribution = async () => {
  try {
    const res = await getChatDistribution()
    const data = res.data || []

    await nextTick()
    renderChatChart(data)
  } catch (error) {
    console.error('加载对话分布失败:', error)
  }
}

// 渲染活动趋势图
const renderActivityChart = (data) => {
  if (!activityChartRef.value) return

  if (activityChart) {
    activityChart.dispose()
  }

  activityChart = echarts.init(activityChartRef.value)

  const dates = data.map(item => item.date)
  const activities = data.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>活动次数: ${param.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '次数'
    },
    series: [
      {
        name: '活动次数',
        type: 'line',
        smooth: true,
        data: activities,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(232, 132, 90, 0.3)' },
            { offset: 1, color: 'rgba(232, 132, 90, 0.03)' }
          ])
        },
        lineStyle: {
          width: 3,
          color: '#e8845a',
          borderWidth: 2,
          borderColor: '#fff'
        }
      }
    ]
  }

  activityChart.setOption(option)
}

// 渲染测试分类饼图
const renderTestChart = (data) => {
  if (!testChartRef.value) return

  if (testChart) {
    testChart.dispose()
  }

  testChart = echarts.init(testChartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center'
    },
    series: [
      {
        name: '测试分类',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  }

  testChart.setOption(option)
}

// 渲染对话主题柱状图
const renderChatChart = (data) => {
  if (!chatChartRef.value) return

  if (chatChart) {
    chatChart.dispose()
  }

  chatChart = echarts.init(chatChartRef.value)

  const categories = data.map(item => item.name)
  const counts = data.map(item => item.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '对话数'
    },
    series: [
      {
        name: '对话数',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 1, color: '#188df0' }
          ]),
          borderRadius: [5, 5, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }
    ]
  }

  chatChart.setOption(option)
}

// 时间范围变化
const handleTimeRangeChange = () => {
  loadStatistics()
  loadActivityTrend()
}

// 返回
const goBack = () => {
  router.push('/profile')
}

// 响应式图表
const handleResize = () => {
  activityChart?.resize()
  testChart?.resize()
  chatChart?.resize()
}

// 组件挂载
onMounted(async () => {
  await loadStatistics()
  await loadActivityTrend()
  await loadTestDistribution()
  await loadChatDistribution()

  window.addEventListener('resize', handleResize)
})

// 组件卸载
onBeforeUnmount(() => {
  activityChart?.dispose()
  testChart?.dispose()
  chatChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.data-statistics-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 24px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;

  h2 { margin: 0; font-size: 24px; font-weight: 700; color: $text-primary; }
}

// ── 汇总卡片行 ──────────────────────────────────────
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 28px;
}

.stat-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;
  text-align: center;

  :deep(.el-card__body) { padding: 28px 20px; }

  .stat-value {
    font-size: 36px;
    font-weight: 800;
    color: $primary-color;
    display: block;
    margin-bottom: 6px;
  }

  .stat-label { font-size: 13px; color: $text-secondary; }
}

// ── 图表卡片 ──────────────────────────────────────────
.chart-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 20px rgba(107,82,68,0.08) !important;
  margin-bottom: 24px;

  :deep(.el-card__header) {
    font-weight: 600;
    color: $text-primary;
    border-bottom: 1px solid $border-lighter;
  }
}

.chart-container { width: 100%; height: 350px; }

// ── 数据表 ──────────────────────────────────────────
.data-table-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;

  :deep(.el-card__header) {
    font-weight: 600;
    color: $text-primary;
    border-bottom: 1px solid $border-lighter;
  }

  :deep(.el-table th) {
    background: $bg-page;
    color: $text-regular;
    font-weight: 600;
  }

  :deep(.el-table tr:hover td) {
    background: rgba(232,132,90,0.04) !important;
  }
}
</style>
