<template>
  <div class="software-asset-list-container">
    <!-- 软件资产表格组件 -->
    <SoftwareAssetTable
      ref="softwareTableRef"
      :loading="loading"
      :dataSource="tableData"
      :pagination="pagination"
      :currentFilter="currentFilter"
      :assetStatus="assetStatus"
      :selected-row-keys="selectedRowKeys"
      :totalCount="statistics.total"
      :activeCount="statistics.active"
      :retiredCount="statistics.retired"
      :searchKeyword="searchKeyword"
      :blockUpCount="statistics.block_up"
      :detailDialogVisible="detailDialogVisible"
      @search="handleSearch"
      @reset="handleReset"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
      @selection-change="handleSelectionChange"
      @view="handleView"
      @delete="handleDelete"
      @license="handleLicense"
      @history="handleHistory"
      @batch-delete="handleBatchDelete"
      @batch-export="handleBatchExport"
      @export="handleExport"
      @statsFilter="handleStatsFilter"
      @add="showAddDialog"
      @viewDetails="viewDetails"
      @import="showImportDialog"
      @searchInput="handleSearchInput"
      @editAsset="handleEdit"
      @table-change="handleTableChange"
    />

    <!-- 软件监控操作组件 -->
    <SoftwareMonitoringActions
      ref="monitoringActionsRef"
      :visible="false"
      @refresh="fetchData"
    />

    <!-- 新增/编辑对话框 -->
    <SoftwareAssetForm
      v-model:visible="formDialogVisible"
      :currentItem="currentItem"
      :is-edit="isEdit"
      @success="handleFormSuccess"
    />

    <!-- 详情对话框 -->
    <SoftwareAssetDetail
      v-model:visible="detailDialogVisible"
      :softwareAssetId="currentAssetId"
    />


    <!-- 导入对话框 -->
    <SoftwareAssetImport
      v-model:visible="importDialogVisible"
      @success="handleImportSuccess"
    />

    <!-- 许可证管理对话框 -->
    <a-modal
      v-model:open="licenseModalVisible"
      title="许可证管理"
      width="800px"
      @ok="handleLicenseConfirm"
      @cancel="handleLicenseCancel"
    >
      <a-form :model="licenseFormData" layout="vertical">
        <a-form-item label="许可证数量">
          <a-input-number
            v-model:value="licenseFormData.license_count"
            :min="0"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="许可证到期日期">
          <a-date-picker
            v-model:value="licenseFormData.license_expiry_date"
            style="width: 100%"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 历史记录弹窗 -->
    <a-modal
      v-model:open="historyModalVisible"
      title="更新历史记录"
      width="1200px"
      :footer="null"
      @cancel="historyModalVisible = false"
    >
      <a-tabs v-model:activeKey="historyActiveTab">
        <a-tab-pane tab="许可证更新记录" key="license">
          <div class="history-section">
            <div class="history-header">
              <h4>许可证更新记录</h4>
              <a-button type="primary" size="small" @click="loadLicenseHistory">
                刷新记录
              </a-button>
            </div>
            
            <a-table
              :data-source="licenseHistory"
              :columns="licenseHistoryColumns"
              bordered
              :loading="licenseHistoryLoading"
              :pagination="false"
              :locale="{ emptyText: '暂无更新记录' }"
            />
          </div>
        </a-tab-pane>
        
        <a-tab-pane tab="版本更新记录" key="version">
          <div class="history-section">
            <div class="history-header">
              <h4>版本更新记录</h4>
              <a-button type="primary" size="small" @click="loadVersionHistory">
                刷新记录
              </a-button>
            </div>
            
            <a-table
              :data-source="versionHistory"
              :columns="versionHistoryColumns"
              bordered
              :loading="versionHistoryLoading"
              :pagination="false"
              :locale="{ emptyText: '暂无更新记录' }"
            />
          </div>
        </a-tab-pane>
      </a-tabs>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted , nextTick } from 'vue'
import { message, Modal } from 'ant-design-vue'
import SoftwareAssetTable from '@/components/business/SoftwareAssetTable.vue'
import SoftwareMonitoringActions from '@/components/business/SoftwareMonitoringActions.vue'
import SoftwareAssetForm from '@/components/business/SoftwareAssetForm.vue'
import SoftwareAssetDetail from '@/components/business/SoftwareAssetDetail.vue'
import SoftwareAssetImport from '@/components/business/SoftwareAssetImport.vue'
import softwareAssetApi from '@/api/softwareAsset'
import { dictionaryAPI } from '@/api'
import { formatDate } from '@/utils/date'

