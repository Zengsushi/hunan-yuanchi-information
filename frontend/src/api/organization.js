import axios from 'axios';

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
      
      // 跳转到登录页
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== 部门管理 API ====================

/**
 * 获取部门列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 状态筛选
 * @param {string} params.level - 层级筛选
 * @param {string} params.category - 分类筛选
 * @returns {Promise} API响应
 */
export const getDepartments = (params = {}) => {
  return api.get('/organization/departments/', { params });
};


/**
 * 获取部门详情
 * @param {number} id - 部门ID
 * @returns {Promise} API响应
 */
export const getDepartmentDetail = (id) => {
  return api.get(`/organization/departments/${id}/`);
};

/**
 * 创建部门
 * @param {Object} data - 部门数据
 * @param {string} data.name - 部门名称
 * @param {string} data.code - 部门编码
 * @param {number} data.parent - 上级部门ID
 * @param {number} data.manager - 部门负责人ID
 * @param {number} data.sort_order - 排序
 * @param {string} data.status - 状态
 * @param {string} data.description - 描述
 * @returns {Promise} API响应
 */
export const createDepartment = (data) => {
  return api.post('/organization/departments/', data);
};

/**
 * 更新部门
 * @param {number} id - 部门ID
 * @param {Object} data - 部门数据
 * @returns {Promise} API响应
 */
export const updateDepartment = (id, data) => {
  return api.put(`/organization/departments/${id}/`, data);
};

/**
 * 删除部门
 * @param {number} id - 部门ID
 * @returns {Promise} API响应
 */
export const deleteDepartment = (id) => {
  return api.delete(`/organization/departments/${id}/`);
};

/**
 * 获取部门树形结构
 * @returns {Promise} API响应
 */
export const getDepartmentTree = () => {
  return api.get('/organization/departments/tree/');
};

/**
 * 导出部门列表
 * @param {Object} params - 导出参数
 * @returns {Promise} API响应
 */
export const exportDepartments = (params = {}) => {
  return api.get('/organization/departments/export/', {
    params,
    responseType: 'blob'
  });
};

// ==================== 职位管理 API ====================

/**
 * 获取职位列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 状态筛选
 * @param {string} params.level - 级别筛选
 * @param {number} params.department - 部门筛选
 * @param {string} params.category - 分类筛选
 * @returns {Promise} API响应
 */
export const getPositions = (params = {}) => {
  return api.get('/organization/positions/', { params });
};

/**
 * 获取职位详情
 * @param {number} id - 职位ID
 * @returns {Promise} API响应
 */
export const getPositionDetail = (id) => {
  return api.get(`/organization/positions/${id}/`);
};

/**
 * 创建职位
 * @param {Object} data - 职位数据
 * @param {string} data.name - 职位名称
 * @param {string} data.code - 职位编码
 * @param {number} data.department - 所属部门ID
 * @param {string} data.level - 职位级别
 * @param {number} data.min_salary - 最低薪资
 * @param {number} data.max_salary - 最高薪资
 * @param {number} data.sort_order - 排序
 * @param {string} data.status - 状态
 * @param {string} data.description - 描述
 * @param {string} data.requirements - 职位要求
 * @returns {Promise} API响应
 */
export const createPosition = (data) => {
  return api.post('/organization/positions/', data);
};

/**
 * 更新职位
 * @param {number} id - 职位ID
 * @param {Object} data - 职位数据
 * @returns {Promise} API响应
 */
export const updatePosition = (id, data) => {
  return api.put(`/organization/positions/${id}/`, data);
};

/**
 * 删除职位
 * @param {number} id - 职位ID
 * @returns {Promise} API响应
 */
export const deletePosition = (id) => {
  return api.delete(`/organization/positions/${id}/`);
};

/**
 * 根据部门获取职位列表
 * @param {number} departmentId - 部门ID
 * @returns {Promise} API响应
 */
export const getPositionsByDepartment = (departmentId) => {
  return api.get('/organization/positions/by_department/', {
    params: { department_id: departmentId }
  });
};

/**
 * 导出职位列表
 * @param {Object} params - 导出参数
 * @returns {Promise} API响应
 */
export const exportPositions = (params = {}) => {
  return api.get('/organization/positions/export/', {
    params,
    responseType: 'blob'
  });
};

// ==================== 员工管理 API ====================

/**
 * 获取员工列表
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @param {string} params.search - 搜索关键词
 * @param {string} params.status - 状态筛选
 * @param {number} params.department - 部门筛选
 * @param {number} params.position - 职位筛选
 * @param {string} params.category - 分类筛选
 * @returns {Promise} API响应
 */
export const getEmployees = (params = {}) => {
  return api.get('/organization/employees/', { params });
};

/**
 * 获取员工详情
 * @param {number} id - 员工ID
 * @returns {Promise} API响应
 */
export const getEmployeeDetail = (id) => {
  return api.get(`/organization/employees/${id}/`);
};

/**
 * 创建员工
 * @param {Object} data - 员工数据
 * @param {string} data.name - 员工姓名
 * @param {string} data.employee_id - 员工工号
 * @param {number} data.user - 关联用户ID
 * @param {number} data.department - 所属部门ID
 * @param {number} data.position - 职位ID
 * @param {number} data.supervisor - 直属上级ID
 * @param {string} data.phone - 手机号码
 * @param {string} data.email - 邮箱地址
 * @param {string} data.hire_date - 入职日期
 * @param {number} data.salary - 薪资
 * @param {string} data.status - 员工状态
 * @param {number} data.sort_order - 排序
 * @param {string} data.notes - 备注
 * @returns {Promise} API响应
 */
export const createEmployee = (data) => {
  return api.post('/organization/employees/', data);
};

