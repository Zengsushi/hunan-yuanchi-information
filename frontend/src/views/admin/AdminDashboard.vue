<template>
  <div class="admin-dashboard">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-bg">
        <div class="bg-decoration"></div>
        <div class="bg-particles"></div>
      </div>
      <div class="welcome-content">
        <h1 class="welcome-title">
          <CrownOutlined class="crown-icon" />
          欢迎回来，{{ currentUserName }}
        </h1>
        <p class="welcome-text">今天是 {{ currentDate }}，祝您工作愉快！</p>
        <div class="welcome-features">
          <div class="feature-item">
            <ShieldCheckOutlined class="feature-icon" />
            <span>安全管理</span>
          </div>
          <div class="feature-item">
            <ControlOutlined class="feature-icon" />
            <span>全局控制</span>
          </div>
          <div class="feature-item">
            <RocketOutlined class="feature-icon" />
            <span>高效运维</span>
          </div>
        </div>
      </div>
      <div class="welcome-stats">
        <div class="quick-stat">
          <div class="stat-icon">
            <UserOutlined />
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ systemStats.onlineUsers }}</div>
            <div class="stat-label">在线用户</div>
          </div>
        </div>
        <div class="quick-stat">
          <div class="stat-icon">
            <DatabaseOutlined />
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ systemStats.totalAssets }}</div>
            <div class="stat-label">资产总数</div>
          </div>
        </div>
        <div class="quick-stat">
          <div class="stat-icon">
            <BellOutlined />
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ systemStats.alerts }}</div>
            <div class="stat-label">待处理告警</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <a-card class="stat-card gradient-blue">
        <div class="stat-header">
          <TeamOutlined class="stat-icon-large" />
          <div class="stat-title">系统用户</div>
        </div>
        <div class="stat-value">{{ dashboardData.totalUsers }}</div>
        <div class="stat-trend">
          <ArrowUpOutlined class="trend-up" />
          <span>较昨日 +12%</span>
        </div>
      </a-card>

      <a-card class="stat-card gradient-green">
        <div class="stat-header">
          <UserOutlined class="stat-icon-large" />
          <div class="stat-title">活跃会话</div>
        </div>
        <div class="stat-value">{{ dashboardData.activeSessions }}</div>
        <div class="stat-trend">
          <ArrowUpOutlined class="trend-up" />
          <span>较昨日 +8%</span>
        </div>
      </a-card>

      <a-card class="stat-card gradient-orange">
        <div class="stat-header">
          <BellOutlined class="stat-icon-large" />
          <div class="stat-title">系统告警</div>
        </div>
        <div class="stat-value">{{ dashboardData.systemAlerts }}</div>
        <div class="stat-trend">
          <ArrowDownOutlined class="trend-down" />
          <span>较昨日 -3%</span>
        </div>
      </a-card>

      <a-card class="stat-card gradient-purple">
        <div class="stat-header">
          <CloudServerOutlined class="stat-icon-large" />
          <div class="stat-title">存储使用</div>
        </div>
        <div class="stat-value">{{ dashboardData.storageUsed }}GB</div>
        <div class="stat-trend">
          <ArrowUpOutlined class="trend-up" />
          <span>较昨日 +2GB</span>
        </div>
      </a-card>
    </div>

    <!-- 主要内容区 -->
    <div class="main-grid">
      <!-- 系统监控 -->
      <a-card title="系统性能监控" class="monitor-card modern-card">
        <template #title>
          <div class="card-title">
            <MonitorOutlined class="title-icon" />
            <span>系统性能监控</span>
          </div>
        </template>
        <template #extra>
          <a-button type="primary" size="small" ghost>查看详情</a-button>
        </template>
        <div class="monitor-content">
          <div class="monitor-item">
            <div class="monitor-label">CPU 使用率</div>
            <a-progress :percent="systemMonitor.cpu" :stroke-color="getProgressColor(systemMonitor.cpu)" />
          </div>
          <div class="monitor-item">
            <div class="monitor-label">内存使用率</div>
            <a-progress :percent="systemMonitor.memory" :stroke-color="getProgressColor(systemMonitor.memory)" />
          </div>
          <div class="monitor-item">
            <div class="monitor-label">磁盘使用率</div>
            <a-progress :percent="systemMonitor.disk" :stroke-color="getProgressColor(systemMonitor.disk)" />
          </div>
          <div class="monitor-item">
            <div class="monitor-label">网络流量</div>
            <a-progress :percent="systemMonitor.network" :stroke-color="getProgressColor(systemMonitor.network)" />
          </div>
        </div>
      </a-card>

      <!-- 最近活动 -->
      <a-card title="最近活动" class="activity-card modern-card">
        <template #title>
          <div class="card-title">
            <HistoryOutlined class="title-icon" />
            <span>最近活动</span>
          </div>
        </template>
        <template #extra>
          <a-button type="primary" size="small" ghost>查看全部</a-button>
        </template>
        <a-timeline class="activity-timeline">
          <a-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :color="activity.type === 'success' ? 'green' : activity.type === 'warning' ? 'orange' : 'red'"
          >
            <div class="activity-item">
              <div class="activity-content">
                <span class="activity-text">{{ activity.text }}</span>
                <span class="activity-user">by {{ activity.user }}</span>
              </div>
              <div class="activity-time">{{ activity.time }}</div>
            </div>
          </a-timeline-item>
        </a-timeline>
      </a-card>

      <!-- 快速操作 -->
      <a-card title="快速操作" class="actions-card modern-card">
        <template #title>
          <div class="card-title">
            <ThunderboltOutlined class="title-icon" />
            <span>快速操作</span>
          </div>
        </template>
        <div class="quick-actions">
          <a-button type="primary" size="large" class="action-btn primary-action" @click="goToUsers">
            <TeamOutlined />
            用户管理
          </a-button>
          <a-button size="large" class="action-btn secondary-action" @click="goToSettings">
            <SettingOutlined />
            系统设置
          </a-button>
          <a-button size="large" class="action-btn secondary-action" @click="goToLogs">
            <FileTextOutlined />
            查看日志
          </a-button>
          <a-button size="large" class="action-btn secondary-action" @click="goToBackup">
            <CloudDownloadOutlined />
            数据备份
          </a-button>
        </div>
      </a-card>

      <!-- 系统信息 -->
      <a-card title="系统信息" class="system-info-card modern-card">
        <template #title>
          <div class="card-title">
            <InfoCircleOutlined class="title-icon" />
            <span>系统信息</span>
          </div>
        </template>
        <div class="system-info">
          <div class="info-item">
            <span class="info-label">系统版本</span>
            <span class="info-value">v1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">运行时间</span>
            <span class="info-value">{{ systemInfo.uptime }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">数据库版本</span>
            <span class="info-value">MySQL 8.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">服务器IP</span>
            <span class="info-value">192.168.1.100</span>
          </div>
          <div class="info-item">
            <span class="info-label">最后备份</span>
            <span class="info-value">{{ systemInfo.lastBackup }}</span>
          </div>
        </div>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import {
  CrownOutlined,
  TeamOutlined,
  UserOutlined,
  BellOutlined,
  CloudServerOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  SettingOutlined,
  FileTextOutlined,
  CloudDownloadOutlined,
  DatabaseOutlined,
  ShieldCheckOutlined,
  ControlOutlined,
  RocketOutlined,
  MonitorOutlined,
  HistoryOutlined,
  ThunderboltOutlined,
  InfoCircleOutlined
} from '@ant-design/icons-vue';

const router = useRouter();

// 响应式数据
const currentUserName = ref(localStorage.getItem('username') || '管理员');
const currentDate = ref(new Date().toLocaleDateString('zh-CN', { 
  weekday: 'long', 
  year: 'numeric', 
  month: 'long', 
  day: 'numeric' 
}));

const systemStats = ref({
  onlineUsers: 12,
  totalAssets: 248,
  alerts: 3
});

const dashboardData = ref({
  totalUsers: 128,
  activeSessions: 45,
  systemAlerts: 8,
  storageUsed: 67.2
});

const systemMonitor = ref({
  cpu: 45,
  memory: 62,
  disk: 78,
  network: 34
});

const systemInfo = ref({
  uptime: '15天 8小时 23分钟',
  lastBackup: '2024-01-20 02:30:00'
});

const recentActivities = ref([
  {
    id: 1,
    text: '新用户注册',
    user: 'user123',
    time: '2分钟前',
    type: 'success'
  },
  {
    id: 2,
    text: '系统设置更新',
    user: 'admin',
    time: '10分钟前',
    type: 'info'
  },
  {
    id: 3,
    text: '数据备份完成',
    user: 'system',
    time: '1小时前',
    type: 'success'
  },
  {
    id: 4,
    text: '磁盘使用率告警',
    user: 'monitor',
    time: '2小时前',
    type: 'warning'
  },
  {
    id: 5,
    text: '用户权限修改',
    user: 'admin',
    time: '3小时前',
    type: 'info'
  }
]);

// 计算属性
const getProgressColor = (percent) => {
  if (percent >= 80) return '#ff4d4f';
  if (percent >= 60) return '#faad14';
  return '#52c41a';
};

// 方法
const goToUsers = () => {
  router.push('/admin/users');
};

const goToSettings = () => {
  router.push('/admin/settings');
};

const goToLogs = () => {
  router.push('/admin/logs');
};

const goToBackup = () => {
  router.push('/admin/backup');
};

// 模拟实时数据更新
onMounted(() => {
  const timer = setInterval(() => {
    // 更新系统监控数据
    systemMonitor.value.cpu = Math.floor(Math.random() * 30) + 30;
    systemMonitor.value.memory = Math.floor(Math.random() * 40) + 40;
    systemMonitor.value.network = Math.floor(Math.random() * 50) + 20;
    
    // 更新在线用户数
    systemStats.value.onlineUsers = Math.floor(Math.random() * 10) + 8;
  }, 5000);
  
  // 清理定时器
  return () => {
    clearInterval(timer);
  };
});
</script>

<style scoped>
.admin-dashboard {
  padding: 0;
  animation: fadeInUp 0.6s ease-out;
}

/* 欢迎区域美化 */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  border-radius: 16px;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.welcome-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  top: -50%;
  right: -20%;
  width: 400px;
  height: 400px;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border-radius: 50%;
  animation: float 6s ease-in-out infinite;
}

