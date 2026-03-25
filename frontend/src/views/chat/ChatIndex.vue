<template>
  <div class="chat-index">
    <!-- 顶部导航栏 -->
    <div class="chat-header">
      <div class="header-left">
        <!-- 返回按钮 -->
        <el-button
          :icon="ArrowLeft"
          circle
          size="small"
          @click="goBack"
          class="back-button"
        />
        <el-icon :size="24" color="#409EFF">
          <ChatDotSquare />
        </el-icon>
        <h2>智能心理问答</h2>
      </div>
      <div class="header-center">
        <!-- 对话信息 -->
        <div v-if="currentChatId" class="current-chat-info">
          <span class="chat-title-display">{{ currentChatTitle }}</span>
          <el-button
            text
            :icon="Edit"
            size="small"
            @click="editChatTitle(currentChatId)"
          />
        </div>
      </div>
      <div class="header-right">
        <!-- 功能按钮组 -->
        <div class="header-actions">
          <el-tooltip content="标签管理" placement="bottom">
            <el-button circle :icon="PriceTag" @click="showTagManager = true" />
          </el-tooltip>
          <el-tooltip content="导出对话" placement="bottom">
            <el-button circle :icon="Download" @click="exportChat" />
          </el-tooltip>
          <el-tooltip content="清空对话" placement="bottom">
            <el-button circle :icon="Delete" @click="clearChat" />
          </el-tooltip>
          <el-tooltip content="通知" placement="bottom">
            <el-button circle :icon="Bell" />
          </el-tooltip>
        </div>
        <!-- 用户菜单 -->
        <el-dropdown @command="handleUserCommand">
          <el-avatar :size="36" :src="userInfo?.avatar">
            <el-icon><User /></el-icon>
          </el-avatar>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                设置
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="chat-container">
      <!-- 左侧历史对话列表 -->
      <div class="chat-sidebar">
        <!-- 新建对话按钮 -->
        <div class="new-chat-btn">
          <el-button type="primary" :icon="Plus" @click="createNewChat">
            新建对话
          </el-button>
        </div>

        <!-- 搜索框 -->
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索对话..."
            prefix-icon="Search"
            clearable
            size="small"
          />
        </div>

        <!-- 标签筛选 -->
        <div class="tag-filter">
          <el-select
            v-model="selectedTag"
            placeholder="选择标签"
            clearable
            size="small"
            style="width: 100%"
          >
            <el-option label="全部" value="" />
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </div>

        <!-- 对话列表 -->
        <div class="chat-list">
          <el-skeleton v-if="loadingChats" :rows="5" animated />
          <div
            v-for="chat in filteredChats"
            :key="chat.id"
            class="chat-item"
            :class="{ active: currentChatId === chat.id }"
            @click="selectChat(chat.id)"
          >
            <div class="chat-item-content">
              <h4 class="chat-title">{{ chat.title }}</h4>
              <p class="chat-preview">{{ chat.lastMessage }}</p>
              <span class="chat-time">{{ formatTime(chat.updatedAt) }}</span>
            </div>
            <el-dropdown
              trigger="click"
              @command="(cmd) => handleChatCommand(cmd, chat.id)"
            >
              <el-icon class="more-icon"><MoreFilled /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">
                    <el-icon><Edit /></el-icon>
                    编辑标题
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <el-icon><Delete /></el-icon>
                    删除对话
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- 右侧对话区域 -->
      <div class="chat-main">
        <!-- 未选择对话时的空状态 -->
        <div v-if="!currentChatId" class="chat-empty">
          <el-result
            icon="info"
            title="选择一个对话或创建新对话"
            sub-title="AI助手随时为您提供帮助"
          >
            <template #extra>
              <el-button type="primary" :icon="Plus" @click="createNewChat">
                开始新对话
              </el-button>
            </template>
          </el-result>
        </div>

        <!-- 对话内容 -->
        <div v-else class="chat-content">
          <!-- 消息列表 -->
          <div class="message-list" ref="messageListRef">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-item"
              :class="message.role"
            >
              <!-- AI消息 -->
              <div v-if="message.role === 'assistant'" class="message-assistant">
                <div class="message-avatar">
                  <el-icon :size="24" color="#409EFF">
                    <ChatDotSquare />
                  </el-icon>
                </div>
                <div class="message-bubble">
                  <div class="message-text" v-html="renderMarkdown(message.content)"></div>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
              </div>

              <!-- 用户消息 -->
              <div v-else class="message-user">
                <div class="message-bubble">
                  <div class="message-text">{{ message.content }}</div>
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
                <div class="message-avatar">
                  <el-avatar :size="32" :src="userInfo?.avatar">
                    <el-icon><User /></el-icon>
                  </el-avatar>
                </div>
              </div>
            </div>

            <!-- 加载中 -->
            <div v-if="loadingMessages" class="message-item assistant">
              <div class="message-avatar">
                <el-icon :size="24" color="#409EFF">
                  <ChatDotSquare />
                </el-icon>
              </div>
              <div class="message-bubble">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input-area">
            <!-- 工具栏 -->
            <div class="input-toolbar">
              <el-upload
                :auto-upload="false"
                :show-file-list="false"
                accept="image/*,.pdf,.doc,.docx"
                :on-change="handleFileChange"
              >
                <el-button circle :icon="Paperclip" />
              </el-upload>
              <el-button
                circle
                :icon="Microphone"
                :type="isRecording ? 'danger' : 'default'"
                @click="toggleRecording"
              />
            </div>

            <!-- 输入框 -->
            <div class="input-box">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="1"
                :autosize="{ minRows: 1, maxRows: 6 }"
                placeholder="输入您的问题...（Enter发送，Shift+Enter换行）"
                @keydown.enter.exact="sendMessage"
                @keydown.enter.shift.prevent
                resize="none"
              />
              <el-button
                type="primary"
                :icon="Promotion"
                circle
                :loading="sendingMessage"
                :disabled="!inputMessage.trim()"
                @click="sendMessage"
              />
            </div>

            <!-- 附件预览 -->
            <div v-if="selectedFile" class="file-preview">
              <el-tag closable @close="removeFile">
                📎 {{ selectedFile.name }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 标签管理对话框 -->
    <el-dialog
      v-model="showTagManager"
      title="标签管理"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="tag-manager">
        <!-- 创建新标签 -->
        <div class="tag-create">
          <h4>创建新标签</h4>
          <el-input
            v-model="newTagName"
            placeholder="标签名称"
            size="small"
            style="width: 200px; margin-right: 10px"
          />
          <el-color-picker v-model="newTagColor" size="small" />
          <el-button type="primary" size="small" @click="createTag" :icon="Plus">
            添加
          </el-button>
        </div>

        <!-- 标签列表 -->
        <div class="tag-list">
          <h4>我的标签</h4>
          <el-empty v-if="tags.length === 0" description="暂无标签" :image-size="80" />
          <div v-else class="tag-items">
            <el-tag
              v-for="tag in tags"
              :key="tag.id"
              closable
              :color="tag.color"
              @close="deleteTag(tag.id)"
              size="large"
              style="margin: 5px"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onBeforeUnmount, reactive, triggerRef } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ChatDotSquare,
  Plus,
  Search,
  Bell,
  User,
  SwitchButton,
  MoreFilled,
  Edit,
  Delete,
  Paperclip,
  Microphone,
  Promotion,
  ArrowLeft,
  PriceTag,
  Download,
  Setting,
  DocumentCopy
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getChatList, createChat, deleteChat, updateChatTitle, sendMessage as sendMessageApi, sendMessageStream, getChatDetail } from '@/api/chat'
import { getTags } from '@/api/chat'
import { formatRelativeTime } from '@/utils/format'

