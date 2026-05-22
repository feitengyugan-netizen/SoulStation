<template>
  <div class="modern-chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <div class="header-left">
        <el-button circle @click="goBack" class="back-btn">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <div class="user-info">
          <el-avatar :size="45" :src="appointment?.userAvatar" class="user-avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="user-details">
            <h3 class="user-name">{{ appointment?.userName || '用户' }}</h3>
            <div class="status-info">
              <span class="online-dot"></span>
              <span class="status-text">{{ isOnline ? '在线咨询中' : '离线' }}</span>
            </div>
          </div>
        </div>
<<<<<<< Updated upstream
=======
        <div class="header-actions">
          <VideoCallButton
            :appointment-id="Number(appointmentId)"
            :can-call="canStartCall"
            @call-started="handleCallStarted"
          />
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
>>>>>>> Stashed changes
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
                <el-icon><User /></el-icon> 用户信息
              </el-dropdown-item>
              <el-dropdown-item command="note">
                <el-icon><Edit /></el-icon> 添加备注
              </el-dropdown-item>
              <el-dropdown-item command="history">
                <el-icon><Clock /></el-icon> 咨询记录
              </el-dropdown-item>
              <el-dropdown-item command="end" divided>
                <el-icon><SwitchButton /></el-icon> 结束咨询
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 用户信息面板（可展开） -->
    <el-collapse-transition>
      <div v-show="showUserInfo" class="user-info-panel">
        <el-card>
          <template #header>
            <div class="panel-header">
              <span>用户详细信息</span>
              <el-button text @click="showUserInfo = false">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="info-content">
            <div class="info-item">
              <span class="label">问题描述：</span>
              <p>{{ appointment?.description || '暂无描述' }}</p>
            </div>
            <div class="info-item">
              <span class="label">咨询方式：</span>
              <el-tag>{{ getTypeText(appointment?.type) }}</el-tag>
            </div>
            <div class="info-item">
              <span class="label">咨询时长：</span>
              <span>{{ appointment?.duration || 60 }}分钟</span>
            </div>
            <div class="info-item">
              <span class="label">历史咨询：</span>
              <span>{{ appointment?.historyCount || 0 }}次</span>
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
          :class="{ 'message-self': msg.senderType === 'counselor' }"
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
              <span v-if="msg.senderType === 'counselor'" class="read-status">
                {{ msg.isRead ? '已读' : '未读' }}
              </span>
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
          <span>对方正在输入...</span>
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
      <!-- 快捷回复 -->
      <div v-if="showQuickReplies" class="quick-replies">
        <div class="replies-scroll">
          <el-button
            v-for="(reply, index) in quickReplies"
            :key="index"
            size="small"
            @click="inputContent = reply"
            class="reply-btn"
          >
            {{ reply }}
          </el-button>
        </div>
      </div>

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
          <el-button circle @click="toggleQuickReplies">
            <el-icon><MagicStick /></el-icon>
          </el-button>
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

    <!-- 备注对话框 -->
    <el-dialog v-model="noteDialogVisible" title="添加咨询备注" width="500px">
      <el-input
        v-model="noteContent"
        type="textarea"
        :rows="6"
        placeholder="记录本次咨询的关键信息、观察结果、建议等..."
      />
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNote">保存</el-button>
      </template>
    </el-dialog>

    <!-- 视频通话对话框 -->
    <el-dialog
      v-model="callDialogVisible"
      title="视频通话"
      width="800px"
      :close-on-click-modal="false"
      @close="handleCallEnded"
    >
      <VideoCallRoom
        v-if="callDialogVisible"
        :appointment-id="Number(appointmentId)"
        :session-id="currentCallSessionId"
        :is-initiator="true"
        @close="callDialogVisible = false"
        @call-ended="handleCallEnded"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Timer, User, ArrowLeft, MoreFilled, Edit, Clock, SwitchButton,
  Close, Picture, Folder, Microphone, ChatDotRound, Document,
  Download, MagicStick, Promotion
} from '@element-plus/icons-vue'
import { getMessages, sendMessage as sendMessageApi, uploadFile, endConsultation, addConsultationNote, getCounselorOrders } from '@/api/consultation'
import { useUserStore } from '@/stores/user'
import VideoCallButton from '@/components/VideoCall/VideoCallButton.vue'
import VideoCallRoom from '@/components/VideoCall/VideoCallRoom.vue'

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
const showUserInfo = ref(false)
const showQuickReplies = ref(false)
const noteDialogVisible = ref(false)
const noteContent = ref('')
const messagesContainer = ref(null)

<<<<<<< Updated upstream
// 咨询师端：当前登录的用户ID需要通过counselor表获取对应的counselor_id
const currentUserId = ref(null)
const currentAvatar = ref(userStore.user?.avatar)

