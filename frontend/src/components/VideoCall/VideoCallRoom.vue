<template>
  <div class="video-call-room">
    <!-- 加载中 -->
    <div v-if="callStatus === 'initiating'" class="call-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>正在初始化通话...</p>
    </div>

    <!-- 呼叫中 -->
    <div v-else-if="callStatus === 'calling'" class="call-calling">
      <div class="calling-animation">
        <div class="wave"></div>
        <div class="wave"></div>
        <div class="wave"></div>
      </div>
      <p>正在呼叫对方...</p>
      <el-button @click="handleCancelCall" type="danger">取消</el-button>
    </div>

    <!-- 通话中 -->
    <div v-else-if="callStatus === 'connected' || callStatus === 'joining'" class="call-container">
      <!-- 远程视频（主屏幕） -->
      <div class="remote-video">
        <video
          ref="remoteVideoRef"
          autoplay
          playsinline
          :muted="false"
        ></video>
        <div v-if="!remoteStream" class="no-video">
          <el-icon><User /></el-icon>
          <p>对方还未加入</p>
        </div>
      </div>

      <!-- 本地视频（画中画） -->
      <div v-if="callType === 'video'" class="local-video">
        <video
          ref="localVideoRef"
          autoplay
          playsinline
          muted
        ></video>
      </div>

      <!-- 通话控制 -->
      <CallControls
        :duration="duration"
        :is-muted="isMuted"
        :is-video-off="isVideoOff"
        :call-type="callType"
        @toggle-mute="handleToggleMute"
        @toggle-video="handleToggleVideo"
        @end-call="handleEndCall"
      />

      <!-- 连接状态指示 -->
      <div class="connection-status" :class="{ connected: isConnected }">
        <el-icon><Connection /></el-icon>
      </div>
    </div>

    <!-- 错误 -->
    <div v-else-if="callStatus === 'error'" class="call-error">
      <el-icon><CircleClose /></el-icon>
      <p>{{ errorMessage || '通话发生错误' }}</p>
      <el-button @click="$emit('close')">关闭</el-button>
    </div>

    <!-- 已结束 -->
    <div v-else-if="callStatus === 'ended'" class="call-ended">
      <el-icon><SuccessFilled /></el-icon>
      <p>通话已结束</p>
      <p class="duration">通话时长: {{ formattedDuration }}</p>
      <el-button @click="$emit('close')">关闭</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Loading,
  User,
  Connection,
  CircleClose,
  SuccessFilled
} from '@element-plus/icons-vue'
import CallControls from './CallControls.vue'
import { useVideoCallStore } from '@/stores/videoCall'
import { useWebRTC } from '@/composables/useWebRTC.js'
import { formatDuration, diagnoseMediaPermissions } from '@/utils/webrtc'

const props = defineProps({
  appointmentId: {
    type: Number,
    required: true
  },
  sessionId: {
    type: Number,
    default: null
  },
  isInitiator: {
    type: Boolean,
    default: false
  },
  callTypeProp: {
    type: String,
    default: 'video'
  }
})

const emit = defineEmits(['close', 'call-ended'])

const videoCallStore = useVideoCallStore()

// 使用 WebRTC composable
const {
  localStream,
  remoteStream,
  error: webrtcError,
  isConnected,
  wsReady,
  initWebRTC,
  connectWebSocket,
  createOffer,
  createAnswer,
  toggleMute,
  toggleVideo,
  cleanup
} = useWebRTC()

// 视频元素引用
const localVideoRef = ref(null)
const remoteVideoRef = ref(null)

// 从 store 获取状态
const callStatus = computed(() => videoCallStore.callStatus)
const callType = computed(() => videoCallStore.callType)
const duration = computed(() => videoCallStore.duration)
const isMuted = computed(() => videoCallStore.isMuted)
const isVideoOff = computed(() => videoCallStore.isVideoOff)
const errorMessage = computed(() => videoCallStore.errorMessage)

const formattedDuration = computed(() => formatDuration(duration.value))

// 监听本地流变化
watch(localStream, (newStream) => {
  if (newStream && localVideoRef.value) {
    localVideoRef.value.srcObject = newStream
  }
})

// 监听远程流变化
watch(remoteStream, (newStream) => {
  if (newStream && remoteVideoRef.value) {
    remoteVideoRef.value.srcObject = newStream
  }
})

