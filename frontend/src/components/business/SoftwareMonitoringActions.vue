<template>
  <div class="software-monitoring-actions">
    <!-- 软件详情模态框 -->
    <a-modal
      v-model:open="detailsVisible"
      title="软件详情"
      width="600px"
      :footer="null"
    >
      <a-descriptions 
        v-if="currentSoftware"
        :column="2" 
        bordered
        size="small"
      >
        <a-descriptions-item label="软件名称">
          {{ currentSoftware.name }}
        </a-descriptions-item>
        <a-descriptions-item label="软件版本">
          {{ currentSoftware.version || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="软件类型">
          {{ currentSoftware.type || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="许可证状态">
          <a-tag :color="getLicenseStatusColor(currentSoftware.license_status)">
            {{ getLicenseStatusLabel(currentSoftware.license_status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="安装路径">
          {{ currentSoftware.install_path || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="供应商">
          {{ currentSoftware.vendor || '-' }}
        </a-descriptions-item>
        <a-descriptions-item label="最后更新">
          {{ formatTime(currentSoftware.last_updated) }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ formatTime(currentSoftware.created_at) }}
        </a-descriptions-item>
        <a-descriptions-item label="备注" :span="2">
          {{ currentSoftware.remark || '-' }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>

    <!-- 软件扫描配置弹窗 -->
    <a-modal
      v-model:open="scanConfigVisible"
      title="软件扫描配置"
      width="800px"
      @ok="startScan"
      :confirm-loading="scanLoading"
      ok-text="开始扫描"
      cancel-text="取消"
    >
      <a-form
        :model="scanForm"
        :rules="scanRules"
        ref="scanFormRef"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="扫描范围" name="scan_scope">
              <a-select
                v-model:value="scanForm.scan_scope"
                placeholder="选择扫描范围"
              >
                <a-select-option value="local">本地计算机</a-select-option>
                <a-select-option value="network">网络范围</a-select-option>
                <a-select-option value="custom">自定义路径</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="扫描类型" name="scan_types">
              <a-select
                v-model:value="scanForm.scan_types"
                mode="multiple"
                placeholder="选择扫描类型"
              >
                <a-select-option value="installed">已安装软件</a-select-option>
                <a-select-option value="registry">注册表扫描</a-select-option>
                <a-select-option value="files">文件系统扫描</a-select-option>
                <a-select-option value="services">服务扫描</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="24" v-if="scanForm.scan_scope === 'custom'">
            <a-form-item label="自定义路径" name="custom_paths">
              <a-textarea 
                v-model:value="scanForm.custom_paths" 
                placeholder="请输入扫描路径，每行一个路径"
                :rows="3"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="并发数" name="concurrent">
              <a-input-number 
                v-model:value="scanForm.concurrent" 
                :min="1" 
                :max="50"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="超时(秒)" name="timeout">
              <a-input-number 
                v-model:value="scanForm.timeout" 
                :min="5" 
                :max="300"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="深度扫描" name="deep_scan">
              <a-switch v-model:checked="scanForm.deep_scan" />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-form-item label="过滤配置">
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="包含关键词" name="include_keywords">
                <a-input v-model:value="scanForm.include_keywords" placeholder="用逗号分隔" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="排除关键词" name="exclude_keywords">
                <a-input v-model:value="scanForm.exclude_keywords" placeholder="用逗号分隔" />
              </a-form-item>
            </a-col>
          </a-row>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 批量操作结果展示 -->
    <a-modal
      v-model:open="batchResultVisible"
      title="批量操作结果"
      width="800px"
      :footer="null"
    >
      <div class="batch-results">
        <div class="result-summary">
          <a-statistic
            title="总计"
            :value="batchResults.length"
            style="margin-right: 32px"
          />
          <a-statistic
            title="成功"
            :value="batchResults.filter(r => r.success).length"
            :value-style="{ color: '#3f8600' }"
            style="margin-right: 32px"
          />
          <a-statistic
            title="失败"
            :value="batchResults.filter(r => !r.success).length"
            :value-style="{ color: '#cf1322' }"
          />
        </div>
        
        <a-divider />
        
        <div class="result-list">
          <div 
            v-for="result in batchResults" 
            :key="result.id"
            class="result-item"
            :class="{ success: result.success, failed: !result.success }"
          >
            <div class="result-name">{{ result.name }}</div>
            <div class="result-status">
              <a-tag :color="result.success ? 'success' : 'error'">
                {{ result.success ? '成功' : '失败' }}
              </a-tag>
            </div>
            <div class="result-operation">{{ result.operation }}</div>
            <div class="result-error" v-if="result.error">
              {{ result.error }}
            </div>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- 任务结果弹窗 -->
    <a-modal
      v-model:open="taskResultVisible"
      title="任务执行结果"
      width="600px"
      :footer="null"
    >
      <div class="task-result">
        <a-result
          :status="taskResult.success ? 'success' : 'error'"
          :title="taskResult.title"
          :sub-title="taskResult.message"
        >
          <template #extra v-if="taskResult.details">
            <div class="task-details">
              <h4>详细信息：</h4>
              <pre>{{ taskResult.details }}</pre>
            </div>
          </template>
        </a-result>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';

// Emits
const emit = defineEmits([
  'start-scan',
  'refresh'
]);

// 响应式数据
const detailsVisible = ref(false);
const scanConfigVisible = ref(false);
const batchResultVisible = ref(false);
const taskResultVisible = ref(false);
const scanLoading = ref(false);
const currentSoftware = ref(null);
const batchResults = ref([]);
const taskResult = ref({});
const scanFormRef = ref();

// 扫描表单数据
const scanForm = reactive({
  scan_scope: 'local',
  scan_types: ['installed'],
  custom_paths: '',
  concurrent: 10,
  timeout: 60,
  deep_scan: false,
  include_keywords: '',
  exclude_keywords: ''
});

// 表单验证规则
const scanRules = {
  scan_scope: [
    { required: true, message: '请选择扫描范围', trigger: 'change' }
  ],
  scan_types: [
    { required: true, message: '请选择扫描类型', trigger: 'change' }
  ],
  custom_paths: [
    { 
      validator: (rule, value) => {
        if (scanForm.scan_scope === 'custom' && !value) {
          return Promise.reject('请输入自定义路径');
        }
        return Promise.resolve();
      },
      trigger: 'blur'
    }
  ],
  concurrent: [
    { required: true, message: '请输入并发数', trigger: 'blur' }
  ],
  timeout: [
    { required: true, message: '请输入超时时间', trigger: 'blur' }
  ]
};

// 方法
const formatTime = (time) => {
  if (!time) return '-';
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss');
};

const getLicenseStatusColor = (status) => {
  const colorMap = {
    'valid': 'success',
    'expired': 'error',
    'trial': 'warning',
    'unknown': 'default'
  };
  return colorMap[status] || 'default';
};

const getLicenseStatusLabel = (status) => {
  const labelMap = {
    'valid': '有效',
    'expired': '已过期',
    'trial': '试用版',
    'unknown': '未知'
  };
  return labelMap[status] || '未知';
};

const showSoftwareDetails = (software) => {
  currentSoftware.value = software;
  detailsVisible.value = true;
};

const showScanConfig = () => {
  scanConfigVisible.value = true;
};

const showBatchResults = (results) => {
  batchResults.value = results;
  batchResultVisible.value = true;
};

const showTaskResult = (result) => {
  taskResult.value = result;
  taskResultVisible.value = true;
};

const startScan = async () => {
  try {
    await scanFormRef.value.validate();
    scanLoading.value = true;
    
    const result = await emit('start-scan', { ...scanForm });
    
    if (result && result.success) {
      message.success('扫描任务已启动');
      scanConfigVisible.value = false;
      
      // 显示任务结果
      showTaskResult({
        success: true,
        title: '扫描任务启动成功',
        message: '正在后台执行软件扫描任务，请稍后查看结果',
        details: result.task_id ? `任务ID: ${result.task_id}` : null
      });
    } else {
      showTaskResult({
        success: false,
        title: '扫描任务启动失败',
        message: result?.message || '未知错误',
        details: result?.details
      });
    }
  } catch (error) {
    console.error('表单验证失败:', error);
  } finally {
    scanLoading.value = false;
  }
};

const resetScanForm = () => {
  Object.assign(scanForm, {
    scan_scope: 'local',
    scan_types: ['installed'],
    custom_paths: '',
    concurrent: 10,
    timeout: 60,
    deep_scan: false,
    include_keywords: '',
    exclude_keywords: ''
  });
  scanFormRef.value?.resetFields();
};

// 暴露方法给父组件
defineExpose({
  showSoftwareDetails,
  showScanConfig,
  showBatchResults,
  showTaskResult,
  resetScanForm
});
</script>

<style scoped>
/* 简洁容器样式 */
.software-monitoring-actions {
  position: relative;
  background: transparent;
  border: none;
}

/* 简洁批量结果展示 */
.batch-results {
  max-height: 500px;
  overflow-y: auto;
  padding: 4px;
  background: #ffffff;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.batch-results::-webkit-scrollbar {
  width: 6px;
}

.batch-results::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.batch-results::-webkit-scrollbar-thumb {
  background: #3b82f6;
  border-radius: 3px;
}

/* 简洁结果摘要 */
.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.result-summary .ant-statistic {
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 简洁结果列表 */
.result-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  transition: all 0.2s ease;
  background: #ffffff;
  border-left: 3px solid transparent;
}

.result-item.success {
  border-left-color: #10b981;
  background: #f0fdf4;
}

.result-item.failed {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.result-item:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.result-name {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-weight: 600;
  flex: 1;
  font-size: 14px;
  color: #2d3748;
}

.result-status {
  flex: 0 0 auto;
  margin: 0 16px;
}

.result-operation {
  flex: 0 0 auto;
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 12px;
  font-weight: 600;
  margin: 0 16px;
}

.result-error {
  flex: 2;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 12px;
  font-weight: 600;
  text-align: right;
}

/* 简洁任务结果 */
.task-result {
  text-align: center;
  padding: 24px;
  background: #ffffff;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.task-details {
  text-align: left;
  margin-top: 24px;
  background: #f8fafc;
  border-radius: 6px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.task-details h4 {
  margin-bottom: 12px;
  font-weight: 600;
  color: #3b82f6;
}

.task-details pre {
  background: #f1f5f9;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.task-details pre::-webkit-scrollbar {
  width: 6px;
}

.task-details pre::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.task-details pre::-webkit-scrollbar-thumb {
  background: #3b82f6;
  border-radius: 3px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-summary {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 16px;
  }
  
  .result-status,
  .result-operation,
  .result-error {
    margin: 0;
  }
  
  .task-details {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .result-summary {
    grid-template-columns: 1fr;
  }
}

/* 现代化模态框样式 */
:deep(.ant-modal) {
  border-radius: 20px;
  overflow: hidden;
}

:deep(.ant-modal-content) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.ant-modal-header) {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px 20px 0 0;
  padding: 24px 32px;
}

:deep(.ant-modal-title) {
  font-weight: 700;
  font-size: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:deep(.ant-modal-body) {
  padding: 32px;
}

:deep(.ant-modal-footer) {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  padding: 20px 32px;
  border-radius: 0 0 20px 20px;
}

/* 现代化描述列表样式 */
:deep(.ant-descriptions) {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.ant-descriptions-item-label) {
  font-weight: 700;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  color: #4a5568;
}

:deep(.ant-descriptions-item-content) {
  color: #2d3748;
  font-weight: 500;
}

/* 现代化表单样式 */
:deep(.ant-form-item-label > label) {
  font-weight: 700;
  color: #4a5568;
}

:deep(.ant-input) {
  border-radius: 12px;
  border: 2px solid rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.ant-input:focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

:deep(.ant-select .ant-select-selector) {
  border-radius: 12px !important;
  border: 2px solid rgba(102, 126, 234, 0.1) !important;
  background: rgba(255, 255, 255, 0.8) !important;
  backdrop-filter: blur(10px);
}

:deep(.ant-select:not(.ant-select-disabled):hover .ant-select-selector) {
  border-color: #667eea !important;
}

/* 现代化统计组件样式 */
:deep(.ant-statistic-title) {
  font-size: 12px;
  color: #718096;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

:deep(.ant-statistic-content) {
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 现代化标签样式 */
:deep(.ant-tag) {
  border-radius: 20px;
  padding: 4px 12px;
  font-weight: 600;
  border: none;
  font-size: 12px;
}

:deep(.ant-tag-success) {
  background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
  color: white;
}

:deep(.ant-tag-processing) {
  background: linear-gradient(135deg, #45b7d1 0%, #2980b9 100%);
  color: white;
}

:deep(.ant-tag-warning) {
  background: linear-gradient(135deg, #feca57 0%, #ff9ff3 100%);
  color: white;
}

:deep(.ant-tag-error) {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
  color: white;
}

:deep(.ant-tag-default) {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #2d3748;
}
</style>