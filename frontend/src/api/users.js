import axios from 'axios';

// WebSocket集成将通过全局变量访问，避免页面加载时自动导入
// 集成模块将在用户登录成功后由UserLogin.vue动态导入并暴露为window.webSocketIntegration

// 创建axios实例
const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加认证token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // 统一错误处理
    if (error.response?.status === 401) {
      // 未授权，清除本地存储并跳转到登录页
      console.warn('收到401错误，用户已被踢出或token已过期');
      
      // 清除所有相关的本地存储
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('userType');
      localStorage.removeItem('username');
      localStorage.removeItem('isAdmin');
      localStorage.removeItem('userRole');
      localStorage.removeItem('remember_user');
      localStorage.removeItem('remember_mode');
      
      // 断开WebSocket连接
      if (window.webSocketIntegration && window.webSocketIntegration.disconnectWebSocket) {
        window.webSocketIntegration.disconnectWebSocket();
      }
      
      // 显示提示信息
      if (typeof window !== 'undefined' && window.antd && window.antd.message) {
        window.antd.message.warning('您的登录状态已失效，请重新登录');
      }
      
      // 延迟跳转，确保消息显示
      setTimeout(() => {
        window.location.href = '/#/login';
      }, 1000);
    }
    return Promise.reject(error);
  }
);

