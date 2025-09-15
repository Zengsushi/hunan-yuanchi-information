<template>
  <a-card class="monitoring-card" :bordered="false">
    <template #title>
      <div class="card-header">
        <span class="card-title">{{ card.title }}</span>
        <div class="card-actions">
          <a-tooltip title="刷新数据">
            <a-button 
              type="text" 
              size="small" 
              @click="$emit('refresh', card.id)"
              :loading="refreshing"
            >
              <ReloadOutlined />
            </a-button>
          </a-tooltip>
        </div>
      </div>
    </template>
    
    <div class="card-content">
      <!-- 图表显示 -->
      <div v-if="card.type === 'chart'" class="chart-container">
        <div 
          v-for="(item, index) in card.data" 
          :key="index"
          class="chart-item"
        >
          <div class="item-info">
            <div class="item-name">{{ item.name }}</div>
            <div class="item-value">{{ item.value }}{{ card.unit }}</div>
          </div>
          <div class="item-bar">
            <div 
              class="bar-fill"
              :style="{ 
                width: `${getPercentage(item.value)}%`,
                backgroundColor: card.color 
              }"
            ></div>
          </div>
        </div>
      </div>
      
      <!-- 列表显示 -->
      <div v-else-if="card.type === 'list'" class="list-container">
        <div 
          v-for="(item, index) in card.data" 
          :key="index"
          class="list-item"
        >
          <div class="item-rank">{{ index + 1 }}</div>
          <div class="item-content">
            <div class="item-name">{{ item.name }}</div>
            <div class="item-detail">{{ item.detail }}</div>
          </div>
          <div class="item-value">{{ item.value }}{{ card.unit }}</div>
        </div>
      </div>
      
      <!-- 空数据状态 -->
      <div v-if="!card.data || card.data.length === 0" class="empty-state">
        <InboxOutlined class="empty-icon" />
        <p>暂无数据</p>
      </div>
    </div>
  </a-card>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ReloadOutlined, InboxOutlined } from '@ant-design/icons-vue';

const props = defineProps({
  card: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['refresh']);

const refreshing = ref(false);

// 计算百分比
const getPercentage = (value) => {
  if (!props.card.data || props.card.data.length === 0) return 0;
  
  const maxValue = Math.max(...props.card.data.map(item => item.value));
  return (value / maxValue) * 100;
};

// 处理刷新
const handleRefresh = async () => {
  refreshing.value = true;
  try {
    emit('refresh', props.card.id);
    // 模拟刷新延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
  } finally {
    refreshing.value = false;
  }
};
</script>

<style scoped>
.monitoring-card {
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(24, 144, 255, 0.06);
  border: 1px solid rgba(24, 144, 255, 0.04);
  overflow: hidden;
  height: 100%;
  transition: all 0.3s ease;
}

.monitoring-card:hover {
  box-shadow: 0 4px 20px rgba(24, 144, 255, 0.1);
  transform: translateY(-1px);
}

:deep(.monitoring-card .ant-card-head) {
  background: linear-gradient(135deg, #f8faff 0%, #ffffff 100%);
  border-bottom: 1px solid rgba(24, 144, 255, 0.08);
  padding: 12px 16px;
  min-height: auto;
}

:deep(.monitoring-card .ant-card-body) {
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  padding: 16px;
  height: calc(100% - 60px);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #434343;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.card-content {
  height: 100%;
  overflow: hidden;
}

/* 图表样式 */
.chart-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
}

.item-info {
  min-width: 80px;
  flex-shrink: 0;
}

.item-name {
  font-size: 12px;
  color: #595959;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-value {
  font-size: 13px;
  font-weight: 600;
  color: #262626;
}

.item-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
  position: relative;
}

.bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 0 4px 4px 0;
}

/* 列表样式 */
.list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);
}

.list-item:last-child {
  border-bottom: none;
}

.item-rank {
  width: 20px;
  height: 20px;
  background: #1890ff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
}

.item-detail {
  font-size: 11px;
  color: #8c8c8c;
  margin-top: 2px;
}

/* 空状态 */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #bfbfbf;
}

.empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 12px;
  margin: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .chart-item {
    gap: 8px;
    padding: 4px 0;
  }
  
  .item-info {
    min-width: 70px;
  }
  
  .item-name {
    font-size: 11px;
  }
  
  .item-value {
    font-size: 12px;
  }
  
  .item-bar {
    height: 6px;
  }
  
  .list-item {
    gap: 8px;
    padding: 6px 0;
  }
  
  .item-rank {
    width: 18px;
    height: 18px;
    font-size: 10px;
  }
}
</style>