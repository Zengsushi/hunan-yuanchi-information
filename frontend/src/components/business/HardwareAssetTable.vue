<template>
  <div class="hardware-asset-table-container">
    <!-- 硬件设备统计按钮组 -->
    <div class="hardware-stats-container">
      <div class="stats-header">
        <div class="page-title">
          <h3 >
            <UnorderedListOutlined class="title-icon" />
            硬件设备管理
          </h3>
        </div>
        
        <!-- 硬件设备统计按钮组 -->
      <div class="hardware-stats-buttons">
        <div 
          class="stats-button active"
          :class="{ 'stats-active': currentFilter === 'active' }"
          @click="handleStatsClick('active')"
        >
          <div class="button-icon">
            <i class="anticon anticon-check-circle"></i>
          </div>
          <div class="button-content">
            <div class="button-title">在用</div>
            <div class="button-count">{{ activeCount || 0 }}</div>
          </div>
        </div>
        
        <div 
          class="stats-button scrapped"
          :class="{ 'stats-active': currentFilter === 'scrapped' }"
          @click="handleStatsClick('scrapped')"
        >
          <div class="button-icon">
            <i class="anticon anticon-delete"></i>
          </div>
          <div class="button-content">
            <div class="button-title">报废</div>
            <div class="button-count">{{ scrappedCount || 0 }}</div>
          </div>
        </div>
        </div>

      </div>
    </div>

    <!-- 查询筛选区域 -->
    <div class="filter-section">
      <div class="filter-header">
        <h3 class="filter-title">
          <SearchOutlined class="title-icon" />
          查询筛选
        </h3>
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
              <label class="filter-label">设备名称/序列号</label>
              <a-input
                :value="searchKeyword"
                @input="handleSearchInput"
                placeholder="输入设备名称或序列号" 
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
                <label class="filter-label">设备状态</label>
                <a-select 
                  :value="assetStatus" 
                  @change="handleStatusChange"
                  placeholder="选择设备状态（可多选）" 
                  allow-clear
                  mode="multiple"
                  :max-tag-count="2"
                  :loading="dictionaryLoading"
                  style="width: 100%"
                >
                  <a-select-option 
                    v-for="option in assetStatusOptions" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    <a-tag :color="option.color" size="small">{{ option.label }}</a-tag>
                  </a-select-option>
                </a-select>
              </div>
            </a-col>
            <a-col :xl="12" :lg="12" :md="24" :sm="24">
              <div class="filter-item">
                <label class="filter-label">设备类型</label>
                <a-select 
                  :value="assetType" 
                  @change="handleTypeChange"
                  placeholder="选择设备类型" 
                  allow-clear
                  :loading="dictionaryLoading"
                  style="width: 100%"
                >
                  <a-select-option 
                    v-for="option in assetTypeOptions" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    <a-tag :color="option.color" size="small">{{ option.label }}</a-tag>
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
          @click="batchUpdateMonitoring"
          :loading="batchMonitoringLoading"
        >
          批量监控
        </a-button>
        <a-button 
          size="small" 
          @click="batchToggleStatus"
          :loading="batchToggleLoading"
        >
          批量{{ allSelectedActive ? '停用' : '启用' }}
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

    <!-- 硬件设施列表表格 -->
    <div class="table-wrapper">
      <!-- 表格头部 -->
      <div class="table-header">
        <div class="table-title">
          <h4>设备列表</h4>
        </div>
        <div class="table-actions">
          <a-space size="middle">
            <a-button v-if="currentFilter !== 'scrapped'" type="primary" @click="handleAdd">
              <template #icon><PlusOutlined /></template>
              新增设备
            </a-button>
            <a-button v-if="currentFilter !== 'scrapped'" @click="handleImport">
              <template #icon><UploadOutlined /></template>
              导入数据
            </a-button>
            <a-button v-if="currentFilter !== 'scrapped'" @click="handleExport">
              <template #icon><DownloadOutlined /></template>
              导出数据
            </a-button>
            <a-tooltip v-if="currentFilter !== 'scrapped'" title="批量监控">
              <a-button @click="handleHeaderBatchMonitoring">
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
          <!-- 设备名称列 -->
          <template v-if="column.key === 'name'">
            <div>
              <span class="asset-name">{{ record.name }}</span>
            </div>
          </template>

          <!-- 序列号列 -->
          <template v-else-if="column.key === 'serial_number'">
            <span :title="record.serial_number">{{ record.serial_number || '-' }}</span>
          </template>

          <!-- 设备状态列 -->
          <template v-else-if="column.key === 'asset_status'">
            <a-tag :color="getAssetStatusColor(record.asset_status)" size="small">
              {{ getAssetStatusText(record.asset_status) }}
            </a-tag>
          </template>

          <!-- 设备类型列 -->
          <template v-else-if="column.key === 'type'">
            <a-tag :color="getTypeColor(record.type)" size="small">
              {{ getTypeText(record.type) }}
            </a-tag>
          </template>

          <!-- 供应商信息列 -->
          <template v-else-if="column.key === 'supplier_info'">
            <span v-if="record.supplier_name">
              {{ record.supplier_name }}
              <span v-if="record.supplier_contact_person">--{{ record.supplier_contact_person }}</span>
            </span>
            <span v-else>-</span>
          </template>

          <!-- 保修状态列 -->
          <template v-else-if="column.key === 'warranty_status_display'">
            <a-tag :color="getWarrantyStatusColor(record.warranty_status_display)" size="small">
              {{ record.warranty_status_display || '-' }}
            </a-tag>
          </template>

          <!-- 监控状态列 -->
          <template v-else-if="column.key === 'monitoring_status'">
            <a-switch
              :checked="record.monitoring_status"
              :loading="record.toggleLoading"
              @change="(checked) => toggleMonitoring(record, checked)"
              size="small"
            />
            <span class="monitoring-text">
              {{ record.monitoring_status ? '已监控' : '未监控' }}
            </span>
          </template>

          <!-- 监控状态列（兼容旧字段） -->
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
              <a-tooltip title="编辑">
                <a-button 
                  type="text" 
                  size="small" 
                  @click="editAsset(record)"
                  class="action-btn"
                >
                  <template #icon><EditOutlined /></template>
                </a-button>
              </a-tooltip>
              <a-tooltip title="历史记录">
                <a-button 
                  type="text" 
                  size="small" 
                  @click="viewHistory(record)"
                  class="action-btn"
                >
                  <template #icon><HistoryOutlined /></template>
                </a-button>
              </a-tooltip>
              <a-popconfirm
                title="确定要删除这个设备吗？"
                @confirm="deleteAsset(record)"
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
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';
import { dictionaryAPI } from '@/api';
import {
  PlusOutlined,
  UploadOutlined,
  DownloadOutlined,
  ApiOutlined,
  UnorderedListOutlined,
  SearchOutlined,
  ReloadOutlined,
  DownOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  HistoryOutlined
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
  assetStatus: {
    type: [String, Array],
    default: () => []
  },
  assetType: {
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
  warrantyCount: {
    type: Number,
    default: 0
  },
  scrappedCount: {
    type: Number,
    default: 0
  },
  tableMode: {
    type: String,
    default: 'all', // 'all', 'in_use', 'scrapped'
    validator: (value) => ['all', 'in_use', 'scrapped'].includes(value)
  },
  currentFilter: {
    type: String,
    default: 'active'
  }
});

