<template>
  <a-drawer
    :open="visible"
    title="选择监控模板"
    width="1200"
    placement="right"
    :onClose="handleClose"
    @update:open="$emit('update:visible', $event)"
  >
    <template #extra>
      <a-space>
        <a-button @click="handleClose">取消</a-button>
        <a-button 
          type="primary" 
          @click="handleCreateMonitoring"
          :loading="monitoringCreating"
          :disabled="selectedTemplateIds.length === 0"
        >
          启用监控 ({{ selectedTemplateIds.length }})
        </a-button>
      </a-space>
    </template>

    <div v-if="selectedIP" class="template-drawer-content">
      <!-- 模板搜索和筛选 -->
      <div class="template-search-section">
        <div class="search-bar">
          <a-input-search
            v-model:value="templateSearchKeyword"
            placeholder="搜索模板名称..."
            @search="handleTemplateSearch"
            @pressEnter="handleTemplateSearch"
            allow-clear
            size="large"
          />
        </div>
        
        <!-- 分类筛选 -->
        <div class="category-filter">
          <a-space wrap>
            <a-tag
              v-for="(stats, category) in categoryStats"
              :key="safeCategoryToString(category)"
              :color="selectedCategory === safeCategoryToString(category) ? 'blue' : 'default'"
              :class="{ 'category-tag-selected': selectedCategory === safeCategoryToString(category) }"
              @click="toggleCategoryFilter(category)"
              class="category-filter-tag"
            >
              <component :is="getCategoryIcon(category)" class="category-filter-icon" />
              {{ safeCategoryToString(category).replace(/^\S+ /, '') }}
              <span class="category-count">({{ Number(stats?.count) || 0 }})</span>
              <span v-if="Number(stats?.selected) > 0" class="category-selected">✓{{ Number(stats.selected) }}</span>
            </a-tag>
            <a-tag 
              v-if="selectedCategory"
              color="red"
              @click="clearCategoryFilter"
              class="clear-filter-tag"
            >
              清除筛选
            </a-tag>
          </a-space>
        </div>
      </div>

      <!-- 模板列表 -->
      <div class="template-list">
        <a-spin :spinning="templateLoading" tip="正在加载模板...">
          <div v-if="Object.keys(groupedTemplates).length === 0" class="empty-templates">
            <a-empty description="暂无可用模板" />
          </div>
          
          <div v-else>
            <!-- 已选模板提示 -->
            <div v-if="selectedTemplateIds.length > 0" class="selected-templates-info">
              <a-alert
                :message="`已选择 ${selectedTemplateIds.length} 个模板`"
                type="info"
                show-icon
                closable
                @close="selectedTemplateIds = []"
              />
            </div>

            <!-- 按分类展示模板 -->
            <div 
              v-for="(templates, category) in filteredTemplates" 
              :key="category" 
              class="template-category"
            >
              <div class="category-header">
                <div class="category-title-wrapper">
                  <component :is="getCategoryIcon(category)" class="category-icon" />
                  <h4 class="category-title">{{ safeCategoryToString(category) }}</h4>
                  <div class="category-stats">
                    <a-badge 
                      :count="Number(categoryStats[safeCategoryToString(category)]?.count) || 0" 
                      :number-style="{ backgroundColor: '#f0f0f0', color: '#666' }"
                    />
                    <a-badge 
                      v-if="Number(categoryStats[safeCategoryToString(category)]?.selected) > 0"
                      :count="Number(categoryStats[safeCategoryToString(category)]?.selected)" 
                      :number-style="{ backgroundColor: '#1890ff', color: '#fff' }"
                      class="selected-badge"
                    />
                  </div>
                </div>
                <a-button
                  v-if="Number(categoryStats[safeCategoryToString(category)]?.count) > 0"
                  type="text"
                  size="small"
                  @click="toggleCategoryExpand(category)"
                  class="expand-button"
                >
                  <UpOutlined v-if="isCategoryExpanded(category)" />
                  <DownOutlined v-else />
                </a-button>
              </div>
              <transition name="collapse">
                <div class="template-grid-wrapper" v-show="isCategoryExpanded(category)">
                  <div class="template-grid">
                    <TemplateCard
                      v-for="template in templates" 
                      :key="template.templateid"
                      :template="template"
                      :selected="selectedTemplateIds.includes(template.templateid)"
                      @select="handleTemplateSelect"
                    />
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </a-spin>
      </div>
    </div>
  </a-drawer>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, h } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { ipAPI } from '@/api';
