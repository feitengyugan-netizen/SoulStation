<template>
  <div class="test-trend">
    <PageHeader />

    <div class="container">
      <!-- 顶部操作栏 -->
      <div class="trend-header">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2>我的历史测试</h2>
        <el-button :icon="Download" @click="exportData">导出数据</el-button>
      </div>

      <!-- 筛选栏 -->
      <el-card class="filter-card">
        <div class="filter-row">
          <!-- 测试选择 -->
          <div class="filter-item">
            <span class="label">测试：</span>
            <el-select
              v-model="filters.testId"
              placeholder="选择测试"
              @change="handleFilterChange"
              style="width: 200px"
            >
              <el-option
                v-for="test in testOptions"
                :key="test.value"
                :label="test.label"
                :value="test.value"
              />
            </el-select>
          </div>

          <!-- 时间范围 -->
          <div class="filter-item">
            <span class="label">时间：</span>
            <el-select
              v-model="filters.timeRange"
              placeholder="选择时间范围"
              @change="handleFilterChange"
              style="width: 150px"
            >
              <el-option label="最近1个月" value="1month" />
              <el-option label="最近3个月" value="3months" />
              <el-option label="最近6个月" value="6months" />
              <el-option label="最近1年" value="1year" />
              <el-option label="全部" value="all" />
            </el-select>
          </div>
        </div>
      </el-card>

      <!-- 趋势图 -->
      <el-card v-loading="loading" class="chart-card">
        <template #header>
          <span>分数变化趋势</span>
        </template>

        <el-empty v-if="!loading && trendData.length === 0" description="暂无数据" />

        <div v-else class="chart-container" ref="chartRef"></div>
      </el-card>

      <!-- 历史记录 -->
      <el-card class="history-card">
        <template #header>
          <span>历史记录</span>
        </template>

        <el-table :data="historyRecords" style="width: 100%">
          <el-table-column prop="date" label="测试日期" width="180" />
          <el-table-column prop="testName" label="测试名称" />
          <el-table-column prop="score" label="得分" width="120">
            <template #default="{ row }">
              <el-tag :type="getScoreType(row.score, row.maxScore)">
                {{ row.score }}/{{ row.maxScore }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="等级" width="120">
            <template #default="{ row }">
              <el-tag :type="getLevelType(row.level)">
                {{ row.level }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button
                type="primary"
                text
                :icon="View"
                @click="viewResult(row.id)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Download, View } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import PageHeader from '@/components/PageHeader.vue'
import { getTestHistory, getTestTrend } from '@/api/test'
import { formatDate } from '@/utils/format'

const router = useRouter()

// 图表引用
const chartRef = ref(null)
let chartInstance = null

// 加载状态
const loading = ref(false)

// 测试选项
const testOptions = ref([
  { label: '全部测试', value: '' }
])

// 筛选条件
const filters = reactive({
  testId: '',
  timeRange: '6months'
})

// 趋势数据
const trendData = ref([])

// 历史记录
const historyRecords = ref([])

// 获取分数类型
const getScoreType = (score, maxScore) => {
  const percentage = (score / maxScore) * 100
  if (percentage >= 75) return 'success'
  if (percentage >= 50) return 'warning'
  return 'danger'
}

// 获取等级类型
const getLevelType = (level) => {
  const typeMap = {
    '无': 'info',
    '轻度': 'warning',
    '中度': 'warning',
    '重度': 'danger'
  }
  return typeMap[level] || 'info'
}

// 加载历史记录
const loadHistory = async () => {
  try {
    loading.value = true
    const params = {
      testId: filters.testId || undefined,
      timeRange: filters.timeRange
    }
    const res = await getTestHistory(params)
    historyRecords.value = res.data.list || []

    // 填充测试选项
    if (testOptions.value.length === 1) {
      const tests = res.data.tests || []
      testOptions.value.push(
        ...tests.map(test => ({
          label: test.name,
          value: test.id
        }))
      )
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 加载趋势数据
const loadTrend = async () => {
  if (!filters.testId) {
    trendData.value = []
    return
  }

  try {
    loading.value = true
    const res = await getTestTrend(filters.testId)
    trendData.value = res.data || []

    // 更新图表
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('加载趋势失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value) return

  // 销毁旧图表
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新图表
  chartInstance = echarts.init(chartRef.value)

  // 准备数据
  const dates = trendData.value.map(item => item.date)
  const scores = trendData.value.map(item => item.score)

  // 图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const param = params[0]
        return `${param.name}<br/>得分: ${param.value}`
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
      name: '分数'
    },
    series: [
      {
        name: '得分',
        type: 'line',
        smooth: true,
        data: scores,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        lineStyle: {
          width: 3,
          color: '#409EFF'
        },
        itemStyle: {
          color: '#409EFF',
          borderWidth: 2,
          borderColor: '#fff'
        },
        emphasis: {
          itemStyle: {
            color: '#409EFF',
            borderWidth: 4,
            borderColor: '#fff'
          }
        }
      }
    ]
  }

  chartInstance.setOption(option)

  // 响应式
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

// 筛选变化
const handleFilterChange = () => {
  loadHistory()
  if (filters.testId) {
    loadTrend()
  }
}

// 查看结果
const viewResult = (resultId) => {
  router.push(`/test/${resultId}/result`)
}

// 导出数据
const exportData = () => {
  ElMessage.info('导出功能开发中...')
}

// 返回
const goBack = () => {
  router.push('/test')
}

// 组件挂载
onMounted(() => {
  loadHistory()
})

// 组件卸载
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.test-trend {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.trend-header {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;

  h2 {
    flex: 1;
    margin: 0;
  }
}

.filter-card {
  margin-bottom: $spacing-lg;
}

.filter-row {
  display: flex;
  gap: $spacing-xl;
  flex-wrap: wrap;

  .filter-item {
    display: flex;
    align-items: center;
    gap: $spacing-sm;

    .label {
      font-weight: 500;
      color: $text-primary;
    }
  }
}

.chart-card {
  margin-bottom: $spacing-lg;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.history-card {
  // 样式
}

// 响应式
@media (max-width: $breakpoint-md) {
  .filter-row {
    flex-direction: column;
    gap: $spacing-md;

    .filter-item {
      width: 100%;

      .el-select {
        width: 100% !important;
      }
    }
  }

  .chart-container {
    height: 300px;
  }
}
</style>
