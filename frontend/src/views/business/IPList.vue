<template>
  <div class="ip-list-container">


    <!-- IP表格组件 -->
    <IPTable
      :dataSource="ipData"
      :loading="loading"
      :pagination="pagination"
      :selectedRowKeys="selectedRowKeys"
      :searchKeyword="searchKeyword"
      :ipStatus="ipStatus"
      :ipType="ipType"
      :totalCount="statistics.total"
      :activeCount="statistics.active"
      :availableCount="statistics.available"
      :onlineCount="statistics.online"
      @select-change="onSelectChange"
      @select-all="onSelectAll"
      @table-change="handleTableChange"
      @view="handleView"
      @edit="handleEdit"
      @delete="handleDelete"
      @ping="handlePing"
      @toggle-monitoring="handleToggleMonitoring"
      @batch-delete="handleBatchDelete"
      @batch-toggle-monitoring="handleBatchToggleMonitoring"
      @clear-selection="clearSelection"
      @add="handleAdd"
      @scan="handleScan"
      @export="handleExport"
      @header-batch-ping="handleBatchPing"
      @list-management="handleListManagement"
      @search="handleSearch"
      @reset="handleReset"
      @search-input="handleSearchInput"
      @status-change="handleStatusChange"
      @type-change="handleTypeChange"
      :batchDeleting="batchDeleting"
      :batchMonitoringToggling="batchMonitoringToggling"
    />

    <!-- 监控操作组件 -->
    <MonitoringActions
      :selectedIP="selectedIP"
      :detailModalVisible="detailModalVisible"
      :scanModalVisible="scanModalVisible"
      :batchPingState="batchPingState"
      :taskResultModalVisible="taskResultModalVisible"
      :scanFormData="scanFormData"
      :scanRules="scanRules"
      :selectedTask="selectedTask"
      :taskResults="taskResults"
      :resultLoading="resultLoading"
      :resultColumns="resultColumns"
      @close-detail-modal="detailModalVisible = false"
      @close-scan-modal="handleScanCancel"
      @scan-confirm="handleScanConfirm"
      @close-batch-ping="closeBatchPingModal"
      @start-batch-ping="startBatchPingTest"
      @close-task-result="taskResultModalVisible = false"
    />

    <!-- 模板选择抽屉组件 -->
    <TemplateDrawer 
      v-model:visible="templateDrawerVisible"
      v-model:selectedTemplateIds="selectedTemplateIds"
      :loading="templateLoading"
      :selectedIP="selectedIP"
      @confirm="handleCreateMonitoring"
      @close="handleCloseTemplateDrawer"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, onBeforeUnmount, nextTick, h, createVNode } from 'vue';
import { useRouter } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import { ipAPI } from '@/api';
import { suppressResizeObserverError } from '@/utils/errorHandler';
import * as Vue from 'vue';
import * as antdvIcons from '@ant-design/icons-vue';

// 导入拆分的组件
import IPTable from '@/components/business/IPTable.vue';
import MonitoringActions from '@/components/business/MonitoringActions.vue';
import TemplateDrawer from '@/components/business/TemplateDrawer.vue';
import { 
  ExclamationCircleOutlined,
} from '@ant-design/icons-vue';

// 路由实例
const router = useRouter();

// 搜索条件
const searchKeyword = ref('');
const ipStatus = ref('');
const ipType = ref('');

// IP数据状态 - 确保始终是数组
const ipData = ref([]);
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

// 防御性检查，确保ipData始终是数组
const setIPData = (data) => {
  if (Array.isArray(data)) {
    // 为每个IP记录设置保护状态信息
    const processedData = data.map(ip => {
      // 确保保护状态字段存在
      if (ip.is_protected === undefined) {
        ip.is_protected = ip.is_auto_discovered || false;
      }
      
      // 设置保护原因
      if (!ip.protection_reason && ip.is_auto_discovered) {
        ip.protection_reason = '自动发现的IP地址';
      }
      
      // 设置可编辑字段列表
      if (ip.is_auto_discovered) {
        ip.editable_fields = ['description', 'status'];
      } else {
        ip.editable_fields = 'all';
      }
      
      return ip;
    });
    
    ipData.value = processedData;
  } else {
    console.warn('尝试设置非数组数据到ipData:', data);
    ipData.value = [];
  }
};

// 统计计算属性 - 添加防御性检查
const activeCount = computed(() => {
  if (!Array.isArray(ipData.value)) {
    console.warn('ipData不是数组，返回0');
    return 0;
  }
  return ipData.value.filter(ip => ip.status === 'active').length;
});

const availableCount = computed(() => {
  if (!Array.isArray(ipData.value)) {
    console.warn('ipData不是数组，返回0');
    return 0;
  }
  return ipData.value.filter(ip => ip.status === 'available').length;
});

const onlineCount = computed(() => {
  if (!Array.isArray(ipData.value)) {
    console.warn('ipData不是数组，返回0');
    return 0;
  }
  return ipData.value.filter(ip => ip.ping_status === 'online' || ip.pingStatus === 'online').length;
});

// 统计对象
const statistics = computed(() => ({
  total: ipData.value.length || 0,
  active: activeCount.value,
  available: availableCount.value,
  online: onlineCount.value
}));

// 计算属性 - 扫描相关
const needsKey = computed(() => {
  const type = scanFormData.checkType;
  // Zabbix agent, SNMPv1, SNMPv2, SNMPv3 需要key
  return type === 9 || type === 10 || type === 11 || type === 13;
});

const isSNMPType = computed(() => {
  const type = scanFormData.checkType;
  return type === 10 || type === 11 || type === 13;
});

const needsAuth = computed(() => {
  return scanFormData.checkType === 13 && (scanFormData.snmpv3Config.securityLevel === '1' || scanFormData.snmpv3Config.securityLevel === '2');
});

const needsPriv = computed(() => {
  return scanFormData.checkType === 13 && scanFormData.snmpv3Config.securityLevel === '2';
});

const getKeyPlaceholder = () => {
  const type = scanFormData.checkType;
  if (type === 9) {
    return '例如：system.uname';
  } else if (type === 10 || type === 11 || type === 13) {
    return '例如：1.3.6.1.2.1.1.1.0';
  }
  return '请输入检查键值';
};



// 工具函数
const getStatusText = (status) => {
  const textMap = {
    'active': '在用',
    'available': '可用',
    'reserved': '预留',
    'conflict': '冲突'
  };
  return textMap[status] || status;
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

const formatDate = (date) => {
  if (!date) return null;
  return new Date(date).toLocaleString('zh-CN');
};

// 弹窗状态
const detailModalVisible = ref(false);
const editModalVisible = ref(false);
const scanModalVisible = ref(false);
const scanTaskModalVisible = ref(false);
const taskDetailModalVisible = ref(false);
const taskResultModalVisible = ref(false);
const selectedIP = ref(null);
const editingIP = ref(null);
const selectedTask = ref(null);

// 扫描任务查询相关
const scanTasks = ref([]);
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
const scanFormRef = ref();
const formData = reactive({
  ipAddress: '',
  hostname: '',
  status: 'available',
  type: 'static',
  macAddress: '',
  device: '',
  subnet: '',
  description: ''
});

// 扫描配置数据
const scanFormData = reactive({
  ipRanges: '192.168.1.0/24', // IP范围
  checkType: 12, // 默认ICMP ping
  ports: '0',
  key: '',
  // Python扫描器新参数
  maxConcurrent: 100, // 最大并发数
  timeout: 3.0, // 连接超时时间
  pingTimeout: 1.0, // Ping超时时间
  // 保留的Zabbix相关参数(仅用于兼容性)
  snmpCommunity: 'public',
  snmpv3Config: {
    securityLevel: '0',
    securityName: '',
    contextName: '',
    authProtocol: 0,
    authPassphrase: '',
    privProtocol: 0,
    privPassphrase: ''
  },
  uniqueCheck: 0,
  hostSource: 1,
  nameSource: 0
});



// 表单验证规则
const rules = {
  ipAddress: [
    { required: true, message: '请输入IP地址' },
    { pattern: /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/, message: '请输入有效的IP地址' }
  ],
  status: [{ required: true, message: '请选择IP状态' }],
  type: [{ required: true, message: '请选择IP类型' }]
};

// 扫描配置验证规则
const scanRules = {
  ipRanges: [
    { required: true, message: '请输入扫描IP范围' },
    { 
      validator: (rule, value) => {
        if (!value) return Promise.reject('请输入IP范围');
        
        const ranges = value.split('\n').filter(range => range.trim());
        for (const range of ranges) {
          const trimmedRange = range.trim();
          // 验证单个IP
          const singleIpPattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
          // 验证IP范围
          const rangePattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}-(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
          // 验证CIDR
          const cidrPattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{1,2}$/;
          // 验证简化范围格式 (192.168.1.1-100)
          const simpleRangePattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}-[0-9]{1,3}$/;
          
          if (!singleIpPattern.test(trimmedRange) && 
              !rangePattern.test(trimmedRange) && 
              !cidrPattern.test(trimmedRange) &&
              !simpleRangePattern.test(trimmedRange)) {
            return Promise.reject(`无效的IP范围格式: ${trimmedRange}`);
          }
        }
        return Promise.resolve();
      }
    }
  ],
  checkType: [{ required: true, message: '请选择检查类型' }],
  maxConcurrent: [
    { type: 'number', min: 1, max: 200, message: '并发数必须在1-200之间' }
  ],
  timeout: [
    { type: 'number', min: 1, max: 30, message: '超时时间必须在1-30秒之间' }
  ],
  pingTimeout: [
    { type: 'number', min: 0.5, max: 10, message: 'Ping超时时间必须在0.5-10秒之间' }
  ]
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

// 加载IP列表数据
const loadIPList = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize  // 使用Django标准的page_size参数名
    };
    
    // 添加搜索条件
    if (searchKeyword.value && searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }
    if (ipStatus.value) {
      params.status = ipStatus.value;
    }
    if (ipType.value) {
      params.type = ipType.value;
    }
    
    console.log('正在获取IP列表，参数:', params);
    console.log('当前分页状态:', {
      current: pagination.current,
      pageSize: pagination.pageSize,
      total: pagination.total
    });
    
    const response = await ipAPI.getIPList(params);
    
    console.log('API响应:', response);
    
    if (response && response.data) {
      // 特殊检查：如果返回的是URL路径列表，说明API路径错误
      if (response.data.records && response.data['scan-tasks']) {
        console.error('API路径错误：返回的是可用路径列表，而不是数据:', response.data);
        message.error('获取IP列表失败: API路径错误，请检查后端配置');
        setIPData([]);
        pagination.total = 0;
        return;
      }
      
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
          
          setIPData(resultData);
          pagination.total = data.count || data.total || resultData.length;
          console.log('成功获取IP列表（统一格式）:', ipData.value);
          message.success('IP列表数据已更新', 1);
        } else {
          console.error('API返回错误代码:', response.data.code, '错误信息:', response.data.message);
          message.error(`获取IP列表失败: ${response.data.message}`);
          setIPData([]);
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
        
        setIPData(resultData);
        pagination.total = response.data.count || response.data.total || resultData.length;
        console.log('成功获取IP列表（DRF格式）:', ipData.value);
        message.success('IP列表数据已更新', 1);
      }
    } else {
      console.error('无效的API响应:', response);
      message.error('获取IP列表失败: 无效的响应数据');
      setIPData([]);
      pagination.total = 0;
    }
  } catch (error) {
    console.error('加载IP列表失败:', error);
    console.error('错误详情:', {
      message: error.message,
      response: error.response,
      request: error.request
    });
    
    let errorMessage = '获取IP列表失败';
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
    
    // 如果API调用失败，显示空数据而不是模拟数据
    setIPData([]);
    pagination.total = 0;
  } finally {
    loading.value = false;
  }
};


