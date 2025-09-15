<template>
  <div 
    class="template-card"
    :class="{ selected: isSelected }"
    @click="$emit('select', templateid)"
  >
    <div class="card-badge" v-if="isSelected">
      <CheckCircleOutlined />
    </div>
    
    <div class="card-header">
      <div class="card-icon-wrapper" :class="category">
        <component :is="getCategoryIcon(category)" class="card-icon" />
      </div>
      <div class="card-title-section">
        <h3 class="card-title" :title="name">{{ truncateName(name) }}</h3>
        <span class="card-category">{{ getCategoryLabel(category) }}</span>
      </div>
    </div>
    
    <div class="card-content">
      <p class="card-description" :title="description">{{ truncateDescription(description) }}</p>
      
      <div class="card-stats">
        <div class="stat-item">
          <div class="stat-icon">
            <EyeOutlined />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ items_count }}</span>
            <span class="stat-label">监控项</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">
            <AlertOutlined />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ triggers_count }}</span>
            <span class="stat-label">触发器</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon">
            <CodeOutlined />
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ macros_count || 0 }}</span>
            <span class="stat-label">宏</span>
          </div>
        </div>
      </div>
      
      <div class="card-groups" v-if="groups && groups.length > 0">
        <a-tag 
          v-for="(group, index) in groups.slice(0, 2)" 
          :key="index"
          :color="getGroupColor(index)"
          size="small"
          :title="group.name"
        >
          {{ truncateGroupName(group.name) }}
        </a-tag>
        <span 
          v-if="groups.length > 2" 
          class="more-groups"
          :title="groups.slice(2).map(g => g.name).join(', ')"
        >
          +{{ groups.length - 2 }}
        </span>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="card-actions">
        <a-button 
          type="primary" 
          size="small" 
          :class="{ 'selected-btn': isSelected }"
          @click.stop="$emit('select', templateid)"
        >
          {{ isSelected ? '已选择' : '选择' }}
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { 
  CheckCircleOutlined, 
  EyeOutlined, 
  AlertOutlined, 
  CodeOutlined,
  DesktopOutlined,
  CloudOutlined,
  DatabaseOutlined,
  ApartmentOutlined,
  GlobalOutlined,
  AppstoreOutlined
} from '@ant-design/icons-vue';

const props = defineProps({
  templateid: String,
  name: String,
  description: String,
  category: String,
  icon: String,
  items_count: Number,
  triggers_count: Number,
  macros_count: Number,
  groups: Array,
  selected: Boolean
});

const emit = defineEmits(['select']);

const isSelected = computed(() => props.selected);

const getCategoryIcon = (category) => {
  const iconMap = {
    'server': DesktopOutlined,
    'network': ApartmentOutlined,
    'cloud': CloudOutlined,
    'database': DatabaseOutlined,
    'application': AppstoreOutlined,
    'default': GlobalOutlined
  };
  return iconMap[category] || iconMap.default;
};

const getCategoryLabel = (category) => {
  const labelMap = {
    'server': '服务器',
    'network': '网络设备',
    'cloud': '云服务',
    'database': '数据库',
    'application': '应用服务',
    'default': '通用模板'
  };
  return labelMap[category] || category || '通用模板';
};

const truncateName = (name) => {
  return name.length > 20 ? name.substring(0, 20) + '...' : name;
};

const truncateDescription = (desc) => {
  if (!desc) return '暂无描述';
  return desc.length > 80 ? desc.substring(0, 80) + '...' : desc;
};

const truncateGroupName = (name) => {
  return name.length > 8 ? name.substring(0, 8) + '...' : name;
};

const getGroupColor = (index) => {
  const colors = ['blue', 'green', 'orange', 'purple', 'cyan'];
  return colors[index % colors.length];
};
</script>

<style scoped>
.template-card {
  position: relative;
  background: linear-gradient(135deg, #ffffff 0%, #fafbff 100%);
  border: 1px solid rgba(24, 144, 255, 0.12);
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  height: 220px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 12px rgba(24, 144, 255, 0.06);
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.12);
  border-color: rgba(24, 144, 255, 0.3);
}

.template-card.selected {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  border-color: #40a9ff;
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.2);
}

.card-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  background: #52c41a;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(82, 196, 26, 0.4);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon-wrapper.server {
  background: linear-gradient(135deg, #ffd6e7 0%, #ffadd2 100%);
}

.card-icon-wrapper.network {
  background: linear-gradient(135deg, #d6e4ff 0%, #85a5ff 100%);
}

.card-icon-wrapper.cloud {
  background: linear-gradient(135deg, #b5f5ec 0%, #36cfc9 100%);
}

.card-icon-wrapper.database {
  background: linear-gradient(135deg, #ffd591 0%, #ffc53d 100%);
}

.card-icon-wrapper.application {
  background: linear-gradient(135deg, #d3f261 0%, #bae637 100%);
}

.card-icon-wrapper.default {
  background: linear-gradient(135deg, #e9d8fd 0%, #b37feb 100%);
}

.card-icon {
  font-size: 24px;
  color: white;
}

.card-title-section {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-category {
  font-size: 12px;
  color: #8c8c8c;
  margin-top: 2px;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-description {
  color: #595959;
  font-size: 13px;
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: auto;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px;
  background: rgba(24, 144, 255, 0.06);
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.stat-item:hover {
  background: rgba(24, 144, 255, 0.1);
}

.stat-icon {
  width: 20px;
  height: 20px;
  background: rgba(24, 144, 255, 0.1);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon .anticon {
  font-size: 12px;
  color: #1890ff;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #262626;
  line-height: 1;
}

.stat-label {
  font-size: 10px;
  color: #8c8c8c;
  line-height: 1;
}

.card-groups {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: auto;
}

.more-groups {
  font-size: 11px;
  color: #8c8c8c;
  background: rgba(140, 140, 140, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  cursor: help;
}

.card-footer {
  margin-top: auto;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
}

.selected-btn {
  background: #52c41a !important;
  border-color: #52c41a !important;
}

.selected-btn:hover {
  background: #73d13d !important;
  border-color: #73d13d !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .template-card {
    height: 200px;
    padding: 16px;
  }
  
  .card-icon-wrapper {
    width: 40px;
    height: 40px;
  }
  
  .card-icon {
    font-size: 20px;
  }
  
  .card-title {
    font-size: 14px;
  }
  
  .card-stats {
    gap: 6px;
  }
  
  .stat-item {
    padding: 4px;
  }
  
  .stat-icon {
    width: 18px;
    height: 18px;
  }
  
  .stat-value {
    font-size: 12px;
  }
  
  .stat-label {
    font-size: 9px;
  }
}

@media (max-width: 480px) {
  .template-card {
    height: 180px;
    padding: 12px;
  }
  
  .card-header {
    gap: 8px;
    margin-bottom: 12px;
  }
  
  .card-icon-wrapper {
    width: 36px;
    height: 36px;
  }
  
  .card-icon {
    font-size: 18px;
  }
  
  .card-description {
    font-size: 12px;
  }
  
  .card-stats {
    grid-template-columns: repeat(3, 1fr);
    gap: 4px;
  }
  
  .stat-item {
    flex-direction: column;
    gap: 2px;
    text-align: center;
    padding: 4px 2px;
  }
  
  .stat-info {
    gap: 0;
  }
}
</style>
