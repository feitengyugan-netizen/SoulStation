<template>
  <div class="call-room" v-if="showRoom">
    <el-dialog
      v-model="showRoom"
      :fullscreen="true"
      :show-close="false"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="call-room-dialog"
    >
      <!-- 通话状态提示 -->
      <div class="call-status" v-if="callState !== 'connected'">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>{{ statusText }}</span>
      </div>

      <!-- 主通话界面 -->
      <div class="call-content">
        <!-- 远程视频/音频区域 -->
        <div class="remote-media">
          <div v-if="callType === 'video'" class="video-container">
            <video
              ref="remoteVideoRef"
              autoplay
              playsinline
              class="remote-video"
              :class="{ 'active': hasRemoteStream }"
            ></video>
            <div v-if="!hasRemoteStream" class="placeholder">
              <el-icon :size="80"><VideoCamera /></el-icon>
              <p>{{ remotePlaceholder }}</p>
            </div>
          </div>
          <div v-else class="voice-indicator">
            <el-icon :size="60"><Phone /></el-icon>
            <p>{{ remoteUser }}</p>
          </div>
        </div>

        <!-- 本地视频（画中画） -->
        <div class="local-media" v-if="callType === 'video' && localStream">
          <video
            ref="localVideoRef"
            autoplay
            playsinline
            muted
            class="local-video"
          ></video>
        </div>

        <!-- 通话控制栏 -->
        <div class="call-controls">
          <el-button
            circle
            size="large"
            :type="isMuted ? 'danger' : 'primary'"
            @click="toggleMute"
          >
            <el-icon :size="24">
              <component :is="isMuted ? 'MuteNotification' : 'Microphone'" />
            </el-icon>
          </el-button>

          <el-button
            v-if="callType === 'video'"
            circle
            size="large"
            :type="isVideoOff ? 'danger' : 'primary'"
            @click="toggleVideo"
          >
            <el-icon :size="24">
              <component :is="isVideoOff ? 'VideoCameraFilled' : 'VideoCamera'" />
            </el-icon>
          </el-button>

          <div class="duration-display">
            <el-icon><Clock /></el-icon>
            <span>{{ formattedDuration }}</span>
          </div>

          <el-button
            circle
            size="large"
            type="danger"
            @click="hangup"
          >
            <el-icon :size="24"><PhoneFilled /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 遮挡层 - 确保对话框关闭前确认 -->
      <template #footer>
        <span></span>
      </template>
    </el-dialog>

    <!-- 挂断确认对话框 -->
    <el-dialog
      v-model="showHangupConfirm"
      title="确认结束通话"
      width="400px"
      :before-close="handleHangupCancel"
    >
      <p>您确定要结束通话吗？</p>
      <template #footer>
        <el-button @click="handleHangupCancel">取消</el-button>
        <el-button type="danger" @click="confirmHangup">确认结束</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  VideoCamera, Phone, PhoneFilled, Microphone, MuteNotification,
  VideoCameraFilled, Clock, Loading
} from '@element-plus/icons-vue'
import { useVideoCallStore } from '@/stores/videoCall'
import { useUserStore } from '@/stores/user'
import { formatDuration, checkWebRTCSupport, checkMediaPermissions, getErrorMessage } from '@/utils/webrtc'

