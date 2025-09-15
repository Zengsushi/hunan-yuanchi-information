<template>
  <a-modal
    v-model:open="dialogVisible"
    title="批量导入硬件设施"
    width="600px"
    :before-close="handleClose"
  >
    <div class="import-container">
      <!-- 步骤指示器 -->
      <a-steps :current="currentStep" status="process">
        <a-step title="下载模板" />
        <a-step title="上传文件" />
        <a-step title="数据预览" />
        <a-step title="导入完成" />
      </a-steps>
      
      <!-- 步骤1: 下载模板 -->
      <div v-if="currentStep === 0" class="step-content">
        <div class="template-section">
          <a-alert
            message="导入说明"
            type="info"
            :closable="false"
            show-icon
          >
            <template #description>
              <p>1. 请先下载导入模板，按照模板格式填写数据</p>
              <p>2. 必填字段：资产标签、型号、资产责任人、制造商、序列号</p>
              <p>3. 日期格式：YYYY-MM-DD（如：2024-01-15）</p>
              <p>4. 资产状态：在用/报废</p>
              <p>5. 保修类型：原厂/第三方</p>
            </template>
          </a-alert>
          
          <div class="template-download">
            <a-button
              type="primary"
              size="large"
              @click="downloadTemplate"
              :loading="downloadLoading"
            >
              <template #icon><DownloadOutlined /></template>
              下载导入模板
            </a-button>
          </div>
        </div>
      </div>
      
      <!-- 步骤2: 上传文件 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="upload-section">
          <a-upload-dragger
            v-model:file-list="fileList"
            :multiple="false"
            :before-upload="beforeUpload"
            @change="handleFileChange"
            accept=".xlsx,.xls"
            :max-count="1"
          >
            <p class="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p class="ant-upload-text">
              将文件拖到此处，或点击上传
            </p>
            <p class="ant-upload-hint">
              只能上传 xlsx/xls 文件，且不超过 10MB
            </p>
          </a-upload-dragger>
          
          <div v-if="uploadFile" class="file-info">
            <a-tag color="green" size="large">
              <template #icon><FileExcelOutlined /></template>
              {{ uploadFile.name }}
            </a-tag>
            <a-button type="text" @click="removeFile" class="remove-btn">
              <template #icon><CloseOutlined /></template>
            </a-button>
          </div>
        </div>
      </div>
      
      <!-- 步骤3: 数据预览 -->
      <div v-if="currentStep === 2" class="step-content">
        <div class="preview-section">
          <div class="preview-header">
            <span>数据预览（共 {{ previewData.length }} 条记录）</span>
            <div class="validation-summary">
              <a-tag v-if="validRecords > 0" color="green">
                有效: {{ validRecords }}
              </a-tag>
              <a-tag v-if="invalidRecords > 0" color="red">
                无效: {{ invalidRecords }}
              </a-tag>
            </div>
          </div>
          
          <a-table
            :data-source="previewData.slice(0, 10)"
            :columns="previewColumns"
            :bordered="true"
            :scroll="{ y: 300 }"
            size="small"
            :pagination="false"
          />
          
          <div v-if="previewData.length > 10" class="more-records">
            <a-typography-text type="secondary">仅显示前10条记录，实际将导入 {{ validRecords }} 条有效记录</a-typography-text>
          </div>
          
          <a-alert
            v-if="invalidRecords > 0"
            message="存在无效数据"
            type="warning"
            :closable="false"
            show-icon
            class="validation-alert"
          >
            <template #description>
              <p>发现 {{ invalidRecords }} 条无效记录，这些记录将被跳过。</p>
              <p>请检查数据格式是否正确，必填字段是否完整。</p>
            </template>
          </a-alert>
        </div>
      </div>
      
      <!-- 步骤4: 导入完成 -->
      <div v-if="currentStep === 3" class="step-content">
        <div class="result-section">
          <div class="result-icon">
            <CheckCircleOutlined v-if="importResult.success" style="font-size: 60px; color: #52c41a;" />
            <CloseCircleOutlined v-else style="font-size: 60px; color: #ff4d4f;" />
          </div>
          
          <div class="result-content">
            <h3 v-if="importResult.success">导入成功！</h3>
            <h3 v-else>导入失败</h3>
            
            <div class="result-details">
              <p v-if="importResult.success">
                成功导入 <strong>{{ importResult.successCount }}</strong> 条记录
              </p>
              <p v-if="importResult.failedCount > 0">
                失败 <strong>{{ importResult.failedCount }}</strong> 条记录
              </p>
              <p v-if="importResult.message">
                {{ importResult.message }}
              </p>
            </div>
            
            <div v-if="importResult.errors && importResult.errors.length > 0" class="error-details">
              <a-collapse>
                <a-collapse-panel key="1" header="查看错误详情">
                  <div v-for="(error, index) in importResult.errors" :key="index" class="error-item">
                    <span class="error-row">第{{ error.row }}行:</span>
                    <span class="error-msg">{{ error.message }}</span>
                  </div>
                </a-collapse-panel>
              </a-collapse>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <a-button @click="handleClose">取消</a-button>
        <a-button
          v-if="currentStep === 0"
          type="primary"
          @click="nextStep"
          :disabled="!templateDownloaded"
        >
          下一步
        </a-button>
        <a-button
          v-if="currentStep === 1"
          type="primary"
          @click="parseFile"
          :disabled="!uploadFile"
          :loading="parseLoading"
        >
          解析文件
        </a-button>
        <a-button
          v-if="currentStep === 2"
          type="primary"
          @click="importData"
          :disabled="validRecords === 0"
          :loading="importLoading"
        >
          开始导入 ({{ validRecords }}条)
        </a-button>
        <a-button
          v-if="currentStep === 3"
          type="primary"
          @click="handleComplete"
        >
          完成
        </a-button>
      </div>
    </template>
  </a-modal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  DownloadOutlined,
  InboxOutlined,
  FileExcelOutlined,
  CloseOutlined,
  CheckOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons-vue'
