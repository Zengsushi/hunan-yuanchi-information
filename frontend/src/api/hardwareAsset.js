import request from '@/utils/request'

// 硬件设施API
export const hardwareAssetApi = {
  // 获取硬件设施列表
  getList(params = {}) {
    return request({
      url: '/hardware-assets/',
      method: 'get',
      params
    })
  },

  // 获取在用硬件设施列表
  getInUseList(params = {}) {
    return request({
      url: '/hardware-assets/in_use/',
      method: 'get',
      params
    })
  },

  // 获取报废硬件设施列表
  getScrappedList(params = {}) {
    return request({
      url: '/hardware-assets/scrapped/',
      method: 'get',
      params
    })
  },

  // 获取硬件设施详情
  getDetail(id) {
    return request({
      url: `/hardware-assets/${id}/`,
      method: 'get'
    })
  },

  // 创建硬件设施
  create(data) {
    return request({
      url: '/hardware-assets/',
      method: 'post',
      data
    })
  },

  // 更新硬件设施
  update(id, data) {
    return request({
      url: `/hardware-assets/${id}/`,
      method: 'put',
      data
    })
  },

  // 部分更新硬件设施
  patch(id, data) {
    return request({
      url: `/hardware-assets/${id}/`,
      method: 'patch',
      data
    })
  },

  // 删除硬件设施
  delete(id) {
    return request({
      url: `/hardware-assets/${id}/`,
      method: 'delete'
    })
  },

  // 批量删除硬件设施
  batchDelete(ids) {
    return request({
      url: '/hardware-assets/batch_delete/',
      method: 'post',
      data: { ids }
    })
  },

  // 获取规格参数更新历史
  getSpecHistory(id) {
    return request({
      url: `/hardware-assets/${id}/spec_history/`,
      method: 'get'
    })
  },

  // 获取保修更新历史
  getWarrantyHistory(id) {
    return request({
      url: `/hardware-assets/${id}/warranty_history/`,
      method: 'get'
    })
  },

  // 导出硬件设施数据
  export(params = {}) {
    return request({
      url: '/hardware-assets/export/',
      method: 'get',
      params,
      responseType: 'blob'
    })
  },

  // 下载导入模板
  downloadTemplate() {
    return request({
      url: '/hardware-assets/import_template/',
      method: 'get',
      responseType: 'blob'
    })
  },

  // 批量导入硬件设施
  batchImport(data) {
    return request({
      url: '/hardware-assets/batch_import/',
      method: 'post',
      data: { assets: data }
    })
  },

  // 搜索硬件设施
  search(params) {
    return request({
      url: '/hardware-assets/search/',
      method: 'get',
      params
    })
  },

  // 获取统计信息
  getStats() {
    return request({
      url: '/hardware-assets/stats/',
      method: 'get'
    })
  },

  // 获取保修状态统计
  getWarrantyStats() {
    return request({
      url: '/hardware-assets/warranty_stats/',
      method: 'get'
    })
  },

  // 获取即将到期的保修
  getExpiringWarranty(days = 30) {
    return request({
      url: '/hardware-assets/expiring_warranty/',
      method: 'get',
      params: { days }
    })
  },

  // 获取已过保的设备
  getExpiredWarranty() {
    return request({
      url: '/hardware-assets/expired_warranty/',
      method: 'get'
    })
  },

  // 更新监控状态
  updateMonitoringStatus(id, status) {
    return request({
      url: `/hardware-assets/${id}/update_monitoring/`,
      method: 'post',
      data: { monitoring_status: status }
    })
  },

  // 批量更新监控状态
  batchUpdateMonitoring(ids, status) {
    return request({
      url: '/hardware-assets/batch_update_monitoring/',
      method: 'post',
      data: { ids, monitoring_status: status }
    })
  },

  // 获取位置信息
  getLocations() {
    return request({
      url: '/hardware-assets/locations/',
      method: 'get'
    })
  },

  // 获取制造商列表
  getManufacturers() {
    return request({
      url: '/hardware-assets/manufacturers/',
      method: 'get'
    })
  },

  // 获取型号列表
  getModels(manufacturer = '') {
    return request({
      url: '/hardware-assets/models/',
      method: 'get',
      params: { manufacturer }
    })
  },

  // 验证资产标签唯一性
  validateAssetTag(assetTag, excludeId = null) {
    return request({
      url: '/hardware-assets/validate_asset_tag/',
      method: 'post',
      data: { asset_tag: assetTag, exclude_id: excludeId }
    })
  },

  // 验证序列号唯一性
  validateSerialNumber(serialNumber, excludeId = null) {
    return request({
      url: '/hardware-assets/validate_serial_number/',
      method: 'post',
      data: { serial_number: serialNumber, exclude_id: excludeId }
    })
  },

  // 获取资产标签建议
  generateAssetTag(manufacturer, model) {
    return request({
      url: '/hardware-assets/generate_asset_tag/',
      method: 'post',
      data: { manufacturer, model }
    })
  },

  // 同步监控数据
  syncMonitoringData(id) {
    return request({
      url: `/hardware-assets/${id}/sync_monitoring/`,
      method: 'post'
    })
  },

  // 批量同步监控数据
  batchSyncMonitoring(ids) {
    return request({
      url: '/hardware-assets/batch_sync_monitoring/',
      method: 'post',
      data: { ids }
    })
  },

  // 获取资产变更历史
  getChangeHistory(id) {
    return request({
      url: `/hardware-assets/${id}/change_history/`,
      method: 'get'
    })
  },

  // 复制硬件设施
  duplicate(id, data = {}) {
    return request({
      url: `/hardware-assets/${id}/duplicate/`,
      method: 'post',
      data
    })
  },

  // 移动设备位置
  moveLocation(id, location) {
    return request({
      url: `/hardware-assets/${id}/move_location/`,
      method: 'post',
      data: location
    })
  },

  // 批量移动设备位置
  batchMoveLocation(ids, location) {
    return request({
      url: '/hardware-assets/batch_move_location/',
      method: 'post',
      data: { ids, ...location }
    })
  },

  // 设备报废
  scrap(id, reason = '') {
    return request({
      url: `/hardware-assets/${id}/scrap/`,
      method: 'post',
      data: { reason }
    })
  },

  // 批量设备报废
  batchScrap(ids, reason = '') {
    return request({
      url: '/hardware-assets/batch_scrap/',
      method: 'post',
      data: { ids, reason }
    })
  },

  // 设备恢复
  restore(id) {
    return request({
      url: `/hardware-assets/${id}/restore/`,
      method: 'post'
    })
  },

  // 批量设备恢复
  batchRestore(ids) {
    return request({
      url: '/hardware-assets/batch_restore/',
      method: 'post',
      data: { ids }
    })
  }
}

export default hardwareAssetApi