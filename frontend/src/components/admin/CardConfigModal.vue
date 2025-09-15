<template>
  <a-modal
    v-model:open="visible"
    title="自定义监控卡片"
    width="600px"
    @ok="handleSave"
    @cancel="handleCancel"
  >
    <a-form
      :model="formData"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 18 }"
    >
      <a-form-item label="卡片标题" required>
        <a-input v-model:value="formData.title" placeholder="请输入卡片标题" />
      </a-form-item>
      
      <a-form-item label="数据类型" required>
        <a-select v-model:value="formData.dataType" placeholder="请选择数据类型">
          <a-select-option value="cpu">CPU使用率</a-select-option>
          <a-select-option value="memory">内存使用率</a-select-option>
          <a-select-option value="disk">磁盘使用率</a-select-option>
          <a-select-option value="network">网络流量</a-select-option>
          <a-select-option value="process">进程数量</a-select-option>
          <a-select-option value="connection">连接数</a-select-option>
          <a-select-option value="response_time">响应时间</a-select-option>
          <a-select-option value="error_rate">错误率</a-select-option>
          <a-select-option value="custom">自定义</a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item v-if="formData.dataType === 'custom'" label="数据源URL">
        <a-input v-model:value="formData.dataUrl" placeholder="请输入数据API地址" />
      </a-form-item>
      
      <a-form-item label="显示类型" required>
        <a-radio-group v-model:value="formData.chartType">
          <a-radio value="bar">条形图</a-radio>
          <a-radio value="line">折线图</a-radio>
          <a-radio value="list">列表</a-radio>
        </a-radio-group>
      </a-form-item>
      
      <a-form-item label="显示数量">
        <a-input-number 
          v-model:value="formData.topCount" 
          :min="3" 
          :max="10" 
          placeholder="显示前N名"
        />
      </a-form-item>
      
      <a-form-item label="单位">
        <a-input v-model:value="formData.unit" placeholder="如：%、MB/s、ms等" />
      </a-form-item>
      
      <a-form-item label="主题色">
        <div class="color-picker">
          <div 
            v-for="color in colorOptions" 
            :key="color"
            class="color-item"
            :class="{ active: formData.color === color }"
            :style="{ backgroundColor: color }"
            @click="formData.color = color"
          ></div>
        </div>
      </a-form-item>
      
      <a-form-item label="刷新间隔">
        <a-select v-model:value="formData.refreshInterval" placeholder="数据刷新频率">
          <a-select-option :value="30">30秒</a-select-option>
          <a-select-option :value="60">1分钟</a-select-option>
          <a-select-option :value="300">5分钟</a-select-option>
          <a-select-option :value="600">10分钟</a-select-option>
          <a-select-option :value="1800">30分钟</a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="启用告警">
        <a-switch v-model:checked="formData.enableAlert" />
      </a-form-item>
      
      <a-form-item v-if="formData.enableAlert" label="告警阈值">
        <a-input-number 
          v-model:value="formData.alertThreshold" 
          :min="0" 
          :max="100" 
          placeholder="超过此值时告警"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { ref, reactive, watch } from 'vue';

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  cardData: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['update:open', 'save']);

const visible = ref(false);

const formData = reactive({
  title: '',
  dataType: '',
  dataUrl: '',
  chartType: 'bar',
  topCount: 5,
  unit: '%',
  color: '#1890ff',
  refreshInterval: 60,
  enableAlert: false,
  alertThreshold: 80
});

const colorOptions = [
  '#1890ff', '#52c41a', '#faad14', '#f5222d', 
  '#722ed1', '#13c2c2', '#eb2f96', '#fa8c16',
  '#2f54eb', '#87d068', '#ffc53d', '#ff7875'
];

watch(() => props.open, (newVal) => {
  visible.value = newVal;
  if (newVal && props.cardData) {
    Object.assign(formData, {
      title: props.cardData.title || '',
      dataType: getDataTypeFromTitle(props.cardData.title),
      dataUrl: props.cardData.dataUrl || '',
      chartType: props.cardData.chartType || 'bar',
      topCount: props.cardData.data?.length || 5,
      unit: props.cardData.unit || '%',
      color: props.cardData.color || '#1890ff',
      refreshInterval: props.cardData.refreshInterval || 60,
      enableAlert: props.cardData.enableAlert || false,
      alertThreshold: props.cardData.alertThreshold || 80
    });
  }
});

watch(visible, (newVal) => {
  emit('update:open', newVal);
});

// 根据标题推测数据类型
const getDataTypeFromTitle = (title) => {
  if (!title) return '';
  
  if (title.includes('CPU')) return 'cpu';
  if (title.includes('内存')) return 'memory';
  if (title.includes('磁盘') || title.includes('文件')) return 'disk';
  if (title.includes('网络')) return 'network';
  if (title.includes('进程')) return 'process';
  if (title.includes('连接')) return 'connection';
  if (title.includes('响应')) return 'response_time';
  if (title.includes('错误')) return 'error_rate';
  
  return 'custom';
};

const handleSave = () => {
  // 验证必填字段
  if (!formData.title || !formData.dataType) {
    return;
  }
  
  // 构造卡片配置
  const cardConfig = {
    id: props.cardData.id || `card_${Date.now()}`,
    title: formData.title,
    type: 'chart',
    chartType: formData.chartType,
    dataType: formData.dataType,
    dataUrl: formData.dataUrl,
    topCount: formData.topCount,
    unit: formData.unit,
    color: formData.color,
    refreshInterval: formData.refreshInterval,
    enableAlert: formData.enableAlert,
    alertThreshold: formData.alertThreshold,
    data: generateMockData() // 生成模拟数据
  };
  
  emit('save', cardConfig);
  visible.value = false;
};

const handleCancel = () => {
  visible.value = false;
};

// 生成模拟数据
const generateMockData = () => {
  const count = formData.topCount;
  const data = [];
  
  for (let i = 0; i < count; i++) {
    data.push({
      name: `${getServerPrefix()}-${String(i + 1).padStart(2, '0')}`,
      value: Math.floor(Math.random() * 100),
      detail: getDetailInfo()
    });
  }
  
  // 按值排序
  return data.sort((a, b) => b.value - a.value);
};

const getServerPrefix = () => {
  const prefixes = ['web-server', 'db-server', 'app-server', 'cache-server', 'proxy-server'];
  return prefixes[Math.floor(Math.random() * prefixes.length)];
};

const getDetailInfo = () => {
  switch (formData.dataType) {
    case 'cpu': return 'CPU负载';
    case 'memory': return '内存占用';
    case 'disk': return '磁盘占用';
    case 'network': return '网络带宽';
    case 'process': return '进程数量';
    case 'connection': return '连接数量';
    case 'response_time': return '平均响应时间';
    case 'error_rate': return '错误率';
    default: return '自定义指标';
  }
};
</script>

<style scoped>
.color-picker {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.color-item {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.color-item:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.color-item.active {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}
</style>