import TemplateCard from './TemplateCard.vue';
import {
  UpOutlined,
  DownOutlined,
  DatabaseOutlined,
  CloudOutlined,
  SettingOutlined,
  MonitorOutlined,
  SecurityScanOutlined,
  AppstoreOutlined
} from '@ant-design/icons-vue';

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  selectedIP: {
    type: Object,
    default: null
  }
});

// Emits
const emit = defineEmits(['update:visible', 'monitoring-created']);

// 响应式数据
const zabbixTemplates = ref([]);
const selectedTemplateIds = ref([]);
const templateLoading = ref(false);
const templateSearchKeyword = ref('');
const monitoringCreating = ref(false);
const selectedCategory = ref('');
const expandedCategories = ref({});

// 计算属性
const groupedTemplates = computed(() => {
  if (!Array.isArray(zabbixTemplates.value)) {
    return {};
  }
  
  const grouped = {};
  zabbixTemplates.value.forEach(template => {
    const category = template.category || '其他';
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(template);
  });
  
  return grouped;
});

const filteredTemplates = computed(() => {
  let filtered = { ...groupedTemplates.value };
  
  // 分类筛选
  if (selectedCategory.value) {
    const categoryKey = selectedCategory.value;
    filtered = {
      [categoryKey]: filtered[categoryKey] || []
    };
  }
  
  // 搜索筛选
  if (templateSearchKeyword.value) {
    const keyword = templateSearchKeyword.value.toLowerCase();
    Object.keys(filtered).forEach(category => {
      filtered[category] = filtered[category].filter(template => 
        template.name.toLowerCase().includes(keyword)
      );
      if (filtered[category].length === 0) {
        delete filtered[category];
      }
    });
  }
  
  return filtered;
});

const categoryStats = computed(() => {
  const stats = {};
  
  Object.keys(groupedTemplates.value).forEach(category => {
    const templates = groupedTemplates.value[category];
    const selectedCount = templates.filter(t => 
      selectedTemplateIds.value.includes(t.templateid)
    ).length;
    
    stats[category] = {
      count: templates.length,
      selected: selectedCount
    };
  });
  
  return stats;
});

// 方法
const safeCategoryToString = (category) => {
  if (category === null || category === undefined) {
    return '其他';
  }
  return String(category);
};

const getCategoryIcon = (category) => {
  const categoryStr = safeCategoryToString(category).toLowerCase();
  
  if (categoryStr.includes('database') || categoryStr.includes('数据库')) {
    return DatabaseOutlined;
  } else if (categoryStr.includes('network') || categoryStr.includes('网络')) {
    return CloudOutlined;
  } else if (categoryStr.includes('system') || categoryStr.includes('系统')) {
    return SettingOutlined;
  } else if (categoryStr.includes('application') || categoryStr.includes('应用')) {
    return AppstoreOutlined;
  } else if (categoryStr.includes('security') || categoryStr.includes('安全')) {
    return SecurityScanOutlined;
  }
  
  return MonitorOutlined;
};

const toggleCategoryFilter = (category) => {
  const categoryStr = safeCategoryToString(category);
  if (selectedCategory.value === categoryStr) {
    selectedCategory.value = '';
  } else {
    selectedCategory.value = categoryStr;
  }
};

const clearCategoryFilter = () => {
  selectedCategory.value = '';
};

const toggleCategoryExpand = (category) => {
  const categoryStr = safeCategoryToString(category);
  expandedCategories.value[categoryStr] = !expandedCategories.value[categoryStr];
};

const isCategoryExpanded = (category) => {
  const categoryStr = safeCategoryToString(category);
  return expandedCategories.value[categoryStr] !== false;
};

const handleTemplateSelect = (templateId, checked) => {
  if (checked) {
    if (!selectedTemplateIds.value.includes(templateId)) {
      selectedTemplateIds.value.push(templateId);
    }
  } else {
    const index = selectedTemplateIds.value.indexOf(templateId);
    if (index > -1) {
      selectedTemplateIds.value.splice(index, 1);
    }
  }
};

const handleTemplateSearch = async () => {
  if (props.selectedIP) {
    await loadZabbixTemplates(props.selectedIP.id);
  }
};

