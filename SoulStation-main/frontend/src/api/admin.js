// 后台管理相关API
import request from './index'

/**
 * 管理员登录
 * @param {Object} data
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 */
export function adminLogin(data) {
  return request({
    url: '/admin/login',
    method: 'post',
    data
  })
}

/**
 * 获取仪表盘统计数据
 */
export function getDashboardStats() {
  return request({
    url: '/admin/dashboard/stats',
    method: 'get'
  })
}

/**
 * 获取图表数据
 * @param {string} type - 图表类型: user/trend/order/revenue
 */
export function getChartData(type) {
  return request({
    url: '/admin/dashboard/chart',
    method: 'get',
    params: { type }
  })
}

/**
 * 获取待审核咨询师列表
 * @param {Object} params
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getPendingCounselors(params) {
  return request({
    url: '/admin/counselors/pending',
    method: 'get',
    params
  })
}

/**
 * 审核咨询师
 * @param {string} id - 咨询师ID
 * @param {Object} data
 * @param {string} data.action - 操作: approve/reject
 * @param {string} data.reason - 拒绝理由
 */
export function reviewCounselor(id, data) {
  return request({
    url: `/admin/counselor/${id}/review`,
    method: 'post',
    data
  })
}

/**
 * 获取知识文章列表
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {string} params.category - 分类
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getKnowledgeArticles(params) {
  return request({
    url: '/admin/knowledge/list',
    method: 'get',
    params
  })
}

/**
 * 创建/更新知识文章
 * @param {Object} data
 * @param {string} data.id - 文章ID（更新时）
 * @param {string} data.title - 标题
 * @param {string} data.content - 内容
 * @param {string} data.category - 分类
 * @param {string} data.cover - 封面图
 */
export function saveKnowledgeArticle(data) {
  return request({
    url: '/admin/knowledge/save',
    method: 'post',
    data
  })
}

/**
 * 删除知识文章
 * @param {string} id - 文章ID
 */
export function deleteKnowledgeArticle(id) {
  return request({
    url: `/admin/knowledge/${id}`,
    method: 'delete'
  })
}

/**
 * 获取用户列表
 * @param {Object} params
 * @param {string} params.keyword - 搜索关键词
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getAdminUsers(params) {
  return request({
    url: '/admin/users',
    method: 'get',
    params
  })
}

/**
 * 封禁用户
 * @param {string} id - 用户ID
 * @param {Object} data
 * @param {boolean} data.banned - 是否封禁
 */
export function banUser(id, data) {
  return request({
    url: `/admin/user/${id}/ban`,
    method: 'post',
    data
  })
}

/**
 * 获取订单列表
 * @param {Object} params
 * @param {string} params.status - 订单状态
 * @param {number} params.page - 页码
 * @param {number} params.pageSize - 每页数量
 */
export function getAdminOrders(params) {
  return request({
    url: '/admin/orders',
    method: 'get',
    params
  })
}

/**
 * 导出订单数据
 */
export function exportOrders() {
  return request({
    url: '/admin/orders/export',
    method: 'get',
    responseType: 'blob'
  })
}
