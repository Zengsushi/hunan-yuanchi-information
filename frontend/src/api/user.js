import request from '@/utils/request'

// 用户API
export const userApi = {
  // 获取用户列表
  getList(params = {}) {
    return request({
      url: '/users/',
      method: 'get',
      params
    })
  },

  // 获取用户简单列表（用于下拉选择）
  getSimpleList(params = {}) {
    return request({
      url: '/users/simple_list/',
      method: 'get',
      params
    })
  },

  // 搜索用户
  search(params) {
    return request({
      url: '/users/search/',
      method: 'get',
      params
    })
  },

  // 获取用户详情
  getDetail(id) {
    return request({
      url: `/users/${id}/`,
      method: 'get'
    })
  },

  // 获取当前用户信息
  getCurrentUser() {
    return request({
      url: '/users/me/',
      method: 'get'
    })
  },

  // 更新当前用户信息
  updateCurrentUser(data) {
    return request({
      url: '/users/me/',
      method: 'put',
      data
    })
  },

  // 创建用户
  create(data) {
    return request({
      url: '/users/',
      method: 'post',
      data
    })
  },

  // 更新用户
  update(id, data) {
    return request({
      url: `/users/${id}/`,
      method: 'put',
      data
    })
  },

  // 部分更新用户
  patch(id, data) {
    return request({
      url: `/users/${id}/`,
      method: 'patch',
      data
    })
  },

  // 删除用户
  delete(id) {
    return request({
      url: `/users/${id}/`,
      method: 'delete'
    })
  },

  // 批量删除用户
  batchDelete(ids) {
    return request({
      url: '/users/batch_delete/',
      method: 'post',
      data: { ids }
    })
  },

  // 重置用户密码
  resetPassword(id, data) {
    return request({
      url: `/users/${id}/reset_password/`,
      method: 'post',
      data
    })
  },

  // 修改密码
  changePassword(data) {
    return request({
      url: '/users/change_password/',
      method: 'post',
      data
    })
  },

  // 启用/禁用用户
  updateStatus(id, isActive) {
    return request({
      url: `/users/${id}/update_status/`,
      method: 'post',
      data: { is_active: isActive }
    })
  },

  // 批量更新用户状态
  batchUpdateStatus(ids, isActive) {
    return request({
      url: '/users/batch_update_status/',
      method: 'post',
      data: { ids, is_active: isActive }
    })
  },

  // 获取用户权限
  getPermissions(id) {
    return request({
      url: `/users/${id}/permissions/`,
      method: 'get'
    })
  },

  // 更新用户权限
  updatePermissions(id, permissions) {
    return request({
      url: `/users/${id}/permissions/`,
      method: 'post',
      data: { permissions }
    })
  },

  // 获取用户角色
  getRoles(id) {
    return request({
      url: `/users/${id}/roles/`,
      method: 'get'
    })
  },

  // 更新用户角色
  updateRoles(id, roles) {
    return request({
      url: `/users/${id}/roles/`,
      method: 'post',
      data: { roles }
    })
  },

  // 获取用户组
  getGroups(id) {
    return request({
      url: `/users/${id}/groups/`,
      method: 'get'
    })
  },

  // 更新用户组
  updateGroups(id, groups) {
    return request({
      url: `/users/${id}/groups/`,
      method: 'post',
      data: { groups }
    })
  },

  // 获取用户资产
  getAssets(id, params = {}) {
    return request({
      url: `/users/${id}/assets/`,
      method: 'get',
      params
    })
  },

  // 获取用户操作日志
  getOperationLogs(id, params = {}) {
    return request({
      url: `/users/${id}/operation_logs/`,
      method: 'get',
      params
    })
  },

  // 获取用户登录历史
  getLoginHistory(id, params = {}) {
    return request({
      url: `/users/${id}/login_history/`,
      method: 'get',
      params
    })
  },

  // 导出用户数据
  export(params = {}) {
    return request({
      url: '/users/export/',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },

  // 下载导入模板
  downloadTemplate() {
    return request({
      url: '/users/import_template/',
      method: 'get',
      responseType: 'blob'
    })
  },

  // 批量导入用户
  batchImport(data) {
    return request({
      url: '/users/batch_import/',
      method: 'post',
      data: { users: data }
    })
  },

  // 验证用户名唯一性
  validateUsername(username, excludeId = null) {
    return request({
      url: '/users/validate_username/',
      method: 'post',
      data: { username, exclude_id: excludeId }
    })
  },

  // 验证邮箱唯一性
  validateEmail(email, excludeId = null) {
    return request({
      url: '/users/validate_email/',
      method: 'post',
      data: { email, exclude_id: excludeId }
    })
  },

  // 获取用户统计信息
  getStats() {
    return request({
      url: '/users/stats/',
      method: 'get'
    })
  },

  // 获取在线用户
  getOnlineUsers() {
    return request({
      url: '/users/online/',
      method: 'get'
    })
  },

  // 强制用户下线
  forceLogout(id) {
    return request({
      url: `/users/${id}/force_logout/`,
      method: 'post'
    })
  },

  // 批量强制用户下线
  batchForceLogout(ids) {
    return request({
      url: '/users/batch_force_logout/',
      method: 'post',
      data: { ids }
    })
  },

  // 发送邮件通知
  sendNotification(id, data) {
    return request({
      url: `/users/${id}/send_notification/`,
      method: 'post',
      data
    })
  },

  // 批量发送邮件通知
  batchSendNotification(ids, data) {
    return request({
      url: '/users/batch_send_notification/',
      method: 'post',
      data: { ids, ...data }
    })
  },

  // 获取用户偏好设置
  getPreferences(id) {
    return request({
      url: `/users/${id}/preferences/`,
      method: 'get'
    })
  },

  // 更新用户偏好设置
  updatePreferences(id, data) {
    return request({
      url: `/users/${id}/preferences/`,
      method: 'put',
      data
    })
  },

  // 上传用户头像
  uploadAvatar(id, formData) {
    return request({
      url: `/users/${id}/avatar/`,
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 删除用户头像
  deleteAvatar(id) {
    return request({
      url: `/users/${id}/avatar/`,
      method: 'delete'
    })
  },

  // 获取用户部门
  getDepartments() {
    return request({
      url: '/users/departments/',
      method: 'get'
    })
  },

  // 获取用户职位
  getPositions() {
    return request({
      url: '/users/positions/',
      method: 'get'
    })
  },

  // 获取用户等级
  getLevels() {
    return request({
      url: '/users/levels/',
      method: 'get'
    })
  },

  // 获取用户变更历史
  getChangeHistory(id) {
    return request({
      url: `/users/${id}/change_history/`,
      method: 'get'
    })
  },

  // 复制用户
  duplicate(id, data = {}) {
    return request({
      url: `/users/${id}/duplicate/`,
      method: 'post',
      data
    })
  },

  // 获取用户推荐
  getRecommendations(params = {}) {
    return request({
      url: '/users/recommendations/',
      method: 'get',
      params
    })
  },

  // 获取用户地区分布
  getRegionDistribution() {
    return request({
      url: '/users/region_distribution/',
      method: 'get'
    })
  },

  // 获取用户部门分布
  getDepartmentDistribution() {
    return request({
      url: '/users/department_distribution/',
      method: 'get'
    })
  }
}

export default userApi