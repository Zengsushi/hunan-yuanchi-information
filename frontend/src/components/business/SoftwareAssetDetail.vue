<template>
  <a-modal
    v-model:open="dialogVisible"
    title="软件资产详情"
    width="900px"
    :before-close="handleClose"
  >
    <div v-if="assetData" class="detail-container">
      <a-tabs v-model:activeKey="activeTab">
        <!-- 基本信息 -->
        <a-tab-pane tab="基本信息" key="basic">
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="软件名称">
              <a-tag color="blue">{{ assetData.software_name }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="软件版本">
              {{ assetData.version }}
            </a-descriptions-item>
            <a-descriptions-item label="软件类型">
              <a-tag :color="getSoftwareTypeColor(assetData.software_type)">
                {{ getSoftwareTypeText(assetData.software_type) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="资产责任人">
              {{ assetData.asset_owner }}
            </a-descriptions-item>
            <a-descriptions-item label="供应商">
              {{ assetData.supplier_name }}
            </a-descriptions-item>
            <a-descriptions-item label="供应商联系人">
              {{ assetData.supplier_contact || '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="采购日期">
              {{ assetData.purchase_date }}
            </a-descriptions-item>
            <a-descriptions-item label="资产状态">
              <a-tag :color="getAssetStatusColor(assetData.asset_status)">
                {{ getAssetStatusText(assetData.asset_status) }}
              </a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </a-tab-pane>
        
        <!-- 许可证信息 -->
        <a-tab-pane tab="许可证信息" key="license">
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="许可证类型">
              <a-tag :color="getLicenseTypeColor(assetData.license_type)">
                {{ getLicenseTypeText(assetData.license_type) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="许可证数量">
              {{ assetData.license_count }}
            </a-descriptions-item>
            <a-descriptions-item label="许可证开始日期">
              {{ assetData.license_start_date }}
            </a-descriptions-item>
            <a-descriptions-item label="许可证结束日期">
              {{ assetData.license_end_date }}
            </a-descriptions-item>
            <a-descriptions-item label="许可证状态">
              <a-tag :color="getLicenseStatusColor(assetData.license_status)">
                {{ getLicenseStatusText(assetData.license_status) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="剩余有效天数" v-if="assetData.license_status !== 'expired'">
              <span :class="getRemainingDaysClass(assetData.license_remaining_days)">
                {{ assetData.license_remaining_days }}天
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="许可证密钥" :span="2" v-if="assetData.license_key">
              <a-typography-text code copyable>
                {{ assetData.license_key }}
              </a-typography-text>
            </a-descriptions-item>
          </a-descriptions>
        </a-tab-pane>
        
        <!-- 部署信息 -->
        <a-tab-pane tab="部署信息" key="deployment">
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="安装路径">
              {{ assetData.installation_path || '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="配置文件路径">
              {{ assetData.config_path || '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="备注" :span="2">
              {{ assetData.notes || '-' }}
            </a-descriptions-item>
          </a-descriptions>
          
          <!-- 部署服务器 -->
          <div class="deployment-section">
            <h4>部署服务器</h4>
            <a-table
              :data-source="deploymentServerList"
              :columns="serverColumns"
              bordered
              :pagination="false"
              :locale="{ emptyText: '暂无部署服务器' }"
            />
          </div>
        </a-tab-pane>
        
        <!-- 许可证更新记录 -->
        <a-tab-pane tab="许可证更新记录" key="license-history">
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
        
        <!-- 版本更新记录 -->
        <a-tab-pane tab="版本更新记录" key="version-history">
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
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <a-button @click="handleClose">关闭</a-button>
        <a-button type="primary" @click="handleEdit">
          编辑
        </a-button>
      </div>
    </template>
  </a-modal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { softwareAssetApi } from '@/api/softwareAsset'
import { formatDateTime } from '@/utils/date'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  assetData: {
    type: Object,
    default: null
  }, 
  softwareAssetId: {
    type : Number,
    default : null
  }
})

console.log(props.softwareAssetId);

// Emits
const emit = defineEmits(['update:visible', 'edit'])

// 响应式数据
const activeTab = ref('basic')
const licenseHistory = ref([])
const versionHistory = ref([])
const licenseHistoryLoading = ref(false)
const versionHistoryLoading = ref(false)

// 表格列配置
const serverColumns = [
  {
    title: '服务器主机名/IP',
    dataIndex: 'hostname',
    key: 'hostname',
    width: 200
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description'
  }
]

const licenseHistoryColumns = [
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    width: 180,
    customRender: ({ text }) => formatDateTime(text)
  },
  {
    title: '更新方式',
    dataIndex: 'update_method',
    key: 'update_method',
    width: 100
  },
  {
    title: '更新前许可证类型',
    dataIndex: 'old_license_type',
    key: 'old_license_type',
    width: 120
  },
  {
    title: '更新后许可证类型',
    dataIndex: 'new_license_type',
    key: 'new_license_type',
    width: 120
  },
  {
    title: '更新前许可证期限',
    key: 'old_license_period',
    width: 200,
    customRender: ({ record }) => `${record.old_license_start_date} ~ ${record.old_license_end_date}`
  },
  {
    title: '更新后许可证期限',
    key: 'new_license_period',
    width: 200,
    customRender: ({ record }) => `${record.new_license_start_date} ~ ${record.new_license_end_date}`
  }
]

const versionHistoryColumns = [
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    width: 180,
    customRender: ({ text }) => formatDateTime(text)
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
    title: '更新说明',
    dataIndex: 'update_notes',
    key: 'update_notes'
  }
]

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const deploymentServerList = computed(() => {
  if (!props.assetData?.deployment_servers) return []
  return props.assetData.deployment_servers
})

// 方法
const getSoftwareTypeText = (type) => {
  const typeMap = {
    'system': '系统软件',
    'application': '应用软件',
    'development': '开发工具',
    'database': '数据库',
    'security': '安全软件',
    'other': '其他'
  }
  return typeMap[type] || type
}

const getSoftwareTypeColor = (type) => {
  const colorMap = {
    'system': 'blue',
    'application': 'green',
    'development': 'orange',
    'database': 'purple',
    'security': 'red',
    'other': 'default'
  }
  return colorMap[type] || 'default'
}

const getAssetStatusText = (status) => {
  const statusMap = {
    'active': '激活',
    'inactive': '未激活',
    'expired': '过期',
    'retired': '退役'
  }
  return statusMap[status] || status
}

const getAssetStatusColor = (status) => {
  const colorMap = {
    'active': 'green',
    'inactive': 'orange',
    'expired': 'red',
    'retired': 'default'
  }
  return colorMap[status] || 'default'
}

const getLicenseTypeText = (type) => {
  const typeMap = {
    'perpetual': '永久许可',
    'subscription': '订阅许可',
    'trial': '试用许可',
    'open_source': '开源许可'
  }
  return typeMap[type] || type
}

const getLicenseTypeColor = (type) => {
  const colorMap = {
    'perpetual': 'green',
    'subscription': 'blue',
    'trial': 'orange',
    'open_source': 'purple'
  }
  return colorMap[type] || 'default'
}

const getLicenseStatusText = (status) => {
  const statusMap = {
    'active': '有效',
    'expired': '已过期',
    'near_expired': '即将过期'
  }
  return statusMap[status] || status
}

const getLicenseStatusColor = (status) => {
  const colorMap = {
    'active': 'green',
    'expired': 'red',
    'near_expired': 'orange'
  }
  return colorMap[status] || 'default'
}

const getRemainingDaysClass = (days) => {
  if (days <= 30) return 'text-danger'
  if (days <= 90) return 'text-warning'
  return 'text-success'
}

const loadLicenseHistory = async () => {
  if (!props.assetData?.id) return
  
  licenseHistoryLoading.value = true
  try {
    const response = await softwareAssetApi.getLicenseHistory(props.assetData.id)
    licenseHistory.value = response.data || []
  } catch (error) {
    console.error('Load license history error:', error)
    message.error('获取许可证更新记录失败')
  } finally {
    licenseHistoryLoading.value = false
  }
}

const loadVersionHistory = async () => {
  if (!props.assetData?.id) return
  
  versionHistoryLoading.value = true
  try {
    const response = await softwareAssetApi.getVersionHistory(props.assetData.id)
    versionHistory.value = response.data || []
  } catch (error) {
    console.error('Load version history error:', error)
    message.error('获取版本更新记录失败')
  } finally {
    versionHistoryLoading.value = false
  }
}

const handleEdit = () => {
  emit('edit', props.assetData)
}

const handleClose = () => {
  dialogVisible.value = false
}

// 监听器
watch(
  () => props.visible,
  (newVal) => {
    if (newVal && props.assetData) {
      activeTab.value = 'basic'
      // 延迟加载历史记录，避免初始加载时的性能问题
      setTimeout(() => {
        if (activeTab.value === 'license-history') {
          loadLicenseHistory()
        } else if (activeTab.value === 'version-history') {
          loadVersionHistory()
        }
      }, 100)
    }
  }
)

watch(activeTab, (newTab) => {
  if (newTab === 'license-history' && licenseHistory.value.length === 0) {
    loadLicenseHistory()
  } else if (newTab === 'version-history' && versionHistory.value.length === 0) {
    loadVersionHistory()
  }
})
</script>

<style scoped>
.detail-container {
  max-height: 600px;
  overflow-y: auto;
}

.deployment-section {
  margin-top: 20px;
}

.deployment-section h4 {
  margin-bottom: 15px;
  color: #303133;
}

.history-section {
  padding: 10px 0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.history-header h4 {
  margin: 0;
  color: #303133;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

.text-warning {
  color: #e6a23c;
  font-weight: bold;
}

.text-success {
  color: #67c23a;
}

.dialog-footer {
  text-align: right;
}
</style>