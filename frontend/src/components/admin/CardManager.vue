<template>
  <a-modal
    v-model:open="visible"
    title="监控卡片管理"
    width="800px"
    @ok="handleSave"
    @cancel="handleCancel"
  >
    <div class="card-manager">
      <div class="manager-header">
        <div class="header-info">
          <span class="grid-info">2×2田字格布局 | 最多显示4个TOP5监控卡片</span>
        </div>
        <div class="header-actions">
          <a-button 
            type="primary" 
            size="small" 
            :disabled="cards.length >= 4"
            @click="addCard"
          >
            <PlusOutlined /> 添加卡片 ({{ cards.length }}/4)
          </a-button>
        </div>
      </div>
      
      <!-- 2×2田字格预览 -->
      <div class="grid-preview">
        <div 
          v-for="index in 4" 
          :key="index"
          class="grid-slot"
          :class="{ 
            'has-card': cards[index - 1],
            'drag-over': dragOverIndex === index - 1,
            'valid-drop': isValidDropZone(index - 1)
          }"
          @dragover.prevent="handleGridDragOver($event, index - 1)"
          @dragleave="handleGridDragLeave($event, index - 1)"
          @drop="handleGridDrop($event, index - 1)"
        >
          <div 
            v-if="cards[index - 1]" 
            class="preview-card"
            :class="{ 'dragging': dragSourceIndex === index - 1 }"
            draggable="true"
            @dragstart="handleCardDragStart($event, index - 1)"
            @dragend="handleCardDragEnd($event)"
          >
            <div class="card-header">
              <span class="card-title">
                <HolderOutlined class="drag-handle" />
                {{ cards[index - 1].title }}
              </span>
              <div class="card-actions">
                <a-button 
                  type="text" 
                  size="small" 
                  @click.stop="editCard(index - 1)"
                >
                  <EditOutlined />
                </a-button>
                <a-button 
                  type="text" 
                  size="small" 
                  danger
                  @click.stop="removeCard(index - 1)"
                >
                  <DeleteOutlined />
                </a-button>
              </div>
            </div>
            <div class="card-content">
              <div class="chart-mini">
                <div 
                  v-for="item in cards[index - 1].data.slice(0, 3)" 
                  :key="item.name"
                  class="mini-bar"
                >
                  <span class="mini-label">{{ item.name }}</span>
                  <div class="mini-value">{{ item.value }}{{ cards[index - 1].unit }}</div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-slot">
            <PlusOutlined class="add-icon" />
            <span>空位置</span>
          </div>
        </div>
      </div>
      
      <!-- 卡片列表管理 -->
    </div>
    
    <!-- 卡片配置弹窗 -->
    <CardConfigModal
      v-model:open="configModalVisible"
      :card-data="currentEditCard"
      @save="handleSaveCard"
    />
  </a-modal>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  HolderOutlined
} from '@ant-design/icons-vue';
import CardConfigModal from './CardConfigModal.vue';

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  showAlertCard: {
    type: Boolean,
    default: true
  },
  showMetricsCard: {
    type: Boolean,
    default: true
  },
  alertData: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update:open', 'update:modelValue', 'update:showAlertCard', 'update:showMetricsCard', 'save']);

// 响应式数据
const visible = ref(false);
const cards = ref([]);
const configModalVisible = ref(false);
const currentEditCard = ref({});
const dragIndex = ref(-1);
const dragSourceIndex = ref(-1);
const dragOverIndex = ref(-1);

// 监听弹窗显示状态
watch(() => props.open, (newVal) => {
  visible.value = newVal;
  if (newVal) {
    loadCards();
  }
});

watch(visible, (newVal) => {
  emit('update:open', newVal);
});

// 加载卡片数据
const loadCards = () => {
  cards.value = [...props.modelValue];
};