import { hardwareAssetApi } from '@/api/hardwareAsset'
import * as XLSX from 'xlsx'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const currentStep = ref(0)
const templateDownloaded = ref(false)
const downloadLoading = ref(false)
const uploadFile = ref(null)
const fileList = ref([])
const parseLoading = ref(false)
const importLoading = ref(false)
const previewData = ref([])
const importResult = ref({
  success: false,
  successCount: 0,
  failedCount: 0,
  message: '',
  errors: []
})

// 表格列配置
const previewColumns = [
  {
    title: '#',
    dataIndex: 'index',
    key: 'index',
    width: 50,
    customRender: ({ index }) => index + 1
  },
  {
    title: '资产标签',
    dataIndex: 'asset_tag',
    key: 'asset_tag',
    width: 120
  },
  {
    title: '型号',
    dataIndex: 'model',
    key: 'model',
    width: 100
  },
  {
    title: '责任人',
    dataIndex: 'asset_owner',
    key: 'asset_owner',
    width: 100
  },
  {
    title: '制造商',
    dataIndex: 'manufacturer',
    key: 'manufacturer',
    width: 100
  },
  {
    title: '状态',
    key: 'status',
    width: 80,
    customRender: ({ record }) => {
      if (record._valid) {
        return '<CheckOutlined style="color: #52c41a;" />'
      } else {
        return '<CloseOutlined style="color: #ff4d4f;" />'
      }
    }
  },
  {
    title: '错误信息',
    key: 'errors',
    minWidth: 150,
    customRender: ({ record }) => {
      if (record._errors && record._errors.length > 0) {
        return `<span class="error-text">${record._errors.join(', ')}</span>`
      } else {
        return '<span class="success-text">验证通过</span>'
      }
    }
  }
]

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const validRecords = computed(() => {
  return previewData.value.filter(item => item._valid).length
})

const invalidRecords = computed(() => {
  return previewData.value.filter(item => !item._valid).length
})

// 方法
const downloadTemplate = async () => {
  downloadLoading.value = true
  try {
    const response = await hardwareAssetApi.downloadTemplate()
    
    // 创建下载链接
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '硬件设施导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    templateDownloaded.value = true
    message.success('模板下载成功')
  } catch (error) {
    message.error('模板下载失败')
    console.error('Download template error:', error)
  } finally {
    downloadLoading.value = false
  }
}

const nextStep = () => {
  currentStep.value++
}

const handleFileChange = (info) => {
  const { fileList } = info
  if (fileList.length > 0) {
    uploadFile.value = fileList[0]
  } else {
    uploadFile.value = null
  }
}

const beforeUpload = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel'
  const isLt10M = file.size / 1024 / 1024 < 10
  
  if (!isExcel) {
    message.error('只能上传 Excel 文件!')
    return false
  }
  if (!isLt10M) {
    message.error('文件大小不能超过 10MB!')
    return false
  }
  return false // 阻止自动上传
}

const removeFile = () => {
  uploadFile.value = null
  fileList.value = []
}

const parseFile = async () => {
  if (!uploadFile.value) return
  
  parseLoading.value = true
  try {
    const file = uploadFile.value.raw
    const data = await readExcelFile(file)
    
    // 验证数据
    const validatedData = validateData(data)
    previewData.value = validatedData
    
    currentStep.value++
    message.success('文件解析成功')
  } catch (error) {
    message.error('文件解析失败: ' + (error.message || '未知错误'))
    console.error('Parse file error:', error)
  } finally {
    parseLoading.value = false
  }
}

const readExcelFile = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        const sheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[sheetName]
        const jsonData = XLSX.utils.sheet_to_json(worksheet)
        resolve(jsonData)
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = reject
    reader.readAsArrayBuffer(file)
  })
}