// 初始化通话
async function initializeCall() {
  try {
    console.log('VideoCallRoom 初始化:', {
      props: props,
      sessionId: props.sessionId,
      videoCallStoreSessionId: videoCallStore.sessionId,
      callType: callType.value,
      isInitiator: props.isInitiator
    })

    // 用 props 中的 callType 同步 store（防止 store 被意外重置）
    if (props.callTypeProp && videoCallStore.callType !== props.callTypeProp) {
      videoCallStore.callType = props.callTypeProp
    }

    // 如果 wsUrl 未设置，需要发起通话
    if (props.isInitiator && !videoCallStore.wsUrl) {
      console.log('wsUrl 未设置，重新调用 initiateVideoCall, type:', props.callTypeProp)
      await videoCallStore.initiateVideoCall(props.appointmentId, props.callTypeProp)
    }

    // 诊断媒体权限（输出详细诊断信息）
    const diagnosis = await diagnoseMediaPermissions()
    console.log('媒体权限诊断:', diagnosis)

    // 如果是 NotAllowedError，提供更详细的系统级排查提示
    if (!diagnosis.isSecureContext) {
      ElMessage.error('当前页面不是安全连接，请使用 localhost 或 HTTPS 访问')
      return
    }

    // 初始化 WebRTC
    await initWebRTC(callType.value)

    // 连接 WebSocket
    connectWebSocket()

    // 如果是发起者，等 WebSocket 就绪后再创建 offer
    if (props.isInitiator) {
      const unwatch = watch(wsReady, async (ready) => {
        if (!ready) return
        unwatch()
        try {
          await createOffer()
        } catch (err) {
          console.error('创建 Offer 失败:', err)
        }
      })
      // 兜底：如果 10 秒还没连上就放弃
      setTimeout(() => {
        if (!wsReady.value) { unwatch(); console.error('WebSocket 连接超时') }
      }, 10000)
    }
  } catch (err) {
    console.error('初始化通话失败:', err)
    ElMessage.error(err.message || '初始化通话失败')
  }
}

// 切换静音
function handleToggleMute() {
  toggleMute()
}

// 切换视频
function handleToggleVideo() {
  toggleVideo()
}

// 取消呼叫
async function handleCancelCall() {
  try {
    await ElMessageBox.confirm('确定要取消通话吗？', '提示', {
      type: 'warning'
    })

    await videoCallStore.endCall('caller_cancelled')
    await cleanup()
    emit('close')
  } catch (error) {
    // 用户取消
  }
}

// 结束通话
async function handleEndCall() {
  try {
    await ElMessageBox.confirm('确定要结束通话吗？', '提示', {
      type: 'warning'
    })

    await videoCallStore.endCall('user_ended')
    await cleanup()
    emit('call-ended', {
      duration: duration.value
    })
  } catch (error) {
    // 用户取消
  }
}

// 组件挂载
onMounted(async () => {
  await initializeCall()
})

// 组件卸载
onUnmounted(async () => {
  await cleanup()
})
</script>

<style lang="scss" scoped>
.video-call-room {
  position: relative;
  width: 100%;
  height: 600px;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
}

.call-loading,
.call-calling,
.call-error,
.call-ended {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #fff;
  gap: 20px;

  .el-icon {
    font-size: 48px;
  }

  p {
    font-size: 18px;
    margin: 0;
  }

  .duration {
    font-size: 14px;
    opacity: 0.8;
  }
}

.call-calling {
  .calling-animation {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;

    .wave {
      width: 10px;
      height: 40px;
      background: #409eff;
      border-radius: 5px;
      animation: wave 1s ease-in-out infinite;

      &:nth-child(2) {
        animation-delay: 0.2s;
      }

      &:nth-child(3) {
        animation-delay: 0.4s;
      }
    }
  }
}

@keyframes wave {
  0%, 100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(2);
  }
}

.call-container {
  position: relative;
  width: 100%;
  height: 100%;

  .remote-video {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #1a1a1a;

    video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .no-video {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      display: flex;
      flex-direction: column;
      align-items: center;
      color: #666;

      .el-icon {
        font-size: 64px;
        margin-bottom: 10px;
      }
    }
  }

  .local-video {
    position: absolute;
    bottom: 100px;
    right: 20px;
    width: 200px;
    height: 150px;
    background: #000;
    border: 2px solid #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
    z-index: 5;

    video {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .connection-status {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #f56c6c;
    z-index: 5;

    &.connected {
      color: #67c23a;
    }

    .el-icon {
      font-size: 24px;
    }
  }
}
</style>
