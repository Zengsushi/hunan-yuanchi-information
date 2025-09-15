import request from '@/utils/request';

// 软件资产API
const softwareAssetApi = {
  // 获取软件资产列表
  getList(params = {}) {
    return request({
      url: '/software-assets/',
      method: 'get',
      params
    });
  },

  // 获取软件资产详情
  getDetail(id) {
    return request({
      url: `/software-assets/${id}/`,
      method: 'get'
    });
  },

  // 创建软件资产
  create(data) {
    return request({
      url: '/software-assets/',
      method: 'post',
      data
    });
  },

  // 更新软件资产
  update(id, data) {
    return request({
      url: `/software-assets/${id}/`,
      method: 'put',
      data
    });
  },

  // 部分更新软件资产
  patch(id, data) {
    return request({
      url: `/software-assets/${id}/`,
      method: 'patch',
      data
    });
  },

  // 删除软件资产
  delete(id) {
    return request({
      url: `/software-assets/${id}/`,
      method: 'delete'
    });
  },

  // 批量删除软件资产
  batchDelete(ids) {
    return request({
      url: '/software-assets/batch_delete/',
      method: 'post',
      data: { ids }
    });
  },

  // 更新许可证信息
  updateLicense(id, data) {
    return request({
      url: `/software-assets/${id}/update_license/`,
      method: 'post',
      data
    });
  },

  // 获取许可证历史记录
  getLicenseHistory(id) {
    return request({
      url: `/software-assets/${id}/license_history/`,
      method: 'get'
    });
  },

  // 获取版本历史记录
  getVersionHistory(id) {
    return request({
      url: `/software-assets/${id}/version_history/`,
      method: 'get'
    });
  },

  // 导出软件资产数据
  export(params = {}) {
    return request({
      url: '/software-assets/export/',
      method: 'get',
      params,
      responseType: 'blob'
    });
  },

  // 下载导入模板
  downloadTemplate() {
    return request({
      url: '/software-assets/download_template/',
      method: 'get',
      responseType: 'blob'
    });
  },

  // 导入软件资产数据
  import(file, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    
    // 添加导入选项
    Object.keys(options).forEach(key => {
      formData.append(key, options[key]);
    });

    return request({
      url: '/software-assets/import/',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  // 获取软件资产统计信息
  getStatistics() {
    return request({
      url: '/software-assets/statistics/',
      method: 'get'
    });
  },

  // 检查许可证状态
  checkLicenseStatus(id) {
    return request({
      url: `/software-assets/${id}/check_license/`,
      method: 'post'
    });
  },

  // 批量检查许可证状态
  batchCheckLicense(ids) {
    return request({
      url: '/software-assets/batch_check_license/',
      method: 'post',
      data: { ids }
    });
  },

  // 获取软件部署信息
  getDeployments(id) {
    return request({
      url: `/software-assets/${id}/deployments/`,
      method: 'get'
    });
  },

  // 创建软件部署
  createDeployment(id, data) {
    return request({
      url: `/software-assets/${id}/deployments/`,
      method: 'post',
      data
    });
  },

  // 更新软件部署
  updateDeployment(assetId, deploymentId, data) {
    return request({
      url: `/software-assets/${assetId}/deployments/${deploymentId}/`,
      method: 'put',
      data
    });
  },

  // 删除软件部署
  deleteDeployment(assetId, deploymentId) {
    return request({
      url: `/software-assets/${assetId}/deployments/${deploymentId}/`,
      method: 'delete'
    });
  },

  // 获取软件类型选项
  getSoftwareTypes() {
    return request({
      url: '/software-assets/software_types/',
      method: 'get'
    });
  },

  // 获取许可证类型选项
  getLicenseTypes() {
    return request({
      url: '/software-assets/license_types/',
      method: 'get'
    });
  },

  // 获取供应商列表
  getVendors() {
    return request({
      url: '/software-assets/vendors/',
      method: 'get'
    });
  },

  // 搜索软件资产
  search(keyword, filters = {}) {
    return request({
      url: '/software-assets/search/',
      method: 'get',
      params: {
        q: keyword,
        ...filters
      }
    });
  },

  // 获取即将过期的许可证
  getExpiringLicenses(days = 30) {
    return request({
      url: '/software-assets/expiring_licenses/',
      method: 'get',
      params: { days }
    });
  },

  // 获取许可证使用情况报告
  getLicenseUsageReport(params = {}) {
    return request({
      url: '/software-assets/license_usage_report/',
      method: 'get',
      params
    });
  },

  // 验证许可证密钥
  validateLicenseKey(data) {
    return request({
      url: '/software-assets/validate_license_key/',
      method: 'post',
      data
    });
  },

  // 同步许可证信息
  syncLicenseInfo(id) {
    return request({
      url: `/software-assets/${id}/sync_license/`,
      method: 'post'
    });
  },

  // 批量同步许可证信息
  batchSyncLicense(ids) {
    return request({
      url: '/software-assets/batch_sync_license/',
      method: 'post',
      data: { ids }
    });
  },

  // 获取软件资产变更日志
  getChangeLog(id, params = {}) {
    return request({
      url: `/software-assets/${id}/change_log/`,
      method: 'get',
      params
    });
  },

  // 创建软件资产备份
  createBackup(id) {
    return request({
      url: `/software-assets/${id}/backup/`,
      method: 'post'
    });
  },

  // 恢复软件资产
  restore(id, backupId) {
    return request({
      url: `/software-assets/${id}/restore/`,
      method: 'post',
      data: { backup_id: backupId }
    });
  }
};

export default softwareAssetApi;