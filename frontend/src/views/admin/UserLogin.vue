<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="geometric-shapes">
        <div class="shape circle-1"></div>
        <div class="shape circle-2"></div>
        <div class="shape triangle-1"></div>
        <div class="shape square-1"></div>
      </div>
      <div class="gradient-overlay"></div>
      
      <!-- 粒子效果 -->
      <div class="particles">
        <div class="particle" v-for="n in 20" :key="n" :style="getParticleStyle(n)"></div>
      </div>
      
      <!-- 光晕效果 -->
      <div class="glow glow-1"></div>
      <div class="glow glow-2"></div>
      <div class="glow glow-3"></div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧信息面板 -->
      <div class="info-panel">
        <div class="brand-section">
          <div class="logo">
            <DatabaseOutlined class="logo-icon" />
          </div>
          <h1 class="brand-title">运维监控系统</h1>
          <p class="brand-subtitle">专业的资产管理与监控平台</p>
        </div>
        
        <div class="features-list">
          <div class="feature-item">
            <div class="feature-icon-wrapper">
              <MonitorOutlined class="feature-icon" />
            </div>
            <div class="feature-content">
              <h3 class="feature-title">实时监控资产状态</h3>
              <p class="feature-desc">7×24小时不间断监控，实时掌握设备运行状态</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon-wrapper">
              <BellOutlined class="feature-icon" />
            </div>
            <div class="feature-content">
              <h3 class="feature-title">智能告警管理</h3>
              <p class="feature-desc">AI驱动的智能告警，精准识别异常并及时通知</p>
            </div>
          </div>
          <div class="feature-item">
            <div class="feature-icon-wrapper">
              <BarChartOutlined class="feature-icon" />
            </div>
            <div class="feature-content">
              <h3 class="feature-title">数据可视化分析</h3>
              <p class="feature-desc">多维度数据分析，直观展示运维趋势和性能指标</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-panel">
        <div class="login-container">
          <div class="login-header">
            <h2 class="login-title">欢迎登录</h2>
            <p class="login-subtitle">请选择登录方式并输入您的凭据</p>
          </div>

          <!-- 登录模式切换 -->
          <div class="mode-selector">
            <div class="mode-options">
              <button 
                class="mode-option"
                :class="{ active: loginMode === 'user' }"
                @click="switchLoginMode('user')"
              >
                <UserOutlined class="mode-icon" />
                <span>普通用户</span>
              </button>
              <button 
                class="mode-option"
                :class="{ active: loginMode === 'admin' }"
                @click="switchLoginMode('admin')"
              >
                <CrownOutlined class="mode-icon" />
                <span>管理员</span>
              </button>
            </div>
          </div>

          <!-- 登录表单 -->
          <a-form
            :model="loginForm"
            :rules="rules"
            @finish="handleLogin"
            @finishFailed="handleLoginFailed"
            class="login-form"
          >
            <a-form-item name="username" class="form-group">
              <label class="form-label">用户名</label>
              <div class="input-group">
                <UserOutlined class="input-prefix-icon" />
                <a-input
                  v-model:value="loginForm.username"
                  size="large"
                  placeholder="请输入用户名"
                  class="form-input"
                  @focus="onInputFocus"
                  @blur="onInputBlur"
                />
              </div>
            </a-form-item>

            <a-form-item name="password" class="form-group">
              <label class="form-label">密码</label>
              <div class="input-group">
                <LockOutlined class="input-prefix-icon" />
                <a-input-password
                  v-model:value="loginForm.password"
                  size="large"
                  placeholder="请输入密码"
                  class="form-input"
                  @focus="onInputFocus"
                  @blur="onInputBlur"
                />
              </div>
            </a-form-item>

            <div class="form-options">
              <a-checkbox v-model:checked="loginForm.remember" class="remember-checkbox">
                记住登录状态
              </a-checkbox>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>

            <a-form-item class="form-submit">
              <a-button
                type="primary"
                html-type="submit"
                size="large"
                :loading="loading"
                class="login-button"
                block
                @mousedown="onButtonPress"
                @mouseup="onButtonRelease"
                @mouseleave="onButtonRelease"
              >
                <template #icon v-if="!loading">
                  <LoginOutlined class="button-icon" />
                </template>
                <span class="button-text">{{ loading ? '登录中...' : (loginMode === 'admin' ? '管理员登录' : '用户登录') }}</span>
              </a-button>
            </a-form-item>
          </a-form>

          <!-- 底部信息 -->
          <div class="login-footer">
            <div class="security-badge">
              <SafetyCertificateOutlined class="security-icon" />
              <span>安全加密传输</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部版权 -->
    <div class="page-footer">
      <p>&copy; 2024 运维监控系统 | 技术支持：运维团队</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import {
  DatabaseOutlined,
  UserOutlined,
  LockOutlined,
  LoginOutlined,
  SafetyCertificateOutlined,
  CrownOutlined,
  MonitorOutlined,
  BellOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue';
import { userAPI } from '@/api/users';

const router = useRouter();
const loading = ref(false);
const loginMode = ref('user');

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ]
};

