<template>
  <div class="license-actions">
    <!-- 详情模态框 -->
    <a-modal
      v-model:open="detailVisible"
      title="软件资产详情"
      width="800px"
      :footer="null"
    >
      <div v-if="selectedAsset" class="asset-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="软件名称">
            {{ selectedAsset.software_name }}
          </a-descriptions-item>
          <a-descriptions-item label="版本">
            {{ selectedAsset.version }}
          </a-descriptions-item>
          <a-descriptions-item label="供应商">
            {{ selectedAsset.vendor }}
          </a-descriptions-item>
          <a-descriptions-item label="软件类型">
            <a-tag :color="getSoftwareTypeColor(selectedAsset.software_type)">
              {{ getSoftwareTypeText(selectedAsset.software_type) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="许可证类型">
            <a-tag :color="getLicenseTypeColor(selectedAsset.license_type)">
              {{ getLicenseTypeText(selectedAsset.license_type) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="许可证数量">
            {{ selectedAsset.license_count }}
          </a-descriptions-item>
          <a-descriptions-item label="已使用数量">
            {{ selectedAsset.used_count }}
          </a-descriptions-item>
          <a-descriptions-item label="可用数量">
            <span :style="{ color: selectedAsset.available_count > 0 ? '#52c41a' : '#f5222d' }">
              {{ selectedAsset.available_count }}
            </span>
          </a-descriptions-item>
          <a-descriptions-item label="采购日期">
            {{ selectedAsset.purchase_date }}
          </a-descriptions-item>
          <a-descriptions-item label="许可证开始日期">
            {{ selectedAsset.license_start_date }}
          </a-descriptions-item>
          <a-descriptions-item label="许可证到期日期">
            <span :style="{ color: getLicenseEndDateColor(selectedAsset.license_end_date) }">
              {{ selectedAsset.license_end_date }}
            </span>
          </a-descriptions-item>
          <a-descriptions-item label="许可证状态">
            <a-tag :color="getLicenseStatusColor(selectedAsset.license_status)">
              {{ getLicenseStatusText(selectedAsset.license_status) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="部署位置" :span="2">
            {{ selectedAsset.deployment_location }}
          </a-descriptions-item>
          <a-descriptions-item label="负责人">
            {{ selectedAsset.responsible_person }}
          </a-descriptions-item>
          <a-descriptions-item label="联系方式">
            {{ selectedAsset.contact_info }}
          </a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">
            {{ selectedAsset.notes || '-' }}
          </a-descriptions-item>
        </a-descriptions>
        
        <!-- 部署信息 -->
        <div v-if="selectedAsset.deployments && selectedAsset.deployments.length > 0" class="deployment-section">
          <h4>部署信息</h4>
          <a-table
            :data-source="selectedAsset.deployments"
            :pagination="false"
            size="small"
            bordered
          >
            <a-table-column title="部署位置" data-index="deployment_location" />
            <a-table-column title="使用数量" data-index="used_count" />
            <a-table-column title="部署日期" data-index="deployment_date" />
            <a-table-column title="状态" data-index="status">
              <template #default="{ record }">
                <a-tag :color="record.status === 'active' ? 'green' : 'red'">
                  {{ record.status === 'active' ? '活跃' : '停用' }}
                </a-tag>
              </template>
            </a-table-column>
          </a-table>
        </div>
      </div>
    </a-modal>

    <!-- 许可证管理模态框 -->
    <a-modal
      v-model:open="licenseVisible"
      title="许可证管理"
      width="600px"
      @ok="handleLicenseConfirm"
    >
      <a-form
        ref="licenseFormRef"
        :model="licenseFormData"
        :rules="licenseRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="许可证类型" name="license_type">
              <a-select v-model:value="licenseFormData.license_type" placeholder="请选择许可证类型">
                <a-select-option value="perpetual">永久许可</a-select-option>
                <a-select-option value="subscription">订阅许可</a-select-option>
                <a-select-option value="trial">试用许可</a-select-option>
                <a-select-option value="free">免费许可</a-select-option>
                <a-select-option value="oem">OEM许可</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="许可证数量" name="license_count">
              <a-input-number
                v-model:value="licenseFormData.license_count"
                :min="1"
                placeholder="请输入许可证数量"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="许可证开始日期" name="license_start_date">
              <a-date-picker
                v-model:value="licenseFormData.license_start_date"
                placeholder="请选择开始日期"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="许可证到期日期" name="license_end_date">
              <a-date-picker
                v-model:value="licenseFormData.license_end_date"
                placeholder="请选择到期日期"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-form-item label="许可证密钥" name="license_key">
          <a-textarea
            v-model:value="licenseFormData.license_key"
            placeholder="请输入许可证密钥"
            :rows="3"
          />
        </a-form-item>
        
        <a-form-item label="备注" name="notes">
          <a-textarea
            v-model:value="licenseFormData.notes"
            placeholder="请输入备注信息"
            :rows="2"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import dayjs from 'dayjs';

// Props
const props = defineProps({
  selectedAsset: {
    type: Object,
    default: null
  },
  detailModalVisible: {
    type: Boolean,
    default: false
  },
  licenseModalVisible: {
    type: Boolean,
    default: false
  },
  licenseFormData: {
    type: Object,
    default: () => ({})
  },
  licenseRules: {
    type: Object,
    default: () => ({})
  }
});

// Emits
const emit = defineEmits([
  'update:detailModalVisible',
  'update:licenseModalVisible',
  'license-confirm',
  'refresh'
]);

// 使用计算属性处理modal显示状态
const detailVisible = computed({
  get: () => props.detailModalVisible,
  set: (value) => emit('update:detailModalVisible', value)
});

const licenseVisible = computed({
  get: () => props.licenseModalVisible,
  set: (value) => emit('update:licenseModalVisible', value)
});

// 表单引用
const licenseFormRef = ref();

// 许可证表单数据
const licenseFormData = ref({
  license_type: '',
  license_count: 1,
  license_start_date: null,
  license_end_date: null,
  license_key: '',
  notes: ''
});

// 表单验证规则
const licenseRules = {
  license_type: [
    { required: true, message: '请选择许可证类型', trigger: 'change' }
  ],
  license_count: [
    { required: true, message: '请输入许可证数量', trigger: 'blur' },
    { type: 'number', min: 1, message: '许可证数量必须大于0', trigger: 'blur' }
  ],
  license_start_date: [
    { required: true, message: '请选择许可证开始日期', trigger: 'change' }
  ],
  license_end_date: [
    {
      validator: (rule, value) => {
        if (!value) {
          return Promise.resolve();
        }
        if (licenseFormData.value.license_start_date && dayjs(value).isBefore(dayjs(licenseFormData.value.license_start_date))) {
          return Promise.reject('到期日期不能早于开始日期');
        }
        return Promise.resolve();
      },
      trigger: 'change'
    }
  ]
};

// 监听许可证模态框显示状态，初始化表单数据
watch(() => props.licenseModalVisible, (visible) => {
  if (visible && props.selectedAsset) {
    licenseFormData.value = {
      license_type: props.selectedAsset.license_type || '',
      license_count: props.selectedAsset.license_count || 1,
      license_start_date: props.selectedAsset.license_start_date ? dayjs(props.selectedAsset.license_start_date) : null,
      license_end_date: props.selectedAsset.license_end_date ? dayjs(props.selectedAsset.license_end_date) : null,
      license_key: props.selectedAsset.license_key || '',
      notes: props.selectedAsset.notes || ''
    };
  }
});

// 处理许可证确认
const handleLicenseConfirm = async () => {
  try {
    await licenseFormRef.value.validate();
    
    const formData = {
      ...licenseFormData.value,
      license_start_date: licenseFormData.value.license_start_date ? licenseFormData.value.license_start_date.format('YYYY-MM-DD') : null,
      license_end_date: licenseFormData.value.license_end_date ? licenseFormData.value.license_end_date.format('YYYY-MM-DD') : null
    };
    
    emit('license-confirm', formData);
  } catch (error) {
    console.error('表单验证失败:', error);
  }
};

// 状态颜色和文本函数
const getSoftwareTypeColor = (type) => {
  const colorMap = {
    'system': 'blue',
    'application': 'green',
    'development': 'purple',
    'security': 'red',
    'database': 'orange',
    'middleware': 'cyan',
    'other': 'default'
  };
  return colorMap[type] || 'default';
};

const getSoftwareTypeText = (type) => {
  const textMap = {
    'system': '系统软件',
    'application': '应用软件',
    'development': '开发工具',
    'security': '安全软件',
    'database': '数据库',
    'middleware': '中间件',
    'other': '其他'
  };
  return textMap[type] || type;
};

const getLicenseTypeColor = (type) => {
  const colorMap = {
    'perpetual': 'green',
    'subscription': 'blue',
    'trial': 'orange',
    'free': 'cyan',
    'oem': 'purple'
  };
  return colorMap[type] || 'default';
};

const getLicenseTypeText = (type) => {
  const textMap = {
    'perpetual': '永久许可',
    'subscription': '订阅许可',
    'trial': '试用许可',
    'free': '免费许可',
    'oem': 'OEM许可'
  };
  return textMap[type] || type;
};

const getLicenseStatusColor = (status) => {
  const colorMap = {
    'valid': 'green',
    'expired': 'red',
    'near_expired': 'orange',
    'unlimited': 'blue'
  };
  return colorMap[status] || 'default';
};

const getLicenseStatusText = (status) => {
  const textMap = {
    'valid': '有效',
    'expired': '已过期',
    'near_expired': '即将过期',
    'unlimited': '永久'
  };
  return textMap[status] || status;
};

const getLicenseEndDateColor = (endDate) => {
  if (!endDate) return '#666';
  
  const today = new Date();
  const end = new Date(endDate);
  const diffDays = Math.ceil((end - today) / (1000 * 60 * 60 * 24));
  
  if (diffDays < 0) return '#f5222d'; // 已过期
  if (diffDays <= 30) return '#fa8c16'; // 即将过期
  return '#52c41a'; // 正常
};
</script>

<style scoped>
.license-actions {
  /* 组件样式 */
}

.asset-detail {
  max-height: 600px;
  overflow-y: auto;
}

.deployment-section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.deployment-section h4 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
}
</style>