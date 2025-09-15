<template>
  <div class="dynamic-metrics-container">
    <div 
      class="metrics-grid" 
      :style="gridStyle"
    >
      <MetricCard 
        v-for="(metric, index) in metricsData" 
        :key="metric.id || index"
        :metric="metric"
        :style="getMetricAnimation(index)"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import MetricCard from './MetricCard.vue';

const props = defineProps({
  // JSON 配置数据
  config: {
    type: Object,
    default: () => ({
      grid: {
        columns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '24px',
        responsive: {
          mobile: 'repeat(1, 1fr)',
          tablet: 'repeat(2, 1fr)'
        }
      },
      animation: {
        enabled: true,
        delay: 0.1
      }
    })
  },
  
  // 指标数据数组
  metrics: {
    type: Array,
    default: () => []
  },

  // 网格布局配置
  gridColumns: {
    type: String,
    default: 'repeat(auto-fit, minmax(200px, 1fr))'
  },

  // 网格间距
  gridGap: {
    type: String,
    default: '16px'
  },

  // 是否启用动画
  enableAnimation: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['metric-click', 'metrics-loaded']);

const metricsData = computed(() => {
  if (props.metrics && props.metrics.length > 0) {
    return props.metrics;
  }
  
  return props.config.metrics || [];
});

const gridStyle = computed(() => {
  const columns = props.gridColumns || props.config.grid?.columns || 'repeat(auto-fit, minmax(200px, 1fr))';
  const gap = props.gridGap || props.config.grid?.gap || '16px';
  
  return {
    display: 'grid',
    gridTemplateColumns: columns,
    gap: gap
  };
});

const getMetricAnimation = (index) => {
  const animationEnabled = props.enableAnimation && (props.config.animation?.enabled !== false);
  
  if (!animationEnabled) return {};
  
  const delay = (props.config.animation?.delay || 0.1) * index;
  
  return {
    animation: `fadeIn 0.6s ease-out ${delay}s both`
  };
};

// 从 API 获取数据的方法
const fetchMetrics = async (apiUrl) => {
  try {
    const response = await fetch(apiUrl);
    const data = await response.json();
    emit('metrics-loaded', data);
    return data;
  } catch (error) {
    console.error('获取指标数据失败:', error);
    return [];
  }
};

// 更新单个指标数据
const updateMetric = (metricId, newData) => {
  const index = metricsData.value.findIndex(m => m.id === metricId);
  if (index !== -1) {
    Object.assign(metricsData.value[index], newData);
  }
};

// 添加新指标
const addMetric = (metric) => {
  metricsData.value.push(metric);
};

// 移除指标
const removeMetric = (metricId) => {
  const index = metricsData.value.findIndex(m => m.id === metricId);
  if (index !== -1) {
    metricsData.value.splice(index, 1);
  }
};

// 暴露方法给父组件使用
defineExpose({
  fetchMetrics,
  updateMetric,
  addMetric,
  removeMetric
});

onMounted(() => {
  // 如果配置中有 API URL，自动获取数据
  if (props.config.apiUrl) {
    fetchMetrics(props.config.apiUrl);
  }
});
</script>

<style scoped>
.dynamic-metrics-container {
  width: 100%;
}

.metrics-grid {
  animation: fadeIn 0.6s ease-out;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr) !important;
    gap: 12px !important;
  }
}

@media (max-width: 480px) {
  .metrics-grid {
    grid-template-columns: 1fr !important;
    gap: 10px !important;
  }
}
</style>