const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 加载状态
const loadingChats = ref(true)
const loadingMessages = ref(false)
const sendingMessage = ref(false)

// 搜索和筛选
const searchKeyword = ref('')
const selectedTag = ref('')

// 对话列表
const chatList = ref([])
const currentChatId = ref(null)

// 消息列表
const messages = ref([])
const messageListRef = ref(null)

// 输入相关
const inputMessage = ref('')
const selectedFile = ref(null)
const isRecording = ref(false)

// 标签列表
const tags = ref([])
const showTagManager = ref(false)
const newTagName = ref('')
const newTagColor = ref('#409EFF')

// 当前对话标题
const currentChatTitle = computed(() => {
  const chat = chatList.value.find(c => c.id === currentChatId.value)
  return chat?.title || '未命名对话'
})

// 过滤后的对话列表
const filteredChats = computed(() => {
  let result = chatList.value

  // 搜索过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(chat =>
      chat.title.toLowerCase().includes(keyword) ||
      chat.lastMessage?.toLowerCase().includes(keyword)
    )
  }

  // 标签过滤
  if (selectedTag.value) {
    result = result.filter(chat => chat.tagId === selectedTag.value)
  }

  // 按更新时间排序
  return result.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

// 格式化时间
const formatTime = (timestamp) => {
  return formatRelativeTime(timestamp)
}

