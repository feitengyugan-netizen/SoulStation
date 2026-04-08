<template>
  <div class="consultation-chat-counselor">
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
          :class="{ 'message-self': msg.sender_type === 'counselor' }"
        >
          <el-avatar :size="40" :src="msg.sender_type === 'counselor' ? currentAvatar : appointment?.userAvatar" />
          <div class="message-content">
            <div class="message-sender">{{ msg.sender_type === 'counselor' ? '我' : appointment?.userName }}</div>
            <div v-if="msg.message_type === 'text'" class="message-bubble">{{ msg.content }}</div>
            <div v-else-if="msg.message_type === 'image'" class="message-image">
              <el-image :src="msg.content" fit="cover" :preview-src-list="[msg.content]" />
            </div>
            <div v-else-if="msg.message_type === 'file'" class="message-file">
              <el-icon><Document /></el-icon>
              <span>{{ getFileName(msg.content) }}</span>
              <el-button type="primary" link @click="downloadFile(msg.content)">下载</el-button>
            </div>
            <div class="message-time">{{ formatTime(msg.created_at) }}</div>
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
import { getMessages, sendMessage as sendMessageApi, uploadFile, endConsultation, addConsultationNote, getCounselorOrders } from '@/api/consultation'
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
  try {
    loading.value = true

    // 获取咨询师的所有订单，然后找到当前订单
    const res = await getCounselorOrders({ page: 1, page_size: 100 })
    const orders = res.data.items || []
    const currentOrder = orders.find(o => o.id == appointmentId)

    if (currentOrder) {
      // 格式化预约数据
      appointment.value = {
        id: currentOrder.id,
        appointmentNo: currentOrder.appointment_no,
        userName: currentOrder.user_name || '用户',
        userAvatar: currentOrder.user_info?.avatar || '',
        date: formatDate(currentOrder.appointment_date),
        timeSlot: formatTimeSlot(currentOrder.appointment_date, currentOrder.duration),
        type: currentOrder.consultation_type,
        description: currentOrder.problem_description || '暂无描述',
        status: currentOrder.status,
        historyCount: 0,
        price: currentOrder.price,
        counselor: currentOrder.counselor,
        userInfo: currentOrder.user_info
      }

      // 更新页面标题
      document.title = `与${appointment.value.userName}的咨询 - SoulStation`
    } else {
      throw new Error('订单不存在')
    }
  } catch (error) {
    console.error('加载预约信息失败', error)
    ElMessage.error('加载预约信息失败')
    // 保留默认数据以便调试
    appointment.value = {
      userName: '用户',
      userAvatar: '',
      date: '待定',
      timeSlot: '待定',
      type: 'video',
      description: '无法加载预约信息',
      status: 'unknown'
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const formatTimeSlot = (dateStr, duration) => {
  if (!dateStr) return '待定'
  const d = new Date(dateStr)
  const startTime = `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  const endDate = new Date(d.getTime() + duration * 60000)
  const endTime = `${String(endDate.getHours()).padStart(2, '0')}:${String(endDate.getMinutes()).padStart(2, '0')}`
  return `${startTime}-${endTime}`
}

const loadMessages = async (lastId = null) => {
  try {
    const res = await getMessages(appointmentId, { lastId })
    const newMessages = res.data.items || []

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
      message_type: 'text'
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
      message_type: 'image'
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
      message_type: 'file'
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


<style lang="scss" scoped>
@use "@/styles/variables.scss" as *;

.consultation-chat-counselor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: $bg-page;
  padding-top: $header-height;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  background: $bg-white;
  box-shadow: 0 4px 32px rgba(107,82,68,0.1);
  border-radius: 20px;
  overflow: hidden;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid $border-lighter;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: $bg-white;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 14px;

  h3 { margin: 0 0 2px; font-weight: 700; color: $text-primary; }
  .status { font-size: 12px; color: $text-secondary; }
  .status.online { color: #52c41a; }
  .appointment-info { font-size: 12px; color: $text-secondary; }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.timer {
  display: flex;
  align-items: center;
  gap: 6px;
  color: $primary-color;
  font-weight: 600;
  background: rgba(232,132,90,0.1);
  padding: 4px 14px;
  border-radius: 999px;
  font-size: 14px;
}

.messages-area {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: $bg-page;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;

  &.message-self {
    flex-direction: row-reverse;

    .message-bubble {
      background: linear-gradient(135deg, #f4a57a 0%, #c96f42 100%);
      color: white;
      border-radius: 18px 4px 18px 18px;
    }

    .message-time { text-align: right; }
  }
}

.message-content { max-width: 60%; }
.message-sender { font-size: 12px; color: $text-secondary; margin-bottom: 4px; }

.message-bubble {
  padding: 12px 16px;
  background: $bg-white;
  border-radius: 4px 18px 18px 18px;
  word-break: break-word;
  border: 1px solid $border-lighter;
  box-shadow: 0 2px 8px rgba(107,82,68,0.06);
  line-height: 1.65;
}

.message-image :deep(.el-image) { max-width: 200px; border-radius: 12px; }

.message-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: $bg-white;
  border-radius: 12px;
  border: 1px solid $border-lighter;
}

.message-time { font-size: 11px; color: $text-secondary; margin-top: 4px; }

.typing-indicator {
  text-align: center;
  color: $text-secondary;
  font-size: 12px;
  padding: 12px;
}

.input-area {
  border-top: 1px solid $border-lighter;
  padding: 16px 24px;
  background: $bg-white;
}

.toolbar { display: flex; gap: 8px; margin-bottom: 12px; }

.input-box {
  display: flex;
  gap: 12px;
  align-items: flex-end;

  :deep(.el-textarea) { flex: 1; }
}

.user-info-panel {
  border-bottom: 1px solid $border-lighter;
  background: rgba(232,132,90,0.04);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 16px 24px;
}

.info-item {
  .label { font-weight: 500; color: $text-secondary; font-size: 12px; }
  p { margin: 4px 0 0; color: $text-primary; font-weight: 500; }
}

.quick-replies {
  padding: 14px 24px;
  background: rgba(155,139,180,0.06);
  border-top: 1px solid $border-lighter;
}

.quick-title { font-size: 12px; color: $text-secondary; margin-bottom: 8px; }
.quick-buttons { display: flex; flex-wrap: wrap; gap: 8px; }

</style>
