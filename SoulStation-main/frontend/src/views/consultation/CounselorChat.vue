<template>
  <div class="counselor-im">
    <PageHeader />

    <div v-loading="loading" class="im-container">
      <!-- 左侧会话列表 -->
      <div class="sessions-panel">
        <div class="panel-header">
          <h3>消息</h3>
          <el-badge :value="unreadCount" :hidden="unreadCount === 0">
            <el-icon><ChatDotRound /></el-icon>
          </el-badge>
        </div>

        <!-- 搜索框 -->
        <div class="search-box">
          <el-input
            v-model="searchText"
            placeholder="搜索会话..."
            :prefix-icon="Search"
            clearable
            size="small"
          />
        </div>

        <!-- 会话列表 -->
        <div class="sessions-list">
          <div
            v-for="session in filteredSessions"
            :key="session.id"
            class="session-item"
            :class="{ active: currentSessionId === session.id }"
            @click="switchSession(session)"
          >
            <div class="session-avatar">
              <el-badge :is-dot="session.unreadCount > 0" :hidden="session.unreadCount === 0">
                <el-avatar :size="48" :src="session.userAvatar">
                  <el-icon v-if="!session.userAvatar"><User /></el-icon>
                </el-avatar>
              </el-badge>
            </div>
            <div class="session-content">
              <div class="session-top">
                <span class="user-name">{{ session.userName }}</span>
                <span class="session-time">{{ formatTime(session.lastMessageTime) }}</span>
              </div>
              <div class="session-bottom">
                <p class="last-message">{{ session.lastMessage }}</p>
                <el-badge v-if="session.unreadCount > 0" :value="session.unreadCount" :max="99" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧聊天窗口 -->
      <div v-if="currentSessionId" class="chat-window">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="user-section">
            <el-avatar :size="45" :src="currentSession?.userAvatar">
              <el-icon v-if="!currentSession?.userAvatar"><User /></el-icon>
            </el-avatar>
            <div class="user-details">
              <h3>{{ currentSession?.userName }}</h3>
              <p class="user-status">
                <span class="status-dot" :class="{ online: currentSession?.isOnline }"></span>
                {{ currentSession?.isOnline ? '在线' : '离线' }}
              </p>
            </div>
          </div>

          <div class="header-actions">
            <div class="consultation-info">
              <el-icon><Clock /></el-icon>
              <span>咨询时长：{{ formatDuration(elapsedTime) }}</span>
            </div>
            <el-button-group>
              <el-tooltip content="语音通话">
                <el-button :icon="Phone" />
              </el-tooltip>
              <el-tooltip content="视频通话">
                <el-button :icon="VideoCamera" />
              </el-tooltip>
              <el-dropdown trigger="click" @command="handleMenuCommand">
                <el-button :icon="MoreFilled" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">
                      <el-icon><User /></el-icon>
                      查看资料
                    </el-dropdown-item>
                    <el-dropdown-item command="note">
                      <el-icon><Edit /></el-icon>
                      添加备注
                    </el-dropdown-item>
                    <el-dropdown-item command="history">
                      <el-icon><Clock /></el-icon>
                      历史咨询
                    </el-dropdown-item>
                    <el-dropdown-item command="transfer">
                      <el-icon><Switch /></el-icon>
                      转介他人
                    </el-dropdown-item>
                    <el-dropdown-item command="end" divided>
                      <el-icon><CircleClose /></el-icon>
                      结束咨询
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-button-group>
          </div>
        </div>

        <!-- 可折叠的用户信息 -->
        <el-collapse v-model="activeInfo" class="user-info-bar">
          <el-collapse-item name="info">
            <template #title>
              <span class="collapse-title">
                <el-icon><InfoFilled /></el-icon>
                预约信息
              </span>
            </template>
            <div class="info-cards">
              <div class="info-card">
                <div class="card-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="card-text">
                  <span class="label">问题描述</span>
                  <p>{{ currentSession?.description || '暂无' }}</p>
                </div>
              </div>
              <div class="info-card">
                <div class="card-icon">
                  <el-icon><Calendar /></el-icon>
                </div>
                <div class="card-text">
                  <span class="label">预约时间</span>
                  <p>{{ currentSession?.appointmentTime || '待定' }}</p>
                </div>
              </div>
              <div class="info-card">
                <div class="card-icon">
                  <el-icon><ChatLineRound /></el-icon>
                </div>
                <div class="card-text">
                  <span class="label">咨询方式</span>
                  <p>{{ getConsultationType(currentSession?.consultationType) }}</p>
                </div>
              </div>
              <div class="info-card">
                <div class="card-icon">
                  <el-icon><Histogram /></el-icon>
                </div>
                <div class="card-text">
                  <span class="label">历史咨询</span>
                  <p>{{ currentSession?.historyCount || 0 }} 次</p>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>

        <!-- 消息区域 -->
        <div
          ref="messagesContainer"
          class="messages-container"
          @scroll="handleScroll"
        >
          <!-- 空状态 -->
          <div v-if="messages.length === 0 && !loading" class="empty-messages">
            <el-empty description="暂无消息">
              <template #image>
                <el-icon :size="100" color="#dcdfe6"><ChatDotRound /></el-icon>
              </template>
              <el-button type="primary" @click="showQuickRepliesPanel = true">
                使用快捷回复
              </el-button>
            </el-empty>
          </div>

          <!-- 时间分组 -->
          <template v-for="(groupMsgs, date) in groupedMessages" :key="date">
            <div class="time-divider">
              <span>{{ formatDate(date) }}</span>
            </div>

            <!-- 消息列表 -->
            <div
              v-for="msg in groupMsgs"
              :key="msg.id"
              class="message-item"
              :class="{ 'is-self': msg.senderId === currentUserId }"
            >
              <!-- 头像 -->
              <div class="msg-avatar">
                <el-avatar :size="38" :src="msg.senderId === currentUserId ? counselorAvatar : currentSession?.userAvatar">
                  <el-icon v-if="msg.senderId === currentUserId && !counselorAvatar"><User /></el-icon>
                  <el-icon v-else-if="msg.senderId !== currentUserId && !currentSession?.userAvatar"><User /></el-icon>
                </el-avatar>
              </div>

              <!-- 消息内容 -->
              <div class="msg-content">
                <!-- 发送者名字 -->
                <div class="msg-sender">{{ msg.senderId === currentUserId ? '我' : currentSession?.userName }}</div>

                <!-- 消息气泡 -->
                <div class="msg-bubble-wrapper">
                  <!-- 文字消息 -->
                  <div v-if="msg.type === 'text'" class="msg-bubble msg-text">
                    {{ msg.content }}
                    <!-- 消息操作（撤回） -->
                    <el-dropdown
                      v-if="msg.senderId === currentUserId && canRecall(msg)"
                      trigger="click"
                      class="msg-actions"
                      @command="cmd => handleMsgCommand(cmd, msg)"
                    >
                      <span class="msg-time">{{ formatMessageTime(msg.createdAt) }}</span>
                      <el-icon><MoreFilled /></el-icon>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="recall">
                            <el-icon><RefreshLeft /></el-icon>
                            撤回消息
                          </el-dropdown-item>
                          <el-dropdown-item command="copy">
                            <el-icon><DocumentCopy /></el-icon>
                            复制
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                    <span v-else class="msg-time">{{ formatMessageTime(msg.createdAt) }}</span>
                  </div>

                  <!-- 图片消息 -->
                  <div v-else-if="msg.type === 'image'" class="msg-bubble msg-image">
                    <el-image
                      :src="msg.content"
                      fit="cover"
                      :preview-src-list="[msg.content]"
                      class="chat-image"
                    >
                      <template #error>
                        <div class="image-error">
                          <el-icon><Picture /></el-icon>
                          <span>图片加载失败</span>
                        </div>
                      </template>
                    </el-image>
                    <span class="msg-time">{{ formatMessageTime(msg.createdAt) }}</span>
                  </div>

                  <!-- 文件消息 -->
                  <div v-else-if="msg.type === 'file'" class="msg-bubble msg-file">
                    <div class="file-content">
                      <div class="file-icon">
                        <el-icon><Document /></el-icon>
                      </div>
                      <div class="file-info">
                        <span class="file-name">{{ getFileName(msg.content) }}</span>
                        <span class="file-size">{{ msg.fileSize ? formatFileSize(msg.fileSize) : '未知大小' }}</span>
                      </div>
                      <el-button type="primary" link @click="downloadFile(msg.content)">
                        <el-icon><Download /></el-icon>
                        下载
                      </el-button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 正在输入提示 -->
          <div v-if="isTyping" class="typing-indicator">
            <span class="typing-avatar">
              <el-avatar :size="24" :src="currentSession?.userAvatar">
                <el-icon v-if="!currentSession?.userAvatar"><User /></el-icon>
              </el-avatar>
            </span>
            <span class="typing-text">对方正在输入</span>
            <span class="typing-dots">
              <span></span><span></span><span></span>
            </span>
          </div>
        </div>

        <!-- 快捷回复面板 -->
        <div v-if="showQuickRepliesPanel" class="quick-replies-bar">
          <div class="quick-header">
            <span class="quick-title">
              <el-icon><ChatDotRound /></el-icon>
              快捷回复
            </span>
            <el-button :icon="Close" circle size="small" @click="showQuickRepliesPanel = false" />
          </div>
          <div class="quick-content">
            <el-button
              v-for="(reply, index) in quickReplies"
              :key="index"
              class="quick-btn"
              @click="sendQuickReply(reply)"
            >
              {{ reply }}
            </el-button>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <!-- 工具栏 -->
          <div class="input-toolbar">
            <!-- 表情按钮 -->
            <el-popover placement="top" :width="320" trigger="click">
              <template #reference>
                <el-button class="tool-btn" title="表情">
                  <el-icon><Management /></el-icon>
                </el-button>
              </template>
              <template #default>
                <div class="emoji-picker">
                  <div
                    v-for="emoji in emojiList"
                    :key="emoji"
                    class="emoji-item"
                    @click="insertEmoji(emoji)"
                  >
                    {{ emoji }}
                  </div>
                </div>
              </template>
            </el-popover>

            <!-- 图片按钮 -->
            <el-upload
              :show-file-list="false"
              :before-upload="handleUploadImage"
              accept="image/*"
            >
              <el-button class="tool-btn" title="发送图片">
                <el-icon><Picture /></el-icon>
              </el-button>
            </el-upload>

            <!-- 文件按钮 -->
            <el-upload
              :show-file-list="false"
              :before-upload="handleUploadFile"
            >
              <el-button class="tool-btn" title="发送文件">
                <el-icon><Folder /></el-icon>
              </el-button>
            </el-upload>

            <!-- 截图提示 -->
            <el-tooltip content="截图功能提示：使用系统截图工具（微信截图、QQ截图等），截图后粘贴到输入框" placement="top">
              <el-button class="tool-btn" title="截图">
                <el-icon><Scissor /></el-icon>
              </el-button>
            </el-tooltip>

            <!-- 语音按钮 -->
            <el-button
              class="tool-btn"
              :type="isRecording ? 'danger' : ''"
              @click="toggleVoiceRecord"
              title="语音消息"
            >
              <el-icon><Microphone /></el-icon>
            </el-button>

            <!-- 快捷回复开关 -->
            <el-button
              class="tool-btn"
              :type="showQuickRepliesPanel ? 'primary' : ''"
              @click="showQuickRepliesPanel = !showQuickRepliesPanel"
              title="快捷回复"
            >
              <el-icon><ChatDotRound /></el-icon>
            </el-button>

            <!-- 清空按钮 -->
            <el-tooltip content="清空聊天记录" placement="top">
              <el-button class="tool-btn" @click="clearChatHistory" title="清空">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>

          <!-- 输入框 -->
          <div class="input-box">
            <el-input
              ref="messageInput"
              v-model="messageContent"
              type="textarea"
              :rows="inputRows"
              :maxlength="500"
              show-word-limit
              placeholder="输入消息... (Enter发送，Shift+Enter换行)"
              @keydown="handleKeyDown"
              @paste="handlePaste"
            />
            <div class="send-section">
              <el-button
                type="primary"
                :icon="Promotion"
                :loading="sending"
                :disabled="!messageContent.trim()"
                @click="sendMessage"
                size="default"
              >
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 未选择会话 -->
      <div v-else class="empty-session">
        <el-empty description="选择左侧会话开始聊天">
          <template #image>
            <el-icon :size="120" color="#dcdfe6"><ChatDotRound /></el-icon>
          </template>
        </el-empty>
      </div>
    </div>

    <!-- 备注对话框 -->
    <el-dialog v-model="noteDialogVisible" title="添加咨询备注" width="500px">
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="备注类型">
          <el-radio-group v-model="noteForm.type">
            <el-radio-button label="观察">观察记录</el-radio-button>
            <el-radio-button label="assessment">评估</el-radio-button>
            <el-radio-button label="suggestion">建议</el-radio-button>
            <el-radio-button label="other">其他</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注内容">
          <el-input
            v-model="noteForm.content"
            type="textarea"
            :rows="6"
            placeholder="记录本次咨询的关键信息、观察结果、专业建议等..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNote">保存</el-button>
      </template>
    </el-dialog>

    <!-- 结束咨询对话框 -->
    <el-dialog v-model="endDialogVisible" title="结束咨询" width="500px">
      <el-form :model="endForm" label-width="80px">
        <el-form-item label="咨询总结">
          <el-input
            v-model="endForm.summary"
            type="textarea"
            :rows="4"
            placeholder="总结本次咨询的主要内容、进展和..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="下次建议">
          <el-input
            v-model="endForm.suggestions"
            type="textarea"
            :rows="3"
            placeholder="给用户的建议和下次咨询的练习..."
            maxlength="300"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="咨询状态">
          <el-radio-group v-model="endForm.status">
            <el-radio-button label="completed">已完成</el-radio-button>
            <el-radio-button label="need_follow">需要跟进</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="endDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmEndConsultation">确定结束</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, User, Timer, Phone, VideoCamera, MoreFilled, ChatDotRound,
  Picture, Folder, Microphone, Document, Download, Management,
  Scissor, Delete, ChatLineRound, Promotion, Edit, Clock, InfoFilled,
  RefreshLeft, DocumentCopy, Histogram, Calendar, Close, CircleClose,
  Switch
} from '@element-plus/icons-vue'
import PageHeader from '@/components/PageHeader.vue'
import { getMessages, sendMessage, uploadFile, endConsultation, addConsultationNote } from '@/api/consultation'
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
const messageContent = ref('')
const inputRows = ref(2)
const messages = ref([])
const sessions = ref([])
const currentSessionId = ref(null)
const activeInfo = ref([])
const showQuickRepliesPanel = ref(false)
const noteDialogVisible = ref(false)
const noteForm = ref({ type: 'observation', content: '' })
const endDialogVisible = ref(false)
const endForm = ref({ summary: '', suggestions: '', status: 'completed' })
const messagesContainer = ref(null)
const messageInput = ref(null)
const searchText = ref('')

