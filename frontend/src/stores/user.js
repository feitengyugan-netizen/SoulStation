// 用户状态管理
import { defineStore } from 'pinia'
import { login, register, logout, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
    isLoggedIn: !!localStorage.getItem('token')
  }),

  getters: {
    // 用户角色
    userRole: (state) => state.userInfo?.role || 'user',

    // 用户昵称
    nickname: (state) => state.userInfo?.nickname || '未登录',

    // 用户头像
    avatar: (state) => state.userInfo?.avatar || '',

    // 是否是咨询师
    isCounselor: (state) => state.userInfo?.role === 'counselor',

    // 是否是管理员
    isAdmin: (state) => state.userInfo?.role === 'admin'
  },

  actions: {
    // 设置token
    setToken(token) {
      this.token = token
      this.isLoggedIn = !!token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },

    // 设置用户信息
    setUserInfo(userInfo) {
      this.userInfo = userInfo
      if (userInfo) {
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
        localStorage.setItem('userRole', userInfo.role || 'user')
      } else {
        localStorage.removeItem('userInfo')
        localStorage.removeItem('userRole')
      }
    },

    // 登录
    async login(loginData) {
      try {
        const res = await login(loginData)
        this.setToken(res.data.token)
        this.setUserInfo(res.data.userInfo)
        return res
      } catch (error) {
        throw error
      }
    },

    // 注册
    async register(registerData) {
      try {
        const res = await register(registerData)
        // 注册后自动登录
        this.setToken(res.data.token)
        this.setUserInfo(res.data.userInfo)
        return res
      } catch (error) {
        throw error
      }
    },

    // 获取用户信息
    async fetchUserInfo() {
      try {
        const res = await getUserInfo()
        this.setUserInfo(res.data)
        return res
      } catch (error) {
        throw error
      }
    },

    // 退出登录
    async logout() {
      try {
        await logout()
      } catch (error) {
        console.error('退出登录失败:', error)
      } finally {
        this.setToken('')
        this.setUserInfo(null)
        // 跳转到登录页
        window.location.href = '/login'
      }
    }
  }
})