/**
 * 更新员工
 * @param {number} id - 员工ID
 * @param {Object} data - 员工数据
 * @returns {Promise} API响应
 */
export const updateEmployee = (id, data) => {
  return api.put(`/organization/employees/${id}/`, data);
};

/**
 * 删除员工
 * @param {number} id - 员工ID
 * @returns {Promise} API响应
 */
export const deleteEmployee = (id) => {
  return api.delete(`/organization/employees/${id}/`);
};

/**
 * 获取部门下的员工
 * @param {number} departmentId - 部门ID
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export const getDepartmentEmployees = (departmentId, params = {}) => {
  return api.get(`/organization/departments/${departmentId}/employees/`, { params });
};

/**
 * 获取职位下的员工
 * @param {number} positionId - 职位ID
 * @returns {Promise} API响应
 */
export const getPositionEmployees = (positionId) => {
  return api.get(`/organization/positions/${positionId}/employees/`);
};

/**
 * 获取员工的下属列表
 * @param {number} employeeId - 员工ID
 * @returns {Promise} API响应
 */
export const getEmployeeSubordinates = (employeeId) => {
  return api.get(`/organization/employees/${employeeId}/subordinates/`);
};

/**
 * 根据上级获取员工列表
 * @param {number} supervisorId - 上级ID
 * @returns {Promise} API响应
 */
export const getEmployeesBySupervisor = (supervisorId) => {
  return api.get('/organization/employees/by_supervisor/', {
    params: { supervisor_id: supervisorId }
  });
};

/**
 * 获取可用的用户（未关联员工的用户）
 * @param {Object} params - 查询参数
 * @returns {Promise} API响应
 */
export const getAvailableUsers = (params = {}) => {
  return api.get('/organization/employees/available_users/', { params });
};

/**
 * 更改员工状态
 * @param {number} employeeId - 员工ID
 * @param {string} status - 新状态
 * @returns {Promise} API响应
 */
export const changeEmployeeStatus = (employeeId, status) => {
  return api.post(`/organization/employees/${employeeId}/change_status/`, { status });
};

/**
 * 导出员工列表
 * @param {Object} params - 导出参数
 * @returns {Promise} API响应
 */
export const exportEmployees = (params = {}) => {
  return api.get('/organization/employees/export/', {
    params,
    responseType: 'blob'
  });
};

// ==================== 组织架构统计 API ====================

/**
 * 获取部门统计信息
 * @returns {Promise} API响应
 */
export const getDepartmentStatistics = () => {
  return api.get('/organization/departments/statistics/');
};

/**
 * 获取员工统计信息
 * @returns {Promise} API响应
 */
export const getEmployeeStatistics = () => {
  return api.get('/organization/employees/statistics/');
};

// ==================== 组织架构图 API ====================

/**
 * 获取组织架构图数据
 * @param {Object} params - 查询参数
 * @param {number} params.department_id - 根部门ID（可选）
 * @param {number} params.max_depth - 最大深度（可选）
 * @returns {Promise} API响应
 */
export const getOrganizationChart = (params = {}) => {
  return api.get('/organization/chart/', { params });
};

/**
 * 获取员工关系图数据
 * @param {number} employeeId - 员工ID
 * @returns {Promise} API响应
 */
export const getEmployeeRelationChart = (employeeId) => {
  return api.get(`/organization/employees/${employeeId}/relations/`);
};

// ==================== 批量操作 API ====================

/**
 * 批量导入部门
 * @param {FormData} formData - 包含Excel文件的FormData
 * @returns {Promise} API响应
 */
export const batchImportDepartments = (formData) => {
  return api.post('/organization/departments/batch_import/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 批量导入职位
 * @param {FormData} formData - 包含Excel文件的FormData
 * @returns {Promise} API响应
 */
export const batchImportPositions = (formData) => {
  return api.post('/organization/positions/batch_import/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 批量导入员工
 * @param {FormData} formData - 包含Excel文件的FormData
 * @returns {Promise} API响应
 */
export const batchImportEmployees = (formData) => {
  return api.post('/organization/employees/batch_import/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
};

/**
 * 批量更新员工状态
 * @param {Object} data - 批量更新数据
 * @param {Array} data.employee_ids - 员工ID列表
 * @param {string} data.status - 新状态
 * @returns {Promise} API响应
 */
export const batchUpdateEmployeeStatus = (data) => {
  return api.post('/organization/employees/batch_update_status/', data);
};

/**
 * 批量删除员工
 * @param {Array} employeeIds - 员工ID列表
 * @returns {Promise} API响应
 */
export const batchDeleteEmployees = (employeeIds) => {
  return api.post('/organization/employees/batch_delete/', {
    employee_ids: employeeIds
  });
};

// ==================== 默认导出 ====================

export default {
  // 部门管理
  getDepartments,
  getDepartmentDetail,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  getDepartmentTree,
  getDepartmentEmployees,
  exportDepartments,
  
  // 职位管理
  getPositions,
  getPositionDetail,
  createPosition,
  updatePosition,
  deletePosition,
  getPositionsByDepartment,
  getPositionEmployees,
  exportPositions,
  
  // 员工管理
  getEmployees,
  getEmployeeDetail,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  getEmployeeSubordinates,
  getEmployeesBySupervisor,
  getAvailableUsers,
  changeEmployeeStatus,
  exportEmployees,
  
  // 统计信息
  getDepartmentStatistics,
  getEmployeeStatistics,
  
  // 组织架构图
  getOrganizationChart,
  getEmployeeRelationChart,
  
  // 批量操作
  batchImportDepartments,
  batchImportPositions,
  batchImportEmployees,
  batchUpdateEmployeeStatus,
  batchDeleteEmployees
};