<template>
  <div class="admin-logs admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <FileTextOutlined />
          操作日志
        </h1>
        <p class="page-description">查看和管理系统操作日志记录</p>
      </div>
      <div class="header-actions">
        <a-button type="primary" @click="exportLogs">
          <DownloadOutlined />
          导出日志
        </a-button>
      </div>
    </div>

    <!-- 日志分类导航 -->
    <div class="logs-layout admin-layout">
      <!-- 左侧菜单 -->
      <div class="logs-menu admin-menu">
        <div class="menu-title">日志分类</div>
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
        
        <!-- 日志统计 -->
        <div class="menu-stats">
          <div class="stats-title">日志统计</div>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">今日日志</span>
              <span class="stat-value">{{ getTodayLogsCount() }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">错误日志</span>
              <span class="stat-value">{{ getErrorLogsCount() }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总日志数</span>
              <span class="stat-value">{{ allLogs.length }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="logs-content admin-content">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
            <a-space>
              <a-input-search
                v-model:value="searchText"
                placeholder="搜索日志内容..."
                style="width: 200px"
                @search="handleSearch"
              />
              <a-select
                v-model:value="dateRange"
                placeholder="选择时间范围"
                style="width: 120px"
                @change="handleDateRangeChange"
              >
                <a-select-option value="today">今天</a-select-option>
                <a-select-option value="week">本周</a-select-option>
                <a-select-option value="month">本月</a-select-option>
                <a-select-option value="all">全部</a-select-option>
              </a-select>
              <a-button @click="refreshData">
                <ReloadOutlined />
              </a-button>
            </a-space>
          </template>

          <a-table
            :columns="tableColumns"
            :data-source="filteredLogs"
            :pagination="pagination"
            :loading="loading"
            row-key="id"
            size="middle"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'level'">
                <a-tag :color="getLevelColor(record.level)">
                  {{ getLevelText(record.level) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'module'">
                <a-tag color="blue">
                  {{ record.module }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-space>
                  <a-button type="link" size="small" @click="viewLogDetail(record)">
                    查看详情
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>
    </div>

    <!-- 日志详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="日志详情"
      width="800px"
      :footer="null"
    >
      <a-descriptions
        v-if="selectedLog"
        :column="1"
        bordered
        size="small"
      >
        <a-descriptions-item label="操作时间">
          {{ selectedLog.created_at }}
        </a-descriptions-item>
        <a-descriptions-item label="操作用户">
          {{ selectedLog.user }}
        </a-descriptions-item>
        <a-descriptions-item label="操作模块">
          <a-tag color="blue">{{ selectedLog.module }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="日志级别">
          <a-tag :color="getLevelColor(selectedLog.level)">
            {{ getLevelText(selectedLog.level) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="操作内容">
          {{ selectedLog.content }}
        </a-descriptions-item>
        <a-descriptions-item label="IP地址">
          {{ selectedLog.ip }}
        </a-descriptions-item>
        <a-descriptions-item label="用户代理">
          {{ selectedLog.user_agent }}
        </a-descriptions-item>
        <a-descriptions-item label="详细信息">
          <pre class="log-detail">{{ selectedLog.details }}</pre>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { message } from 'ant-design-vue';
import {
  FileTextOutlined,
  DownloadOutlined,
  ReloadOutlined,
  UserOutlined,
  LoginOutlined,
  SettingOutlined,
  DatabaseOutlined,
  SafetyOutlined,
  FileOutlined
} from '@ant-design/icons-vue';

// 响应式数据
const activeCategory = ref('user');
const searchText = ref('');
const dateRange = ref('all');
const loading = ref(false);
const detailModalVisible = ref(false);
const selectedLog = ref(null);

// 分类列表
const categoryList = [
  { key: 'user', name: '用户操作', icon: UserOutlined },
  { key: 'login', name: '登录日志', icon: LoginOutlined },
  { key: 'system', name: '系统操作', icon: SettingOutlined },
  { key: 'database', name: '数据操作', icon: DatabaseOutlined },
  { key: 'security', name: '安全日志', icon: SafetyOutlined },
  { key: 'error', name: '错误日志', icon: FileOutlined }
];

// 表格配置
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`
});

// 表格列配置
const tableColumns = [
  {
    title: '时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
    fixed: 'left',
    sorter: (a, b) => new Date(a.created_at) - new Date(b.created_at)
  },
  {
    title: '用户',
    dataIndex: 'user',
    key: 'user',
    width: 120
  },
  {
    title: '模块',
    dataIndex: 'module',
    key: 'module',
    width: 100
  },
  {
    title: '级别',
    dataIndex: 'level',
    key: 'level',
    width: 100
  },
  {
    title: '操作内容',
    dataIndex: 'content',
    key: 'content',
    ellipsis: true
  },
  {
    title: 'IP地址',
    dataIndex: 'ip',
    key: 'ip',
    width: 140
  },
  {
    title: '操作',
    key: 'actions',
    width: 120,
    fixed: 'right'
  }
];

// 模拟日志数据
const allLogs = ref([
  // 用户操作日志
  { id: 1, category: 'user', level: 'info', user: 'admin', module: '用户管理', content: '创建新用户 user1', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 10:30:15', details: '{"action": "create_user", "target": "user1", "success": true}' },
  { id: 2, category: 'user', level: 'warning', user: 'admin', module: '用户管理', content: '修改用户权限 user2', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 11:15:30', details: '{"action": "modify_permission", "target": "user2", "old_role": "viewer", "new_role": "operator"}' },
  { id: 3, category: 'user', level: 'error', user: 'admin', module: '用户管理', content: '删除用户失败 user3', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 14:22:45', details: '{"action": "delete_user", "target": "user3", "error": "用户正在使用中，无法删除"}' },
  
  // 登录日志
  { id: 4, category: 'login', level: 'info', user: 'admin', module: '登录', content: '用户登录成功', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 09:00:00', details: '{"login_time": "2024-01-20 09:00:00", "success": true}' },
  { id: 5, category: 'login', level: 'warning', user: 'unknown', module: '登录', content: '登录失败，密码错误', ip: '192.168.1.150', user_agent: 'Mozilla/5.0 Firefox/121.0', created_at: '2024-01-20 09:05:12', details: '{"username": "admin", "reason": "wrong_password", "attempt": 3}' },
  { id: 6, category: 'login', level: 'info', user: 'operator1', module: '登录', content: '用户登录成功', ip: '192.168.1.120', user_agent: 'Mozilla/5.0 Safari/17.0', created_at: '2024-01-20 09:30:25', details: '{"login_time": "2024-01-20 09:30:25", "success": true}' },
  
  // 系统操作日志
  { id: 7, category: 'system', level: 'info', user: 'admin', module: '系统设置', content: '修改系统配置', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 15:45:00', details: '{"config": "system_name", "old_value": "旧系统名", "new_value": "新系统名"}' },
  { id: 8, category: 'system', level: 'warning', user: 'admin', module: '系统维护', content: '系统重启', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 16:00:00', details: '{"action": "system_restart", "reason": "配置更新"}' },
  
  // 数据操作日志
  { id: 9, category: 'database', level: 'info', user: 'admin', module: '数据管理', content: '备份数据库', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 02:00:00', details: '{"backup_file": "backup_20240120.sql", "size": "2.5GB"}' },
  { id: 10, category: 'database', level: 'error', user: 'system', module: '数据同步', content: '数据同步失败', ip: '127.0.0.1', user_agent: 'System Process', created_at: '2024-01-20 03:15:30', details: '{"sync_target": "remote_server", "error": "连接超时"}' },
  
  // 安全日志
  { id: 11, category: 'security', level: 'warning', user: 'unknown', module: '安全', content: '检测到异常登录尝试', ip: '203.0.113.0', user_agent: 'Unknown Bot', created_at: '2024-01-20 12:30:00', details: '{"attempts": 10, "blocked": true, "duration": "1小时"}' },
  { id: 12, category: 'security', level: 'info', user: 'admin', module: '权限', content: '更新安全策略', ip: '192.168.1.100', user_agent: 'Mozilla/5.0 Chrome/120.0', created_at: '2024-01-20 13:00:00', details: '{"policy": "password_strength", "level": "high"}' },
  
  // 错误日志
  { id: 13, category: 'error', level: 'error', user: 'system', module: '系统错误', content: '服务异常退出', ip: '127.0.0.1', user_agent: 'System Process', created_at: '2024-01-20 08:45:22', details: '{"service": "monitoring_service", "exit_code": 1, "restart": true}' },
  { id: 14, category: 'error', level: 'error', user: 'system', module: '数据库', content: '数据库连接失败', ip: '127.0.0.1', user_agent: 'System Process', created_at: '2024-01-20 09:12:33', details: '{"database": "mysql", "error": "Too many connections"}' }
]);

// 计算属性
const currentLogs = computed(() => {
  return allLogs.value.filter(item => item.category === activeCategory.value);
});

const filteredLogs = computed(() => {
  let logs = currentLogs.value;
  
  // 按搜索文本过滤
  if (searchText.value) {
    logs = logs.filter(item => 
      item.content.toLowerCase().includes(searchText.value.toLowerCase()) ||
      item.user.toLowerCase().includes(searchText.value.toLowerCase()) ||
      item.module.toLowerCase().includes(searchText.value.toLowerCase())
    );
  }
  
  // 按时间范围过滤
  if (dateRange.value !== 'all') {
    const now = new Date();
    let startDate;
    
    switch (dateRange.value) {
      case 'today':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        break;
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        startDate = new Date(now.getFullYear(), now.getMonth(), 1);
        break;
    }
    
    if (startDate) {
      logs = logs.filter(item => new Date(item.created_at) >= startDate);
    }
  }
  
  return logs;
});

// 方法
const getCurrentCategoryName = () => {
  const categoryNames = {
    'user': '用户操作日志',
    'login': '登录日志',
    'system': '系统操作日志',
    'database': '数据操作日志',
    'security': '安全日志',
    'error': '错误日志'
  };
  return categoryNames[activeCategory.value] || '未知分类';
};

const getLevelColor = (level) => {
  const colors = {
    'info': 'blue',
    'warning': 'orange',
    'error': 'red',
    'debug': 'gray'
  };
  return colors[level] || 'default';
};

const getLevelText = (level) => {
  const texts = {
    'info': '信息',
    'warning': '警告',
    'error': '错误',
    'debug': '调试'
  };
  return texts[level] || level;
};

const handleCategoryChange = (key) => {
  activeCategory.value = key;
  searchText.value = '';
  dateRange.value = 'all';
  pagination.value.current = 1;
};

const handleSearch = () => {
  pagination.value.current = 1;
};

const handleDateRangeChange = () => {
  pagination.value.current = 1;
};

const refreshData = () => {
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
    message.success('数据刷新成功');
  }, 500);
};

const viewLogDetail = (record) => {
  selectedLog.value = record;
  detailModalVisible.value = true;
};

const exportLogs = () => {
  // 模拟导出功能
  message.success('日志导出成功');
};

// 统计方法
const getTodayLogsCount = () => {
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  return allLogs.value.filter(log => log.created_at.startsWith(todayStr)).length;
};

const getErrorLogsCount = () => {
  return allLogs.value.filter(log => log.level === 'error').length;
};

// 监听器
watch(() => filteredLogs.value, (newVal) => {
  pagination.value.total = newVal.length;
});

// 生命周期
onMounted(() => {
  refreshData();
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 操作日志页面特有的样式 */
/* 日志详情样式 */
.log-detail {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #333;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}
</style>