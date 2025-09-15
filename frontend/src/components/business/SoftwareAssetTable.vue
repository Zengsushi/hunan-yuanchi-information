<template>
  <div class="software-asset-table-container">
    <!-- 软件资产统计按钮组 -->
    <div class="software-stats-container">
      <div class="stats-header">
        <div class="page-title">
          <h3>
            <UnorderedListOutlined class="title-icon" />
            软件资产列表
          </h3>
        </div>
        <!-- 软件资产统计按钮组 -->
        <div class="software-stats-buttons">
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
          <div class="software-stats-buttons">
          <div 
            class="stats-button active"
            :class="{ 'stats-active': currentFilter === 'test' }"
            @click="handleStatsClick('test')"
          >
            <div class="button-icon">
              <i class="anticon anticon-check-circle"></i>
            </div>
            <div class="button-content">  
              <div class="button-title">占位</div>
              <div class="button-count">{{ activeCount || 0 }}</div>
            </div>
          </div>
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
              <label class="filter-label">软件名称/版本</label>
              <a-input
                :value="searchKeyword"
                @input="handleSearchInput"
                placeholder="输入软件名称或版本" 
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
            <a-col :xl="8" :lg="12" :md="24" :sm="24">
              <div class="filter-item">
                <label class="filter-label">资产状态</label>
                <a-select 
                  :value="assetStatus" 
                  @change="handleStatusChange"
                  placeholder="选择资产状态" 
                  allow-clear
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
            <a-col :xl="8" :lg="12" :md="24" :sm="24">
              <div class="filter-item">
                <label class="filter-label">软件类型</label>
                <a-select 
                  :value="softwareType" 
                  @change="handleTypeChange"
                  placeholder="选择软件类型" 
                  allow-clear
                  :loading="dictionaryLoading"
                  style="width: 100%"
                >
                  <a-select-option 
                    v-for="option in softwareTypeOptions" 
                    :key="option.value" 
                    :value="option.value"
                  >
                    <a-tag :color="option.color" size="small">{{ option.label }}</a-tag>
                  </a-select-option>
                </a-select>
              </div>
            </a-col>
            <a-col :xl="8" :lg="12" :md="24" :sm="24">
              <div class="filter-item">
                <label class="filter-label">制造商</label>
                <a-input
                  :value="manufacturer"
                  @input="handleManufacturerInput"
                  placeholder="输入制造商" 
                  allow-clear
                  style="width: 100%"
                />
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

    <!-- 软件资产列表表格 -->
    <div class="table-wrapper">
      <!-- 表格头部 -->
      <div class="table-header" v-if="currentFilter === 'active'">
        <div class="table-title">
          <h4>软件列表</h4>
        </div>
        <div class="table-actions">
          <a-space size="middle">
            <a-button v-if="currentFilter !== 'scrapped'" type="primary" @click="handleAdd">
              <template #icon><PlusOutlined /></template>
              新增软件
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
          <!-- 资产标签	列 -->
          <template v-if="column.key === 'asset_tag'">
            <div>
              <span class="asset-name">{{ record.asset_tag  }} </span>
            </div>
          </template>
          <!-- 型号 列 -->
          <template v-else-if="column.key === 'model'">
            <span :title="record.serial_number">{{ record.software_type || '-' }}</span>
          </template>
          <!-- 制造商 列 -->
          <template v-else-if="column.key === 'vendor'">
            <span :title="record.serial_number">{{ record.vendor || '-' }}</span>
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
          <!-- 保修状态 列 -->
          <template v-else-if="column.key === 'warranty_status'">
            <a-tag :color="getWarrantyStatusColor(record.warranty_status)" size="small">
              {{ record.warranty_status || '-' }}
            </a-tag>
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
          <template v-else-if="column.key === 'asset_owener'">
            <span :title="record.serial_number">{{ record.asset_owener || '-' }}</span>
          </template>
          <template v-else-if="column.key === 'supplier_contact'">
            <span :title="record.serial_number">{{ record.supplier_contact || '-' }}</span>
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
import { ref, reactive, computed, onMounted, watch } from 'vue'
import {
  PlusOutlined,
  UploadOutlined,
  DownloadOutlined,
  ApiOutlined,
  UnorderedListOutlined,
  SearchOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ToolOutlined,
  ExclamationCircleOutlined,
  DatabaseOutlined,
  NodeIndexOutlined,
  HddOutlined,
  SafetyOutlined,
  DownOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  HistoryOutlined, 
  NodeExpandOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
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
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
    })
  },
  selectedRowKeys: {
    type: Array,
    default: () => []
  },
  searchKeyword: {
    type: String,
    default: ''
  },
  assetStatus: {
    type: String,
    default: ''
  },
  softwareType: {
    type: String,
    default: ''
  },
  manufacturer: {
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
  maintenanceCount: {
    type: Number,
    default: 0
  },
  retiredCount: {
    type: Number,
    default: 0
  },
  batchDeleting: {
    type: Boolean,
    default: false
  },
  currentFilter: {
    type: String,
    default : "active"
  } ,
})

// Emits
const emit = defineEmits([
  'search',
  'reset',
  'add',
  'edit',
  'delete',
  'view',
  'export',
  'import',
  'batch-delete',
  'clear-selection',
  'table-change',
  'search-input',
  'status-change',
  'type-change',
  'manufacturer-input',
  'batch-operations',
  'list-management',
  'statsFilter'
])

// 响应式数据
const showAdvancedFilter = ref(false)
const dictionaryLoading = ref(false)
const selectedRows = ref([])
const currentFilter = ref(props.currentFilter)

