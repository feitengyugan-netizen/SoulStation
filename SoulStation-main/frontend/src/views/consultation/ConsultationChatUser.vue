<template>
  <div class="consultation-chat-user">
    <PageHeader />
    <div v-loading="loading" class="chat-container">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-info">
          <el-avatar :size="50" :src="appointment?.counselorAvatar">
            <el-icon v-if="!appointment?.counselorAvatar"><User /></el-icon>
          </el-avatar>
          <div class="info-text">
            <h3>{{ appointment?.counselorName }}</h3>
            <p class="status" :class="{ online: isOnline }">
              <span class="status-dot"></span>
              {{ isOnline ? '在线咨询中' : '咨询师离线' }}
            </p>
          </div>
        </div>
        <div class="header-actions">
          <div class="timer">
            <el-icon><Clock /></el-icon>
            <span>{{ formatTime(elapsedTime) }}</span>
          </div>
          <el-button type="danger" plain @click="showEndDialog = true">
            <el-icon><Switch /></el-icon>
            结束咨询
          </el-button>
        </div>
      </div>

      <!-- 消息区域 -->
      <div ref="messagesContainer" class="messages-area">
        <div v-if="messages.length === 0" class="empty-messages">
          <el-empty description="暂无消息，开始您的咨询吧" />
        </div>

        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message"
          :class="{ 'message-self': msg.isSelf }"
        >
          <el-avatar :size="40" :src="msg.isSelf ? currentUserAvatar : appointment?.counselorAvatar">
            <el-icon v-if="!msg.isSelf"><User /></el-icon>
          </el-avatar>

          <div class="message-content">
            <div class="message-sender">{{ msg.isSelf ? '我' : appointment?.counselorName }}</div>

            <!-- 文本消息 -->
            <div v-if="msg.type === 'text'" class="bubble text">
              {{ msg.content }}
            </div>

            <!-- 图片消息 -->
            <div v-else-if="msg.type === 'image'" class="bubble image">
              <el-image
                :src="msg.content"
                fit="cover"
                :preview-src-list="[msg.content]"
                preview-teleported
              />
            </div>

            <!-- 文件消息 -->
            <div v-else-if="msg.type === 'file'" class="bubble file">
              <el-icon><Document /></el-icon>
              <span>{{ msg.fileName || '文件' }}</span>
              <el-button type="primary" link size="small" @click="downloadFile(msg.content)">
                下载
              </el-button>
            </div>

            <div class="message-time">{{ formatMessageTime(msg.createdAt) }}</div>
          </div>
        </div>

        <div v-if="isTyping" class="typing-indicator">
          <span>对方正在输入...</span>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="toolbar">
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileSelect"
            accept="image/*,.pdf,.doc,.docx"
          >
            <el-button :icon="Picture" circle />
          </el-upload>

          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleDocumentSelect"
            accept=".pdf,.doc,.docx,.txt"
          >
            <el-button :icon="Folder" circle />
          </el-upload>
        </div>

        <el-input
          v-model="inputContent"
          type="textarea"
          :rows="3"
          placeholder="输入消息内容..."
          @keydown.enter.exact="sendMessage"
          @keydown.enter.shift.prevent
          :disabled="sending"
        />

        <div class="send-btn">
          <el-button
            type="primary"
            :loading="sending"
            :disabled="!inputContent.trim()"
            @click="sendMessage"
          >
            发送 (Enter)
          </el-button>
        </div>
      </div>
    </div>

    <!-- 结束咨询对话框 -->
    <el-dialog v-model="showEndDialog" title="结束咨询" width="500px">
      <el-alert
        title="提示"
        type="info"
        description="结束咨询后，您可以对本次咨询进行评价，帮助我们改进服务质量。"
        :closable="false"
        show-icon
      />
      <div style="margin-top: 20px;">
        <el-button type="primary" @click="confirmEndConsultation">
          确认结束
        </el-button>
        <el-button @click="showEndDialog = false">继续咨询</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Picture, Folder, Document, User, Clock, Switch } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getMessages, sendMessage as sendMessageAPI, uploadFile, endConsultation, getAppointmentDetail } from '@/api/consultation'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const appointmentId = ref(route.params.id)