// 组件引用
const softwareTableRef = ref(null)
const monitoringActionsRef = ref(null)

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const selectedItems = ref([])
const selectedRowKeys = ref([])
const formDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const importDialogVisible = ref(false)
const licenseModalVisible = ref(false)
const historyModalVisible = ref(false)
const isEdit = ref(false)
const currentItem = ref({})
const currentAssetId = ref(null)
const licenseFormData = ref({})
const historyActiveTab = ref('license')
const currentHistoryAsset = ref(null)
const licenseHistory = ref([])
const versionHistory = ref([])
const licenseHistoryLoading = ref(false)
const versionHistoryLoading = ref(false)
const assetStatusCount = ref(null)

// 软件资产搜索条件
const searchKeyword = ref("")
const assetStatus = ref("") ;
const softwareType = ref("") ;
const manufacturer = ref("") ;
// 获取软件列表数据指向参数
const currentFilter = ref("in_use") ; 

// 字典数据
const assetStatusOptions = ref([])
const softwareTypeOptions = ref([])

// 搜索表单
const searchForm = reactive({
  software_name: '',
  version: '',
  manufacturer: '',
  asset_status: '',
  software_type: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})


// 统计计算属性
const statistics = computed(() => {
  const total = assetStatusCount.value.use_count + assetStatusCount.value.block_up_count
  const active = assetStatusCount.value.use_count
  const block_up = assetStatusCount.value.block_up_count
  console.log(total , active, block_up)
  return {
    total: pagination.total || 0,
    active,
    block_up
  }
})


// 历史记录表格列配置
const licenseHistoryColumns = [
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    width: 180,
    customRender: ({ text }) => {
      return text ? new Date(text).toLocaleString() : '-'
    }
  },
  {
    title: '更新方式',
    dataIndex: 'update_method',
    key: 'update_method',
    width: 100,
    customRender: ({ text }) => {
      return text === 'manual' ? '手动' : '自动'
    }
  },
  {
    title: '更新前许可证信息',
    dataIndex: 'old_license_info',
    key: 'old_license_info',
    customRender: ({ text }) => {
      if (!text) return '-'
      try {
        const info = typeof text === 'string' ? JSON.parse(text) : text
        return `许可证数量: ${info.license_count || '-'}, 到期日期: ${info.expiry_date || '-'}`
      } catch (e) {
        return text
      }
    }
  },
  {
    title: '更新后许可证信息',
    dataIndex: 'new_license_info',
    key: 'new_license_info',
    customRender: ({ text }) => {
      if (!text) return '-'
      try {
        const info = typeof text === 'string' ? JSON.parse(text) : text
        return `许可证数量: ${info.license_count || '-'}, 到期日期: ${info.expiry_date || '-'}`
      } catch (e) {
        return text
      }
    }
  },
  {
    title: '更新人',
    dataIndex: 'updated_by',
    key: 'updated_by',
    width: 120
  }
]
const versionHistoryColumns = [
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    width: 180,
    customRender: ({ text }) => {
      return text ? new Date(text).toLocaleString() : '-'
    }
  },
  {
    title: '更新方式',
    dataIndex: 'update_method',
    key: 'update_method',
    width: 100,
    customRender: ({ text }) => {
      return text === 'manual' ? '手动' : '自动'
    }
  },
  {
    title: '更新前版本',
    dataIndex: 'old_version',
    key: 'old_version',
    width: 150
  },
  {
    title: '更新后版本',
    dataIndex: 'new_version',
    key: 'new_version',
    width: 150
  },
  {
    title: '更新人',
    dataIndex: 'updated_by',
    key: 'updated_by',
    width: 120
  }
]

