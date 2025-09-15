<template>
  <div class="ip-table-container">
    <!-- IP统计按钮组 -->
    <div class="ip-stats-container">
      <div class="stats-header">
        <h3 class="page-title">
          <UnorderedListOutlined class="title-icon" />
          IP地址管理
        </h3>
        <div class="table-actions">
          <a-space size="middle">
            <a-button type="primary" @click="handleAdd">
              <template #icon><PlusOutlined /></template>
              新增IP
            </a-button>
            <a-button @click="handleScan">
              <template #icon><ScanOutlined /></template>
              IP扫描
            </a-button>
            <a-button @click="handleExport">
              <template #icon><DownloadOutlined /></template>
              导出数据
            </a-button>
            <a-divider type="vertical" />
            <a-tooltip title="批量Ping">
              <a-button @click="handleHeaderBatchPing">
                <template #icon><ApiOutlined /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip title="列表管理">
              <a-button @click="handleListManagement">
                <template #icon><UnorderedListOutlined /></template>
              </a-button>
            </a-tooltip>
          </a-space>
        </div>
      </div>
      
      <!-- IP统计按钮组 -->
      <div class="ip-stats-buttons">
        <div class="stats-button total">
          <div class="button-icon">
            <i class="anticon anticon-appstore"></i>
          </div>
          <div class="button-content">
            <div class="button-title">总IP</div>
            <div class="button-count">{{ totalCount || 0 }}</div>
          </div>
        </div>
        
        <div class="stats-button active">
          <div class="button-icon">
            <i class="anticon anticon-check-circle"></i>
          </div>
          <div class="button-content">
            <div class="button-title">在用</div>
            <div class="button-count">{{ activeCount || 0 }}</div>
          </div>
        </div>
        
        <div class="stats-button available">
          <div class="button-icon">
            <i class="anticon anticon-clock-circle"></i>
          </div>
          <div class="button-content">
            <div class="button-title">可用</div>
            <div class="button-count">{{ availableCount || 0 }}</div>
          </div>
        </div>
        
        <div class="stats-button online">
          <div class="button-icon">
            <i class="anticon anticon-wifi"></i>
          </div>
          <div class="button-content">
            <div class="button-title">在线</div>
            <div class="button-count">{{ onlineCount || 0 }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 查询筛选区域 -->
    <div class="filter-section">
      <div class="filter-header">
        <h4 class="filter-title">
          <SearchOutlined class="title-icon" />
          查询筛选
        </h4>
        <div class="filter-actions">
          <a-space size="middle">
            <a-button type="link" @click="toggleAdvancedFilter" class="expand-btn">
              {{ showAdvancedFilter ? '收起' : '展开' }}
              <DownOutlined :class="{ 'rotate-180': showAdvancedFilter }" />
            </a-button>
            <a-button type="primary" @click="handleSearch">
              <template #icon><SearchOutlined /></template>
              搜索
            </a-button>
            <a-button @click="handleReset">
              <template #icon><ReloadOutlined /></template>
              重置
            </a-button>
          </a-space>
        </div>
      </div>
      <div class="filter-content">
        <!-- 基础搜索 - 始终显示 -->
        <a-row :gutter="[12, 8]">
            <a-col :span="24">
              <div class="filter-item">
                <label class="filter-label">IP地址/主机名</label>
              <a-input
                  :value="searchKeyword"
                  @input="handleSearchInput"
                  placeholder="输入IP地址或主机名" 
                  allow-clear
                >
                  <template #prefix><SearchOutlined /></template>
                </a-input>
            </div>
          </a-col>
        </a-row>
        
        <!-- 高级筛选 - 可折叠 -->
        <div v-show="showAdvancedFilter" class="advanced-filter">
          <a-divider>高级筛选</a-divider>
          <a-row :gutter="[12, 8]">
             <a-col :xl="12" :lg="12" :md="24" :sm="24">
              <div class="filter-item">
                <label class="filter-label">IP状态</label>
                <a-select 
                  :value="ipStatus" 
                  @change="handleStatusChange"
                  placeholder="选择IP状态" 
                  allow-clear
                  style="width: 100%"
                >
                  <a-select-option value="active">
                    <CheckCircleOutlined style="color: #52c41a" /> 在用
                  </a-select-option>
                  <a-select-option value="available">
                    <ClockCircleOutlined style="color: #1890ff" /> 可用
                  </a-select-option>
                  <a-select-option value="reserved">
                    <LockOutlined style="color: #fa8c16" /> 预留
                  </a-select-option>
                  <a-select-option value="conflict">
                    <ExclamationCircleOutlined style="color: #ff4d4f" /> 冲突
                  </a-select-option>
                </a-select>
              </div>
            </a-col>
            <a-col :xl="12" :lg="12" :md="24" :sm="24">
              <div class="filter-item">
                <label class="filter-label">IP类型</label>
                <a-select 
                  :value="ipType" 
                  @change="handleTypeChange"
                  placeholder="选择IP类型" 
                  allow-clear
                  style="width: 100%"
                >
                  <a-select-option value="static">
                    <DatabaseOutlined style="color: #1890ff" /> 静态IP
                  </a-select-option>
                  <a-select-option value="dynamic">
                    <ThunderboltOutlined style="color: #52c41a" /> 动态IP
                  </a-select-option>
                  <a-select-option value="gateway">
                    <NodeIndexOutlined style="color: #fa8c16" /> 网关
                  </a-select-option>
                  <a-select-option value="dns">
                    <CloudOutlined style="color: #722ed1" /> DNS服务器
                  </a-select-option>
                </a-select>
              </div>
            </a-col>
          </a-row>
        </div>
      </div>
    </div>

    <!-- 批量操作工具栏 -->
    <div class="batch-toolbar" v-if="selectedRowKeys.length > 0">
      <div class="selected-info">
        <span>已选择 {{ selectedRowKeys.length }} 项</span>
        <a-button type="link" size="small" @click="clearSelection">清空</a-button>
      </div>
      <div class="batch-actions">
        <a-button 
          type="primary" 
          size="small" 
          @click="batchPing"
          :loading="batchPingLoading"
        >
          批量Ping
        </a-button>
        <a-button 
          size="small" 
          @click="batchToggleMonitoring"
          :loading="batchToggleLoading"
        >
          批量{{ allSelectedMonitored ? '停止' : '启用' }}监控
        </a-button>
        <a-button 
          type="danger" 
          size="small" 
          @click="batchDelete"
          :loading="batchDeleteLoading"
        >
          批量删除
        </a-button>
      </div>
    </div>

    <!-- IP列表表格 -->
    <div class="table-wrapper">
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :row-key="record => record.id"
        :pagination="pagination"
        :loading="loading"
        :row-selection="rowSelection"

        size="middle"
        @change="handleTableChange"
      >
      <!-- 使用新的v-slot语法 -->
      <template #bodyCell="{ column, record }">
        <!-- IP地址列 -->
        <template v-if="column.key === 'ip_address'">
          <div>
            <span class="ip-address">{{ record.ip_address }}</span>
          </div>
        </template>

        <!-- 主机名列 -->
        <template v-else-if="column.key === 'hostname'">
          <span :title="record.hostname">{{ record.hostname || '-' }}</span>
        </template>

        <!-- IP状态列 -->
        <template v-else-if="column.key === 'status'">
          <a-tag :color="getIPStatusColor(record.status)" size="small">
            {{ getIPStatusText(record.status) }}
          </a-tag>
        </template>

        <!-- IP类型列 -->
        <template v-else-if="column.key === 'type'">
          <a-tag :color="getTypeColor(record.type)" size="small">
            {{ getTypeText(record.type) }}
          </a-tag>
        </template>

        <!-- 监控状态列 -->
        <template v-else-if="column.key === 'monitoring_enabled'">
          <a-switch
            :checked="record.monitoring_enabled"
            :loading="record.toggleLoading"
            @change="(checked) => toggleMonitoring(record, checked)"
            size="small"
          />
          <span class="monitoring-text">
            {{ record.monitoring_enabled ? '已监控' : '未监控' }}
          </span>
        </template>


        <!-- 创建时间列 -->
        <template v-else-if="column.key === 'created_at'">
          <div class="time-cell">
            <span v-if="record.created_at" class="time-text">
              {{ formatTime(record.created_at) }}
            </span>
            <span v-else class="no-data">-</span>
            <div v-if="record.created_at" class="time-relative">
              {{ getRelativeTime(record.created_at) }}
            </div>
          </div>
        </template>


        <!-- 操作列 -->
        <template v-else-if="column.key === 'action'">
          <div class="action-buttons">
            <a-tooltip title="查看详情">
              <a-button 
                type="text" 
                size="small" 
                @click="viewDetails(record)"
                class="action-btn"
              >
                <template #icon><EyeOutlined /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip title="Ping测试">
              <a-button 
                type="text" 
                size="small" 
                @click="pingIP(record)"
                :loading="record.pingLoading"
                class="action-btn"
              >
                <template #icon><ApiOutlined /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip title="编辑">
              <a-button 
                type="text" 
                size="small" 
                @click="editIP(record)"
                class="action-btn"
              >
                <template #icon><EditOutlined /></template>
              </a-button>
            </a-tooltip>
            <a-popconfirm
              title="确定要删除这个IP吗？"
              @confirm="deleteIP(record)"
              ok-text="确定"
              cancel-text="取消"
            >
              <a-tooltip title="删除">
                <a-button 
                  type="text" 
                  size="small" 
                  danger
                  :loading="record.deleteLoading"
                  class="action-btn danger"
                >
                  <template #icon><DeleteOutlined /></template>
                </a-button>
              </a-tooltip>
            </a-popconfirm>
          </div>
        </template>
      </template>
      </a-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';
import {
  PlusOutlined,
  ScanOutlined,
  DownloadOutlined,
  ApiOutlined,
  UnorderedListOutlined,
  SearchOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  LockOutlined,
  ExclamationCircleOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
  NodeIndexOutlined,
  CloudOutlined,
  DownOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';

// Props
const props = defineProps({
  dataSource: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    default: () => ({
      current: 1,
      pageSize: 20,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
    })
  },
  searchKeyword: {
    type: String,
    default: ''
  },
  ipStatus: {
    type: String,
    default: ''
  },
  ipType: {
    type: String,
    default: ''
  },
  totalCount: {
    type: Number,
    default: 0
  },
  activeCount: {
    type: Number,
    default: 0
  },
  availableCount: {
    type: Number,
    default: 0
  },
  onlineCount: {
    type: Number,
    default: 0
  }
});

// Emits
const emit = defineEmits([
  'tableChange',
  'viewDetails',
  'pingIP',
  'editIP',
  'deleteIP',
  'toggleMonitoring',
  'batchPing',
  'batchDelete',
  'batchToggleMonitoring',
  'add',
  'scan',
  'export',
  'headerBatchPing',
  'listManagement',
  'search',
  'reset',
  'searchInput',
  'statusChange',
  'typeChange'
]);

// 响应式数据
const selectedRowKeys = ref([]);
const batchPingLoading = ref(false);
const batchDeleteLoading = ref(false);
const batchToggleLoading = ref(false);
const showAdvancedFilter = ref(false);


// 表格列配置
const columns = [
  {
    title: 'IP地址',
    dataIndex: 'ip_address',
    key: 'ip_address',
    width: 120,
    sorter: true
  },
  {
    title: '主机名',
    dataIndex: 'hostname',
    key: 'hostname',
    width: 150,
    ellipsis: true
  },
  {
    title: 'IP状态',
    dataIndex: 'status',
    key: 'status',
    width: 80
  },
  {
    title: '监控状态',
    dataIndex: 'monitoring_enabled',
    key: 'monitoring_enabled',
    width: 90
  },
  {
    title: '操作',
    key: 'action',
    align: 'center',
    width: 50
  }
];

// 行选择配置
const rowSelection = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys) => {
    selectedRowKeys.value = keys;
  },
  onSelectAll: (selected, selectedRows, changeRows) => {
    console.log('onSelectAll:', selected, selectedRows, changeRows);
  }
};