// 渲染Markdown（简化版）
const renderMarkdown = (content) => {
  // 这里简化处理，实际项目应该使用marked或markdown-it库
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

// 加载对话列表
const loadChatList = async () => {
  try {
    loadingChats.value = true
    const res = await getChatList()
    chatList.value = res.data || []

    // 如果有对话，默认选择第一个
    if (chatList.value.length > 0 && !currentChatId.value) {
      selectChat(chatList.value[0].id)
    }
  } catch (error) {
    console.error('加载对话列表失败:', error)
  } finally {
    loadingChats.value = false
  }
}

// 加载标签列表
const loadTags = async () => {
  try {
    const res = await getTags()
    tags.value = res.data || []
  } catch (error) {
    console.error('加载标签失败:', error)
  }
}

// 选择对话
const selectChat = async (chatId) => {
  currentChatId.value = chatId
  await loadMessages(chatId)
  scrollToBottom()
}

// 加载消息
const loadMessages = async (chatId) => {
  try {
    loadingMessages.value = true
    const res = await getChatDetail(chatId)
    messages.value = res.data.messages || []
  } catch (error) {
    console.error('加载消息失败:', error)
  } finally {
    loadingMessages.value = false
  }
}

// 创建新对话
const createNewChat = async () => {
  try {
    const res = await createChat({
      title: '新对话'
    })
    ElMessage.success('创建成功')
    await loadChatList()
    selectChat(res.data.id)
  } catch (error) {
    console.error('创建对话失败:', error)
  }
}

// 处理对话命令
const handleChatCommand = async (command, chatId) => {
  switch (command) {
    case 'edit':
      await editChatTitle(chatId)
      break
    case 'delete':
      await deleteChatById(chatId)
      break
  }
}

// 编辑对话标题
const editChatTitle = async (chatId) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新的对话标题', '编辑标题', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: chatList.value.find(c => c.id === chatId)?.title
    })

    await updateChatTitle(chatId, value)
    ElMessage.success('修改成功')
    await loadChatList()
  } catch {
    // 取消编辑
  }
}

// 删除对话
const deleteChatById = async (chatId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个对话吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteChat(chatId)
    ElMessage.success('删除成功')

    // 如果删除的是当前对话，清空消息区
    if (currentChatId.value === chatId) {
      currentChatId.value = null
      messages.value = []
    }

    await loadChatList()
  } catch {
    // 取消删除
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const content = inputMessage.value.trim()
  inputMessage.value = ''

  // 添加用户消息到列表
  const userMessage = {
    id: Date.now(),
    role: 'user',
    content,
    timestamp: new Date()
  }
  messages.value.push(userMessage)
  scrollToBottom()

  try {
    sendingMessage.value = true
    loadingMessages.value = true

    // 创建AI消息占位符（空消息，准备接收流式内容）
    const aiMessageIndex = messages.value.length
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    })
    scrollToBottom()

    // 使用流式API接收AI回复
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/chat/${currentChatId.value}/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content, type: 'text' }),
      // 重要：确保流式传输不被缓冲
      cache: 'no-store',
      // 某些浏览器可能需要这个
      priority: 'high'
    })

    if (!response.ok) {
      throw new Error('网络响应失败')
    }

    // 读取流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let chunkCount = 0  // 用于调试

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 处理SSE格式的数据
      const lines = buffer.split('\n\n')
      buffer = lines.pop() // 保留不完整的数据

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            // 如果有错误
            if (data.error) {
              throw new Error(data.error)
            }

            // 如果完成
            if (data.done) {
              console.log('流式接收完成，总chunk数:', chunkCount)

              // 更新消息状态
              const completedMessage = {
                ...messages.value[aiMessageIndex],
                id: data.message_id,
                isStreaming: false
              }
              messages.value.splice(aiMessageIndex, 1, completedMessage)

              sendingMessage.value = false
              loadingMessages.value = false
              break
            }

            // 接收内容并更新UI（打字机效果）
            if (data.content) {
              chunkCount++
              console.log('接收chunk #', chunkCount, ':', data.content)

              // 更新内容（创建新对象以触发Vue更新）
              const updatedMessage = {
                ...messages.value[aiMessageIndex],
                content: messages.value[aiMessageIndex].content + data.content
              }
              messages.value.splice(aiMessageIndex, 1, updatedMessage)

              // 立即滚动到底部
              scrollToBottom()
            }
          } catch (e) {
            console.error('解析数据失败:', e, line)
          }
        }
      }
    }

    // 更新对话列表的最后消息
    const chat = chatList.value.find(c => c.id === currentChatId.value)
    if (chat) {
      // 从数组中获取最新的AI消息
      const finalMessage = messages.value[aiMessageIndex]
      if (finalMessage && finalMessage.content) {
        chat.lastMessage = finalMessage.content.substring(0, 50) + (finalMessage.content.length > 50 ? '...' : '')
        chat.updatedAt = new Date()
      }
    }

  } catch (error) {
    console.error('发送消息失败:', error)

    // 移除失败的AI消息
    const index = messages.value.findIndex(m => m.role === 'assistant' && m.isStreaming)
    if (index !== -1) {
      messages.value.splice(index, 1)
    }

    ElMessage.error('发送失败，请重试')
  } finally {
    sendingMessage.value = false
    loadingMessages.value = false
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file
}

