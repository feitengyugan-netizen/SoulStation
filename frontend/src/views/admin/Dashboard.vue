<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card blue">
        <div class="stat-content">
          <p class="stat-value">{{ stats.users }}</p>
          <p class="stat-label">用户总数</p>
        </div>
        <el-icon :size="48" color="#fff"><User /></el-icon>
      </div>

      <div class="stat-card red">
        <div class="stat-content">
          <p class="stat-value">{{ stats.counselors }}</p>
          <p class="stat-label">咨询师总数</p>
        </div>
        <el-icon :size="48" color="#fff"><UserFilled /></el-icon>
      </div>

      <div class="stat-card cyan">
        <div class="stat-content">
          <p class="stat-value">{{ stats.orders }}</p>
          <p class="stat-label">订单总数</p>
        </div>
        <el-icon :size="48" color="#fff"><List /></el-icon>
      </div>

      <div class="stat-card orange">
        <div class="stat-content">
          <p class="stat-value">{{ stats.tests }}</p>
          <p class="stat-label">测试完成数</p>
        </div>
        <el-icon :size="48" color="#fff"><Notebook /></el-icon>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <h3>订单统计</h3>
        </div>
        <div ref="orderChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>热门心理测试</h3>
        </div>
        <div ref="testChartRef" class="chart-container"></div>
      </div>
    </div>

    <!-- 公告列表 -->
    <div class="announcement-card">
      <div class="card-header">
        <h3>公告列表</h3>
        <el-button type="primary" size="small" @click="handleAddAnnouncement">发布公告</el-button>
      </div>
      <div class="announcement-list">
        <el-empty v-if="announcements.length === 0" description="暂无公告" />
        <div v-for="item in announcements" :key="item.id" class="announcement-item">
          <div class="announcement-content">
            <h4>{{ item.title }}</h4>
            <p>{{ item.content }}</p>
            <span class="announcement-date">{{ item.date }}</span>
          </div>
          <div class="announcement-actions">
            <el-button type="primary" text size="small" @click="handleEditAnnouncement(item)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDeleteAnnouncement(item)">删除</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, UserFilled, List, Notebook } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 统计数据
const stats = ref({
  users: 0,
  counselors: 0,
  orders: 0,
  tests: 0
})

// 公告列表
const announcements = ref([
  {
    id: 1,
    title: '系统维护通知',
    content: '系统将于本周六晚上22:00进行维护，预计维护时间为2小时。',
    date: '2026-04-01 10:00:00'
  },
  {
    id: 2,
    title: '新功能上线通知',
    content: 'AI智能问答功能已上线，欢迎用户体验。',
    date: '2026-03-28 15:30:00'
  }
])

const orderChartRef = ref(null)
const testChartRef = ref(null)

let orderChart = null
let testChart = null

// 初始化订单统计图表
const initOrderChart = () => {
  if (!orderChartRef.value) return

  orderChart = echarts.init(orderChartRef.value)

  // 生成最近7天的日期
  const dates = []
  const today = new Date()
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    dates.push(`${date.getMonth() + 1}-${date.getDate()}`)
  }

  orderChart.setOption({
    tooltip: {
      trigger: 'axis'
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
      type: 'value'
    },
    series: [
      {
        name: '订单数',
        type: 'line',
        smooth: true,
        data: [12, 18, 15, 23, 20, 28, 25],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
            { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
          ])
        },
        lineStyle: {
          color: '#3b82f6',
          width: 2
        },
        itemStyle: {
          color: '#3b82f6'
        }
      }
    ]
  })
}

// 初始化测试统计图表
const initTestChart = () => {
  if (!testChartRef.value) return

  testChart = echarts.init(testChartRef.value)

  testChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '测试类型',
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
        data: [
          { value: 234, name: '焦虑自评量表', itemStyle: { color: '#3b82f6' } },
          { value: 187, name: '抑郁自评量表', itemStyle: { color: '#ef4444' } },
          { value: 156, name: '大五人格量表', itemStyle: { color: '#06b6d4' } },
          { value: 123, name: '工作压力量表', itemStyle: { color: '#f59e0b' } },
          { value: 89, name: '其他测试', itemStyle: { color: '#8b5cf6' } }
        ]
      }
    ]
  })
}

// 加载统计数据
const loadStats = async () => {
  // 这里应该调用实际的API
  // 模拟数据
  stats.value = {
    users: 1234,
    counselors: 56,
    orders: 856,
    tests: 2345
  }
}

// 公告操作
const handleAddAnnouncement = () => {
  ElMessage.info('发布公告功能开发中...')
}

const handleEditAnnouncement = (item) => {
  ElMessage.info('编辑公告功能开发中...')
}

const handleDeleteAnnouncement = (item) => {
  ElMessage.info('删除公告功能开发中...')
}

onMounted(() => {
  loadStats()
  initOrderChart()
  initTestChart()

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    orderChart?.resize()
    testChart?.resize()
  })
})

onUnmounted(() => {
  orderChart?.dispose()
  testChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  border-radius: 12px;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-card.blue {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.stat-card.red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.stat-card.cyan {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.stat-card.orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  margin: 0;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
}

/* 图表区域 */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.chart-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.chart-container {
  height: 300px;
}

/* 公告列表 */
.announcement-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.announcement-item {
  display: flex;
  justify-content: space-between;
  align-items: start;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.announcement-item:hover {
  background: #f3f4f6;
}

.announcement-content {
  flex: 1;
}

.announcement-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.announcement-content p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #6b7280;
}

.announcement-date {
  font-size: 12px;
  color: #9ca3af;
}

.announcement-actions {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