// 计算属性
const allSelectedMonitored = computed(() => {
  if (selectedRowKeys.value.length === 0) return false;
  const selectedRecords = props.dataSource.filter(item => 
    selectedRowKeys.value.includes(item.id)
  );
  return selectedRecords.every(record => record.is_monitored);
});

// 方法
// IP状态相关
const getIPStatusColor = (status) => {
  const statusMap = {
    'active': 'success',
    'available': 'processing',
    'reserved': 'warning',
    'conflict': 'error'
  };
  return statusMap[status] || 'default';
};

const getIPStatusText = (status) => {
  const statusMap = {
    'active': '在用',
    'available': '可用',
    'reserved': '预留',
    'conflict': '冲突'
  };
  return statusMap[status] || status;
};

// IP类型相关
const getTypeColor = (type) => {
  const typeMap = {
    'static': 'blue',
    'dynamic': 'green',
    'gateway': 'orange',
    'dns': 'purple'
  };
  return typeMap[type] || 'default';
};

const getTypeText = (type) => {
  const typeMap = {
    'static': '静态IP',
    'dynamic': '动态IP',
    'gateway': '网关',
    'dns': 'DNS服务器'
  };
  return typeMap[type] || type;
};

// Ping状态相关
const getPingStatusColor = (status) => {
  const statusMap = {
    'online': 'success',
    'offline': 'error',
    'unknown': 'warning'
  };
  return statusMap[status] || 'default';
};