// Emits
const emit = defineEmits([
  'tableChange',
  'viewDetails',
  'editAsset',
  'deleteAsset',
  'toggleMonitoring',
  'batchUpdateMonitoring',
  'batchDelete',
  'batchToggleStatus',
  'openDrawer',
  'add',
  'import',
  'export',
  'headerBatchMonitoring',
  'listManagement',
  'search',
  'reset',
  'searchInput',
  'statusChange',
  'typeChange',
  'viewHistory',
  'statsFilter'
]);

// 响应式数据
const selectedRowKeys = ref([]);
const batchMonitoringLoading = ref(false);
const batchDeleteLoading = ref(false);
const batchToggleLoading = ref(false);
const showAdvancedFilter = ref(false);

// 统计按钮点击处理
const handleStatsClick = (filterType) => {
  emit('statsFilter', filterType);
};

// 字典数据
const assetStatusOptions = ref([]);
const assetTypeOptions = ref([]);
const dictionaryLoading = ref(false);

// 表格列配置
const columns = computed(() => {
  // 在用设备表格列配置
  const inUseColumns = [
    {
      title: '资产标签',
      dataIndex: 'asset_tag',
      key: 'asset_tag',
      width: 120,
      sorter: true
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 150,
      ellipsis: true
    },
    {
      title: '制造商',
      dataIndex: 'manufacturer',
      key: 'manufacturer',
      width: 120
    },
    {
      title: '保修状态',
      dataIndex: 'warranty_status_display',
      key: 'warranty_status_display',
      width: 180
    },
    {
      title: '监控状态',
      dataIndex: 'monitoring_status',
      key: 'monitoring_status',
      width: 90
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
      width: 150,
      ellipsis: true
    },
    {
      title: '资产责任人',
      dataIndex: 'asset_owner',
      key: 'asset_owner',
      width: 100
    },
    {
      title: '供应商机构名--责任人',
      key: 'supplier_info',
      width: 220,
      ellipsis: true
    },
    {
      title: '操作',
      key: 'action',
      align: 'center',
      width: 120
    }
  ];

  // 报废设备表格列配置
  const scrappedColumns = [
    {
      title: '资产标签',
      dataIndex: 'asset_tag',
      key: 'asset_tag',
      width: 120,
      sorter: true
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 150,
      ellipsis: true
    },
    {
      title: '制造商',
      dataIndex: 'manufacturer',
      key: 'manufacturer',
      width: 120
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
      width: 150,
      ellipsis: true
    },
    {
      title: '操作',
      key: 'action',
      align: 'center',
      width: 120
    }
  ];

  // 默认全部列配置（保持原有功能）
  const allColumns = [
    {
      title: '资产标签',
      dataIndex: 'asset_tag',
      key: 'asset_tag',
      width: 120,
      sorter: true
    },
    {
      title: '序列号',
      dataIndex: 'serial_number',
      key: 'serial_number',
      width: 120,
      ellipsis: true
    },
    {
      title: '设备状态',
      dataIndex: 'asset_status',
      key: 'asset_status',
      width: 80
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 150,
      ellipsis: true
    },
    {
      title: '监控状态',
      dataIndex: 'monitoring_status',
      key: 'monitoring_status',
      width: 90
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 120,
      sorter: true
    },
    {
      title: '操作',
      key: 'action',
      align: 'center',
      width: 120
    }
  ];

  switch (props.currentFilter) {
    case 'active':
      return inUseColumns;
    case 'scrapped':
      return scrappedColumns;
    default:
      return allColumns;
  }
});

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
const allSelectedActive = computed(() => {
  if (selectedRowKeys.value.length === 0) return false;
  const selectedRecords = props.dataSource.filter(item => 
    selectedRowKeys.value.includes(item.id)
  );
  return selectedRecords.every(record => record.status === 'active');
});

