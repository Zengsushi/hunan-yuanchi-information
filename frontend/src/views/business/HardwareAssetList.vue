<template>
  <div class="hardware-asset-list-container">
    <!-- 设备内容区域 -->
    <div class="device-content">
        <!-- 在用设备表格 -->
        <div class="content-container">
          <HardwareAssetTable
            :dataSource="currentFilter === 'scrapped' ? scrappedAssets : activeAssets"
            :loading="loading"
            :pagination="activePagination"
            :selectedRowKeys="selectedRowKeys"
            :searchKeyword="searchKeyword"
            :assetStatus="assetStatus"
            :assetType="assetType"
            :totalCount="totalCount"
            :activeCount="activeCount"
            :maintenanceCount="0"
            :retiredCount="0"
            :scrappedCount="scrappedCount"
            :tableMode="currentFilter"
            :currentFilter="currentFilter"
            @select-change="onSelectChange"
            @select-all="onSelectAll"
            @table-change="handleActiveTableChange"
            @view="handleView"
            @edit="handleEdit"
            @delete="handleDelete"
            @check-warranty="handleCheckWarranty"
            @toggle-monitoring="handleToggleMonitoring"
            @batch-delete="handleBatchDelete"
            @batch-toggle-monitoring="handleBatchToggleMonitoring"
            @clear-selection="clearSelection"
            @add="handleAdd"
            @export="handleExport"
            @import="handleImport"
            @search="handleSearch"
            @reset="handleReset"
            @search-input="handleSearchInput"
            @status-change="handleStatusChange"
            @type-change="handleTypeChange"
            @view-history="handleViewHistory"
            @stats-filter="handleStatsFilter"
            :batchDeleting="batchDeleting"
            :batchMonitoringToggling="batchMonitoringToggling"
          />
        </div>
      </div>
    </div>

    <!-- 监控操作组件 -->
    <MonitoringActions
      :selectedAsset="selectedAsset"
      :detailModalVisible="detailModalVisible"
      :warrantyModalVisible="warrantyModalVisible"
      :batchWarrantyState="batchWarrantyState"
      :taskResultModalVisible="taskResultModalVisible"
      :warrantyFormData="warrantyFormData"
      :warrantyRules="warrantyRules"
      :selectedTask="selectedTask"
      :taskResults="taskResults"
      :resultLoading="resultLoading"
      :resultColumns="resultColumns"
      @close-detail-modal="detailModalVisible = false"
      @close-warranty-modal="handleWarrantyCancel"
      @warranty-confirm="handleWarrantyConfirm"
      @close-batch-warranty="closeBatchWarrantyModal"
      @start-batch-warranty="startBatchWarrantyCheck"
      @close-task-result="taskResultModalVisible = false"
    />

    <!-- 模板选择抽屉组件 -->
    <TemplateDrawer 
      v-model:visible="templateDrawerVisible"
      v-model:selectedTemplateIds="selectedTemplateIds"
      :loading="templateLoading"
      :selectedAsset="selectedAsset"
      @confirm="handleCreateMonitoring"
    />
    <!-- 资产详情弹窗 -->
    <HardwareAssetForm
      ref="assetFormRef"
      v-model:visible="formDialogVisible"
      :selectedAsset="selectedAsset"
      :assetTypes="assetTypeOptions"
      :statusOptions="assetStatusOptions"
      @close="formDialogVisible = false"
      @submit="handleSubmit"
    />

    <!-- 历史记录弹窗 -->
    <a-modal
      v-model:open="historyModalVisible"
      title="更新历史记录"
      width="1200px"
      :footer="null"
      @cancel="historyModalVisible = false"
    >
      <a-tabs v-model:activeKey="historyActiveTab">
        <a-tab-pane tab="规格参数更新记录" key="spec">
          <div class="history-section">
            <div class="history-header">
              <h4>规格参数更新记录</h4>
              <a-button type="primary" size="small" @click="loadSpecHistory">
                刷新记录
              </a-button>
            </div>
            
            <a-table
              :data-source="specHistory"
              :columns="specHistoryColumns"
              bordered
              :loading="specHistoryLoading"
              :pagination="false"
              :locale="{ emptyText: '暂无更新记录' }"
            />
          </div>
        </a-tab-pane>
        
        <a-tab-pane tab="保修更新记录" key="warranty">
          <div class="history-section">
            <div class="history-header">
              <h4>保修更新记录</h4>
              <a-button type="primary" size="small" @click="loadWarrantyHistory">
                刷新记录
              </a-button>
            </div>
            
            <a-table
              :data-source="warrantyHistory"
              :columns="warrantyHistoryColumns"
              bordered
              :loading="warrantyHistoryLoading"
              :pagination="false"
              :locale="{ emptyText: '暂无更新记录' }"
            />
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-modal>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, onBeforeUnmount, nextTick, h, createVNode } from 'vue';
import { useRouter } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import hardwareAssetApi from '@/api/hardwareAsset';
import { suppressResizeObserverError } from '@/utils/errorHandler';
import * as Vue from 'vue';
import * as antdvIcons from '@ant-design/icons-vue';
import HardwareAssetForm from '@/components/business/HardwareAssetForm.vue';

// 导入拆分的组件
import HardwareAssetTable from '@/components/business/HardwareAssetTable.vue';
import MonitoringActions from '@/components/business/MonitoringActions.vue';
import TemplateDrawer from '@/components/business/TemplateDrawer.vue';
import { 
  ExclamationCircleOutlined,
} from '@ant-design/icons-vue';