const props = defineProps({
  appointmentId: {
    type: Number,
    required: true
  },
  callType: {
    type: String,
    default: 'voice', // voice 或 video
    validator: (value) => ['voice', 'video'].includes(value)
  },
  autoStart: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['call-ended', 'call-connected'])

// Store
const videoCallStore = useVideoCallStore()
const userStore = useUserStore()

// Refs
const localVideoRef = ref(null)
const remoteVideoRef = ref(null)

// 状态
const showRoom = ref(false)
const showHangupConfirm = ref(false)
const callState = ref('idle') // idle, calling, connected, ending
const localStream = ref(null)
const remoteStream = ref(null)
const peerConnection = ref(null)
const websocket = ref(null)
const hasRemoteStream = ref(false)

// 计算属性
const isMuted = computed(() => videoCallStore.isMuted)
const isVideoOff = computed(() => videoCallStore.isVideoOff)

const statusText = computed(() => {
  const texts = {
    'idle': '准备中...',
    'calling': '正在呼叫...',
    'connected': '通话中',
    'ending': '正在结束...'
  }
  return texts[callState.value] || '未知状态'
})

const formattedDuration = computed(() => formatDuration(videoCallStore.duration))

const remotePlaceholder = computed(() => {
  if (callState.value === 'calling') {
    return '正在等待对方接听...'
  }
  return '通话中...'
})

const remoteUser = computed(() => {
  // 可以从预约信息中获取对方名称
  return '对方用户'
})

// WebRTC 配置
const config = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' }
  ]
}

// 初始化
onMounted(async () => {
  if (props.autoStart) {
    await startCall()
  }
})

// 清理
onBeforeUnmount(() => {
  cleanup()
})

// 监听通话状态变化
watch(() => videoCallStore.callStatus, (newStatus) => {
  if (newStatus === 'connected') {
    callState.value = 'connected'
    emit('call-connected')
  } else if (newStatus === 'ended' || newStatus === 'error') {
    callState.value = 'ending'
    setTimeout(() => {
      showRoom.value = false
      cleanup()
      emit('call-ended')
    }, 500)
  }
})

// 开始通话
async function startCall() {
  try {
    // 检查浏览器支持
    if (!checkWebRTCSupport()) {
      ElMessage.error('当前浏览器不支持语音通话功能')
      return
    }

    // 检查媒体权限
    const permissions = await checkMediaPermissions()

    if (props.callType === 'video') {
      if (!permissions.hasVideo) {
        ElMessage.error('未检测到摄像头，无法进行视频通话')
        return
      }
    }

    if (!permissions.hasAudio) {
      ElMessage.error('未检测到麦克风，无法进行语音通话')
      return
    }

    // 获取本地媒体流
    const constraints = props.callType === 'video'
      ? { audio: true, video: true }
      : { audio: true, video: false }

    localStream.value = await navigator.mediaDevices.getUserMedia(constraints)
    videoCallStore.setLocalStream(localStream.value)

    // 设置本地视频
    if (localVideoRef.value && localStream.value) {
      localVideoRef.value.srcObject = localStream.value
    }

    // 发起通话
    await videoCallStore.initiateVideoCall(props.appointmentId, props.callType)

    showRoom.value = true
    callState.value = 'calling'

    // 建立 WebSocket 连接
    await connectWebSocket()

    // 创建 WebRTC 连接
    await createPeerConnection()

  } catch (error) {
    console.error('开始通话失败:', error)
    ElMessage.error(getErrorMessage(error))
    cleanup()
  }
}

// 连接 WebSocket
async function connectWebSocket() {
  try {
    // 使用环境变量配置的WebSocket服务器地址
    const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
    const wsUrl = `${wsBaseUrl}${videoCallStore.wsUrl}`

    console.log('连接 WebSocket:', wsUrl)
    websocket.value = new WebSocket(wsUrl)

    websocket.value.onopen = () => {
      console.log('WebSocket 已连接，发送加入消息')

      // 发送加入消息
      sendSignalingMessage({
        type: 'join',
        data: {
          session_id: videoCallStore.sessionId,
          user_id: getUserId(),
          user_type: getUserType()
        }
      })
    }

    websocket.value.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data)
        await handleSignalingMessage(message)
      } catch (error) {
        console.error('处理 WebSocket 消息失败:', error)
      }
    }

    websocket.value.onerror = (error) => {
      console.error('WebSocket 错误:', error)
    }

    websocket.value.onclose = () => {
      console.log('WebSocket 已关闭')
      if (callState.value !== 'ending') {
        ElMessage.warning('连接已断开')
        handleHangup()
      }
    }
  } catch (error) {
    console.error('连接 WebSocket 失败:', error)
  }
}

