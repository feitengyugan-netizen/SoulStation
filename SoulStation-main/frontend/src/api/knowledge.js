// 心理知识相关API
import request from './index'

/**
 * 获取知识列表
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.category - 分类筛选
 * @param {string} params.sort - 排序方式
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getKnowledgeList(params) {
  return request({
    url: '/knowledge/list',
    method: 'get',
    params
  })
}

/**
 * 获取知识详情
 * @param {string} id - 知识ID
 */
export function getKnowledgeDetail(id) {
  return request({
    url: `/knowledge/${id}`,
    method: 'get'
  })
}

/**
 * 获取推荐知识
 * @param {string} id - 当前知识ID
 */
export function getRecommendedKnowledge(id) {
  return request({
    url: `/knowledge/${id}/recommended`,
    method: 'get'
  })
}

/**
 * 收藏知识
 * @param {string} id - 知识ID
 */
export function favoriteKnowledge(id) {
  return request({
    url: `/knowledge/${id}/favorite`,
    method: 'post'
  })
}

/**
 * 取消收藏知识
 * @param {string} id - 知识ID
 */
export function unfavoriteKnowledge(id) {
  return request({
    url: `/knowledge/${id}/favorite`,
    method: 'delete'
  })
}

/**
 * 点赞知识
 * @param {string} id - 知识ID
 */
export function likeKnowledge(id) {
  return request({
    url: `/knowledge/${id}/like`,
    method: 'post'
  })
}

/**
 * 提交评论
 * @param {string} id - 知识ID
 * @param {Object} data
 * @param {string} data.content - 评论内容
 */
export function submitComment(id, data) {
  return request({
    url: `/knowledge/${id}/comment`,
    method: 'post',
    data
  })
}
