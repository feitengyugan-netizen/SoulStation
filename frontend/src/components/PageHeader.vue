<template>
  <header class="page-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo -->
        <div class="logo" @click="goHome">
          <el-icon :size="32" color="#409EFF">
            <component :is="icons.ChatLineSquare" />
          </el-icon>
          <span class="logo-text">心理咨询平台</span>
        </div>

        <!-- 导航菜单 -->
        <nav class="nav-menu">
          <el-menu
            :default-active="activeMenu"
            mode="horizontal"
            :ellipsis="false"
            router
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/chat">智能问答</el-menu-item>
            <el-menu-item index="/test">心理测试</el-menu-item>
            <el-menu-item index="/counselor">找咨询师</el-menu-item>
            <el-menu-item index="/knowledge">心理知识</el-menu-item>
          </el-menu>
        </nav>

        <!-- 右侧操作区 -->
        <div class="header-actions">
          <!-- 搜索框 -->
          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索..."
              prefix-icon="Search"
              clearable
              @keyup.enter="handleSearch"
            />
          </div>

          <!-- 未登录状态 -->
          <template v-if="!isLoggedIn">
            <el-button text @click="goToLogin">登录</el-button>
            <el-button type="primary" @click="goToRegister">注册</el-button>
          </template>

          <!-- 已登录状态 -->
          <template v-else>
            <!-- 通知 -->
<<<<<<< Updated upstream
            <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="notification-badge">
              <el-button circle :icon="icons.Bell" @click="showNotifications" />
            </el-badge>
=======
            <el-popover
              placement="bottom-end"
              :width="380"
              trigger="click"
              :show-arrow="false"
              popper-class="notification-popover"
              @show="loadNotifications"
            >
              <template #reference>
                <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="notification-badge">
                  <el-button circle :icon="Bell" />
                </el-badge>
              </template>

              <div class="notify-panel">
                <div class="notify-header">
                  <span class="notify-title">消息通知</span>
                  <el-button
                    v-if="unreadCount > 0"
                    text
                    size="small"
                    type="primary"
                    @click="markAllRead"
                  >全部已读</el-button>
                </div>

                <div class="notify-list" v-loading="notifyLoading">
                  <template v-if="notifications.length > 0">
                    <div
                      v-for="item in notifications"
                      :key="item.id"
                      class="notify-item"
                      :class="{ unread: !item.is_read }"
                      @click="handleNotifyClick(item)"
                    >
                      <div class="notify-dot" v-if="!item.is_read" />
                      <div class="notify-content">
                        <p class="notify-item-title">{{ item.title }}</p>
                        <p class="notify-item-text">{{ item.content }}</p>
                        <span class="notify-time">{{ formatNotifyTime(item.created_at) }}</span>
                      </div>
                    </div>
                  </template>
                  <el-empty v-else description="暂无通知" :image-size="60" />
                </div>
              </div>
            </el-popover>
>>>>>>> Stashed changes

            <!-- 用户下拉菜单 -->
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="36" :src="userInfo?.avatar">
                  <el-icon><component :is="icons.User" /></el-icon>
                </el-avatar>
                <span class="username">{{ userInfo?.nickname || '用户' }}</span>
                <el-icon class="dropdown-icon"><component :is="icons.ArrowDown" /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><component :is="icons.User" /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="orders" v-if="!isCounselor">
                    <el-icon><component :is="icons.Calendar" /></el-icon>
                    我的预约
                  </el-dropdown-item>
                  <el-dropdown-item command="counselor-orders" v-if="isCounselor">
                    <el-icon><component :is="icons.Calendar" /></el-icon>
                    工作台
                  </el-dropdown-item>
                  <el-dropdown-item command="admin" v-if="isAdmin">
                    <el-icon><component :is="icons.Setting" /></el-icon>
                    后台管理
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><component :is="icons.SwitchButton" /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
<<<<<<< Updated upstream
import { ref, computed, markRaw } from 'vue'
=======
import { ref, computed, onMounted, onUnmounted } from 'vue'
>>>>>>> Stashed changes
import { useRouter, useRoute } from 'vue-router'
import {
  ChatLineSquare,
  Bell,
  User,
  ArrowDown,
  Calendar,
  Setting,
  SwitchButton
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { ElMessageBox, ElMessage } from 'element-plus'
import { getNotifications, getUnreadCount, markNotificationRead, markAllNotificationsRead } from '@/api/consultation'

// Mark icon components as raw to prevent unnecessary reactivity
const icons = markRaw({
  ChatLineSquare,
  Bell,
  User,
  ArrowDown,
  Calendar,
  Setting,
  SwitchButton
})

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 搜索关键词
const searchKeyword = ref('')

// 通知状态
const unreadCount = ref(0)
const notifications = ref([])
const notifyLoading = ref(false)
let pollTimer = null

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 是否登录
const isLoggedIn = computed(() => userStore.isLoggedIn)

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 是否是咨询师
const isCounselor = computed(() => userStore.isCounselor)

// 是否是管理员
const isAdmin = computed(() => userStore.isAdmin)

// 回到首页
const goHome = () => {
  router.push('/')
}

// 搜索处理
const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    // 跳转到搜索结果页
    router.push({
      path: '/search',
      query: { keyword: searchKeyword.value }
    })
  }
}

