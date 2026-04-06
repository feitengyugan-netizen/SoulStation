<template>
  <div class="profile-page">
    <PageHeader />

    <div class="container">
      <!-- 个人信息卡片 -->
      <el-card class="profile-card">
        <div class="profile-header">
          <div class="avatar-section" @click="editAvatar">
            <el-avatar :size="100" :src="userInfo?.avatar">
              <el-icon :size="50"><User /></el-icon>
            </el-avatar>
            <el-button class="edit-avatar-btn" :icon="Camera" circle />
          </div>

          <div class="user-info">
            <h2>{{ userInfo?.nickname || '未设置昵称' }}</h2>
            <p class="email">{{ userInfo?.email }}</p>
            <el-tag :type="userRoleType" size="large">
              {{ userRoleText }}
            </el-tag>
          </div>

          <el-button type="primary" :icon="Edit" @click="goToEdit">
            编辑资料
          </el-button>
        </div>

        <!-- 数据统计 -->
        <div class="stats-grid">
          <div class="stat-item" @click="navigateTo('/test')">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f4a57a 0%, #e8845a 100%)">
              <el-icon :size="28"><DocumentCopy /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ statistics.testCount || 0 }}</div>
              <div class="stat-label">心理测试</div>
            </div>
          </div>

          <div class="stat-item" @click="navigateTo('/chat')">
            <div class="stat-icon" style="background: linear-gradient(135deg, #e8c4d8 0%, #9b8bb4 100%)">
              <el-icon :size="28"><ChatDotSquare /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ statistics.chatCount || 0 }}</div>
              <div class="stat-label">智能问答</div>
            </div>
          </div>

          <div class="stat-item" @click="navigateTo('/counselor/orders')">
            <div class="stat-icon" style="background: linear-gradient(135deg, #a8e6cf 0%, #56ab91 100%)">
              <el-icon :size="28"><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ statistics.appointmentCount || 0 }}</div>
              <div class="stat-label">咨询预约</div>
            </div>
          </div>

          <div class="stat-item" @click="navigateTo('/knowledge')">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fde8d8 0%, #f4a57a 100%)">
              <el-icon :size="28"><Star /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ statistics.favoriteCount || 0 }}</div>
              <div class="stat-label">收藏内容</div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 快捷入口 -->
      <el-card class="quick-access-card">
        <template #header>
          <span>快捷入口</span>
        </template>

        <div class="quick-access-grid">
          <div class="access-item" @click="navigateTo('/test')">
            <div class="access-icon">
              <el-icon :size="32" color="#e8845a"><DocumentCopy /></el-icon>
            </div>
            <span>我的测试</span>
          </div>

          <div class="access-item" @click="navigateTo('/chat')">
            <div class="access-icon">
              <el-icon :size="32" color="#9b8bb4"><ChatDotSquare /></el-icon>
            </div>
            <span>我的对话</span>
          </div>

          <div class="access-item" @click="navigateTo('/counselor/orders')">
            <div class="access-icon">
              <el-icon :size="32" color="#56ab91"><Calendar /></el-icon>
            </div>
            <span>我的预约</span>
          </div>

          <div class="access-item" @click="navigateTo('/knowledge')">
            <div class="access-icon">
              <el-icon :size="32" color="#43e97b"><Star /></el-icon>
            </div>
            <span>我的收藏</span>
          </div>

          <div class="access-item" @click="goToEdit">
            <div class="access-icon">
              <el-icon :size="32" color="#E6A23C"><Setting /></el-icon>
            </div>
            <span>账号设置</span>
          </div>

          <div class="access-item" @click="goToPrivacy">
            <div class="access-icon">
              <el-icon :size="32" color="#F56C6C"><Lock /></el-icon>
            </div>
            <span>隐私设置</span>
          </div>

          <div class="access-item" @click="goToStatistics">
            <div class="access-icon">
              <el-icon :size="32" color="#909399"><DataAnalysis /></el-icon>
            </div>
            <span>数据统计</span>
          </div>

          <div class="access-item" @click="handleLogout">
            <div class="access-icon">
              <el-icon :size="32" color="#F56C6C"><SwitchButton /></el-icon>
            </div>
            <span>退出登录</span>
          </div>

          <div class="access-item" @click="handleDeleteAccount">
            <div class="access-icon">
              <el-icon :size="32" color="#F56C6C"><Delete /></el-icon>
            </div>
            <span>注销账户</span>
          </div>

          <div class="access-item" @click="goToCounselorApply" v-if="!isCounselor">
            <div class="access-icon">
              <el-icon :size="32" color="#67C23A"><Briefcase /></el-icon>
            </div>
            <span>加入我们</span>
          </div>

          <div class="access-item" @click="goToCounselorDashboard" v-else>
            <div class="access-icon">
              <el-icon :size="32" color="#E6A23C"><Briefcase /></el-icon>
            </div>
            <span>咨询师中心</span>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 头像上传对话框 -->
    <el-dialog
      v-model="avatarDialogVisible"
      title="更换头像"
      width="400px"
      @closed="handleDialogClosed"
    >
      <el-upload
        class="avatar-uploader"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleAvatarChange"
        accept="image/*"
      >
        <img v-if="avatarPreview" :src="avatarPreview" class="avatar-preview" />
        <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
      </el-upload>

      <template #footer>
        <el-button @click="avatarDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="uploadAvatar" :loading="uploading">
          确认上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Camera,
  Edit,
  DocumentCopy,
  ChatDotSquare,
  Calendar,
  Star,
  Setting,
  Lock,
  DataAnalysis,
  SwitchButton,
  Plus,
  Delete,
  Briefcase
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { useUserStore } from '@/stores/user'
import { getUserProfile, uploadAvatar as uploadAvatarApi, getUserStatistics, deleteAccount } from '@/api/user'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 用户角色
const userRoleType = computed(() => {
  const role = userInfo.value?.role
  if (role === 'admin') return 'danger'
  if (role === 'counselor') return 'warning'
  return ''
})