const columns = [
  {
    title: 'IP地址',
    dataIndex: 'ip_address', // 数据库字段名
    key: 'ipAddress',
    width: 70,
    fixed: 'left'
  },
  {
    title: '来源',
    dataIndex: 'is_auto_discovered',
    key: 'source',
    width: 100
  },
  {
    title: 'Ping状态',
    dataIndex: 'ping_status', // 数据库字段名
    key: 'pingStatus',
    width: 80
  },
  {
    title: '监控状态',
    dataIndex: 'monitoring_enabled',
    key: 'monitoringStatus',
    width: 90
  },
  {
    title: 'IP类型',
    dataIndex: 'type',
    key: 'type',
    width: 80
  },
  {
    title: 'MAC地址',
    dataIndex: 'mac_address', // 数据库字段名
    key: 'macAddress',
    width: 150
  },
  {
    title: '关联资产',
    dataIndex: 'device',
    key: 'device',
    width: 150
  },
  {
    title: '所属网段',
    dataIndex: 'subnet',
    key: 'subnet',
    width: 140
  },
  {
    title: '最后在线时间',
    dataIndex: 'last_seen', // 数据库字段名
    key: 'lastSeen',
    width: 160
  },
  {
    title: '操作',
    key: 'operation',
    fixed: 'right',
    width: 280
  }
];

// 扫描任务表格列定义

// 扫描结果表格列定义
const resultColumns = [
  {
    title: 'IP地址',
    dataIndex: 'ip_address',
    key: 'ip_address',
    width: 90,
  },
  {
    title: '主机名',
    dataIndex: 'hostname',
    key: 'hostname',
    ellipsis: true
  },
  {
    title: 'MAC地址',
    dataIndex: 'mac_address',
    key: 'mac_address'
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status'
  },
  {
    title: '响应时间',
    dataIndex: 'response_time',
    key: 'response_time'
  },
  {
    title: '发现时间',
    dataIndex: 'created_at',
    key: 'created_at'
  }
];

// 事件处理函数
// 批量ping状态管理
const batchPingState = reactive({
  isVisible: false,
  phase: 'confirm', // confirm, testing, result
  stats: {
    total: 0,
    currentOnline: 0,
    currentOffline: 0,
    testResult: null
  },
  testing: {
    progress: 0,
    currentIP: '',
    startTime: null
  }
});

const handleBatchPing = async () => {
  try {
    // 获取当前页面的所有IP ID
    const allIpIds = ipData.value.map(ip => ip.id).filter(id => id);
    
    if (allIpIds.length === 0) {
      message.warning('没有可以ping的IP记录');
      return;
    }
    
    // 初始化状态
    batchPingState.stats.total = allIpIds.length;
    batchPingState.stats.currentOnline = ipData.value.filter(ip => ip.ping_status === 'online' || ip.pingStatus === 'online').length;
    batchPingState.stats.currentOffline = allIpIds.length - batchPingState.stats.currentOnline;
    batchPingState.phase = 'confirm';
    batchPingState.isVisible = true;
    
  } catch (error) {
    console.error('初始化批量ping失败:', error);
    message.error('初始化批量ping失败');
  }
};

