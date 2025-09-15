/**
 * WebSocket集成模块
 * 处理用户登录时的WebSocket连接建立和踢出通知处理
 */

import websocketManager from './websocketManager';
import { message } from 'ant-design-vue';

class WebSocketIntegration {
  constructor() {
    this.isInitialized = false;
    this.currentUser = null;
    
    // 绑定事件处理器
    this.setupEventHandlers();
  }

  /**
   * 初始化WebSocket集成
   * 在用户登录后调用
   */
  initialize() {
    if (this.isInitialized) {
      console.log('WebSocket集成已初始化，跳过重复初始化');
      
      // 检查是否需要重新连接
      const token = localStorage.getItem('token');
      const isLoggedIn = localStorage.getItem('isLoggedIn');
      
      if (token && isLoggedIn === 'true' && !websocketManager.isConnected()) {
        console.log('检测到未连接，尝试重新连接WebSocket...');
        this.connectWebSocket(token);
      }
      return;
    }

    const token = localStorage.getItem('token');
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    
    if (token && isLoggedIn === 'true') {
      console.log('初始化WebSocket连接...');
      this.connectWebSocket(token);
    } else {
      console.log('用户未登录，跳过WebSocket初始化');
    }
    
    this.isInitialized = true;
  }

  /**
   * 建立WebSocket连接
   * @param {string} token - 用户认证token
   */
  connectWebSocket(token) {
    if (!token) {
      console.warn('无法建立WebSocket连接：缺少token');
      return;
    }

    // 如果已经有连接，先检查状态
    if (websocketManager.isConnected()) {
      console.log('WebSocket已连接，跳过重复连接');
      return;
    }

    try {
      console.log('开始建立WebSocket连接...');
      const success = websocketManager.connect(token);
      if (success) {
        console.log('WebSocket连接已启动');
      } else {
        console.log('WebSocket连接被跳过（可能已存在连接）');
      }
    } catch (error) {
      console.error('启动WebSocket连接失败:', error);
    }
  }

  /**
   * 断开WebSocket连接
   */
  disconnectWebSocket() {
    try {
      websocketManager.disconnect();
      console.log('WebSocket连接已断开');
    } catch (error) {
      console.error('断开WebSocket连接失败:', error);
    }
  }

  /**
   * 设置事件处理器
   */
  setupEventHandlers() {
    // 连接建立事件
    websocketManager.on('onConnected', (event) => {
      console.log('WebSocket连接已建立');
      
      // 可以在这里添加连接成功的提示
      // message.success({
      //   content: '实时通信连接已建立',
      //   duration: 2
      // });
    });

    // 连接断开事件
    websocketManager.on('onDisconnected', (event) => {
      console.log('WebSocket连接已断开');
      
      // 如果是异常断开，可以提示用户
      if (event.code !== 1000 && this.isLoggedIn()) {
        console.warn('WebSocket连接异常断开，将尝试重连');
      }
    });

    // 被踢出事件
    websocketManager.on('onKickedOut', (data) => {
      console.warn('收到踢出通知:', data);
      this.handleKickedOut(data);
    });

    // 强制登出事件
    websocketManager.on('onForceLogout', (data) => {
      console.warn('收到强制登出通知:', data);
      this.handleForceLogout(data);
    });

    // 连接错误事件
    websocketManager.on('onError', (error) => {
      console.error('WebSocket连接错误:', error);
      
      // 如果用户已登录但WebSocket连接失败，可以提示
      if (this.isLoggedIn()) {
        console.warn('实时通信连接出现问题，某些功能可能受到影响');
      }
    });
  }

  /**
   * 处理被踢出通知
   * @param {Object} data - 踢出通知数据
   */
  handleKickedOut(data) {
    const { message: kickMessage, reason, kicked_by } = data;
    
    console.log('处理被踢出通知:', data);
    console.log('kickMessage:', kickMessage);
    console.log('reason:', reason);
    console.log('kicked_by:', kicked_by);
    console.log('即将显示倒计时提示');
    
    // 创建倒计时功能
    this.showKickOutCountdown(kickMessage, reason, kicked_by);
    
    console.log('倒计时功能已启动');
  }

  /**
   * 显示被踢出倒计时提示
   * @param {string} kickMessage - 踢出消息
   * @param {string} reason - 踢出原因
   * @param {string} kicked_by - 操作者
   */
  showKickOutCountdown(kickMessage, reason, kicked_by) {
    console.log('开始显示踢出倒计时提示');
    console.log('参数:', { kickMessage, reason, kicked_by });
    
    let countdown = 5; // 5秒倒计时
    
    // 创建带倒计时的消息内容
    const updateMessage = () => {
      const messageObj = {
        content: `${kickMessage} - ${countdown}秒后自动退出`,
        description: `原因：${reason} (操作者：${kicked_by})`,
        duration: 0, // 不自动消失
        key: 'kick-out-notification', // 唯一标识符，用于更新消息
        onClose: () => {
          console.log('用户手动关闭踢出提示');
          // 如果用户手动关闭，也要执行登出
          this.performLogout('kicked');
        }
      };
      console.log('生成的消息对象:', messageObj);
      return messageObj;
    };
    
    // 显示初始消息
    console.log('显示初始踢出消息');
    message.error(updateMessage());
    console.log('初始消息已显示');
    
    // 开始倒计时
    console.log('开始5秒倒计时');
    const timer = setInterval(() => {
      countdown--;
      console.log(`倒计时: ${countdown}秒`);
      
      if (countdown > 0) {
        // 更新消息
        console.log('更新踢出消息');
        message.error(updateMessage());
      } else {
        // 倒计时结束，清除定时器并执行登出
        console.log('倒计时结束，清除定时器');
        clearInterval(timer);
        
        // 显示最后一个消息
        console.log('显示最后一个踢出消息');
        message.error({
          content: `${kickMessage} - 正在退出登录...`,
          description: `原因：${reason} (操作者：${kicked_by})`,
          duration: 2,
          key: 'kick-out-notification'
        });
        
        // 执行登出
        console.log('即将执行登出操作');
        setTimeout(() => {
          this.performLogout('kicked');
        }, 500);
      }
    }, 1000);
    
    console.log('倒计时定时器已设置');
  }