// 添加新卡片
const addCard = () => {
  if (cards.value.length >= 4) {
    return;
  }
  
  currentEditCard.value = {
    id: `card_${Date.now()}`,
    title: 'CPU使用率 TOP5',
    type: 'chart',
    chartType: 'bar',
    dataType: 'cpu',
    unit: '%',
    color: '#ff7875',
    refreshInterval: 60,
    data: [
      { name: 'web-server-01', value: 85.2 },
      { name: 'db-server-02', value: 78.5 },
      { name: 'app-server-03', value: 72.8 },
      { name: 'proxy-server-01', value: 68.3 },
      { name: 'cache-server-01', value: 65.7 }
    ]
  };
  
  configModalVisible.value = true;
};

// 编辑卡片
const editCard = (index) => {
  currentEditCard.value = { ...cards.value[index] };
  currentEditCard.value.index = index;
  configModalVisible.value = true;
};

// 删除卡片
const removeCard = (index) => {
  cards.value.splice(index, 1);
  saveChanges();
};

// 保存卡片配置
const handleSaveCard = (cardConfig) => {
  if (cardConfig.index !== undefined) {
    // 编辑现有卡片
    cards.value[cardConfig.index] = { ...cardConfig };
    delete cards.value[cardConfig.index].index;
  } else {
    // 添加新卡片
    if (cards.value.length < 4) {
      cards.value.push(cardConfig);
    }
  }
  
  saveChanges();
  configModalVisible.value = false;
};

// 田字格卡片拖拽开始
const handleCardDragStart = (event, sourceIndex) => {
  dragSourceIndex.value = sourceIndex;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('text/plain', sourceIndex.toString());
};

// 田字格卡片拖拽结束
const handleCardDragEnd = (event) => {
  dragSourceIndex.value = -1;
  dragOverIndex.value = -1;
};

// 田字格拖拽悬停
const handleGridDragOver = (event, targetIndex) => {
  event.preventDefault();
  if (dragSourceIndex.value !== -1 && dragSourceIndex.value !== targetIndex) {
    dragOverIndex.value = targetIndex;
    event.dataTransfer.dropEffect = 'move';
  }
};

// 田字格拖拽离开
const handleGridDragLeave = (event, targetIndex) => {
  if (dragOverIndex.value === targetIndex) {
    dragOverIndex.value = -1;
  }
};

// 田字格拖拽放置
const handleGridDrop = (event, targetIndex) => {
  event.preventDefault();
  
  const sourceIndex = dragSourceIndex.value;
  if (sourceIndex !== -1 && sourceIndex !== targetIndex) {
    // 交换位置
    const draggedCard = cards.value[sourceIndex];
    const targetCard = cards.value[targetIndex];
    
    if (targetCard) {
      // 交换两个卡片的位置
      cards.value[sourceIndex] = targetCard;
      cards.value[targetIndex] = draggedCard;
    } else {
      // 移动到空位置
      cards.value[targetIndex] = draggedCard;
      cards.value[sourceIndex] = undefined;
      // 清理数组中的undefined
      cards.value = cards.value.filter(card => card !== undefined);
    }
    
    saveChanges();
  }
  
  dragSourceIndex.value = -1;
  dragOverIndex.value = -1;
};

// 检查是否是有效的放置区域
const isValidDropZone = (targetIndex) => {
  return dragSourceIndex.value !== -1 && dragSourceIndex.value !== targetIndex;
};

// 拖拽开始
const handleDragStart = (event, index) => {
  dragIndex.value = index;
  event.dataTransfer.effectAllowed = 'move';
};

// 拖拽放置（列表拖拽到田字格）
const handleDrop = (event, targetIndex) => {
  event.preventDefault();
  
  if (dragIndex.value !== -1 && dragIndex.value !== targetIndex) {
    // 交换位置
    const draggedCard = cards.value[dragIndex.value];
    const targetCard = cards.value[targetIndex];
    
    if (targetCard) {
      // 交换两个卡片的位置
      cards.value[dragIndex.value] = targetCard;
      cards.value[targetIndex] = draggedCard;
    } else {
      // 移动到空位置
      cards.value[targetIndex] = draggedCard;
      cards.value.splice(dragIndex.value, 1);
    }
    
    saveChanges();
  }
  
  dragIndex.value = -1;
};