// 开始ping测试
const startBatchPingTest = async () => {
  try {
    const allIpIds = ipData.value.map(ip => ip.id).filter(id => id);
    
    // 切换到测试阶段
    batchPingState.phase = 'testing';
    batchPingState.testing.startTime = new Date();
    batchPingState.testing.progress = 0;
    
    loading.value = true;
    
    // 调用批量ping API
    const response = await ipAPI.batchPingIPs(allIpIds);
    
    if (response.data && response.data.code === 200) {
      const batchData = response.data.data;
      const summary = batchData.summary;
      
      // 更新本地数据
      const resultsMap = new Map();
      batchData.results.forEach(result => {
        resultsMap.set(result.ip_id, result);
      });
      
      // 更新ipData中的记录
      ipData.value.forEach(ip => {
        const result = resultsMap.get(ip.id);
        if (result) {
          ip.ping_status = result.status;
          ip.pingStatus = result.status; // 兼容字段
          if (result.is_online) {
            ip.last_seen = new Date().toISOString();
            ip.lastSeen = new Date().toISOString(); // 兼容字段
          }
        }
      });
      
      // 设置测试结果并切换到结果阶段
      batchPingState.stats.testResult = summary;
      batchPingState.phase = 'result';
      
    } else {
      message.error(`批量ping测试失败: ${response.data?.message || '未知错误'}`);
      batchPingState.isVisible = false;
    }
  } catch (error) {
    console.error('批量ping测试失败:', error);
    let errorMessage = '批量ping测试失败';
    if (error.response && error.response.data) {
      errorMessage += `: ${error.response.data.message || error.response.data.error || '网络错误'}`;
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    message.error(errorMessage);
    batchPingState.isVisible = false;
  } finally {
    loading.value = false;
  }
};

// 关闭批量ping弹窗
const closeBatchPingModal = () => {
  batchPingState.isVisible = false;
  batchPingState.phase = 'confirm';
  batchPingState.stats.testResult = null;
  batchPingState.testing.progress = 0;
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
    message.warning('请选择要删除的IP地址');
    return;
  }

  try {
    Modal.confirm({
      title: '批量删除确认',
      content: `您将删除 ${selectedRowKeys.value.length} 个IP地址，此操作不可恢复！`,
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        batchDeleting.value = true;
        try {
          const response = await ipAPI.batchDeleteIPs(selectedRowKeys.value);
          
          if (response.data && response.data.code === 200) {
            const result = response.data.data;
            message.success(`批量删除成功！删除: ${result.deleted_count} 个，失败: ${result.failed_count} 个`, 1);
            
            // 清空选中状态
            clearSelection();
            
            // 刷新列表
            await loadIPList();
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
    message.warning('请选择要操作的IP地址');
    return;
  }

  const actionText = enableMonitoring ? '启用监控' : '禁用监控';
  
  try {
    Modal.confirm({
      title: `批量${actionText}`,
      content: `您将对 ${selectedRowKeys.value.length} 个IP地址${actionText}，是否继续？`,
      okText: `确认${actionText}`,
      cancelText: '取消',
      onOk: async () => {
        batchMonitoringToggling.value = true;
        try {
          const response = await ipAPI.batchToggleMonitoring(selectedRowKeys.value, enableMonitoring);
          
          if (response.data && response.data.code === 200) {
            const result = response.data.data;
            message.success(`批量${actionText}成功！成功: ${result.success_count} 个，失败: ${result.failed_count} 个`, 1);
            
            // 更新本地数据
            ipData.value.forEach(ip => {
              if (selectedRowKeys.value.includes(ip.id)) {
                ip.monitoring_enabled = enableMonitoring;
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
    selectedIP.value = record;
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
    const response = await ipAPI.toggleMonitoring(record.id, enableMonitoring);
    
    if (response.data && response.data.code === 200) {
      // 更新本地数据
      record.monitoring_enabled = enableMonitoring;
      message.success(`${record.ip_address || record.ipAddress} ${actionText}成功`, 1);
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
const loadZabbixTemplates = async (ipId) => {
  templateLoading.value = true;
  try {
    const response = await ipAPI.getZabbixTemplates(ipId, templateSearchKeyword.value);
    
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
      // 检查是否是Zabbix连接问题
      if (response.data && response.data.message && response.data.message.includes('Zabbix API连接不可用')) {
        // 显示详细的诊断信息
        const errorMessage = '⚠️ Zabbix服务器连接失败';
        const suggestions = [
          '请检查Zabbix服务器是否正常运行',
          '验证网络连接和防火墙设置',
          '检查Zabbix API配置是否正确'
        ];
        
        Modal.error({
          title: '无法加载监控模板',
          content: h('div', [
            h('p', { style: 'margin-bottom: 16px;' }, errorMessage),
            h('div', { style: 'background: #f5f5f5; padding: 12px; border-radius: 6px;' }, [
              h('p', { style: 'margin: 0 0 8px 0; font-weight: 600;' }, '解决建议：'),
              h('ul', { style: 'margin: 0; padding-left: 20px;' }, 
                suggestions.map(suggestion => 
                  h('li', { style: 'margin-bottom: 4px;' }, suggestion)
                )
              )
            ])
          ]),
          width: 500
        });
      } else {
        message.error(`加载模板列表失败: ${response.data?.message || '未知错误'}`);
      }
      
      zabbixTemplates.value = [];
    }
  } catch (error) {
    console.error('加载模板列表失败:', error);
    
    // 检查是否是网络连接问题
    if (error.message && (error.message.includes('Network Error') || error.message.includes('timeout'))) {
      Modal.error({
        title: '网络连接失败',
        content: '无法连接到后端服务器，请检查网络连接和服务器状态。'
      });
    } else {
      message.error(`加载模板列表失败: ${error.message}`);
    }
    
    zabbixTemplates.value = [];
  } finally {
    templateLoading.value = false;
  }
};

// 搜索模板
const handleTemplateSearch = async () => {
  if (selectedIP.value) {
    await loadZabbixTemplates(selectedIP.value.id);
  }
};

// 模板选择变化 - 确保类型安全
const handleTemplateSelect = (templateIds) => {
  try {
    // 确保 templateIds 是数组并且所有元素都是字符串
    if (Array.isArray(templateIds)) {
      selectedTemplateIds.value = templateIds.map(id => {
        if (id === null || id === undefined) return '';
        return String(id);
      });
    } else {
      selectedTemplateIds.value = [];
    }
    console.log('已选择模板:', selectedTemplateIds.value);
  } catch (error) {
    console.error('处理模板选择时出错:', error);
    selectedTemplateIds.value = [];
  }
};

// 创建监控主机
const handleCreateMonitoring = async () => {
  if (!selectedIP.value) {
    message.error('请先选择IP地址');
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
      host_name: selectedIP.value.hostname || selectedIP.value.ip_address || selectedIP.value.ipAddress,
      group_ids: [] // 使用默认主机组
    };
    
    const response = await ipAPI.createMonitoring(selectedIP.value.id, monitoringData);
    
    if (response.data && response.data.code === 200) {
      const result = response.data.data;
      
      message.success({
        content: `监控主机创建成功！\n主机名: ${result.host_name}\nIP: ${result.ip_address}\n模板数量: ${result.template_count}`,
        duration: 5
      });
      
      // 更新本地IP记录的监控状态
      selectedIP.value.monitoring_enabled = true;
      
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
// 安全获取模板的唯一key
const getTemplateKey = (template) => {
  try {
    if (!template) return Math.random().toString();
    if (template.templateid) return String(template.templateid);
    if (template.id) return String(template.id);
    return Math.random().toString();
  } catch (error) {
    console.error('获取模板key失败:', error);
    return Math.random().toString();
  }
};

// 安全获取模板的value
const getTemplateValue = (template) => {
  try {
    if (!template) return '';
    if (template.templateid) return String(template.templateid);
    if (template.id) return String(template.id);
    return '';
  } catch (error) {
    console.error('获取模板value失败:', error);
    return '';
  }
};

const handleCloseTemplateDrawer = () => {
  templateDrawerVisible.value = false;
  selectedTemplateIds.value = [];
  templateSearchKeyword.value = '';
  selectedCategory.value = '';
  expandedCategories.value = {};
  selectedIP.value = null;
};

// 模板数据安全验证函数
const validateTemplateData = (template) => {
  try {
    if (!template || typeof template !== 'object') {
      console.warn('模板不是有效对象:', template);
      return null;
    }
    
    // 安全地获取所有字段
    const safeTemplate = {
      templateid: safeString(template.templateid || template.id || `temp_${Date.now()}`),
      name: safeString(template.name || '未知模板'),
      description: safeString(template.description || ''),
      category: safeString(template.category || '📝 其他'),
      items_count: Number(template.items_count) || 0,
      triggers_count: Number(template.triggers_count) || 0,
      macros_count: Number(template.macros_count) || 0,
      groups: Array.isArray(template.groups) ? template.groups.map(group => ({
        groupid: safeString(group.groupid || group.id || ''),
        name: safeString(group.name || '未知组')
      })) : [],
      icon: safeString(template.icon || 'setting')
    };
    
    // 验证必需字段
    if (!safeTemplate.templateid || !safeTemplate.name) {
      console.warn('模板缺少必需字段:', safeTemplate);
      return null;
    }
    
    return safeTemplate;
  } catch (error) {
    console.error('验证模板时出错:', error, template);
    return null;
  }
};

// 按分类组织模板 - 增强类型安全
const groupedTemplates = computed(() => {
  const groups = {};
  
  try {
    if (!Array.isArray(zabbixTemplates.value)) {
      console.warn('zabbixTemplates不是数组:', zabbixTemplates.value);
      return groups;
    }
    
    zabbixTemplates.value.forEach((template) => {
      const safeTemplate = validateTemplateData(template);
      if (!safeTemplate) {
        return; // 跳过无效模板
      }
      
      const category = safeTemplate.category;
      if (!groups[category]) {
        groups[category] = [];
      }
      
      groups[category].push(safeTemplate);
    });
    
    // 对每个分类的模板按名称排序
    Object.keys(groups).forEach(category => {
      try {
        groups[category].sort((a, b) => {
          const nameA = safeString(a.name || '');
          const nameB = safeString(b.name || '');
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

// 分类图标映射 - 增强类型安全
const getCategoryIcon = (category) => {
  try {
    const categoryStr = safeCategoryToString(category);
    const iconMap = {
      '💻 操作系统': 'DesktopOutlined',
      '🗄 数据库': 'DatabaseOutlined', 
      '🌐 Web服务器': 'GlobalOutlined',
      '📦 容器平台': 'ContainerOutlined',
      '🌐 网络设备': 'RouterOutlined',
      '☁️ 虚拟化': 'CloudOutlined',
      '📊 网络监控': 'WifiOutlined',
      '☁️ 云服务': 'CloudServerOutlined',
      '🚀 应用服务': 'CodeOutlined',
      '📬 消息队列': 'MessageOutlined',
      '⚡ 缓存系统': 'ThunderboltOutlined',
      '💾 存储系统': 'HddOutlined',
      '🔒 安全监控': 'SafetyOutlined',
      '🌡️ IoT设备': 'NodeIndexOutlined',
      '📝 其他': 'SettingOutlined'
    };
    
    return iconMap[categoryStr] || 'SettingOutlined';
  } catch (error) {
    console.warn('getCategoryIcon处理错误:', error, category);
    return 'SettingOutlined';
  }
};

// 分类统计信息 - 增强类型安全
const categoryStats = computed(() => {
  const stats = {};
  
  try {
    if (!groupedTemplates.value || typeof groupedTemplates.value !== 'object') {
      return stats;
    }
    
    Object.entries(groupedTemplates.value).forEach(([category, templates]) => {
      try {
        const categoryKey = safeCategoryToString(category);
        if (!Array.isArray(templates)) {
          console.warn(`分类${categoryKey}的模板不是数组:`, templates);
          stats[categoryKey] = { count: 0, selected: 0 };
          return;
        }
        
        const selectedIds = Array.isArray(selectedTemplateIds.value) ? selectedTemplateIds.value : [];
        
        stats[categoryKey] = {
          count: Number(templates.length) || 0,
          selected: templates.filter(t => {
            try {
              const templateId = safeString(t.templateid || t.id || '');
              return selectedIds.includes(templateId);
            } catch (filterError) {
              console.warn('过滤模板时出错:', filterError, t);
              return false;
            }
          }).length
        };
      } catch (categoryError) {
        console.warn(`处理分类${category}统计时出错:`, categoryError);
        stats[safeCategoryToString(category)] = { count: 0, selected: 0 };
      }
    });
  } catch (error) {
    console.error('categoryStats计算出错:', error);
  }
  
  return stats;
});

// 筛选后的模板 - 增强类型安全
const filteredTemplates = computed(() => {
  try {
    let result = groupedTemplates.value || {};
    
    // 分类筛选
    if (selectedCategory.value) {
      const categoryStr = safeString(selectedCategory.value);
      result = {
        [categoryStr]: result[categoryStr] || []
      };
    }
    
    return result;
  } catch (error) {
    console.error('filteredTemplates计算出错:', error);
    return {};
  }
});

// 安全的分类显示名称函数
const safeCategoryDisplayName = (category) => {
  try {
    return safeCategoryToString(category);
  } catch (error) {
    console.error('safeCategoryDisplayName处理错误:', error, category);
    return '📝 其他';
  }
};

// 切换分类筛选 - 确保类型安全
const toggleCategoryFilter = (category) => {
  try {
    const categoryStr = safeCategoryToString(category);
    if (selectedCategory.value === categoryStr) {
      selectedCategory.value = '';
    } else {
      selectedCategory.value = categoryStr;
    }
  } catch (error) {
    console.warn('toggleCategoryFilter处理错误:', error, category);
    selectedCategory.value = '';
  }
};

// 清除分类筛选
const clearCategoryFilter = () => {
  selectedCategory.value = '';
};

// 切换分类展开状态 - 使用安全的类型转换
const toggleCategoryExpand = (category) => {
  try {
    const categoryStr = safeCategoryToString(category);
    expandedCategories.value[categoryStr] = !expandedCategories.value[categoryStr];
  } catch (error) {
    console.warn('toggleCategoryExpand处理错误:', error, category);
  }
};

// 安全检查分类是否展开 - 避免对象类型转换错误
const isCategoryExpanded = (category) => {
  // 检查是对象还是字符串
  if (typeof category === 'object') {
    try {
      return isCategoryExpanded(JSON.stringify(category));
    } catch (jsonError) {
      console.warn('对象转字符串失败:', jsonError);
      return true; // 默认展开
    }
  }

  try {
    if (category === null || category === undefined) {
      return true;
    }
    const categoryStr = safeCategoryToString(category);
    // 默认展开所有分类，除非明确设置为false
    return expandedCategories.value[categoryStr] !== false;
  } catch (error) {
    console.warn('isCategoryExpanded处理错误:', error, category);
    return true; // 默认展开
  }
};

// 安全的分类转字符串函数 - 根据规范处理各种类型
const safeCategoryToString = (category) => {
  try {
    if (category === null || category === undefined) {
      return '📝 其他';
    }
    
    if (typeof category === 'string') {
      return category.trim() || '📝 其他';
    }
    
    if (typeof category === 'object') {
      // 如果是对象，尝试提取有效属性
      if (category.name && typeof category.name === 'string') {
        return category.name.trim();
      }
      if (category.title && typeof category.title === 'string') {
        return category.title.trim();
      }
      if (category.label && typeof category.label === 'string') {
        return category.label.trim();
      }
      
      // 尝试使用JSON.stringify安全地转换对象
      try {
        const jsonStr = JSON.stringify(category);
        if (jsonStr && jsonStr !== '[object Object]') {
          return jsonStr;
        }
      } catch (jsonError) {
        // JSON转换失败时继续处理
        console.warn('JSON转换失败:', jsonError);
      }
      
      // 对象转换失败时的安全处理
      console.warn('分类是对象但缺少有效字段:', category);
      return '📝 其他';
    }
    
    // 其他类型的安全转换
    const stringResult = String(category);
    // 检查是否是有效的字符串表示
    if (stringResult && stringResult !== '[object Object]') {
      return stringResult.trim() || '📝 其他';
    } else {
      return '📝 其他';
    }
  } catch (error) {
    console.error('safeCategoryToString处理错误:', error, category);
    return '📝 其他';
  }
};

// 安全的字符串转换函数 - 增强版，防止"Cannot convert object to primitive value"错误
const safeString = (value) => {
  try {
    // 处理null/undefined
    if (value == null) {
      return '';
    }
    
    // 处理基本类型
    switch (typeof value) {
      case 'string':
        return value;
      case 'number':
      case 'boolean':
      case 'bigint':
        return String(value);
      case 'symbol':
        return value.toString();
    }
    
    // 处理对象类型
    if (typeof value === 'object') {
      // 优先检查常见对象类型
      if (value instanceof Date) {
        return value.toISOString();
      }
      
      if (value instanceof Error) {
        return value.message || value.name || 'Error';
      }
      
      // 尝试获取对象的常见字符串属性
      const stringProps = ['name', 'title', 'label', 'text', 'message', 'value'];
      for (const prop of stringProps) {
        if (typeof value[prop] === 'string') {
          return value[prop];
        }
      }
      
      // 安全地使用JSON.stringify
      try {
        const jsonStr = JSON.stringify(value, (key, val) => {
          if (typeof val === 'object' && val !== null) {
            return Object.prototype.toString.call(val);
          }
          return val;
        });
        if (jsonStr && jsonStr !== '{}' && jsonStr !== '[]') {
          return jsonStr;
        }
      } catch (jsonError) {
        console.warn('JSON.stringify failed:', jsonError);
      }
      
      // 最后尝试调用toString()
      try {
        const toStringResult = Object.prototype.toString.call(value);
        if (toStringResult !== '[object Object]') {
          return toStringResult;
        }
      } catch (toStringError) {
        console.warn('toString call failed:', toStringError);
      }
      
      return '[object]';
    }
    
    // 其他未知类型
    return String(value);
  } catch (error) {
    console.error('safeString处理错误:', error, value);
    return '';
  }
};

// 获取模板图标 - 根据内存规范增强类型安全和错误处理
const getTemplateIcon = (template) => {
  try {
    // 基础验证
    if (!template || typeof template !== 'object') {
      console.warn('getTemplateIcon: 模板对象无效', template);
      return 'SettingOutlined';
    }
    
    if (!template.icon) {
      return 'SettingOutlined';
    }
    
    // 安全处理图标名称 - 确保必须是字符串类型
    let iconName;
    try {
      if (typeof template.icon === 'string') {
        iconName = template.icon.trim();
      } else if (typeof template.icon === 'object' && template.icon !== null) {
        // 如果是对象，尝试获取有效的字符串属性
        if (template.icon.name && typeof template.icon.name === 'string') {
          iconName = template.icon.name.trim();
        } else if (template.icon.type && typeof template.icon.type === 'string') {
          iconName = template.icon.type.trim();
        } else {
          // 对象转换为字符串时的安全处理
          try {
            const objStr = JSON.stringify(template.icon);
            console.warn('getTemplateIcon: 图标是对象，尝试JSON转换', template.icon, objStr);
            iconName = 'setting'; // 使用默认值
          } catch (jsonError) {
            console.error('getTemplateIcon: JSON转换失败', jsonError);
            iconName = 'setting';
          }
        }
      } else if (template.icon === null || template.icon === undefined) {
        iconName = 'setting';
      } else {
        // 其他类型的安全转换
        iconName = String(template.icon).trim();
      }
    } catch (typeError) {
      console.error('getTemplateIcon: 类型处理错误', typeError, template.icon);
      iconName = 'setting';
    }
    
    // 验证图标名称
    if (!iconName || iconName === '[object Object]' || iconName.length === 0) {
      console.warn('getTemplateIcon: 无效的图标名称', iconName, template);
      return 'SettingOutlined';
    }
    
    // 如果已经包含Outlined后缀，直接返回
    if (iconName.endsWith('Outlined')) {
      return iconName;
    }
    
    // 特殊图标名称映射
    const iconMap = {
      'global': 'GlobalOutlined',
      'database': 'DatabaseOutlined',
      'server': 'ServerOutlined',
      'network': 'RouterOutlined',
      'cloud': 'CloudOutlined',
      'container': 'ContainerOutlined',
      'security': 'SafetyOutlined',
      'storage': 'HddOutlined',
      'monitor': 'DashboardOutlined',
      'setting': 'SettingOutlined'
    };
    
    // 检查是否有直接映射
    const lowerIconName = iconName.toLowerCase();
    if (iconMap[lowerIconName]) {
      return iconMap[lowerIconName];
    }
    
    // 处理首字母大写并添加Outlined后缀
    try {
      const capitalizedIcon = iconName.charAt(0).toUpperCase() + iconName.slice(1);
      const finalIconName = `${capitalizedIcon}Outlined`;
      
      // 验证图标是否存在于Ant Design图标库中
      const availableIcons = [
        'GlobalOutlined', 'DatabaseOutlined', 'DesktopOutlined', 'RouterOutlined',
        'CloudOutlined', 'ContainerOutlined', 'SafetyOutlined', 'HddOutlined',
        'CodeOutlined', 'MessageOutlined', 'ThunderboltOutlined', 'NodeIndexOutlined',
        'SettingOutlined', 'DashboardOutlined', 'ServerOutlined', 'WifiOutlined'
      ];
      
      if (availableIcons.includes(finalIconName)) {
        return finalIconName;
      }
    } catch (processError) {
      console.error('getTemplateIcon: 图标名称处理错误', processError, iconName);
    }
    
    // 如果图标不存在，返回默认图标
    return 'SettingOutlined';
  } catch (error) {
    console.error('getTemplateIcon处理严重错误:', error, template);
    return 'SettingOutlined';
  }
};

const handleSearch = async () => {
  pagination.current = 1;
  await loadIPList();
};

const handleReset = async () => {
  searchKeyword.value = '';
  ipStatus.value = '';
  ipType.value = '';
  pagination.current = 1;
  await loadIPList();
};

const handleSearchInput = (value) => {
  searchKeyword.value = value;
};

const handleStatusChange = (value) => {
  ipStatus.value = value;
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
  
  await loadIPList();
};

const handleAdd = () => {
  router.push({ name: 'ipAdd' });
};

const handleView = (record) => {
  selectedIP.value = record;
  detailModalVisible.value = true;
};

const handleEdit = (record) => {
  // 检查IP是否受保护
  if (record.is_protected || record.is_auto_discovered) {
    message.warning({
      content: `不能编辑此IP地址：${record.ip_address || record.ipAddress}\n原因：${record.protection_reason || '自动发现的IP地址不允许编辑'}\n可编辑字段：${Array.isArray(record.editable_fields) ? record.editable_fields.join(', ') : '备注、状态'}`,
      duration: 5
    });
    return;
  }
  
  editingIP.value = record;
  Object.assign(formData, record);
  editModalVisible.value = true;
};

const handleDelete = async (record) => {
  try {
    // 显示加载状态
    const loadingMessage = message.loading('正在检查删除影响...', 0);
    
    try {
      // 检查删除影响
      const impactResponse = await ipAPI.checkDeletionImpact(record.id);
      loadingMessage();
      
      if (impactResponse.data && impactResponse.data.code === 200) {
        const impactData = impactResponse.data.data;
        
        // 构建详细的确认对话框内容
        const confirmContent = await new Promise((resolve) => {
          const { createVNode } = Vue;
          const { ExclamationCircleOutlined, WarningOutlined } = antdvIcons;
          
          const warningItems = impactData.deletion_warnings.map(warning => 
            createVNode('li', { style: 'margin: 4px 0; color: #ff4d4f;' }, warning)
          );
          
          // 如果是自动发现的IP，添加特殊警告
          if (impactData.is_auto_discovered) {
            warningItems.unshift(
              createVNode('li', { 
                style: 'margin: 4px 0; color: #ff4d4f; font-weight: bold; background: #fff2f0; padding: 8px; border-radius: 4px; border-left: 4px solid #ff4d4f;' 
              }, '⚠️ 警告：此IP为Zabbix自动发现，删除后可能影响监控系统！')
            );
          }
          
          const content = createVNode('div', {}, [
            createVNode('p', { style: 'font-weight: bold; margin-bottom: 12px; color: #ff4d4f;' }, 
              impactData.is_auto_discovered ? 
              `⚠️ 删除自动发现的IP地址: ${impactData.ip_address}` : 
              `确认删除 IP地址: ${impactData.ip_address}`
            ),
            
            // 基本信息
            createVNode('div', { style: 'margin-bottom: 12px; padding: 8px; background: #f5f5f5; border-radius: 4px;' }, [
              createVNode('p', { style: 'margin: 0; font-size: 12px; color: #666;' }, `主机名: ${impactData.hostname || '未设置'}`),
              createVNode('p', { style: 'margin: 0; font-size: 12px; color: #666;' }, `来源: ${impactData.is_auto_discovered ? 'Zabbix自动发现' : '手动创建'}`),
              impactData.zabbix_drule_id ? createVNode('p', { style: 'margin: 0; font-size: 12px; color: #666;' }, `Zabbix规则ID: ${impactData.zabbix_drule_id}`) : null
            ]),
            
            // 影响统计
            createVNode('div', { style: 'margin-bottom: 12px;' }, [
              createVNode('p', { style: 'margin: 0; font-weight: bold; color: #fa8c16;' }, '删除影响范围:'),
              impactData.scan_results_count > 0 ? 
                createVNode('p', { style: 'margin: 4px 0; color: #ff4d4f;' }, `· 扫描结果: ${impactData.scan_results_count} 条记录`) : null,
              impactData.related_tasks.length > 0 ? 
                createVNode('p', { style: 'margin: 4px 0; color: #ff4d4f;' }, `· 相关任务: ${impactData.related_tasks.length} 个`) : null,
              impactData.will_cleanup_zabbix ? 
                createVNode('p', { style: 'margin: 4px 0; color: #ff4d4f;' }, '· Zabbix监控数据: 将尝试清理') : null
            ]),
            
            // 警告列表
            createVNode('div', {}, [
              createVNode('p', { style: 'margin: 8px 0 4px 0; font-weight: bold; color: #ff4d4f;' }, [
                createVNode(WarningOutlined, { style: 'margin-right: 4px;' }),
                '警告信息:'
              ]),
              createVNode('ul', { style: 'margin: 0; padding-left: 16px; max-height: 200px; overflow-y: auto;' }, warningItems)
            ]),
            
            createVNode('p', { style: 'margin-top: 12px; font-weight: bold; color: #ff4d4f; text-align: center;' }, '此操作不可恢复！')
          ]);
          
          resolve(content);
        });
        
        // 显示确认对话框
        await new Promise((resolve, reject) => {
          const modal = Modal.confirm({
            title: impactData.is_auto_discovered ? '删除自动发现的IP地址及相关数据' : '删除IP地址及相关数据',
            content: confirmContent,
            width: 600,
            okText: '确认删除',
            okType: 'danger',
            cancelText: '取消',
            icon: createVNode(ExclamationCircleOutlined, { style: 'color: #ff4d4f;' }),
            onOk: () => resolve(true),
            onCancel: () => reject(new Error('User cancelled'))
          });
        });
        
      } else {
        loadingMessage();
        throw new Error('获取删除影响信息失败');
      }
      
    } catch (impactError) {
      loadingMessage();
      console.warn('检查删除影响失败，使用默认确认对话框:', impactError);
      
      // 如果检查影响失败，使用简单的确认对话框
      await new Promise((resolve, reject) => {
        const modal = Modal.confirm({
          title: '确认删除IP',
          content: `确定要删除IP地址 "${record.ipAddress || record.ip_address}" 吗？\n\n警告：此操作将删除IP记录及所有相关数据（包括扫描结果、Zabbix监控数据等），该操作不可恢复！`,
          okText: '确认删除',
          okType: 'danger',
          cancelText: '取消',
          onOk: () => resolve(true),
          onCancel: () => reject(new Error('User cancelled'))
        });
      });
    }
    
    // 执行删除操作
    const deleteMessage = message.loading('正在删除IP及相关数据...', 0);
    
    try {
      const response = await ipAPI.deleteIP(record.id);
      deleteMessage();
      
      if (response.data && response.data.code === 200) {
        const cleanupData = response.data.data;
        
        // 构建成功消息
        let successMessage = `IP地址 "${cleanupData.ip_address}" 已成功删除`;
        
        const cleanupDetails = [];
        if (cleanupData.scan_results_deleted > 0) {
          cleanupDetails.push(`扫描结果: ${cleanupData.scan_results_deleted}条`);
        }
        if (cleanupData.zabbix_cleanup && cleanupData.zabbix_cleanup.success) {
          if (cleanupData.zabbix_cleanup.hosts && cleanupData.zabbix_cleanup.hosts.length > 0) {
            const deletedCount = cleanupData.zabbix_cleanup.hosts.filter(h => h.deleted).length;
            cleanupDetails.push(`Zabbix主机: ${deletedCount}个`);
          }
        }
        
        if (cleanupDetails.length > 0) {
          successMessage += `\n同时清理了：${cleanupDetails.join('、')}`;
        }
        
        message.success({
          content: successMessage,
          duration: 6
        });
        
        // 直接从列表中移除已删除的IP，而不是刷新整个列表
        ipData.value = ipData.value.filter(ip => ip.id !== record.id);
        pagination.total = ipData.value.length;
      } else {
        message.error('删除IP地址失败');
      }
    } catch (deleteError) {
      deleteMessage();
      throw deleteError;
    }
    
  } catch (error) {
    if (error.message !== 'User cancelled') {
      console.error('删除IP地址失败:', error);
      message.error(`删除IP地址失败: ${error.response?.data?.message || error.message}`);
    }
  }
};

const handlePing = async (record) => {
  record.pinging = true;
  try {
    // 调用后端ping API
    const response = await ipAPI.pingIP(record.id);
    
    if (response.data && response.data.code === 200) {
      const pingData = response.data.data;
      // 更新记录的ping状态
      record.ping_status = pingData.status;
      record.pingStatus = pingData.status; // 兼容字段
      record.last_seen = pingData.last_seen;
      record.lastSeen = pingData.last_seen; // 兼容字段
      
      const statusText = pingData.is_online ? '在线' : '离线';
      const responseTimeText = pingData.response_time ? ` (${pingData.response_time}ms)` : '';
      
      message.success(`Ping ${record.ip_address || record.ipAddress} 完成: ${statusText}${responseTimeText}`, 1);
    } else {
      message.error(`Ping失败: ${response.data?.message || '未知错误'}`);
    }
  } catch (error) {
    console.error('Ping测试失败:', error);
    let errorMessage = 'Ping失败';
    if (error.response && error.response.data) {
      errorMessage += `: ${error.response.data.message || error.response.data.error || '网络错误'}`;
    } else if (error.message) {
      errorMessage += `: ${error.message}`;
    }
    message.error(errorMessage);
  } finally {
    record.pinging = false;
  }
};




const handleExport = () => {
  message.info('导出功能开发中...');
};

const handleListManagement = () => {
  message.info('列表管理功能开发中...');
};

const handleScan = () => {
  // 重置扫描表单并设置当前页面可能的IP范围
  resetScanForm();
  
  // 如果有搜索关键词，尝试智能设置IP范围
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.trim();
    // 如果搜索关键词是IP格式，自动设置为扫描范围
    const ipPattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
    if (ipPattern.test(keyword)) {
      // 提取网段
      const ipParts = keyword.split('.');
      const networkBase = `${ipParts[0]}.${ipParts[1]}.${ipParts[2]}.0/24`;
      scanFormData.ipRanges = networkBase;
    }
  }
  
  scanModalVisible.value = true;
};

const handleScanConfirm = async () => {
  try {
    await scanFormRef.value.validate();
    
    // 处理IP范围数据
    const ipRanges = scanFormData.ipRanges.split('\n')
      .map(range => range.trim())
      .filter(range => range.length > 0);
    
    // 构建Python扫描配置数据，发送给后端
    const scanConfig = {
      ipRanges: ipRanges,
      checkType: scanFormData.checkType,
      ports: scanFormData.ports,
      key: scanFormData.key,
      // Python扫描器参数
      maxConcurrent: scanFormData.maxConcurrent || 100,
      timeout: scanFormData.timeout || 3.0,
      pingTimeout: scanFormData.pingTimeout || 1.0,
      // 保留一些参数用于服务检测
      snmpCommunity: scanFormData.snmpCommunity,
      snmpv3Config: scanFormData.snmpv3Config
    };
    
    console.log('发送Python扫描配置:', scanConfig);
    
    try {
      // 调用后端Python扫描API
      const response = await ipAPI.createScanTask(scanConfig);
      
      if (response.data && response.data.code === 200) {
        const taskData = response.data.data;
        
        // 显示成功消息
        const scanEngineText = taskData.scanEngine === 'python' ? 'Python原生扫描' : '扫描';
        
        message.success({
          content: `${scanEngineText}任务创建成功！\n扫描范围: ${ipRanges.join(', ')}\n检查类型: ${getCheckTypeName(scanFormData.checkType)}\n任务ID: ${taskData.taskId}\n并发数: ${scanConfig.maxConcurrent}\n超时配置: 连接${scanConfig.timeout}s, Ping${scanConfig.pingTimeout}s\n已启动后台异步处理，系统将自动扫描网络并保存结果到数据库...`,
          duration: 8
        });
        
        // 刷新IP列表
        await loadIPList();
        
        // 自动打开任务查询面板查看进度
        setTimeout(() => {
          handleScanTaskQuery();
        }, 1000);
        
      } else {
        throw new Error(response.data?.message || 'Python扫描任务创建失败');
      }
    } catch (apiError) {
      console.error('后端Python扫描API调用失败:', apiError);
      message.error(`Python扫描任务创建失败: ${apiError.response?.data?.message || apiError.message}`);
      return;
    }
    
    scanModalVisible.value = false;
    resetScanForm();
  } catch (error) {
    console.error('扫描配置验证失败:', error);
    message.error('请检查扫描配置是否正确');
  }
};

// 获取检查类型名称
const getCheckTypeName = (type) => {
  const typeNames = {
    0: 'SSH', 1: 'LDAP', 2: 'SMTP', 3: 'FTP', 4: 'HTTP',
    5: 'POP', 6: 'NNTP', 7: 'IMAP', 8: 'TCP', 9: 'Zabbix agent',
    10: 'SNMPv1', 11: 'SNMPv2', 12: 'ICMP ping', 13: 'SNMPv3',
    14: 'HTTPS', 15: 'Telnet'
  };
  return typeNames[type] || '未知类型';
};

const handleScanCancel = () => {
  scanModalVisible.value = false;
  resetScanForm();
};

const handleTypeChange = (value) => {
  // 根据类型设置默认端口
  const defaultPorts = {
    0: '22',      // SSH
    1: '389',     // LDAP
    2: '25',      // SMTP
    3: '21',      // FTP
    4: '80',      // HTTP
    5: '110',     // POP
    6: '119',     // NNTP
    7: '143',     // IMAP
    8: '0',       // TCP
    9: '10050',   // Zabbix agent
    10: '161',    // SNMPv1
    11: '161',    // SNMPv2
    12: '0',      // ICMP (不需要端口)
    13: '161',    // SNMPv3
    14: '443',    // HTTPS
    15: '23'      // Telnet
  };
  
  scanFormData.ports = defaultPorts[value] || '0';
  
  // 清空相关字段
  scanFormData.key = '';
  if (value !== 10 && value !== 11) {
    scanFormData.snmpCommunity = 'public';
  }
  if (value !== 13) {
    // 清空SNMPv3配置
    scanFormData.snmpv3Config.securityLevel = '0';
    scanFormData.snmpv3Config.securityName = '';
    scanFormData.snmpv3Config.contextName = '';
    scanFormData.snmpv3Config.authProtocol = 0;
    scanFormData.snmpv3Config.authPassphrase = '';
    scanFormData.snmpv3Config.privProtocol = 0;
    scanFormData.snmpv3Config.privPassphrase = '';
  }
};

const handleSecurityLevelChange = (value) => {
  // 清空认证和隐私配置
  if (value === '0') {
    scanFormData.snmpv3Config.authProtocol = 0;
    scanFormData.snmpv3Config.authPassphrase = '';
    scanFormData.snmpv3Config.privProtocol = 0;
    scanFormData.snmpv3Config.privPassphrase = '';
  } else if (value === '1') {
    scanFormData.snmpv3Config.privProtocol = 0;
    scanFormData.snmpv3Config.privPassphrase = '';
  }
};

const resetScanForm = () => {
  Object.assign(scanFormData, {
    ipRanges: '192.168.1.0/24',
    checkType: 12,
    ports: '0',
    key: '',
    // Python扫描器参数
    maxConcurrent: 100,
    timeout: 3.0,
    pingTimeout: 1.0,
    // 保留参数
    snmpCommunity: 'public',
    snmpv3Config: {
      securityLevel: '0',
      securityName: '',
      contextName: '',
      authProtocol: 0,
      authPassphrase: '',
      privProtocol: 0,
      privPassphrase: ''
    },
    uniqueCheck: 0,
    hostSource: 1,
    nameSource: 0
  });
  scanFormRef.value?.resetFields();
};

// 扫描任务查询相关函数
const handleScanTaskQuery = () => {
  scanTaskModalVisible.value = true;
  loadScanTasks();
  
  // 启动异步状态监控
  startAsyncStatusMonitoring();
};

// 异步状态监控
let statusCheckInterval = null;

// 组件初始化状态标记
let isComponentInitialized = false;
let isMonitoringActive = false;

const startAsyncStatusMonitoring = () => {
  // 防止重复启动
  if (isMonitoringActive) {
    console.log('异步监控已在运行，跳过重复启动');
    return;
  }
  
  // 清理旧的间隔器
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval);
    statusCheckInterval = null;
  }
  
  console.log('启动异步状态监控...');
  isMonitoringActive = true;
  
  // 每5秒检查一次任务状态（减少频率）
  statusCheckInterval = setInterval(async () => {
    if (scanTaskModalVisible.value && isMonitoringActive) {
      await checkRunningTasksStatus();
    } else {
      // 弹窗关闭时停止监控
      stopAsyncStatusMonitoring();
    }
  }, 5000); // 从3秒改为5秒
};

const stopAsyncStatusMonitoring = () => {
  console.log('停止异步状态监控...');
  
  // 标记监控已停止
  isMonitoringActive = false;
  
  // 清理主定时器
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval);
    statusCheckInterval = null;
  }
  
  // 清理可能存在的其他定时器引用
  [statusCheckInterval].forEach(timer => {
    if (timer) {
      clearInterval(timer);
    }
  });
  
  // 等待一个微任务周期，确保正在运行的检查完成
  setTimeout(() => {
    console.log('异步状态监控已停止');
  }, 100);
};

const checkRunningTasksStatus = async () => {
  try {
    // 找到所有运行中的任务
    const runningTasks = scanTasks.value.filter(task => 
      task.status === 'running' || task.status === 'pending'
    );
    
    // 如果没有运行中的任务，停止监控
    if (runningTasks.length === 0) {
      stopAsyncStatusMonitoring();
      return;
    }
    
    for (const task of runningTasks) {
      try {
        const response = await ipAPI.getAsyncTaskStatus(task.id);
        if (response.data && response.data.code === 200) {
          const statusData = response.data.data;
          
          // 只有当状态发生变化时才更新
          const taskIndex = scanTasks.value.findIndex(t => t.id === task.id);
          if (taskIndex !== -1) {
            const currentTask = scanTasks.value[taskIndex];
            const hasStatusChanged = currentTask.status !== statusData.status;
            const hasProgressChanged = currentTask.progress !== statusData.progress;
            
            if (hasStatusChanged || hasProgressChanged) {
              // 使用 Vue 的响应式更新，减少 DOM 操作
              Object.assign(scanTasks.value[taskIndex], {
                status: statusData.status,
                progress: statusData.progress,
                result_data: statusData.result_data,
                error_message: statusData.error_message
              });
              
              // 如果任务完成，显示通知
              if (statusData.status === 'completed' && hasStatusChanged) {
                const resultData = statusData.result_data || {};
                message.success({
                  content: `任务 ${task.id} 已完成！\n发现主机: ${resultData.discovered_hosts || 0} 个\n新增IP: ${resultData.saved_count || 0} 个\n更新IP: ${resultData.updated_count || 0} 个`,
                  duration: 5
                });
                
                // 延迟刷新IP列表，避免并发更新
                setTimeout(() => {
                  loadIPList();
                }, 1000);
              }
              
              // 如果任务失败，显示错误
              if (statusData.status === 'failed' && hasStatusChanged) {
                message.error({
                  content: `任务 ${task.id} 失败：${statusData.error_message || '未知错误'}`,
                  duration: 5
                });
              }
            }
          }
        }
      } catch (error) {
        // 静默处理单个任务检查失败
        console.debug(`检查任务 ${task.id} 状态失败:`, error.message);
      }
    }
  } catch (error) {
    console.debug('检查运行任务状态失败:', error.message);
  }
};


const loadScanTasks = async () => {
  taskLoading.value = true;
  try {
    const params = {
      page: taskPagination.current,
      page_size: taskPagination.pageSize
    };
    
    // 添加查询条件
    if (taskStatusFilter.value && taskStatusFilter.value !== '') {
      params.status = taskStatusFilter.value;
    }
    if (taskNameFilter.value && taskNameFilter.value !== '') {
      params.search = taskNameFilter.value;
    }
    if (taskDateRange.value && Array.isArray(taskDateRange.value) && taskDateRange.value.length === 2) {
      params.created_after = taskDateRange.value[0].toISOString();
      params.created_before = taskDateRange.value[1].toISOString();
    }
    
    console.log('调用扫描任务API，参数:', params);
    
    // 调用后端API获取扫描任务列表
    const response = await ipAPI.getScanTasks(params);
    
    console.log('API响应:', response);
    
    if (response && response.data) {
      // 检查是否是统一响应格式（包含code字段）
      if (response.data.code !== undefined) {
        // 统一响应格式
        if (response.data.code === 200) {
          const data = response.data.data;
          // 过滤掉已取消的任务
          let tasks = data.results || [];
          tasks = tasks.filter(task => task.status !== 'cancelled');
          scanTasks.value = tasks;
          taskPagination.total = tasks.length; // 使用过滤后的数量
          console.log('成功获取扫描任务（统一格式，已过滤取消任务）:', scanTasks.value);
        } else {
          console.error('API返回错误代码:', response.data.code, '错误信息:', response.data.message);
          message.error(`获取扫描任务列表失败: ${response.data.message}`);
          scanTasks.value = [];
          taskPagination.total = 0;
        }
      } else {
        // DRF标准响应格式（直接包含count、results字段）
        console.log('检测到DRF标准响应格式');
        // 过滤掉已取消的任务
        let tasks = response.data.results || [];
        tasks = tasks.filter(task => task.status !== 'cancelled');
        scanTasks.value = tasks;
        taskPagination.total = tasks.length; // 使用过滤后的数量
        console.log('成功获取扫描任务（DRF格式，已过滤取消任务）:', scanTasks.value);
        message.success('获取扫描任务列表成功', 1);
      }
    } else {
      console.error('无效的API响应:', response);
      message.error('获取扫描任务列表失败: 无效的响应数据');
      scanTasks.value = [];
      taskPagination.total = 0;
    }
  } catch (error) {
    console.error('加载扫描任务失败:', error);
    console.error('错误详情:', {
      message: error.message,
      response: error.response,
      request: error.request
    });
    
    let errorMessage = '加载扫描任务失败';
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
    scanTasks.value = [];
    taskPagination.total = 0;
  } finally {
    taskLoading.value = false;
  }
};

const handleSearchTasks = () => {
  taskPagination.current = 1;
  loadScanTasks();
};

const handleRefreshTasks = () => {
  taskStatusFilter.value = '';
  taskDateRange.value = [];
  taskNameFilter.value = '';
  taskPagination.current = 1;
  loadScanTasks();
};


const handleTaskTableChange = (paginationInfo) => {
  taskPagination.current = paginationInfo.current;
  taskPagination.pageSize = paginationInfo.pageSize;
  loadScanTasks();
};

const handleViewTaskDetail = (record) => {
  selectedTask.value = record;
  taskDetailModalVisible.value = true;
};

const handleViewTaskResults = async (record) => {
  selectedTask.value = record;
  await loadTaskResults(record.id);
  taskResultModalVisible.value = true;
};

const handleCancelTask = async (record) => {
  try {
    // 如果任务正在运行，先停止异步处理
    if (record.status === 'running' || record.status === 'pending') {
      try {
        const stopResponse = await ipAPI.stopAsyncTask(record.id);
        if (stopResponse.data && stopResponse.data.code === 200) {
          message.success('异步任务已停止', 1);
        }
      } catch (stopError) {
        console.warn('停止异步任务失败:', stopError);
      }
    }
    
    // 取消任务
    const response = await ipAPI.cancelScanTask(record.id);
    if (response.data && response.data.code === 200) {
      message.success(`任务 ${record.task_name || record.id} 已取消`, 1);
      // 直接从列表中移除已取消的任务，而不是刷新整个列表
      scanTasks.value = scanTasks.value.filter(task => task.id !== record.id);
      taskPagination.total = scanTasks.value.length;
    } else {
      message.error('取消任务失败');
    }
  } catch (error) {
    console.error('取消任务失败:', error);
    message.error(`取消任务失败: ${error.response?.data?.message || error.message}`);
  }
};

const handleDeleteTask = async (record) => {
  try {
    // 显示确认对话框
    await new Promise((resolve, reject) => {
      const modal = Modal.confirm({
        title: '确认删除任务',
        content: `确定要删除任务 "${record.id}" 吗？该操作不可恢复！`,
        okText: '确认删除',
        okType: 'danger',
        cancelText: '取消',
        onOk: () => resolve(true),
        onCancel: () => reject(new Error('User cancelled'))
      });
    });
    
    // 调用删除API
    const response = await ipAPI.deleteScanTask(record.id);
    
    if (response.data && response.data.code === 200) {
      message.success(`任务 "${record.id}" 已成功删除`, 1);
      
      // 直接从列表中移除已删除的任务，而不是刷新整个列表
      scanTasks.value = scanTasks.value.filter(task => task.id !== record.id);
      taskPagination.total = scanTasks.value.length;
    } else {
      message.error('删除任务失败');
    }
  } catch (error) {
    if (error.message !== 'User cancelled') {
      console.error('删除任务失败:', error);
      message.error(`删除任务失败: ${error.response?.data?.message || error.message}`);
    }
  }
};

const loadTaskResults = async (taskId) => {
  resultLoading.value = true;
  try {
    const response = await ipAPI.getScanTaskResults(taskId);
    if (response.data && response.data.code === 200) {
      taskResults.value = response.data.data || [];
    } else {
      message.error('获取扫描结果失败');
      taskResults.value = [];
    }
  } catch (error) {
    console.error('加载扫描结果失败:', error);
    message.error(`加载扫描结果失败: ${error.response?.data?.message || error.message}`);
    taskResults.value = [];
  } finally {
    resultLoading.value = false;
  }
};

// 任务状态相关工具函数
const getTaskStatusColor = (status) => {
  const colorMap = {
    'pending': 'default',
    'running': 'processing',
    'completed': 'success',
    'failed': 'error',
    'cancelled': 'warning'
  };
  return colorMap[status] || 'default';
};

const getTaskStatusText = (status) => {
  const textMap = {
    'pending': '等待中',
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'cancelled': '已取消'
  };
  return textMap[status] || status;
};

// 判断是否为长时间运行的任务
const isLongRunningTask = (task) => {
  if (task.status !== 'running') {
    return false;
  }
  
  // 检查任务的运行时间，如果超过180秒（5分钟）则认为是长时间运行
  if (task.started_at) {
    const startTime = new Date(task.started_at);
    const currentTime = new Date();
    const diffInSeconds = (currentTime - startTime) / 1000;
    return diffInSeconds > 180; // 3分钟
  }
  
  // 根据进度判断：如果进度大于30%但仍在运行，可能是长时间任务
  return task.progress > 30;
};

// 获取取消按钮的文本
const getCancelButtonText = (record) => {
  if (record.status === 'running' && isLongRunningTask(record)) {
    return '停止';
  }
  return '取消';
};

// 获取取消按钮的提示信息
const getCancelButtonTitle = (record) => {
  if (record.status === 'completed') {
    return '任务已完成，无法取消';
  }
  if (record.status === 'cancelled') {
    return '任务已取消';
  }
  if (record.status === 'failed') {
    return '任务已失败，无法取消';
  }
  if (record.status === 'running') {
    if (isLongRunningTask(record)) {
      return '停止正在持续运行的任务。任务将会立即停止，不再检查新的主机发现';
    }
    return '取消正在运行的任务';
  }
  if (record.status === 'pending') {
    return '取消等待中的任务';
  }
  return '取消任务';
};

// 获取删除按钮的提示信息
const getDeleteButtonTitle = (record) => {
  if (record.status === 'running') {
    return '任务正在运行中，无法删除';
  }
  if (record.status === 'pending') {
    return '任务正在等待处理，无法删除';
  }
  return `删除任务 ${record.id} 的记录（不可恢复）`;
};




const handleRefresh = () => {
  loadIPList();
  message.success('数据已刷新', 1);
};

const handleSave = async () => {
  try {
    await formRef.value.validate();
    
    // 转换字段名：前端驼峰命名转后端下划线命名
    const submitData = {
      ip_address: formData.ipAddress,
      hostname: formData.hostname,
      status: formData.status,
      type: formData.type,
      mac_address: formData.macAddress,
      device: formData.device,
      subnet: formData.subnet,
      description: formData.description
    };
    
    if (editingIP.value) {
      // 编辑模式
      await ipAPI.updateIP(editingIP.value.id, submitData);
      message.success('IP信息更新成功', 1);
    } else {
      // 新增模式
      await ipAPI.createIP(submitData);
      message.success('IP添加成功', 1);
    }
    
    editModalVisible.value = false;
    resetForm();
    await loadIPList();
  } catch (error) {
    console.error('保存IP失败:', error);
    message.error(`保存失败: ${error.response?.data?.message || error.message}`);
  }
};

const handleCancel = () => {
  editModalVisible.value = false;
  resetForm();
};

const resetForm = () => {
  Object.assign(formData, {
    ipAddress: '',
    hostname: '',
    status: 'available',
    type: 'static',
    macAddress: '',
    device: '',
    subnet: '',
    description: ''
  });
  formRef.value?.resetFields();
};

// 组件挂载时初始化数据
onMounted(() => {
  // 防止重复初始化
  if (isComponentInitialized) {
    console.log('IP列表组件已初始化，跳过重复初始化');
    return;
  }
  
  console.log('IP列表组件挂载，开始加载IP数据...');
  isComponentInitialized = true;
  
  // 从 URL 参数中读取分页设置
  const urlParams = new URLSearchParams(window.location.search);
  const pageParam = urlParams.get('page');
  const pageSizeParam = urlParams.get('page_size');
  
  if (pageParam && !isNaN(parseInt(pageParam))) {
    pagination.current = parseInt(pageParam);
    console.log('从 URL 读取到 page 参数:', pagination.current);
  }
  
  if (pageSizeParam && !isNaN(parseInt(pageSizeParam))) {
    const requestedPageSize = parseInt(pageSizeParam);
    // 检查是否在允许的选项中
    const allowedSizes = [10, 20, 50, 100];
    if (allowedSizes.includes(requestedPageSize)) {
      pagination.pageSize = requestedPageSize;
      console.log('从 URL 读取到 page_size 参数:', pagination.pageSize);
    } else {
      console.warn(`URL 中的 page_size=${requestedPageSize} 不在允许范围内，使用默认值 ${pagination.pageSize}`);
    }
  }
  
  // 全局抑制 ResizeObserver 错误
  const originalError = console.error;
  console.error = function(...args) {
    if (args[0] && args[0].toString().includes('ResizeObserver loop completed')) {
      return; // 忽略 ResizeObserver 错误
    }
    originalError.apply(console, args);
  };
  
  // 使用现有的错误抑制函数
  suppressResizeObserverError();
  
  // 延迟加载数据，避免DOM渲染冲突
  nextTick(() => {
    loadIPList();
  });
});

// 组件即将卸载时的预清理
onBeforeUnmount(() => {
  console.log('IP列表组件即将卸载，进行预清理...');
  
  // 立即停止所有监控活动
  stopAsyncStatusMonitoring();
  
  // 关闭所有弹窗，避免残留的DOM元素
  scanTaskModalVisible.value = false;
  taskDetailModalVisible.value = false;
  taskResultModalVisible.value = false;
  editModalVisible.value = false;
  detailModalVisible.value = false;
  scanModalVisible.value = false;
});

// 组件销毁时清理资源
onUnmounted(() => {
  console.log('IP列表组件销毁，清理监控定时器...');
  
  // 1. 停止异步状态监控
  stopAsyncStatusMonitoring();
  
  // 2. 清理所有可能的定时器
  if (statusCheckInterval) {
    clearInterval(statusCheckInterval);
    statusCheckInterval = null;
  }
  
  // 3. 强制清理所有ResizeObserver实例
  try {
    // 查找页面中所有的ResizeObserver实例并断开连接
    const tableElements = document.querySelectorAll('.modern-table, .ant-table, .ant-progress');
    tableElements.forEach(element => {
      // 移除可能的观察器
      if (element._resizeObserver) {
        element._resizeObserver.disconnect();
        delete element._resizeObserver;
      }
    });
  } catch (error) {
    console.debug('清理ResizeObserver时出错:', error.message);
  }
  
  // 4. 清理组件状态
  scanTasks.value = [];
  ipData.value = [];
  taskResults.value = [];
  
  // 5. 重置初始化状态标记
  isComponentInitialized = false;
  isMonitoringActive = false;
  
  console.log('IP列表组件资源清理完成');
});

// 监听扫描任务弹窗状态
watch(scanTaskModalVisible, (newValue, oldValue) => {
  console.log(`扫描任务弹窗状态变化: ${oldValue} -> ${newValue}`);
  
  if (!newValue) {
    // 弹窗关闭时停止监控
    console.log('弹窗关闭，停止异步监控');
    stopAsyncStatusMonitoring();
  }
});
</script>

<style scoped>
/* 简洁蓝白背景 */
.ip-list-container {
  background: #f8fafc;
  min-height: 100vh;
}

/* 简洁卡片样式 */
.table-card {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e40af;
}

.table-extra {
  display: flex;
  align-items: center;
}

/* 简洁表格样式 */
:deep(.modern-table) {
  border-radius: 6px;
  overflow: hidden;
  background: #ffffff;
}

:deep(.modern-table .ant-table-thead > tr > th) {
  background: #f1f5f9;
  border: none;
  color: #374151;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.modern-table .ant-table-tbody > tr > td) {
  border: none;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}

:deep(.modern-table .ant-table-tbody > tr:hover > td) {
  background: #f8fafc;
}

:deep(.modern-table .ant-table-tbody > tr:last-child > td) {
  border-bottom: none;
}

/* 简洁按钮样式 */
:deep(.ant-btn-primary) {
  background: #2563eb;
  border: 1px solid #2563eb;
  border-radius: 6px;
  height: 36px;
  font-weight: 500;
}

:deep(.ant-btn-primary:hover) {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

:deep(.ant-btn:not(.ant-btn-primary)) {
  border-radius: 6px;
  height: 36px;

  background: #ffffff;
  font-weight: 500;
}

:deep(.ant-btn:not(.ant-btn-primary):hover) {
  border-color: #2563eb;
  color: #2563eb;
}

/* 简洁标签样式 */
:deep(.ant-tag) {
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 500;
  border: 1px solid;
  font-size: 12px;
}

/* 状态标签简洁色彩 */
:deep(.ant-tag-success) {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}

:deep(.ant-tag-processing) {
  background: #dbeafe;
  color: #1e40af;
  border-color: #93c5fd;
}

:deep(.ant-tag-warning) {
  background: #fef3c7;
  color: #92400e;
  border-color: #fde68a;
}

:deep(.ant-tag-error) {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fecaca;
}

:deep(.ant-tag-default) {
  background: #f3f4f6;
  color: #374151;
  border-color: #d1d5db;
}

/* 保护状态样式 */
.protected-button {
  opacity: 0.5;
  cursor: not-allowed !important;
}

.protected-button:hover {
  background: none !important;
  border-color: transparent !important;
  transform: none !important;
}

/* 保护信息提示 */
.protection-info {
  margin-top: 4px;
  color: #718096;
  font-style: italic;
}

/* 统计卡片样式 */
:deep(.ant-statistic) {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.ant-statistic-title) {
  color: #4a5568;
  font-weight: 600;
}

:deep(.ant-statistic-content) {
  color: #2d3748;
  font-weight: 700;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ip-list-container {
    padding: 16px;
  }
  
  .table-header {
    padding: 16px 20px;
    flex-wrap: wrap;
    gap: 12px;
  }
  
  .table-title {
    font-size: 18px;
  }
  
  .table-extra {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  :deep(.modern-table .ant-table-thead > tr > th),
  :deep(.modern-table .ant-table-tbody > tr > td) {
    padding: 12px 16px;
  }
}

/* 滚动条美化 */
:deep(.ant-table-body)::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

:deep(.ant-table-body)::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

:deep(.ant-table-body)::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
}

:deep(.ant-table-body)::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  font-size: 12px;
  line-height: 1.4;
}

.table-header-text {
  font-weight: 600;
  color: #374151;
}

/* IP地址单元格 */
.ip-address-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ip-info {
  flex: 1;
}

.ip-address {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #1890ff;
  font-size: 14px;
  margin-bottom: 2px;
}

.ip-hostname {
  font-size: 12px;
  color: #6b7280;
}

/* 状态标签 */
.status-tag {
  border-radius: 6px;
  font-weight: 500;
  font-size: 12px;
  padding: 4px 8px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* 类型标签 */
.type-tag {
  border-radius: 6px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Ping状态 */
.ping-status {
  font-weight: 500;
}

/* 最后在线时间 */
.last-seen {
  color: #6b7280;
  font-size: 12px;
}

.no-data {
  color: #9ca3af;
  font-style: italic;
}

.form-section {
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
  padding-bottom: 8px;
  border-bottom: 1px solid #e8f3ff;
}

.input-hint {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 4px;
}

/* 扫描弹窗样式 */
:deep(.ant-modal-body) {
  max-height: 600px;
  overflow-y: auto;
}
:deep(.detail-modal .ant-modal-content) {
  border-radius: 8px;
}

:deep(.edit-modal .ant-modal-content) {
  border-radius: 8px;
}

/* 按钮样式优化 */
:deep(.ant-btn-primary) {
  background: #1890ff;
  border-color: #1890ff;
  border-radius: 6px;
}

:deep(.ant-btn-primary:hover) {
  background: #40a9ff;
  border-color: #40a9ff;
}

:deep(.ant-btn) {
  border-radius: 6px;
}

/* 输入框样式 */
:deep(.ant-input) {
  border-radius: 6px;
  border-color: #e8f3ff;
}

:deep(.ant-input:focus) {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
}

:deep(.ant-select .ant-select-selector) {
  border-radius: 6px;
  border-color: #e8f3ff;
}

:deep(.ant-select:not(.ant-select-disabled):hover .ant-select-selector) {
  border-color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  
  .filter-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
}

@media (max-width: 768px) {
  .ip-list-container {
    padding: 16px;
  }
  
  .filter-content {
    padding: 16px;
  }
  
  .filter-header {
    gap: 12px;
  }
  
  .filter-title {
    font-size: 16px;
  }
  
  .title-icon {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .ip-list-container {
    padding: 12px;
  }
  
  .ip-address-cell {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .filter-content {
    padding: 12px;
  }
  
  .filter-actions {
    flex-direction: column;
    gap: 8px;
  }
}

/* 表格容器样式 */
.table-container {
  overflow: hidden;
  background: white;
  border-radius: 8px;
}

/* 批量操作工具栏 */
.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f0f7ff;
  border: 1px solid #d6e4ff;
  border-radius: 8px;
  margin-bottom: 16px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.batch-info {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #1890ff;
  font-weight: 500;
}

.batch-info strong {
  color: #1890ff;
  margin: 0 4px;
  font-weight: 600;
}

/* 监控状态按钮样式 */
.monitoring-enabled {
  background: #f6ffed !important;
  border-color: #b7eb8f !important;
}

.monitoring-enabled:hover {
  background: #d9f7be !important;
  border-color: #95de64 !important;
}

/* 统计卡片样式 */
.stat-card {
  border-radius: 8px;
  border: 1px solid #e8f3ff;
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* 批量Ping弹窗样式 - 重新设计 */
.ping-confirm-phase,
.ping-testing-phase,
.ping-result-phase {
  padding: 8px 0;
}

/* 阶段头部 */
.phase-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid;
  transition: all 0.3s ease;
}

.ping-confirm-phase .phase-header {
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f3ff 100%);
  border-color: #91caff;
}

.ping-testing-phase .phase-header {
  background: linear-gradient(135deg, #fff7e6 0%, #fff2e8 100%);
  border-color: #ffec8b;
}

.ping-result-phase .phase-header {
  background: linear-gradient(135deg, #f6ffed 0%, #f0f9e8 100%);
  border-color: #d9f7be;
}

.phase-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  font-size: 24px;
  position: relative;
}

.phase-icon.confirm {
  background: rgba(24, 144, 255, 0.1);
  color: #1890ff;
}

.phase-icon.testing {
  background: rgba(250, 140, 22, 0.1);
  color: #fa8c16;
}

.phase-icon.success {
  background: rgba(82, 196, 26, 0.1);
  color: #52c41a;
}

.phase-content {
  flex: 1;
}

.phase-title {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
}

.phase-description {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
}

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
  line-height: 1;
}

.stat-number.primary { color: #1890ff; }
.stat-number.success { color: #52c41a; }
.stat-number.error { color: #ff4d4f; }

.stat-label {
  font-size: 12px;
  color: #8c8c8c;
  text-transform: uppercase;
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* 测试参数 */
.test-parameters {
  margin-bottom: 20px;
}

.param-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.param-list {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #f0f0f0;
}

.param-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.param-item:last-child {
  margin-bottom: 0;
}

.param-label {
  color: #8c8c8c;
  font-size: 14px;
}

.param-value {
  color: #262626;
  font-weight: 500;
  font-size: 14px;
}

/* 提示信息 */
.warning-tip,
.tech-tip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
}

.warning-tip {
  background: rgba(250, 140, 22, 0.05);
  border: 1px solid rgba(250, 140, 22, 0.2);
}

.tech-tip {
  background: rgba(24, 144, 255, 0.05);
  border: 1px solid rgba(24, 144, 255, 0.2);
}

.tip-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.tip-text {
  font-size: 13px;
  color: #595959;
  line-height: 1.5;
}

/* 测试中的动画和状态 */
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #fa8c16;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  position: absolute;
  top: 16px;
  left: 16px;
}

.testing-icon {
  margin-left: 4px;
  z-index: 1;
}

.testing-info {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #8c8c8c;
  font-size: 14px;
}

.info-value {
  color: #262626;
  font-weight: 500;
  font-size: 14px;
}

.info-value.status-active {
  color: #fa8c16;
  animation: pulse 2s infinite;
}

/* 进度条 */
.progress-section {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #f5f5f5;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #1890ff, #40a9ff, #69c0ff, #40a9ff, #1890ff);
  background-size: 200% 100%;
  border-radius: 3px;
  animation: progressFlow 2s ease-in-out infinite;
}

.progress-text {
  text-align: center;
  font-size: 13px;
  color: #8c8c8c;
  font-style: italic;
}

/* 结果阶段 */
.success-icon {
  font-size: 32px;
  animation: bounce 0.6s ease-out;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.result-card {
  text-align: center;
  padding: 24px 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease-out;
}

.result-card.success {
  border-color: #d9f7be;
  background: #f6ffed;
}

.result-card.error {
  border-color: #ffccc7;
  background: #fff2f0;
}

.result-card.primary {
  border-color: #91caff;
  background: #f0f7ff;
}

.result-card:nth-child(1) { animation-delay: 0.1s; }
.result-card:nth-child(2) { animation-delay: 0.2s; }
.result-card:nth-child(3) { animation-delay: 0.3s; }

.result-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 8px;
  line-height: 1;
}

.result-card.success .result-number { color: #52c41a; }
.result-card.error .result-number { color: #ff4d4f; }
.result-card.primary .result-number { color: #1890ff; }

.result-label {
  font-size: 12px;
  color: #8c8c8c;
  text-transform: uppercase;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.result-summary {
  text-align: center;
  padding: 16px;
  background: rgba(82, 196, 26, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(82, 196, 26, 0.2);
  margin-bottom: 24px;
  animation: fadeIn 0.5s ease-in 0.4s both;
}

.summary-item {
  margin-bottom: 8px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-item.success-rate .summary-value {
  color: #52c41a;
  font-weight: 600;
  font-size: 16px;
}

.summary-item.test-time .summary-value {
  color: #8c8c8c;
  font-size: 13px;
}

.summary-label {
  color: #8c8c8c;
  font-size: 14px;
}

/* 按钮操作区域 */
.modal-actions {
  text-align: center;
  margin-top: 8px;
}

/* 动画定义 */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes progressFlow {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounce {
  0%, 20%, 53%, 80%, 100% {
    transform: translate3d(0, 0, 0);
  }
  40%, 43% {
    transform: translate3d(0, -8px, 0);
  }
  70% {
    transform: translate3d(0, -4px, 0);
  }
  90% {
    transform: translate3d(0, -2px, 0);
  }
}

:deep(.ping-info-header) {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f3ff 100%);
  border-radius: 8px;
  border: 1px solid #d4edda;
}

:deep(.ping-icon) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: rgba(24, 144, 255, 0.1);
  border-radius: 50%;
}

:deep(.ping-title) {
  font-size: 18px;
  font-weight: 600;
  color: #1890ff;
  margin: 0;
}

:deep(.ping-stats) {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

:deep(.stat-item) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.stat-label) {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

:deep(.stat-value) {
  font-size: 14px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 4px;
}

:deep(.stat-value.primary) {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

:deep(.stat-value.success) {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

:deep(.stat-value.error) {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

:deep(.ping-description) {
  margin-bottom: 16px;
}

:deep(.ping-warning) {
  padding: 12px;
  background: rgba(250, 140, 22, 0.05);
  border: 1px solid rgba(250, 140, 22, 0.2);
  border-radius: 6px;
}

/* 批量Ping结果弹窗样式 */
:deep(.ping-result-content) {
  padding: 8px 0;
}

:deep(.result-header) {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: linear-gradient(135deg, #f6ffed 0%, #f0f9e8 100%);
  border-radius: 8px;
  border: 1px solid #d9f7be;
}

:deep(.result-icon.success) {
  font-size: 32px;
  color: #52c41a;
}

:deep(.result-title) {
  font-size: 18px;
  font-weight: 600;
  color: #52c41a;
  margin: 0;
}

:deep(.result-stats) {
  padding: 0;
}

:deep(.result-grid) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

:deep(.result-item) {
  text-align: center;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

:deep(.result-number) {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

:deep(.result-number.success) {
  color: #52c41a;
}

:deep(.result-number.error) {
  color: #ff4d4f;
}

:deep(.result-number.primary) {
  color: #1890ff;
}

:deep(.result-label) {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  font-weight: 500;
}

:deep(.result-summary) {
  text-align: center;
  padding: 16px;
  background: rgba(82, 196, 26, 0.05);
  border-radius: 6px;
  border: 1px solid rgba(82, 196, 26, 0.2);
}

/* 进度消息美化 */
:deep(.ant-message-custom-content) {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 弹窗按钮美化 */
:deep(.ant-modal-confirm .ant-btn-primary) {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
}

:deep(.ant-modal-confirm .ant-btn-primary:hover) {
  background: linear-gradient(135deg, #40a9ff 0%, #69c0ff 100%);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.4);
}

/* Zabbix模板选择抽屉样式 */
.template-drawer-content {
  padding: 0;
}

.ip-info-card {
  margin-bottom: 24px;
  border-radius: 12px;
  border: 1px solid #e8f3ff;
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f3ff 100%);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.ip-info-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ip-icon {
  font-size: 24px;
  color: #1890ff;
}

.ip-details h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}

.ip-details p {
  margin: 0;
  font-size: 12px;
  color: #8c8c8c;
}

/* 搜索和筛选区域 */
.template-search-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

.search-bar {
  margin-bottom: 20px;
  position: relative;
}

.search-bar .ant-input-search {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-bar .ant-input-search:hover {
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
}

.search-bar .ant-input-search:focus-within {
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.category-filter {
  margin: 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}
.category-filter-tag {
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  background: #f5f5f5;
  border: 1px solid #f0f0f0;
}

.category-filter-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background: white;
}

.category-filter-tag-selected {
  background: #1890ff !important;
  color: white !important;
  border-color: #1890ff !important;
}

.category-filter-tag-selected .category-count {
  color: rgba(255, 255, 255, 0.8) !important;
}

.category-filter-tag-selected .category-selected {
  background: white !important;
  color: #1890ff !important;
}

.category-tag-selected {
  background: #1890ff !important;
  color: white !important;
  border-color: #1890ff !important;
}

.category-filter-icon {
  font-size: 14px;
}

.category-count {
  font-weight: 600;
  margin-left: 4px;
}

.category-selected {
  background: rgba(255, 255, 255, 0.3);
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  margin-left: 4px;
}

.clear-filter-tag {
  cursor: pointer;
  font-weight: 600;
}

/* 模板列表 */
.template-list {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.empty-templates {
  text-align: center;
  padding: 80px 20px;
  animation: fadeIn 0.3s ease;
}

.empty-templates .ant-empty {
  margin-bottom: 24px;
}

.empty-templates .ant-empty-image {
  height: 120px;
}

.empty-templates .ant-empty-description {
  font-size: 15px;
  color: #666;
}

.empty-templates .ant-btn {
  margin-top: 16px;
  border-radius: 8px;
}

.template-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
  padding: 40px;
}

.template-loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid #f0f0f0;
  border-top: 4px solid #1890ff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.selected-templates-info {
  margin-bottom: 20px;
  animation: slideDown 0.3s ease-out;
}

.search-results-info {
  margin: 12px 0;
  padding: 12px 16px;
  background: #f6f6f6;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  animation: fadeIn 0.3s ease;
}

.search-results-info strong {
  color: #1890ff;
  font-weight: 600;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.template-grid {
  animation: fadeIn 0.5s ease;
}

.template-card {
  animation: fadeInUp 0.4s ease-out;
  animation-fill-mode: both;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 分类样式 */
.template-category {
  margin-bottom: 20px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.category-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  border-bottom: 1px solid #f0f0f0;
}

.category-title-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.category-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #262626;
}

.category-icon {
  font-size: 16px;
  color: #1890ff;
}

.category-stats {
  display: flex;
  gap: 8px;
  align-items: center;
}

.selected-badge {
  margin-left: 8px;
}

.expand-button {
  color: #666;
  border: none;
  background: transparent;
}

.expand-button:hover {
  color: #1890ff;
  background: rgba(24, 144, 255, 0.1);
}

/* 模板网格 */
.template-grid-wrapper {
  padding: 16px;
  overflow: hidden;
  max-width: 100%;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  width: 100%;
  max-width: 100%;
  padding: 0;
  justify-content: start;
}

.template-card-container {
  position: relative;
}

.template-checkbox {
  width: 100%;
  margin: 0;
}

:deep(.template-checkbox .ant-checkbox) {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 10;
  background: white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.template-card {
  width: 100%;
  max-width: 260px;
  height: 140px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
}

.template-card:hover {
  border-color: #40a9ff;
  box-shadow: 0 12px 24px rgba(24, 144, 255, 0.25);
  transform: translateY(-6px);
}

.template-card.selected {
  border-color: #40a9ff;
  background: linear-gradient(135deg, #e6f7ff 0%, #d6f0ff 100%);
  box-shadow: 0 12px 28px rgba(24, 144, 255, 0.35);
  transform: translateY(-6px);
}

.template-card.selected::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 0 36px 36px 0;
  border-color: transparent #40a9ff transparent transparent;
}

.template-card.selected::before {
  content: '✓';
  position: absolute;
  top: 6px;
  right: 6px;
  color: white;
  font-size: 16px;
  font-weight: bold;
  z-index: 2;
}

:deep(.template-card .ant-card-head) {
  min-height: auto;
  padding: 12px 16px 8px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
}

:deep(.template-card .ant-card-head-title) {
  padding: 0;
}

:deep(.template-card .ant-card-body) {
  padding: 12px 16px;
  height: calc(100% - 50px);
  overflow: hidden;
}

.template-header {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 8px 10px;
  background: #fafafa;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.template-icon {
  font-size: 14px;
  color: #1890ff;
  flex-shrink: 0;
}

.template-name {
  font-size: 12px;
  font-weight: 600;
  color: #262626;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  transition: all 0.2s ease;
}

.template-card:hover .template-name {
  color: #40a9ff;
}

.template-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 8px 10px;
  flex: 1;
}

.template-description {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 8px;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.template-stats {
  display: flex;
  justify-content: space-between;
  margin: 6px 0;
  padding: 6px 8px;
  background: #f8f9fa;
  border-radius: 4px;
  flex-shrink: 0;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 10px;
  color: #666;
  margin-bottom: 1px;
  font-weight: 400;
}

.stat-value {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #1890ff;
}

.template-groups {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  align-items: center;
  margin-top: auto;
  padding-top: 4px;
}

.template-groups .ant-tag {
  font-size: 9px;
  padding: 1px 4px;
  margin: 0;
  border-radius: 8px;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  color: #1890ff;
  line-height: 1.2;
}

.template-groups .ant-tag:hover {
  background: linear-gradient(135deg, #e0e0e0 0%, #d0d0d0 100%);
}

.more-groups {
  font-size: 10px;
  color: #888;
  font-weight: 500;
  background: #f5f5f5;
  padding: 1px 4px;
  border-radius: 8px;
}

/* 模板抽屉响应式设计 */
@media (max-width: 1400px) {
  .template-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }
}

@media (max-width: 1200px) {
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .template-card {
    height: 140px;
  }
  
  .template-header {
    padding: 10px 10px 5px;
  }
  
  .template-name {
    font-size: 13px;
  }
  
  .template-icon {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .template-grid-wrapper {
    padding: 12px;
  }
  
  .template-card {
    height: 120px;
  }
  
  .template-header {
    padding: 8px 8px 4px;
    gap: 6px;
  }
  
  .template-name {
    font-size: 12px;
  }
  
  .template-icon {
    font-size: 12px;
  }
  
  .template-stats {
    margin: 6px 0;
    padding: 6px 0;
  }
  
  .stat-label {
    font-size: 10px;
  }
  
  .stat-value {
    font-size: 12px;
  }
  
  .template-groups {
    margin-top: 6px;
    padding: 0 8px;
    gap: 3px;
  }
  
  .template-groups .ant-tag {
    font-size: 9px;
    padding: 1px 4px;
  }
  
  .more-groups {
    font-size: 9px;
    padding: 1px 3px;
  }
  
  .category-header {
    padding: 10px 12px;
  }
  
  .category-title {
    font-size: 13px;
  }
  
  .category-icon {
    font-size: 14px;
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .template-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .category-header {
    padding: 12px 16px;
  }
  
  .template-search-section {
    padding: 16px;
  }
}
</style>