// 路由实例
const router = useRouter();

// 搜索条件
const searchKeyword = ref('');
const assetStatus = ref([]);
const assetType = ref('');
const formDialogVisible = ref(false);

// 资产类型选项
const assetTypeOptions = ref([
  { label: '服务器', value: 'server' },
  { label: '网络设备', value: 'network' },
  { label: '存储设备', value: 'storage' },
  { label: '安全设备', value: 'security' }
]);

// 资产状态选项
const assetStatusOptions = ref([
  { label: '在用', value: 'active' },
  { label: '维护中', value: 'maintenance' },
  { label: '已退役', value: 'retired' },
  { label: '预留', value: 'reserved' }
]);

// 硬件资产数据状态 - 确保始终是数组
const assetData = ref([]);
const loading = ref(false);

// 批量操作相关状态
const selectedRowKeys = ref([]);
const batchDeleting = ref(false);
const batchMonitoringToggling = ref(false);

// 模板选择抽屉相关状态
const templateDrawerVisible = ref(false);
const zabbixTemplates = ref([]);
const selectedTemplateIds = ref([]);
const templateLoading = ref(false);
const templateSearchKeyword = ref('');
const monitoringCreating = ref(false);
const selectedCategory = ref(''); // 当前选中的分类
const expandedCategories = ref({}); // 展开的分类

// 历史记录相关状态
const historyModalVisible = ref(false);
const historyActiveTab = ref('spec');
const currentHistoryAsset = ref(null);
const specHistory = ref([]);
const warrantyHistory = ref([]);
const specHistoryLoading = ref(false);
const warrantyHistoryLoading = ref(false);

// 历史记录表格列配置
const specHistoryColumns = [
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    width: 180,
    customRender: ({ text }) => {
      return text ? new Date(text).toLocaleString() : '-';
    }
  },
  {
    title: '更新方式',
    dataIndex: 'update_method',
    key: 'update_method',
    width: 100,
    customRender: ({ text }) => {
      return text === 'manual' ? '手动' : '自动';
    }
  },
  {
    title: '更新前规格参数',
    dataIndex: 'old_specifications',
    key: 'old_specifications',
    minWidth: 200,
    customRender: ({ text }) => {
      return text ? JSON.stringify(text, null, 2) : '-';
    }
  },
  {
    title: '更新后规格参数',
    dataIndex: 'new_specifications',
    key: 'new_specifications',
    minWidth: 200,
    customRender: ({ text }) => {
      return text ? JSON.stringify(text, null, 2) : '-';
    }
  },
  {
    title: '更新人',
    dataIndex: 'updated_by',
    key: 'updated_by',
    width: 120
  },
  {
    title: '备注',
    dataIndex: 'remarks',
    key: 'remarks',
    width: 150
  }
];

const warrantyHistoryColumns = [
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    width: 180,
    customRender: ({ text }) => {
      return text ? new Date(text).toLocaleString() : '-';
    }
  },
  {
    title: '更新前保修类型',
    dataIndex: 'old_warranty_type',
    key: 'old_warranty_type',
    width: 120,
    customRender: ({ text }) => {
      return text === 'original' ? '原厂保修' : '第三方保修';
    }
  },
  {
    title: '更新后保修类型',
    dataIndex: 'new_warranty_type',
    key: 'new_warranty_type',
    width: 120,
    customRender: ({ text }) => {
      return text === 'original' ? '原厂保修' : '第三方保修';
    }
  },
  {
    title: '更新前保修期',
    key: 'old_warranty_period',
    width: 200,
    customRender: ({ record }) => {
      return `${record.old_warranty_start_date} ~ ${record.old_warranty_end_date}`;
    }
  },
  {
    title: '更新后保修期',
    key: 'new_warranty_period',
    width: 200,
    customRender: ({ record }) => {
      return `${record.new_warranty_start_date} ~ ${record.new_warranty_end_date}`;
    }
  },
  {
    title: '更新人',
    dataIndex: 'updated_by',
    key: 'updated_by',
    width: 120
  },
  {
    title: '备注',
    dataIndex: 'remarks',
    key: 'remarks',
    width: 150
  }
];

// 防御性检查，确保assetData始终是数组
const setAssetData = (data) => {
  if (Array.isArray(data)) {
    // 为每个硬件资产记录设置保护状态信息
    const processedData = data.map(asset => {
      // 确保保护状态字段存在
      if (asset.is_protected === undefined) {
        asset.is_protected = asset.is_auto_discovered || false;
      }
      
      // 设置保护原因
      if (!asset.protection_reason && asset.is_auto_discovered) {
        asset.protection_reason = '自动发现的硬件资产';
      }
      
      // 设置可编辑字段列表
      if (asset.is_auto_discovered) {
        asset.editable_fields = ['description', 'status'];
      } else {
        asset.editable_fields = 'all';
      }
      
      return asset;
    });
    
    assetData.value = processedData;
  } else {
    console.warn('尝试设置非数组数据到assetData:', data);
    assetData.value = [];
  }
};

// 统计计算属性 - 添加防御性检查
const activeCount = computed(() => {
  if (!Array.isArray(assetData.value)) {
    console.warn('assetData不是数组，返回0');
    return 0;
  }
  return assetData.value.filter(asset => asset.asset_status === 'active').length;
});