const loadZabbixTemplates = async (ipId) => {
  templateLoading.value = true;
  try {
    const response = await ipAPI.getZabbixTemplates(ipId, templateSearchKeyword.value);
    
    if (response.data && response.data.code === 200) {
      zabbixTemplates.value = response.data.data.templates || [];
      
      // 初始化展开状态，默认展开所有分类
      nextTick(() => {
        try {
          const categories = Object.keys(groupedTemplates.value || {});
          categories.forEach(category => {
            const categoryStr = String(category);
            expandedCategories.value[categoryStr] = true;
          });
        } catch (error) {
          console.warn('初始化展开状态错误:', error);
        }
      });
      
      console.log('成功加载模板列表:', zabbixTemplates.value.length, '个模板');
    } else {
      // 检查是否是Zabbix连接问题
      if (response.data && response.data.message && response.data.message.includes('Zabbix API连接不可用')) {
        // 显示详细的诊断信息
        const errorMessage = '⚠️ Zabbix服务器连接失败';
        const suggestions = [
          '请检查Zabbix服务器是否正常运行',
          '验证网络连接和防火墙设置',
          '检查Zabbix API配置是否正确'
        ];
        
        Modal.error({
          title: '无法加载监控模板',
          content: h('div', [
            h('p', { style: 'margin-bottom: 16px;' }, errorMessage),
            h('div', { style: 'background: #f5f5f5; padding: 12px; border-radius: 6px;' }, [
              h('p', { style: 'margin: 0 0 8px 0; font-weight: 600;' }, '解决建议：'),
              h('ul', { style: 'margin: 0; padding-left: 20px;' }, 
                suggestions.map(suggestion => 
                  h('li', { style: 'margin-bottom: 4px;' }, suggestion)
                )
              )
            ])
          ]),
          width: 500
        });
      } else {
        message.error(`加载模板列表失败: ${response.data?.message || '未知错误'}`);
      }
      
      zabbixTemplates.value = [];
    }
  } catch (error) {
    console.error('加载模板列表失败:', error);
    
    // 检查是否是网络连接问题
    if (error.message && (error.message.includes('Network Error') || error.message.includes('timeout'))) {
      Modal.error({
        title: '网络连接失败',
        content: '无法连接到后端服务器，请检查网络连接和服务器状态。'
      });
    } else {
      message.error(`加载模板列表失败: ${error.message}`);
    }
    
    zabbixTemplates.value = [];
  } finally {
    templateLoading.value = false;
  }
};

const handleCreateMonitoring = async () => {
  if (!props.selectedIP) {
    message.error('请先选择IP地址');
    return;
  }
  
  if (selectedTemplateIds.value.length === 0) {
    message.error('请选择至少一个监控模板');
    return;
  }
  
  monitoringCreating.value = true;
  
  try {
    const monitoringData = {
      template_ids: selectedTemplateIds.value,
      host_name: props.selectedIP.hostname || props.selectedIP.ip_address || props.selectedIP.ipAddress,
      group_ids: [] // 使用默认主机组
    };
    
    const response = await ipAPI.createMonitoring(props.selectedIP.id, monitoringData);
    
    if (response.data && response.data.code === 200) {
      message.success('监控启用成功！');
      emit('monitoring-created', props.selectedIP);
      handleClose();
    } else {
      message.error(`启用监控失败: ${response.data?.message || '未知错误'}`);
    }
  } catch (error) {
    console.error('启用监控失败:', error);
    message.error(`启用监控失败: ${error.message}`);
  } finally {
    monitoringCreating.value = false;
  }
};

const handleClose = () => {
  emit('update:visible', false);
  // 清理状态
  selectedTemplateIds.value = [];
  templateSearchKeyword.value = '';
  selectedCategory.value = '';
  expandedCategories.value = {};
};

// 监听props变化
watch(() => props.visible, (newVal) => {
  if (newVal && props.selectedIP) {
    loadZabbixTemplates(props.selectedIP.id);
  }
});
</script>

<style scoped>
/* 简洁抽屉内容 */
.template-drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

