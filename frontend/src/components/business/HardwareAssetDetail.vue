<template>
  <a-modal
    v-model:open="dialogVisible"
    title="硬件设施详情"
    width="900px"
    :before-close="handleClose"
  >
    <div v-if="assetData" class="detail-container">
      <a-tabs v-model:activeKey="activeTab">
        <!-- 基本信息 -->
        <a-tab-pane tab="基本信息" key="basic">
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="资产标签">
              <a-tag color="blue">{{ assetData.asset_tag }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="型号">
              {{ assetData.model }}
            </a-descriptions-item>
            <a-descriptions-item label="资产责任人">
              {{ assetData.asset_owner }}
            </a-descriptions-item>
            <a-descriptions-item label="采购日期">
              {{ assetData.purchase_date }}
            </a-descriptions-item>
            <a-descriptions-item label="供应商">
              {{ assetData.supplier_name }}
            </a-descriptions-item>
            <a-descriptions-item label="供应商联系人">
              {{ assetData.supplier_contact || '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="项目来源">
              {{ assetData.project_source || '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="资产状态">
              <a-tag :color="assetData.asset_status === 'in_use' ? 'green' : 'red'">
                {{ assetData.asset_status === 'in_use' ? '在用' : '报废' }}
              </a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </a-tab-pane>
        
        <!-- 产品信息 -->
        <a-tab-pane tab="产品信息" key="product">
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="制造商">
              {{ assetData.manufacturer }}
            </a-descriptions-item>
            <a-descriptions-item label="序列号">
              {{ assetData.serial_number }}
            </a-descriptions-item>
            <a-descriptions-item label="位置">
              {{ getLocationText(assetData) }}
            </a-descriptions-item>
            <a-descriptions-item label="产品尺寸">
              {{ assetData.dimensions || '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="监控状态">
              <a-tag :color="assetData.monitoring_status ? 'green' : 'default'">
                {{ assetData.monitoring_status ? '已监控' : '未监控' }}
              </a-tag>
            </a-descriptions-item>
          </a-descriptions>
          
          <!-- 规格参数 -->
          <div class="spec-section">
            <h4>规格参数</h4>
            <a-table
              :data-source="specificationList"
              :columns="specColumns"
              bordered
              :pagination="false"
              :locale="{ emptyText: '暂无规格参数' }"
            />
          </div>
        </a-tab-pane>
        
        <!-- 保修信息 -->
        <a-tab-pane tab="保修信息" key="warranty">
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="保修类型">
              <a-tag :color="assetData.warranty_type === 'original' ? 'green' : 'orange'">
                {{ assetData.warranty_type === 'original' ? '原厂保修' : '第三方保修' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="保修状态">
              <a-tag :color="getWarrantyStatusColor(assetData.warranty_status)">
                {{ getWarrantyStatusText(assetData.warranty_status) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="保修开始日期">
              {{ assetData.warranty_start_date }}
            </a-descriptions-item>
            <a-descriptions-item label="保修结束日期">
              {{ assetData.warranty_end_date }}
            </a-descriptions-item>
            <a-descriptions-item label="剩余保修天数" v-if="assetData.warranty_status !== 'expired'">
              <span :class="getRemainingDaysClass(assetData.warranty_remaining_days)">
                {{ assetData.warranty_remaining_days }}天
              </span>
            </a-descriptions-item>
          </a-descriptions>
        </a-tab-pane>
        
        <!-- 规格参数更新记录 -->
        <a-tab-pane tab="规格参数更新记录" key="spec-history">
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
        
        <!-- 保修更新记录 -->
        <a-tab-pane tab="保修更新记录" key="warranty-history">
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
import { hardwareAssetApi } from '@/api/hardwareAsset'
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
  }
})

// Emits
const emit = defineEmits(['update:visible', 'edit'])

// 响应式数据
const activeTab = ref('basic')
const specHistory = ref([])
const warrantyHistory = ref([])
const specHistoryLoading = ref(false)
const warrantyHistoryLoading = ref(false)

// 表格列配置
const specColumns = [
  {
    title: '参数名称',
    dataIndex: 'key',
    key: 'key',
    width: 150
  },
  {
    title: '参数值',
    dataIndex: 'value',
    key: 'value'
  }
]

const specHistoryColumns = [
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
    title: '更新前规格参数',
    dataIndex: 'old_specifications',
    key: 'old_specifications',
    minWidth: 200
  },
  {
    title: '更新后规格参数',
    dataIndex: 'new_specifications',
    key: 'new_specifications',
    minWidth: 200
  }
]

const warrantyHistoryColumns = [
  {
    title: '更新时间',
    dataIndex: 'update_time',
    key: 'update_time',
    width: 180,
    customRender: ({ text }) => formatDateTime(text)
  },
  {
    title: '更新前保修类型',
    dataIndex: 'old_warranty_type',
    key: 'old_warranty_type',
    width: 120
  },
  {
    title: '更新后保修类型',
    dataIndex: 'new_warranty_type',
    key: 'new_warranty_type',
    width: 120
  },
  {
    title: '更新前保修期',
    key: 'old_warranty_period',
    width: 200,
    customRender: ({ record }) => `${record.old_warranty_start_date} ~ ${record.old_warranty_end_date}`
  },
  {
    title: '更新后保修期',
    key: 'new_warranty_period',
    width: 200,
    customRender: ({ record }) => `${record.new_warranty_start_date} ~ ${record.new_warranty_end_date}`
  }
]

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const specificationList = computed(() => {
  if (!props.assetData?.specifications) return []
  return Object.entries(props.assetData.specifications).map(([key, value]) => ({
    key,
    value
  }))
})

// 方法
const getLocationText = (asset) => {
  const parts = []
  if (asset.room) parts.push(`机房: ${asset.room}`)
  if (asset.cabinet) parts.push(`机柜: ${asset.cabinet}`)
  if (asset.u_position) parts.push(`U位: ${asset.u_position}`)
  return parts.length > 0 ? parts.join(' | ') : '-'
}

const getWarrantyStatusText = (status) => {
  const statusMap = {
    'original': '原厂保修',
    'third_party': '第三方保修',
    'expired': '已过保'
  }
  return statusMap[status] || status
}

const getWarrantyStatusColor = (status) => {
  const colorMap = {
    'original': 'green',
    'third_party': 'orange',
    'expired': 'red'
  }
  return colorMap[status] || 'default'
}

const getRemainingDaysClass = (days) => {
  if (days <= 30) return 'text-danger'
  if (days <= 90) return 'text-warning'
  return 'text-success'
}

const loadSpecHistory = async () => {
  if (!props.assetData?.id) return
  
  specHistoryLoading.value = true
  try {
    const response = await hardwareAssetApi.getSpecHistory(props.assetData.id)
    specHistory.value = response.data || []
  } catch (error) {
    console.error('Load spec history error:', error)
    message.error('获取规格参数更新记录失败')
  } finally {
    specHistoryLoading.value = false
  }
}

const loadWarrantyHistory = async () => {
  if (!props.assetData?.id) return
  
  warrantyHistoryLoading.value = true
  try {
    const response = await hardwareAssetApi.getWarrantyHistory(props.assetData.id)
    warrantyHistory.value = response.data || []
  } catch (error) {
    console.error('Load warranty history error:', error)
    message.error('获取保修更新记录失败')
  } finally {
    warrantyHistoryLoading.value = false
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
        if (activeTab.value === 'spec-history') {
          loadSpecHistory()
        } else if (activeTab.value === 'warranty-history') {
          loadWarrantyHistory()
        }
      }, 100)
    }
  }
)

watch(activeTab, (newTab) => {
  if (newTab === 'spec-history' && specHistory.value.length === 0) {
    loadSpecHistory()
  } else if (newTab === 'warranty-history' && warrantyHistory.value.length === 0) {
    loadWarrantyHistory()
  }
})
</script>

<style scoped>
.detail-container {
  max-height: 600px;
  overflow-y: auto;
}

.spec-section {
  margin-top: 20px;
}

.spec-section h4 {
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

.spec-diff {
  line-height: 1.6;
}

.spec-item {
  margin-bottom: 5px;
}

.spec-key {
  font-weight: bold;
  margin-right: 8px;
}

.spec-value.old {
  color: #f56c6c;
  text-decoration: line-through;
}

.spec-value.new {
  color: #67c23a;
  font-weight: bold;
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