<template>
  <div class="consultation-chat">
    <PageHeader />

    <div v-loading="loading" element-loading-text="加载中..." class="chat-wrapper">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <div class="user-info">
          <el-avatar :size="48" :src="userData.avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <div class="info">
            <h3>{{ userData.name }}</h3>
            <p class="status" :class="{ online: userData.online }">
              <span class="dot"></span>
              {{ userData.online ? '在线' : '离线' }}
            </p>
          </div>
        </div>

        <div class="actions">
          <div class="timer">
            <el-icon><Clock /></el-icon>
            <span>{{ formatTime(elapsedTime) }}</span>
          </div>
          <el-button-group>
            <el-tooltip content="添加备注">
              <el-button :icon="Edit" @click="showNoteDialog = true" />
            </el-tooltip>
            <el-tooltip content="结束咨询">
              <el-button type="danger" :icon="Switch" @click="showEndDialog = true" />
            </el-tooltip>
          </el-button-group>
        </div>
      </div>

      <!-- 消息列表 -->
      <div ref="messagesRef" class="messages-list">
        <div v-if="messages.length === 0" class="empty-messages">
          <el-empty description="暂无消息，开始咨询吧" />
        </div>

        <div v-for="msg in messages" :key="msg.id" class="message-item" :class="{ self: msg.isSelf }">
          <el-avatar :size="40" :src="msg.isSelf ? counselorAvatar : userData.avatar">
            <el-icon v-if="!msg.isSelf"><User /></el-icon>
          </el-avatar>

          <div class="message-content">
            <div class="sender">{{ msg.isSelf ? '我' : userData.name }}</div>

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

            <div class="time">{{ formatMessageTime(msg.createdAt) }}</div>
          </div>
        </div>
      </div>

      <!-- 快捷回复 -->
      <div v-if="showQuickReplies" class="quick-replies">
        <div class="quick-header">
          <span>快捷回复</span>
          <el-button text size="small" @click="showQuickReplies = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <div class="quick-list">
          <el-button
            v-for="(reply, i) in quickReplies"
            :key="i"
            size="small"
            @click="sendQuickReply(reply)"
          >
            {{ reply }}
          </el-button>
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

          <el-button :icon="Folder" circle @click="showQuickReplies = !showQuickReplies" />

          <el-tooltip content="素材库">
            <el-button :icon="Document" circle @click="showMaterialLibrary = true" />
          </el-tooltip>
        </div>

        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="输入消息..."
          @keydown.enter.exact="sendMessage"
          @keydown.enter.shift.prevent
          :disabled="sending"
        />

        <div class="send-btn">
          <el-button
            type="primary"
            :loading="sending"
            :disabled="!inputText.trim()"
            @click="sendMessage"
          >
            发送 (Enter)
          </el-button>
        </div>
      </div>
    </div>

    <!-- 结束咨询对话框 -->
    <el-dialog v-model="showEndDialog" title="结束咨询" width="500px">
      <el-form :model="endForm" label-width="80px">
        <el-form-item label="咨询总结">
          <el-input v-model="endForm.summary" type="textarea" :rows="4" placeholder="请总结本次咨询的主要内容..." />
        </el-form-item>
        <el-form-item label="后续建议">
          <el-input v-model="endForm.suggestions" type="textarea" :rows="3" placeholder="请给来访者提供建议..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEndDialog = false">取消</el-button>
        <el-button type="primary" @click="endConsultation">确认结束</el-button>
      </template>
    </el-dialog>

    <!-- 添加备注对话框 -->
    <el-dialog v-model="showNoteDialog" title="添加咨询备注" width="600px">
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="备注类型">
          <el-select v-model="noteForm.type" placeholder="选择备注类型">
            <el-option
              v-for="type in noteTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注内容">
          <el-input
            v-model="noteForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入备注内容..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showNoteDialog = false">取消</el-button>
        <el-button type="primary" @click="saveNote">保存备注</el-button>
      </template>
    </el-dialog>

    <!-- 素材库对话框 -->
    <el-dialog v-model="showMaterialLibrary" title="素材库" width="800px" top="5vh">
      <el-tabs>
        <el-tab-pane
          v-for="category in materialLibrary"
          :key="category.category"
          :label="category.category"
        >
          <div class="material-list">
            <el-card
              v-for="(template, idx) in category.templates"
              :key="idx"
              class="material-item"
              shadow="hover"
              @click="useMaterial(template)"
            >
              {{ template }}
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User, Clock, Picture, Folder, Document, Switch, Close, Edit
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getMessages, sendMessage as sendMessageAPI, uploadFile, endConsultation as endConsultationAPI } from '@/api/consultation'

