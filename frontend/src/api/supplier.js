import request from '@/utils/request'

// 供应商API
export const supplierApi = {
  // 获取供应商列表
  getList(params = {}) {
    return request({
      url: '/suppliers/',
      method: 'get',
      params
    })
  },

  // 获取供应商简单列表（用于下拉选择）
  getSimpleList(params = {}) {
    return request({
      url: '/suppliers/simple_list/',
      method: 'get',
      params
    })
  },

  // 获取供应商详情
  getDetail(id) {
    return request({
      url: `/suppliers/${id}/`,
      method: 'get'
    })
  },

  // 创建供应商
  create(data) {
    return request({
      url: '/suppliers/',
      method: 'post',
      data
    })
  },

  // 更新供应商
  update(id, data) {
    return request({
      url: `/suppliers/${id}/`,
      method: 'put',
      data
    })
  },

  // 部分更新供应商
  patch(id, data) {
    return request({
      url: `/suppliers/${id}/`,
      method: 'patch',
      data
    })
  },

  // 删除供应商
  delete(id) {
    return request({
      url: `/suppliers/${id}/`,
      method: 'delete'
    })
  },

  // 批量删除供应商
  batchDelete(ids) {
    return request({
      url: '/suppliers/batch_delete/',
      method: 'post',
      data: { ids }
    })
  },

  // 获取供应商联系人
  getContacts(id) {
    return request({
      url: `/suppliers/${id}/contacts/`,
      method: 'get'
    })
  },

  // 添加供应商联系人
  addContact(id, data) {
    return request({
      url: `/suppliers/${id}/contacts/`,
      method: 'post',
      data
    })
  },

  // 更新供应商联系人
  updateContact(id, contactId, data) {
    return request({
      url: `/suppliers/${id}/contacts/${contactId}/`,
      method: 'put',
      data
    })
  },

  // 删除供应商联系人
  deleteContact(id, contactId) {
    return request({
      url: `/suppliers/${id}/contacts/${contactId}/`,
      method: 'delete'
    })
  },

  // 获取供应商资产列表
  getAssets(id, params = {}) {
    return request({
      url: `/suppliers/${id}/`,
      method: 'get',
      params
    })
  },

  // 搜索供应商
  search(params) {
    return request({
      url: '/suppliers/search/',
      method: 'get',
      params
    })
  },

  // 获取供应商统计信息
  getStats(id) {
    return request({
      url: `/suppliers/${id}/stats/`,
      method: 'get'
    })
  },

  // 导出供应商数据
  export(params = {}) {
    return request({
      url: '/suppliers/export/',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },

  // 下载导入模板
  downloadTemplate() {
    return request({
      url: '/suppliers/import_template/',
      method: 'get',
      responseType: 'blob'
    })
  },

  // 批量导入供应商
  batchImport(data) {
    return request({
      url: '/suppliers/batch_import/',
      method: 'post',
      data: { suppliers: data }
    })
  },

  // 验证供应商名称唯一性
  validateName(name, excludeId = null) {
    return request({
      url: '/suppliers/validate_name/',
      method: 'post',
      data: { name, exclude_id: excludeId }
    })
  },

  // 获取供应商类型列表
  getTypes() {
    return request({
      url: '/suppliers/types/',
      method: 'get'
    })
  },

  // 获取供应商等级列表
  getLevels() {
    return request({
      url: '/suppliers/levels/',
      method: 'get'
    })
  },

  // 更新供应商状态
  updateStatus(id, status) {
    return request({
      url: `/suppliers/${id}/update_status/`,
      method: 'post',
      data: { status }
    })
  },

  // 批量更新供应商状态
  batchUpdateStatus(ids, status) {
    return request({
      url: '/suppliers/batch_update_status/',
      method: 'post',
      data: { ids, status }
    })
  },

  // 获取供应商合作历史
  getCooperationHistory(id) {
    return request({
      url: `/suppliers/${id}/cooperation_history/`,
      method: 'get'
    })
  },

  // 获取供应商评价
  getEvaluations(id) {
    return request({
      url: `/suppliers/${id}/evaluations/`,
      method: 'get'
    })
  },

  // 添加供应商评价
  addEvaluation(id, data) {
    return request({
      url: `/suppliers/${id}/evaluations/`,
      method: 'post',
      data
    })
  },

  // 获取供应商合同列表
  getContracts(id, params = {}) {
    return request({
      url: `/suppliers/${id}/contracts/`,
      method: 'get',
      params
    })
  },

  // 添加供应商合同
  addContract(id, data) {
    return request({
      url: `/suppliers/${id}/contracts/`,
      method: 'post',
      data
    })
  },

  // 更新供应商合同
  updateContract(id, contractId, data) {
    return request({
      url: `/suppliers/${id}/contracts/${contractId}/`,
      method: 'put',
      data
    })
  },

  // 删除供应商合同
  deleteContract(id, contractId) {
    return request({
      url: `/suppliers/${id}/contracts/${contractId}/`,
      method: 'delete'
    })
  },

  // 获取供应商财务信息
  getFinancialInfo(id) {
    return request({
      url: `/suppliers/${id}/financial_info/`,
      method: 'get'
    })
  },

  // 更新供应商财务信息
  updateFinancialInfo(id, data) {
    return request({
      url: `/suppliers/${id}/financial_info/`,
      method: 'put',
      data
    })
  },

  // 获取供应商资质证书
  getCertificates(id) {
    return request({
      url: `/suppliers/${id}/certificates/`,
      method: 'get'
    })
  },

  // 上传供应商资质证书
  uploadCertificate(id, formData) {
    return request({
      url: `/suppliers/${id}/certificates/`,
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 删除供应商资质证书
  deleteCertificate(id, certificateId) {
    return request({
      url: `/suppliers/${id}/certificates/${certificateId}/`,
      method: 'delete'
    })
  },

  // 获取供应商变更历史
  getChangeHistory(id) {
    return request({
      url: `/suppliers/${id}/change_history/`,
      method: 'get'
    })
  },

  // 复制供应商
  duplicate(id, data = {}) {
    return request({
      url: `/suppliers/${id}/duplicate/`,
      method: 'post',
      data
    })
  },

  // 合并供应商
  merge(sourceId, targetId) {
    return request({
      url: `/suppliers/${sourceId}/merge/`,
      method: 'post',
      data: { target_id: targetId }
    })
  },

  // 获取供应商推荐
  getRecommendations(params = {}) {
    return request({
      url: '/suppliers/recommendations/',
      method: 'get',
      params
    })
  },

  // 获取供应商地区分布
  getRegionDistribution() {
    return request({
      url: '/suppliers/region_distribution/',
      method: 'get'
    })
  },

  // 获取供应商行业分布
  getIndustryDistribution() {
    return request({
      url: '/suppliers/industry_distribution/',
      method: 'get'
    })
  }
}

export default supplierApi