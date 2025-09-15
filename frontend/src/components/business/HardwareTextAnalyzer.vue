<template>
  <div class="hardware-text-analyzer">
    <a-card title="智能硬件信息识别" class="analyzer-card">
      <div class="input-section">
        <a-form-item label="设备描述" class="form-item">
          <a-textarea
            v-model:value="inputText"
            placeholder="请输入设备描述，例如：Dell PowerEdge R740服务器，配置Intel Xeon Gold 6248处理器，64GB DDR4内存，2TB SSD硬盘"
            :rows="4"
            :maxlength="1000"
            show-count
            @input="handleTextChange"
          />
        </a-form-item>
        
        <div class="action-buttons">
          <a-button 
            type="primary" 
            @click="analyzeText"
            :loading="analyzing"
            :disabled="!inputText.trim()"
          >
            <template #icon>
              <SearchOutlined />
            </template>
            智能识别
          </a-button>
          
          <a-button @click="clearAll">
            <template #icon>
              <ClearOutlined />
            </template>
            清空
          </a-button>
        </div>
      </div>
      
      <a-divider>识别结果</a-divider>
      
      <div class="result-section">
        <a-row :gutter="16">
          <a-col :span="12">
            <div class="result-card">
              <h4>基本信息</h4>
              <div class="result-item" v-for="(value, key) in basicInfo" :key="key">
                <span class="label">{{ getFieldLabel(key) }}:</span>
                <span class="value" :class="{ 'detected': value }">{{ value || '未识别' }}</span>
              </div>
            </div>
          </a-col>
          
          <a-col :span="12">
            <div class="result-card">
              <h4>规格参数</h4>
              <div class="spec-list">
                <div 
                  v-for="(spec, index) in specifications" 
                  :key="index"
                  class="spec-item"
                >
                  <span class="spec-key">{{ spec.key }}:</span>
                  <span class="spec-value">{{ spec.value }}</span>
                </div>
                <div v-if="specifications.length === 0" class="no-specs">
                  暂无识别到的规格参数
                </div>
              </div>
            </div>
          </a-col>
        </a-row>
        
        <div class="apply-section" v-if="hasResults">
          <a-button 
            type="primary" 
            size="large"
            @click="applyToForm"
            class="apply-button"
          >
            <template #icon>
              <CheckOutlined />
            </template>
            应用到表单
          </a-button>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { SearchOutlined, ClearOutlined, CheckOutlined } from '@ant-design/icons-vue'

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['apply-data'])

// 响应式数据
const inputText = ref('')
const analyzing = ref(false)

// 识别结果
const basicInfo = reactive({
  model: '',
  manufacturer: '',
  serial_number: ''
})

const specifications = ref([])

// 计算属性
const hasResults = computed(() => {
  return Object.values(basicInfo).some(v => v) || specifications.value.length > 0
})

// 字段标签映射
const fieldLabels = {
  model: '设备型号',
  manufacturer: '制造商',
  serial_number: '序列号'
}

const getFieldLabel = (key) => {
  return fieldLabels[key] || key
}

// 硬件关键词库
const hardwarePatterns = {
  // 制造商
  manufacturers: {
    'Dell|戴尔': 'Dell',
    'HP|惠普|HPE': 'HP',
    'IBM|国际商业机器': 'IBM',
    'Lenovo|联想': 'Lenovo',
    'Cisco|思科': 'Cisco',
    'Huawei|华为': 'Huawei',
    'Intel|英特尔': 'Intel',
    'AMD|超威': 'AMD',
    'NVIDIA|英伟达': 'NVIDIA',
    'Supermicro|超微': 'Supermicro'
  },
  
  // 设备型号
  models: {
    'PowerEdge\\s+([A-Z0-9]+)': 'PowerEdge $1',
    'ProLiant\\s+([A-Z0-9]+)': 'ProLiant $1',
    'ThinkServer\\s+([A-Z0-9]+)': 'ThinkServer $1',
    'System\\s+x([0-9]+)': 'System x$1'
  },
  
  // 处理器
  processors: {
    'Intel\\s+Xeon\\s+([A-Z0-9\\s-]+)': 'Intel Xeon $1',
    'AMD\\s+EPYC\\s+([A-Z0-9\\s-]+)': 'AMD EPYC $1',
    'Intel\\s+Core\\s+([A-Z0-9\\s-]+)': 'Intel Core $1'
  },
  
  // 内存
  memory: {
    '(\\d+)\\s*GB\\s*(DDR[0-9]*)': '$1GB $2',
    '(\\d+)\\s*G\\s*(内存|RAM)': '$1GB RAM'
  },
  
  // 存储
  storage: {
    '(\\d+)\\s*TB\\s*(SSD|HDD|硬盘)': '$1TB $2',
    '(\\d+)\\s*GB\\s*(SSD|HDD|硬盘)': '$1GB $2'
  },
  
  // 网络
  network: {
    '(\\d+)\\s*Gbps': '$1Gbps',
    '千兆|1000M': '1Gbps',
    '万兆|10G': '10Gbps'
  }
}

