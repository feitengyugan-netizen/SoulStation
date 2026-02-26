// 咨询对话相关API
import request from './index'

/**
 * 获取咨询师订单列表
 * @param {Object} params
 * @param {string} params.status - 订单状态筛选
 */
export function getCounselorOrders(params) {
  return request({
    url: '/consultation/counselor/orders',
    method: 'get',
    params
  })
}

/**
 * 处理预约订单
 * @param {string} id - 订单ID
 * @param {Object} data
 * @param {string} data.action - 动作: agree/reject
 * @param {string} data.reason - 拒绝理由（可选）
 */
export function handleOrder(id, data) {
  return request({
    url: `/consultation/order/${id}/handle`,
    method: 'post',
    data
  })
}

/**
 * 获取对话消息
 * @param {string} appointmentId - 订单ID
 * @param {number} params.lastId - 最后一条消息ID（用于增量获取）
 */
export function getMessages(appointmentId, params) {
  return request({
    url: `/consultation/${appointmentId}/messages`,
    method: 'get',
    params
  })
}

/**
 * 发送消息
 * @param {string} appointmentId - 订单ID
 * @param {Object} data
 * @param {string} data.content - 消息内容
 * @param {string} data.type - 消息类型
 */
export function sendMessage(appointmentId, data) {
  return request({
    url: `/consultation/${appointmentId}/message`,
    method: 'post',
    data
  })
}

/**
 * 上传文件
 * @param {File} file - 文件
 */
export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/consultation/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * 结束咨询
 * @param {string} appointmentId - 订单ID
 */
export function endConsultation(appointmentId) {
  return request({
    url: `/consultation/${appointmentId}/end`,
    method: 'post'
  })
}

/**
 * 添加咨询备注
 * @param {string} appointmentId - 订单ID
 * @param {Object} data
 * @param {string} data.note - 备注内容
 */
export function addConsultationNote(appointmentId, data) {
  return request({
    url: `/consultation/${appointmentId}/note`,
    method: 'post',
    data
  })
}
