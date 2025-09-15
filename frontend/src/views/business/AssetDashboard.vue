<template>
  <div class="dashboard-container">    
    <!-- 统计卡片区域 -->
    <DynamicMetrics 
      v-if="showMetrics"
      :config="metricsConfig" 
      :metrics="metrics"
      @metric-click="handleMetricClick"
      @metrics-loaded="handleMetricsLoaded"
    />
    
    <!-- 主要内容区域 -->
    <div class="main-content" :class="{ 'no-alerts': !showAlerts }">
      <!-- 左侧告警区域 -->
      <div v-if="showAlerts" class="alerts-section">
        <a-card class="alerts-card" :bordered="false">
          <template #title>
            <div class="alerts-header">
              <span class="alerts-title">最新告警</span>
              <div class="alerts-stats">
                <div class="stat-item total">
                  <span class="stat-number">{{ totalAlerts }}</span>
                  <span class="stat-label">总告警</span>
                </div>
                <div class="stat-item unhandled">
                  <span class="stat-number">{{ unhandledAlerts }}</span>
                  <span class="stat-label">未处理</span>
                </div>
              </div>
            </div>
          </template>
          <template #extra>
            <a-button type="link" size="small">查看全部</a-button>
          </template>
          <div class="alerts-list">
            <div 
              v-for="alert in recentAlerts" 
              :key="alert.id"
              class="alert-item"
              :class="[`alert-${alert.level}`, { 'alert-unhandled': !alert.handled }]"
            >
              <div class="alert-indicator"></div>
              <div class="alert-icon">
                <WarningOutlined v-if="alert.level === 'warning'" />
                <ExclamationCircleOutlined v-if="alert.level === 'error'" />
                <InfoCircleOutlined v-if="alert.level === 'info'" />
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-meta">
                  <span class="alert-time">{{ alert.time }}</span>
                  <span class="alert-host">{{ alert.host }}</span>
                  <a-tag v-if="!alert.handled" class="alert-status" color="orange" size="small">未处理</a-tag>
                  <a-tag v-else class="alert-status" color="green" size="small">已处理</a-tag>
                </div>
              </div>
              <div class="alert-actions">
                <a-button v-if="!alert.handled" type="text" size="small" @click="handleAlert(alert.id)">
                  处理
                </a-button>
              </div>
            </div>
            <div v-if="recentAlerts.length === 0" class="empty-alerts">
              <CheckCircleOutlined class="empty-icon" />
              <p>暂无告警信息</p>
            </div>
          </div>
        </a-card>
      </div>
      
      <!-- 右侧监控数据区域 -->
      <div class="monitoring-section">
        <div class="monitoring-header">
          <h3>监控数据</h3>
          <a-button type="text" size="small" @click="showCardManager">
            <SettingOutlined />
          </a-button>
        </div>
        <div class="monitoring-grid">
          <MonitoringCard
            v-for="card in monitoringCards"
            :key="card.id"
            :card="card"
            @refresh="handleRefreshCard"
          />
        </div>
      </div>
    </div>
    
    <!-- 卡片管理弹窗 -->
    <CardManager
      v-model:open="cardManagerVisible"
      v-model="monitoringCards"
      v-model:showAlertCard="showAlerts"
      v-model:showMetricsCard="showMetrics"
      :alert-data="recentAlerts"
      @save="handleSaveCards"
    />
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue';
import DynamicMetrics from '@/components/business/DynamicMetrics.vue';
import {
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  SettingOutlined,
  ReloadOutlined,
  EditOutlined,
  PlusOutlined
} from '@ant-design/icons-vue';
import MonitoringCard from '@/components/business/MonitoringCard.vue';
import CardManager from '@/components/admin/CardManager.vue';

// 动态指标配置
const metricsConfig = ref({
  grid: {
    columns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px'
  },
  animation: {
    enabled: true,
    delay: 0.1
  }
});

// 卡片管理相关
const cardManagerVisible = ref(false);
const showAlerts = ref(true); // 默认显示告警卡片
const showMetrics = ref(true); // 默认显示统计卡片

