import { axiosInstance as api } from './users';

// IP管理API
export const ipAPI = {
  /**
   * 获取IP列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.pageSize - 每页数量
   * @param {string} params.search - 搜索关键词(IP地址或主机名)
   * @param {string} params.status - IP状态筛选
   * @param {string} params.type - IP类型筛选
   * @returns {Promise} IP列表响应
   */
  getIPList(params = {}) {
    return api.get('/ip-management/records/', { params });
  },

  /**
   * 获取IP详情
   * @param {number|string} ipId - IP记录ID
   * @returns {Promise} IP详情
   */
  getIPDetail(ipId) {
    return api.get(`/ip-management/records/${ipId}/`);
  },

  /**
   * 创建IP记录
   * @param {Object} ipData - IP数据
   * @param {string} ipData.ipAddress - IP地址
   * @param {string} ipData.hostname - 主机名
   * @param {string} ipData.status - IP状态
   * @param {string} ipData.type - IP类型
   * @param {string} ipData.macAddress - MAC地址
   * @param {string} ipData.device - 关联设备
   * @param {string} ipData.subnet - 所属网段
   * @param {string} ipData.description - 备注
   * @returns {Promise} 创建结果
   */
  createIP(ipData) {
    return api.post('/ip-management/records/', ipData);
  },

  /**
   * 更新IP记录
   * @param {number|string} ipId - IP记录ID
   * @param {Object} ipData - 更新的IP数据
   * @returns {Promise} 更新结果
   */
  updateIP(ipId, ipData) {
    return api.put(`/ip-management/records/${ipId}/`, ipData);
  },

  /**
   * 删除IP记录
   * @param {number|string} ipId - IP记录ID
   * @returns {Promise} 删除结果
   */
  deleteIP(ipId) {
    return api.delete(`/ip-management/records/${ipId}/`);
  },

  /**
   * 检查删除IP的影响范围
   * @param {number|string} ipId - IP记录ID
   * @returns {Promise} 删除影响评估结果
   */
  checkDeletionImpact(ipId) {
    return api.get(`/ip-management/records/${ipId}/check-deletion-impact/`);
  },

  /**
   * 批量删除IP记录
   * @param {Array} ipIds - IP记录ID数组
   * @returns {Promise} 批量删除结果
   */
  batchDeleteIPs(ipIds) {
    return api.delete('/ip-management/records/batch/', { data: { ipIds } });
  },

  /**
   * 切换单个IP的监控状态
   * @param {number|string} ipId - IP记录ID
   * @param {boolean} enabled - 是否启用监控
   * @returns {Promise} 切换结果
   */
  toggleMonitoring(ipId, enabled) {
    return api.patch(`/ip-management/records/${ipId}/monitoring/`, { enabled });
  },

  /**
   * 批量切换监控状态
   * @param {Array} ipIds - IP记录ID数组
   * @param {boolean} enabled - 是否启用监控
   * @returns {Promise} 批量切换结果
   */
  batchToggleMonitoring(ipIds, enabled) {
    return api.patch('/ip-management/records/batch-monitoring/', { ipIds, enabled });
  },

  /**
   * 获取Zabbix监控模板列表
   * @param {number|string} ipId - IP记录ID
   * @param {string} search - 搜索关键词
   * @returns {Promise} 模板列表响应
   */
  getZabbixTemplates(ipId, search = '') {
    const params = search ? { search } : {};
    return api.get(`/ip-management/records/${ipId}/zabbix-templates/`, { params });
  },

  /**
   * 为IP创建Zabbix监控主机
   * @param {number|string} ipId - IP记录ID
   * @param {Object} monitoringData - 监控配置数据
   * @param {Array} monitoringData.template_ids - 模板ID列表
   * @param {string} monitoringData.host_name - 主机名称
   * @param {Array} monitoringData.group_ids - 主机组ID列表
   * @returns {Promise} 创建结果
   */
  createMonitoring(ipId, monitoringData) {
    return api.post(`/ip-management/records/${ipId}/create-monitoring/`, monitoringData);
  },

  /**
   * Ping测试单个IP
   * @param {number|string} ipId - IP记录ID
   * @returns {Promise} Ping测试结果
   */
  pingIP(ipId) {
    return api.post(`/ip-management/records/${ipId}/ping/`);
  },

  /**
   * 批量Ping测试
   * @param {Array} ipIds - IP记录ID数组
   * @returns {Promise} 批量Ping测试结果
   */
  batchPingIPs(ipIds) {
    return api.post('/ip-management/records/batch-ping/', { ipIds });
  },

  /**
   * 导出IP列表
   * @param {Object} params - 导出参数
   * @returns {Promise} 导出文件
   */
  exportIPs(params = {}) {
    return api.get('/ip-management/records/export/', { 
      params,
      responseType: 'blob'
    });
  },

  /**
   * 获取IP统计信息
   * @returns {Promise} IP统计数据
   */
  getIPStats() {
    return api.get('/ip-management/records/statistics/');
  },

  /**
   * 创建IP扫描任务（通过后端调用Zabbix）
   * @param {Object} scanData - 扫描配置数据
   * @param {Array} scanData.ipRanges - IP范围数组
   * @param {number} scanData.checkType - 检查类型
   * @param {string} scanData.ports - 端口范围
   * @param {string} scanData.key - 检查键值或SNMP OID
   * @param {string} scanData.snmpCommunity - SNMP社区
   * @param {Object} scanData.snmpv3Config - SNMPv3配置
   * @param {number} scanData.uniqueCheck - 唯一性检查
   * @param {number} scanData.hostSource - 主机名称来源
   * @param {number} scanData.nameSource - 可见名称来源
   * @returns {Promise} 扫描任务创建结果
   */
  createScanTask(scanData) {
    return api.post('/ip-management/scan/', scanData);
  },

  /**
   * 获取扫描任务状态
   * @param {string} taskId - 任务ID
   * @returns {Promise} 任务状态
   */
  getScanTaskStatus(taskId) {
    return api.get(`/ip-management/scan/${taskId}/status/`);
  },

  /**
   * 获取扫描结果
   * @param {string} taskId - 任务ID
   * @returns {Promise} 扫描结果
   */
  getScanResults(taskId) {
    return api.get(`/ip-management/scan/${taskId}/results/`);
  },

  /**
   * 取消扫描任务
   * @param {string} taskId - 任务ID
   * @returns {Promise} 取消结果
   */
  cancelScanTask(taskId) {
    return api.delete(`/ip-management/scan/${taskId}/`);
  },

  /**
   * 获取扫描历史记录
   * @param {Object} params - 查询参数
   * @returns {Promise} 扫描历史列表
   */
  getScanHistory(params = {}) {
    return api.get('/ip-management/scan/history/', { params });
  },

  /**
   * 获取扫描任务列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.page_size - 每页数量
   * @param {string} params.status - 任务状态筛选
   * @param {string} params.search - 搜索关键词
   * @param {string} params.created_after - 创建时间起始
   * @param {string} params.created_before - 创建时间结束
   * @returns {Promise} 扫描任务列表
   */
  getScanTasks(params = {}) {
    return api.get('/ip-management/scan-tasks/', { params });
  },

  /**
   * 获取扫描任务结果
   * @param {string} taskId - 任务ID
   * @returns {Promise} 扫描任务结果
   */
  getScanTaskResults(taskId) {
    return api.get(`/ip-management/scan/${taskId}/results/`);
  },

  /**
   * 创建测试数据
   * @returns {Promise} 创建结果
   */
  createTestData() {
    return api.post('/ip-management/scan-tasks/create-test-data/');
  },

  /**
   * 同步特定扫描任务的Zabbix发现IP到数据库
   * @param {string} taskId - 任务ID
   * @returns {Promise} 同步结果
   */
  syncTaskZabbixIPs(taskId) {
    return api.post(`/ip-management/scan-tasks/${taskId}/sync-zabbix-ips/`);
  },

  /**
   * 获取异步任务处理状态
   * @param {string} taskId - 任务ID
   * @returns {Promise} 任务状态
   */
  getAsyncTaskStatus(taskId) {
    return api.get(`/ip-management/scan-tasks/${taskId}/async-status/`);
  },

  /**
   * 停止异步任务处理
   * @param {string} taskId - 任务ID
   * @returns {Promise} 停止结果
   */
  stopAsyncTask(taskId) {
    return api.post(`/ip-management/scan-tasks/${taskId}/stop-async/`);
  },

  /**
   * 删除扫描任务记录
   * @param {string} taskId - 任务ID
   * @returns {Promise} 删除结果
   */
  deleteScanTask(taskId) {
    return api.delete(`/ip-management/scan-tasks/${taskId}/`);
  },

  /**
   * 强制启用所有禁用的Zabbix发现规则
   * @returns {Promise} 启用结果
   */
  forceEnableZabbixRules() {
    return api.post('/ip-management/zabbix/management/');
  },

  /**
   * 获取Zabbix发现规则状态信息
   * @returns {Promise} 规则状态信息
   */
  getZabbixRulesStatus() {
    return api.get('/ip-management/zabbix/management/');
  },

  /**
   * 测试Zabbix连接状态
   * @returns {Promise} 连接状态和诊断信息
   */
  testZabbixConnection() {
    return api.get('/ip-management/zabbix/management/');
  }
};