// 加载通知列表
const loadNotifications = async () => {
  notifyLoading.value = true
  try {
    const res = await getNotifications({ page_size: 10 })
    notifications.value = res.data?.items || []
    unreadCount.value = res.data?.unread_count || 0
  } catch {
    // silent
  } finally {
    notifyLoading.value = false
  }
}

// 轮询未读数量
const pollUnreadCount = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data?.unread_count || 0
  } catch {
    // silent
  }
}

// 全部已读
const markAllRead = async () => {
  try {
    await markAllNotificationsRead()
    unreadCount.value = 0
    notifications.value = notifications.value.map(n => ({ ...n, is_read: true }))
  } catch {
    ElMessage.error('操作失败')
  }
}

// 点击通知
const handleNotifyClick = async (item) => {
  if (!item.is_read) {
    try {
      await markNotificationRead(item.id)
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch {
      // silent
    }
  }
  // 根据通知类型跳转
  if (!item.related_id) return
  if (['new_message', 'consultation_started'].includes(item.type)) {
    // 有未读消息，跳转到咨询对话
    const isCounselor = userStore.isCounselor
    router.push(`/consultation/${isCounselor ? 'counselor' : 'user'}/${item.related_id}`)
  } else if (['appointment_confirmed', 'appointment_rejected', 'appointment_cancelled', 'consultation_ended'].includes(item.type)) {
    router.push('/counselor/orders')
  }
}

// 格式化通知时间
const formatNotifyTime = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

onMounted(() => {
  pollUnreadCount()
  pollTimer = setInterval(pollUnreadCount, 30000) // 每30秒轮询
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

// 下拉菜单命令处理
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'orders':
      router.push('/counselor/orders')
      break
    case 'counselor-orders':
      router.push('/consultation/counselor/orders')
      break
    case 'admin':
      router.push('/admin/dashboard')
      break
    case 'logout':
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
      break
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/register')
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.page-header {
  background: $bg-white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: $header-height;
  gap: $spacing-lg;
}

.logo {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  cursor: pointer;
  flex-shrink: 0;

  .logo-text {
    font-size: $font-size-large;
    font-weight: 600;
    color: $text-primary;
    white-space: nowrap;
  }
}

.nav-menu {
  flex: 1;
  overflow-x: auto;

  :deep(.el-menu) {
    border-bottom: none;
    background: transparent;

    .el-menu-item {
      font-size: $font-size-base;
      color: $text-regular;

      &:hover {
        color: $primary-color;
      }

      &.is-active {
        color: $primary-color;
        font-weight: 500;
        border-bottom-color: $primary-color;
      }
    }
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  flex-shrink: 0;

  .search-box {
    width: 200px;

    :deep(.el-input__wrapper) {
      border-radius: 20px;
    }
  }

  .notification-badge {
    :deep(.el-badge__content) {
      transform: translateY(-50%) translateX(50%);
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: $spacing-sm;
    cursor: pointer;
    padding: $spacing-xs $spacing-sm;
    border-radius: $border-radius-md;
    transition: $transition-base;

    &:hover {
      background-color: $bg-color;
    }

    .username {
      font-size: $font-size-base;
      color: $text-primary;
      max-width: 100px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .dropdown-icon {
      font-size: $font-size-small;
      color: $text-secondary;
    }
  }
}

// ── 通知面板样式（全局注入） ──────────────────────────
</style>

<style lang="scss">
@use '@/styles/variables.scss' as *;

.notification-popover {
  padding: 0 !important;
  border-radius: 16px !important;
  border: 1px solid $border-lighter !important;
  box-shadow: 0 8px 32px rgba(107,82,68,0.12) !important;
}

.notify-panel {
  .notify-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 18px 12px;
    border-bottom: 1px solid $border-lighter;

    .notify-title {
      font-size: 15px;
      font-weight: 700;
      color: $text-primary;
    }
  }

  .notify-list {
    max-height: 380px;
    overflow-y: auto;
    min-height: 80px;
  }

  .notify-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 14px 18px;
    cursor: pointer;
    transition: background 0.15s;
    border-bottom: 1px solid rgba(0,0,0,0.04);

    &:hover { background: $bg-subtle; }

    &.unread { background: rgba(232,132,90,0.04); }

    .notify-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: $primary-color;
      flex-shrink: 0;
      margin-top: 6px;
    }

    .notify-content {
      flex: 1;
      min-width: 0;

      .notify-item-title {
        font-size: 13px;
        font-weight: 600;
        color: $text-primary;
        margin: 0 0 4px;
      }

      .notify-item-text {
        font-size: 12px;
        color: $text-secondary;
        margin: 0 0 6px;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .notify-time {
        font-size: 11px;
        color: $text-placeholder;
      }
    }
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .nav-menu {
    display: none;
  }

  .search-box {
    width: 150px !important;
  }

  .username {
    display: none;
  }
}

@media (max-width: $breakpoint-sm) {
  .header-content {
    padding: 0 $spacing-md;
  }

  .search-box {
    display: none;
  }

  .logo-text {
    display: none;
  }
}
</style>
