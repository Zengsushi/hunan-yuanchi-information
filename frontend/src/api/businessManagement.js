import { axiosInstance as request } from './users';

// 业务管理API
export const businessAPI = {
  // 获取业务列表
  getBusinessList(params = {}) {
    return request({
      url: '/business/businesses/',
      method: 'get',
      params
    });
  },

  // 获取业务详情
  getBusinessDetail(id) {
    return request({
      url: `/business/businesses/${id}/`,
      method: 'get'
    });
  },

  // 创建业务
  createBusiness(data) {
    return request({
      url: '/business/businesses/',
      method: 'post',
      data
    });
  },

  // 更新业务
  updateBusiness(id, data) {
    return request({
      url: `/business/businesses/${id}/`,
      method: 'put',
      data
    });
  },

  // 删除业务
  deleteBusiness(id) {
    return request({
      url: `/business/businesses/${id}/`,
      method: 'delete'
    });
  },

  // 批量删除业务
  batchDeleteBusiness(ids) {
    return request({
      url: '/business/businesses/batch_delete/',
      method: 'post',
      data: { ids }
    });
  },

  // 获取关联IP列表
  getBusinessIPs(businessId) {
    return request({
      url: `/business/businesses/${businessId}/associated_ips/`,
      method: 'get'
    });
  },

  // 添加关联IP
  addBusinessIP(businessId, ipData) {
    return request({
      url: `/business/businesses/${businessId}/add_ip/`,
      method: 'post',
      data: ipData
    });
  },

  // 移除关联IP
  removeBusinessIP(businessId, ipId) {
    return request({
      url: `/business/business-ips/${ipId}/`,
      method: 'delete'
    });
  },


  // 获取用户列表（用于责任人选择）
  getUsers() {
    return request({
      url: '/organization/employees/',
      method: 'get'
    });
  },

  // 搜索业务
  searchBusiness(keyword) {
    return request({
      url: '/business/businesses/',
      method: 'get',
      params: { search: keyword }
    });
  },

  // 导出业务列表
  exportBusiness(params = {}) {
    return request({
      url: '/business/businesses/export/',
      method: 'get',
      params,
      responseType: 'blob'
    });
  }
};

export default businessAPI;