.bg-particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(2px 2px at 20% 30%, rgba(255, 255, 255, 0.3), transparent),
    radial-gradient(2px 2px at 40% 70%, rgba(255, 255, 255, 0.2), transparent),
    radial-gradient(1px 1px at 60% 20%, rgba(255, 255, 255, 0.4), transparent),
    radial-gradient(1px 1px at 80% 80%, rgba(255, 255, 255, 0.2), transparent);
  background-repeat: no-repeat;
  background-size: 300px 300px;
  animation: twinkle 4s linear infinite;
}

.welcome-content {
  flex: 1;
  z-index: 2;
  position: relative;
}

.welcome-title {
  margin: 0 0 16px 0;
  font-size: 32px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 16px;
}

.crown-icon {
  color: #ffd700;
  font-size: 36px;
  filter: drop-shadow(0 0 10px rgba(255, 215, 0, 0.5));
  animation: glow 2s ease-in-out infinite alternate;
}

.welcome-text {
  margin: 0 0 24px 0;
  font-size: 18px;
  opacity: 0.9;
  line-height: 1.6;
}

.welcome-features {
  display: flex;
  gap: 32px;
  margin-top: 24px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 25px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 18px;
  color: #fff;
}

.welcome-stats {
  display: flex;
  gap: 24px;
  z-index: 2;
  position: relative;
}

