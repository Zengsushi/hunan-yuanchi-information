// API统一入口文件

// 用户相关API
export { userAPI, roleAPI, permissionAPI } from './users';


// 字典管理API - 使用新的admin_management应用
export const dictionaryAPI = {
  // 获取所有字典数据
  getDictionaryList: (params) => import('./users').then(m => m.axiosInstance.get('/dictionaries/', { params })),
  
  // 根据分类获取字典数据
  getDictionaryByCategory: async (category, params = {}) => {
    const m = await import('./users');
    return await m.axiosInstance.get(`/dictionaries/by-category/${category}/`, { params });
  },
  
  // 获取字典分类
  getDictionaryCategories: () => import('./users').then(m => m.axiosInstance.get('/dictionaries/categories/')),
  
  // 创建字典项
  createDictionary: (data) => import('./users').then(m => m.axiosInstance.post('/dictionaries/', data)),
  
  // 更新字典项
  updateDictionary: (id, data) => import('./users').then(m => m.axiosInstance.put(`/dictionaries/${id}/`, data)),
  
  // 删除字典项
  deleteDictionary: (id) => import('./users').then(m => m.axiosInstance.delete(`/dictionaries/${id}/`)),
  
  // 批量创建字典项
  batchCreateDictionary: (data) => import('./users').then(m => m.axiosInstance.post('/dictionaries/batch_create/', data)),
  
  // 初始化字典数据 - 使用批量创建接口
  initDictionaryData: async () => {
    // 定义初始字典数据
    const dictionaryData = [
      // 用户分类
      {
        category: 'user_category',
        key: 'admin',
        label: '管理员',
        description: '系统管理员用户',
        priority: 100,
        status: 'active'
      },
      {
        category: 'user_category',
        key: 'operator',
        label: '操作员',
        description: '系统操作员用户',
        priority: 80,
        status: 'active'
      },
      {
        category: 'user_category',
        key: 'viewer',
        label: '查看者',
        description: '只读权限用户',
        priority: 60,
        status: 'active'
      },
      // 系统配置
      {
        category: 'system_config',
        key: 'session_timeout',
        label: '会话超时时间',
        description: '用户会话的超时时间设置',
        priority: 90,
        status: 'active'
      },
      {
        category: 'system_config',
        key: 'password_policy',
        label: '密码策略',
        description: '用户密码复杂度要求',
        priority: 80,
        status: 'active'
      },
      // 资产类型
      {
        category: 'asset_type',
        key: 'server',
        label: '服务器',
        description: '物理服务器或虚拟机',
        priority: 100,
        status: 'active'
      },
      {
        category: 'asset_type',
        key: 'network_device',
        label: '网络设备',
        description: '交换机、路由器等网络设备',
        priority: 90,
        status: 'active'
      },
      // 部门
      {
        category: 'department',
        key: 'it',
        label: 'IT部门',
        description: '信息技术部门',
        priority: 100,
        status: 'active'
      },
      {
        category: 'department',
        key: 'ops',
        label: '运维部门',
        description: '系统运维部门',
        priority: 90,
        status: 'active'
      },
      // 状态
      {
        category: 'status',
        key: 'active',
        label: '活跃',
        description: '正常活跃状态',
        priority: 100,
        status: 'active'
      },
      {
        category: 'status',
        key: 'inactive',
        label: '非活跃',
        description: '暂时停用状态',
        priority: 80,
        status: 'active'
      }
    ];
    
    const m = await import('./users');
    return await m.axiosInstance.post('/dictionaries/batch_create/', dictionaryData);
  },

  // 分类管理API
  // 创建字典分类
  createDictionaryCategory: (data) => import('./users').then(m => m.axiosInstance.post('/dictionaries/categories/', data)),
  
  // 更新字典分类
  updateDictionaryCategory: (key, data) => import('./users').then(m => m.axiosInstance.put(`/dictionaries/categories/${key}/`, data)),
  
  // 删除字典分类
  deleteDictionaryCategory: (key) => import('./users').then(m => m.axiosInstance.delete(`/dictionaries/categories/${key}/`))
};

// 别名保持兼容性
export const dictionariesAPI = dictionaryAPI;

// 系统配置API - 新增
export const systemConfigAPI = {
  // 获取系统配置列表
  getConfigList: (params) => import('./users').then(m => m.axiosInstance.get('/admin/system-configs/', { params })),
  
  // 创建系统配置
  createConfig: (data) => import('./users').then(m => m.axiosInstance.post('/admin/system-configs/', data)),
  
  // 更新系统配置
  updateConfig: (id, data) => import('./users').then(m => m.axiosInstance.put(`/admin/system-configs/${id}/`, data)),
  
  // 删除系统配置
  deleteConfig: (id) => import('./users').then(m => m.axiosInstance.delete(`/admin/system-configs/${id}/`))
};

// 管理日志API - 更新为新的路径
export const adminLogsAPI = {
  // 获取管理日志列表
  getLogsList: (params) => import('./users').then(m => m.axiosInstance.get('/admin/logs/', { params })),
  
  // 导出日志
  exportLogs: (params) => import('./users').then(m => m.axiosInstance.get('/admin/logs/export/', { 
    params, 
    responseType: 'blob' 
  }))
};

// 仪表盘API - 新增
export const dashboardAPI = {
  // 获取仪表盘统计数据
  getStats: () => import('./users').then(m => m.axiosInstance.get('/admin/dashboard/stats/')),
  
  // 获取仪表盘组件
  getWidgets: (params) => import('./users').then(m => m.axiosInstance.get('/admin/dashboard-widgets/', { params })),
  
  // 创建仪表盘组件
  createWidget: (data) => import('./users').then(m => m.axiosInstance.post('/admin/dashboard-widgets/', data)),
  
  // 更新仪表盘组件
  updateWidget: (id, data) => import('./users').then(m => m.axiosInstance.put(`/admin/dashboard-widgets/${id}/`, data)),
  
  // 删除仪表盘组件
  deleteWidget: (id) => import('./users').then(m => m.axiosInstance.delete(`/admin/dashboard-widgets/${id}/`))
};

// 操作日志API（兼容性，保留原有接口）
export const logsAPI = adminLogsAPI;

// 系统设置API（兼容性，保留原有接口）
export const settingsAPI = systemConfigAPI;

// 默认导出常用API
export { userAPI as default } from './users';
export { ipAPI } from './ipManagement';