<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card blue">
        <div class="stat-content">
          <p class="stat-value">{{ stats.users }}</p>
          <p class="stat-label">用户总数</p>
          <p class="stat-sub">今日新增 {{ stats.todayUsers }}</p>
        </div>
        <el-icon :size="48" color="#fff"><User /></el-icon>
      </div>

      <div class="stat-card red">
        <div class="stat-content">
          <p class="stat-value">{{ stats.counselors }}</p>
          <p class="stat-label">咨询师总数</p>
          <p class="stat-sub">待审核 {{ stats.pending }}</p>
        </div>
        <el-icon :size="48" color="#fff"><UserFilled /></el-icon>
      </div>

      <div class="stat-card cyan">
        <div class="stat-content">
          <p class="stat-value">{{ stats.orders }}</p>
          <p class="stat-label">订单总数</p>
          <p class="stat-sub">今日新增 {{ stats.todayOrders }}</p>
        </div>
        <el-icon :size="48" color="#fff"><List /></el-icon>
      </div>

      <div class="stat-card orange">
        <div class="stat-content">
          <p class="stat-value">{{ stats.tests }}</p>
          <p class="stat-label">测试完成数</p>
          <p class="stat-sub">收入 ¥{{ stats.revenue }}</p>
        </div>
        <el-icon :size="48" color="#fff"><Notebook /></el-icon>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <h3>订单趋势（近30天）</h3>
        </div>
        <div ref="orderChartRef" class="chart-container"></div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>用户增长（近30天）</h3>
        </div>
        <div ref="userChartRef" class="chart-container"></div>
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
import { getDashboardStats, getChartData } from '@/api/admin'

const stats = ref({
  users: 0,
  counselors: 0,
  orders: 0,
  tests: 0,
  revenue: 0,
  pending: 0,
  todayUsers: 0,
  todayOrders: 0
})

const announcements = ref([])

const orderChartRef = ref(null)
const userChartRef = ref(null)

let orderChart = null
let userChart = null

const chartColors = {
  line: '#3b82f6',
  areaStart: 'rgba(59, 130, 246, 0.3)',
  areaEnd: 'rgba(59, 130, 246, 0.05)'
}

// 初始化订单趋势图表
const initOrderChart = (dates = [], values = []) => {
  if (!orderChartRef.value) return
  if (!orderChart) orderChart = echarts.init(orderChartRef.value)

  orderChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      name: '订单数',
      type: 'line',
      smooth: true,
      data: values,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: chartColors.areaStart },
          { offset: 1, color: chartColors.areaEnd }
        ])
      },
      lineStyle: { color: chartColors.line, width: 2 },
      itemStyle: { color: chartColors.line }
    }]
  })
}

// 初始化用户增长图表
const initUserChart = (dates = [], values = []) => {
  if (!userChartRef.value) return
  if (!userChart) userChart = echarts.init(userChartRef.value)

  userChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{
      name: '新增用户',
      type: 'bar',
      data: values,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#06b6d4' },
          { offset: 1, color: '#0891b2' }
        ]),
        borderRadius: [6, 6, 0, 0]
      }
    }]
  })
}

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await getDashboardStats()
    const d = res.data || {}
    stats.value = {
      users: d.user_count || 0,
      counselors: d.counselor_count || 0,
      orders: d.order_count || 0,
      tests: d.test_count || 0,
      revenue: d.total_revenue || 0,
      pending: d.pending_counselor_count || 0,
      todayUsers: d.today_user_count || 0,
      todayOrders: d.today_order_count || 0
    }
  } catch (e) {
    console.error('加载统计数据失败:', e)
  }
}

// 加载图表数据
const loadCharts = async () => {
  try {
    const [orderRes, userRes] = await Promise.all([
      getChartData('order'),
      getChartData('user')
    ])
    const orderData = orderRes.data?.data || []
    const userData = userRes.data?.data || []

    initOrderChart(
      orderData.map(d => d.date),
      orderData.map(d => d.value)
    )
    initUserChart(
      userData.map(d => d.date),
      userData.map(d => d.value)
    )
  } catch (e) {
    console.error('加载图表数据失败:', e)
  }
}

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
  loadCharts()

  window.addEventListener('resize', () => {
    orderChart?.resize()
    userChart?.resize()
  })
})

onUnmounted(() => {
  orderChart?.dispose()
  userChart?.dispose()
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

.stat-sub {
  font-size: 12px;
  opacity: 0.7;
  margin: 2px 0 0;
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
