<template>
  <div class="modern-chat-container user">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-left">
        <el-button circle @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div class="user-info">
          <el-avatar :size="45" :src="appointment?.counselorAvatar" class="user-avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <h3 class="user-name">{{ appointment?.counselorName || '咨询师' }}</h3>
            <div class="status-info">
              <span class="online-dot" :class="{ offline: !isOnline }"></span>
              <span class="status-text">{{ isOnline ? '在线' : '离线' }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <div class="chat-info">
          <el-icon><Timer /></el-icon>
          <span>{{ formatDuration(elapsedTime) }}</span>
        </div>
        <el-dropdown @command="handleMenuCommand" trigger="click">
          <el-button circle>
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="info">
                <el-icon><User /></el-icon> 咨询师信息
              </el-dropdown-item>
              <el-dropdown-item command="end" divided>
                <el-icon><SwitchButton /></el-icon> 结束咨询
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 咨询师信息面板（可展开） -->
    <el-collapse-transition>
      <div v-show="showCounselorInfo" class="counselor-info-panel">
        <el-card>
          <template #header>
            <div class="panel-header">
              <span>咨询师详细信息</span>
              <el-button text @click="showCounselorInfo = false">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="info-content">
            <div class="info-item">
              <span class="label">咨询状态：</span>
              <el-tag :type="appointment?.status === 'in_progress' ? 'primary' : 'info'">
                {{ getStatusText(appointment?.status) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="label">咨询方式：</span>
              <el-tag>{{ getTypeText(appointment?.type) }}</el-tag>
            </div>
            <div class="info-item">
              <span class="label">咨询时长：</span>
              <span>{{ appointment?.duration || 60 }}分钟</span>
            </div>
          </div>
        </el-card>
      </div>
    </el-collapse-transition>

    <!-- 消息区域 -->
    <div ref="messagesContainer" class="messages-container">
      <div v-loading="loading" class="messages-content">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message-wrapper"
          :class="{ 'message-self': msg.senderType === 'user' }"
        >
          <div class="message-bubble">
            <div v-if="msg.type === 'text'" class="message-text">
              {{ msg.content }}
            </div>
            <div v-else-if="msg.type === 'image'" class="message-image">
              <el-image :src="msg.content" fit="cover" :preview-src-list="[msg.content]" />
            </div>
            <div v-else-if="msg.type === 'file'" class="message-file">
              <el-icon><Document /></el-icon>
              <span class="file-name">{{ getFileName(msg.content) }}</span>
              <el-button type="primary" text @click="downloadFile(msg.content)">
                <el-icon><Download /></el-icon> 下载
              </el-button>
            </div>
            <div class="message-time">
              {{ formatTime(msg.createdAt) }}
            </div>
          </div>
        </div>

        <!-- 正在输入指示器 -->
        <div v-if="isTyping" class="typing-indicator">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <span>咨询师正在输入...</span>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && messages.length === 0" class="empty-messages">
          <el-empty description="暂无消息，开始对话吧">
            <template #image>
              <el-icon :size="80"><ChatDotRound /></el-icon>
            </template>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="input-container">
      <!-- 工具栏 -->
      <div class="input-toolbar">
        <div class="toolbar-left">
          <el-upload
            :show-file-list="false"
            :before-upload="handleUploadImage"
            accept="image/*"
          >
            <el-button circle>
              <el-icon><Picture /></el-icon>
            </el-button>
          </el-upload>
          <el-upload
            :show-file-list="false"
            :before-upload="handleUploadFile"
          >
            <el-button circle>
              <el-icon><Folder /></el-icon>
            </el-button>
          </el-upload>
        </div>
        <div class="toolbar-right">
          <el-button circle @click="toggleVoiceRecording" :type="isRecording ? 'danger' : ''">
            <el-icon><Microphone /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 输入框 -->
      <div class="input-area">
        <el-input
          v-model="inputContent"
          type="textarea"
          :rows="2"
          placeholder="输入消息... (Ctrl+Enter 发送)"
          @keydown.ctrl.enter="sendMessage"
          class="message-input"
        />
        <el-button
          type="primary"
          :loading="sending"
          @click="sendMessage"
          class="send-btn"
          :disabled="!inputContent.trim()"
        >
          <el-icon v-if="!sending"><Promotion /></el-icon>
          {{ sending ? '发送中' : '发送' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Timer, User, ArrowLeft, MoreFilled, SwitchButton, Close, Picture,
  Folder, Microphone, ChatDotRound, Document, Download, Promotion
} from '@element-plus/icons-vue'
import { getMessages, sendMessage as sendMessageApi, uploadFile, endConsultation } from '@/api/consultation'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const appointmentId = route.params.id
const loading = ref(true)
const sending = ref(false)
const isRecording = ref(false)
const isTyping = ref(false)
const isOnline = ref(true)
const elapsedTime = ref(0)
const inputContent = ref('')
const messages = ref([])
const appointment = ref({})
const showCounselorInfo = ref(false)
const messagesContainer = ref(null)

const currentUserId = computed(() => userStore.user?.id)
const currentUserAvatar = computed(() => userStore.user?.avatar)

let pollingTimer = null
let durationTimer = null

const goBack = () => {
  router.push('/counselor/orders')
}

const loadAppointment = async () => {
  try {
    // 从用户订单API获取当前用户的所有订单，找到对应的订单
    const { getUserAppointments } = await import('@/api/counselor')
    const res = await getUserAppointments({ page: 1, pageSize: 100 })

    if (res.code === 200 && res.data) {
      const orders = res.data.items || res.data.list || []
      const currentOrder = orders.find(o => o.id === parseInt(appointmentId))

      if (currentOrder) {
        appointment.value = {
          counselorName: currentOrder.counselorName || '咨询师',
          counselorAvatar: currentOrder.counselorAvatar || '',
          type: currentOrder.consultationType,
          status: currentOrder.status,
          duration: currentOrder.duration
        }
      } else {
        ElMessage.error('未找到该订单')
        goBack()
      }
    }
  } catch (error) {
    console.error('加载订单信息失败', error)
  }
}

const loadMessages = async (lastId = null) => {
  try {
    const res = await getMessages(appointmentId, { lastId })
    console.log('获取消息API响应:', res)

    const newMessages = res.data.items || res.data.list || []
    const processedMessages = newMessages.map(msg => {
      const processed = {
        ...msg,
        type: msg.message_type || msg.type,
        senderId: msg.sender_id,
        senderType: msg.sender_type,
        createdAt: msg.created_at
      }
      console.log('消息详情:', {
        id: msg.id,
        sender_id: msg.sender_id,
        sender_type: msg.sender_type,
        content: msg.content,
        isSelf: msg.sender_type === 'user'
      })
      return processed
    })

    console.log('当前用户ID:', currentUserId.value)
    console.log('处理后的消息数量:', processedMessages.length)

    if (lastId === null) {
      messages.value = processedMessages
    } else {
      messages.value = [...messages.value, ...processedMessages]
    }

    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败', error)
  }
}

const sendMessage = async () => {
  if (!inputContent.value.trim()) return

  try {
    sending.value = true
    const res = await sendMessageApi(appointmentId, {
      content: inputContent.value,
      type: 'text'
    })

    inputContent.value = ''
    await loadMessages()
    ElMessage.success('发送成功')
  } catch (error) {
    console.error('发送失败:', error)
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

const handleUploadImage = async (file) => {
  try {
    const res = await uploadFile(file)
    await sendMessageApi(appointmentId, {
      content: res.data.url,
      type: 'image'
    })
    await loadMessages()
  } catch (error) {
    ElMessage.error('上传失败')
  }
  return false
}

const handleUploadFile = async (file) => {
  try {
    const res = await uploadFile(file)
    await sendMessageApi(appointmentId, {
      content: res.data.url,
      type: 'file'
    })
    await loadMessages()
  } catch (error) {
    ElMessage.error('上传失败')
  }
  return false
}

const toggleVoiceRecording = () => {
  isRecording.value = !isRecording.value
  ElMessage.info(isRecording.value ? '开始录音' : '停止录音')
}

const handleMenuCommand = async (command) => {
  switch (command) {
    case 'info':
      showCounselorInfo.value = !showCounselorInfo.value
      break
    case 'end':
      await handleEndConsultation()
      break
  }
}

const handleEndConsultation = async () => {
  try {
    await ElMessageBox.confirm('确定要结束本次咨询吗？', '提示', { type: 'warning' })
    await endConsultation(appointmentId)
    ElMessage.success('咨询已结束')
    goBack()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const getTypeText = (type) => ({ video: '视频', voice: '语音', offline: '线下' }[type] || type)

const getStatusText = (status) => ({
  confirmed: '已确认',
  in_progress: '咨询中',
  completed: '已完成'
}[status] || status)

const formatTime = (time) => {
  const date = new Date(time)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
}

const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}时${m}分${s}秒`
  if (m > 0) return `${m}分${s}秒`
  return `${s}秒`
}

const getFileName = (url) => url.split('/').pop()

const downloadFile = (url) => {
  window.open(url, '_blank')
}

const startPolling = () => {
  pollingTimer = setInterval(() => loadMessages(), 3000)
}

const startTimer = () => {
  durationTimer = setInterval(() => {
    elapsedTime.value++
  }, 1000)
}

onMounted(async () => {
  try {
    await loadAppointment()
    await loadMessages()
    loading.value = false
    startPolling()
    startTimer()
  } catch (error) {
    ElMessage.error('加载失败')
    goBack()
  }
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
  if (durationTimer) clearInterval(durationTimer)
})
</script>

<style scoped>
/* 使用与咨询师端相同的样式，但添加用户特有的样式 */
@import url('./ConsultationChatCounselor.vue');

.modern-chat-container.user .message-wrapper:not(.message-self) .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-left-radius: 2px;
}

.modern-chat-container.user .message-wrapper.message-self .message-bubble {
  background: white;
  color: #303133;
  border-bottom-right-radius: 2px;
  border: 1px solid #e4e7ed;
}

.modern-chat-container.user .online-dot.offline {
  background: #909399;
}
</style>