const maintenanceCount = computed(() => {
  if (!Array.isArray(assetData.value)) {
    console.warn('assetData不是数组，返回0');
    return 0;
  }
  return assetData.value.filter(asset => asset.asset_status === 'maintenance').length;
});

const retiredCount = computed(() => {
  if (!Array.isArray(assetData.value)) {
    console.warn('assetData不是数组，返回0');
    return 0;
  }
  return assetData.value.filter(asset => asset.asset_status === 'retired').length;
});

// 统计对象
const statistics = computed(() => ({
  total: assetData.value.length || 0,
  active: activeCount.value,
  maintenance: maintenanceCount.value,
  retired: retiredCount.value
}));

// 计算属性：分离在用和报废设备
const inUseAssets = computed(() => {
  return assetData.value.filter(asset => asset.asset_status === 'in_use');
});

const scrappedAssets = computed(() => {
  return assetData.value.filter(asset => asset.asset_status === 'scrapped');
});

// 计算属性：统计数据
const totalCount = computed(() => assetData.value.length);
const inUseCount = computed(() => inUseAssets.value.length);
const scrappedCount = computed(() => scrappedAssets.value.length);

// 计算属性：按状态分离设备
const activeAssets = computed(() => {
  return assetData.value.filter(asset => asset.asset_status === 'active' || asset.asset_status === 'in_use');
});

// 统计按钮过滤状态
const currentFilter = ref('active');

// 计算属性 - 保修相关
const needsWarrantyCheck = computed(() => {
  const type = warrantyFormData.checkType;
  return type === 'auto' || type === 'manual';
});

// 工具函数
const getStatusText = (status) => {
  const textMap = {
    'active': '在用',
    'maintenance': '维护中',
    'retired': '已退役',
    'reserved': '预留'
  };
  return textMap[status] || status;
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

const formatDate = (date) => {
  if (!date) return null;
  return new Date(date).toLocaleString('zh-CN');
};

// 弹窗状态
const detailModalVisible = ref(false);
const editModalVisible = ref(false);
const warrantyModalVisible = ref(false);
const taskDetailModalVisible = ref(false);
const taskResultModalVisible = ref(false);
const selectedAsset = ref(null);
const editingAsset = ref(null);
const selectedTask = ref(null);

// 保修查询相关
const warrantyTasks = ref([]);
const taskResults = ref([]);
const taskLoading = ref(false);
const resultLoading = ref(false);
const taskStatusFilter = ref('');
const taskDateRange = ref([]);
const taskNameFilter = ref('');
const taskPagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
});

// 表单相关
const formRef = ref();
const warrantyFormRef = ref();
const formData = reactive({
  assetTag: '',
  assetName: '',
  status: 'active',
  type: 'server',
  brand: '',
  model: '',
  serialNumber: '',
  location: '',
  description: ''
});

// 保修配置数据
const warrantyFormData = reactive({
  checkType: 'auto', // 默认自动检查
  warrantyPeriod: 36, // 保修期（月）
  purchaseDate: null,
  warrantyStartDate: null,
  warrantyEndDate: null,
  supplierInfo: {
    name: '',
    contact: '',
    phone: '',
    email: ''
  }
});

// 表单验证规则
const rules = {
  assetTag: [
    { required: true, message: '请输入资产标签' },
    { pattern: /^[A-Za-z0-9-_]+$/, message: '资产标签只能包含字母、数字、横线和下划线' }
  ],
  assetName: [{ required: true, message: '请输入资产名称' }],
  status: [{ required: true, message: '请选择资产状态' }],
  type: [{ required: true, message: '请选择资产类型' }]
};

