// 用户预约订单相关API
import request from './index'

/**
 * 获取用户订单列表
 * @param {Object} params
 * @param {string} params.status - 订单状态筛选
 */
export function getUserOrders(params) {
  return request({
    url: '/user/orders',
    method: 'get',
    params
  })
}

/**
 * 取消预约订单
 * @param {string} id - 订单ID
 */
export function cancelAppointment(id) {
  return request({
    url: `/appointment/${id}`,
    method: 'delete'
  })
}