// 加载软件资产列表数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      ...searchForm
    }
    // 添加搜索条件
    if (searchKeyword.value && searchKeyword.value.trim()) {
      params.search = searchKeyword.value.trim();
    }
    if (assetStatus.value) {
      params.status = assetStatus.value;
    }
    if (softwareType.value) {
      params.type = softwareType.value;
    }
    if (manufacturer.value) {
      params.manufacturer = manufacturer.value;
    }

    console.log('当前分页状态:', {
      current: pagination.current,
      pageSize: pagination.pageSize,
      total: pagination.total
    });
    // 过滤空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    // 向后端请求数据
    console.log('请求参数:', params);
    const response = await  softwareAssetApi.getInUseList(params)
    // 更新传入子组件数据
    tableData.value = response.data.results
    pagination.total = response.data.count
    message.success('资产数据更新成功')
  } catch (error) {
    message.error('获取数据失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

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


// 模板选择抽屉相关状态
const templateDrawerVisible = ref(false);
const zabbixTemplates = ref([]);
const selectedTemplateIds = ref([]);
const templateLoading = ref(false);
const templateSearchKeyword = ref('');
const monitoringCreating = ref(false);
const selectedCategory = ref(''); // 当前选中的分类
const expandedCategories = ref({}); // 展开的分类
// 加载Zabbix模板列表
const loadZabbixTemplates = async (assetId) => {
  templateLoading.value = true;
  try {
    const response = await softwareAssetApi.getZabbixTemplates(assetId, templateSearchKeyword.value);
    
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
const selectedAsset = ref(null);
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
    const response = await softwareAssetApi.toggleMonitoring(record.id, enableMonitoring);
    
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
// 新的事件处理方法
const handleSearch = (searchParams) => {
  Object.assign(searchForm, searchParams)
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  pagination.page = 1
  fetchData()
}

const viewDetails = () => {
  detailDialogVisible.value = true ;
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchData()
}

// 输入时间处理
const handleSearchInput = (value) => {
  searchKeyword.value = value;
};

// 处理新增/编辑表单提交

// 处理统计按钮点击事件
const handleStatsFilter = async(filterType) => {
  currentFilter.value = filterType;    
  // 根据点击的统计按钮类型进行相应的过滤或操作
  switch (filterType) {
    case 'in_use':
      // 显示在用软件
      assetStatus.value = "in_use";
      break;
    case "block_up":
      assetStatus.value = "block_up";
      break;
    default:
      break;
  }
  // 更新当前过滤器状态
  currentFilter.value = filterType;
  // 重新加载数据
  pagination.current = 1;
  fetchData() ; 
};

const handleSelectionChange = (selectedKeys, selectedRows) => {
  selectedRowKeys.value = selectedKeys
  selectedItems.value = selectedRows
}

// 表格操作事件处理
const handleView = (record) => {
  currentAssetId.value = record.id
  detailDialogVisible.value = true
}

// 软件资产编辑
const handleEdit = (record) => {
  currentItem.value = { ...record }
  isEdit.value = true
  formDialogVisible.value = true
}


// 软件资产删除
const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除软件资产 "${record.software_name}" 吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        await softwareAssetApi.delete(record.id)
        message.success('删除成功')
        fetchData()
      } catch (error) {
        message.error('删除失败：' + (error.message || '未知错误'))
      }
    }
  })
}

// 处理分页
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
  
  await fetchData();
};


const handleLicense = (record) => {
  currentItem.value = record
  licenseFormData.value = {
    license_count: record.license_count,
    license_expiry_date: record.license_expiry_date
  }
  licenseModalVisible.value = true
}

