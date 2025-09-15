<template>
  <div class="admin-settings admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <SettingOutlined />
          系统设置
        </h1>
        <p class="page-description">管理监控系统的配置参数</p>
      </div>
      <div class="header-actions">
        <a-button type="primary" @click="saveAllSettings">
          <SaveOutlined />
          保存设置
        </a-button>
      </div>
    </div>

    <!-- 设置分类导航 -->
    <div class="settings-layout admin-layout">
      <!-- 左侧菜单 -->
      <div class="settings-menu admin-menu">
        <div class="menu-title">配置分类</div>
        <div class="menu-list">
          <div 
            v-for="category in categoryList" 
            :key="category.key"
            :class="['menu-item', { 'active': activeCategory === category.key }]"
            @click="handleCategoryChange(category.key)"
          >
            <component :is="category.icon" class="menu-icon" />
            <span class="menu-text">{{ category.name }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="settings-content admin-content">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>

        <!-- 基础配置 -->
        <div v-if="activeCategory === 'basic'" class="setting-section content-section">
          <a-form layout="vertical" :model="basicSettings">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="系统名称">
                  <a-input v-model:value="basicSettings.systemName" placeholder="运维监控系统" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="系统版本">
                  <a-input v-model:value="basicSettings.systemVersion" placeholder="v1.0.0" />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="公司名称">
                  <a-input v-model:value="basicSettings.companyName" placeholder="您的公司名称" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="联系邮箱">
                  <a-input v-model:value="basicSettings.contactEmail" placeholder="admin@company.com" />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="系统描述">
              <a-textarea 
                v-model:value="basicSettings.description" 
                placeholder="系统功能描述"
                :rows="3"
              />
            </a-form-item>
          </a-form>
        </div>

        <!-- 监控配置 -->
        <div v-if="activeCategory === 'monitor'" class="setting-section content-section">
          <a-form layout="vertical" :model="monitorSettings">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="数据采集间隔（秒）">
                  <a-input-number 
                    v-model:value="monitorSettings.collectInterval" 
                    :min="10" 
                    :max="300"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="数据保留天数">
                  <a-input-number 
                    v-model:value="monitorSettings.retentionDays" 
                    :min="1" 
                    :max="365"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="启用自动发现">
              <a-switch v-model:checked="monitorSettings.autoDiscovery" />
              <span class="switch-description">自动发现网络中的新设备</span>
            </a-form-item>
          </a-form>
        </div>

        <!-- 告警配置 -->
        <div v-if="activeCategory === 'alert'" class="setting-section content-section">
          <a-form layout="vertical" :model="alertSettings">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="CPU告警阈值（%）">
                  <a-input-number 
                    v-model:value="alertSettings.cpuThreshold" 
                    :min="1" 
                    :max="100"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="内存告警阈值（%）">
                  <a-input-number 
                    v-model:value="alertSettings.memoryThreshold" 
                    :min="1" 
                    :max="100"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="邮件通知">
              <a-switch v-model:checked="alertSettings.emailNotification" />
              <span class="switch-description">发送告警邮件通知</span>
            </a-form-item>
          </a-form>
        </div>

        <!-- 存储配置 -->
        <div v-if="activeCategory === 'storage'" class="setting-section content-section">
          <a-form layout="vertical" :model="storageSettings">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="数据库类型">
                  <a-select v-model:value="storageSettings.dbType">
                    <a-select-option value="mysql">MySQL</a-select-option>
                    <a-select-option value="postgresql">PostgreSQL</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="数据库主机">
                  <a-input v-model:value="storageSettings.dbHost" placeholder="127.0.0.1" />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="启用数据压缩">
              <a-switch v-model:checked="storageSettings.compression" />
              <span class="switch-description">压缩历史数据以节省存储空间</span>
            </a-form-item>
          </a-form>
        </div>

        <!-- 安全配置 -->
        <div v-if="activeCategory === 'security'" class="setting-section content-section">
          <a-form layout="vertical" :model="securitySettings">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="会话超时（分钟）">
                  <a-input-number 
                    v-model:value="securitySettings.sessionTimeout" 
                    :min="5" 
                    :max="1440"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="密码最小长度">
                  <a-input-number 
                    v-model:value="securitySettings.minPasswordLength" 
                    :min="6" 
                    :max="32"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="启用两步验证">
              <a-switch v-model:checked="securitySettings.twoFactorAuth" />
              <span class="switch-description">提高账户安全性</span>
            </a-form-item>
          </a-form>
        </div>

        <!-- 备份配置 -->
        <div v-if="activeCategory === 'backup'" class="setting-section">
          <a-form layout="vertical" :model="backupSettings">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="备份频率">
                  <a-select v-model:value="backupSettings.frequency">
                    <a-select-option value="daily">每日</a-select-option>
                    <a-select-option value="weekly">每周</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="保留备份数量">
                  <a-input-number 
                    v-model:value="backupSettings.retentionCount" 
                    :min="1" 
                    :max="30"
                    style="width: 100%"
                  />
                </a-form-item>
              </a-col>
            </a-row>
            <a-form-item label="启用自动备份">
              <a-switch v-model:checked="backupSettings.autoBackup" />
              <span class="switch-description">按照设定频率自动备份</span>
            </a-form-item>
          </a-form>
        </div>
      </a-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  SettingOutlined,
  SaveOutlined,
  DesktopOutlined,
  MonitorOutlined,
  BellOutlined,
  DatabaseOutlined,
  SafetyOutlined,
  CloudDownloadOutlined
} from '@ant-design/icons-vue';