// 文本分析函数
const analyzeText = async () => {
  if (!inputText.value.trim()) {
    message.warning('请输入设备描述')
    return
  }
  
  analyzing.value = true
  
  try {
    // 模拟分析延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const text = inputText.value
    
    // 重置结果
    Object.keys(basicInfo).forEach(key => {
      basicInfo[key] = ''
    })
    specifications.value = []
    
    // 识别制造商
    for (const [pattern, value] of Object.entries(hardwarePatterns.manufacturers)) {
      const regex = new RegExp(pattern, 'gi')
      if (regex.test(text)) {
        basicInfo.manufacturer = value
        break
      }
    }
    
    // 识别设备型号
    for (const [pattern, template] of Object.entries(hardwarePatterns.models)) {
      const regex = new RegExp(pattern, 'gi')
      const match = text.match(regex)
      if (match) {
        basicInfo.model = match[0]
        break
      }
    }
    
    // 识别序列号（简单模式）
    const serialPattern = /序列号[：:]?\s*([A-Z0-9]{6,})/gi
    const serialMatch = text.match(serialPattern)
    if (serialMatch) {
      basicInfo.serial_number = serialMatch[0].replace(/序列号[：:]?\s*/gi, '')
    }
    
    // 识别规格参数
    const specs = []
    
    // 处理器
    for (const [pattern, template] of Object.entries(hardwarePatterns.processors)) {
      const regex = new RegExp(pattern, 'gi')
      const match = text.match(regex)
      if (match) {
        specs.push({ key: 'CPU', value: match[0] })
        break
      }
    }
    
    // 内存
    for (const [pattern, template] of Object.entries(hardwarePatterns.memory)) {
      const regex = new RegExp(pattern, 'gi')
      const match = text.match(regex)
      if (match) {
        specs.push({ key: '内存', value: match[0] })
        break
      }
    }
    
    // 存储
    for (const [pattern, template] of Object.entries(hardwarePatterns.storage)) {
      const regex = new RegExp(pattern, 'gi')
      const matches = text.match(new RegExp(pattern, 'gi'))
      if (matches) {
        matches.forEach(match => {
          specs.push({ key: '存储', value: match })
        })
      }
    }
    
    // 网络
    for (const [pattern, template] of Object.entries(hardwarePatterns.network)) {
      const regex = new RegExp(pattern, 'gi')
      const match = text.match(regex)
      if (match) {
        specs.push({ key: '网络', value: match[0] })
        break
      }
    }
    
    specifications.value = specs
    
    if (hasResults.value) {
      message.success('识别完成！')
    } else {
      message.info('未识别到相关硬件信息，请检查描述内容')
    }
    
  } catch (error) {
    console.error('Analysis error:', error)
    message.error('分析失败，请重试')
  } finally {
    analyzing.value = false
  }
}

// 应用到表单
const applyToForm = () => {
  const formData = {
    ...basicInfo,
    specifications: specifications.value
  }
  
  emit('apply-data', formData)
  message.success('数据已应用到表单')
}

// 清空所有内容
const clearAll = () => {
  inputText.value = ''
  Object.keys(basicInfo).forEach(key => {
    basicInfo[key] = ''
  })
  specifications.value = []
}

// 文本变化处理
const handleTextChange = () => {
  // 可以添加实时分析逻辑
}
</script>

<style scoped>
.hardware-text-analyzer {
  padding: 20px;
}

.analyzer-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.input-section {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.result-section {
  margin-top: 20px;
}

.result-card {
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 16px;
  height: 200px;
  overflow-y: auto;
}

.result-card h4 {
  margin: 0 0 12px 0;
  color: #1890ff;
  font-weight: 600;
}

.result-item {
  display: flex;
  margin-bottom: 8px;
  align-items: center;
}

.result-item .label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.result-item .value {
  color: #999;
  margin-left: 8px;
}

.result-item .value.detected {
  color: #52c41a;
  font-weight: 500;
}

.spec-list {
  max-height: 150px;
  overflow-y: auto;
}

.spec-item {
  display: flex;
  margin-bottom: 8px;
  padding: 6px 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e8e8e8;
}

.spec-key {
  font-weight: 500;
  color: #1890ff;
  min-width: 60px;
}

.spec-value {
  color: #333;
  margin-left: 8px;
}

.no-specs {
  color: #999;
  text-align: center;
  padding: 20px;
}

.apply-section {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.apply-button {
  min-width: 120px;
}

.form-item {
  margin-bottom: 16px;
}
</style>