const handleHistory = (record) => {
  currentHistoryAsset.value = record
  historyModalVisible.value = true
  loadLicenseHistory()
}
const handleBatchDelete = () => {
  Modal.confirm({
    title: '确认批量删除',
    content: `确定要删除选中的 ${selectedItems.value.length} 项软件资产吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        const ids = selectedItems.value.map(item => item.id)
        await softwareAssetApi.batchDelete({ ids })
        message.success('批量删除成功')
        selectedItems.value = []
        selectedRowKeys.value = []
        fetchData()
      } catch (error) {
        message.error('批量删除失败：' + (error.message || '未知错误'))
      }
    }
  })
}

const handleBatchExport = async () => {
  try {
    loading.value = true
    const ids = selectedItems.value.map(item => item.id)
    const response = await softwareAssetApi.export({ ids })
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `软件资产数据_选中项_${formatDate(new Date(), 'YYYY-MM-DD')}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    
    message.success('批量导出成功')
  } catch (error) {
    message.error('批量导出失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

const handleExport = async () => {
  try {
    loading.value = true
    const params = { ...searchForm }
    
    // 过滤空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const response = await softwareAssetApi.export(params)
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `软件资产数据_${formatDate(new Date(), 'YYYY-MM-DD')}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 新增
const showAddDialog = () => {
  currentItem.value = {}
  isEdit.value = false
  formDialogVisible.value = true
}

// 导出数据
const exportData = async () => {
  try {
    loading.value = true
    const params = { ...searchForm }
    
    // 过滤空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const response = await softwareAssetApi.export(params)
    
    // 创建下载链接
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `软件资产数据_${formatDate(new Date(), 'YYYY-MM-DD')}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败：' + (error.message || '未知错误'))
  } finally {
    loading.value = false
  }
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true
}

// 显示扫描配置
const showScanConfig = () => {
  if (monitoringActionsRef.value) {
    monitoringActionsRef.value.showScanConfig()
  }
}

// 许可证处理
const handleLicenseCancel = () => {
  licenseModalVisible.value = false
  licenseFormData.value = {}
}

const handleLicenseConfirm = async () => {
  try {
    await softwareAssetApi.updateLicense(currentItem.value.id, licenseFormData.value)
    message.success('许可证信息更新成功')
    licenseModalVisible.value = false
    fetchData()
  } catch (error) {
    message.error('许可证信息更新失败：' + (error.message || '未知错误'))
  }
}

// 历史记录加载函数
const loadLicenseHistory = async () => {
  if (!currentHistoryAsset.value) return
  
  try {
    licenseHistoryLoading.value = true
    const response = await softwareAssetApi.getLicenseHistory(currentHistoryAsset.value.id)
    licenseHistory.value = response.data || []
  } catch (error) {
    message.error('加载许可证历史记录失败：' + (error.message || '未知错误'))
  } finally {
    licenseHistoryLoading.value = false
  }
}

const loadVersionHistory = async () => {
  if (!currentHistoryAsset.value) return
  
  try {
    versionHistoryLoading.value = true
    const response = await softwareAssetApi.getVersionHistory(currentHistoryAsset.value.id)
    versionHistory.value = response.data || []
  } catch (error) {
    message.error('加载版本历史记录失败：' + (error.message || '未知错误'))
  } finally {
    versionHistoryLoading.value = false
  }
}

// 表单成功回调
const handleFormSuccess = () => {
  fetchData()
}

// 导入成功回调
const handleImportSuccess = () => {
  fetchData()
}

// 获取字典数据
const fetchDictionaryData = async () => {
  try {
    const [assetStatusRes, softwareTypeRes] = await Promise.all([
      dictionaryAPI.getDictionaryByCategory('asset_status'),
      dictionaryAPI.getDictionaryByCategory('software_type')
    ])
    
    if (assetStatusRes.data && assetStatusRes.data.results) {
      assetStatusOptions.value = assetStatusRes.data.results.map(item => ({
        value: item.value,
        label: item.label
      }))
    }
    
    if (softwareTypeRes.data && softwareTypeRes.data.results) {
      softwareTypeOptions.value = softwareTypeRes.data.results.map(item => ({
        value: item.value,
        label: item.label
      }))
    }
  } catch (error) {
    console.error('获取字典数据失败:', error)
    message.error('获取字典数据失败')
  }
}

// 获取软件类型文本
const getSoftwareTypeText = (type) => {
  const option = softwareTypeOptions.value.find(item => item.value === type)
  return option ? option.label : '未知'
}

const assetCount = async () => {
  const res = await softwareAssetApi.getStatusCount() 
  assetStatusCount.value = res.data.data ;
}

// 生命周期
onMounted(() => {
  fetchDictionaryData() ;
  fetchData() ;
  assetCount()  ;
})
</script>

<style scoped>
.software-asset-list-container {
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

.history-section {
  margin-bottom: 16px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.history-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

/* 表格样式 */
:deep(.ant-table) {
  border-radius: 0;
}

:deep(.ant-table-thead > tr > th) {
  background-color: #f9fafb;
  color: #374151;
  font-weight: 500;
  border-bottom: 1px solid #e5e7eb;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background-color: #f9fafb;
}

:deep(.ant-table-tbody > tr > td) {
  border-bottom: 1px solid #f3f4f6;
}

/* 按钮样式 */
:deep(.ant-btn) {
  border-radius: 6px;
  font-weight: 500;
}

:deep(.ant-btn-primary) {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

:deep(.ant-btn-primary:hover) {
  background-color: #2563eb;
  border-color: #2563eb;
}

:deep(.ant-btn-danger) {
  background-color: #ef4444;
  border-color: #ef4444;
}

:deep(.ant-btn-danger:hover) {
  background-color: #dc2626;
  border-color: #dc2626;
}

/* 标签样式 */
:deep(.ant-tag) {
  border-radius: 4px;
  font-weight: 500;
}

/* 表单样式 */
:deep(.ant-form-item-label > label) {
  font-weight: 500;
  color: #374151;
}

/* 对话框样式 */
:deep(.ant-modal) {
  border-radius: 8px;
}

:deep(.ant-modal-header) {
  border-bottom: 1px solid #e5e7eb;
}

:deep(.ant-modal-title) {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

:deep(.ant-modal-body) {
  padding: 24px;
}

:deep(.ant-modal-footer) {
  border-top: 1px solid #e5e7eb;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .software-asset-list {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .search-section {
    padding: 16px;
  }
}
</style>