// 响应式数据
const activeCategory = ref('basic');

// 分类列表
const categoryList = [
  { key: 'basic', name: '基础配置', icon: DesktopOutlined },
  { key: 'monitor', name: '监控配置', icon: MonitorOutlined },
  { key: 'alert', name: '告警配置', icon: BellOutlined },
  { key: 'storage', name: '存储配置', icon: DatabaseOutlined },
  { key: 'security', name: '安全配置', icon: SafetyOutlined },
  { key: 'backup', name: '备份配置', icon: CloudDownloadOutlined }
];

// 基础配置
const basicSettings = ref({
  systemName: '运维监控系统',
  systemVersion: 'v1.0.0',
  companyName: '',
  contactEmail: '',
  description: '企业级运维监控系统'
});

// 监控配置
const monitorSettings = ref({
  collectInterval: 30,
  retentionDays: 90,
  autoDiscovery: true
});

// 告警配置
const alertSettings = ref({
  cpuThreshold: 85,
  memoryThreshold: 90,
  emailNotification: true
});

// 存储配置
const storageSettings = ref({
  dbType: 'mysql',
  dbHost: '127.0.0.1',
  compression: true
});

// 安全配置
const securitySettings = ref({
  sessionTimeout: 60,
  minPasswordLength: 8,
  twoFactorAuth: false
});

// 备份配置
const backupSettings = ref({
  frequency: 'daily',
  retentionCount: 7,
  autoBackup: true
});

// 方法
const getCurrentCategoryName = () => {
  const categoryNames = {
    'basic': '基础配置',
    'monitor': '监控配置',
    'alert': '告警配置',
    'storage': '存储配置',
    'security': '安全配置',
    'backup': '备份配置'
  };
  return categoryNames[activeCategory.value] || '未知分类';
};

const handleCategoryChange = (key) => {
  activeCategory.value = key;
};

const saveAllSettings = async () => {
  try {
    const allSettings = {
      basic: basicSettings.value,
      monitor: monitorSettings.value,
      alert: alertSettings.value,
      storage: storageSettings.value,
      security: securitySettings.value,
      backup: backupSettings.value
    };
    
    localStorage.setItem('systemSettings', JSON.stringify(allSettings));
    message.success('设置保存成功');
  } catch (error) {
    message.error('设置保存失败: ' + error.message);
  }
};

// 生命周期
onMounted(() => {
  const savedSettings = localStorage.getItem('systemSettings');
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings);
      if (settings.basic) Object.assign(basicSettings.value, settings.basic);
      if (settings.monitor) Object.assign(monitorSettings.value, settings.monitor);
      if (settings.alert) Object.assign(alertSettings.value, settings.alert);
      if (settings.storage) Object.assign(storageSettings.value, settings.storage);
      if (settings.security) Object.assign(securitySettings.value, settings.security);
      if (settings.backup) Object.assign(backupSettings.value, settings.backup);
    } catch (error) {
      console.error('加载配置失败:', error);
    }
  }
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 系统设置页面特有的样式 */
/* 所有通用样式已在 admin-common.css 中定义 */
</style>