const loading = ref(true)
const sending = ref(false)
const isRecording = ref(false)
const isTyping = ref(false)
const isOnline = ref(true)
const elapsedTime = ref(0)
const inputContent = ref('')
const messages = ref([])
const appointment = ref({})
const messagesContainer = ref(null)
const showEndDialog = ref(false)

const currentUserId = computed(() => userStore.user?.id)
const currentUserAvatar = computed(() => userStore.user?.avatar)

let pollingTimer = null
let durationTimer = null

// 格式化时间
const formatTime = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

const formatMessageTime = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 加载预约信息
const loadAppointment = async () => {
  try {
    const res = await getAppointmentDetail(appointmentId.value)
    appointment.value = res.data

    // 根据预约状态判断是否在线
    isOnline.value = ['confirmed', 'in_progress'].includes(appointment.value.status)
  } catch (error) {
    console.error('加载预约信息失败:', error)
    ElMessage.error('加载预约信息失败')
  }
}

// 加载消息（带新消息检测）
const loadMessages = async (lastId = null) => {
  try {
    // 避免首次加载显示loading
    if (messages.value.length === 0) {
      loading.value = true
    }

    const res = await getMessages(appointmentId.value, { lastId })
    const newMessages = res.data.list || []

    if (lastId === null) {
      messages.value = newMessages.map(msg => ({
        id: msg.id,
        content: msg.content,
        type: msg.message_type || 'text',
        isSelf: msg.sender_type === 'user',
        createdAt: msg.created_at,
        fileName: msg.file_name
      }))
    } else {
      const additionalMessages = newMessages.map(msg => ({
        id: msg.id,
        content: msg.content,
        type: msg.message_type || 'text',
        isSelf: msg.sender_type === 'user',
        createdAt: msg.created_at,
        fileName: msg.file_name
      }))

      // 检测咨询师的新消息
      if (messages.value.length > 0 && additionalMessages.length > 0) {
        const lastMsgId = messages.value[messages.value.length - 1].id
        const hasNewMessages = additionalMessages.some(msg => msg.id > lastMsgId && !msg.isSelf)

        if (hasNewMessages) {
          // 播放提示音
          playNotificationSound()
          // 显示浏览器通知
          showBrowserNotification()
        }
      }

      messages.value = [...messages.value, ...additionalMessages]
    }

    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败:', error)
    // 轮询时不显示错误
    if (messages.value.length === 0) {
      ElMessage.error('加载消息失败')
    }
  } finally {
    loading.value = false
  }
}

// 播放提示音
const playNotificationSound = () => {
  try {
    const audio = new Audio('/sounds/notification.mp3')
    audio.volume = 0.5
    audio.play().catch(() => {
      console.log('无法播放提示音')
    })
  } catch (error) {
    console.log('提示音文件不存在')
  }
}

// 显示浏览器通知
const showBrowserNotification = () => {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('新消息', {
      body: '咨询师回复了您的消息',
      icon: '/logo.png',
      tag: 'consultation-message'
    })
  }
}

// 请求通知权限
const requestNotificationPermission = async () => {
  if ('Notification' in window && Notification.permission === 'default') {
    await Notification.requestPermission()
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputContent.value.trim() || sending.value) return

  const content = inputContent.value.trim()
  inputContent.value = ''

  // 乐观更新
  const tempMsg = {
    id: Date.now(),
    content: content,
    type: 'text',
    isSelf: true,
    createdAt: new Date().toISOString()
  }
  messages.value.push(tempMsg)
  scrollToBottom()

  try {
    sending.value = true
    await sendMessageAPI(appointmentId.value, {
      content: content,
      type: 'text'
    })

    // 重新加载消息
    await loadMessages()
  } catch (error) {
    console.error('发送失败:', error)
    ElMessage.error(error.response?.data?.detail || '发送失败')

    // 发送失败，移除临时消息
    const index = messages.value.findIndex(m => m.id === tempMsg.id)
    if (index !== -1) {
      messages.value.splice(index, 1)
    }
  } finally {
    sending.value = false
  }
}

