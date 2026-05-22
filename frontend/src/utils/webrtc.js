/**
 * WebRTC 工具函数
 */

// ICE 服务器配置
export const ICE_SERVERS = [
  { urls: 'stun:stun.l.google.com:19302' },
  { urls: 'stun:stun1.l.google.com:19302' },
  { urls: 'stun:stun2.l.google.com:19302' },
  { urls: 'stun:stun3.l.google.com:19302' },
  { urls: 'stun:stun4.l.google.com:19302' }
]

// 媒体约束
export const MEDIA_CONSTRAINTS = {
  video: {
    audio: true,
    video: {
      width: { ideal: 1280 },
      height: { ideal: 720 },
      frameRate: { ideal: 30 }
    }
  },
  voice: {
    audio: true,
    video: false
  }
}

/**
 * 格式化时长
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的时长
 */
export function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }
  return `${minutes}:${String(secs).padStart(2, '0')}`
}

/**
 * 检查浏览器是否支持 WebRTC
 * @returns {boolean} 是否支持
 */
export function checkWebRTCSupport() {
  const supported = !!(
    window.RTCPeerConnection ||
    window.mozRTCPeerConnection ||
    window.webkitRTCPeerConnection
  )

  if (!supported) {
    console.error('当前浏览器不支持 WebRTC')
  }

  return supported
}

/**
 * 诊断媒体权限问题
 * @returns {Promise<Object>} 诊断结果和修复建议
 */
export async function diagnoseMediaPermissions() {
  const result = {
    isSecureContext: window.isSecureContext,
    hasMediaDevices: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
    hasCamera: false,
    hasMicrophone: false,
    canAccessCamera: false,
    canAccessMicrophone: false,
    errors: [],
    suggestions: []
  }

  // 1. 检查安全上下文
  if (!result.isSecureContext) {
    result.errors.push('当前页面不是安全上下文(非HTTPS或非localhost)')
    result.suggestions.push('请通过 localhost 或 HTTPS 访问页面，否则浏览器会阻止摄像头/麦克风')
    return result
  }

  // 2. 检查 mediaDevices API
  if (!result.hasMediaDevices) {
    result.errors.push('浏览器不支持 mediaDevices API')
    result.suggestions.push('请使用 Chrome 80+、Edge 80+ 或 Firefox 75+ 浏览器')
    return result
  }

  // 3. 检查设备列表（不需要权限）
  try {
    const devices = await navigator.mediaDevices.enumerateDevices()
    result.hasCamera = devices.some(d => d.kind === 'videoinput')
    result.hasMicrophone = devices.some(d => d.kind === 'audioinput')

    if (!result.hasMicrophone) {
      result.errors.push('未检测到麦克风设备')
    }
    if (!result.hasCamera) {
      result.errors.push('未检测到摄像头设备')
    }
  } catch (e) {
    result.errors.push('无法获取设备列表: ' + e.message)
  }

  // 4. 尝试获取音频权限（最小权限）
  try {
    const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
    result.canAccessMicrophone = true
    audioStream.getTracks().forEach(t => t.stop())
  } catch (e) {
    result.canAccessMicrophone = false
    if (e.name === 'NotAllowedError') {
      result.errors.push('麦克风权限被拒绝 (NotAllowedError)')
      result.suggestions.push(
        'Windows 设置 → 隐私与安全性 → 麦克风 → 确保"麦克风访问权限"已开启',
        'Windows 设置 → 隐私与安全性 → 麦克风 → 确保"允许应用访问麦克风"已开启',
        '检查列表中的浏览器是否已单独开启',
        '设置修改后请重启浏览器'
      )
    } else if (e.name === 'NotFoundError') {
      result.errors.push('系统找不到可用的麦克风硬件')
    } else {
      result.errors.push(`麦克风访问失败: ${e.name} - ${e.message}`)
    }
  }

  // 5. 尝试获取摄像头权限
  try {
    const videoStream = await navigator.mediaDevices.getUserMedia({ audio: false, video: true })
    result.canAccessCamera = true
    videoStream.getTracks().forEach(t => t.stop())
  } catch (e) {
    result.canAccessCamera = false
    if (e.name === 'NotAllowedError') {
      result.errors.push('摄像头权限被拒绝 (NotAllowedError)')
      result.suggestions.push(
        'Windows 设置 → 隐私与安全性 → 摄像头 → 确保"摄像头访问权限"已开启',
        'Windows 设置 → 隐私与安全性 → 摄像头 → 确保"允许应用访问摄像头"已开启',
        '检查列表中的浏览器是否已单独开启',
        '设置修改后请重启浏览器'
      )
    } else if (e.name === 'NotFoundError') {
      result.errors.push('系统找不到可用的摄像头硬件')
    } else {
      result.errors.push(`摄像头访问失败: ${e.name} - ${e.message}`)
    }
  }

  return result
}

