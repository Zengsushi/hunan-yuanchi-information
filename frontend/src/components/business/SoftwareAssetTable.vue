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

    <!-- 表格区域 -->
     
     <div class="table-wrapper">
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
      <!-- 软件资产表格区域 -->
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        :scroll="{ x: 1500 }"
        row-key="id"
        size="middle"
        @change="handleTableChange"
        class="asset-table"
      >
        <!-- 软件名称列 -->
        <template #software_name="{ record }">
          <div class="asset-info">
            <div class="asset-name">{{ record.software_name }}</div>
            <div class="asset-detail">版本: {{ record.version }}</div>
          </div>
        </template>

        <!-- 软件类型列 -->
        <template #software_type="{ record }">
          <a-tag :color="getSoftwareTypeColor(record.software_type)" size="small">
            {{ getSoftwareTypeLabel(record.software_type) }}
          </a-tag>
        </template>

        <!-- 许可证状态列 -->
        <template #license_status="{ record }">
          <a-tag :color="getLicenseStatusColor(record.license_status)" size="small">
            {{ getLicenseStatusLabel(record.license_status) }}
          </a-tag>
        </template>


        <!-- 操作列 -->
        <template #action="{ record }">
          <a-space size="small">
            <a-tooltip title="查看详情">
              <a-button type="text" size="small" @click="handleView(record)" class="action-btn">
                <template #icon><EyeOutlined /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip title="编辑">
              <a-button type="text" size="small" @click="handleEdit(record)" class="action-btn">
                <template #icon><EditOutlined /></template>
              </a-button>
            </a-tooltip>
            <a-tooltip title="删除">
              <a-button type="text" size="small" danger @click="handleDelete(record)" class="action-btn">
                <template #icon><DeleteOutlined /></template>
              </a-button>
            </a-tooltip>
          </a-space>
        </template>
      </a-table>
    </div>

    <!-- 批量操作 -->
    <div class="batch-actions" v-if="selectedRowKeys.length > 0">
      <a-alert
        :message="`已选择 ${selectedRowKeys.length} 项`"
        type="info"
        show-icon
        :closable="false"
      >
        <template #action>
          <a-space>
            <a-button size="small" danger @click="$emit('batch-delete')" :loading="batchDeleting">
              批量删除
            </a-button>
            <a-button size="small" @click="$emit('clear-selection')">
              清除选择
            </a-button>
          </a-space>
        </template>
      </a-alert>
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
  HistoryOutlined 
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
    default: 'total'
  } , 
  data : {
    type: Array,
    default: () => []
  }
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
  'stats-filter'
])

// 响应式数据
const showAdvancedFilter = ref(false)
const dictionaryLoading = ref(false)
const selectedRows = ref([])

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
const columns = [
  {
    title: '软件名称',
    dataIndex: 'software_name',
    key: 'software_name',
    width: 200,
    fixed: 'left',
    slots: { customRender: 'software_name' }
  },
  {
    title: '供应商',
    dataIndex: 'vendor',
    key: 'vendor',
    width: 150
  },
  {
    title: '软件类型',
    dataIndex: 'software_type',
    key: 'software_type',
    width: 120,
    slots: { customRender: 'software_type' }
  },
  {
    title: '许可证类型',
    dataIndex: 'license_type',
    key: 'license_type',
    width: 120
  },
  {
    title: '许可证数量',
    dataIndex: 'license_count',
    key: 'license_count',
    width: 100
  },
  {
    title: '已使用',
    dataIndex: 'used_count',
    key: 'used_count',
    width: 80
  },
  {
    title: '可用',
    dataIndex: 'available_count',
    key: 'available_count',
    width: 80
  },
  {
    title: '采购日期',
    dataIndex: 'purchase_date',
    key: 'purchase_date',
    width: 120
  },
  {
    title: '许可证状态',
    dataIndex: 'license_status',
    key: 'license_status',
    width: 120,
    slots: { customRender: 'license_status' }
  },
  {
    title: '操作',
    key: 'action',
    width: 200,
    fixed: 'right',
    slots: { customRender: 'action' }
  }
]

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
  emit('stats-filter', filterType)
}

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
.software-asset-table-container {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  min-height: calc(100vh - 40px);
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 软件资产统计容器样式 */
.software-stats-container {
  background: #fff;
  overflow: hidden;
}

/* 统计头部样式 */
.stats-header {
  display: flex;
  height: 80px;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.page-title h3 {
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
  color: #1e40af;
}

/* 软件资产统计按钮组样式 */
.software-stats-buttons {
  display: flex;
  gap: 16px;
  flex: 1;
  justify-content: center;
  max-width: 600px;
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
  min-width: 140px;
  max-width: 180px;
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

.stats-button.maintenance .button-icon {
  background: linear-gradient(135deg, #fa709a, #fee140);
  color: white;
}

.stats-button.maintenance .button-count {
  color: #fa8c16;
}

.stats-button.retired .button-icon {
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
  color: white;
}

.stats-button.retired .button-count {
  color: #ff4d4f;
}

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

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .software-stats-buttons {
    max-width: none;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .software-stats-buttons {
    flex-direction: column;
    gap: 12px;
  }
  
  .stats-button {
    min-width: auto;
    max-width: none;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-section {
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
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
  font-size: 14px;
  font-weight: 600;
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

.expand-btn {
  padding: 4px 8px;
  font-size: 12px;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: transform 0.3s;
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

.advanced-filter {
  margin-top: 8px;
  margin-top: 12px;
  animation: fadeIn 0.3s ease;
}

.table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.table-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.asset-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.asset-name {
  font-weight: 500;
  color: #262626;
  font-size: 14px;
}

.asset-detail {
  font-size: 12px;
  color: #8c8c8c;
}

.action-btn {
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f0f0f0;
}

.batch-actions {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 6px;
}

.batch-actions .ant-alert {
  margin: 0;
  border-radius: 6px;
}

:deep(.asset-table) {
  .ant-table-thead > tr > th {
    background: #fafafa;
    font-weight: 600;
    font-size: 12px;
    color: #262626;
    border-bottom: 2px solid #e9ecef;
  }
  
  .ant-table-tbody > tr {
    transition: all 0.2s;
  }
  
  .ant-table-tbody > tr:hover > td {
    background: #f8f9fa;
  }
  
  .ant-table-row-selected > td {
    background: #e6f7ff;
  }
  
  .ant-table-row-selected:hover > td {
    background: #bae7ff;
  }
}

:deep(.ant-btn) {
  border-radius: 6px;
  font-weight: 500;
}

:deep(.ant-input) {
  border-radius: 6px;
}

:deep(.ant-select .ant-select-selector) {
  border-radius: 6px;
}

:deep(.ant-tag) {
  border-radius: 4px;
  font-weight: 500;
}

:deep(.ant-divider) {
  margin: 12px 0;
  font-size: 12px;
  color: #8c8c8c;
}
</style>