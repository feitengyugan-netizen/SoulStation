// 咨询师预约相关API
import request from './index'

/**
 * 获取咨询师列表
 * @param {Object} params - 查询参数
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.specialty - 擅长领域
 * @param {string} params.consultationType - 咨询方式
 * @param {string} params.priceMin - 最低价格
 * @param {string} params.priceMax - 最高价格
 * @param {string} params.sort - 排序方式
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getCounselorList(params) {
  return request({
    url: '/counselor/list',
    method: 'get',
    params
  })
}

/**
 * 获取咨询师详情
 * @param {string} id - 咨询师ID
 */
export function getCounselorDetail(id) {
  return request({
    url: `/counselor/${id}`,
    method: 'get'
  })
}

/**
 * 获取可预约时段
 * @param {string} counselorId - 咨询师ID
 * @param {string} date - 日期
 */
export function getAvailableSlots(counselorId, date) {
  return request({
    url: `/counselor/${counselorId}/slots`,
    method: 'get',
    params: { date }
  })
}

/**
 * 创建预约订单
 * @param {Object} data
 * @param {string} data.counselorId - 咨询师ID
 * @param {string} data.type - 咨询方式
 * @param {string} data.date - 日期
 * @param {string} data.timeSlot - 时段
 * @param {string} data.userName - 用户姓名
 * @param {string} data.contact - 联系方式
 * @param {string} data.description - 问题描述
 */
export function createAppointment(data) {
  return request({
    url: '/appointment/create',
    method: 'post',
    data
  })
}

/**
 * 获取用户预约列表
 * @param {Object} params
 * @param {string} params.status - 订单状态筛选
 * @param {number} params.page - 页码
 */
export function getUserAppointments(params) {
  return request({
    url: '/appointment/user/list',
    method: 'get',
    params
  })
}

/**
 * 取消预约
 * @param {string} id - 订单ID
 */
export function cancelAppointment(id) {
  return request({
    url: `/appointment/${id}/cancel`,
    method: 'post'
  })
}

/**
 * 提交咨询评价
 * @param {string} appointmentId - 订单ID
 * @param {Object} data
 * @param {number} data.rating - 评分
 * @param {Array} data.tags - 标签
 * @param {string} data.content - 评价内容
 * @param {boolean} data.isAnonymous - 是否匿名
 */
export function submitReview(appointmentId, data) {
  return request({
    url: `/appointment/${appointmentId}/review`,
    method: 'post',
    data
  })
}

/**
 * 获取咨询师评价列表
 * @param {string} counselorId - 咨询师ID
 * @param {Object} params
 * @param {number} params.page - 页码
 */
export function getCounselorReviews(counselorId, params) {
  return request({
    url: `/counselor/${counselorId}/reviews`,
    method: 'get',
    params
  })
}