// 处理信令消息
async function handleSignalingMessage(message) {
  const { type, data } = message

  switch (type) {
    case 'offer':
      await handleRemoteOffer(data)
      break
    case 'answer':
      await handleRemoteAnswer(data)
      break
    case 'ice_candidate':
      await handleRemoteIceCandidate(data)
      break
    case 'joined':
      callState.value = 'connected'
      hasRemoteStream.value = true
      break
    case 'leave':
    case 'end':
      ElMessage.info('对方已结束通话')
      handleHangup()
      break
    case 'error':
      ElMessage.error(data.message || '通话错误')
      break
  }
}

// 创建 WebRTC 连接
async function createPeerConnection() {
  peerConnection.value = new RTCPeerConnection(config)

  // 添加本地流
  localStream.value.getTracks().forEach(track => {
    peerConnection.value.addTrack(track, localStream.value)
  })

  // 监听 ICE 候选
  peerConnection.value.onicecandidate = (event) => {
    if (event.candidate) {
      sendSignalingMessage({
        type: 'ice_candidate',
        data: {
          session_id: videoCallStore.sessionId,
          candidate: event.candidate,
          user_type: getUserType()
        }
      })
    }
  }

  // 监听远程流
  peerConnection.value.ontrack = (event) => {
    if (event.streams && event.streams[0]) {
      remoteStream.value = event.streams[0]

      if (remoteVideoRef.value && props.callType === 'video') {
        remoteVideoRef.value.srcObject = remoteStream.value
      }

      hasRemoteStream.value = true
      videoCallStore.setRemoteStream(remoteStream.value)
    }
  }

  // 监听连接状态
  peerConnection.value.onconnectionstatechange = () => {
    console.log('连接状态:', peerConnection.value.connectionState)

    if (peerConnection.value.connectionState === 'connected') {
      callState.value = 'connected'
    } else if (peerConnection.value.connectionState === 'disconnected' ||
               peerConnection.value.connectionState === 'failed') {
      if (callState.value !== 'ending') {
        handleHangup()
      }
    }
  }

  // 创建 Offer（如果是发起者）
  const offer = await peerConnection.value.createOffer()
  await peerConnection.value.setLocalDescription(offer)

  sendSignalingMessage({
    type: 'offer',
    data: {
      session_id: videoCallStore.sessionId,
      sdp: offer,
      user_type: getUserType()
    }
  })
}

// 处理远程 Offer
async function handleRemoteOffer(data) {
  try {
    await peerConnection.value.setRemoteDescription(
      new RTCSessionDescription(data.sdp)
    )

    const answer = await peerConnection.value.createAnswer()
    await peerConnection.value.setLocalDescription(answer)

    sendSignalingMessage({
      type: 'answer',
      data: {
        session_id: videoCallStore.sessionId,
        sdp: answer,
        user_type: getUserType()
      }
    })
  } catch (error) {
    console.error('处理远程 Offer 失败:', error)
  }
}

// 处理远程 Answer
async function handleRemoteAnswer(data) {
  try {
    await peerConnection.value.setRemoteDescription(
      new RTCSessionDescription(data.sdp)
    )
  } catch (error) {
    console.error('处理远程 Answer 失败:', error)
  }
}

// 处理远程 ICE 候选
async function handleRemoteIceCandidate(data) {
  try {
    await peerConnection.value.addIceCandidate(new RTCIceCandidate(data.candidate))
  } catch (error) {
    console.error('添加 ICE 候选失败:', error)
  }
}

// 发送信令消息
function sendSignalingMessage(message) {
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    websocket.value.send(JSON.stringify(message))
  } else {
    console.warn('WebSocket 未连接，无法发送消息:', message)
  }
}

// 获取用户ID
function getUserId() {
  return userStore.user?.id
}

// 获取用户类型
function getUserType() {
  return userStore.isCounselor ? 'counselor' : 'user'
}