const validateData = (data) => {
  const requiredFields = ['资产标签', '型号', '资产责任人', '制造商', '序列号']
  
  return data.map((row, index) => {
    const errors = []
    const item = {
      asset_tag: row['资产标签'],
      model: row['型号'],
      asset_owner: row['资产责任人'],
      manufacturer: row['制造商'],
      serial_number: row['序列号'],
      purchase_date: row['采购日期'],
      project_source: row['项目来源'],
      asset_status: row['资产状态'] === '报废' ? 'scrapped' : 'in_use',
      room: row['机房'],
      cabinet: row['机柜'],
      u_position: row['U位'],
      dimensions: row['产品尺寸'],
      warranty_type: row['保修类型'] === '第三方' ? 'third_party' : 'original',
      warranty_start_date: row['保修开始日期'],
      warranty_end_date: row['保修结束日期'],
      _rowIndex: index + 2 // Excel行号（从2开始，因为第1行是标题）
    }
    
    // 验证必填字段
    requiredFields.forEach(field => {
      const value = row[field]
      if (!value || String(value).trim() === '') {
        errors.push(`${field}不能为空`)
      }
    })
    
    // 验证日期格式
    if (item.purchase_date && !isValidDate(item.purchase_date)) {
      errors.push('采购日期格式不正确')
    }
    if (item.warranty_start_date && !isValidDate(item.warranty_start_date)) {
      errors.push('保修开始日期格式不正确')
    }
    if (item.warranty_end_date && !isValidDate(item.warranty_end_date)) {
      errors.push('保修结束日期格式不正确')
    }
    
    item._valid = errors.length === 0
    item._errors = errors
    
    return item
  })
}

const isValidDate = (dateString) => {
  if (!dateString) return true // 可选字段
  const date = new Date(dateString)
  return date instanceof Date && !isNaN(date)
}

const importData = async () => {
  const validData = previewData.value.filter(item => item._valid)
  
  if (validData.length === 0) {
    message.error('没有有效数据可导入')
    return
  }
  
  importLoading.value = true
  try {
    // 清理验证字段
    const cleanData = validData.map(item => {
      const { _valid, _errors, _rowIndex, ...cleanItem } = item
      return cleanItem
    })
    
    const response = await hardwareAssetApi.batchImport(cleanData)
    
    importResult.value = {
      success: true,
      successCount: response.data.success_count || cleanData.length,
      failedCount: response.data.failed_count || 0,
      message: response.data.message || '导入成功',
      errors: response.data.errors || []
    }
    
    currentStep.value++
    message.success('导入完成')
  } catch (error) {
    importResult.value = {
      success: false,
      successCount: 0,
      failedCount: validData.length,
      message: error.response?.data?.message || '导入失败',
      errors: error.response?.data?.errors || []
    }
    currentStep.value++
    message.error('导入失败: ' + (error.response?.data?.message || error.message || '未知错误'))
    console.error('Import data error:', error)
  } finally {
    importLoading.value = false
  }
}

const handleComplete = () => {
  emit('success')
  handleClose()
}

const handleClose = () => {
  dialogVisible.value = false
  // 重置状态
  setTimeout(() => {
    currentStep.value = 0
    templateDownloaded.value = false
    uploadFile.value = null
    previewData.value = []
    importResult.value = {
      success: false,
      successCount: 0,
      failedCount: 0,
      message: '',
      errors: []
    }
  }, 300)
}
</script>

<style scoped>
.import-container {
  padding: 20px 0;
}

.step-content {
  margin-top: 30px;
  min-height: 300px;
}

.template-section {
  text-align: center;
}

.template-download {
  margin-top: 30px;
}

.upload-section {
  padding: 20px;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  gap: 10px;
}

.remove-btn {
  color: #f56c6c;
}

.preview-section {
  padding: 10px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.validation-summary {
  display: flex;
  gap: 10px;
}

.more-records {
  text-align: center;
  margin-top: 10px;
}

.validation-alert {
  margin-top: 15px;
}

.error-text {
  color: #f56c6c;
  font-size: 12px;
}

.success-text {
  color: #67c23a;
  font-size: 12px;
}

.result-section {
  text-align: center;
  padding: 40px 20px;
}

.result-icon {
  margin-bottom: 20px;
}

.result-content h3 {
  margin-bottom: 20px;
  color: #303133;
}

.result-details {
  margin-bottom: 20px;
}

.result-details p {
  margin: 10px 0;
  color: #606266;
}

.error-details {
  text-align: left;
  max-width: 500px;
  margin: 0 auto;
}

.error-item {
  margin-bottom: 8px;
  padding: 8px;
  background-color: #fef0f0;
  border-radius: 4px;
}

.error-row {
  font-weight: bold;
  color: #f56c6c;
  margin-right: 10px;
}

.error-msg {
  color: #606266;
}

.dialog-footer {
  text-align: right;
}
</style>