/**
 * 检查是否有摄像头和麦克风权限（简单版，仅检查不诊断）
 * @param {boolean} needsVideo - 是否需要视频设备（默认true）
 * @returns {Promise<Object>} 权限状态
 */
export async function checkMediaPermissions(needsVideo = true) {
  try {
    const constraints = needsVideo
      ? { audio: true, video: true }
      : { audio: true, video: false }

    const stream = await navigator.mediaDevices.getUserMedia(constraints)
    const devices = await navigator.mediaDevices.enumerateDevices()

    const audioInputs = devices.filter(device => device.kind === 'audioinput')
    const videoInputs = devices.filter(device => device.kind === 'videoinput')

    stream.getTracks().forEach(track => track.stop())

    return {
      hasAudio: audioInputs.length > 0,
      hasVideo: videoInputs.length > 0,
      audioCount: audioInputs.length,
      videoCount: videoInputs.length,
      granted: true
    }
  } catch (error) {
    console.error('媒体权限检查失败:', error)
    return {
      hasAudio: false,
      hasVideo: false,
      audioCount: 0,
      videoCount: 0,
      granted: false,
      error: error.name
    }
  }
}

/**
 * 获取错误消息
 * @param {Error} error - 错误对象
 * @returns {string} 用户友好的错误消息
 */
export function getErrorMessage(error) {
  const errorMessages = {
    'NotAllowedError': '摄像头/麦克风权限被拒绝。请检查：1) 浏览器地址栏左侧点击允许权限 2) Windows设置 → 隐私与安全性 → 摄像头/麦克风 → 确保已开启',
    'NotFoundError': '未检测到摄像头或麦克风设备。请确保您的设备有摄像头和麦克风，然后重试。',
    'NotReadableError': '摄像头或麦克风被其他应用占用。请关闭其他使用这些设备的应用，然后重试。',
    'OverconstrainedError': '设备不满足通话要求。请尝试使用其他浏览器或设备。',
    'SecurityError': '由于安全限制，无法访问媒体设备。请确保您在HTTPS或localhost环境下访问。',
    'TypeError': '参数配置错误，请联系技术支持。',
    'InvalidStateError': '媒体设备状态异常，请刷新页面后重试。'
  }

  const message = errorMessages[error.name] || errorMessages[error.code] || `发生错误: ${error.message || '未知错误'}`

  console.error('WebRTC错误详情:', {
    name: error.name,
    message: error.message,
    code: error.code,
    toString: error.toString()
  })

  return message
}

/**
 * 创建 RTCPeerConnection 配置
 * @returns {Object} RTCConfiguration
 */
export function createRTCConfiguration() {
  return {
    iceServers: ICE_SERVERS,
    iceCandidatePoolSize: 10
  }
}

/**
 * 获取媒体约束
 * @param {string} callType - 通话类型（video/voice）
 * @returns {Object} 媒体约束
 */
export function getMediaConstraints(callType) {
  return MEDIA_CONSTRAINTS[callType] || MEDIA_CONSTRAINTS.video
}

/**
 * 记录 WebRTC 统计信息
 * @param {RTCPeerConnection} peerConnection - WebRTC 连接
 * @returns {Promise<Object>} 统计信息
 */
export async function getRTCStats(peerConnection) {
  try {
    const stats = await peerConnection.getStats(null)
    const result = {
      bytesReceived: 0,
      bytesSent: 0,
      packetsReceived: 0,
      packetsSent: 0
    }

    stats.forEach(report => {
      if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
        result.bytesReceived += report.bytesReceived || 0
        result.packetsReceived += report.packetsReceived || 0
      }
      if (report.type === 'outbound-rtp' && report.mediaType === 'video') {
        result.bytesSent += report.bytesSent || 0
        result.packetsSent += report.packetsSent || 0
      }
    })

    return result
  } catch (error) {
    console.error('获取 WebRTC 统计信息失败:', error)
    return null
  }
}