const getPingStatusText = (status) => {
  const statusMap = {
    'online': '在线',
    'offline': '离线',
    'unknown': '未知'
  };
  return statusMap[status] || status;
};

// 时间格式化
const formatTime = (time) => {
  if (!time) return '-';
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};

// 相对时间显示
const getRelativeTime = (time) => {
  if (!time) return '';
  const now = dayjs();
  const target = dayjs(time);
  const diffInMinutes = now.diff(target, 'minute');
  const diffInHours = now.diff(target, 'hour');
  const diffInDays = now.diff(target, 'day');
  
  if (diffInMinutes < 1) {
    return '刚刚';
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}分钟前`;
  } else if (diffInHours < 24) {
    return `${diffInHours}小时前`;
  } else if (diffInDays < 30) {
    return `${diffInDays}天前`;
  } else {
    return target.format('YYYY-MM-DD');
  }
};

// 兼容旧方法
const getStatusColor = getPingStatusColor;
const getStatusText = getPingStatusText;

const clearSelection = () => {
  selectedRowKeys.value = [];
};

const handleTableChange = (pagination, filters, sorter) => {
  emit('tableChange', pagination, filters, sorter);
};

const viewDetails = (record) => {
  emit('viewDetails', record);
};

const editIP = (record) => {
  emit('editIP', record);
};

const pingIP = async (record) => {
  record.pingLoading = true;
  try {
    await emit('pingIP', record);
  } finally {
    record.pingLoading = false;
  }
};

const deleteIP = async (record) => {
  record.deleteLoading = true;
  try {
    await emit('deleteIP', record);
    // 如果删除成功，从选中列表中移除
    const index = selectedRowKeys.value.indexOf(record.id);
    if (index > -1) {
      selectedRowKeys.value.splice(index, 1);
    }
  } finally {
    record.deleteLoading = false;
  }
};

const toggleMonitoring = async (record, checked) => {
  record.toggleLoading = true;
  try {
    await emit('toggleMonitoring', record, checked);
  } finally {
    record.toggleLoading = false;
  }
};

const batchPing = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要操作的IP');
    return;
  }
  
  batchPingLoading.value = true;
  try {
    const selectedRecords = props.dataSource.filter(item => 
      selectedRowKeys.value.includes(item.id)
    );
    await emit('batchPing', selectedRecords);
  } finally {
    batchPingLoading.value = false;
  }
};

const batchDelete = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要删除的IP');
    return;
  }
  
  batchDeleteLoading.value = true;
  try {
    const selectedRecords = props.dataSource.filter(item => 
      selectedRowKeys.value.includes(item.id)
    );
    await emit('batchDelete', selectedRecords);
    // 清空选择
    selectedRowKeys.value = [];
  } finally {
    batchDeleteLoading.value = false;
  }
};

const batchToggleMonitoring = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要操作的IP');
    return;
  }
  
  batchToggleLoading.value = true;
  try {
    const selectedRecords = props.dataSource.filter(item => 
      selectedRowKeys.value.includes(item.id)
    );
    await emit('batchToggleMonitoring', selectedRecords, !allSelectedMonitored.value);
  } finally {
    batchToggleLoading.value = false;
  }
};

// 表格头部按钮事件处理
const handleAdd = () => {
  emit('add');
};

const handleScan = () => {
  emit('scan');
};

const handleExport = () => {
  emit('export');
};

const handleHeaderBatchPing = () => {
  emit('headerBatchPing');
};

const handleListManagement = () => {
  emit('listManagement');
};

// 筛选相关事件处理
const handleSearch = () => {
  emit('search');
};

const handleReset = () => {
  emit('reset');
};

const handleSearchInput = (e) => {
  emit('searchInput', e.target.value);
};

const handleStatusChange = (value) => {
  emit('statusChange', value);
};

const handleTypeChange = (value) => {
  emit('typeChange', value);
};

const toggleAdvancedFilter = () => {
  showAdvancedFilter.value = !showAdvancedFilter.value;
};



// 暴露方法给父组件
defineExpose({
  clearSelection,
  getSelectedRowKeys: () => selectedRowKeys.value,
  getSelectedRecords: () => props.dataSource.filter(item => 
    selectedRowKeys.value.includes(item.id)
  )
});
</script>

<style scoped>
/* 简洁容器样式 */
.ip-table-container {
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  min-height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  position: relative;
}

.table-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* IP统计容器样式 */
.ip-stats-container {
  margin-bottom: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* 统计头部样式 */
.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
}

.title-icon {
  font-size: 22px;
  color: rgba(255, 255, 255, 0.9);
}

/* IP统计按钮组样式 */
.ip-stats-buttons {
  display: flex;
  padding: 24px;
  gap: 20px;
  background: #fafafa;
}

.stats-button {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.stats-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.button-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
}

.button-content {
  flex: 1;
}

.button-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
  font-weight: 500;
}

.button-count {
  font-size: 24px;
  font-weight: 700;
  line-height: 1;
}

/* 不同状态的颜色主题 */
.stats-button.total .button-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.stats-button.total .button-count {
  color: #667eea;
}

.stats-button.active .button-icon {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: white;
}

.stats-button.active .button-count {
  color: #1890ff;
}

.stats-button.available .button-icon {
  background: linear-gradient(135deg, #43e97b, #38f9d7);
  color: white;
}

.stats-button.available .button-count {
  color: #52c41a;
}

.stats-button.online .button-icon {
  background: linear-gradient(135deg, #fa709a, #fee140);
  color: white;
}

.stats-button.online .button-count {
  color: #fa8c16;
}

/* 简洁操作按钮区域 */
.table-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .table-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    width: 100%;
  }
  
  .stats-inline {
    width: 100%;
    justify-content: space-between;
  }
  
  .stat-item {
    flex: 1;
    min-width: 0;
  }
}

/* 简洁搜索过滤区域 */
.filter-section {
  padding: 20px 24px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

.advanced-filter {
  margin-top: 12px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.filter-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #262626;
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  color: #1890ff;
}

.filter-actions {
  display: flex;
  align-items: center;
}

.filter-content {
  margin: 0;
}

.filter-item {
  margin-bottom: 0;
}

.filter-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #262626;
  font-size: 13px;
}

/* 简洁批量操作区域 */
.batch-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #eff6ff;
  border-bottom: 1px solid #e2e8f0;
}

.selected-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1890ff;
  font-weight: 500;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.ip-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ip-address {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-weight: 500;
}

.mac-address {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #666;
}

.monitoring-text {
  margin-left: 8px;
  font-size: 12px;
  color: #8c8c8c;
}

.no-data {
  color: #bfbfbf;
}

.time-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-text {
  font-size: 13px;
  color: #262626;
  font-weight: 500;
}

.time-relative {
  font-size: 11px;
  color: #8c8c8c;
  font-style: italic;
}

.description-text {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 4px;
  animation: pulse 2s infinite;
}

.status-dot.status-online {
  background-color: #52c41a;
  box-shadow: 0 0 0 2px rgba(82, 196, 26, 0.2);
}

.status-dot.status-offline {
  background-color: #ff4d4f;
  box-shadow: 0 0 0 2px rgba(255, 77, 79, 0.2);
}

.status-dot.status-unknown {
  background-color: #faad14;
  box-shadow: 0 0 0 2px rgba(250, 173, 20, 0.2);
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #f5f5f5;
  transform: scale(1.1);
}

.action-btn.danger:hover {
  background-color: #fff2f0;
  color: #ff4d4f;
}

.action-btn .anticon {
  font-size: 14px;
}

/* 简洁输入框样式 */
:deep(.ant-input) {
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  transition: all 0.2s ease;
}

:deep(.ant-input:focus) {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

:deep(.ant-select) {
  border-radius: 6px;
}

:deep(.ant-select .ant-select-selector) {
  border-radius: 6px !important;
  border: 1px solid #d1d5db !important;
  background: #ffffff !important;
}

:deep(.ant-select:not(.ant-select-disabled):hover .ant-select-selector) {
  border-color: #2563eb !important;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .ip-table-container {
    height: calc(100vh - 20px);
  }
  
  .table-header {
    flex-direction: column;
    align-items: stretch;
    padding: 24px;
  }
  
  .stats-inline {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-section {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .ip-table-container {
    height: calc(100vh - 10px);
  }
  
  .table-header {
    padding: 20px;
  }
  
  .filter-section {
    padding: 20px;
  }
  
  .stats-inline {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .batch-toolbar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
    padding: 16px 20px;
  }
  
  .batch-actions {
    justify-content: center;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  .time-cell {
    gap: 1px;
  }
  
  .time-text {
    font-size: 12px;
  }
  
  .time-relative {
    font-size: 10px;
  }
  
  .description-text {
    font-size: 11px;
  }
  
  .mac-address {
    font-size: 11px;
  }
}

/* 表格样式优化 */
:deep(.ant-table) {
  font-size: 13px;
}

:deep(.ant-table-container) {
  display: flex;
  flex-direction: column;
}

:deep(.ant-table-content) {
  overflow: auto;
}

:deep(.ant-table-body) {
  overflow-y: visible;
}

:deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
  color: #262626;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #f5f5f5;
}

:deep(.ant-table-row-selected) {
  background: #e6f7ff;
}

:deep(.ant-table-row-selected:hover > td) {
  background: #bae7ff;
}

:deep(.ant-pagination) {
  margin: 12px 16px;
  text-align: right;
  flex-shrink: 0;
  border-top: 1px solid #f0f0f0;
  padding-top: 12px;
}

:deep(.ant-switch) {
  min-width: 28px;
}

:deep(.ant-tag) {
  margin: 0;
  border-radius: 4px;
}

/* 只有操作列居中对齐 */
:deep(.ant-table-tbody > tr > td:nth-child(6)) {
  text-align: center !important;
}

:deep(.ant-table-thead > tr > th:nth-child(6)) {
  text-align: center !important;
}
</style>