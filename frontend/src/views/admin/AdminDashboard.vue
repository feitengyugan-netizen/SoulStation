<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h2>数据概览</h2>
      <div class="header-actions">
        <el-date-picker v-model="dateRange" type="daterange" placeholder="选择日期范围" />
        <el-button type="primary" @click="refreshData">刷新数据</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div v-for="stat in stats" :key="stat.key" class="stat-card">
        <div class="stat-icon" :style="{ background: stat.color }">
          <el-icon :size="24"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-content">
          <p class="stat-value">{{ stat.value.toLocaleString() }}</p>
          <p class="stat-label">{{ stat.label }}</p>
          <p v-if="stat.trend > 0" class="stat-trend up">
            <el-icon><ArrowUp /></el-icon>
            {{ stat.trend }} 待处理
          </p>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>用户增长趋势</span>
            <el-radio-group v-model="userChartPeriod" size="small" @change="loadUserChart">
              <el-radio-button value="week">周</el-radio-button>
              <el-radio-button value="month">月</el-radio-button>
              <el-radio-button value="year">年</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="userChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>订单统计</span>
          </div>
        </template>
        <div ref="orderChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <div class="charts-row">
      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>收入统计</span>
          </div>
        </template>
        <div ref="revenueChartRef" class="chart-container"></div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="card-header">
            <span>测试完成分布</span>
          </div>
        </template>
        <div ref="testChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <!-- 待处理事项 -->
    <el-card class="pending-card">
      <template #header>
        <div class="card-header">
          <span>待处理事项</span>
          <el-button type="primary" text @click="$router.push('/admin/counselors')">查看全部</el-button>
        </div>
      </template>
      <div class="pending-list">
        <div v-for="item in pendingItems" :key="item.id" class="pending-item">
          <el-icon class="pending-icon" :color="item.color"><component :is="item.icon" /></el-icon>
          <div class="pending-content">
            <p class="pending-title">{{ item.title }}</p>
            <p class="pending-desc">{{ item.desc }}</p>
          </div>
          <el-button type="primary" text @click="item.action">处理</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { User, ShoppingCart, Money, Document, ArrowUp, ArrowDown, Warning, UserFilled, Bell } from '@element-plus/icons-vue'
import { getDashboardStats, getChartData } from '@/api/admin'

const router = useRouter()
const loading = ref(false)
const dateRange = ref([])
const userChartPeriod = ref('week')

const stats = ref([
  { key: 'users', label: '用户总数', value: 0, trend: 0, color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: User },
  { key: 'orders', label: '预约总数', value: 0, trend: 0, color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: ShoppingCart },
  { key: 'revenue', label: '总收入(元)', value: 0, trend: 0, color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: Money },
  { key: 'articles', label: '知识文章', value: 0, trend: 0, color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: Document }
])

const pendingItems = ref([])

const userChartRef = ref(null)
const orderChartRef = ref(null)
const revenueChartRef = ref(null)
const testChartRef = ref(null)

let userChart = null
let orderChart = null
let revenueChart = null
let testChart = null

