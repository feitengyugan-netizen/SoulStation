// 智能问答相关API
import request from './index'

/**
 * 获取对话列表
 * @param {Object} params - 查询参数
 * @param {string} params.tag - 标签筛选（可选）
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getChatList(params) {
  return request({
    url: '/chat/list',
    method: 'get',
    params
  })
}

/**
 * 获取对话详情
 * @param {string} id - 对话ID
 */
export function getChatDetail(id) {
  return request({
    url: `/chat/${id}`,
    method: 'get'
  })
}

/**
 * 创建新对话
 * @param {Object} data
 * @param {string} data.title - 对话标题（可选）
 */
export function createChat(data) {
  return request({
    url: '/chat/create',
    method: 'post',
    data
  })
}

/**
 * 发送消息
 * @param {string} chatId - 对话ID
 * @param {Object} data
 * @param {string} data.content - 消息内容
 * @param {string} data.type - 消息类型 text/voice
 */
export function sendMessage(chatId, data) {
  return request({
    url: `/chat/${chatId}/message`,
    method: 'post',
    data
  })
}

/**
 * 删除对话
 * @param {string} id - 对话ID
 */
export function deleteChat(id) {
  return request({
    url: `/chat/${id}`,
    method: 'delete'
  })
}

/**
 * 更新对话标题
 * @param {string} id - 对话ID
 * @param {string} title - 新标题
 */
export function updateChatTitle(id, title) {
  return request({
    url: `/chat/${id}/title`,
    method: 'put',
    data: { title }
  })
}

/**
 * 获取所有标签
 */
export function getTags() {
  return request({
    url: '/chat/tags',
    method: 'get'
  })
}

/**
 * 为对话添加标签
 * @param {string} chatId - 对话ID
 * @param {string} tagId - 标签ID
 */
export function addTagToChat(chatId, tagId) {
  return request({
    url: `/chat/${chatId}/tag`,
    method: 'post',
    data: { tagId }
  })
}

/**
 * 创建自定义标签
 * @param {Object} data
 * @param {string} data.name - 标签名称
 * @param {string} data.color - 标签颜色
 */
export function createTag(data) {
  return request({
    url: '/chat/tag',
    method: 'post',
    data
  })
}

/**
 * 删除自定义标签
 * @param {string} tagId - 标签ID
 */
export function deleteTag(tagId) {
  return request({
    url: `/chat/tag/${tagId}`,
    method: 'delete'
  })
}

/**
 * 语音转文字
 * @param {File} file - 音频文件
 */
export function voiceToText(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request({
    url: '/chat/voice-to-text',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