// 保修配置验证规则
const warrantyRules = {
  checkType: [{ required: true, message: '请选择检查类型' }],
  warrantyPeriod: [
    { type: 'number', min: 1, max: 120, message: '保修期必须在1-120个月之间' }
  ],
  purchaseDate: [{ required: true, message: '请选择采购日期' }]
};

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  pageSizeOptions: ['10', '20', '50', '100'],
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`,
});

// 在用设备分页配置
const inUsePagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
});

// 报废设备分页配置
const scrappedPagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
});

// 正常设备分页配置
const activePagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
});



// 加载硬件资产列表数据
const loadAssetList = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    };
    
    // 添加搜索条件
    if (searchKeyword.value && searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }
    if (assetStatus.value) {
      params.status = assetStatus.value;
    }
    if (assetType.value) {
      params.type = assetType.value;
    }
    
    console.log('正在获取硬件资产列表，参数:', params);
    console.log('当前分页状态:', {
      current: pagination.current,
      pageSize: pagination.pageSize,
      total: pagination.total
    });
    
    const response = await hardwareAssetApi.getList(params);
    
    console.log('API响应:', response);
    
    if (response && response.data) {
      // 检查是否是统一响应格式（包含code字段）
      if (response.data.code !== undefined) {
        // 统一响应格式
        if (response.data.code === 200) {
          const data = response.data.data;
          // 确保获取的数据是数组
          let resultData = [];
          if (data && data.results && Array.isArray(data.results)) {
            resultData = data.results;
          } else if (Array.isArray(data)) {
            resultData = data;
          } else {
            console.warn('API返回的数据不是数组格式:', data);
            resultData = [];
          }
          
          setAssetData(resultData);
          pagination.total = data.count || data.total || resultData.length;
          // 更新各表格的分页总数
          inUsePagination.total = inUseCount.value;
          scrappedPagination.total = scrappedCount.value;
          console.log('成功获取硬件资产列表（统一格式）:', assetData.value);
          message.success('硬件资产列表数据已更新', 1);
        } else {
          console.error('API返回错误代码:', response.data.code, '错误信息:', response.data.message);
          message.error(`获取硬件资产列表失败: ${response.data.message}`);
          setAssetData([]);
          pagination.total = 0;
        }
      } else {
        // DRF标准响应格式（直接包含count、results字段）
        console.log('检测到DRF标准响应格式');
        // 确保获取的数据是数组
        let resultData = [];
        if (response.data.results && Array.isArray(response.data.results)) {
          resultData = response.data.results;
        } else if (Array.isArray(response.data)) {
          resultData = response.data;
        } else {
          console.warn('API返回的数据不是数组格式:', response.data);
          resultData = [];
        }
        
        setAssetData(resultData);
        pagination.total = response.data.count || response.data.total || resultData.length;
        // 更新各表格的分页总数
        inUsePagination.total = inUseCount.value;
        scrappedPagination.total = scrappedCount.value;
        console.log('成功获取硬件资产列表（DRF格式）:', assetData.value);
        message.success('硬件资产列表数据已更新', 1);
      }
    } else {
      console.error('无效的API响应:', response);
      message.error('获取硬件资产列表失败: 无效的响应数据');
      setAssetData([]);
      pagination.total = 0;
    }
  } catch (error) {
    console.error('加载硬件资产列表失败:', error);
    console.error('错误详情:', {
      message: error.message,
      response: error.response,
      request: error.request
    });
    
    let errorMessage = '获取硬件资产列表失败';
    if (error.response) {
      // 服务器响应错误
      errorMessage += `: HTTP ${error.response.status}`;
      if (error.response.data && error.response.data.message) {
        errorMessage += ` - ${error.response.data.message}`;
      }
    } else if (error.request) {
      // 请求发送但无响应
      errorMessage += ': 网络连接失败或服务器无响应';
    } else {
      // 请求设置错误
      errorMessage += `: ${error.message}`;
    }
    
    message.error(errorMessage);
    
    // 如果API调用失败，显示空数据
    setAssetData([]);
    pagination.total = 0;
  } finally {
    loading.value = false;
  }
};

const columns = [
  {
    title: '资产标签',
    dataIndex: 'asset_tag',
    key: 'assetTag',
    width: 120,
    fixed: 'left'
  },
  {
    title: '资产名称',
    dataIndex: 'asset_name',
    key: 'assetName',
    width: 150
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 80
  },
  {
    title: '类型',
    dataIndex: 'type',
    key: 'type',
    width: 100
  },
  {
    title: '品牌',
    dataIndex: 'brand',
    key: 'brand',
    width: 100
  },
  {
    title: '型号',
    dataIndex: 'model',
    key: 'model',
    width: 120
  },
  {
    title: '序列号',
    dataIndex: 'serial_number',
    key: 'serialNumber',
    width: 150
  },
  {
    title: '位置',
    dataIndex: 'location',
    key: 'location',
    width: 120
  },
  {
    title: '保修状态',
    dataIndex: 'warranty_status',
    key: 'warrantyStatus',
    width: 100
  },
  {
    title: '最后更新',
    dataIndex: 'updated_at',
    key: 'updatedAt',
    width: 160
  },
  {
    title: '操作',
    key: 'operation',
    fixed: 'right',
    width: 280
  }
];

// 保修结果表格列定义
const resultColumns = [
  {
    title: '资产标签',
    dataIndex: 'asset_tag',
    key: 'asset_tag',
    width: 120,
  },
  {
    title: '资产名称',
    dataIndex: 'asset_name',
    key: 'asset_name',
    ellipsis: true
  },
  {
    title: '保修状态',
    dataIndex: 'warranty_status',
    key: 'warranty_status'
  },
  {
    title: '保修到期日',
    dataIndex: 'warranty_end_date',
    key: 'warranty_end_date'
  },
  {
    title: '检查时间',
    dataIndex: 'created_at',
    key: 'created_at'
  }
];

// 事件处理函数
// 批量保修检查状态管理
const batchWarrantyState = reactive({
  isVisible: false,
  phase: 'confirm', // confirm, checking, result
  stats: {
    total: 0,
    currentValid: 0,
    currentExpired: 0,
    testResult: null
  },
  checking: {
    progress: 0,
    currentAsset: '',
    startTime: null
  }
});

const handleBatchWarrantyCheck = async () => {
  try {
    // 获取当前页面的所有资产ID
    const allAssetIds = assetData.value.map(asset => asset.id).filter(id => id);
    
    if (allAssetIds.length === 0) {
      message.warning('没有可以检查保修的资产记录');
      return;
    }
    
    // 初始化状态
    batchWarrantyState.stats.total = allAssetIds.length;
    batchWarrantyState.stats.currentValid = assetData.value.filter(asset => asset.warranty_status === 'valid').length;
    batchWarrantyState.stats.currentExpired = allAssetIds.length - batchWarrantyState.stats.currentValid;
    batchWarrantyState.phase = 'confirm';
    batchWarrantyState.isVisible = true;
    
  } catch (error) {
    console.error('初始化批量保修检查失败:', error);
    message.error('初始化批量保修检查失败');
  }
};

// 开始保修检查
const startBatchWarrantyCheck = async () => {
  try {
    const allAssetIds = assetData.value.map(asset => asset.id).filter(id => id);
    
    // 切换到检查阶段
    batchWarrantyState.phase = 'checking';
    batchWarrantyState.checking.startTime = new Date();
    batchWarrantyState.checking.progress = 0;
    
    loading.value = true;
    
    // 调用批量保修检查API
    const response = await hardwareAssetApi.batchCheckWarranty(allAssetIds);
    
    if (response.data && response.data.code === 200) {
      const batchData = response.data.data;
      const summary = batchData.summary;
      
      // 更新本地数据
      const resultsMap = new Map();
      batchData.results.forEach(result => {
        resultsMap.set(result.asset_id, result);
      });
      
      // 更新assetData中的记录
      assetData.value.forEach(asset => {
        const result = resultsMap.get(asset.id);
        if (result) {
          asset.warranty_status = result.status;
          asset.warranty_end_date = result.warranty_end_date;
          asset.updated_at = new Date().toISOString();
        }
      });
      
      // 设置检查结果并切换到结果阶段
      batchWarrantyState.stats.testResult = summary;
      batchWarrantyState.phase = 'result';
      
    } else {
      message.error(`批量保修检查失败: ${response.data?.message || '未知错误'}`);
      batchWarrantyState.isVisible = false;
    }
  } catch (error) {
    console.error('批量保修检查失败:', error);
    let errorMessage = '批量保修检查失败';
    if (error.response && error.response.data) {
      errorMessage += `: ${error.response.data.message || error.response.data.error || '网络错误'}`;
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    message.error(errorMessage);
    batchWarrantyState.isVisible = false;
  } finally {
    loading.value = false;
  }
};

// 关闭批量保修检查弹窗
const closeBatchWarrantyModal = () => {
  batchWarrantyState.isVisible = false;
  batchWarrantyState.phase = 'confirm';
  batchWarrantyState.stats.testResult = null;
  batchWarrantyState.checking.progress = 0;
};

// 行选择管理
const onSelectChange = (newSelectedRowKeys) => {
  console.log('选中的行 keys:', newSelectedRowKeys);
  selectedRowKeys.value = newSelectedRowKeys;
};

const onSelectAll = (selected, selectedRows, changeRows) => {
  console.log('全选/反选:', { selected, selectedRows: selectedRows.length, changeRows: changeRows.length });
};

const clearSelection = () => {
  selectedRowKeys.value = [];
};

// 批量删除
const handleBatchDelete = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要删除的硬件资产');
    return;
  }

  try {
    Modal.confirm({
      title: '批量删除确认',
      content: `您将删除 ${selectedRowKeys.value.length} 个硬件资产，此操作不可恢复！`,
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        batchDeleting.value = true;
        try {
          const response = await hardwareAssetApi.batchDeleteAssets(selectedRowKeys.value);
          
          if (response.data && response.data.code === 200) {
            const result = response.data.data;
            message.success(`批量删除成功！删除: ${result.deleted_count} 个，失败: ${result.failed_count} 个`, 1);
            
            // 清空选中状态
            clearSelection();
            
            // 刷新列表
            await loadAssetList();
          } else {
            message.error(`批量删除失败: ${response.data?.message || '未知错误'}`);
          }
        } catch (error) {
          console.error('批量删除失败:', error);
          message.error(`批量删除失败: ${error.message}`);
        } finally {
          batchDeleting.value = false;
        }
      }
    });
  } catch (error) {
    console.error('批量删除操作失败:', error);
    message.error('批量删除操作失败');
  }
};

// 批量切换监控状态
const handleBatchToggleMonitoring = async (enableMonitoring) => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要操作的硬件资产');
    return;
  }

  const actionText = enableMonitoring ? '启用监控' : '禁用监控';
  
  try {
    Modal.confirm({
      title: `批量${actionText}`,
      content: `您将对 ${selectedRowKeys.value.length} 个硬件资产${actionText}，是否继续？`,
      okText: `确认${actionText}`,
      cancelText: '取消',
      onOk: async () => {
        batchMonitoringToggling.value = true;
        try {
          const response = await hardwareAssetApi.batchToggleMonitoring(selectedRowKeys.value, enableMonitoring);
          
          if (response.data && response.data.code === 200) {
            const result = response.data.data;
            message.success(`批量${actionText}成功！成功: ${result.success_count} 个，失败: ${result.failed_count} 个`, 1);
            
            // 更新本地数据
            assetData.value.forEach(asset => {
              if (selectedRowKeys.value.includes(asset.id)) {
                asset.monitoring_enabled = enableMonitoring;
              }
            });
            
            // 清空选中状态
            clearSelection();
          } else {
            message.error(`批量${actionText}失败: ${response.data?.message || '未知错误'}`);
          }
        } catch (error) {
          console.error(`批量${actionText}失败:`, error);
          message.error(`批量${actionText}失败: ${error.message}`);
        } finally {
          batchMonitoringToggling.value = false;
        }
      }
    });
  } catch (error) {
    console.error(`批量${actionText}操作失败:`, error);
    message.error(`批量${actionText}操作失败`);
  }
};

// 单个监控状态切换
const handleToggleMonitoring = async (record, enableMonitoring) => {
  if (enableMonitoring) {
    // 启用监控时显示模板选择抽屉
    selectedAsset.value = record;
    await loadZabbixTemplates(record.id);
    templateDrawerVisible.value = true;
  } else {
    // 直接禁用监控
    await toggleMonitoringStatus(record, false);
  }
};

// 切换监控状态的实际方法
const toggleMonitoringStatus = async (record, enableMonitoring) => {
  const actionText = enableMonitoring ? '启用监控' : '禁用监控';
  
  // 设置单个记录的加载状态
  record.monitoringToggling = true;
  
  try {
    const response = await hardwareAssetApi.toggleMonitoring(record.id, enableMonitoring);
    
    if (response.data && response.data.code === 200) {
      // 更新本地数据
      record.monitoring_enabled = enableMonitoring;
      message.success(`${record.asset_name || record.asset_tag} ${actionText}成功`, 1);
    } else {
      message.error(`${actionText}失败: ${response.data?.message || '未知错误'}`);
    }
  } catch (error) {
    console.error(`${actionText}失败:`, error);
    message.error(`${actionText}失败: ${error.message}`);
  } finally {
    record.monitoringToggling = false;
  }
};

// 加载Zabbix模板列表
const loadZabbixTemplates = async (assetId) => {
  templateLoading.value = true;
  try {
    const response = await hardwareAssetApi.getZabbixTemplates(assetId, templateSearchKeyword.value);
    
    if (response.data && response.data.code === 200) {
      zabbixTemplates.value = response.data.data.templates || [];
      
      // 初始化展开状态，默认展开所有分类
      nextTick(() => {
        try {
          const categories = Object.keys(groupedTemplates.value || {});
          categories.forEach(category => {
            const categoryStr = String(category);
            expandedCategories.value[categoryStr] = true;
          });
        } catch (error) {
          console.warn('初始化展开状态错误:', error);
        }
      });
      
      console.log('成功加载模板列表:', zabbixTemplates.value.length, '个模板');
    } else {
      message.error(`加载模板列表失败: ${response.data?.message || '未知错误'}`);
      zabbixTemplates.value = [];
    }
  } catch (error) {
    console.error('加载模板列表失败:', error);
    message.error(`加载模板列表失败: ${error.message}`);
    zabbixTemplates.value = [];
  } finally {
    templateLoading.value = false;
  }
};

// 创建监控主机
const handleCreateMonitoring = async () => {
  if (!selectedAsset.value) {
    message.error('请先选择硬件资产');
    return;
  }
  
  if (selectedTemplateIds.value.length === 0) {
    message.error('请选择至少一个监控模板');
    return;
  }
  
  monitoringCreating.value = true;
  
  try {
    const monitoringData = {
      template_ids: selectedTemplateIds.value,
      host_name: selectedAsset.value.asset_name || selectedAsset.value.asset_tag,
      group_ids: []
    };
    
    const response = await hardwareAssetApi.createMonitoring(selectedAsset.value.id, monitoringData);
    
    if (response.data && response.data.code === 200) {
      const result = response.data.data;
      
      message.success({
        content: `监控主机创建成功！\n主机名: ${result.host_name}\n资产: ${result.asset_tag}\n模板数量: ${result.template_count}`,
        duration: 5
      });
      
      // 更新本地资产记录的监控状态
      selectedAsset.value.monitoring_enabled = true;
      
      // 关闭抽屉
      templateDrawerVisible.value = false;
      
      // 清空选中的模板
      selectedTemplateIds.value = [];
      
    } else {
      message.error(`创建监控主机失败: ${response.data?.message || '未知错误'}`);
    }
  } catch (error) {
    console.error('创建监控主机失败:', error);
    message.error(`创建监控主机失败: ${error.message}`);
  } finally {
    monitoringCreating.value = false;
  }
};

// 关闭模板抽屉
const handleCloseTemplateDrawer = () => {
  templateDrawerVisible.value = false;
  selectedTemplateIds.value = [];
  templateSearchKeyword.value = '';
  selectedCategory.value = '';
  expandedCategories.value = {};
  selectedAsset.value = null;
};

// 按分类组织模板
const groupedTemplates = computed(() => {
  const groups = {};
  
  try {
    if (!Array.isArray(zabbixTemplates.value)) {
      console.warn('zabbixTemplates不是数组:', zabbixTemplates.value);
      return groups;
    }
    
    zabbixTemplates.value.forEach((template) => {
      if (!template || typeof template !== 'object') {
        return;
      }
      
      const category = template.category || '📝 其他';
      if (!groups[category]) {
        groups[category] = [];
      }
      
      groups[category].push(template);
    });
    
    // 对每个分类的模板按名称排序
    Object.keys(groups).forEach(category => {
      try {
        groups[category].sort((a, b) => {
          const nameA = a.name || '';
          const nameB = b.name || '';
          return nameA.localeCompare(nameB);
        });
      } catch (sortError) {
        console.warn(`排序分类${category}时出错:`, sortError);
      }
    });
  } catch (error) {
    console.error('groupedTemplates计算出错:', error);
  }
  
  return groups;
});

const handleSearch = async () => {
  pagination.current = 1;
  await loadAssetList();
};

const handleReset = async () => {
  searchKeyword.value = '';
  assetStatus.value = [];
  assetType.value = '';
  pagination.current = 1;
  await loadAssetList();
};

const handleSearchInput = (value) => {
  searchKeyword.value = value;
};

const handleStatusChange = (value) => {
  assetStatus.value = value;
};

const handleTypeChange = (value) => {
  assetType.value = value;
};

// 处理统计按钮点击事件
const handleStatsFilter = (filterType) => {
  currentFilter.value = filterType;
  console.log('统计按钮点击:', filterType);
  
  // 根据点击的统计按钮类型进行相应的过滤或操作
  switch (filterType) {
    case 'total':
      // 显示所有设备
      assetStatus.value = [];
      break;
    case 'active':
      // 显示在用设备
      assetStatus.value = ['active'];
      break;
    case 'available':
      // 显示可用设备（这里可以根据实际业务逻辑调整）
      assetStatus.value = ['reserved'];
      break;
    case 'scrapped':
      // 显示报废设备
      assetStatus.value = ['scrapped'];
      break;
    case 'warranty':
      // 显示保修中的设备（这里可以根据实际业务逻辑调整）
      // 可以添加特定的过滤逻辑
      break;
    default:
      break;
  }
  
  // 更新当前过滤器状态
  currentFilter.value = filterType;
  
  // 重新加载数据
  pagination.current = 1;
  loadAssetList();
};

// 查看历史记录
const handleViewHistory = (record) => {
  currentHistoryAsset.value = record;
  historyModalVisible.value = true;
  historyActiveTab.value = 'spec';
  // 自动加载规格参数历史
  loadSpecHistory();
};

// 加载规格参数更新历史
const loadSpecHistory = async () => {
  if (!currentHistoryAsset.value) return;
  
  specHistoryLoading.value = true;
  try {
    const response = await hardwareAssetApi.getSpecHistory(currentHistoryAsset.value.id);
    if (response.data && response.data.code === 200) {
      specHistory.value = response.data.data || [];
    } else {
      message.error('加载规格参数历史失败');
      specHistory.value = [];
    }
  } catch (error) {
    console.error('加载规格参数历史失败:', error);
    message.error('加载规格参数历史失败');
    specHistory.value = [];
  } finally {
    specHistoryLoading.value = false;
  }
};

// 加载保修更新历史
const loadWarrantyHistory = async () => {
  if (!currentHistoryAsset.value) return;
  
  warrantyHistoryLoading.value = true;
  try {
    const response = await hardwareAssetApi.getWarrantyHistory(currentHistoryAsset.value.id);
    if (response.data && response.data.code === 200) {
      warrantyHistory.value = response.data.data || [];
    } else {
      message.error('加载保修历史失败');
      warrantyHistory.value = [];
    }
  } catch (error) {
    console.error('加载保修历史失败:', error);
    message.error('加载保修历史失败');
    warrantyHistory.value = [];
  } finally {
    warrantyHistoryLoading.value = false;
  }
};

// 历史记录标签页切换
const handleHistoryTabChange = (activeKey) => {
  historyActiveTab.value = activeKey;
  if (activeKey === 'warranty' && warrantyHistory.value.length === 0) {
    loadWarrantyHistory();
  }
};

// 关闭历史记录弹窗
const handleHistoryModalClose = () => {
  historyModalVisible.value = false;
  currentHistoryAsset.value = null;
  specHistory.value = [];
  warrantyHistory.value = [];
  historyActiveTab.value = 'spec';
};

const handleTableChange = async (paginationInfo, filters, sorter) => {
  console.log('handleTableChange 被调用:', {
    paginationInfo, 
    当前分页状态: {
      current: pagination.current,
      pageSize: pagination.pageSize
    }
  });
  
  pagination.current = paginationInfo.current;
  pagination.pageSize = paginationInfo.pageSize;
  
  console.log('更新后的分页状态:', {
    current: pagination.current,
    pageSize: pagination.pageSize
  });
  
  // 更新 URL 参数
  const currentUrl = new URL(window.location);
  currentUrl.searchParams.set('page', pagination.current.toString());
  currentUrl.searchParams.set('page_size', pagination.pageSize.toString());
  window.history.replaceState({}, '', currentUrl.toString());
  console.log('已更新 URL:', currentUrl.toString());
  
  await loadAssetList();
};

// 在用设备表格变化处理
const handleActiveTableChange = async (paginationInfo, filters, sorter) => {
  activePagination.current = paginationInfo.current;
  activePagination.pageSize = paginationInfo.pageSize;
  // 更新查询参数
  pagination.current = paginationInfo.current;
  pagination.pageSize = paginationInfo.pageSize;
  await loadAssetList();
};

const handleView = (record) => {
  selectedAsset.value = record;
  detailModalVisible.value = true;
};

const handleEdit = (record) => {
  // 检查资产是否受保护
  if (record.is_protected || record.is_auto_discovered) {
    message.warning({
      content: `不能编辑此硬件资产：${record.asset_name || record.asset_tag}\n原因：${record.protection_reason || '自动发现的硬件资产不允许编辑'}\n可编辑字段：${Array.isArray(record.editable_fields) ? record.editable_fields.join(', ') : '备注、状态'}`,
      duration: 5
    });
    return;
  }
  
  editingAsset.value = record;
  Object.assign(formData, record);
  editModalVisible.value = true;
};

const handleDelete = async (record) => {
  try {
    Modal.confirm({
      title: '确认删除硬件资产',
      content: `确定要删除硬件资产 "${record.asset_name || record.asset_tag}" 吗？\n\n警告：此操作将删除资产记录及所有相关数据（包括保修记录、监控数据等），该操作不可恢复！`,
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        const deleteMessage = message.loading('正在删除硬件资产及相关数据...', 0);
        
        try {
          const response = await hardwareAssetApi.deleteAsset(record.id);
          deleteMessage();
          
          if (response.data && response.data.code === 200) {
            const cleanupData = response.data.data;
            
            let successMessage = `硬件资产 "${cleanupData.asset_name || cleanupData.asset_tag}" 已成功删除`;
            
            const cleanupDetails = [];
            if (cleanupData.warranty_records_deleted > 0) {
              cleanupDetails.push(`保修记录: ${cleanupData.warranty_records_deleted}条`);
            }
            if (cleanupData.monitoring_cleanup && cleanupData.monitoring_cleanup.success) {
              cleanupDetails.push('监控数据: 已清理');
            }
            
            if (cleanupDetails.length > 0) {
              successMessage += `\n同时清理了：${cleanupDetails.join('、')}`;
            }
            
            message.success({
              content: successMessage,
              duration: 6
            });
            
            // 直接从列表中移除已删除的资产
            assetData.value = assetData.value.filter(asset => asset.id !== record.id);
            pagination.total = assetData.value.length;
          } else {
            message.error('删除硬件资产失败');
          }
        } catch (deleteError) {
          deleteMessage();
          throw deleteError;
        }
      }
    });
  } catch (error) {
    if (error.message !== 'User cancelled') {
      console.error('删除硬件资产失败:', error);
      message.error(`删除硬件资产失败: ${error.response?.data?.message || error.message}`);
    }
  }
};

const handleCheckWarranty = async (record) => {
  record.warrantyChecking = true;
  try {
    const response = await hardwareAssetApi.checkWarranty(record.id);
    
    if (response.data && response.data.code === 200) {
      const warrantyData = response.data.data;
      // 更新记录的保修状态
      record.warranty_status = warrantyData.status;
      record.warranty_end_date = warrantyData.warranty_end_date;
      record.updated_at = new Date().toISOString();
      
      const statusText = warrantyData.is_valid ? '有效' : '已过期';
      const endDateText = warrantyData.warranty_end_date ? ` (到期日: ${warrantyData.warranty_end_date})` : '';
      
      message.success(`保修检查 ${record.asset_name || record.asset_tag} 完成: ${statusText}${endDateText}`, 1);
    } else {
      message.error(`保修检查失败: ${response.data?.message || '未知错误'}`);
    }
  } catch (error) {
    console.error('保修检查失败:', error);
    let errorMessage = '保修检查失败';
    if (error.response && error.response.data) {
      errorMessage += `: ${error.response.data.message || error.response.data.error || '网络错误'}`;
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    message.error(errorMessage);
  } finally {
    record.warrantyChecking = false;
  }
};

const handleExport = () => {
  message.info('导出功能开发中...');
};

const handleImport = () => {
  message.info('导入功能开发中...');
};

// 处理新增设备
const handleAdd = () => {
  formDialogVisible.value = true;
};

// 处理表单提交
const handleSubmit = async (formData) => {
  try {
    const response = await hardwareAssetApi.createAsset(formData);
    
    if (response.data && response.data.code === 200) {
      message.success('硬件资产创建成功');
      formDialogVisible.value = false;
      // 刷新列表
      await loadAssetList();
    } else {
      message.error(`创建失败: ${response.data?.message || '未知错误'}`);
    }
  } catch (error) {
    console.error('创建硬件资产失败:', error);
    message.error(`创建失败: ${error.message}`);
  }
};

const handleWarrantyCancel = () => {
  warrantyModalVisible.value = false;
};

const handleWarrantyConfirm = () => {
  message.info('保修配置功能开发中...');
  warrantyModalVisible.value = false;
};

// 生命周期钩子
onMounted(async () => {
  try {
    // 抑制ResizeObserver错误
    suppressResizeObserverError();
    
    // 从URL参数恢复分页状态
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');
    const pageSize = urlParams.get('page_size');
    
    if (page && !isNaN(parseInt(page))) {
      pagination.current = parseInt(page);
    }
    if (pageSize && !isNaN(parseInt(pageSize))) {
      pagination.pageSize = parseInt(pageSize);
    }
    
    console.log('从URL恢复分页状态:', {
      current: pagination.current,
      pageSize: pagination.pageSize
    });
    
    // 加载硬件资产列表
    await loadAssetList();
  } catch (error) {
    console.error('初始化硬件资产列表失败:', error);
    message.error('初始化硬件资产列表失败');
  }
});

// 清理函数
onBeforeUnmount(() => {
  // 清理定时器或其他资源
});
</script>

<style scoped>
.hardware-asset-list-container {
  min-height: 100vh;
}

.ant-table-wrapper {
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.search-form {
  background: white;
  padding: 24px;
  border-radius: 6px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.batch-actions {
  margin-bottom: 16px;
}

.statistics-cards {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.stat-card {
  flex: 1;
  background: white;
  padding: 20px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.stat-label {
  color: #666;
  margin-top: 8px;
}

/* 标签页样式 */
.device-tabs {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  border: 1px solid #f0f0f0;
}



.device-content {
  border-radius: 12px;
  overflow: hidden;
}

.device-tabs :deep(.ant-tabs-content-holder) {
  padding: 16px;
  background: white;
}

.device-tabs :deep(.ant-tabs-tabpane) {
  padding: 0;
}

.device-tabs .ant-table-wrapper {
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.device-tabs .ant-table {
  border-radius: 8px;
}

.device-tabs .ant-table-thead > tr > th {
  background: #fafafa;
  border-bottom: 2px solid #f0f0f0;
  font-weight: 600;
}

/* 历史记录弹窗样式 */
.history-section {
  padding: 16px 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.history-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}
</style>