// 资产状态选项
const assetStatusOptions = ref([
  { value: 'in_use', label: '使用中', color: 'green' },
  { value: 'idle', label: '闲置', color: 'orange' },
  { value: 'maintenance', label: '维护中', color: 'blue' },
  { value: 'scrapped', label: '报废', color: 'red' }
])

// 软件类型选项
const softwareTypeOptions = ref([
  { value: 'system', label: '系统软件', color: 'blue' },
  { value: 'application', label: '应用软件', color: 'green' },
  { value: 'development', label: '开发工具', color: 'purple' },
  { value: 'security', label: '安全软件', color: 'red' },
  { value: 'database', label: '数据库', color: 'orange' },
  { value: 'middleware', label: '中间件', color: 'cyan' },
  { value: 'other', label: '其他', color: 'default' }
])

// 表格列配置

const columns = computed( () => {
  const inUseColumns = [
    {
      title: '资产标签',
      dataIndex: 'asset_tag',
      key: 'asset_tag',
      width: 100,
      fixed: 'left',
      slots: { customRender: 'asset_tag' }
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 150
    },
    {
      title: '制造商',
      dataIndex: 'vendor',
      key: 'vendor',
      width: 120,
      slots: { customRender: 'vendor' }
    },
    { 
      title: '监控状态',
      dataIndex: 'monitoring_status',
      key: 'monitoring_status',
      width: 80
    },
    {
      title: '保修状态',
      dataIndex: 'warranty_status',
      key: 'warranty_status',
      width: 80
    },
    {
      title: '资产负责人',
      dataIndex: 'asset_owener',
      key: 'asset_owener',
      width: 80
    },
    {
      title: '供应商负责人',
      dataIndex: 'supplier_contact',
      key: 'supplier_contact',
      width: 80
    },
    {
        title: '操作',
        key: 'action',
        align: 'center',
        width: 120,
        slots: { customRender: 'action' }
    }]

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
      title: '操作',
      key: 'action',
      align: 'center',
      width: 120
    }
  ];

    const allColumns = []
    switch (props.currentFilter) {
      case 'active':
        return inUseColumns;
      case 'scrapped':
        return scrappedColumns;
      default:
        return allColumns;
    }
})

// 行选择配置
const rowSelection = computed(() => ({
  selectedRowKeys: props.selectedRowKeys,
  onChange: (keys, rows) => {
    selectedRows.value = rows
    emit('select-change', keys)
  },
  onSelectAll: (selected, selectedRows, changeRows) => {
    console.log('onSelectAll', selected, selectedRows, changeRows)
  }
}))

// 计算属性
const hasSelected = computed(() => props.selectedRowKeys.length > 0)
const selectedCount = computed(() => props.selectedRowKeys.length)

// 方法
const toggleAdvancedFilter = () => {
  showAdvancedFilter.value = !showAdvancedFilter.value
}

const handleSearchInput = (e) => {
  emit('search-input', e.target.value)
}

const handleStatusChange = (value) => {
  emit('status-change', value)
}

const handleTypeChange = (value) => {
  emit('type-change', value)
}

const handleManufacturerInput = (e) => {
  emit('manufacturer-input', e.target.value)
}

const handleSearch = () => {
  const searchParams = {
    keyword: props.searchKeyword,
    assetStatus: props.assetStatus,
    softwareType: props.softwareType,
    manufacturer: props.manufacturer
  }
  emit('search', searchParams)
}

const handleReset = () => {
  emit('reset')
}

const handleAdd = () => {
  emit('add')
}

const handleEdit = (record) => {
  emit('edit', record)
}

const handleDelete = (record) => {
  emit('delete', record)
}

const handleView = (record) => {
  emit('view', record)
}

const handleExport = () => {
  emit('export')
}

const handleImport = () => {
  emit('import')
}

const handleBatchOperations = () => {
  emit('batch-operations')
}

const handleListManagement = () => {
  emit('list-management')
}

// 统计按钮点击处理
const handleStatsClick = (filterType) => {
  emit('statsFilter', filterType);
};

const handleTableChange = (pagination, filters, sorter) => {
  emit('table-change', { pagination, filters, sorter })
}

// 获取软件类型颜色
const getSoftwareTypeColor = (type) => {
  const option = softwareTypeOptions.value.find(item => item.value === type)
  return option ? option.color : 'default'
}

// 获取软件类型标签
const getSoftwareTypeLabel = (type) => {
  const option = softwareTypeOptions.value.find(item => item.value === type)
  return option ? option.label : type
}

// 获取许可证状态颜色
const getLicenseStatusColor = (status) => {
  const colorMap = {
    'valid': 'green',
    'expired': 'red',
    'near_expired': 'orange',
    'unlimited': 'blue'
  }
  return colorMap[status] || 'default'
}

// 获取许可证状态标签
const getLicenseStatusLabel = (status) => {
  const labelMap = {
    'valid': '有效',
    'expired': '已过期',
    'near_expired': '即将过期',
    'unlimited': '永久'
  }
  return labelMap[status] || status
}

const getLicenseEndDateColor = (endDate) => {
  if (!endDate) return '#666'
  
  const today = new Date()
  const end = new Date(endDate)
  const diffDays = Math.ceil((end - today) / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) return '#f5222d' // 已过期
  if (diffDays <= 30) return '#fa8c16' // 即将过期
  return '#52c41a' // 正常
}
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


.software-stats-buttons {
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
  font-weight: 900;
  background-color: black;
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