// 加载统计数据
const loadStats = async () => {
  try {
    loading.value = true
    const res = await getDashboardStats()
    const data = res.data

    stats.value = [
      { key: 'users', label: '用户总数', value: data.user_count || 0, trend: data.today_user_count || 0, color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', icon: User },
      { key: 'counselors', label: '咨询师总数', value: data.counselor_count || 0, trend: data.pending_counselor_count || 0, color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', icon: UserFilled },
      { key: 'orders', label: '预约总数', value: data.order_count || 0, trend: data.today_order_count || 0, color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', icon: ShoppingCart },
      { key: 'revenue', label: '总收入(元)', value: data.total_revenue || 0, trend: 0, color: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', icon: Money },
      { key: 'articles', label: '知识文章', value: data.article_count || 0, trend: 0, color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', icon: Document }
    ]

    // 待处理事项
    pendingItems.value = []
    if (data.pending_counselor_count > 0) {
      pendingItems.value.push({
        id: 1,
        title: '待审核咨询师',
        desc: `${data.pending_counselor_count} 位咨询师申请待审核`,
        icon: UserFilled,
        color: '#f56c6c',
        action: () => router.push('/admin/counselors')
      })
    }
    if (data.today_order_count > 0) {
      pendingItems.value.push({
        id: 2,
        title: '今日新预约',
        desc: `${data.today_order_count} 个新预约待处理`,
        icon: Bell,
        color: '#409eff',
        action: () => router.push('/admin/orders')
      })
    }
    if (pendingItems.value.length === 0) {
      pendingItems.value.push({
        id: 0,
        title: '暂无待处理事项',
        desc: '所有业务都已处理完毕',
        icon: Document,
        color: '#67c23a',
        action: () => {}
      })
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

const initUserChart = () => {
  if (!userChartRef.value) return
  userChart = echarts.init(userChartRef.value)
  userChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [{ name: '新增用户', type: 'line', smooth: true, data: [12, 23, 15, 34, 28, 45, 38], areaStyle: { color: 'rgba(102, 126, 234, 0.2)' } }]
  })
}

const initOrderChart = () => {
  if (!orderChartRef.value) return
  orderChart = echarts.init(orderChartRef.value)
  orderChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['待确认', '已确认', '进行中', '已完成', '已取消'] },
    yAxis: { type: 'value' },
    series: [{ name: '订单数', type: 'bar', data: [45, 123, 67, 234, 23], itemStyle: { color: '#667eea' } }]
  })
}

const initRevenueChart = () => {
  if (!revenueChartRef.value) return
  revenueChart = echarts.init(revenueChartRef.value)
  revenueChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
    yAxis: { type: 'value' },
    series: [{ name: '收入', type: 'line', smooth: true, data: [3200, 4500, 3800, 5200, 6100, 7500], areaStyle: { color: 'rgba(67, 233, 123, 0.2)' } }]
  })
}

const initTestChart = () => {
  if (!testChartRef.value) return
  testChart = echarts.init(testChartRef.value)
  testChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%', left: 'center' },
    series: [{
      name: '测试类型',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false, position: 'center' },
      emphasis: { label: { show: true, fontSize: 18, fontWeight: 'bold' } },
      data: [
        { value: 234, name: '焦虑测试' },
        { value: 187, name: '抑郁测试' },
        { value: 156, name: '性格测试' },
        { value: 123, name: '压力测试' },
        { value: 89, name: '其他' }
      ]
    }]
  })
}

const refreshData = async () => {
  await loadStats()
  ElMessage.success('数据已刷新')
}

const loadUserChart = async () => {
  // 根据时间周期加载图表数据
}

onMounted(() => {
  loadStats()
  initUserChart()
  initOrderChart()
  initRevenueChart()
  initTestChart()

  window.addEventListener('resize', () => {
    userChart?.resize()
    orderChart?.resize()
    revenueChart?.resize()
    testChart?.resize()
  })
})

onUnmounted(() => {
  userChart?.dispose()
  orderChart?.dispose()
  revenueChart?.dispose()
  testChart?.dispose()
})
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.admin-dashboard { padding: $spacing-lg; }
.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-xl; }
.dashboard-header h2 { margin: 0; }
.header-actions { display: flex; gap: $spacing-md; }

.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: $spacing-lg; margin-bottom: $spacing-xl; }
.stat-card { display: flex; align-items: center; gap: $spacing-lg; padding: $spacing-lg; background: white; border-radius: $border-radius; box-shadow: $shadow; }
.stat-icon { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; border-radius: 12px; color: white; }
.stat-content { flex: 1; }
.stat-value { font-size: 28px; font-weight: 600; margin: 0 0 $spacing-xs; }
.stat-label { color: $text-secondary; margin: $spacing-xs 0; }
.stat-trend { font-size: 12px; display: flex; align-items: center; gap: $spacing-xs; }
.stat-trend.up { color: $success-color; }
.stat-trend.down { color: $danger-color; }

.charts-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: $spacing-lg; margin-bottom: $spacing-xl; }
.chart-card { height: 350px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.chart-container { height: 250px; }

.pending-card { margin-bottom: $spacing-lg; }
.pending-list { display: flex; flex-direction: column; gap: $spacing-md; }
.pending-item { display: flex; align-items: center; gap: $spacing-md; padding: $spacing-md; border: 1px solid $border-color; border-radius: $border-radius; }
.pending-icon { font-size: 24px; }
.pending-content { flex: 1; }
.pending-title { font-weight: 500; margin: 0 0 $spacing-xs; }
.pending-desc { color: $text-secondary; font-size: 12px; margin: 0; }
</style>
