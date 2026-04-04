<template>
  <div class="test-manage">
    <div class="page-header">
      <h2>心理测试管理</h2>
      <el-button type="primary" @click="handleAddTest">
        <el-icon><Plus /></el-icon>
        添加测试
      </el-button>
    </div>

    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="测试名称">
          <el-input v-model="searchForm.keyword" placeholder="请输入测试名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="testList" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="测试名称" />
        <el-table-column prop="questionCount" label="题目数量" width="120" />
        <el-table-column prop="completedCount" label="完成次数" width="120" />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" text size="small" @click="handleViewQuestions(row)">题目管理</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const searchForm = ref({
  keyword: ''
})

const testList = ref([
  {
    id: 1,
    title: '焦虑自评量表 (SAS-20)',
    questionCount: 20,
    completedCount: 234,
    createTime: '2026-01-15 10:00:00'
  },
  {
    id: 2,
    title: '抑郁自评量表 (SDS-20)',
    questionCount: 20,
    completedCount: 187,
    createTime: '2026-01-15 10:00:00'
  }
])

const handleAddTest = () => {
  ElMessage.info('添加测试功能开发中...')
}

const handleSearch = () => {
  ElMessage.info('搜索功能开发中...')
}

const handleReset = () => {
  searchForm.value.keyword = ''
}

const handleEdit = (row) => {
  ElMessage.info('编辑测试功能开发中...')
}

const handleViewQuestions = (row) => {
  ElMessage.info('题目管理功能开发中...')
}

const handleDelete = (row) => {
  ElMessage.info('删除测试功能开发中...')
}
</script>

<style scoped>
.test-manage {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  flex: 1;
}
</style>
