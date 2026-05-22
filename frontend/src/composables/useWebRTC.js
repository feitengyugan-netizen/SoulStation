/**
 * WebRTC 核心逻辑 composable
 */
import { ref, onUnmounted } from 'vue'
import { useVideoCallStore } from '@/stores/videoCall'
import { useUserStore } from '@/stores/user'
import { checkWebRTCSupport, getMediaConstraints, createRTCConfiguration, getErrorMessage } from '@/utils/webrtc'

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

  // ICE 候选 + 消息缓冲队列（WebSocket 就绪前暂存）
  const iceBuffer = []
  const messageQueue = []
  const wsReady = ref(false)

  /**
   * 初始化 WebRTC (增强版错误处理)
   */
  async function initWebRTC(callType = 'video') {
    try {
      // 检查浏览器支持
      if (!checkWebRTCSupport()) {
        throw new Error('BROWSER_NOT_SUPPORTED')
      }

      const needsVideo = callType === 'video'

      // 读取设备偏好（由 DeviceCheck 保存）
      let devicePrefs = { cameraId: '', micId: '' }
      try {
        const saved = sessionStorage.getItem('devicePreferences')
        if (saved) devicePrefs = JSON.parse(saved)
      } catch (e) { /* ignore */ }

      // 构建约束，优先使用用户选择的设备
      const makeConstraints = (basic = false) => {
        const audioCfg = devicePrefs.micId ? { deviceId: { exact: devicePrefs.micId } } : true
        if (!needsVideo) return { audio: audioCfg, video: false }
        const videoCfg = devicePrefs.cameraId ? { deviceId: { exact: devicePrefs.cameraId } } : true
        if (basic) return { audio: audioCfg, video: videoCfg }
        return {
          audio: audioCfg,
          video: typeof videoCfg === 'object' ? { ...videoCfg, width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30 } } : {
            width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30 }
          }
        }
      }

      // 一次性获取媒体流并检查设备（避免重复弹出权限提示）
      let stream
      try {
        stream = await navigator.mediaDevices.getUserMedia(makeConstraints(false))
      } catch (mediaErr) {
        // 某些摄像头不支持 720p/30fps 等高级约束，降级使用基础约束重试
        if (mediaErr.name === 'OverconstrainedError' || mediaErr.name === 'TypeError') {
          console.warn('高级媒体约束失败，降级为基础约束重试:', mediaErr.message)
          stream = await navigator.mediaDevices.getUserMedia(makeConstraints(true))
        } else {
          throw mediaErr
        }
      }
      localStream.value = stream

      // 验证设备可用性
      const devices = await navigator.mediaDevices.enumerateDevices()
      const hasAudio = devices.some(d => d.kind === 'audioinput')
      const hasVideo = devices.some(d => d.kind === 'videoinput')

      if (needsVideo && !hasVideo) {
        localStream.value.getTracks().forEach(t => t.stop())
        localStream.value = null
        throw new Error('NO_VIDEO_DEVICE')
      }
      if (!hasAudio) {
        localStream.value.getTracks().forEach(t => t.stop())
        localStream.value = null
        throw new Error('NO_AUDIO_DEVICE')
      }

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
      } else if (err.message === 'NO_VIDEO_DEVICE') {
        error.value = '未检测到摄像头设备，无法进行视频通话。请使用语音通话或检查摄像头连接。'
      } else if (err.message === 'NO_AUDIO_DEVICE') {
        error.value = '未检测到麦克风设备，无法进行通话。请确保您的设备有麦克风或已连接耳麦。'
      } else if (err.name === 'NotAllowedError') {
        error.value = '摄像头/麦克风权限被拒绝。请检查：1) 浏览器地址栏左侧点击允许权限 2) Windows设置 → 隐私与安全性 → 摄像头/麦克风 → 确保已开启'
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

  /**
   * 连接 WebSocket 信令服务器
   */
  function connectWebSocket() {
    const wsPath = videoCallStore.wsUrl
    if (!wsPath) {
      console.error('wsUrl 未设置，无法连接 WebSocket。videoCallStore.wsUrl:', videoCallStore.wsUrl)
      error.value = '未找到 WebSocket 连接地址，请确认通话已成功发起'
      return
    }

    const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
    const fullWsUrl = `${wsBaseUrl}${wsPath}`

    console.log('正在连接 WebSocket:', fullWsUrl)
    console.log('  - wsBaseUrl:', wsBaseUrl)
    console.log('  - wsPath:', wsPath)
    console.log('  - sessionId:', videoCallStore.sessionId)

    let ws
    try {
      ws = new WebSocket(fullWsUrl)
    } catch (e) {
      console.error('创建 WebSocket 失败:', e)
      error.value = `创建 WebSocket 连接失败: ${e.message}`
      return
    }
    websocket.value = ws

    // 连接超时（5秒）
    const connectTimeout = setTimeout(() => {
      if (!wsReady.value && ws.readyState !== WebSocket.OPEN) {
        console.error('WebSocket 连接超时 (5s), readyState:', ws.readyState)
        error.value = 'WebSocket 连接超时，请确认后端服务已启动'
        ws.close()
      }
    }, 5000)

    ws.onopen = () => {
      clearTimeout(connectTimeout)
      console.log('WebSocket 已连接')
      wsReady.value = true
      reconnectAttempts.value = 0

      const userId = getUserId()
      const userType = getUserType()
      const sessionId = videoCallStore.sessionId

      sendMessage({
        type: 'join',
        data: {
          session_id: sessionId,
          user_id: userId,
          user_type: userType
        }
      })

      flushBuffers()
    }

    ws.onmessage = async (event) => {
      try {
        const message = JSON.parse(event.data)
        console.log('收到信令消息:', message.type)
        await handleSignalingMessage(message)
      } catch (err) {
        console.error('处理消息失败:', err)
      }
    }

    ws.onerror = (event) => {
      clearTimeout(connectTimeout)
      console.error('WebSocket 错误, readyState:', ws.readyState)
      // 尝试获取更详细的错误信息
      if (ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
        error.value = 'WebSocket 连接失败，请确认后端服务已启动且端口正确'
      } else {
        error.value = 'WebSocket 连接异常'
      }
    }

    ws.onclose = (event) => {
      clearTimeout(connectTimeout)
      console.log(`WebSocket 已关闭, code: ${event.code}, reason: ${event.reason}`)
      wsReady.value = false
      isConnected.value = false

      if (reconnectAttempts.value < maxReconnectAttempts && event.code !== 1000) {
        reconnectAttempts.value++
        console.log(`尝试重连 (${reconnectAttempts.value}/${maxReconnectAttempts})...`)
        reconnectTimer = setTimeout(() => {
          connectWebSocket()
        }, 2000)
      } else if (event.code !== 1000) {
        error.value = `连接已断开（${event.reason || '未知原因'}），请刷新页面重试`
      }
    }
  }

  /**
   * 创建并发送 Offer
   */
  async function createOffer() {
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

  /**
   * 创建并发送 Answer
   */
  async function createAnswer() {
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

  /**
   * 处理收到的信令消息
   */
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
        // 其他人加入了通话
        console.log('用户加入通话:', data)
        break
      case 'leave':
        // 对方离开了通话
        console.log('对方离开通话:', data)
        break
      case 'end':
        // 通话结束
        await handleEndCall(data)
        break
      case 'error':
        console.error('收到错误消息:', data)
        error.value = data.message || '发生错误'
        break
      default:
        console.warn('未知消息类型:', type)
    }
  }

  /**
   * 处理 Offer
   */
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

  /**
   * 处理 Answer
   */
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

  /**
   * 处理 ICE 候选
   */
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

  /**
   * 处理通话结束
   */
  async function handleEndCall(data) {
    console.log('通话结束:', data)
    await cleanup()
    videoCallStore.updateStatus('ended')
  }

  /**
   * 发送 ICE 候选
   */
  function sendIceCandidate(candidate) {
    const msg = {
      type: 'ice_candidate',
      data: {
        session_id: videoCallStore.sessionId,
        candidate,
        user_type: getUserType()
      }
    }
    if (wsReady.value) {
      websocket.value.send(JSON.stringify(msg))
    } else {
      iceBuffer.push(msg)
    }
  }

  /**
   * 发送消息到 WebSocket（未就绪时排队）
   */
  function sendMessage(message) {
    if (wsReady.value) {
      websocket.value.send(JSON.stringify(message))
    } else {
      messageQueue.push(message)
    }
  }

  /**
   * 清空缓冲队列
   */
  function flushBuffers() {
    while (messageQueue.length > 0) {
      websocket.value.send(JSON.stringify(messageQueue.shift()))
    }
    while (iceBuffer.length > 0) {
      websocket.value.send(JSON.stringify(iceBuffer.shift()))
    }
  }

  /**
   * 处理断开连接
   */
  function handleDisconnect() {
    console.log('连接已断开')
    isConnected.value = false
  }

  /**
   * 获取用户ID
   */
  function getUserId() {
    const userStore = useUserStore()
    return userStore.user?.id || userStore.userInfo?.id
  }

  function getUserType() {
    const userStore = useUserStore()
    return userStore.isCounselor ? 'counselor' : 'user'
  }

  /**
   * 切换静音
   */
  function toggleMute() {
    if (localStream.value) {
      const audioTrack = localStream.value.getAudioTracks()[0]
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled
        videoCallStore.toggleMute()
      }
    }
  }

  /**
   * 切换视频
   */
  function toggleVideo() {
    if (localStream.value) {
      const videoTrack = localStream.value.getVideoTracks()[0]
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled
        videoCallStore.toggleVideo()
      }
    }
  }

  /**
   * 清理资源
   */
  async function cleanup() {
    console.log('清理 WebRTC 资源')

    // 停止重连
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }

    // 关闭 WebSocket
    if (websocket.value) {
      if (wsReady.value) {
        sendMessage({
          type: 'leave',
          data: {
            session_id: videoCallStore.sessionId,
            user_id: getUserId()
          }
        })
      }

      websocket.value.close()
      websocket.value = null
    }

    // 停止本地流
    if (localStream.value) {
      localStream.value.getTracks().forEach(track => track.stop())
      localStream.value = null
    }

    // 关闭 PeerConnection
    if (peerConnection.value) {
      peerConnection.value.close()
      peerConnection.value = null
    }

    remoteStream.value = null
    isConnected.value = false
    reconnectAttempts.value = 0
    wsReady = false
    iceBuffer.length = 0
    messageQueue.length = 0
  }

  // 组件卸载时清理
  onUnmounted(() => {
    cleanup()
  })

  return {
    // 状态
    localStream,
    remoteStream,
    error,
    isConnected,
    wsReady,

    // 方法
    initWebRTC,
    connectWebSocket,
    createOffer,
    createAnswer,
    toggleMute,
    toggleVideo,
    cleanup
  }
}
