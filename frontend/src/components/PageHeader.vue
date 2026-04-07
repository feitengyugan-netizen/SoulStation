<template>
  <header class="page-header">
    <div class="container">
      <div class="header-content">
        <!-- Logo -->
        <div class="logo" @click="goHome">
          <span class="logo-icon">🌸</span>
          <span class="logo-text">心灵驿站</span>
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
            <el-button text class="auth-btn-login" @click="goToLogin">登录</el-button>
            <el-button type="primary" class="auth-btn-register" @click="goToRegister">注册</el-button>
          </template>

          <!-- 已登录状态 -->
          <template v-else>
            <!-- 通知 -->
            <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="notification-badge">
              <el-button circle :icon="Bell" @click="showNotifications" />
            </el-badge>

            <!-- 用户下拉菜单 -->
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="36" :src="userInfo?.avatar">
                  <el-icon><User /></el-icon>
                </el-avatar>
                <span class="username">{{ userInfo?.nickname || '用户' }}</span>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="orders" v-if="!isCounselor">
                    <el-icon><Calendar /></el-icon>
                    我的预约
                  </el-dropdown-item>
                  <el-dropdown-item command="counselor-orders" v-if="isCounselor">
                    <el-icon><Calendar /></el-icon>
                    工作台
                  </el-dropdown-item>
                  <el-dropdown-item command="admin" v-if="isAdmin">
                    <el-icon><Setting /></el-icon>
                    后台管理
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
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
import { ref, computed } from 'vue'
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

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 搜索关键词
const searchKeyword = ref('')

// 通知数量
const notificationCount = ref(0)

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

// 显示通知
const showNotifications = () => {
  ElMessage.info('暂无新通知')
}

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
  background: rgba(255, 252, 248, 0.92);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid $border-lighter;
  box-shadow: 0 2px 16px rgba(107, 82, 68, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
  transition: $transition-base;
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
  padding: 6px 10px;
  border-radius: $border-radius-lg;
  transition: $transition-base;

  &:hover {
    background: $bg-subtle;
  }

  .logo-icon {
    font-size: 28px;
    line-height: 1;
  }

  .logo-text {
    font-size: 17px;
    font-weight: 700;
    color: $text-primary;
    white-space: nowrap;
    letter-spacing: 1px;
  }
}

.nav-menu {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;

  :deep(.el-menu--horizontal) {
    height: $header-height !important;
    border-bottom: none !important;
    background: transparent !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px;

    &.el-menu {
      border-bottom: none !important;
    }

    .el-menu-item {
      font-size: 14px;
      font-weight: 600;
      color: $text-regular !important;
      border-radius: $border-radius-full !important;
      margin: 0 2px;
      padding: 0 16px !important;
      height: 38px !important;
      line-height: 38px !important;
      transition: $transition-base !important;
      border-bottom: none !important;

      &:hover {
        color: $primary-color !important;
        background: $bg-subtle !important;
      }

      &.is-active {
        color: $primary-dark !important;
        background: rgba(232, 132, 90, 0.1) !important;
        border-bottom: none !important;
      }

      &::before,
      &::after {
        display: none !important;
      }
    }
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex-shrink: 0;

  .search-box {
    width: 180px;
    transition: $transition-base;

    :deep(.el-input__wrapper) {
      border-radius: $border-radius-full !important;
      background: $bg-subtle !important;
      box-shadow: none !important;
      border: 1px solid $border-lighter !important;

      &:hover, &.is-focus {
        border-color: $primary-light !important;
        background: white !important;
      }
    }
  }

  .notification-badge {
    :deep(.el-badge__content) {
      background: $primary-color;
    }
  }

  .auth-btn-login {
    color: $text-regular !important;
    font-weight: 500;
    border-radius: $border-radius-full !important;
    padding: 0 16px !important;

    &:hover {
      color: $primary-color !important;
      background: $bg-subtle !important;
    }
  }

  .auth-btn-register {
    border-radius: $border-radius-full !important;
    background: $primary-gradient !important;
    border: none !important;
    color: white !important;
    font-weight: 600;
    padding: 0 20px !important;
    box-shadow: 0 4px 12px rgba(232, 132, 90, 0.3) !important;

    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(232, 132, 90, 0.4) !important;
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 6px 10px 6px 6px;
    border-radius: $border-radius-full;
    transition: $transition-base;
    border: 1px solid transparent;

    &:hover {
      background: $bg-subtle;
      border-color: $border-base;
    }

    .username {
      font-size: 14px;
      font-weight: 500;
      color: $text-primary;
      max-width: 90px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .dropdown-icon {
      font-size: 12px;
      color: $text-secondary;
    }
  }
}

// 响应式
@media (max-width: $breakpoint-md) {
  .nav-menu { display: none; }
  .search-box { width: 140px !important; }
  .username { display: none !important; }
}

@media (max-width: $breakpoint-sm) {
  .header-content { padding: 0 $spacing-md; }
  .search-box { display: none !important; }
  .logo-text { display: none; }
}
</style>
