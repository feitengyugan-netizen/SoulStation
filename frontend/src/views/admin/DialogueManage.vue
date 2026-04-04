<template>
  <div class="dialogue-manage">
    <div class="page-header">
      <h2>对话管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleExport">导出数据</el-button>
      </div>
    </div>

    <el-card class="search-card">
      <el-form :inline="true">
        <el-form-item label="用户ID">
          <el-input v-model="searchForm.userId" placeholder="请输入用户ID" clearable />
        </el-form-item>
        <el-form-item label="对话标签">
          <el-select v-model="searchForm.tag" placeholder="请选择标签" clearable>
            <el-option label="焦虑" value="anxiety" />
            <el-option label="抑郁" value="depression" />
            <el-option label="压力" value="stress" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table :data="dialogueList" style="width: 100%">
        <el-table-column prop="id" label="对话ID" width="100" />
        <el-table-column prop="userId" label="用户ID" width="100" />
        <el-table-column prop="messageCount" label="消息数" width="100" />
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <el-tag v-for="tag in row.tags" :key="tag" size="small" style="margin-right: 8px">
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column prop="lastMessageTime" label="最后消息时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleViewDetail(row)">查看详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const searchForm = ref({
  userId: '',
  tag: ''
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const dialogueList = ref([
  {
    id: 1,
    userId: 1001,
    messageCount: 23,
    tags: ['焦虑', '失眠'],
    createTime: '2026-04-01 10:00:00',
    lastMessageTime: '2026-04-04 15:30:00'
  },
  {
    id: 2,
    userId: 1002,
    messageCount: 15,
    tags: ['抑郁'],
    createTime: '2026-04-02 14:00:00',
    lastMessageTime: '2026-04-03 09:20:00'
  }
])

const handleSearch = () => {
  ElMessage.info('搜索功能开发中...')
}

const handleReset = () => {
  searchForm.value = {
    userId: '',
    tag: ''
  }
}

const handleExport = () => {
  ElMessage.info('导出功能开发中...')
}

const handleViewDetail = (row) => {
  ElMessage.info('查看详情功能开发中...')
}
</script>

<style scoped>
.dialogue-manage {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  flex: 1;
}
</style>