// 切换登录模式
const switchLoginMode = (mode) => {
  loginMode.value = mode;
  loginForm.username = '';
  loginForm.password = '';
  loginForm.remember = false;
};

// 动画相关函数
const onInputFocus = (e) => {
  e.target.parentElement.classList.add('input-focused');
};

const onInputBlur = (e) => {
  e.target.parentElement.classList.remove('input-focused');
};

const onButtonPress = (e) => {
  e.target.classList.add('button-pressed');
};

const onButtonRelease = (e) => {
  e.target.classList.remove('button-pressed');
};

// 粒子动画
const getParticleStyle = (index) => {
  const size = Math.random() * 4 + 2;
  const left = Math.random() * 100;
  const animationDelay = Math.random() * 20;
  const animationDuration = Math.random() * 10 + 15;
  
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    animationDelay: `${animationDelay}s`,
    animationDuration: `${animationDuration}s`
  };
};

// 登录处理
const handleLogin = async () => {
  loading.value = true;
  
  // 清理旧的WebSocket连接
  if (typeof window !== 'undefined' && window.webSocketIntegration) {
    console.log('清理旧的WebSocket连接...');
    window.webSocketIntegration.reset();
  }
  
  try {
    const response = await userAPI.login({
      username: loginForm.username,
      password: loginForm.password,
      remember: loginForm.remember,
      loginMode: loginMode.value
    });
    
    if (response.status === 200 && response.data.code === 200) {
      const userData = response.data.data;
      
      // 保存认证信息
      if (userData && userData.token) {
        localStorage.setItem('token', userData.token);
      }
      
      if (userData && userData.user) {
        localStorage.setItem('userInfo', JSON.stringify(userData.user));
        localStorage.setItem('username', userData.user.username);
        
        const isAdmin = userData.user.is_admin || userData.user.role === 'admin';
        const userRole = userData.user.role || (userData.user.is_admin ? 'admin' : 'viewer');
        
        localStorage.setItem('userRole', userRole);
        localStorage.setItem('isAdmin', isAdmin.toString());
        
        // 权限验证
        if (loginMode.value === 'admin' && !isAdmin) {
          message.error({
            content: '您没有管理员权限，无法使用管理员模式登录',
            duration: 1
          });
          return;
        }
        
        if (loginMode.value === 'user' && isAdmin) {
          message.warning({
            content: '检测到您是管理员，建议使用管理员模式登录以获得完整功能',
            duration: 1
          });
        }
        
        const userType = isAdmin ? 'admin' : 'user';
        localStorage.setItem('userType', userType);
      }
      
      localStorage.setItem('isLoggedIn', 'true');
      
      // 记住用户
      if (loginForm.remember) {
        localStorage.setItem('remember_user', loginForm.username);
        localStorage.setItem('remember_mode', loginMode.value);
      } else {
        localStorage.removeItem('remember_user');
        localStorage.removeItem('remember_mode');
      }
      
      message.success({
        content: '登录成功',
        duration: 1
      });
      
      // 初始化WebSocket
      try {
        const webSocketModule = await import('@/utils/webSocketIntegration');
        const webSocketIntegration = webSocketModule.default;
        window.webSocketIntegration = webSocketIntegration;
        
        webSocketIntegration.reset();
        setTimeout(() => {
          webSocketIntegration.initialize();
        }, 100);
      } catch (error) {
        console.error('WebSocket初始化失败:', error);
      }
      
      // 触发菜单更新
      try {
        // 通知App.vue重新获取菜单
        window.dispatchEvent(new CustomEvent('userLoggedIn'));
      } catch (error) {
        console.error('触发菜单更新失败:', error);
      }
      
      // 根据用户类型跳转到不同页面
      setTimeout(() => {
        const isAdmin = localStorage.getItem('isAdmin') === 'true';
        if (loginMode.value === 'admin' && isAdmin) {
          router.push('/admin/dashboard');
        } else {
          router.push('/');
        }
      }, 500);
      
    } else {
      message.error({
        content: response.data.message || '登录失败，请检查用户名和密码',
        duration: 1
      });
    }
  } catch (error) {
    console.error('登录错误:', error);
    if (error.response && error.response.data && error.response.data.message) {
      message.error({
        content: error.response.data.message,
        duration: 1
      });
    } else {
      message.error({
        content: '网络错误，请稍后重试',
        duration: 1
      });
    }
  } finally {
    loading.value = false;
  }
};