const userRoleText = computed(() => {
  const role = userInfo.value?.role
  if (role === 'admin') return '管理员'
  if (role === 'counselor') return '咨询师'
  return '普通用户'
})

// 是否是咨询师
const isCounselor = computed(() => {
  return userInfo.value?.role === 'counselor'
})

// 统计数据
const statistics = ref({
  testCount: 0,
  chatCount: 0,
  appointmentCount: 0,
  favoriteCount: 0
})

// 头像对话框
const avatarDialogVisible = ref(false)
const avatarPreview = ref('')
const avatarFile = ref(null)
const uploading = ref(false)

// 加载用户信息
const loadUserProfile = async () => {
  try {
    const res = await getUserProfile()
    userStore.setUserInfo(res.data)
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const res = await getUserStatistics()
    statistics.value = res.data || {}
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 编辑头像
const editAvatar = () => {
  // 重置状态
  avatarFile.value = null
  // 显示当前头像或预览
  if (userInfo.value?.avatar) {
    avatarPreview.value = userInfo.value.avatar
  } else {
    avatarPreview.value = ''
  }
  avatarDialogVisible.value = true
}

// 对话框关闭时的处理
const handleDialogClosed = () => {
  avatarFile.value = null
  avatarPreview.value = ''
}

// 头像文件选择
const handleAvatarChange = (file) => {
  const isImage = file.raw.type.startsWith('image/')
  const isLt2M = file.raw.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }

  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }

  avatarFile.value = file.raw
  avatarPreview.value = URL.createObjectURL(file.raw)
  return false
}

// 上传头像
const uploadAvatar = async () => {
  if (!avatarFile.value) {
    ElMessage.warning('请选择头像')
    return
  }

  try {
    uploading.value = true
    const res = await uploadAvatarApi(avatarFile.value)

    // 重新获取用户信息，确保显示最新的头像
    await loadUserProfile()

    ElMessage.success('头像更新成功')
    avatarDialogVisible.value = false
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
    avatarFile.value = null
  }
}

// 导航到指定路径
const navigateTo = (path) => {
  router.push(path)
}

// 跳转到编辑资料
const goToEdit = () => {
  router.push('/profile/edit')
}

// 跳转到隐私设置
const goToPrivacy = () => {
  router.push('/profile/privacy')
}

// 跳转到数据统计
const goToStatistics = () => {
  router.push('/profile/statistics')
}

