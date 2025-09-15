import request from '@/utils/request'

// 菜单管理API
export const menuApi = {
  // 获取用户菜单列表（根据权限）
  getUserMenus() {
    return request({
      url: '/menus/user_menus/',
      method: 'get'
    })
  },

  // 获取所有菜单列表（管理员用）
  getList(params = {}) {
    return request({
      url: '/menus/',
      method: 'get',
      params
    })
  },

  // 获取菜单详情
  getDetail(id) {
    return request({
      url: `/menus/${id}/`,
      method: 'get'
    })
  },

  // 创建菜单
  create(data) {
    return request({
      url: '/menus/',
      method: 'post',
      data
    })
  },

  // 更新菜单
  update(id, data) {
    return request({
      url: `/menus/${id}/`,
      method: 'put',
      data
    })
  },

  // 部分更新菜单
  patch(id, data) {
    return request({
      url: `/menus/${id}/`,
      method: 'patch',
      data
    })
  },

  // 删除菜单
  delete(id) {
    return request({
      url: `/menus/${id}/`,
      method: 'delete'
    })
  },

  // 批量删除菜单
  batchDelete(ids) {
    return request({
      url: '/menus/batch_delete/',
      method: 'post',
      data: { ids }
    })
  },

  // 更新菜单排序
  updateOrder(data) {
    return request({
      url: '/menus/update_order/',
      method: 'post',
      data
    })
  },

  // 获取菜单树结构
  getMenuTree() {
    return request({
      url: '/menus/tree/',
      method: 'get'
    })
  },

  // 获取用户菜单树结构（根据权限）
  getUserMenuTree() {
    return request({
      url: '/menus/user_tree/',
      method: 'get'
    })
  },

  // 启用/禁用菜单
  updateStatus(id, isActive) {
    return request({
      url: `/menus/${id}/update_status/`,
      method: 'post',
      data: { is_active: isActive }
    })
  },

  // 批量更新菜单状态
  batchUpdateStatus(ids, isActive) {
    return request({
      url: '/menus/batch_update_status/',
      method: 'post',
      data: { ids, is_active: isActive }
    })
  }
}

export default menuApi