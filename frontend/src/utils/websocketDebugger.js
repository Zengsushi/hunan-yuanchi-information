/**
 * WebSocket调试工具
 * 用于诊断WebSocket连接问题
 */

export class WebSocketDebugger {
  constructor() {
    this.logs = [];
    this.isDebugMode = process.env.NODE_ENV === 'development';
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      type,
      message: typeof message === 'object' ? JSON.stringify(message) : message
    };
    
    this.logs.push(logEntry);
    
    if (this.isDebugMode) {
      console.log(`[WebSocket Debug ${type.toUpperCase()}] ${timestamp}: ${logEntry.message}`);
    }
    
    // 保持最近100条日志
    if (this.logs.length > 100) {
      this.logs = this.logs.slice(-100);
    }
  }

  error(message) {
    this.log(message, 'error');
  }

  warn(message) {
    this.log(message, 'warn');
  }

  info(message) {
    this.log(message, 'info');
  }

  debug(message) {
    this.log(message, 'debug');
  }

  /**
   * 诊断WebSocket连接环境
   */
  diagnoseEnvironment() {
    const diagnosis = {
      timestamp: new Date().toISOString(),
      browser: {
        userAgent: navigator.userAgent,
        webSocketSupport: typeof WebSocket !== 'undefined',
        protocol: window.location.protocol,
        hostname: window.location.hostname,
        port: window.location.port
      },
      localStorage: {
        token: !!localStorage.getItem('token'),
        isLoggedIn: localStorage.getItem('isLoggedIn'),
        userType: localStorage.getItem('userType'),
        username: localStorage.getItem('username')
      },
      websocketIntegration: {
        exists: !!window.webSocketIntegration,
        initialized: window.webSocketIntegration?.isInitialized || false
      }
    };

    this.info(`环境诊断结果: ${JSON.stringify(diagnosis, null, 2)}`);
    return diagnosis;
  }

  /**
   * 测试WebSocket连接
   */
  async testConnection() {
    this.info('开始WebSocket连接测试...');
    
    // 检查多个token来源
    let token = localStorage.getItem('token') || 
                localStorage.getItem('temp_test_token') ||
                sessionStorage.getItem('token');
    
    if (!token) {
      this.error('测试失败: 缺少认证token，请先登录或在登录表单中填写用户名密码');
      return false;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host; // 使用当前页面的host，通过Vue代理
    const wsUrl = `${protocol}//${host}/websocket/users/session/?token=${token}`;

    this.info(`测试连接URL: ${wsUrl}`);

    return new Promise((resolve) => {
      const testSocket = new WebSocket(wsUrl);
      const timeout = setTimeout(() => {
        this.error('连接测试超时 (10秒)');
        testSocket.close();
        resolve(false);
      }, 10000);

      testSocket.onopen = (event) => {
        clearTimeout(timeout);
        this.info('测试连接成功建立');
        testSocket.close();
        resolve(true);
      };

      testSocket.onerror = (error) => {
        clearTimeout(timeout);
        this.error(`测试连接失败: ${error}`);
        resolve(false);
      };

      testSocket.onclose = (event) => {
        this.info(`测试连接关闭: code=${event.code}, reason=${event.reason}`);
      };
    });
  }

  /**
   * 获取所有日志
   */
  getLogs() {
    return this.logs;
  }

  /**
   * 清空日志
   */
  clearLogs() {
    this.logs = [];
    this.info('日志已清空');
  }

  /**
   * 导出诊断报告
   */
  exportDiagnosisReport() {
    const report = {
      timestamp: new Date().toISOString(),
      environment: this.diagnoseEnvironment(),
      logs: this.logs,
      websocketManager: {
        status: window.webSocketIntegration?.getConnectionStatus?.() || 'unknown',
        isConnected: window.webSocketIntegration?.isWebSocketConnected?.() || false
      }
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `websocket-diagnosis-${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    this.info('诊断报告已导出');
    return report;
  }
}

// 创建全局调试器实例
const wsDebugger = new WebSocketDebugger();

// 全局暴露调试器
if (typeof window !== 'undefined') {
  window.webSocketDebugger = wsDebugger;
}

export default wsDebugger;