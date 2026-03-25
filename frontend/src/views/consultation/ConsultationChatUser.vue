<template>
  <div class="consultation-chat-user">
    <PageHeader />
    <div v-loading="loading" class="chat-container">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-info">
          <el-avatar :size="50" :src="appointment?.counselorAvatar" />
          <div class="info-text">
            <h3>{{ appointment?.counselorName }}</h3>
            <p class="status" :class="{ online: isOnline }">
              {{ isOnline ? '在线咨询中' : '暂不在线' }}
            </p>
          </div>
        </div>
        <div class="header-actions">
          <div class="timer">
            <el-icon><Timer /></el-icon>
            <span>{{ formatDuration(elapsedTime) }}</span>
          </div>
          <el-button type="danger" plain @click="handleEndConsultation">结束咨询</el-button>
        </div>
      </div>

      <!-- 消息区域 -->
      <div ref="messagesContainer" class="messages-area">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message"
          :class="{ 'message-self': msg.senderId === currentUserId }"
        >
          <el-avatar :size="40" :src="msg.senderId === currentUserId ? currentUserAvatar : appointment?.counselorAvatar" />
          <div class="message-content">
            <div class="message-sender">{{ msg.senderId === currentUserId ? '我' : appointment?.counselorName }}</div>
            <div v-if="msg.type === 'text'" class="message-bubble">{{ msg.content }}</div>
            <div v-else-if="msg.type === 'image'" class="message-image">
              <el-image :src="msg.content" fit="cover" :preview-src-list="[msg.content]" />
            </div>
            <div v-else-if="msg.type === 'file'" class="message-file">
              <el-icon><Document /></el-icon>
              <span>{{ getFileName(msg.content) }}</span>
              <el-button type="primary" link @click="downloadFile(msg.content)">下载</el-button>
            </div>
            <div class="message-time">{{ formatTime(msg.createdAt) }}</div>
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
            :show-file-list="false"
            :before-upload="handleUploadImage"
            accept="image/*"
          >
            <el-button :icon="Picture" circle />
          </el-upload>
          <el-upload
            :show-file-list="false"
            :before-upload="handleUploadFile"
          >
            <el-button :icon="Folder" circle />
          </el-upload>
          <el-button :icon="Microphone" circle @click="toggleVoiceRecording" :type="isRecording ? 'danger' : ''" />
        </div>

        <div class="input-box">
          <el-input
            v-model="inputContent"
            type="textarea"
            :rows="3"
            placeholder="输入消息内容..."
            @keydown.enter.ctrl="sendMessage"
          />
          <el-button type="primary" :loading="sending" @click="sendMessage">
            发送 (Ctrl+Enter)
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Picture, Folder, Microphone, Document } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
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
const messagesContainer = ref(null)

const currentUserId = computed(() => userStore.user?.id)
const currentUserAvatar = computed(() => userStore.user?.avatar)

let pollingTimer = null
let durationTimer = null

const loadAppointment = async () => {
  // 加载预约信息
  appointment.value = {
    counselorName: '张老师',
    counselorAvatar: '',
    status: 'inprogress'
  }
}

const loadMessages = async (lastId = null) => {
  try {
    const res = await getMessages(appointmentId, { lastId })
    const newMessages = res.data.list || []

    if (lastId === null) {
      messages.value = newMessages
    } else {
      messages.value = [...messages.value, ...newMessages]
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
    await sendMessageApi(appointmentId, {
      content: inputContent.value,
      type: 'text'
    })
    inputContent.value = ''
    await loadMessages()
  } catch (error) {
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

const handleEndConsultation = async () => {
  try {
    await ElMessageBox.confirm('确定要结束本次咨询吗？', '提示', { type: 'warning' })
    await endConsultation(appointmentId)
    ElMessage.success('咨询已结束')
    router.push('/counselor/orders')
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
  }
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
  if (durationTimer) clearInterval(durationTimer)
})
</script>

<style scoped>
@use '@/styles/variables.scss' as *;
.consultation-chat-user { height: 100vh; display: flex; flex-direction: column; background: $bg-color; }
.chat-container { flex: 1; display: flex; flex-direction: column; max-width: 1000px; margin: 0 auto; width: 100%; background: white; box-shadow: $shadow; }

.chat-header { padding: $spacing-lg; border-bottom: 1px solid $border-color; display: flex; justify-content: space-between; align-items: center; }
.header-info { display: flex; align-items: center; gap: $spacing-md; }
.header-info h3 { margin: 0 0 $spacing-xs; }
.header-info .status { font-size: 12px; color: $text-secondary; }
.header-info .status.online { color: $success-color; }
.header-actions { display: flex; align-items: center; gap: $spacing-lg; }
.timer { display: flex; align-items: center; gap: $spacing-xs; color: $primary-color; font-weight: 500; }

.messages-area { flex: 1; padding: $spacing-lg; overflow-y: auto; background: #f5f7fa; }
.message { display: flex; gap: $spacing-md; margin-bottom: $spacing-lg; }
.message.message-self { flex-direction: row-reverse; }
.message-content { max-width: 60%; }
.message-sender { font-size: 12px; color: $text-secondary; margin-bottom: $spacing-xs; }
.message-bubble { padding: $spacing-md; background: white; border-radius: $border-radius; word-break: break-word; }
.message.message-self .message-bubble { background: $primary-color; color: white; }
.message-image :deep(.el-image) { max-width: 200px; border-radius: $border-radius; }
.message-file { display: flex; align-items: center; gap: $spacing-sm; padding: $spacing-md; background: white; border-radius: $border-radius; }
.message-time { font-size: 12px; color: $text-secondary; margin-top: $spacing-xs; }
.message.message-self .message-time { text-align: right; }

.typing-indicator { text-align: center; color: $text-secondary; font-size: 12px; padding: $spacing-md; }

.input-area { border-top: 1px solid $border-color; padding: $spacing-lg; background: white; }
.toolbar { display: flex; gap: $spacing-sm; margin-bottom: $spacing-md; }
.input-box { display: flex; gap: $spacing-md; align-items: flex-end; }
.input-box .el-textarea { flex: 1; }
</style>