// 用户管理API
export const userAPI = {
  /**
   * 用户登录
   * @param {Object} loginData - 登录数据
   * @param {string} loginData.username - 用户名
   * @param {string} loginData.password - 密码
   * @param {boolean} loginData.remember - 是否记住密码
   * @returns {Promise} 登录响应
   */
  async login(loginData) {
    const response = await api.post('/auth/login/', loginData);
    
    // 不在这里初始化WebSocket，由UserLogin.vue组件负责
    // WebSocket初始化逻辑已移到登录组件中，避免重复连接
    
    return response;
  },

  /**
   * 用户登出
   * @returns {Promise} 登出响应
   */
  async logout() {
    const response = await api.post('/auth/logout/');
    
    // 登出成功后断开WebSocket连接
    if (window.webSocketIntegration) {
      console.log('登出成功，断开WebSocket连接...');
      window.webSocketIntegration.disconnectWebSocket();
    }
    
    return response;
  },

  /**
   * 获取当前用户信息
   * @returns {Promise} 用户信息
   */
  getCurrentUser() {
    return api.get('/auth/me/');
  },

  /**
   * 刷新Token
   * @returns {Promise} 新的Token
   */
  refreshToken() {
    return api.post('/auth/refresh/');
  },

  /**
   * 修改密码
   * @param {Object} passwordData - 密码数据
   * @param {string} passwordData.oldPassword - 旧密码
   * @param {string} passwordData.newPassword - 新密码
   * @returns {Promise} 修改结果
   */
  changePassword(passwordData) {
    return api.put('/auth/change-password/', passwordData);
  },

  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.pageSize - 每页数量
   * @param {string} params.search - 搜索关键词
   * @param {string} params.role - 角色筛选
   * @returns {Promise} 用户列表响应
   */
  getUserList(params = {}) {
    return api.get('/users/', { params });
  },

  

  /**
   * 获取用户统计信息
   * @returns {Promise} 用户统计数据
   */
  getUserStats() {
    return api.get('/users/statistics/');
  },

  /**
   * 创建新用户
   * @param {Object} userData - 用户数据
   * @param {string} userData.username - 用户名
   * @param {string} userData.realName - 真实姓名
   * @param {string} userData.email - 邮箱
   * @param {string} userData.role - 角色
   * @param {string} userData.password - 密码
   * @returns {Promise} 创建结果
   */
  createUser(userData) {
    return api.post('/users/', userData);
  },

  /**
   * 更新用户信息
   * @param {number|string} userId - 用户ID
   * @param {Object} userData - 更新的用户数据
   * @returns {Promise} 更新结果
   */
  updateUser(userId, userData) {
    return api.put(`/users/${userId}/`, userData);
  },

  /**
   * 删除用户
   * @param {number|string} userId - 用户ID
   * @returns {Promise} 删除结果
   */
  deleteUser(userId) {
    return api.delete(`/users/${userId}/`);
  },

  /**
   * 切换用户状态
   * @param {number|string} userId - 用户ID
   * @param {boolean} active - 激活状态
   * @returns {Promise} 切换结果
   */
  toggleUserStatus(userId, active) {
    return api.patch(`/users/${userId}/status/`, { active });
  },

  /**
   * 重置用户密码
   * @param {number|string} userId - 用户ID
   * @returns {Promise} 重置结果
   */
  resetUserPassword(userId) {
    return api.post(`/users/${userId}/reset_password/`);
  },

  /**
   * 踢出用户（关闭所有会话）
   * @param {number|string} userId - 用户ID
   * @returns {Promise} 踢出结果
   */
  kickOutUser(userId) {
    return api.post(`/users/${userId}/kick_out/`);
  },

  /**
   * 获取所有在线会话信息
   * @returns {Promise} 在线会话列表
   */
  getOnlineSessions() {
    return api.get('/users/online-sessions/');
  },

  /**
   * 批量删除用户
   * @param {Array} userIds - 用户ID数组
   * @returns {Promise} 批量删除结果
   */
  batchDeleteUsers(userIds) {
    return api.delete('/users/batch/', { data: { userIds } });
  },

  /**
   * 导出用户列表
   * @param {Object} params - 导出参数
   * @returns {Promise} 导出文件
   */
  exportUsers(params = {}) {
    return api.get('/users/export/', { 
      params,
      responseType: 'blob'
    });
  },

  /**
   * 导入用户列表
   * @param {FormData} formData - 包含文件的表单数据
   * @returns {Promise} 导入结果
   */
  importUsers(formData) {
    return api.post('/users/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  }
};

// 角色管理API
export const roleAPI = {
  /**
   * 获取角色列表
   * @returns {Promise} 角色列表
   */
  getRoleList() {
    return api.get('/admin/roles/');
  },

  /**
   * 创建角色
   * @param {Object} roleData - 角色数据
   * @returns {Promise} 创建结果
   */
  createRole(roleData) {
    return api.post('/admin/roles/', roleData);
  },

  /**
   * 更新角色
   * @param {number|string} roleId - 角色ID
   * @param {Object} roleData - 角色数据
   * @returns {Promise} 更新结果
   */
  updateRole(roleId, roleData) {
    return api.put(`/admin/roles/${roleId}/`, roleData);
  },

  /**
   * 删除角色
   * @param {number|string} roleId - 角色ID
   * @returns {Promise} 删除结果
   */
  deleteRole(roleId) {
    return api.delete(`/admin/roles/${roleId}/`);
  },

  /**
   * 获取角色权限
   * @param {number|string} roleId - 角色ID
   * @returns {Promise} 权限列表
   */
  getRolePermissions(roleId) {
    return api.get(`/admin/roles/${roleId}/permissions/`);
  },

  /**
   * 更新角色权限
   * @param {number|string} roleId - 角色ID
   * @param {Array} permissions - 权限数组
   * @returns {Promise} 更新结果
   */
  updateRolePermissions(roleId, permissions) {
    return api.put(`/admin/roles/${roleId}/permissions/`, { permissions });
  }
};

// 权限管理API
export const permissionAPI = {
  /**
   * 获取权限树
   * @returns {Promise} 权限树结构
   */
  getPermissionTree() {
    return api.get('/admin/permissions/tree/');
  },

  /**
   * 获取所有权限
   * @returns {Promise} 权限列表
   */
  getAllPermissions() {
    return api.get('/admin/permissions/');
  }
};

// 统一导出所有API
export {
  api as axiosInstance
};