// 方法
// 设备状态相关
const getAssetStatusColor = (status) => {
  const statusMap = {
    'active': 'success',
    'available': 'processing',
    'maintenance': 'warning',
    'retired': 'error'
  };
  return statusMap[status] || 'default';
};

const getAssetStatusText = (status) => {
  const statusMap = {
    'active': '在用',
    'in_use': '在用',
    'available': '可用',
    'maintenance': '维护',
    'retired': '退役',
    'scrapped': '报废'
  };
  return statusMap[status] || status;
};

// 保修状态相关
const getWarrantyStatusColor = (status) => {
  const statusMap = {
    '在保': 'success',
    '过保': 'error',
    '即将过保': 'warning',
    '未知': 'default'
  };
  return statusMap[status] || 'default';
};

// 设备类型相关
const getTypeColor = (type) => {
  const typeMap = {
    'server': 'blue',
    'network': 'green',
    'storage': 'orange',
    'security': 'purple'
  };
  return typeMap[type] || 'default';
};

const getTypeText = (type) => {
  const typeMap = {
    'server': '服务器',
    'network': '网络设备',
    'storage': '存储设备',
    'security': '安全设备'
  };
  return typeMap[type] || type;
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

const clearSelection = () => {
  selectedRowKeys.value = [];
};

const handleTableChange = (pagination, filters, sorter) => {
  emit('tableChange', pagination, filters, sorter);
};

const viewDetails = (record) => {
  emit('viewDetails', record);
};

const editAsset = (record) => {
  emit('editAsset', record);
};

const viewHistory = (record) => {
  emit('viewHistory', record);
};

const deleteAsset = async (record) => {
  record.deleteLoading = true;
  try {
    await emit('deleteAsset', record);
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

const batchUpdateMonitoring = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要操作的设备');
    return;
  }
  
  batchMonitoringLoading.value = true;
  try {
    const selectedRecords = props.dataSource.filter(item => 
      selectedRowKeys.value.includes(item.id)
    );
    await emit('batchUpdateMonitoring', selectedRecords);
  } finally {
    batchMonitoringLoading.value = false;
  }
};

const batchDelete = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要删除的设备');
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

const batchToggleStatus = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请先选择要操作的设备');
    return;
  }
  
  batchToggleLoading.value = true;
  try {
    const selectedRecords = props.dataSource.filter(item => 
      selectedRowKeys.value.includes(item.id)
    );
    await emit('batchToggleStatus', selectedRecords, !allSelectedActive.value);
  } finally {
    batchToggleLoading.value = false;
  }
};

// 表格头部按钮事件处理
const handleAdd = () => {
  //打开弹窗
  emit('add')
};

