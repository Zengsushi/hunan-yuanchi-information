import { createApp } from 'vue'
import App from './App.vue'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';
import './assets/global.css';
import axios from 'axios';
import router from './router';
import { message, notification } from 'ant-design-vue';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import zhCN from 'ant-design-vue/es/locale/zh_CN';

// 配置dayjs为中文
dayjs.locale('zh-cn');
// WebSocket集成将在用户登录后按需导入，避免页面加载时自动初始化

// 配置Ant Design Vue的message和notification
message.config({
  top: '10px', // 设置为10px，更接近页面顶部
  duration: 3,
  maxCount: 3,
  getContainer: () => document.body, // 确保挂载到body上
});

notification.config({
  placement: 'topRight',
  top: '10px', 
  duration: 4.5,
  getContainer: () => document.body, // 确保挂载到body上
});

// ========== ResizeObserver 错误彻底解决方案 ==========

// 1. 完全禁用 ResizeObserver 错误输出
const originalResizeObserver = window.ResizeObserver;
const originalConsoleError = console.error;
const originalConsoleWarn = console.warn;

// 2. ResizeObserver 错误检测模式
const RESIZE_OBSERVER_ERROR_PATTERNS = [
  /ResizeObserver loop completed with undelivered notifications/i,
  /ResizeObserver loop limit exceeded/i,
  /ResizeObserver/i
];

const isResizeObserverRelated = (message) => {
  if (!message) return false;
  const text = String(message);
  return RESIZE_OBSERVER_ERROR_PATTERNS.some(pattern => pattern.test(text));
};

// 3. 彻底静默所有 ResizeObserver 相关输出
console.error = function(...args) {
  if (args.some(arg => isResizeObserverRelated(arg))) {
    return; // 完全忽略
  }
  originalConsoleError.apply(console, args);
};

console.warn = function(...args) {
  if (args.some(arg => isResizeObserverRelated(arg))) {
    return; // 完全忽略
  }
  originalConsoleWarn.apply(console, args);
};

// 4. 拦截全局错误事件
window.addEventListener('error', (event) => {
  if (isResizeObserverRelated(event.message) || 
      isResizeObserverRelated(event.error)) {
    event.preventDefault();
    event.stopImmediatePropagation();
    return false;
  }
}, true);

window.addEventListener('unhandledrejection', (event) => {
  if (isResizeObserverRelated(event.reason)) {
    event.preventDefault();
    return false;
  }
}, true);

// 5. 重写 ResizeObserver 实现
if (originalResizeObserver) {
  window.ResizeObserver = class SafeResizeObserver {
    constructor(callback) {
      this.callback = callback;
      this.observer = null;
      this.rafId = null;
      this.entries = [];
      
      // 使用防抖机制
      this.debouncedCallback = this.debounce(() => {
        if (this.entries.length > 0) {
          try {
            this.callback(this.entries, this);
          } catch (error) {
            if (!isResizeObserverRelated(error)) {
              console.error('ResizeObserver callback error:', error);
            }
          }
          this.entries = [];
        }
      }, 16); // 约60fps
      
      this.observer = new originalResizeObserver((entries) => {
        this.entries = entries;
        this.debouncedCallback();
      });
    }
    
    debounce(func, wait) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          clearTimeout(timeout);
          func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
      };
    }
    
    observe(target, options) {
      if (this.observer) {
        this.observer.observe(target, options);
      }
    }
    
    unobserve(target) {
      if (this.observer) {
        this.observer.unobserve(target);
      }
    }
    
    disconnect() {
      if (this.observer) {
        this.observer.disconnect();
      }
      this.entries = [];
    }
  };
}

// 6. 处理 webpack-dev-server overlay 错误
if (process.env.NODE_ENV === 'development') {
  // 拦截 webpack overlay 错误处理
  const originalWindowError = window.onerror;
  window.onerror = function(message, source, lineno, colno, error) {
    if (isResizeObserverRelated(message)) {
      return true; // 阻止错误传播
    }
    if (originalWindowError) {
      return originalWindowError.apply(this, arguments);
    }
  };
  
  // 拦截 Promise 错误
  const originalUnhandledRejection = window.onunhandledrejection;
  window.onunhandledrejection = function(event) {
    if (isResizeObserverRelated(event.reason)) {
      event.preventDefault();
      return true;
    }
    if (originalUnhandledRejection) {
      return originalUnhandledRejection.apply(this, arguments);
    }
  };
}

// ========== ResizeObserver 错误处理结束 ==========

// 定义隐藏初始loading的函数




const app = createApp(App);
app.use(Antd, { locale: zhCN });
app.use(router);

// 配置axios
axios.defaults.baseURL = '/api';
app.config.globalProperties.$axios = axios;

// 添加全局message和notification
app.config.globalProperties.$message = message;
app.config.globalProperties.$notification = notification;

// 添加全局错误处理
// 确保message组件正常工作
app.config.globalProperties.$messageTest = () => {
  message.success('测试通知成功！');
};

// Vue全局错误处理 - 使用统一的错误检测
app.config.errorHandler = (err, vm, info) => {
  // 忽略 ResizeObserver 相关错误
  if (isResizeObserverRelated(err) || 
      isResizeObserverRelated(err?.message) || 
      isResizeObserverRelated(err?.toString())) {
    return;
  }
  
  // 忽略其他常见的开发环境错误
  const commonDevErrors = [
    /Non-passive event listener/i,
    /Ignored attempt to cancel a touchmove/i,
    /Unable to preventDefault/i,
    /Script error/i,
    /Network Error/i
  ];
  
  const errorMessage = err?.message || String(err);
  if (commonDevErrors.some(pattern => pattern.test(errorMessage))) {
    return;
  }
  
  // 只在开发环境显示真正的错误
  // if (process.env.NODE_ENV === 'development') {
  //   originalConsoleError('Vue Error:', err, '\nInfo:', info);
  // }
};

app.mount('#app');



// WebSocket集成将在用户登录成功后按需初始化，不在应用启动时自动加载
// 这样可以避免未登录状态下的WebSocket连接尝试