// 最新告警数据
const recentAlerts = reactive([
  {
    id: 1,
    title: 'CPU使用率过高',
    time: '2分钟前',
    host: 'web-server-01',
    level: 'warning',
    handled: false
  },
  {
    id: 2,
    title: '磁盘空间不足',
    time: '5分钟前',
    host: 'db-server-02',
    level: 'error',
    handled: false
  },
  {
    id: 3,
    title: '内存使用率异常',
    time: '10分钟前',
    host: 'app-server-03',
    level: 'warning',
    handled: true
  },
  {
    id: 4,
    title: '网络连接超时',
    time: '15分钟前',
    host: 'proxy-server-01',
    level: 'error',
    handled: false
  },
  {
    id: 5,
    title: '服务重启完成',
    time: '20分钟前',
    host: 'web-server-02',
    level: 'info',
    handled: true
  },
  {
    id: 2,
    title: '磁盘空间不足',
    time: '5分钟前',
    host: 'db-server-02',
    level: 'error',
    handled: false
  },
  {
    id: 3,
    title: '内存使用率异常',
    time: '10分钟前',
    host: 'app-server-03',
    level: 'warning',
    handled: true
  },
  {
    id: 4,
    title: '网络连接超时',
    time: '15分钟前',
    host: 'proxy-server-01',
    level: 'error',
    handled: false
  },
  {
    id: 5,
    title: '服务重启完成',
    time: '20分钟前',
    host: 'web-server-02',
    level: 'info',
    handled: true
  },
  {
    id: 2,
    title: '磁盘空间不足',
    time: '5分钟前',
    host: 'db-server-02',
    level: 'error',
    handled: false
  },
  {
    id: 3,
    title: '内存使用率异常',
    time: '10分钟前',
    host: 'app-server-03',
    level: 'warning',
    handled: true
  },
  {
    id: 4,
    title: '网络连接超时',
    time: '15分钟前',
    host: 'proxy-server-01',
    level: 'error',
    handled: false
  },
  {
    id: 5,
    title: '服务重启完成',
    time: '20分钟前',
    host: 'web-server-02',
    level: 'info',
    handled: true
  },
  {
    id: 2,
    title: '磁盘空间不足',
    time: '5分钟前',
    host: 'db-server-02',
    level: 'error',
    handled: false
  },
  {
    id: 3,
    title: '内存使用率异常',
    time: '10分钟前',
    host: 'app-server-03',
    level: 'warning',
    handled: true
  },
  {
    id: 4,
    title: '网络连接超时',
    time: '15分钟前',
    host: 'proxy-server-01',
    level: 'error',
    handled: false
  },
  {
    id: 5,
    title: '服务重启完成',
    time: '20分钟前',
    host: 'web-server-02',
    level: 'info',
    handled: true
  }
]);

// 计算告警统计
const totalAlerts = computed(() => recentAlerts.length);
const unhandledAlerts = computed(() => recentAlerts.filter(alert => !alert.handled).length);

// 监控卡片配置
const monitoringCards = reactive([
  {
    id: 'cpu-top5',
    title: 'CPU使用率 TOP5',
    type: 'chart',
    chartType: 'bar',
    data: [
      { name: 'web-server-01', value: 85.2 },
      { name: 'db-server-02', value: 78.5 },
      { name: 'app-server-03', value: 72.8 },
      { name: 'proxy-server-01', value: 68.3 },
      { name: 'cache-server-01', value: 65.7 }
    ],
    unit: '%',
    color: '#ff7875'
  },
  {
    id: 'memory-top5',
    title: '内存使用率 TOP5',
    type: 'chart',
    chartType: 'bar',
    data: [
      { name: 'db-server-02', value: 92.1 },
      { name: 'app-server-03', value: 86.4 },
      { name: 'web-server-01', value: 79.8 },
      { name: 'cache-server-01', value: 74.2 },
      { name: 'proxy-server-01', value: 68.9 }
    ],
    unit: '%',
    color: '#5cdbd3'
  },
  {
    id: 'disk-top5',
    title: '磁盘使用率 TOP5',
    type: 'chart',
    chartType: 'bar',
    data: [
      { name: 'log-server-01', value: 95.3 },
      { name: 'db-server-02', value: 88.7 },
      { name: 'backup-server-01', value: 82.1 },
      { name: 'web-server-01', value: 76.5 },
      { name: 'app-server-03', value: 71.2 }
    ],
    unit: '%',
    color: '#ffc53d'
  },
  {
    id: 'network-top5',
    title: '网络流量 TOP5',
    type: 'chart',
    chartType: 'line',
    data: [
      { name: 'proxy-server-01', value: 156.8 },
      { name: 'web-server-01', value: 124.3 },
      { name: 'db-server-02', value: 98.7 },
      { name: 'app-server-03', value: 87.2 },
      { name: 'cache-server-01', value: 76.5 }
    ],
    unit: 'MB/s',
    color: '#40a9ff'
  }
]);

