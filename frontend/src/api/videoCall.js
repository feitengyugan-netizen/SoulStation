// 视频通话相关 API
import request from './index'

/**
 * 获取 WebRTC 配置
 */
export function getWebRTCConfig() {
  return request({
    url: '/video-call/config',
    method: 'get'
  })
}

/**
 * 发起通话
 * @param {number} appointmentId - 预约ID
 * @param {string} callType - 通话类型 video/voice
 */
export function initiateCall(appointmentId, callType) {
  return request({
    url: '/video-call/call/initiate',
    method: 'post',
    data: {
      appointment_id: appointmentId,
      call_type: callType
    }
  })
}

/**
 * 加入通话
 * @param {number} sessionId - 会话ID
 */
export function joinCall(sessionId) {
  return request({
    url: `/video-call/call/${sessionId}/join`,
    method: 'post'
  })
}

/**
 * 结束通话
 * @param {number} sessionId - 会话ID
 * @param {string} reason - 结束原因
 */
export function endCall(sessionId, reason = 'user_ended') {
  return request({
    url: `/video-call/call/${sessionId}/end`,
    method: 'post',
    data: {
      end_reason: reason
    }
  })
}

/**
 * 获取通话状态
 * @param {number} sessionId - 会话ID
 */
export function getCallStatus(sessionId) {
  return request({
    url: `/video-call/call/${sessionId}/status`,
    method: 'get'
  })
}

/**
 * 获取通话历史
 * @param {number} appointmentId - 预约ID
 */
export function getCallHistory(appointmentId) {
  return request({
    url: `/video-call/appointment/${appointmentId}/call-history`,
    method: 'get'
  })
}

/**
 * 获取当前活跃通话
 * @param {number} appointmentId - 预约ID
 */
export function getActiveCall(appointmentId) {
  return request({
    url: `/video-call/appointment/${appointmentId}/active-call`,
    method: 'get'
  })
}
