/**
 * 路由守卫 - 专门处理ResizeObserver和资源清理
 */

// 全局资源清理函数
export const cleanupGlobalResources = () => {
  console.log('执行全局资源清理...');
  
  try {
    // 1. 清理所有定时器
    const highestTimeoutId = setTimeout(function(){}, 1);
    for (let i = 0; i < highestTimeoutId; i++) {
      clearTimeout(i);
    }
    
    const highestIntervalId = setInterval(function(){}, 1);
    for (let i = 0; i < highestIntervalId; i++) {
      clearInterval(i);
    }
    
    // 2. 强制断开所有ResizeObserver
    const allElements = document.querySelectorAll('*');
    allElements.forEach(element => {
      if (element._resizeObserver) {
        try {
          element._resizeObserver.disconnect();
          delete element._resizeObserver;
        } catch (error) {
          // 静默处理
        }
      }
    });
    
    // 3. 清理可能的事件监听器
    const events = ['resize', 'scroll', 'load'];
    events.forEach(eventType => {
      const listeners = window[`__${eventType}_listeners__`];
      if (listeners && Array.isArray(listeners)) {
        listeners.forEach(listener => {
          try {
            window.removeEventListener(eventType, listener);
          } catch (error) {
            // 静默处理
          }
        });
        window[`__${eventType}_listeners__`] = [];
      }
    });
    
    // 4. 强制垃圾回收提示（如果支持）
    if (window.gc && typeof window.gc === 'function') {
      window.gc();
    }
    
    console.log('全局资源清理完成');
  } catch (error) {
    console.debug('全局资源清理时出错:', error.message);
  }
};

// 路由切换前的清理
export const beforeRouteLeave = (to, from, next) => {
  console.log(`路由切换: ${from.path} -> ${to.path}`);
  
  // 如果是从IP管理页面离开
  if (from.path && from.path.includes('ip')) {
    console.log('从IP管理页面离开，执行深度清理...');
    
    // 延迟执行清理，确保组件生命周期完成
    setTimeout(() => {
      cleanupGlobalResources();
    }, 100);
  }
  
  next();
};

// 路由切换后的初始化
export const afterRouteEnter = (to, from) => {
  console.log(`路由进入: ${to.path}`);
  
  // 如果是进入IP管理页面
  if (to.path && to.path.includes('ip')) {
    console.log('进入IP管理页面，重新初始化错误处理...');
    
    // 延迟重新初始化错误处理
    setTimeout(() => {
      if (window.suppressResizeObserverError) {
        window.suppressResizeObserverError();
      }
    }, 200);
  }
};

// 创建安全的路由切换处理器
export const createSafeRouteHandler = (router) => {
  // 路由前置守卫
  router.beforeEach((to, from, next) => {
    beforeRouteLeave(to, from, next);
  });
  
  // 路由后置守卫
  router.afterEach((to, from) => {
    afterRouteEnter(to, from);
  });
  
  return router;
};

export default {
  cleanupGlobalResources,
  beforeRouteLeave,
  afterRouteEnter,
  createSafeRouteHandler
};