const currentUserId = userStore.user?.id
const counselorAvatar = userStore.user?.avatar

// 未读消息总数
const unreadCount = computed(() => {
  return sessions.value.reduce((sum, s) => sum + (s.unreadCount || 0), 0)
})

// 过滤后的会话列表
const filteredSessions = computed(() => {
  if (!searchText.value) return sessions.value
  const search = searchText.value.toLowerCase()
  return sessions.value.filter(s =>
    s.userName?.toLowerCase().includes(search) ||
    s.lastMessage?.toLowerCase().includes(search)
  )
})

// 当前会话
const currentSession = computed(() => {
  return sessions.value.find(s => s.id === currentSessionId.value)
})

// 按日期分组的消息
const groupedMessages = computed(() => {
  const groups = {}
  messages.value.forEach(msg => {
    const date = new Date(msg.createdAt).toDateString()
    if (!groups[date]) groups[date] = []
    groups[date].push(msg)
  })
  return groups
})

// 表情列表
const emojiList = ['😊', '😂', '🥰', '😍', '🤔', '😌', '😎', '😭', '😘', '👍', '🙏', '💪', '🎉', '💯', '🌟', '❤️', '🌈']

// 快捷回复
const quickReplies = [
  '您好，我已准备好，请开始讲述您的情况。',
  '我理解您的感受，能详细说说吗？',
  '这个问题很重要，我们深入探讨一下。',
  '您的进步很明显，继续保持！',
  '今天的咨询时间差不多了，总结一下我们讨论的内容。',
  '谢谢您的信任，我们下次再聊。',
  '可以多说说这方面的感受吗？',
  '您觉得这样做会有什么改变？',
  '我明白了，继续说...'
]