// 网络扫描API
export const networkAPI = {
  /**
   * 执行网络扫描
   * @param {Object} scanData - 扫描配置
   * @param {Array} scanData.ipRanges - IP范围
   * @param {Array} scanData.ports - 端口列表
   * @param {string} scanData.scanType - 扫描类型
   * @param {number} scanData.timeout - 超时时间
   * @returns {Promise} 扫描任务ID
   */
  startNetworkScan(scanData) {
    return api.post('/network/scan/', scanData);
  },

  /**
   * 获取扫描任务状态
   * @param {string} taskId - 任务ID
   * @returns {Promise} 任务状态
   */
  getScanStatus(taskId) {
    return api.get(`/network/scan/${taskId}/status/`);
  },

  /**
   * 获取扫描结果
   * @param {string} taskId - 任务ID
   * @returns {Promise} 扫描结果
   */
  getScanResults(taskId) {
    return api.get(`/network/scan/${taskId}/results/`);
  },

  /**
   * 取消扫描任务
   * @param {string} taskId - 任务ID
   * @returns {Promise} 取消结果
   */
  cancelScan(taskId) {
    return api.delete(`/network/scan/${taskId}/`);
  },

  /**
   * 获取扫描历史
   * @param {Object} params - 查询参数
   * @returns {Promise} 扫描历史列表
   */
  getScanHistory(params = {}) {
    return api.get('/network/scan/history/', { params });
  },

  /**
   * 删除扫描历史
   * @param {string} taskId - 任务ID
   * @returns {Promise} 删除结果
   */
  deleteScanHistory(taskId) {
    return api.delete(`/network/scan/history/${taskId}/`);
  }
};

// 统一导出
export default {
  ipAPI,
  networkAPI
};