// 保存更改
const saveChanges = () => {
  emit('update:modelValue', cards.value);
  emit('save', {
    cards: cards.value,
    showAlert: props.showAlertCard,
    showMetrics: props.showMetricsCard
  });
};

// 确认保存
const handleSave = () => {
  saveChanges();
  visible.value = false;
};

// 取消
const handleCancel = () => {
  visible.value = false;
};
</script>

<style scoped>
.card-manager {
  padding: 0;
}

.manager-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.header-info {
  flex: 1;
}

.grid-info {
  color: #666;
  font-size: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 2×2网格预览 */
.grid-preview {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 16px;
  height: 400px;
  margin-bottom: 24px;
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.grid-slot {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.grid-slot:hover {
  border-color: #1890ff;
  background: #f0f8ff;
}

.grid-slot.has-card {
  border-style: solid;
  border-color: #1890ff;
  background: #fff;
}

.grid-slot.drag-over {
  border-color: #52c41a !important;
  background: #f6ffed !important;
  border-style: solid !important;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
}

.grid-slot.valid-drop {
  border-color: #faad14;
  background: #fffbe6;
  border-style: dashed;
}

/* 预览卡片 */
.preview-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
  border-radius: 6px;
  overflow: hidden;
  cursor: grab;
  transition: all 0.3s ease;
}

.preview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.15);
}

.preview-card:active {
  cursor: grabbing;
}

.preview-card.dragging {
  opacity: 0.5;
  transform: rotate(2deg) scale(0.95);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(24, 144, 255, 0.05);
  border-bottom: 1px solid rgba(24, 144, 255, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #262626;
  flex: 1;
}

.drag-handle {
  color: #1890ff;
  cursor: grab;
  font-size: 10px;
  transition: all 0.2s ease;
}

.drag-handle:hover {
  color: #40a9ff;
  transform: scale(1.2);
}

.drag-handle:active {
  cursor: grabbing;
  color: #096dd9;
}

.card-actions {
  display: flex;
  gap: 4px;
}

.card-content {
  flex: 1;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 图表预览 */
.chart-mini {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mini-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
}

.mini-label {
  width: 60px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-value {
  font-weight: 500;
  color: #1890ff;
}

/* 空位置样式 */
.empty-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #bbb;
  font-size: 12px;
  transition: all 0.3s ease;
}

.grid-slot.drag-over .empty-slot {
  color: #52c41a;
}

.add-icon {
  font-size: 24px;
  margin-bottom: 8px;
  color: #d9d9d9;
  transition: all 0.3s ease;
}

.grid-slot.drag-over .add-icon {
  color: #52c41a;
  transform: scale(1.2);
}

/* 卡片列表管理 */
.card-list {
  border-top: 1px solid #f0f0f0;
  padding-top: 20px;
}

.card-list h4 {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #262626;
  font-weight: 600;
}

.list-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.3s ease;
}

.list-item:hover {
  background: #f0f8ff;
  border-color: #1890ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.list-item:active {
  cursor: grabbing;
}

.item-title {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #262626;
}

.item-type {
  font-size: 11px;
  color: #666;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
}

.item-actions {
  display: flex;
  gap: 4px;
}

.empty-list {
  text-align: center;
  padding: 40px 20px;
  color: #bbb;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .grid-preview {
    height: 300px;
    gap: 12px;
    padding: 12px;
  }
  
  .manager-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    align-self: stretch;
    justify-content: flex-end;
  }
  
  .card-header {
    padding: 6px 8px;
  }
  
  .card-title {
    font-size: 11px;
  }
  
  .card-content {
    padding: 6px 8px;
  }
}
</style>