.quick-stat {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  min-width: 140px;
  transition: all 0.3s ease;
}

.quick-stat:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-4px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
  color: #fff;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 4px;
  color: #fff;
}

/* 统计卡片美化 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  border-radius: 16px;
  border: none;
  overflow: hidden;
  position: relative;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.stat-card.gradient-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card.gradient-green {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-card.gradient-orange {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-card.gradient-purple {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-icon-large {
  font-size: 24px;
  opacity: 0.9;
}

.stat-title {
  font-size: 16px;
  font-weight: 600;
  opacity: 0.9;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  opacity: 0.8;
}

.trend-up {
  color: rgba(255, 255, 255, 0.9);
}

.trend-down {
  color: rgba(255, 255, 255, 0.9);
}

/* 主要内容区美化 */
.main-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.modern-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.modern-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.title-icon {
  color: #1890ff;
  font-size: 18px;
}

/* 快速操作美化 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-btn {
  height: 56px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.primary-action {
  background: linear-gradient(135deg, #1890ff, #40a9ff);
  border: none;
}

.primary-action:hover {
  background: linear-gradient(135deg, #40a9ff, #1890ff);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(24, 144, 255, 0.3);
}

.secondary-action {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  color: #495057;
}

.secondary-action:hover {
  background: #e9ecef;
  border-color: #1890ff;
  color: #1890ff;
  transform: translateY(-2px);
}

/* 监控卡片 */
.monitor-card {
  grid-column: span 2;
}

.monitor-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.monitor-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.monitor-label {
  font-weight: 500;
  color: #666;
  font-size: 14px;
}

/* 活动卡片 */
.activity-timeline {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.activity-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.activity-text {
  font-size: 14px;
  color: #333;
}

.activity-user {
  font-size: 12px;
  color: #666;
}

.activity-time {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

/* 系统信息 */
.system-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  color: #666;
  font-size: 14px;
}

.info-value {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes twinkle {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
  }
  to {
    text-shadow: 0 0 20px rgba(255, 215, 0, 0.8), 0 0 30px rgba(255, 215, 0, 0.6);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .welcome-section {
    flex-direction: column;
    gap: 24px;
    text-align: center;
  }
  
  .welcome-features {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .welcome-stats {
    justify-content: center;
  }
  
  .monitor-card {
    grid-column: span 1;
  }
  
  .monitor-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .welcome-section {
    padding: 24px;
    margin-bottom: 24px;
  }
  
  .welcome-title {
    font-size: 24px;
  }
  
  .welcome-text {
    font-size: 16px;
  }
  
  .welcome-features {
    gap: 16px;
  }
  
  .welcome-stats {
    flex-direction: column;
    width: 100%;
  }
  
  .quick-stat {
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .main-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
}
</style>