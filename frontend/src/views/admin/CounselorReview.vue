<template>
  <div class="counselor-review">
    <div class="page-header">
      <h2>咨询师审核</h2>
      <el-input
        v-model="searchKeyword"
        placeholder="搜索咨询师姓名或手机号"
        style="width: 300px"
        :prefix-icon="Search"
        clearable
        @input="handleSearch"
      />
    </div>

    <el-card>
      <el-tabs v-model="activeTab" @tab-change="loadCounselors">
        <el-tab-pane label="待审核" name="pending">
          <span class="badge">({{ counts.pending || 0 }})</span>
        </el-tab-pane>
        <el-tab-pane label="已通过" name="approved" />
        <el-tab-pane label="已拒绝" name="rejected" />
      </el-tabs>

      <el-table v-loading="loading" :data="counselors" stripe>
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="specialties" label="专长领域" width="200">
          <template #default="{ row }">
            <el-tag v-for="tag in row.specialties" :key="tag" size="small" style="margin-right: 5px">
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="experience" label="从业年限" width="100">
          <template #default="{ row }">
            {{ row.experience }}年
          </template>
        </el-table-column>
        <el-table-column prop="qualification" label="资质证书" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewQualification(row)">查看证书</el-button>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="申请时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="{ row }">
            <template v-if="activeTab === 'pending'">
              <el-button type="primary" link @click="handleApprove(row)">通过</el-button>
              <el-button type="danger" link @click="handleReject(row)">拒绝</el-button>
              <el-button link @click="viewDetail(row)">详情</el-button>
            </template>
            <template v-else>
              <el-button link @click="viewDetail(row)">查看</el-button>
            </template>
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
          @size-change="loadCounselors"
          @current-change="loadCounselors"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="申请详情" width="600px">
      <div v-if="currentCounselor" class="detail-content">
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">{{ currentCounselor.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ currentCounselor.gender }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ currentCounselor.phone }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ currentCounselor.email }}</el-descriptions-item>
            <el-descriptions-item label="出生日期">{{ currentCounselor.birthDate }}</el-descriptions-item>
            <el-descriptions-item label="从业年限">{{ currentCounselor.experience }}年</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h4>专业信息</h4>
          <p><strong>专长领域:</strong> {{ currentCounselor.specialties?.join(', ') }}</p>
          <p><strong>教育背景:</strong> {{ currentCounselor.education }}</p>
          <p><strong>工作经历:</strong> {{ currentCounselor.workHistory }}</p>
        </div>

        <div class="detail-section">
          <h4>资质证书</h4>
          <el-image
            v-if="currentCounselor.qualificationFile"
            :src="currentCounselor.qualificationFile"
            fit="contain"
            style="width: 100%; max-height: 300px"
            :preview-src-list="[currentCounselor.qualificationFile]"
          />
        </div>

        <div class="detail-section">
          <h4>个人简介</h4>
          <p>{{ currentCounselor.bio }}</p>
        </div>
      </div>
    </el-dialog>

    <!-- 拒绝对话框 -->
    <el-dialog v-model="rejectVisible" title="拒绝申请" width="500px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="4"
        placeholder="请输入拒绝理由..."
      />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getPendingCounselors, reviewCounselor } from '@/api/admin'

const loading = ref(false)
const activeTab = ref('pending')
const searchKeyword = ref('')
const counselors = ref([])
const counts = ref({})
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const detailVisible = ref(false)
const rejectVisible = ref(false)
const currentCounselor = ref(null)
const rejectReason = ref('')

const loadCounselors = async () => {
  try {
    loading.value = true
    const res = await getPendingCounselors({
      status: activeTab.value,
      keyword: searchKeyword.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    counselors.value = res.data.list || []
    counts.value = res.data.counts || {}
    total.value = res.data.total || 0
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadCounselors()
}

const viewDetail = (row) => {
  currentCounselor.value = row
  detailVisible.value = true
}

const viewQualification = (row) => {
  currentCounselor.value = row
  detailVisible.value = true
}

const handleApprove = async (row) => {
  try {
    await ElMessageBox.confirm(`确定通过 ${row.name} 的申请吗？`, '确认', { type: 'success' })
    await reviewCounselor(row.id, { action: 'approve' })
    ElMessage.success('已通过')
    loadCounselors()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

const handleReject = (row) => {
  currentCounselor.value = row
  rejectReason.value = ''
  rejectVisible.value = true
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请输入拒绝理由')
    return
  }
  try {
    await reviewCounselor(currentCounselor.value.id, {
      action: 'reject',
      reason: rejectReason.value
    })
    ElMessage.success('已拒绝')
    rejectVisible.value = false
    loadCounselors()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => loadCounselors())
</script>

<style scoped>
@import '@/styles/variables.scss';
.counselor-review { padding: $spacing-lg; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: $spacing-lg; }
.page-header h2 { margin: 0; }
.badge { margin-left: $spacing-sm; font-size: 12px; }
.pagination { display: flex; justify-content: center; margin-top: $spacing-lg; }

.detail-content { display: flex; flex-direction: column; gap: $spacing-xl; }
.detail-section h4 { margin: 0 0 $spacing-md; }
.detail-section p { line-height: 1.8; }
</style>
