// 评价相关API
import request from './index'

/**
 * 提交咨询评价
 * @param {number} appointmentId - 预约ID
 * @param {Object} data
 * @param {number} data.rating - 评分1-5
 * @param {string[]} data.tags - 评价标签
 * @param {string} data.content - 评价内容
 * @param {boolean} data.is_anonymous - 是否匿名
 */
export function submitReview(appointmentId, data) {
  return request({
    url: `/consultation/reviews/${appointmentId}`,
    method: 'post',
    data
  })
}

/**
 * 获取预约评价
 * @param {number} appointmentId - 预约ID
 */
export function getReview(appointmentId) {
  return request({
    url: `/consultation/reviews/${appointmentId}`,
    method: 'get'
  })
}

/**
 * 获取待评价列表
 */
export function getPendingReviews() {
  return request({
    url: '/consultation/reviews/pending/list',
    method: 'get'
  })
}
