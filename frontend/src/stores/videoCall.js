/**
 * 视频通话状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { initiateCall, joinCall, endCall as endCallApi } from '@/api/videoCall'

export const useVideoCallStore = defineStore('videoCall', () => {
  // 状态
  const currentCall = ref(null)
  const callStatus = ref('idle') // idle/calling/connected/ended/error
  const callType = ref('video') // video/voice
  const localStream = ref(null)
  const remoteStream = ref(null)
  const isMuted = ref(false)
  const isVideoOff = ref(false)
  const duration = ref(0)
  const roomId = ref(null)
  const sessionId = ref(null)
  const errorMessage = ref(null)
  const wsUrl = ref(null)
  const wsToken = ref(null)
  const devicePreferences = ref({ cameraId: '', micId: '', speakerId: '' })

  // 计时器
  let durationTimer = null

  // 计算属性
  const isCalling = computed(() => callStatus.value === 'calling')
  const isConnected = computed(() => callStatus.value === 'connected')
  const canToggleVideo = computed(() => callType.value === 'video')

  // Actions
  async function initiateVideoCall(appointmentId, type = 'video') {
    try {
      callType.value = type
      callStatus.value = 'initiating'
      errorMessage.value = null

      const response = await initiateCall(appointmentId, type)
      const data = response.data

      currentCall.value = data
      sessionId.value = data.session_id
      roomId.value = data.room_id
      wsUrl.value = data.ws_url
      wsToken.value = data.ws_token

      if (data.is_new) {
        callStatus.value = 'calling'
      } else {
        callStatus.value = data.call_status === 'in_progress' ? 'connected' : 'calling'
      }

      startDurationTimer()

      return data
    } catch (error) {
      console.error('发起通话失败:', error)
      callStatus.value = 'error'
      errorMessage.value = error.response?.data?.detail || '发起通话失败'
      throw error
    }
  }

  async function joinVideoCall(sessionIdParam) {
    try {
      callStatus.value = 'joining'
      errorMessage.value = null

      const response = await joinCall(sessionIdParam)
      const data = response.data

      sessionId.value = data.session_id
      roomId.value = data.room_id
      wsUrl.value = data.ws_url
      wsToken.value = data.ws_token
      callStatus.value = 'connected'

      startDurationTimer()

      return data
    } catch (error) {
      console.error('加入通话失败:', error)
      callStatus.value = 'error'
      errorMessage.value = error.response?.data?.detail || '加入通话失败'
      throw error
    }
  }

  async function endCall(reason = 'user_ended') {
    try {
      if (sessionId.value) {
        await endCallApi(sessionId.value, reason)
      }

      stopDurationTimer()
      callStatus.value = 'ended'

      // 清理媒体流
      if (localStream.value) {
        localStream.value.getTracks().forEach(track => track.stop())
        localStream.value = null
      }

      remoteStream.value = null

      return true
    } catch (error) {
      console.error('结束通话失败:', error)
      errorMessage.value = error.response?.data?.detail || '结束通话失败'
      return false
    }
  }

  function toggleMute() {
    if (localStream.value) {
      const audioTrack = localStream.value.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled
        isMuted.value = !audioTrack.enabled
      }
    }
  }

  function toggleVideo() {
    if (localStream.value && callType.value === 'video') {
      const videoTrack = localStream.value.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled
        isVideoOff.value = !videoTrack.enabled
      }
    }
  }

  function setLocalStream(stream) {
    localStream.value = stream
    // 初始化静音状态
    if (stream) {
      const audioTrack = stream.getAudioTracks()[0]
      if (audioTrack) {
        isMuted.value = !audioTrack.enabled
      }
      const videoTrack = stream.getVideoTracks()[0]
      if (videoTrack) {
        isVideoOff.value = !videoTrack.enabled
      }
    }
  }

  function setRemoteStream(stream) {
    remoteStream.value = stream
  }

  function updateStatus(status) {
    callStatus.value = status
  }

  function setError(message) {
    errorMessage.value = message
    callStatus.value = 'error'
  }

  function setDevicePreferences(prefs) {
    devicePreferences.value = prefs || {}
  }

  function startDurationTimer() {
    stopDurationTimer()
    duration.value = 0
    durationTimer = setInterval(() => {
      duration.value++
    }, 1000)
  }

  function stopDurationTimer() {
    if (durationTimer) {
      clearInterval(durationTimer)
      durationTimer = null
    }
  }

  function resetState() {
    stopDurationTimer()

    currentCall.value = null
    callStatus.value = 'idle'
    callType.value = 'video'
    localStream.value = null
    remoteStream.value = null
    isMuted.value = false
    isVideoOff.value = false
    duration.value = 0
    roomId.value = null
    sessionId.value = null
    errorMessage.value = null
    wsUrl.value = null
    wsToken.value = null
  }

  return {
    // 状态
    currentCall,
    callStatus,
    callType,
    localStream,
    remoteStream,
    isMuted,
    isVideoOff,
    duration,
    roomId,
    sessionId,
    errorMessage,
    wsUrl,
    wsToken,
    devicePreferences,

    // 计算属性
    isCalling,
    isConnected,
    canToggleVideo,

    // Actions
    initiateVideoCall,
    joinVideoCall,
    endCall,
    toggleMute,
    toggleVideo,
    setLocalStream,
    setRemoteStream,
    updateStatus,
    setError,
    setDevicePreferences,
    resetState
  }
})
