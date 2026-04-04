<template>
  <div class="consultation-chat-counselor">
    <PageHeader />
    <div v-loading="loading" class="chat-container">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="header-info">
          <el-avatar :size="50" :src="appointment?.userAvatar" />
          <div class="info-text">
            <h3>{{ appointment?.userName }}</h3>
            <p class="appointment-info">{{ appointment?.date }} {{ appointment?.timeSlot }}</p>
          </div>
        </div>
        <div class="header-actions">
          <div class="timer">
            <el-icon><Timer /></el-icon>
            <span>{{ formatDuration(elapsedTime) }}</span>
          </div>
          <el-dropdown @command="handleMenuCommand">
            <el-button type="primary" plain>
              更多操作 <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="note">添加备注</el-dropdown-item>
                <el-dropdown-item command="history">历史记录</el-dropdown-item>
                <el-dropdown-item command="end" divided>结束咨询</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 用户信息摘要 -->
      <el-collapse v-model="activeInfo" class="user-info-panel">
        <el-collapse-item title="用户信息" name="info">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">问题描述:</span>
              <p>{{ appointment?.description || '暂无' }}</p>
            </div>
            <div class="info-item">
              <span class="label">咨询方式:</span>
              <p>{{ getTypeText(appointment?.type) }}</p>
            </div>
            <div class="info-item">
              <span class="label">历史咨询:</span>
              <p>{{ appointment?.historyCount || 0 }} 次</p>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>

      <!-- 消息区域 -->
      <div ref="messagesContainer" class="messages-area">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="message"
          :class="{ 'message-self': msg.senderId === currentUserId }"
        >
          <el-avatar :size="40" :src="msg.senderId === currentUserId ? currentAvatar : appointment?.userAvatar" />
          <div class="message-content">
            <div class="message-sender">{{ msg.senderId === currentUserId ? '我' : appointment?.userName }}</div>
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

      <!-- 快捷回复 -->
      <div v-if="showQuickReplies" class="quick-replies">
        <div class="quick-title">快捷回复:</div>
        <div class="quick-buttons">
          <el-button
            v-for="(reply, index) in quickReplies"
            :key="index"
            size="small"
            @click="inputContent = reply"
          >
            {{ reply }}
          </el-button>
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
          <el-button :icon="ChatDotRound" circle @click="showQuickReplies = !showQuickReplies" />
        </div>

        <div class="input-box">
          <el-input
            v-model="inputContent"
            type="textarea"
            :rows="3"
            placeholder="输入回复内容..."
            @keydown.enter.ctrl="sendMessage"
          />
          <el-button type="primary" :loading="sending" @click="sendMessage">
            发送 (Ctrl+Enter)
          </el-button>
        </div>
      </div>
    </div>

    <!-- 备注对话框 -->
    <el-dialog v-model="noteDialogVisible" title="添加咨询备注" width="500px">
      <el-input
        v-model="noteContent"
        type="textarea"
        :rows="5"
        placeholder="记录本次咨询的关键信息、观察结果、建议等..."
      />
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNote">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, ArrowDown, Picture, Folder, Microphone, Document, ChatDotRound } from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getMessages, sendMessage as sendMessageApi, uploadFile, endConsultation, addConsultationNote } from '@/api/consultation'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const appointmentId = route.params.id
const loading = ref(true)
const sending = ref(false)
const isRecording = ref(false)
const isTyping = ref(false)
const elapsedTime = ref(0)
const inputContent = ref('')
const messages = ref([])
const appointment = ref({})
const activeInfo = ref(['info'])
const showQuickReplies = ref(false)
const noteDialogVisible = ref(false)
const noteContent = ref('')
const messagesContainer = ref(null)

const currentUserId = userStore.user?.id
const currentAvatar = userStore.user?.avatar

const quickReplies = [
  '您好，我已准备好，请开始讲述您的情况。',
  '我理解您的感受，能详细说说吗？',
  '这个问题很重要，我们深入探讨一下。',
  '您的进步很明显，继续保持！',
  '今天的咨询时间差不多了，总结一下我们讨论的内容。'
]

let pollingTimer = null
let durationTimer = null

const loadAppointment = async () => {
  // 加载预约信息
  appointment.value = {
    userName: '李同学',
    userAvatar: '',
    date: '2026-02-26',
    timeSlot: '14:00-15:00',
    type: 'video',
    description: '最近感到压力很大，睡眠不好，希望得到帮助。',
    historyCount: 2
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

const handleMenuCommand = async (command) => {
  switch (command) {
    case 'note':
      noteDialogVisible.value = true
      break
    case 'history':
      ElMessage.info('查看历史记录功能开发中')
      break
    case 'end':
      await handleEndConsultation()
      break
  }
}

const saveNote = async () => {
  try {
    await addConsultationNote(appointmentId, { note: noteContent.value })
    ElMessage.success('备注已保存')
    noteDialogVisible.value = false
    noteContent.value = ''
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const handleEndConsultation = async () => {
  try {
    await ElMessageBox.confirm('确定要结束本次咨询吗？', '提示', { type: 'warning' })
    await endConsultation(appointmentId)
    ElMessage.success('咨询已结束')
    router.push('/consultation/counselor/orders')
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
.consultation-chat-counselor { height: 100vh; display: flex; flex-direction: column; background: $bg-color; }
.chat-container { flex: 1; display: flex; flex-direction: column; max-width: 1000px; margin: 0 auto; width: 100%; background: white; box-shadow: $shadow; }

.chat-header { padding: $spacing-lg; border-bottom: 1px solid $border-color; display: flex; justify-content: space-between; align-items: center; }
.header-info { display: flex; align-items: center; gap: $spacing-md; }
.header-info h3 { margin: 0 0 $spacing-xs; }
.appointment-info { font-size: 12px; color: $text-secondary; }
.header-actions { display: flex; align-items: center; gap: $spacing-lg; }
.timer { display: flex; align-items: center; gap: $spacing-xs; color: $primary-color; font-weight: 500; }

.user-info-panel { border-bottom: 1px solid $border-color; }
.info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: $spacing-lg; padding: $spacing-md; }
.info-item .label { font-weight: 500; color: $text-secondary; }
.info-item p { margin: $spacing-xs 0 0; }

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

.quick-replies { padding: $spacing-md; background: #f0f9ff; border-top: 1px solid $border-color; }
.quick-title { font-size: 12px; color: $text-secondary; margin-bottom: $spacing-sm; }
.quick-buttons { display: flex; flex-wrap: wrap; gap: $spacing-sm; }

.input-area { border-top: 1px solid $border-color; padding: $spacing-lg; background: white; }
.toolbar { display: flex; gap: $spacing-sm; margin-bottom: $spacing-md; }
.input-box { display: flex; gap: $spacing-md; align-items: flex-end; }
.input-box .el-textarea { flex: 1; }
</style>
