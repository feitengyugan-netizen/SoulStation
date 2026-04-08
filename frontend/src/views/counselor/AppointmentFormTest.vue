<template>
  <div class="test-appointment">
    <h1>预约表单测试页面</h1>
    <p>Counselor ID: {{ counselorId }}</p>
    <p>当前时间: {{ new Date().toLocaleString() }}</p>
    <el-button type="primary" @click="testClick">测试按钮</el-button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const counselorId = ref(route.query.counselorId || '无')

const testClick = () => {
  ElMessage.success('测试按钮工作正常！')
  console.log('Counselor ID:', counselorId.value)
}

onMounted(() => {
  console.log('AppointmentFormTest mounted')
  console.log('Route query:', route.query)
  ElMessage.info('测试页面已加载')
})
</script>

<style scoped>
.test-appointment {
  padding: 40px;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #303133;
  font-size: 32px;
  margin-bottom: 20px;
}

p {
  color: #606266;
  font-size: 16px;
  margin: 10px 0;
}
</style>