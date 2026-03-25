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
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
              <el-icon :size="28"><DocumentCopy /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ statistics.testCount || 0 }}</div>
              <div class="stat-label">心理测试</div>
            </div>
          </div>

          <div class="stat-item" @click="navigateTo('/chat')">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)">
              <el-icon :size="28"><ChatDotSquare /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ statistics.chatCount || 0 }}</div>
              <div class="stat-label">智能问答</div>
            </div>
          </div>

          <div class="stat-item" @click="navigateTo('/counselor/orders')">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)">
              <el-icon :size="28"><Calendar /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-number">{{ statistics.appointmentCount || 0 }}</div>
              <div class="stat-label">咨询预约</div>
            </div>
          </div>

          <div class="stat-item" @click="navigateTo('/knowledge')">
            <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)">
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
              <el-icon :size="32" color="#667eea"><DocumentCopy /></el-icon>
            </div>
            <span>我的测试</span>
          </div>

          <div class="access-item" @click="navigateTo('/chat')">
            <div class="access-icon">
              <el-icon :size="32" color="#f093fb"><ChatDotSquare /></el-icon>
            </div>
            <span>我的对话</span>
          </div>

          <div class="access-item" @click="navigateTo('/counselor/orders')">
            <div class="access-icon">
              <el-icon :size="32" color="#4facfe"><Calendar /></el-icon>
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
  Delete
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
@use '@/styles/variables.scss' as *;

.profile-page {
  min-height: 100vh;
  background: $bg-color;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: $spacing-lg;
}

.profile-card {
  margin-bottom: $spacing-lg;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
  padding: $spacing-xl 0;
  border-bottom: 1px solid $border-lighter;
  margin-bottom: $spacing-xl;

  .avatar-section {
    position: relative;
    cursor: pointer;

    .edit-avatar-btn {
      position: absolute;
      bottom: 0;
      right: 0;
      opacity: 0;
      transition: $transition-base;
    }

    &:hover .edit-avatar-btn {
      opacity: 1;
    }
  }

  .user-info {
    flex: 1;

    h2 {
      margin: 0 0 $spacing-sm;
      font-size: $font-size-extra-large;
    }

    .email {
      color: $text-secondary;
      margin-bottom: $spacing-md;
    }
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-lg;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-lg;
  border: 1px solid $border-lighter;
  border-radius: $border-radius-md;
  cursor: pointer;
  transition: $transition-base;

  &:hover {
    border-color: $primary-color;
    box-shadow: $box-shadow-base;
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: $border-radius-md;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .stat-content {
    .stat-number {
      font-size: 28px;
      font-weight: 600;
      color: $text-primary;
      line-height: 1.2;
    }

    .stat-label {
      font-size: $font-size-base;
      color: $text-secondary;
    }
  }
}

.quick-access-card {
  .quick-access-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: $spacing-md;
  }

  .access-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: $spacing-lg;
    border: 1px solid $border-lighter;
    border-radius: $border-radius-md;
    cursor: pointer;
    transition: $transition-base;

    &:hover {
      border-color: $primary-color;
      background: rgba($primary-color, 0.05);
    }

    .access-icon {
      margin-bottom: $spacing-sm;
    }

    span {
      font-size: $font-size-base;
      color: $text-primary;
    }
  }
}

// 头像上传
.avatar-uploader {
  display: flex;
  justify-content: center;

  .avatar-preview {
    width: 200px;
    height: 200px;
    border-radius: 50%;
    object-fit: cover;
  }

  .avatar-uploader-icon {
    width: 200px;
    height: 200px;
    border: 2px dashed $border-light;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: $text-placeholder;
    font-size: 48px;
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .profile-header {
    flex-direction: column;
    text-align: center;

    .user-info {
      width: 100%;
    }
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .quick-access-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: $breakpoint-sm) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
