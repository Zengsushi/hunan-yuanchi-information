/**
 * WebSocket客户端管理器
 * 处理用户会话WebSocket连接，接收踢出通知等实时消息
 */

class WebSocketManager {
  constructor() {
    this.socket = null;
    this.reconnectCount = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 3000; // 3秒
    this.heartbeatInterval = 30000; // 30秒心跳
    this.heartbeatTimer = null;
    this.isConnecting = false;
    this.isManualDisconnect = false;
    
    // 事件监听器
    this.listeners = {
      onConnected: [],
      onDisconnected: [],
      onKickedOut: [],
      onForceLogout: [],
      onMessage: [],
      onError: []
    };
  }

  /**
   * 连接WebSocket
   * @param {string} token - 用户认证token
   */
  connect(token) {
    // 更严格的连接状态检查
    if (this.isConnecting) {
      console.log('WebSocket正在连接中，跳过重复连接请求');
      return false;
    }
    
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN) {
        console.log('WebSocket已连接，跳过重复连接请求');
        return false;
      } else if (this.socket.readyState === WebSocket.CONNECTING) {
        console.log('WebSocket正在连接中，跳过重复连接请求');
        return false;
      } else {
        // 如果有旧连接但已关闭，先清理
        console.log('清理旧的WebSocket连接，准备新连接');
        this.socket = null;
      }
    }

    if (!token) {
      console.error('WebSocket连接失败：缺少认证token');
      return false;
    }

    this.isConnecting = true;
    this.isManualDisconnect = false;
    
    console.log('开始建立新的WebSocket连接...');

    try {
      // 构建WebSocket URL - 使用Vue代理，避免与HMR冲突
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host; // 使用当前页面的host，通过Vue代理
      const wsUrl = `${protocol}//${host}/websocket/users/session/?token=${token}`;

      console.log('正在连接WebSocket:', wsUrl);

      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = (event) => {
        console.log('WebSocket连接已建立');
        this.isConnecting = false;
        this.reconnectCount = 0;
        
        // 启动心跳
        this.startHeartbeat();
        
        // 触发连接事件
        this.emit('onConnected', event);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('收到WebSocket消息:', data);

          // 根据消息类型处理
          switch (data.type) {
            case 'connection_established':
              console.log('WebSocket连接确认:', data.message);
              break;
              
            case 'kicked_out':  // 修复消息类型处理，与后端发送的一致
              console.warn('用户被踢出:', data.message);
              this.emit('onKickedOut', data);
              break;
              
            case 'force_logout':  // 保持与后端发送的一致
              console.warn('强制登出:', data.message);
              this.emit('onForceLogout', data);
              break;
              
            case 'pong':
              // 心跳响应
              console.log('心跳响应正常');
              break;
              
            case 'user_status':
              console.log('用户状态更新:', data);
              break;
              
            default:
              console.log('未知消息类型:', data.type);
              this.emit('onMessage', data);
          }
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      this.socket.onclose = (event) => {
        console.log('WebSocket连接已关闭', event.code, event.reason);
        this.isConnecting = false;
        
        // 停止心跳
        this.stopHeartbeat();
        
        // 触发断开连接事件
        this.emit('onDisconnected', event);
        
        // 如果不是手动断开，尝试重连
        if (!this.isManualDisconnect && this.reconnectCount < this.maxReconnectAttempts) {
          this.scheduleReconnect(token);
        }
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket连接错误:', error);
        this.isConnecting = false;
        
        // 触发错误事件
        this.emit('onError', error);
      };

    } catch (error) {
      console.error('创建WebSocket连接失败:', error);
      this.isConnecting = false;
      this.emit('onError', error);
      return false;
    }
    
    return true;
  }

  /**
   * 断开WebSocket连接
   */
  disconnect() {
    this.isManualDisconnect = true;
    this.stopHeartbeat();
    
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN) {
        this.socket.close(1000, '用户主动断开连接');
      }
      this.socket = null;
    }
    
    this.reconnectCount = 0;
    console.log('WebSocket连接已手动断开');
  }

  /**
   * 发送消息
   * @param {Object} message - 要发送的消息对象
   */
  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
      return true;
    } else {
      console.warn('WebSocket未连接，无法发送消息');
      return false;
    }
  }

  /**
   * 启动心跳检测
   */
  startHeartbeat() {
    this.stopHeartbeat(); // 先停止已有的心跳
    
    this.heartbeatTimer = setInterval(() => {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.send({
          type: 'ping',
          timestamp: Date.now()
        });
      }
    }, this.heartbeatInterval);
  }

  /**
   * 停止心跳检测
   */
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * 安排重连
   * @param {string} token - 认证token
   */
  scheduleReconnect(token) {
    this.reconnectCount++;
    console.log(`准备第${this.reconnectCount}次重连...`);
    
    setTimeout(() => {
      if (!this.isManualDisconnect && this.reconnectCount <= this.maxReconnectAttempts) {
        console.log(`正在进行第${this.reconnectCount}次重连`);
        this.connect(token);
      }
    }, this.reconnectInterval * this.reconnectCount); // 递增延迟
  }

  /**
   * 添加事件监听器
   * @param {string} eventType - 事件类型
   * @param {Function} callback - 回调函数
   */
  on(eventType, callback) {
    if (this.listeners[eventType] && typeof callback === 'function') {
      this.listeners[eventType].push(callback);
    }
  }

  /**
   * 移除事件监听器
   * @param {string} eventType - 事件类型
   * @param {Function} callback - 回调函数
   */
  off(eventType, callback) {
    if (this.listeners[eventType]) {
      const index = this.listeners[eventType].indexOf(callback);
      if (index > -1) {
        this.listeners[eventType].splice(index, 1);
      }
    }
  }

  /**
   * 触发事件
   * @param {string} eventType - 事件类型
   * @param {*} data - 事件数据
   */
  emit(eventType, data) {
    if (this.listeners[eventType]) {
      this.listeners[eventType].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`事件监听器执行错误 (${eventType}):`, error);
        }
      });
    }
  }

  /**
   * 获取连接状态
   */
  getStatus() {
    if (!this.socket) return 'DISCONNECTED';
    
    switch (this.socket.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }

  /**
   * 检查是否已连接
   */
  isConnected() {
    return this.socket && this.socket.readyState === WebSocket.OPEN;
  }
}

// 创建全局WebSocket管理器实例
const websocketManager = new WebSocketManager();

export default websocketManager;