/* 简洁搜索区域 */
.template-search-section {
  margin-bottom: 24px;
  padding: 20px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.search-bar {
  margin-bottom: 20px;
}

/* 简洁搜索输入框 */
:deep(.ant-input-search) {
  border-radius: 6px;
}

:deep(.ant-input-search .ant-input) {
  border-radius: 6px 0 0 6px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  transition: all 0.2s ease;
  height: 40px;
  font-size: 14px;
}

:deep(.ant-input-search .ant-input:focus) {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
}

:deep(.ant-input-search .ant-input-search-button) {
  border-radius: 0 6px 6px 0;
  background: #2563eb;
  border: 1px solid #2563eb;
  height: 40px;
  width: 40px;
}

:deep(.ant-input-search .ant-input-search-button:hover) {
  background: #1d4ed8;
  border-color: #1d4ed8;
}

/* 简洁分类过滤 */
.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.category-filter-tag {
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 6px;
  padding: 6px 12px;
  font-weight: 500;
  border: 1px solid #d1d5db;
  background: #ffffff;
  user-select: none;
}

.category-filter-tag:hover {
  border-color: #2563eb;
  color: #2563eb;
}

.category-tag-selected {
  background: #2563eb !important;
  color: white !important;
  border-color: #2563eb !important;
}

.category-filter-icon {
  font-size: 12px;
}

.category-count {
  font-size: 11px;
  opacity: 0.8;
}

.category-selected {
  font-size: 10px;
  background: #4ecdc4;
  color: white;
  padding: 1px 4px;
  border-radius: 8px;
  margin-left: 2px;
}

.clear-filter-tag {
  cursor: pointer;
  background: #dc2626 !important;
  color: white !important;
  border-color: #dc2626 !important;
}

.clear-filter-tag:hover {
  background: #b91c1c !important;
  border-color: #b91c1c !important;
}

/* 简洁模板列表 */
.template-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 20px 20px;
}

.template-list::-webkit-scrollbar {
  width: 6px;
}

.template-list::-webkit-scrollbar {
  display: none;
}

.template-list::-webkit-scrollbar-track {
  display: none;
}

.template-list::-webkit-scrollbar-thumb {
  display: none;
}

.template-list::-webkit-scrollbar-thumb:hover {
  display: none;
}

/* 简洁空状态 */
.empty-templates {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 300px;
  background: #ffffff;
  border-radius: 8px;
  border: 2px dashed #d1d5db;
  color: #6b7280;
  font-size: 16px;
  font-weight: 500;
}

/* 简洁选中信息 */
.selected-templates-info {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #eff6ff;
  border-radius: 6px;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  font-weight: 500;
}

/* 简洁模板分类 */
.template-category {
  margin-bottom: 24px;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #ffffff;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.category-header:hover {
  border-color: #cbd5e1;
}

.category-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.category-icon {
  font-size: 16px;
  color: #2563eb;
}

.category-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.category-stats {
  display: flex;
  gap: 12px;
  align-items: center;
}

.selected-badge {
  margin-left: 8px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: 500;
}

.expand-button {
  padding: 6px;
  height: auto;
  min-width: auto;
  border-radius: 6px;
  border: 1px solid #d1d5db;
  background: #ffffff;
  transition: all 0.2s ease;
}

.expand-button:hover {
  border-color: #2563eb;
  color: #2563eb;
}

/* 简洁模板网格 */
.template-grid-wrapper {
  overflow: hidden;
  max-width: 100%;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  justify-content: start;
}

/* 折叠动画 */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
  max-height: 1000px;
  opacity: 1;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

/* 简洁模板卡片 */
:deep(.template-card) {
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  overflow: hidden;
}

:deep(.template-card:hover) {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.template-card.selected) {
  border-color: #2563eb;
  background: #eff6ff;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

:deep(.template-card .ant-card-body) {
  padding: 20px;
}

:deep(.template-card .ant-card-meta-title) {
  font-weight: 700;
  color: #2d3748;
  font-size: 14px;
}

:deep(.template-card .ant-card-meta-description) {
  color: #718096;
  font-size: 12px;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .template-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
  }
}

@media (max-width: 1200px) {
  .template-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .template-search-section {
    padding: 20px;
  }
  
  .template-list {
    padding: 0 20px 20px;
  }
}

@media (max-width: 768px) {
  .template-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .template-search-section {
    padding: 16px;
    margin-bottom: 24px;
  }
  
  .template-list {
    padding: 0 16px 16px;
  }
  
  .category-header {
    padding: 16px 20px;
  }
  
  .category-filter {
    gap: 8px;
  }
  
  .category-filter-tag {
    padding: 6px 12px;
    font-size: 12px;
  }
}

/* 简洁抽屉样式 */
:deep(.ant-drawer-content) {
  background: #f8fafc;
}

:deep(.ant-drawer-header) {
  background: #ffffff;
  border-bottom: 1px solid #e2e8f0;
  padding: 20px 24px;
}

:deep(.ant-drawer-title) {
  font-weight: 600;
  font-size: 18px;
  color: #1f2937;
}

:deep(.ant-drawer-body) {
  padding: 24px;
}

:deep(.ant-drawer-extra) {
  gap: 8px;
}
</style>