// 处理图片上传
const handleFileSelect = async (file) => {
  if (!file) return

  const isImage = file.raw.type.startsWith('image/')
  const tempMsg = {
    id: Date.now(),
    content: '',
    type: isImage ? 'image' : 'file',
    fileName: file.name,
    isSelf: true,
    createdAt: new Date().toISOString()
  }
  messages.value.push(tempMsg)
  scrollToBottom()

  try {
    sending.value = true

    // 上传文件
    const uploadRes = await uploadFile(file.raw)
    const fileUrl = uploadRes.data?.url || uploadRes.url

    // 发送文件消息
    await sendMessageAPI(appointmentId.value, {
      content: fileUrl,
      type: isImage ? 'image' : 'file'
    })

    await loadMessages()
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败')

    const index = messages.value.findIndex(m => m.id === tempMsg.id)
    if (index !== -1) {
      messages.value.splice(index, 1)
    }
  } finally {
    sending.value = false
  }
}

// 处理文档上传
const handleDocumentSelect = async (file) => {
  if (!file) return
  handleFileSelect(file)
}

// 下载文件
const downloadFile = (url) => {
  window.open(url, '_blank')
}

// 结束咨询
const confirmEndConsultation = async () => {
  try {
    await endConsultation(appointmentId.value)
    ElMessage.success('咨询已结束')

    showEndDialog.value = false

    // 跳转到评价页面
    router.push({
      path: '/consultation/review',
      query: { appointmentId: appointmentId.value }
    })
  } catch (error) {
    console.error('结束咨询失败:', error)
    ElMessage.error('操作失败')
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 启动轮询
const startPolling = () => {
  // 每3秒轮询一次
  pollingTimer = setInterval(() => {
    if (!sending.value) {
      loadMessages()
    }
  }, 3000)
}

// 启动计时器
const startTimer = () => {
  durationTimer = setInterval(() => {
    elapsedTime.value++
  }, 1000)
}

onMounted(async () => {
  console.log('User chat - Appointment ID:', appointmentId.value)

  await loadAppointment()
  await loadMessages()
  await requestNotificationPermission()

  startPolling()
  startTimer()
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
  if (durationTimer) clearInterval(durationTimer)
})
</script>

<style scoped>
.consultation-chat-user {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
  gap: 16px;
}

/* 聊天头部 */
.chat-header {
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #2c3e50;
}

.status {
  margin: 0;
  font-size: 14px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
}

.status.online .status-dot {
  background: #67c23a;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.timer {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}

/* 消息区域 */
.messages-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  overflow-y: auto;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.empty-messages {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.message-self {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 60%;
}

.sender {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.message:not(.message-self) .sender {
  text-align: left;
}

.message.message-self .sender {
  text-align: right;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  word-break: break-word;
}

.message:not(.message-self) .bubble {
  background: #f4f4f5;
  border-bottom-left-radius: 4px;
}

.message.message-self .bubble {
  background: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.bubble.image {
  padding: 8px;
}

.bubble.image :deep(.el-image) {
  max-width: 300px;
  border-radius: 8px;
}

.bubble.file {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

.message.message-self .time {
  text-align: right;
}

.typing-indicator {
  text-align: center;
  padding: 10px;
  color: #909399;
  font-size: 14px;
}

/* 输入区域 */
.input-area {
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.send-btn {
  margin-top: 12px;
  text-align: right;
}

/* 响应式 */
@media (max-width: 768px) {
  .chat-container {
    padding: 12px;
  }

  .message-content {
    max-width: 80%;
  }
}

.typing-indicator {
  text-align: center;
  padding: 10px;
  color: #909399;
  font-size: 14px;
}
</style>