// 跳转到咨询师申请
const goToCounselorApply = () => {
  router.push('/counselor/apply')
}

// 跳转到咨询师中心
const goToCounselorDashboard = () => {
  router.push('/counselor/dashboard')
}

// 退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await userStore.logout()
  } catch {
    // 取消退出
  }
}

// 注销账户
const handleDeleteAccount = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要注销账户吗？注销后将无法恢复。',
      '注销账户',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 调用注销账户API
    await deleteAccount()

    // 清除用户状态
    userStore.setToken('')
    userStore.setUserInfo(null)

    ElMessage.success('账户已注销，感谢您的使用')

    // 跳转到首页
    setTimeout(() => {
      window.location.href = '/'
    }, 1000)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('注销账户失败:', error)
      ElMessage.error('注销账户失败，请稍后重试')
    }
  }
}

// 组件挂载
onMounted(() => {
  loadUserProfile()
  loadStatistics()
})
</script>


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.profile-page {
  min-height: 100vh;
  background: $bg-page;
  padding-top: $header-height;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 24px;
}

// ── 顶部用户信息卡片 ──────────────────────────────────
.profile-card {
  border-radius: 24px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 4px 24px rgba(107,82,68,0.08) !important;
  margin-bottom: 28px;
  overflow: hidden;
  background: linear-gradient(160deg, #fde8d8 0%, #fbd4c0 60%, $bg-white 100%) !important;

  :deep(.el-card__body) { padding: 36px 40px; }
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 28px;
  flex-wrap: wrap;

  .user-info {
    flex: 1;

    h2 { font-size: 24px; font-weight: 700; color: $text-primary; margin: 0 0 6px; }
    .email { font-size: 14px; color: $text-secondary; margin-bottom: 14px; }
  }

  .avatar-wrapper { position: relative; }

  .edit-btn { margin-top: 12px; }
}

.profile-stats {
  display: flex;
  gap: 32px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(232,132,90,0.2);

  .stat-item {
    text-align: center;

    .value { font-size: 24px; font-weight: 700; color: $primary-color; display: block; }
    .label { font-size: 12px; color: $text-secondary; margin-top: 2px; }
  }
}

.tags { display: flex; flex-wrap: wrap; gap: 8px; }

// ── 内容卡片通用 ──────────────────────────────────────
.section-card {
  border-radius: 20px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 2px 12px rgba(107,82,68,0.06) !important;
  margin-bottom: 24px;

  :deep(.el-card__header) {
    font-weight: 600;
    color: $text-primary;
    border-bottom: 1px solid $border-lighter;
    padding: 18px 24px;
  }

  :deep(.el-card__body) { padding: 24px; }
}

// ── 测试历史 ──────────────────────────────────────────
.history-list { display: flex; flex-direction: column; gap: 12px; }

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: $bg-page;
  border-radius: 12px;
  border: 1px solid $border-lighter;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: rgba(232,132,90,0.06);
    border-color: rgba(232,132,90,0.25);
    transform: translateX(4px);
  }

  .item-info {
    h4 { margin: 0 0 4px; font-size: 14px; font-weight: 600; color: $text-primary; }
    .meta { font-size: 12px; color: $text-secondary; display: flex; gap: 12px; align-items: center; }
  }
}

// ── 咨询记录 ──────────────────────────────────────────
.consultation-list { display: flex; flex-direction: column; gap: 12px; }

.consultation-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 18px;
  background: $bg-page;
  border-radius: 12px;
  border: 1px solid $border-lighter;
  transition: all 0.2s ease;
  cursor: pointer;

  &:hover {
    background: rgba(232,132,90,0.06);
    border-color: rgba(232,132,90,0.2);
  }

  .counselor-info {
    flex: 1;
    h4 { margin: 0 0 4px; font-weight: 600; color: $text-primary; font-size: 14px; }
    .meta { font-size: 12px; color: $text-secondary; }
  }
}

// ── 响应式 ──────────────────────────────────────────
@media (max-width: $breakpoint-md) {
  .profile-header { flex-direction: column; text-align: center; }
  .profile-stats { justify-content: center; gap: 24px; }
}
</style>