const route = useRoute()
const router = useRouter()

const appointmentId = ref(route.params.id)
const loading = ref(true)
const sending = ref(false)
const messagesRef = ref(null)
const inputText = ref('')
const messages = ref([])
const elapsedTime = ref(0)
const showQuickReplies = ref(false)
const showEndDialog = ref(false)
const showNoteDialog = ref(false)
const showMaterialLibrary = ref(false)
const endForm = ref({ summary: '', suggestions: '' })
const noteForm = ref({
  type: 'observation',
  content: ''
})

const noteTypes = [
  { label: '观察记录', value: 'observation' },
  { label: '评估分析', value: 'assessment' },
  { label: '干预建议', value: 'suggestion' },
  { label: '其他备注', value: 'other' }
]

// 素材库（预设回复模板）
const materialLibrary = ref([
  { category: '开场', templates: [
    '您好，我是您的咨询师，很高兴为您服务。',
    '今天我们可以聊聊什么话题？',
    '感觉最近怎么样？有什么想聊的吗？'
  ]},
  { category: '共情', templates: [
    '我理解您的感受，这确实不容易。',
    '听起来您经历了很大的压力。',
    '您的感受是完全可以理解的。'
  ]},
  { category: '引导', templates: [
    '能多说说这方面的情况吗？',
    '您觉得是什么原因导致的呢？',
    '如果换个角度思考，您会怎么看？'
  ]},
  { category: '总结', templates: [
    '今天我们讨论了很多，您觉得最有收获的是什么？',
    '让我们总结一下今天的咨询内容。',
    '对于下次咨询，您有什么建议吗？'
  ]}
])

// 用户数据（模拟，实际应该从API获取）
const userData = ref({
  name: '用户',
  avatar: '',
  online: true
})

const counselorAvatar = ref('')

// 快捷回复
const quickReplies = [
  '您好，我已准备好，请开始讲述您的情况。',
  '我理解您的感受，能详细说说吗？',
  '这个问题很重要，我们深入探讨一下。',
  '您的进步很明显，继续保持！',
  '谢谢您的信任，我们下次再聊。'
]

let timerInterval = null
let pollingInterval = null
let unreadCount = ref(0)

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

// 加载消息
const loadMessages = async () => {
  try {
    // 不显示loading，避免轮询时闪烁
    if (messages.value.length === 0) {
      loading.value = true
    }

    console.log('Loading messages for appointment:', appointmentId.value)

    const res = await getMessages(appointmentId.value, {})
    console.log('Messages response:', res)

    if (res.data && res.data.list) {
      const newMessages = res.data.list.map(msg => ({
        id: msg.id,
        content: msg.content,
        type: msg.message_type || 'text',
        isSelf: msg.sender_type === 'counselor',
        createdAt: msg.created_at,
        fileName: msg.file_name,
        isRead: msg.is_read
      }))

      // 检测新消息
      if (messages.value.length > 0) {
        const lastMsgId = messages.value[messages.value.length - 1].id
        const hasNewMessages = newMessages.some(msg => msg.id > lastMsgId && !msg.isSelf)

        if (hasNewMessages) {
          // 播放提示音
          playNotificationSound()
          // 显示浏览器通知
          showBrowserNotification()
        }
      }

      messages.value = newMessages

      // 统计未读消息（对方发送且未读的）
      unreadCount.value = messages.value.filter(msg => !msg.isSelf && !msg.isRead).length

      await nextTick()
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载消息失败:', error)
    // 轮询时不显示错误提示
    if (messages.value.length === 0) {
      ElMessage.error(error.response?.data?.detail || '加载消息失败')
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
      // 忽略播放失败（浏览器可能阻止自动播放）
    })
  } catch (error) {
    console.log('无法播放提示音')
  }
}