// 指标数据
const metrics = reactive([
  {
    id: 'total-assets',
    label: '总资产数量',
    value: 128,
    change: '+5%',
    trend: 'up',
    icon: 'DatabaseOutlined',
    iconColor: '#1890ff',
    iconBgColor: 'linear-gradient(135deg, #e6f7ff, #bae7ff)'
  },
  {
    id: 'servers',
    label: '服务器数量',
    value: 64,
    change: '+2%',
    trend: 'up',
    icon: 'CloudServerOutlined',
    iconColor: '#52c41a',
    iconBgColor: 'linear-gradient(135deg, #f6ffed, #d9f7be)'
  },
  {
    id: 'network-devices',
    label: '网络设备',
    value: 32,
    change: '-1%',
    trend: 'down',
    icon: 'GlobalOutlined',
    iconColor: '#fa8c16',
    iconBgColor: 'linear-gradient(135deg, #fff7e6, #ffd591)'
  },
  {
    id: 'online-rate',
    label: '在线率',
    value: '98.7%',
    change: '+0.5%',
    trend: 'up',
    icon: 'CheckCircleOutlined',
    iconColor: '#13c2c2',
    iconBgColor: 'linear-gradient(135deg, #e6fffb, #b5f5ec)'
  },
  {
    id: 'warning-alerts',
    label: '告警数量',
    value: 3,
    change: '-2',
    trend: 'down',
    icon: 'WarningOutlined',
    iconColor: '#faad14',
    iconBgColor: 'linear-gradient(135deg, #fffbe6, #fff1b8)'
  },
  {
    id: 'monthly-growth',
    label: '月增长率',
    value: '12.3%',
    change: '+1.2%',
    trend: 'up',
    icon: 'RiseOutlined',
    iconColor: '#722ed1',
    iconBgColor: 'linear-gradient(135deg, #f9f0ff, #efdbff)'
  }
]);

// 处理指标点击事件
const handleMetricClick = (metric) => {
  console.log('点击了指标:', metric);
  // 可以在这里处理指标点击逻辑，比如跳转到详细页面
};

// 处理指标数据加载完成事件
const handleMetricsLoaded = (data) => {
  console.log('指标数据加载完成:', data);
  // 可以在这里处理数据加载完成后的逻辑
};

// 显示卡片管理弹窗
const showCardManager = () => {
  cardManagerVisible.value = true;
};

// 保存卡片配置
const handleSaveCards = (data) => {
  if (data.cards) {
    // 更新本地存储
    localStorage.setItem('monitoringCards', JSON.stringify(data.cards));
  }
  if (data.showAlert !== undefined) {
    localStorage.setItem('showAlerts', JSON.stringify(data.showAlert));
  }
  if (data.showMetrics !== undefined) {
    localStorage.setItem('showMetrics', JSON.stringify(data.showMetrics));
  }
};

// 处理告警
const handleAlert = (alertId) => {
  const alert = recentAlerts.find(a => a.id === alertId);
  if (alert) {
    alert.handled = true;
  }
};

// 处理卡片刷新
const handleRefreshCard = (cardId) => {
  console.log('刷新卡片:', cardId);
  // 重新获取卡片数据
};

// 动态添加指标的方法
const addMetric = (newMetric) => {
  metrics.push(newMetric);
};

// 动态更新指标的方法
const updateMetric = (metricId, newData) => {
  const index = metrics.findIndex(m => m.id === metricId);
  if (index !== -1) {
    Object.assign(metrics[index], newData);
  }
};

// 暴露方法供外部调用
defineExpose({
  addMetric,
  updateMetric
});
</script>

<style scoped>
.dashboard-container {
  padding: 0;
  animation: fadeIn 0.6s ease-out;
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 20px;
  margin-top: 24px;
}

.main-content.no-alerts {
  grid-template-columns: 1fr;
}
.alerts-section {
  display: flex;
  flex-direction: column;
}

.alerts-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(24, 144, 255, 0.06);
  border: 1px solid rgba(24, 144, 255, 0.04);
  overflow: hidden;
  height: 100%;
}

:deep(.alerts-card .ant-card-head) {
  background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
  border-bottom: 1px solid rgba(24, 144, 255, 0.08);
  padding: 12px 16px;
  min-height: auto;
}

:deep(.alerts-card .ant-card-head-title) {
  width: 100%;
}

.alerts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.alerts-title {
  color: #434343;
  font-weight: 600;
  font-size: 16px;
}

.alerts-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  min-width: 50px;
}

.stat-item.total {
  border: 1px solid rgba(24, 144, 255, 0.2);
}

.stat-item.unhandled {
  border: 1px solid rgba(250, 173, 20, 0.3);
  background: rgba(250, 173, 20, 0.05);
}

.stat-number {
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
  color: #262626;
}

.stat-item.unhandled .stat-number {
  color: #faad14;
}