// 移除文件
const removeFile = () => {
  selectedFile.value = null
}

// 录音切换（模拟）
const toggleRecording = () => {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    ElMessage.info('开始录音...')
    // 实际项目这里应该调用录音API
    setTimeout(() => {
      isRecording.value = false
      inputMessage.value = '这是语音转文字的内容（模拟）'
    }, 2000)
  }
}

// 标签管理方法
const createTag = async () => {
  if (!newTagName.value.trim()) {
    ElMessage.warning('请输入标签名称')
    return
  }

  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/chat/tag`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: newTagName.value.trim(),
        color: newTagColor.value
      })
    })

    if (response.ok) {
      ElMessage.success('标签创建成功')
      newTagName.value = ''
      await loadTags()
    } else {
      throw new Error('创建失败')
    }
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

const deleteTag = async (tagId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个标签吗？', '删除标签', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/chat/tag/${tagId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      ElMessage.success('标签删除成功')
      await loadTags()
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 返回上一页
const goBack = () => {
  // 检查是否有历史记录
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    // 如果没有历史记录，返回首页
    router.push('/')
  }
}

// 导出对话
const exportChat = () => {
  if (!currentChatId.value || messages.value.length === 0) {
    ElMessage.warning('没有可导出的对话内容')
    return
  }

  // 导出为文本
  let content = `对话：${currentChatTitle.value}\n`
  content += `导出时间：${new Date().toLocaleString()}\n`
  content += `─`.repeat(50) + '\n\n'

  messages.value.forEach(msg => {
    const role = msg.role === 'user' ? '用户' : 'AI助手'
    content += `${role} [${formatTime(msg.timestamp)}]：\n${msg.content}\n\n`
  })

  // 创建下载
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `对话_${currentChatTitle.value}_${Date.now()}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('对话已导出')
}

// 清空对话
const clearChat = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空当前对话的所有消息吗？此操作不可恢复。',
      '清空对话',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    // 清空消息列表
    messages.value = []
    ElMessage.success('对话已清空')
  } catch {
    // 用户取消
  }
}

// 用户菜单命令
const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/profile/privacy')
      break
    case 'logout':
      await userStore.logout()
      break
  }
}

// 组件挂载
onMounted(() => {
  loadChatList()
  loadTags()
})

// 组件卸载前
onBeforeUnmount(() => {
  if (isRecording.value) {
    isRecording.value = false
  }
})
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.chat-index {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: $bg-color;
}

