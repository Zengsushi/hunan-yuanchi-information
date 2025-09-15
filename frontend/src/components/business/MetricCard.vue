<template>
  <div class="metric-card">
    <div class="metric-icon" :style="{ backgroundColor: iconBgColor }">
      <component :is="iconComponent" :style="{ color: iconColor }" />
    </div>
    <div class="metric-content">
      <div class="metric-label">{{ metric.label }}</div>
      <div class="metric-value">{{ formatValue(metric.value) }}</div>
      <div class="metric-change" v-if="metric.change">
        <span :class="['change-indicator', metric.trend]">
          <ArrowUpOutlined v-if="metric.trend === 'up'" />
          <ArrowDownOutlined v-if="metric.trend === 'down'" />
          {{ metric.change }}
        </span>
        {{ metric.changeLabel || '较上月' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons-vue';
import * as Icons from '@ant-design/icons-vue';

const props = defineProps({
  metric: {
    type: Object,
    required: true,
    validator: (value) => {
      return value.label && value.value !== undefined;
    }
  }
});

const iconComponent = computed(() => {
  if (!props.metric.icon) return 'div';
  
  if (typeof props.metric.icon === 'string') {
    return Icons[props.metric.icon] || 'div';
  }
  
  return props.metric.icon;
});

const iconBgColor = computed(() => {
  return props.metric.iconBgColor || 'linear-gradient(135deg, #e6f7ff, #bae7ff)';
});

const iconColor = computed(() => {
  return props.metric.iconColor || '#1890ff';
});

const formatValue = (value) => {
  if (value === null || value === undefined) {
    return '-';
  }
  
  if (typeof value === 'number') {
    if (value >= 10000) {
      return (value / 10000).toFixed(1) + '万';
    }
    if (value >= 1000) {
      return (value / 1000).toFixed(1) + 'k';
    }
    return value.toString();
  }
  
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  
  return String(value);
};
</script>

<style scoped>
.metric-card {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(24, 144, 255, 0.06);
  border: 1px solid rgba(24, 144, 255, 0.04);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 90px;
  backdrop-filter: blur(10px);
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #1890ff, #40a9ff, #69c0ff);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(24, 144, 255, 0.12);
}

.metric-card:hover::before {
  opacity: 1;
}

.metric-card::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(24, 144, 255, 0.03) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.metric-card:hover::after {
  opacity: 1;
}

.metric-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-icon .anticon {
  font-size: 22px;
  color: #1890ff;
}

.metric-content {
  flex: 1;
}

.metric-label {
  color: #8c8c8c;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 3px;
  line-height: 1.2;
}

.metric-value {
  font-size: 26px;
  font-weight: 700;
  color: #262626;
  line-height: 1.1;
  margin-bottom: 4px;
}

.metric-change {
  font-size: 12px;
  color: #8c8c8c;
  display: flex;
  align-items: center;
  gap: 4px;
  line-height: 1.2;
}

.change-indicator {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 11px;
  backdrop-filter: blur(4px);
}

.change-indicator.up {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.change-indicator.down {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

.change-indicator .anticon {
  font-size: 10px;
}

@media (max-width: 768px) {
  .metric-card {
    padding: 16px;
    gap: 14px;
    min-height: 80px;
  }
  
  .metric-icon {
    width: 42px;
    height: 42px;
  }
  
  .metric-icon .anticon {
    font-size: 18px;
  }
  
  .metric-value {
    font-size: 22px;
  }
  
  .metric-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .metric-card {
    padding: 14px;
    gap: 12px;
    min-height: 70px;
  }
  
  .metric-icon {
    width: 36px;
    height: 36px;
  }
  
  .metric-icon .anticon {
    font-size: 16px;
  }
  
  .metric-value {
    font-size: 20px;
  }
  
  .metric-label {
    font-size: 11px;
  }
  
  .metric-change {
    font-size: 11px;
  }
}
</style>