const handleImport = () => {
  emit('import');
};

const handleExport = () => {
  emit('export');
};

const handleHeaderBatchMonitoring = () => {
  emit('headerBatchMonitoring');
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

// 字典数据加载方法
const loadDictionaryData = async () => {
  try {
    dictionaryLoading.value = true;
    
    // 加载设备状态字典
    const statusResponse = await dictionaryAPI.getDictionaryByCategory('status');
    if (statusResponse.data && statusResponse.data.results) {
      assetStatusOptions.value = statusResponse.data.results.map(item => ({
        value: item.value,
        label: item.label,
        color: getAssetStatusColor(item.value)
      }));
    }
    
    // 加载设备类型字典
    const typeResponse = await dictionaryAPI.getDictionaryByCategory('asset_type');
    if (typeResponse.data && typeResponse.data.results) {
      assetTypeOptions.value = typeResponse.data.results.map(item => ({
        value: item.value,
        label: item.label,
        color: getTypeColor(item.value)
      }));
    }
  } catch (error) {
    console.error('加载字典数据失败:', error);
    message.error('加载字典数据失败');
  } finally {
    dictionaryLoading.value = false;
  }
};

// 组件挂载时加载字典数据
onMounted(() => {
  loadDictionaryData();
});

// 暴露方法给父组件
defineExpose({
  clearSelection,
  getSelectedRowKeys: () => selectedRowKeys.value,
  getSelectedRecords: () => props.dataSource.filter(item => 
    selectedRowKeys.value.includes(item.id)
  ),
  loadDictionaryData
});
</script>

<style scoped>
/* 简洁容器样式 */
.hardware-asset-table-container {
  background: #ffffff;
  border-radius: 8px;
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

/* 硬件设备统计容器样式 */
.hardware-stats-container {
  background: #fff;
  overflow: hidden;
}

/* 统计头部样式 */
.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  color: white;
}

.page-title h3{
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e40af;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  font-size: 22px;
  color: rgba(255, 255, 255, 0.9);
}

/* 硬件设备统计按钮组样式 */
.stats-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 80px;
  padding: 0 24px;
  gap: 24px;
}


.hardware-stats-buttons {
  display: flex;
  gap: 16px;
  flex: 1;
  justify-content: center;
  max-width: 500px;
}

.table-actions {
  flex-shrink: 0;
}

.stats-button {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
  min-width: 160px;
  max-width: 200px;
  height: 56px;
}

.stats-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  cursor: pointer;
}

.stats-button.stats-active {
  border: 1px solid #1890ff;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.2);
  transform: translateY(-2px);
}

.button-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  font-size: 14px;
  flex-shrink: 0;
}

.button-content {
  flex: 1;
}

.button-title {
  font-size: 11px;
  color: #666;
  margin-bottom: 1px;
  font-weight: 500;
}

.button-count {
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 2px;
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

.stats-button.warranty .button-icon {
  background: linear-gradient(135deg, #fa709a, #fee140);
  color: white;
}

.stats-button.warranty .button-count {
  color: #fa8c16;
}

.stats-button.scrapped .button-icon {
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
  color: white;
}

.stats-button.scrapped .button-count {
  color: #ff4d4f;
}

/* 表格头部样式 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e9ecef;
  border-radius: 6px 6px 0 0;
}

.table-title h4 {
  margin: 0;
  font-size: 17px;
  font-weight: 600;
  color: #262626;
}

/* 简洁操作按钮区域 */
.table-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .hardware-stats-buttons {
    max-width: none;
    justify-content: center;
  }
}

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
  
  .hardware-stats-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .stats-button {
    min-width: auto;
    max-width: none;
  }
}

/* 简洁搜索过滤区域 */
.filter-section {
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
}

.expand-btn {
  padding: 4px 8px;
  font-size: 12px;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: transform 0.3s ease;
}

.advanced-filter {
  margin-top: 12px;
  animation: fadeIn 0.3s ease;
  margin-top: 8px;
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
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e9ecef;
}

.filter-title {
  font-size: 15px;
  font-weight: bold;
  color: #495057;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  color: #1890ff;
  font-size: 14px;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-content {
  padding: 16px 24px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
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
  padding: 16px 16px;
  background: #ffffff;
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

.asset-name {
  font-weight: 500;
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
  background: #ffffff;
  font-weight: 600;
  color: #262626;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #ffffff;
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
:deep(.ant-table-tbody > tr > td:nth-child(7)) {
  text-align: center !important;
}

:deep(.ant-table-thead > tr > th:nth-child(7)) {
  text-align: center !important;
}
</style>