const handleLoginFailed = (errorInfo) => {
  console.log('表单验证失败:', errorInfo);
};

// 组件挂载时恢复记住的用户信息
onMounted(() => {
  const rememberedUser = localStorage.getItem('remember_user');
  const rememberedMode = localStorage.getItem('remember_mode');
  
  if (rememberedUser) {
    loginForm.username = rememberedUser;
    loginForm.remember = true;
  }
  
  if (rememberedMode) {
    loginMode.value = rememberedMode;
  }
});
</script>

<style scoped>
/* 全局样式重置 */
.login-page {
  width: 100vw;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  overflow: hidden;
  animation: pageLoad 1.2s ease-out;
}

@keyframes pageLoad {
  0% {
    opacity: 0;
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* 粒子效果 */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: particleFloat 20s linear infinite;
  pointer-events: none;
}

@keyframes particleFloat {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

/* 光晕效果 */
.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(40px);
  opacity: 0.3;
  animation: glowPulse 8s ease-in-out infinite;
}

.glow-1 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.4), transparent);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.glow-2 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.4), transparent);
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.glow-3 {
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2), transparent);
  bottom: 20%;
  left: 30%;
  animation-delay: 4s;
}

@keyframes glowPulse {
  0%, 100% {
    transform: scale(1) rotate(0deg);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.2) rotate(180deg);
    opacity: 0.6;
  }
}

.geometric-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  opacity: 0.1;
  animation: float 20s ease-in-out infinite;
  will-change: transform;
}

.circle-1 {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  bottom: 20%;
  right: 15%;
  animation-delay: 5s;
}

.triangle-1 {
  width: 0;
  height: 0;
  border-left: 60px solid transparent;
  border-right: 60px solid transparent;
  border-bottom: 100px solid rgba(255, 255, 255, 0.1);
  top: 60%;
  left: 5%;
  animation-delay: 10s;
}

.square-1 {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.12);
  transform: rotate(45deg);
  top: 30%;
  right: 10%;
  animation-delay: 15s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg) scale(1);
  }
  25% {
    transform: translateY(-15px) rotate(45deg) scale(1.1);
  }
  50% {
    transform: translateY(-20px) rotate(180deg) scale(0.9);
  }
  75% {
    transform: translateY(-10px) rotate(270deg) scale(1.05);
  }
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
}

