import axios from 'axios';

// 创建axios实例
const request = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://127.0.0.1:8001/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 请求拦截器
request.interceptors.request.use(
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
request.interceptors.response.use(
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

export default request;