.chat-header {
  height: 60px;
  background: $bg-white;
  border-bottom: 1px solid $border-light;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-lg;

  .header-left {
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .back-button {
      margin-right: $spacing-xs;
    }

    h2 {
      font-size: $font-size-large;
      margin: 0;
    }
  }

  .header-center {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;

    .current-chat-info {
      display: flex;
      align-items: center;
      gap: $spacing-sm;

      .chat-title-display {
        font-size: $font-size-medium;
        font-weight: 500;
        color: $text-primary;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: $spacing-md;

    .header-actions {
      display: flex;
      align-items: center;
      gap: $spacing-xs;
      margin-right: $spacing-md;
    }
  }
}

.chat-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

// 左侧边栏
.chat-sidebar {
  width: 280px;
  background: $bg-white;
  border-right: 1px solid $border-light;
  display: flex;
  flex-direction: column;

  .new-chat-btn {
    padding: $spacing-md;
    border-bottom: 1px solid $border-lighter;

    .el-button {
      width: 100%;
    }
  }

  .search-box,
  .tag-filter {
    padding: $spacing-sm $spacing-md;
  }

  .chat-list {
    flex: 1;
    overflow-y: auto;
    padding: $spacing-sm;
  }

  .chat-item {
    padding: $spacing-md;
    border-radius: $border-radius-md;
    cursor: pointer;
    transition: $transition-base;
    position: relative;

    &:hover {
      background: $bg-color;
    }

    &.active {
      background: $primary-color;
      color: white;

      .chat-preview,
      .chat-time {
        color: rgba(255, 255, 255, 0.7);
      }
    }

    .chat-item-content {
      .chat-title {
        font-size: $font-size-base;
        font-weight: 500;
        margin-bottom: $spacing-xs;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .chat-preview {
        font-size: $font-size-small;
        color: $text-secondary;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .chat-time {
        font-size: $font-size-extra-small;
        color: $text-placeholder;
      }
    }

    .more-icon {
      position: absolute;
      top: $spacing-sm;
      right: $spacing-sm;
      opacity: 0;
      transition: $transition-base;

      &:hover {
        color: $primary-color;
      }
    }

    &:hover .more-icon {
      opacity: 1;
    }
  }
}

// 右侧主区域
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: $bg-white;
}

.chat-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

// 消息列表
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-lg;
  background: $bg-color;
}

.message-item {
  margin-bottom: $spacing-lg;

  &.assistant .message-assistant {
    display: flex;
    gap: $spacing-md;
  }

  &.user .message-user {
    display: flex;
    gap: $spacing-md;
    flex-direction: row-reverse;
  }
}

.message-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-white;
}

.message-bubble {
  max-width: 70%;
}

.message-text {
  padding: $spacing-md;
  border-radius: $border-radius-md;
  line-height: 1.6;
  word-break: break-word;
}

.message-assistant .message-text {
  background: $bg-white;
  color: $text-primary;
  box-shadow: $box-shadow-base;
}

.message-user .message-text {
  background: $primary-color;
  color: white;
}

.message-time {
  font-size: $font-size-extra-small;
  color: $text-placeholder;
  margin-top: $spacing-xs;
  display: block;
}

// 打字动画
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: $spacing-md;

  span {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: $text-placeholder;
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

// 输入区域
.chat-input-area {
  background: $bg-white;
  border-top: 1px solid $border-light;
  padding: $spacing-md;
}

.input-toolbar {
  display: flex;
  gap: $spacing-sm;
  margin-bottom: $spacing-sm;
}

.input-box {
  display: flex;
  gap: $spacing-sm;
  align-items: flex-end;

  .el-textarea {
    flex: 1;
  }

  :deep(.el-textarea__inner) {
    border-radius: $border-radius-md;
  }
}

.file-preview {
  margin-top: $spacing-sm;
}

// 响应式
@media (max-width: $breakpoint-md) {
  .chat-sidebar {
    position: absolute;
    left: -280px;
    height: calc(100vh - 60px);
    z-index: 100;
    transition: $transition-base;

    &.show {
      left: 0;
    }
  }

  .message-bubble {
    max-width: 85%;
  }
}
</style>

<!-- 标签管理对话框样式 -->
<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.tag-manager {
  .tag-create {
    display: flex;
    align-items: center;
    padding: $spacing-md 0;
    margin-bottom: $spacing-lg;
    border-bottom: 1px solid $border-light;

    h4 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-size-medium;
      color: $text-secondary;
    }
  }

  .tag-list {
    h4 {
      margin: 0 0 $spacing-sm 0;
      font-size: $font-size-medium;
      color: $text-secondary;
    }

    .tag-items {
      display: flex;
      flex-wrap: wrap;
      gap: $spacing-sm;
      padding: $spacing-sm 0;
    }
  }
}
</style>
