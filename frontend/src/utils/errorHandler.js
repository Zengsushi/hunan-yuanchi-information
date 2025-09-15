/**
 * ResizeObserver 错误处理工具
 * 用于处理 "ResizeObserver loop completed with undelivered notifications" 错误
 */

/**
 * 捕获并忽略 ResizeObserver 错误
 * 这是一个已知的无害错误，通常在复杂布局或动态内容更新时发生
 */
export const suppressResizeObserverError = () => {
  // 保存原始的错误处理函数
  const originalErrorHandler = window.onerror;
  const originalUnhandledRejection = window.onunhandledrejection;

  // 重写全局错误处理
  window.onerror = function(message, source, lineno, colno, error) {
    // 检查是否是 ResizeObserver 错误
    if (
      message && 
      typeof message === 'string' && 
      message.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      // 忽略这个错误，不显示在控制台
      return true;
    }
    
    // 其他错误正常处理
    if (originalErrorHandler) {
      return originalErrorHandler.call(this, message, source, lineno, colno, error);
    }
    
    return false;
  };

  // 处理未捕获的Promise错误
  window.onunhandledrejection = function(event) {
    if (
      event.reason && 
      event.reason.message && 
      event.reason.message.includes('ResizeObserver loop completed with undelivered notifications')
    ) {
      // 忽略这个错误
      event.preventDefault();
      return;
    }
    
    // 其他错误正常处理
    if (originalUnhandledRejection) {
      return originalUnhandledRejection.call(this, event);
    }
  };
};

/**
 * 创建一个防抖的 ResizeObserver
 * 用于避免频繁的resize事件触发
 */
export const createDebouncedResizeObserver = (callback, delay = 100) => {
  let timeoutId = null;
  
  return new ResizeObserver((entries) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(() => {
      try {
        callback(entries);
      } catch (error) {
        // 静默处理 ResizeObserver 相关错误
        if (!error.message || !error.message.includes('ResizeObserver')) {
          console.error('ResizeObserver callback error:', error);
        }
      }
    }, delay);
  });
};

/**
 * 安全的元素观察器
 * 提供错误保护的元素尺寸监听
 */
export class SafeResizeObserver {
  constructor(callback, options = {}) {
    this.callback = callback;
    this.debounceDelay = options.debounceDelay || 100;
    this.observer = null;
    this.timeoutId = null;
    
    this.createObserver();
  }
  
  createObserver() {
    try {
      this.observer = new ResizeObserver((entries) => {
        this.handleResize(entries);
      });
    } catch (error) {
      console.warn('Failed to create ResizeObserver:', error);
    }
  }
  
  handleResize(entries) {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
    }
    
    this.timeoutId = setTimeout(() => {
      try {
        this.callback(entries);
      } catch (error) {
        // 静默处理错误，避免控制台报错
        if (process.env.NODE_ENV === 'development') {
          console.debug('ResizeObserver callback handled error:', error.message);
        }
      }
    }, this.debounceDelay);
  }
  
  observe(element) {
    if (this.observer && element) {
      try {
        this.observer.observe(element);
      } catch (error) {
        console.warn('Failed to observe element:', error);
      }
    }
  }
  
  unobserve(element) {
    if (this.observer && element) {
      try {
        this.observer.unobserve(element);
      } catch (error) {
        console.warn('Failed to unobserve element:', error);
      }
    }
  }
  
  disconnect() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    
    if (this.observer) {
      try {
        this.observer.disconnect();
      } catch (error) {
        console.warn('Failed to disconnect ResizeObserver:', error);
      }
      this.observer = null;
    }
  }
}

export default {
  suppressResizeObserverError,
  createDebouncedResizeObserver,
  SafeResizeObserver
};