/* 主要内容区域 */
.main-content {
  position: relative;
  z-index: 2;
  min-height: 100vh;
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 左侧信息面板 */
.info-panel {
  flex: 1;
  padding: 60px 40px;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  animation: slideInLeft 0.8s ease-out 0.2s both;
  overflow: hidden;
  height: 100%;
}

@keyframes slideInLeft {
  0% {
    opacity: 0;
    transform: translateX(-50px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

.brand-section {
  margin-bottom: 60px;
}

.logo {
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 64px;
  color: white;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
  animation: logoFloat 3s ease-in-out infinite, logoGlow 2s ease-in-out infinite alternate;
  transition: transform 0.3s ease;
}

.logo-icon:hover {
  transform: scale(1.1) rotate(5deg);
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes logoGlow {
  0% {
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
  }
  100% {
    filter: drop-shadow(0 6px 20px rgba(255, 255, 255, 0.3));
  }
}

.brand-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 16px 0;
  background: linear-gradient(135deg, #ffffff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  animation: titleSlideIn 0.8s ease-out 0.4s both;
}

@keyframes titleSlideIn {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-subtitle {
  font-size: 20px;
  opacity: 0.9;
  margin: 0;
  font-weight: 300;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  font-size: 16px;
  opacity: 0.9;
  animation: featureSlideIn 0.6s ease-out both;
  transition: transform 0.3s ease, opacity 0.3s ease;
  padding: 16px 0;
}

.feature-item:nth-child(1) {
  animation-delay: 0.6s;
}

.feature-item:nth-child(2) {
  animation-delay: 0.8s;
}

.feature-item:nth-child(3) {
  animation-delay: 1s;
}

.feature-item:hover {
  transform: translateX(10px);
  opacity: 1;
}

@keyframes featureSlideIn {
  0% {
    opacity: 0;
    transform: translateX(-30px);
  }
  100% {
    opacity: 0.9;
    transform: translateX(0);
  }
}

.feature-icon-wrapper {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-item:hover .feature-icon-wrapper {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.1);
}

.feature-icon {
  font-size: 20px;
  color: #52c41a;
}

.feature-content {
  flex: 1;
}

.feature-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.feature-desc {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
  line-height: 1.5;
}

/* 右侧登录面板 */
.login-panel {
  flex: 0 0 480px;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: slideInRight 0.8s ease-out 0.3s both;
  overflow: hidden;
  height: 100%;
  padding: 20px;
}

@keyframes slideInRight {
  0% {
    opacity: 0;
    transform: translateX(50px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

.login-container {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 
    0 20px 40px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  animation: containerFloat 0.8s ease-out 0.5s both, containerPulse 4s ease-in-out infinite 2s;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.login-container:hover {
  transform: translateY(-5px);
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.3);
}

@keyframes containerFloat {
  0% {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes containerPulse {
  0%, 100% {
    box-shadow: 
      0 20px 40px rgba(0, 0, 0, 0.1),
      0 0 0 1px rgba(255, 255, 255, 0.2);
  }
  50% {
    box-shadow: 
      0 25px 50px rgba(102, 126, 234, 0.15),
      0 0 0 1px rgba(102, 126, 234, 0.3);
  }
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
  font-weight: 400;
}

/* 模式选择器 */
.mode-selector {
  margin-bottom: 32px;
}

.mode-options {
  display: flex;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
}

.mode-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 14px;
  font-weight: 500;
  color: #666;
  position: relative;
  overflow: hidden;
}

.mode-option::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.6s ease;
}

.mode-option:hover::before {
  left: 100%;
}

.mode-option.active {
  background: white;
  color: #667eea;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.mode-option:hover:not(.active) {
  color: #333;
  background: rgba(255, 255, 255, 0.5);
}

.mode-icon {
  font-size: 16px;
}

/* 登录表单 */
.login-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.input-group {
  position: relative;
  display: flex;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.input-group.input-focused {
  transform: scale(1.02);
}

.input-group.input-focused .input-prefix-icon {
  color: #667eea;
  transform: scale(1.1);
}

.input-prefix-icon {
  position: absolute;
  left: 16px;
  color: #999;
  font-size: 16px;
  z-index: 1;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-input {
  padding-left: 48px !important;
  height: 48px;
  border-radius: 12px;
  border: 2px solid #e8e8e8;
  font-size: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.8);
  position: relative;
}

.form-input:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.form-input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 8px 25px rgba(102, 126, 234, 0.15);
  background: white;
  transform: translateY(-3px);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  font-size: 14px;
}

.remember-checkbox {
  color: #666;
}

.forgot-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.forgot-link:hover {
  color: #5a67d8;
}

.form-submit {
  margin-bottom: 0;
}

.login-button {
  width: 100%;
  height: 52px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  animation: buttonPulse 2s ease-in-out infinite 3s;
}

@keyframes buttonPulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.login-button.button-pressed {
  transform: translateY(0px) scale(0.98);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
}

.button-icon {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-button:hover .button-icon {
  transform: scale(1.1) rotate(5deg);
}

.button-text {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-button:hover .button-text {
  letter-spacing: 0.5px;
}

/* 登录底部 */
.login-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.security-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #52c41a;
  font-size: 14px;
  font-weight: 500;
}

.security-icon {
  font-size: 16px;
}

/* 页面底部 */
.page-footer {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .main-content {
    flex-direction: column;
    padding: 20px;
  }
  
  .info-panel {
    flex: none;
    padding: 40px 20px;
    text-align: center;
  }
  
  .brand-title {
    font-size: 36px;
  }
  
  .login-panel {
    flex: none;
    width: 100%;
    max-width: 400px;
  }
}

/* 页面切换动画 */
.page-transition-enter-active,
.page-transition-leave-active {
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-transition-enter-from {
  opacity: 0;
  transform: scale(1.1) translateY(30px);
}

.page-transition-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(-30px);
}

@media (max-width: 768px) {
  .login-page {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }
  
  .login-container {
    flex-direction: column;
    height: 100%;
    overflow: hidden;
    padding: 0;
  }
  
  .info-panel {
    flex: 0 0 auto;
    height: 40%;
    padding: 20px;
    overflow: hidden;
    animation-delay: 0s;
  }
  
  .brand-title {
    font-size: 28px;
    margin-bottom: 8px;
  }
  
  .brand-subtitle {
    font-size: 14px;
    margin-bottom: 20px;
  }
  
  .features-list {
    gap: 8px;
  }
  
  .feature-item {
    padding: 8px 0;
  }
  
  .feature-title {
    font-size: 14px;
  }
  
  .feature-desc {
    font-size: 12px;
  }
  
  .feature-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .login-panel {
    flex: 1;
    height: 60%;
    padding: 20px;
    overflow: hidden;
    animation-delay: 0.1s;
  }
  
  .login-form {
    padding: 24px 20px;
    border-radius: 16px;
  }
  
  .brand-title {
    font-size: 28px;
  }
  
  .login-title {
    font-size: 24px;
  }
  
  .form-input {
    height: 44px;
    font-size: 15px;
  }
  
  .login-button {
    height: 48px;
    font-size: 15px;
  }
  
  .particle {
    display: none;
  }
  
  .glow {
    opacity: 0.1;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 16px;
  }
  
  .info-panel {
    padding: 20px 16px;
  }
  
  .login-container {
    padding: 24px 20px;
  }
  
  .brand-title {
    font-size: 24px;
  }
  
  .features-list {
    gap: 16px;
  }
  
  .feature-item {
    font-size: 16px;
  }
}

/* Ant Design 组件样式覆盖 */
:deep(.ant-form-item) {
  margin-bottom: 0;
}

:deep(.ant-form-item-label) {
  padding: 0;
}

:deep(.ant-input-affix-wrapper) {
  border-radius: 12px;
  border: 2px solid #e8e8e8;
  transition: all 0.3s ease;
}

:deep(.ant-input-affix-wrapper:focus-within) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.ant-input-password) {
  padding-left: 48px;
  height: 48px;
  font-size: 16px;
}

:deep(.ant-checkbox-wrapper) {
  color: #666;
  font-size: 14px;
}

:deep(.ant-checkbox-checked .ant-checkbox-inner) {
  background-color: #667eea;
  border-color: #667eea;
}

:deep(.ant-btn-loading-icon) {
  margin-right: 8px;
}
</style>