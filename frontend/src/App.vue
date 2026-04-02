<template>
  <div id="app">
    <!-- 登录/注册页面使用简单布局 -->
    <router-view v-if="isAuthPage" />

    <!-- 其他页面使用主布局 -->
    <MainLayout v-else>
      <router-view />
    </MainLayout>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import MainLayout from '@/components/MainLayout.vue'

const route = useRoute()

// 判断是否是认证相关页面
const isAuthPage = computed(() => {
  const authPaths = ['/login', '/register', '/forgot-password', '/admin/login']
  return authPaths.some(path => route.path.startsWith(path))
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  transition: background 0.3s;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>
  