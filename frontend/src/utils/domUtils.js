/**
 * DOM操作工具函数 - 减少ResizeObserver警告
 */

/**
 * 安全的DOM操作包装器
 * @param {Function} operation DOM操作函数
 * @param {number} delay 延迟时间
 * @returns {Promise}
 */
export const safeDOMOperation = (operation, delay = 0) => {
  return new Promise((resolve, reject) => {
    const execute = () => {
      try {
        requestAnimationFrame(() => {
          const result = operation();
          resolve(result);
        });
      } catch (error) {
        if (error.message && error.message.includes('ResizeObserver')) {
          // 静默处理ResizeObserver错误
          resolve(null);
        } else {
          reject(error);
        }
      }
    };
    
    if (delay > 0) {
      setTimeout(execute, delay);
    } else {
      execute();
    }
  });
};

/**
 * 防抖函数 - 减少频繁的DOM操作
 * @param {Function} func 要防抖的函数
 * @param {number} wait 等待时间
 * @param {boolean} immediate 是否立即执行
 * @returns {Function}
 */
export const debounce = (func, wait = 300, immediate = false) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      timeout = null;
      if (!immediate) {
        try {
          func(...args);
        } catch (error) {
          if (!error.message || !error.message.includes('ResizeObserver')) {
            console.error('Debounced function error:', error);
          }
        }
      }
    };
    
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    
    if (callNow) {
      try {
        func(...args);
      } catch (error) {
        if (!error.message || !error.message.includes('ResizeObserver')) {
          console.error('Immediate function error:', error);
        }
      }
    }
  };
};

/**
 * 节流函数 - 限制函数执行频率
 * @param {Function} func 要节流的函数
 * @param {number} limit 限制时间
 * @returns {Function}
 */
export const throttle = (func, limit = 100) => {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      try {
        func.apply(this, args);
      } catch (error) {
        if (!error.message || !error.message.includes('ResizeObserver')) {
          console.error('Throttled function error:', error);
        }
      }
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

/**
 * 安全的ResizeObserver包装器
 * @param {Function} callback 回调函数
 * @returns {ResizeObserver|null}
 */
export const createSafeResizeObserver = (callback) => {
  if (!window.ResizeObserver) {
    return null;
  }
  
  const wrappedCallback = throttle((entries, observer) => {
    try {
      callback(entries, observer);
    } catch (error) {
      if (!error.message || !error.message.includes('ResizeObserver')) {
        console.error('ResizeObserver callback error:', error);
      }
    }
  }, 16); // 约60fps
  
  return new ResizeObserver(wrappedCallback);
};

/**
 * 安全的元素尺寸获取
 * @param {Element} element DOM元素
 * @returns {Object} 尺寸信息
 */
export const getSafeElementSize = (element) => {
  try {
    if (!element) {
      return { width: 0, height: 0 };
    }
    
    const rect = element.getBoundingClientRect();
    return {
      width: rect.width || 0,
      height: rect.height || 0
    };
  } catch (error) {
    console.warn('获取元素尺寸失败:', error);
    return { width: 0, height: 0 };
  }
};

/**
 * 检查是否为ResizeObserver相关错误
 * @param {Error|string} error 错误对象或消息
 * @returns {boolean}
 */
export const isResizeObserverError = (error) => {
  const resizeObserverMessages = [
    'ResizeObserver loop completed with undelivered notifications',
    'ResizeObserver loop limit exceeded',
    'ResizeObserver'
  ];
  
  if (typeof error === 'string') {
    return resizeObserverMessages.some(msg => error.includes(msg));
  }
  
  if (error && error.message) {
    return resizeObserverMessages.some(msg => error.message.includes(msg));
  }
  
  return false;
};