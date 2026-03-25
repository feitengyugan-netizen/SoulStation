<template>
  <div class="admin-login">
    <div class="login-container">
      <div class="login-header">
        <h1>心理咨询平台</h1>
        <p>后台管理系统</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            size="large"
            placeholder="请输入管理员账号"
            :prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            size="large"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            @keydown.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="form.remember">记住账号</el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <el-button text @click="goToUserLogin">返回用户端</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { adminLogin } from '@/api/admin'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const rules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
    loading.value = true
    const res = await adminLogin({
      username: form.username,
      password: form.password
    })

    localStorage.setItem('adminToken', res.data.token)
    localStorage.setItem('adminInfo', JSON.stringify(res.data.admin))

    if (form.remember) {
      localStorage.setItem('adminUsername', form.username)
    } else {
      localStorage.removeItem('adminUsername')
    }

    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch (error) {
    ElMessage.error('登录失败')
  } finally {
    loading.value = false
  }
}

const goToUserLogin = () => {
  router.push('/auth/login')
}

// 记住账号
const savedUsername = localStorage.getItem('adminUsername')
if (savedUsername) {
  form.username = savedUsername
  form.remember = true
}
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.admin-login { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.login-container { width: 400px; padding: $spacing-xl; background: white; border-radius: $border-radius-lg; box-shadow: $shadow-lg; }
.login-header { text-align: center; margin-bottom: $spacing-xl; }
.login-header h1 { font-size: 24px; margin: 0 0 $spacing-sm; color: $text-primary; }
.login-header p { color: $text-secondary; margin: 0; }
.login-form { margin-top: $spacing-lg; }
.login-btn { width: 100%; }
.login-footer { text-align: center; margin-top: $spacing-lg; }
</style>