  /**
   * 处理强制登出通知
   * @param {Object} data - 强制登出通知数据
   */
  handleForceLogout(data) {
    const { message: logoutMessage, reason } = data;
    
    console.log('处理强制登出通知:', data);
    
    // 创建倒计时功能
    this.showForceLogoutCountdown(logoutMessage, reason);
  }

  /**
   * 显示强制登出倒计时提示
   * @param {string} logoutMessage - 登出消息
   * @param {string} reason - 登出原因
   */
  showForceLogoutCountdown(logoutMessage, reason) {
    let countdown = 5; // 5秒倒计时
    
    // 创建带倒计时的消息内容
    const updateMessage = () => {
      return {
        content: `${logoutMessage} - ${countdown}秒后自动退出`,
        description: `原因：${reason}`,
        duration: 0, // 不自动消失
        key: 'force-logout-notification', // 唯一标识符
        onClose: () => {
          // 如果用户手动关闭，也要执行登出
          this.performLogout('force');
        }
      };
    };
    
    // 显示初始消息
    message.warning(updateMessage());
    
    // 开始倒计时
    const timer = setInterval(() => {
      countdown--;
      
      if (countdown > 0) {
        // 更新消息
        message.warning(updateMessage());
      } else {
        // 倒计时结束，清除定时器并执行登出
        clearInterval(timer);
        
        // 显示最后一个消息
        message.warning({
          content: `${logoutMessage} - 正在退出登录...`,
          description: `原因：${reason}`,
          duration: 2,
          key: 'force-logout-notification'
        });
        
        // 执行登出
        setTimeout(() => {
          this.performLogout('force');
        }, 500);
      }
    }, 1000);
  }

  /**
   * 执行登出操作
   * @param {string} reason - 登出原因
   */
  performLogout(reason = 'normal') {
    console.log(`执行登出操作，原因：${reason}`);
    
    try {
      // 断开WebSocket连接
      this.disconnectWebSocket();
      
      // 清除本地存储的登录状态
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      localStorage.removeItem('isLoggedIn');
      localStorage.removeItem('userType');
      localStorage.removeItem('username');
      localStorage.removeItem('isAdmin');
      localStorage.removeItem('userRole');
      localStorage.removeItem('remember_user');
      localStorage.removeItem('remember_mode');
      
      // 根据登出原因显示不同的消息
      const messages = {
        kicked: '', // 不再显示，因为已经在handleKickedOut中显示过了
        force: '',  // 不再显示，因为已经在handleForceLogout中显示过了
        normal: '已退出登录'
      };
      
      // 只有在非WebSocket触发的登出情况下才显示消息
      if (reason === 'normal') {
        message.info({
          content: messages[reason] || messages.normal,
          duration: 2
        });
      }
      
      // 跳转到登录页面
      setTimeout(() => {
        window.location.href = '/#/login';
      }, 1000);
      
    } catch (error) {
      console.error('执行登出操作时出错:', error);
      
      // 即使出错也要强制跳转到登录页
      setTimeout(() => {
        window.location.href = '/#/login';
      }, 1000);
    }
  }

  /**
   * 检查用户是否已登录
   */
  isLoggedIn() {
    const token = localStorage.getItem('token');
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    return token && isLoggedIn === 'true';
  }

  /**
   * 获取WebSocket连接状态
   */
  getConnectionStatus() {
    return websocketManager.getStatus();
  }

  /**
   * 检查WebSocket是否已连接
   */
  isWebSocketConnected() {
    return websocketManager.isConnected();
  }

  /**
   * 发送WebSocket消息
   * @param {Object} message - 消息对象
   */
  sendMessage(message) {
    return websocketManager.send(message);
  }

  /**
   * 添加自定义事件监听器
   * @param {string} eventType - 事件类型
   * @param {Function} callback - 回调函数
   */
  addEventListener(eventType, callback) {
    websocketManager.on(eventType, callback);
  }

  /**
   * 移除自定义事件监听器
   * @param {string} eventType - 事件类型
   * @param {Function} callback - 回调函数
   */
  removeEventListener(eventType, callback) {
    websocketManager.off(eventType, callback);
  }

  /**
   * 清理资源
   */
  cleanup() {
    this.disconnectWebSocket();
    this.isInitialized = false;
    this.currentUser = null;
  }

  /**
   * 重置 WebSocket 集成状态
   * 用于新的登录会话
   */
  reset() {
    console.log('重置 WebSocket 集成状态...');
    this.disconnectWebSocket();
    this.isInitialized = false;
    this.currentUser = null;
  }
}

// 创建全局WebSocket集成实例
const webSocketIntegration = new WebSocketIntegration();

// 初始化逻辑已移到用户登录成功后的API调用中

export default webSocketIntegration;