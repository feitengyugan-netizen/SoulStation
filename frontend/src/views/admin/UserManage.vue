<template>
  <div class="user-manage">
    <div class="page-header">
      <h2>用户管理</h2>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索用户名、手机号或邮箱"
        style="width: 300px"
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
    </div>

    <el-card>
      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="50" :src="row.avatar" />
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'counselor' ? 'success' : 'primary'">
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.banned ? 'danger' : 'success'">
              {{ row.banned ? '已封禁' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数据统计" width="200">
          <template #default="{ row }">
            <div class="stats">
              <span>测试: {{ row.testCount }}</span>
              <span>对话: {{ row.chatCount }}</span>
              <span>预约: {{ row.appointmentCount }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="lastLoginTime" label="最后登录" width="180" />
        <el-table-column prop="createdAt" label="注册时间" width="180" />
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
            <el-button
              :type="row.banned ? 'success' : 'danger'"
              link
              @click="toggleBan(row)"
            >
              {{ row.banned ? '解封' : '封禁' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadUsers"
          @current-change="loadUsers"
        />
      </div>
    </el-card>

    <!-- 用户详情对话框 -->
    <el-dialog v-model="detailVisible" title="用户详情" width="600px">
      <div v-if="currentUser" class="detail-content">
        <div class="detail-header">
          <el-avatar :size="80" :src="currentUser.avatar" />
          <div class="header-info">
            <h3>{{ currentUser.nickname || currentUser.username }}</h3>
            <p>{{ currentUser.email }}</p>
            <p>{{ currentUser.phone }}</p>
          </div>
        </div>

        <el-divider />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="用户ID">{{ currentUser.id }}</el-descriptions-item>
          <el-descriptions-item label="用户名">{{ currentUser.username }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ currentUser.gender || '未知' }}</el-descriptions-item>
          <el-descriptions-item label="生日">{{ currentUser.birthDate || '未设置' }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="currentUser.role === 'admin' ? 'danger' : currentUser.role === 'counselor' ? 'success' : 'primary'">
              {{ getRoleText(currentUser.role) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentUser.banned ? 'danger' : 'success'">
              {{ currentUser.banned ? '已封禁' : '正常' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="个人简介" :span="2">
            {{ currentUser.bio || '暂无简介' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.testCount }}</span>
            <span class="stat-label">完成测试</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.chatCount }}</span>
            <span class="stat-label">对话次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.appointmentCount }}</span>
            <span class="stat-label">预约次数</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ currentUser.favoriteCount }}</span>
            <span class="stat-label">收藏文章</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getAdminUsers, banUser } from '@/api/admin'

const loading = ref(false)
const searchKeyword = ref('')
const users = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const detailVisible = ref(false)
const currentUser = ref(null)

const loadUsers = async () => {
  try {
    loading.value = true
    const res = await getAdminUsers({
      keyword: searchKeyword.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    users.value = res.data.list || []
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

const getRoleText = (role) => {
  const map = { admin: '管理员', counselor: '咨询师', user: '用户' }
  return map[role] || role
}

const viewDetail = (row) => {
  currentUser.value = row
  detailVisible.value = true
}

const toggleBan = async (row) => {
  const action = row.banned ? '解封' : '封禁'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${row.nickname || row.username} 吗？`, '提示', { type: 'warning' })
    await banUser(row.id, { banned: !row.banned })
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

onMounted(() => loadUsers())
</script>

<style scoped>
@import '@/styles/variables.scss';
.user-manage { padding: $spacing-lg; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-lg; }
.page-header h2 { margin: 0; }
.stats { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: $text-secondary; }
.pagination { display: flex; justify-content: center; margin-top: $spacing-lg; }

.detail-content { display: flex; flex-direction: column; gap: $spacing-lg; }
.detail-header { display: flex; gap: $spacing-lg; }
.header-info h3 { margin: 0 0 $spacing-xs; }
.header-info p { margin: $spacing-xs 0; color: $text-secondary; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: $spacing-lg; text-align: center; }
.stat-item { padding: $spacing-lg; background: #f5f7fa; border-radius: $border-radius; }
.stat-value { display: block; font-size: 24px; font-weight: 600; color: $primary-color; }
.stat-label { font-size: 12px; color: $text-secondary; }
</style>