// 从API获取当前咨询师的counselor_id
const getCurrentCounselorId = async () => {
  try {
    const res = await getCounselorOrders({ page: 1, pageSize: 1 })
    if (res.code === 200 && res.data.items && res.data.items.length > 0) {
      // 从第一个订单中获取counselor_id（因为都是当前咨询师的订单）
      currentUserId.value = res.data.items[0].counselor_id
      console.log('当前咨询师ID:', currentUserId.value)
    }
  } catch (error) {
    console.error('获取咨询师ID失败:', error)
  }
}
=======
// 视频通话相关
const callDialogVisible = ref(false)
const currentCallSessionId = ref(null)

const currentUserId = userStore.user?.id
const currentAvatar = userStore.user?.avatar
>>>>>>> Stashed changes

const quickReplies = [
  '您好，我已准备好，请开始讲述您的情况。',
  '我理解您的感受，能详细说说吗？',
  '这个问题很重要，我们深入探讨一下。',
  '您的进步很明显，继续保持！',
  '今天的咨询时间差不多了，总结一下我们讨论的内容。'
]

let pollingTimer = null
let durationTimer = null

const goBack = () => {
  router.push('/consultation/counselor/orders')
}

const loadAppointment = async () => {
  try {
    // 从订单列表API获取当前咨询师的所有订单，找到对应的订单
    const res = await getCounselorOrders({ page: 1, pageSize: 100 })
    if (res.code === 200 && res.data) {
      const orders = res.data.items || []
      const currentOrder = orders.find(o => o.id === parseInt(appointmentId))

      if (currentOrder) {
        appointment.value = {
          userName: currentOrder.user_name || '未知用户',
          userAvatar: '',
          type: currentOrder.consultation_type,
          description: currentOrder.problem_description || '暂无描述',
          duration: currentOrder.duration,
          historyCount: 0
        }
      } else {
        ElMessage.error('未找到该订单或无权访问')
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
        isSelf: msg.sender_type === 'counselor'
      })
      return processed
    })

    console.log('当前咨询师ID:', currentUserId.value)
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

const toggleQuickReplies = () => {
  showQuickReplies.value = !showQuickReplies.value
}

const toggleVoiceRecording = () => {
  isRecording.value = !isRecording.value
  ElMessage.info(isRecording.value ? '开始录音' : '停止录音')
}

const handleMenuCommand = async (command) => {
  switch (command) {
    case 'info':
      showUserInfo.value = !showUserInfo.value
      break
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
    goBack()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('操作失败')
  }
}

// 视频通话相关方法
const canStartCall = computed(() => {
  // 只有 confirmed 或 in_progress 状态的预约才能发起通话
  return appointment.value?.status === 'confirmed' || appointment.value?.status === 'in_progress'
})

const handleCallStarted = ({ sessionId, callType }) => {
  currentCallSessionId.value = sessionId
  callDialogVisible.value = true
}

const handleCallEnded = () => {
  callDialogVisible.value = false
  currentCallSessionId.value = null
  ElMessage.success('通话已结束')
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
    await getCurrentCounselorId()  // 先获取咨询师ID
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
.modern-chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
}

/* 头部样式 */
.chat-header {
  background: white;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  margin-right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.online-dot {
  width: 8px;
  height: 8px;
  background: #67c23a;
  border-radius: 50%;
}

.status-text {
  color: #909399;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409eff;
  font-weight: 500;
}

/* 用户信息面板 */
.user-info-panel {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.info-content {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item .label {
  font-size: 12px;
  color: #909399;
  font-weight: 500;
}

.info-item p {
  margin: 0;
  color: #303133;
  line-height: 1.5;
}

/* 消息区域 */
.messages-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.messages-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-wrapper {
  display: flex;
  width: 100%;
}

.message-wrapper.message-self {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 60%;
  padding: 10px 14px;
  border-radius: 12px;
  position: relative;
  word-wrap: break-word;
}

.message-wrapper:not(.message-self) .message-bubble {
  background: white;
  border-bottom-left-radius: 2px;
}

.message-wrapper.message-self .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 2px;
}

.message-text {
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 4px;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 6px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.read-status {
  font-size: 10px;
}

.message-image :deep(.el-image) {
  max-width: 200px;
  border-radius: 8px;
}

.message-file {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.file-name {
  flex: 1;
  font-size: 13px;
}

/* 正在输入 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 12px;
  color: #909399;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 6px;
  height: 6px;
  background: #909399;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

/* 空状态 */
.empty-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

/* 输入区域 */
.input-container {
  background: white;
  border-top: 1px solid #e4e7ed;
}

.quick-replies {
  padding: 8px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.replies-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 4px 0;
}

.reply-btn {
  flex-shrink: 0;
  white-space: nowrap;
}

.input-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 8px 16px 16px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 8px;
  resize: none;
}

.send-btn {
  height: auto;
  padding: 10px 20px;
  border-radius: 8px;
}

/* 响应式 */
@media (max-width: 768px) {
  .info-content {
    grid-template-columns: 1fr;
  }

  .message-bubble {
    max-width: 80%;
  }
}
</style>