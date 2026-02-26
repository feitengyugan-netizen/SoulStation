<template>
  <div class="register-container">
    <div class="register-box">
      <!-- Logo和标题 -->
      <div class="register-header">
        <div class="logo">
          <el-icon :size="48" color="#409EFF">
            <ChatLineSquare />
          </el-icon>
        </div>
        <h1 class="title">心理咨询平台</h1>
        <p class="subtitle">创建新账户，开启心灵之旅</p>
      </div>

      <!-- 注册表单 -->
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="registerRules"
        class="register-form"
        @submit.prevent="handleRegister"
      >
        <!-- 邮箱输入 -->
        <el-form-item prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            prefix-icon="Message"
            size="large"
            clearable
          />
        </el-form-item>

        <!-- 验证码输入 -->
        <el-form-item prop="code">
          <div class="code-input-wrapper">
            <el-input
              v-model="registerForm.code"
              placeholder="请输入验证码"
              prefix-icon="Key"
              size="large"
              maxlength="6"
            />
            <el-button
              type="primary"
              size="large"
              :disabled="countdown > 0"
              :loading="sendingCode"
              @click="sendVerificationCode"
            >
              {{ countdown > 0 ? `${countdown}秒后重试` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <!-- 密码输入 -->
        <el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请设置密码（6-20位）"
            prefix-icon="Lock"
            size="large"
            show-password
            @input="checkPasswordStrength"
          />
          <!-- 密码强度指示器 -->
          <div v-if="registerForm.password" class="password-strength">
            <span class="strength-label">密码强度：</span>
            <div class="strength-bar">
              <div
                class="strength-bar-fill"
                :class="passwordStrength.class"
                :style="{ width: passwordStrength.width }"
              ></div>
            </div>
            <span class="strength-text" :class="passwordStrength.class">
              {{ passwordStrength.text }}
            </span>
          </div>
        </el-form-item>

        <!-- 确认密码输入 -->
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <!-- 用户协议 -->
        <el-form-item prop="agreed">
          <el-checkbox v-model="registerForm.agreed">
            我已阅读并同意
            <el-link type="primary">《用户协议》</el-link>
            和
            <el-link type="primary">《隐私政策》</el-link>
          </el-checkbox>
        </el-form-item>

        <!-- 注册按钮 -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="register-button"
            :loading="loading"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>

        <!-- 登录链接 -->
        <div class="login-link">
          已有账号？
          <el-link type="primary" @click="goToLogin">立即登录</el-link>
        </div>
      </el-form>
    </div>

    <!-- 页脚 -->
    <footer class="register-footer">
      <p>© 2026 心理咨询平台 - 关注心理健康</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ChatLineSquare } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { sendEmailCode } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

// 表单引用
const registerFormRef = ref(null)

// 加载状态
const loading = ref(false)
const sendingCode = ref(false)

// 倒计时
const countdown = ref(0)
let countdownTimer = null

// 表单数据
const registerForm = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
  agreed: false
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = registerForm.password
  if (!password) return { width: '0%', text: '', class: '' }

  let strength = 0
  if (password.length >= 6) strength++
  if (password.length >= 10) strength++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++

  if (strength <= 2) return { width: '33%', text: '弱', class: 'weak' }
  if (strength <= 3) return { width: '66%', text: '中', class: 'medium' }
  return { width: '100%', text: '强', class: 'strong' }
})

// 自定义校验规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateAgreed = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请阅读并同意用户协议'))
  } else {
    callback()
  }
}

// 表单校验规则
const registerRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    {
      type: 'email',
      message: '请输入正确的邮箱格式',
      trigger: ['blur', 'change']
    }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码应为6位数字', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应为6-20位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ],
  agreed: [
    { required: true, validator: validateAgreed, trigger: 'change' }
  ]
}

// 发送验证码
const sendVerificationCode = async () => {
  // 校验邮箱
  if (!registerForm.email) {
    ElMessage.warning('请先输入邮箱地址')
    return
  }

  const emailReg = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailReg.test(registerForm.email)) {
    ElMessage.error('请输入正确的邮箱格式')
    return
  }

  try {
    sendingCode.value = true
    await sendEmailCode({ email: registerForm.email })
    ElMessage.success('验证码已发送至您的邮箱，请注意查收')

    // 开始倒计时
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
  } finally {
    sendingCode.value = false
  }
}

// 检查密码强度
const checkPasswordStrength = () => {
  // 密码强度通过computed自动计算
}

// 注册处理
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    // 表单校验
    await registerFormRef.value.validate()

    // 开始注册
    loading.value = true

    // 调用注册接口
    await userStore.register({
      email: registerForm.email,
      code: registerForm.code,
      password: registerForm.password
    })

    // 注册成功提示
    ElMessage.success('注册成功！欢迎加入')

    // 跳转到首页
    setTimeout(() => {
      router.push('/')
    }, 500)
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 组件销毁时清除定时器
const onBeforeUnmount = () => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
}
</script>

<style lang="scss" scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;

  // 背景装饰
  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: moveBackground 20s linear infinite;
  }

  @keyframes moveBackground {
    0% {
      transform: translate(0, 0);
    }
    100% {
      transform: translate(50px, 50px);
    }
  }
}

.register-box {
  position: relative;
  width: 100%;
  max-width: 460px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 48px 40px;
  z-index: 1;
}

.register-header {
  text-align: center;
  margin-bottom: 32px;

  .logo {
    margin-bottom: 16px;
  }

  .title {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .subtitle {
    font-size: 14px;
    color: #909399;
  }
}

.register-form {
  .code-input-wrapper {
    display: flex;
    gap: 12px;

    .el-input {
      flex: 1;
    }

    .el-button {
      white-space: nowrap;
    }
  }

  .password-strength {
    display: flex;
    align-items: center;
    margin-top: 8px;
    font-size: 12px;

    .strength-label {
      color: #909399;
      margin-right: 8px;
    }

    .strength-bar {
      flex: 1;
      height: 4px;
      background: #e4e7ed;
      border-radius: 2px;
      overflow: hidden;
      margin-right: 8px;
    }

    .strength-bar-fill {
      height: 100%;
      transition: all 0.3s;

      &.weak {
        background: #f56c6c;
      }

      &.medium {
        background: #e6a23c;
      }

      &.strong {
        background: #67c23a;
      }
    }

    .strength-text {
      font-weight: 500;

      &.weak {
        color: #f56c6c;
      }

      &.medium {
        color: #e6a23c;
      }

      &.strong {
        color: #67c23a;
      }
    }
  }

  .el-form-item {
    margin-bottom: 20px;
  }

  .register-button {
    width: 100%;
    height: 44px;
    font-size: 16px;
    font-weight: 500;
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border: none;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4);
    }

    &:active {
      transform: translateY(0);
    }
  }

  .login-link {
    text-align: center;
    font-size: 14px;
    color: #606266;
    margin-top: 16px;
  }
}

.register-footer {
  position: relative;
  z-index: 1;
  margin-top: 32px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

// 响应式
@media (max-width: 768px) {
  .register-box {
    padding: 32px 24px;
  }

  .register-header .title {
    font-size: 24px;
  }

  .code-input-wrapper {
    flex-direction: column !important;

    .el-button {
      width: 100%;
    }
  }
}
</style>