// 显示浏览器通知
const showBrowserNotification = () => {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('新消息', {
      body: '您收到一条新的咨询消息',
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
  if (!inputText.value.trim() || sending.value) return

  const content = inputText.value.trim()
  inputText.value = ''

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
    console.log('Sending message:', { content, type: 'text' })

    await sendMessageAPI(appointmentId.value, {
      content: content,
      type: 'text'
    })

    // 重新加载消息列表
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

// 发送快捷回复
const sendQuickReply = (reply) => {
  inputText.value = reply
  sendMessage()
  showQuickReplies.value = false
}

// 处理文件选择
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
    console.log('Upload response:', uploadRes)

    const fileUrl = uploadRes.data?.url || uploadRes.url

    // 发送文件消息
    await sendMessageAPI(appointmentId.value, {
      content: fileUrl,
      type: isImage ? 'image' : 'file'
    })

    // 重新加载
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

// 下载文件
const downloadFile = (url) => {
  window.open(url, '_blank')
}

// 结束咨询
const endConsultation = async () => {
  if (!endForm.value.summary) {
    ElMessage.warning('请填写咨询总结')
    return
  }

  try {
    await endConsultationAPI(appointmentId.value, {
      summary: endForm.value.summary,
      suggestions: endForm.value.suggestions
    })
    ElMessage.success('咨询已结束')
    showEndDialog.value = false

    // 跳转到评价页面
    router.push({
      path: '/consultation/review',
      query: { appointmentId: appointmentId.value }
    })
  } catch (error) {
    console.error('结束咨询失败:', error)
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// 保存备注
const saveNote = async () => {
  if (!noteForm.value.content) {
    ElMessage.warning('请输入备注内容')
    return
  }

  try {
    const noteContent = `[${noteTypes.find(t => t.value === noteForm.value.type)?.label}] ${noteForm.value.content}`
    // TODO: 调用保存备注API
    ElMessage.success('备注已保存')
    showNoteDialog.value = false
    noteForm.value = { type: 'observation', content: '' }
  } catch (error) {
    console.error('保存备注失败:', error)
    ElMessage.error('保存失败')
  }
}

// 使用素材
const useMaterial = (template) => {
  inputText.value = template
  showMaterialLibrary.value = false
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

// 启动计时器
const startTimer = () => {
  elapsedTime.value = 0
  timerInterval = setInterval(() => {
    elapsedTime.value++
  }, 1000)
}

// 启动消息轮询
const startPolling = () => {
  pollingInterval = setInterval(() => {
    if (!sending.value) {
      loadMessages()
    }
  }, 3000) // 每3秒轮询一次
}

onMounted(async () => {
  console.log('Appointment ID:', appointmentId.value)
  await loadMessages()
  startTimer()
  startPolling()
  requestNotificationPermission()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
  if (pollingInterval) clearInterval(pollingInterval)
})
</script>

<style scoped>
.consultation-chat {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.chat-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 1200px;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info .info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #2c3e50;
}

.user-info .status {
  margin: 0;
  font-size: 14px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 6px;
}

.user-info .status .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
}

.user-info .status.online .dot {
  background: #67c23a;
}

.actions {
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

/* 消息列表 */
.messages-list {
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

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-item.self {
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

.message-item.self .sender {
  text-align: right;
}

.bubble {
  padding: 12px 16px;
  border-radius: 12px;
  word-break: break-word;
}

.message-item:not(.self) .bubble {
  background: #f4f4f5;
  border-bottom-left-radius: 4px;
}

.message-item.self .bubble {
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

.message-item.self .time {
  text-align: right;
}

/* 快捷回复 */
.quick-replies {
  background: white;
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.quick-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #606266;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
  .chat-wrapper {
    padding: 12px;
  }

  .message-content {
    max-width: 80%;
  }
}

/* 素材库样式 */
.material-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.material-item {
  cursor: pointer;
  padding: 12px;
  transition: all 0.3s;
}

.material-item:hover {
  background: #409eff;
  color: white;
  transform: translateY(-2px);
}
</style>
