/**
 * WebRTC 核心逻辑 composable (修复版)
 */
import { ref, onUnmounted } from 'vue'
import { useVideoCallStore } from '@/stores/videoCall'
import { useUserStore } from '@/stores/user'
import { checkWebRTCSupport, getMediaConstraints, createRTCConfiguration, getErrorMessage, checkMediaPermissions } from '@/utils/webrtc'

export function useWebRTC() {
  const videoCallStore = useVideoCallStore()

  const localStream = ref(null)
  const remoteStream = ref(null)
  const peerConnection = ref(null)
  const websocket = ref(null)
  const error = ref(null)
  const isConnected = ref(false)

  let reconnectTimer = null
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 3

  /**
   * 初始化 WebRTC (增强版错误处理)
   */
  async function initWebRTC(callType = 'video') {
    try {
      // 检查浏览器支持
      if (!checkWebRTCSupport()) {
        throw new Error('BROWSER_NOT_SUPPORTED')
      }

      // 先检查设备是否可用
      const permissions = await checkMediaPermissions()

      if (!permissions.granted) {
        if (permissions.error === 'NotAllowedError') {
          throw new Error('PERMISSION_DENIED')
        } else if (permissions.error === 'NotFoundError') {
          throw new Error('DEVICE_NOT_FOUND')
        } else {
          throw new Error('PERMISSION_CHECK_FAILED')
        }
      }

      // 根据通话类型检查必要的设备
      if (callType === 'video' && !permissions.hasVideo) {
        throw new Error('NO_VIDEO_DEVICE')
      }

      if (!permissions.hasAudio) {
        throw new Error('NO_AUDIO_DEVICE')
      }

      // 获取本地媒体流
      const constraints = getMediaConstraints(callType)
      localStream.value = await navigator.mediaDevices.getUserMedia(constraints)

      // 更新 store
      videoCallStore.setLocalStream(localStream.value)

      // 创建 PeerConnection
      peerConnection.value = new RTCPeerConnection(createRTCConfiguration())

      // 添加本地流到连接
      localStream.value.getTracks().forEach(track => {
        peerConnection.value.addTrack(track, localStream.value)
      })

      // 监听远程流
      peerConnection.value.ontrack = (event) => {
        console.log('收到远程流:', event)
        if (event.streams && event.streams[0]) {
          remoteStream.value = event.streams[0]
          videoCallStore.setRemoteStream(remoteStream.value)
        }
      }

      // 监听 ICE 候选
      peerConnection.value.onicecandidate = (event) => {
        if (event.candidate) {
          sendIceCandidate(event.candidate)
        }
      }

      // 监听连接状态
      peerConnection.value.onconnectionstatechange = () => {
        console.log('连接状态:', peerConnection.value.connectionState)
        if (peerConnection.value.connectionState === 'connected') {
          isConnected.value = true
          videoCallStore.updateStatus('connected')
        } else if (peerConnection.value.connectionState === 'disconnected') {
          isConnected.value = false
          handleDisconnect()
        } else if (peerConnection.value.connectionState === 'failed') {
          isConnected.value = false
          error.value = '连接失败'
        }
      }

      // 监听 ICE 状态
      peerConnection.value.oniceconnectionstatechange = () => {
        console.log('ICE 状态:', peerConnection.value.iceConnectionState)
        if (peerConnection.value.iceConnectionState === 'disconnected') {
          handleDisconnect()
        }
      }

      return localStream.value
    } catch (err) {
      console.error('初始化 WebRTC 失败:', err)

      // 设置用户友好的错误消息
      if (err.message === 'BROWSER_NOT_SUPPORTED') {
        error.value = '当前浏览器不支持视频通话功能，请使用现代浏览器（Chrome 80+、Firefox 75+、Edge 80+）'
      } else if (err.message === 'PERMISSION_DENIED') {
        error.value = '您拒绝了摄像头和麦克风权限。请在浏览器地址栏点击允许权限，然后重试。'
      } else if (err.message === 'DEVICE_NOT_FOUND') {
        error.value = '未检测到摄像头或麦克风设备。请确保您的设备有摄像头和麦克风，然后重试。'
      } else if (err.message === 'NO_VIDEO_DEVICE') {
        error.value = '未检测到摄像头设备，无法进行视频通话。请使用语音通话或检查摄像头连接。'
      } else if (err.message === 'NO_AUDIO_DEVICE') {
        error.value = '未检测到麦克风设备，无法进行通话。请确保您的设备有麦克风或已连接耳麦。'
      } else if (err.name === 'NotAllowedError') {
        error.value = '您拒绝了摄像头和麦克风权限。请在浏览器地址栏点击允许权限，然后重试。'
      } else if (err.name === 'NotFoundError') {
        error.value = '未检测到摄像头或麦克风设备。请确保您的设备有摄像头和麦克风，然后重试。'
      } else if (err.name === 'NotReadableError') {
        error.value = '摄像头或麦克风被其他应用占用。请关闭其他使用这些设备的应用，然后重试。'
      } else if (err.name === 'SecurityError') {
        error.value = '由于安全限制，无法访问媒体设备。请确保您在HTTPS或localhost环境下访问。'
      } else {
        error.value = getErrorMessage(err)
      }

      throw err
    }
  }

  // ... 其余代码保持不变
  function connectWebSocket() {
    const wsUrl = videoCallStore.wsUrl
    if (!wsUrl) {
      error.value = '未找到 WebSocket 连接地址'
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const fullWsUrl = `${protocol}//${host}${wsUrl}`

    console.log('连接 WebSocket:', fullWsUrl)
    websocket.value = new WebSocket(fullWsUrl)

    websocket.value.onopen = () => {
      console.log('WebSocket 已连接')
      reconnectAttempts.value = 0

      sendMessage({
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
        console.log('收到消息:', message)
        await handleSignalingMessage(message)
      } catch (err) {
        console.error('处理消息失败:', err)
      }
    }

    websocket.value.onerror = (event) => {
      console.error('WebSocket 错误:', event)
      error.value = '网络连接错误'
    }

    websocket.value.onclose = () => {
      console.log('WebSocket 已关闭')
      isConnected.value = false

      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++
        console.log(`尝试重连 (${reconnectAttempts.value}/${maxReconnectAttempts})...`)
        reconnectTimer = setTimeout(() => {
          connectWebSocket()
        }, 2000)
      } else {
        error.value = '连接已断开，请刷新页面重试'
      }
    }
  }

  function createOffer() {
    if (!peerConnection.value) {
      throw new Error('WebRTC 未初始化')
    }

    try {
      const offer = await peerConnection.value.createOffer()
      await peerConnection.value.setLocalDescription(offer)

      sendMessage({
        type: 'offer',
        data: {
          session_id: videoCallStore.sessionId,
          sdp: offer,
          user_id: getUserId(),
          user_type: getUserType()
        }
      })

      console.log('已发送 Offer')
    } catch (err) {
      console.error('创建 Offer 失败:', err)
      throw err
    }
  }

  function createAnswer() {
    if (!peerConnection.value) {
      throw new Error('WebRTC 未初始化')
    }

    try {
      const answer = await peerConnection.value.createAnswer()
      await peerConnection.value.setLocalDescription(answer)

      sendMessage({
        type: 'answer',
        data: {
          session_id: videoCallStore.sessionId,
          sdp: answer,
          user_id: getUserId(),
          user_type: getUserType()
        }
      })

      console.log('已发送 Answer')
    } catch (err) {
      console.error('创建 Answer 失败:', err)
      throw err
    }
  }

  async function handleSignalingMessage(message) {
    const { type, data } = message

    switch (type) {
      case 'offer':
        await handleOffer(data)
        break
      case 'answer':
        await handleAnswer(data)
        break
      case 'ice_candidate':
        await handleIceCandidate(data)
        break
      case 'joined':
        videoCallStore.updateStatus('connected')
        break
      case 'join':
        console.log('用户加入通话:', data)
        break
      case 'leave':
        console.log('用户离开通话:', data)
        break
      case 'end':
        await handleEndCall(data)
        break
      case 'error':
        console.error('收到错误消息:', data)
        error.value = data.message || '发生错误'
        break
    }
  }

  async function handleOffer(data) {
    if (!peerConnection.value) {
      console.error('PeerConnection 未初始化')
      return
    }

    try {
      await peerConnection.value.setRemoteDescription(new RTCSessionDescription(data.sdp))
      await createAnswer()
    } catch (err) {
      console.error('处理 Offer 失败:', err)
    }
  }

  async function handleAnswer(data) {
    if (!peerConnection.value) {
      console.error('PeerConnection 未初始化')
      return
    }

    try {
      await peerConnection.value.setRemoteDescription(new RTCSessionDescription(data.sdp))
    } catch (err) {
      console.error('处理 Answer 失败:', err)
    }
  }

  async function handleIceCandidate(data) {
    if (!peerConnection.value) {
      console.error('PeerConnection 未初始化')
      return
    }

    try {
      await peerConnection.value.addIceCandidate(new RTCIceCandidate(data.candidate))
    } catch (err) {
      console.error('添加 ICE 候选失败:', err)
    }
  }

  async function handleEndCall(data) {
    console.log('通话结束:', data)
    await cleanup()
    videoCallStore.updateStatus('ended')
  }

  function sendIceCandidate(candidate) {
    sendMessage({
      type: 'ice_candidate',
      data: {
        session_id: videoCallStore.sessionId,
        candidate,
        user_type: getUserType()
      }
    })
  }

  function sendMessage(message) {
    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      websocket.value.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket 未连接，无法发送消息')
    }
  }

  function handleDisconnect() {
    console.log('连接已断开')
    isConnected.value = false
  }

  function getUserId() {
    const userStore = useUserStore()
    return userStore.user?.id
  }

  function getUserType() {
    const userStore = useUserStore()
    return userStore.isCounselor ? 'counselor' : 'user'
  }

  function toggleMute() {
    if (localStream.value) {
      const audioTrack = localStream.value.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled
        videoCallStore.toggleMute()
      }
    }
  }

  function toggleVideo() {
    if (localStream.value) {
      const videoTrack = localStream.value.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled
        videoCallStore.toggleVideo()
      }
    }
  }

  async function cleanup() {
    console.log('清理 WebRTC 资源')

    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    if (websocket.value) {
      sendMessage({
        type: 'leave',
        data: {
          session_id: videoCallStore.sessionId,
          user_id: getUserId()
        }
      })

      websocket.value.close()
      websocket.value = null
    }

    if (localStream.value) {
      localStream.value.getTracks().forEach(track => track.stop())
      localStream.value = null
    }

    if (peerConnection.value) {
      peerConnection.value.close()
      peerConnection.value = null
    }

    remoteStream.value = null
    isConnected.value = false
    reconnectAttempts.value = 0
  }

  onUnmounted(() => {
    cleanup()
  })

  return {
    localStream,
    remoteStream,
    error,
    isConnected,
    initWebRTC,
    connectWebSocket,
    createOffer,
    createAnswer,
    toggleMute,
    toggleVideo,
    cleanup
  }
}