.stat-label {
  font-size: 11px;
  color: #8c8c8c;
  line-height: 1;
  margin-top: 2px;
}

:deep(.alerts-card .ant-card-body) {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  padding: 12px;
  height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
}

.alerts-list {
  height: calc(100% - 20px);
  overflow-y: auto;
  padding-right: 4px;
  margin-right: -4px;
}

/* 优化滚动条样式 */
.alerts-list::-webkit-scrollbar {
  width: 6px;
}

.alerts-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 3px;
}

.alerts-list::-webkit-scrollbar-thumb {
  background: rgba(24, 144, 255, 0.3);
  border-radius: 3px;
  transition: background 0.3s ease;
}

.alerts-list::-webkit-scrollbar-thumb:hover {
  background: rgba(24, 144, 255, 0.5);
}

/* Firefox 滚动条样式 */
.alerts-list {
  scrollbar-width: thin;
  scrollbar-color: rgba(24, 144, 255, 0.3) rgba(0, 0, 0, 0.04);
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  margin-bottom: 6px;
  position: relative;
  background: rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.alert-item:hover {
  background: rgba(24, 144, 255, 0.04);
  border-color: rgba(24, 144, 255, 0.1);
}

.alert-indicator {
  width: 3px;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  border-radius: 0 3px 3px 0;
}

.alert-item.alert-warning .alert-indicator {
  background: #faad14;
}

.alert-item.alert-error .alert-indicator {
  background: #ff4d4f;
}

.alert-item.alert-info .alert-indicator {
  background: #1890ff;
}

.alert-item.alert-unhandled {
  border-left: 2px solid #faad14;
  background: linear-gradient(90deg, rgba(250, 173, 20, 0.03) 0%, rgba(255, 255, 255, 0.6) 20%);
}

.alert-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-icon .anticon {
  font-size: 14px;
}

.alert-warning .alert-icon .anticon {
  color: #faad14;
}

.alert-error .alert-icon .anticon {
  color: #ff4d4f;
}

.alert-info .alert-icon .anticon {
  color: #1890ff;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: 13px;
  font-weight: 500;
  color: #262626;
  margin-bottom: 3px;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alert-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.alert-time {
  font-size: 11px;
  color: #8c8c8c;
}

.alert-host {
  font-size: 11px;
  color: #595959;
  background: rgba(0, 0, 0, 0.05);
  padding: 1px 4px;
  border-radius: 3px;
  white-space: nowrap;
}

.alert-status {
  margin: 0;
}

:deep(.alert-status.ant-tag) {
  font-size: 10px;
  padding: 0 4px;
  height: 16px;
  line-height: 14px;
  border-radius: 8px;
  margin: 0;
}

.alert-actions {
  flex-shrink: 0;
}

.alert-actions .ant-btn {
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
  border-radius: 4px;
}

.empty-alerts {
  text-align: center;
  padding: 40px 20px;
  color: #bfbfbf;
}

.empty-icon {
  font-size: 48px;
  color: #52c41a;
  margin-bottom: 16px;
  display: block;
}

.empty-alerts p {
  font-size: 14px;
  margin: 0;
}

/* 监控区域 */
.monitoring-section {
  display: flex;
  flex-direction: column;
}

.monitoring-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.monitoring-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #434343;
}

.monitoring-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 16px;
  height: 100%;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 350px 1fr;
    gap: 16px;
  }
  
  .monitoring-grid {
    gap: 12px;
  }
  
  .alerts-stats {
    gap: 12px;
  }
  
  .stat-item {
    min-width: 45px;
  }
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .alerts-section {
    order: 2;
  }
  
  .monitoring-section {
    order: 1;
  }
  
  .monitoring-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(4, auto);
    gap: 12px;
  }
  
  :deep(.alerts-card .ant-card-body) {
    height: calc(100vh - 200px);
  }
  
  .alerts-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .alerts-stats {
    align-self: flex-end;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .main-content {
    gap: 12px;
  }
  
  .monitoring-grid {
    gap: 8px;
  }
  
  .alert-item {
    padding: 6px 8px;
    margin-bottom: 4px;
    gap: 8px;
  }
  
  .alert-title {
    font-size: 12px;
  }
  
  .alert-time,
  .alert-host {
    font-size: 10px;
  }
  
  .alerts-stats {
    gap: 6px;
  }
  
  .stat-item {
    min-width: 40px;
    padding: 3px 6px;
  }
  
  .stat-number {
    font-size: 16px;
  }
  
  .stat-label {
    font-size: 10px;
  }
  
  .alert-actions .ant-btn {
    height: 18px;
    padding: 0 4px;
    font-size: 10px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>