// 切换静音
function toggleMute() {
  videoCallStore.toggleMute()

  if (localStream.value) {
    const audioTrack = localStream.value.getAudioTracks()[0]
    if (audioTrack) {
      audioTrack.enabled = !audioTrack.enabled
    }
  }
}

// 切换视频
function toggleVideo() {
  videoCallStore.toggleVideo()

  if (localStream.value) {
    const videoTrack = localStream.value.getVideoTracks()[0]
    if (videoTrack) {
      videoTrack.enabled = !videoTrack.enabled
    }
  }
}

// 挂断
function hangup() {
  if (callState.value === 'connected') {
    showHangupConfirm.value = true
  } else {
    handleHangup()
  }
}

// 确认挂断
async function confirmHangup() {
  showHangupConfirm.value = false
  await handleHangup()
}

// 取消挂断
function handleHangupCancel() {
  showHangupConfirm.value = false
}

// 处理挂断
async function handleHangup() {
  callState.value = 'ending'

  try {
    await videoCallStore.endCall('user_ended')
  } catch (error) {
    console.error('结束通话失败:', error)
  }

  cleanup()
}

// 清理资源
function cleanup() {
  // 停止媒体流
  if (localStream.value) {
    localStream.value.getTracks().forEach(track => track.stop())
    localStream.value = null
  }

  if (remoteStream.value) {
    remoteStream.value.getTracks().forEach(track => track.stop())
    remoteStream.value = null
  }

  // 关闭 WebRTC 连接
  if (peerConnection.value) {
    peerConnection.value.close()
    peerConnection.value = null
  }

  // 关闭 WebSocket
  if (websocket.value) {
    websocket.value.close()
    websocket.value = null
  }

  // 重置状态
  hasRemoteStream.value = false
  showRoom.value = false
  showHangupConfirm.value = false
  callState.value = 'idle'

  videoCallStore.resetState()
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.call-room-dialog {
  :deep(.el-dialog__header) {
    display: none;
  }

  :deep(.el-dialog__body) {
    padding: 0;
    height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  :deep(.el-dialog__footer) {
    display: none;
  }
}

.call-content {
  height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.call-status {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 12px 24px;
  border-radius: 20px;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  z-index: 10;

  .el-icon {
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.remote-media {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  .video-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .remote-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    background: #000;

    &.active {
      opacity: 1;
    }

    &:not(.active) {
      opacity: 0;
    }
  }

  .placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    color: rgba(255, 255, 255, 0.6);

    .el-icon {
      opacity: 0.5;
    }

    p {
      margin: 0;
      font-size: 18px;
    }
  }

  .voice-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    color: white;

    .el-icon {
      opacity: 0.8;
      animation: pulse 2s ease-in-out infinite;
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.8;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

.local-media {
  position: absolute;
  bottom: 120px;
  right: 20px;
  width: 160px;
  height: 120px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  background: #000;
}

.local-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scaleX(-1); // 镜像翻转
}

.call-controls {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 50px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);

  .el-button {
    width: 56px;
    height: 56px;
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);

    &:hover {
      background: rgba(255, 255, 255, 0.3);
      border-color: rgba(255, 255, 255, 0.5);
    }

    &.el-button--danger {
      background: rgba(245, 108, 108, 0.2);
      border-color: rgba(245, 108, 108, 0.3);

      &:hover {
        background: rgba(245, 108, 108, 0.4);
        border-color: rgba(245, 108, 108, 0.5);
      }
    }
  }

  .duration-display {
    display: flex;
    align-items: center;
    gap: 8px;
    color: white;
    font-size: 18px;
    font-weight: 600;
    padding: 0 16px;
    min-width: 80px;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .local-media {
    width: 120px;
    height: 90px;
    bottom: 100px;
    right: 10px;
  }

  .call-controls {
    bottom: 20px;
    padding: 12px 16px;
    gap: 12px;

    .el-button {
      width: 48px;
      height: 48px;
    }

    .duration-display {
      font-size: 16px;
      min-width: 60px;
    }
  }
}
</style>