// 模拟会话数据
const loadSessions = async () => {
  // TODO: 从API加载真实会话列表
  sessions.value = [
    {
      id: 1,
      userName: '李同学',
      userAvatar: '',
      lastMessage: '谢谢老师的帮助',
      lastMessageTime: new Date(),
      unreadCount: 0,
      isOnline: true,
      status: 'in_progress',
      consultationType: 'video',
      description: '最近感到压力很大，睡眠不好，希望得到帮助',
      appointmentTime: '2026-04-02 14:00-15:00',
      historyCount: 2
    }
  ]

  // 自动选择第一个会话
  if (sessions.value.length > 0) {
    currentSessionId.value = sessions.value[0].id
    await loadMessages()
  }

  loading.value = false
}

const switchSession = async (sessionId) => {
  currentSessionId.value = sessionId
  messages.value = []
  await loadMessages()
}

const loadMessages = async () => {
  if (!currentSessionId.value) return

  try {
    const res = await getMessages(currentSessionId.value)
    messages.value = res.data.list || []
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败', error)
    ElMessage.error('加载消息失败')
  }
}

const sendMessage = async () => {
  if (!messageContent.value.trim() || !currentSessionId.value) return

  try {
    sending.value = true
    await sendMessage(currentSessionId.value, {
      content: messageContent.value,
      type: 'text'
    })
    messageContent.value = ''
    inputRows.value = 2
    await loadMessages()
  } catch (error) {
    ElMessage.error('发送失败')
  } finally {
    sending.value = false
  }
}

const sendQuickReply = (reply) => {
  messageContent.value = reply
  sendMessage()
  showQuickRepliesPanel.value = false
}

const insertEmoji = (emoji) => {
  messageContent.value += emoji
  messageInput.value?.focus()
}

const handleUploadImage = async (file) => {
  if (!currentSessionId.value) {
    ElMessage.warning('请先选择会话')
    return false
  }

  try {
    const res = await uploadFile(file)
    await sendMessage(currentSessionId.value, {
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
  if (!currentSessionId.value) {
    ElMessage.warning('请先选择会话')
    return false
  }

  try {
    const res = await uploadFile(file)
    await sendMessage(currentSessionId.value, {
      content: res.data.url,
      type: 'file',
      fileName: file.name
    })
    await loadMessages()
  } catch (error) {
    ElMessage.error('上传失败')
  }
  return false
}

const handlePaste = async (event) => {
  const items = event.clipboardData.items
  for (const item of items) {
    if (item.type.indexOf('image') !== -1) {
      const file = item.getAsFile()
      if (file) {
        await handleUploadImage(file)
      }
      break
    }
  }
}

const toggleVoiceRecord = () => {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    ElMessage.info('开始录音（语音功能开发中）')
  } else {
    ElMessage.info('停止录音')
  }
}

const clearChatHistory = async () => {
  try {
    await ElMessageBox.confirm('确定要清空本次对话的所有消息记录吗？', '清空确认', {
      type: 'warning',
      confirmButtonText: '确定清空',
      cancelButtonText: '取消'
    })
    messages.value = []
    ElMessage.success('已清空聊天记录')
  } catch {
    // 用户取消
  }
}

const canRecall = (msg) => {
  // 消息发送2分钟内可撤回
  const now = new Date()
  const msgTime = new Date(msg.createdAt)
  const diff = now - msgTime
  return diff < 2 * 60 * 1000 && msg.senderId === currentUserId
}

const handleMsgCommand = async (command, msg) => {
  switch (command) {
    case 'recall':
      try {
        await ElMessageBox.confirm('确定要撤回这条消息吗？', '撤回消息', {
          type: 'warning'
        })
        // TODO: 调用撤回API
        messages.value = messages.value.filter(m => m.id !== msg.id)
        ElMessage.success('消息已撤回')
      } catch {
        // 用户取消
      }
      break
    case 'copy':
      navigator.clipboard.writeText(msg.content)
      ElMessage.success('已复制到剪贴板')
      break
  }
}

const handleMenuCommand = (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('查看用户资料功能开发中')
      break
    case 'note':
      noteDialogVisible.value = true
      break
    case 'history':
      ElMessage.info('历史记录功能开发中')
      break
    case 'transfer':
      ElMessage.info('转介功能开发中')
      break
    case 'end':
      endDialogVisible.value = true
      break
  }
}

const saveNote = async () => {
  try {
    await addConsultationNote(currentSessionId.value, noteForm.value)
    ElMessage.success('备注已保存')
    noteDialogVisible.value = false
    noteForm.value = { type: 'observation', content: '' }
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const confirmEndConsultation = async () => {
  try {
    await endConsultation(currentSessionId.value, endForm.value)
    ElMessage.success('咨询已结束')
    endDialogVisible.value = false

    // 更新会话状态
    const session = sessions.value.find(s => s.id === currentSessionId.value)
    if (session) {
      session.status = 'completed'
    }

    router.push('/consultation/counselor/orders')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleKeyDown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  } else if (e.key === 'Enter' && e.shiftKey) {
    // Shift+Enter允许换行
    inputRows.value = Math.min(inputRows.value + 1, 6)
  }
}

const handleScroll = (e) => {
  const { scrollTop, scrollHeight, clientHeight } = e.target
  // 接近底部时，标记已读
  if (scrollHeight - scrollTop - clientHeight < 50) {
    // TODO: 标记消息为已读
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const getFileName = (url) => {
  try {
    const parts = url.split('/')
    return parts[parts.length - 1]
  } catch {
    return '文件'
  }
}

const formatFileSize = (size) => {
  if (!size) return '未知大小'
  if (size < 1024) return size + 'B'
  if (size < 1024 * 1024) return (size / 1024).toFixed(1) + 'KB'
  return (size / (1024 * 1024)).toFixed(1) + 'MB'
}

const downloadFile = (url) => {
  window.open(url, '_blank')
}

const formatTime = (time) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'

  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const formatMessageTime = (time) => {
  const date = new Date(time)
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  if (date.toDateString() === today.toDateString()) return '今天'
  if (date.toDateString() === yesterday.toDateString()) return '昨天'

  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const formatDuration = (seconds) => {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60

  if (h > 0) return `${h}小时${m}分`
  if (m > 0) return `${m}分${s}秒`
  return `${s}秒`
}

const getConsultationType = (type) => {
  const types = {
    video: '视频咨询',
    voice: '语音咨询',
    offline: '线下咨询'
  }
  return types[type] || type
}

let pollingTimer = null
let durationTimer = null

const startPolling = () => {
  pollingTimer = setInterval(async () => {
    if (currentSessionId.value) {
      await loadMessages()
    }
  }, 3000)
}

const startTimer = () => {
  durationTimer = setInterval(() => {
    elapsedTime.value++
  }, 1000)
}

onMounted(async () => {
  await loadSessions()
  startPolling()
  startTimer()
})

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
  if (durationTimer) clearInterval(durationTimer)
})
</script>

<style scoped lang="scss">
@use '@/styles/variables.scss' as *;

.counselor-im {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: $bg-color;
}

.im-container {
  flex: 1;
  display: flex;
  gap: $spacing-md;
  padding: $spacing-lg;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  height: calc(100vh - 80px); // 减去header高度
}

// 左侧会话面板
.sessions-panel {
  width: 280px;
  background: white;
  border-radius: $border-radius;
  box-shadow: $shadow;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color;
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0;
    font-size: 16px;
    font-weight: 500;
  }
}

.search-box {
  padding: $spacing-md;
  border-bottom: 1px solid $border-color;
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-md;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background-color: #f5f7fa;
  }

  &.active {
    background-color: #e6f7ff;
  }
}

.session-avatar {
  flex-shrink: 0;
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: $spacing-xs;
}

.user-name {
  font-weight: 500;
  color: $text-primary;
  font-size: 14px;
}

.session-time {
  font-size: 11px;
  color: $text-secondary;
}

.session-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.last-message {
  flex: 1;
  font-size: 12px;
  color: $text-secondary;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: $spacing-xs;
}

// 右侧聊天窗口
.chat-window {
  flex: 1;
  background: white;
  border-radius: $border-radius;
  box-shadow: $shadow;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to bottom, #ffffff, #fafafa);
}

.user-section {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.user-details {
  h3 {
    margin: 0 0 $spacing-xs;
    font-size: 15px;
  }

  .user-status {
    font-size: 12px;
    color: $text-secondary;
    display: flex;
    align-items: center;
    gap: $spacing-xs;
  }
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ccc;

  &.online {
    background-color: $success-color;
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: $spacing-lg;
}

.consultation-info {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  color: $primary-color;
  font-size: 13px;
  font-weight: 500;
  padding: $spacing-sm $spacing-md;
  background: #f0f9ff;
  border-radius: 20px;
}

// 用户信息栏
.user-info-bar {
  border-bottom: 1px solid $border-color;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 14px;
  font-weight: 500;
  color: $primary-color;
}

.info-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
  padding: $spacing-md;
}

.info-card {
  display: flex;
  gap: $spacing-sm;
  padding: $spacing-md;
  background: #f5f7fa;
  border-radius: $border-radius;
}

.card-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  color: $primary-color;
  font-size: 16px;
}

.card-text {
  flex: 1;

  .label {
    font-size: 11px;
    color: $text-secondary;
    display: block;
    margin-bottom: 2px;
  }

  p {
    margin: 0;
    font-size: 13px;
    line-height: 1.4;
  }
}

// 消息区域
.messages-container {
  flex: 1;
  padding: $spacing-lg;
  overflow-y: auto;
  background: linear-gradient(to bottom, #f5f7fa 0%, #e8ebf0 100%);
}

.empty-messages {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.time-divider {
  text-align: center;
  margin: $spacing-lg 0;
  position: relative;

  &::before {
    content: '';
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    height: 1px;
    background: #d9d9d9;
  }

  span {
    background: #e8ebf0;
    padding: $spacing-xs $spacing-md;
    font-size: 11px;
    color: $text-secondary;
    position: relative;
    z-index: 1;
    border-radius: 12px;
  }
}

.message-item {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;

  &.is-self {
    flex-direction: row-reverse;

    .msg-content {
      align-items: flex-end;
    }
  }
}

.msg-avatar {
  flex-shrink: 0;
}

.msg-content {
  max-width: 60%;
}

.msg-sender {
  font-size: 12px;
  color: $text-secondary;
  margin-bottom: $spacing-xs;
}

.msg-bubble-wrapper {
  position: relative;
}

.msg-bubble {
  padding: $spacing-md;
  background: white;
  border-radius: $border-radius;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  word-break: break-word;
  line-height: 1.5;
  position: relative;
}

.message-item.is-self .msg-bubble {
  background: linear-gradient(135deg, $primary-color, #409eff);
  color: white;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);

  &::before {
    content: '';
    position: absolute;
    right: -6px;
    top: 12px;
    border-width: 6px 0 6px 6px;
    border-style: solid;
    border-color: transparent transparent transparent #409eff;
  }
}

.message-item:not(.is-self) .msg-bubble {
  &::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 12px;
    border-width: 6px 6px 6px 0;
    border-style: solid;
    border-color: transparent transparent transparent white;
  }
}

.msg-text {
  white-space: pre-wrap;
}

.msg-image {
  .chat-image {
    max-width: 240px;
    max-height: 200px;
    border-radius: $border-radius;
    overflow: hidden;
    cursor: pointer;
  }

  .image-error {
    width: 200px;
    height: 140px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: $spacing-sm;
    background: #f5f7fa;
    border-radius: $border-radius;
    color: $text-secondary;
  }
}

.msg-file {
  .file-content {
    display: flex;
    align-items: center;
    gap: $spacing-md;
  }
}

.file-icon {
  font-size: 28px;
  color: $primary-color;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;

  .file-name {
    font-size: 13px;
    font-weight: 500;
    color: $text-primary;
  }

  .file-size {
    font-size: 11px;
    color: $text-secondary;
  }
}

.msg-actions {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  transition: background 0.2s;

  &:hover {
    background: rgba(0, 0, 0, 0.05);
  }
}

.msg-time {
  font-size: 11px;
  color: $text-secondary;
  margin-top: $spacing-xs;
  display: flex;
  align-items: center;
}

.message-item.is-self .msg-actions {
  flex-direction: row-reverse;
}

.message-item.is-self .msg-time {
  justify-content: flex-end;
}

// 输入指示器
.typing-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  padding: $spacing-md;
  margin-bottom: $spacing-md;
}

.typing-avatar {
  margin-right: $spacing-xs;
}

.typing-text {
  font-size: 12px;
  color: $text-secondary;
}

.typing-dots {
  display: flex;
  gap: 4px;

  span {
    width: 6px;
    height: 6px;
    background: #999;
    border-radius: 50%;
    animation: typing 1.4s infinite;

    &:nth-child(2) {
      animation-delay: 0.2s;
    }

    &:nth-child(3) {
      animation-delay: 0.4s;
    }
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-10px);
  }
}

// 快捷回复面板
.quick-replies-bar {
  border-top: 1px solid $border-color;
  background: #fafafa;
}

.quick-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-sm $spacing-lg;
  border-bottom: 1px solid #eee;

  .quick-title {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    font-size: 13px;
    font-weight: 500;
    color: $primary-color;
  }
}

.quick-content {
  padding: $spacing-md $spacing-lg;
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
}

.quick-btn {
  border-radius: 20px;
  border: 1px solid $border-color;
}

// 输入区域
.input-area {
  border-top: 1px solid $border-color;
  background: white;
}

.input-toolbar {
  padding: $spacing-sm $spacing-lg;
  display: flex;
  gap: $spacing-sm;
  border-bottom: 1px solid #f5f5f5;
}

.tool-btn {
  border: none;
  background: transparent;
  color: $text-secondary;

  &:hover {
    color: $primary-color;
  }
}

.input-box {
  padding: $spacing-md $spacing-lg;
  display: flex;
  gap: $spacing-md;
  align-items: flex-end;
}

.send-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  align-items: flex-end;
}

// 表情选择器
.emoji-picker {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: $spacing-xs;
  padding: $spacing-sm;
}

.emoji-item {
  font-size: 24px;
  text-align: center;
  padding: $spacing-xs;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;

  &:hover {
    background: #f5f5f5;
  }
}

// 空状态
.empty-session {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: $border-radius;
  box-shadow: $shadow;
}
</style>
