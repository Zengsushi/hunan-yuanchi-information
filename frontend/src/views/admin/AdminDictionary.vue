<template>
  <div class="admin-dictionary admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <BookOutlined />
          字典管理
        </h1>
        <p class="page-description">管理监控系统的字典数据</p>
      </div>
      <div class="header-actions">
        <a-space>
          <a-button 
            type="default" 
            @click="initDictionaryData"
            :loading="initLoading"
          >
            <ReloadOutlined />
            初始化数据
          </a-button>
          <a-button type="primary" @click="showAddModal">
            <PlusOutlined />
            新建字典
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- 字典分类导航 -->
    <div class="dictionary-layout admin-layout">
      <!-- 左侧菜单 -->
      <div class="dictionary-menu admin-menu">
        <div class="menu-title">
          字典分类
          <a-space class="menu-actions">
            <a-button type="text" size="small" @click="showAddCategoryModal">
              <PlusOutlined />
            </a-button>
            <a-button type="text" size="small" @click="showManageCategoriesModal">
              <SettingOutlined />
            </a-button>
          </a-space>
        </div>
        <div class="menu-list">
          <div 
            v-for="category in categoryList" 
            :key="category.key"
            :class="['menu-item', { 'active': activeCategory === category.key }]"
            @click="handleCategoryChange(category.key)"
          >
            <component :is="category.icon" class="menu-icon" />
            <span class="menu-text">{{ category.name }}</span>
            <span class="menu-count">({{ category.count || 0 }})</span>
          </div>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="dictionary-content admin-content">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
            <a-space>
              <a-input-search
                v-model:value="searchText"
                placeholder="搜索字典项..."
                style="width: 200px"
                @search="handleSearch"
              />
              <a-button @click="refreshData">
                <ReloadOutlined />
              </a-button>
            </a-space>
          </template>

          <a-table
            :columns="tableColumns"
            :data-source="filteredDictionaries"
            :pagination="pagination"
            :loading="loading"
            row-key="id"
            size="middle"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag :color="record.status === 'active' ? 'green' : 'red'">
                  {{ record.status === 'active' ? '启用' : '禁用' }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'priority'">
                <a-tag :color="getPriorityColor(record.priority)">
                  {{ record.priority }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-space>
                  <a-button type="link" size="small" @click="editDictionary(record)">
                    编辑
                  </a-button>
                  <a-button 
                    type="link" 
                    size="small" 
                    @click="toggleStatus(record)"
                  >
                    {{ record.status === 'active' ? '禁用' : '启用' }}
                  </a-button>
                  <a-popconfirm
                    title="确定要删除这个字典项吗？"
                    @confirm="deleteDictionary(record)"
                  >
                    <a-button type="link" size="small" danger>
                      删除
                    </a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>
    </div>

    <!-- 添加/编辑字典弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEditing ? '编辑字典项' : '新建字典项'"
      width="600px"
      @ok="handleSubmit"
      @cancel="handleCancel"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="字典分类" name="category">
              <a-select v-model:value="formData.category" placeholder="选择字典分类">
                <a-select-option 
                  v-for="category in categoryList" 
                  :key="category.key" 
                  :value="category.key"
                >
                  {{ category.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="字典键名" name="key">
              <a-input v-model:value="formData.key" placeholder="输入字典键名" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="显示名称" name="label">
              <a-input v-model:value="formData.label" placeholder="输入显示名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="排序权重" name="priority">
              <a-input-number 
                v-model:value="formData.priority" 
                :min="0" 
                :max="999"
                placeholder="数值越大优先级越高"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="描述信息" name="description">
          <a-textarea 
            v-model:value="formData.description" 
            placeholder="输入字典项的详细描述"
            :rows="3"
          />
        </a-form-item>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="状态" name="status">
              <a-select v-model:value="formData.status">
                <a-select-option value="active">启用</a-select-option>
                <a-select-option value="inactive">禁用</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="扩展配置" name="config">
              <a-input v-model:value="formData.config" placeholder="JSON格式配置（可选）" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <!-- 创建分类弹窗 -->
    <a-modal
      v-model:open="categoryModalVisible"
      title="创建字典分类"
      width="500px"
      @ok="handleCreateCategory"
      @cancel="handleCancelCategory"
    >
      <a-form
        ref="categoryFormRef"
        :model="categoryFormData"
        :rules="categoryFormRules"
        layout="vertical"
      >
        <a-form-item label="分类键名" name="key">
          <a-input v-model:value="categoryFormData.key" placeholder="输入分类键名（英文）" />
        </a-form-item>
        <a-form-item label="分类名称" name="label">
          <a-input v-model:value="categoryFormData.label" placeholder="输入分类显示名称" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea 
            v-model:value="categoryFormData.description" 
            placeholder="输入分类描述"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 管理分类弹窗 -->
    <a-modal
      v-model:open="manageCategoriesModalVisible"
      title="管理字典分类"
      width="700px"
      :footer="null"
    >
      <a-table
        :columns="categoryTableColumns"
        :data-source="categoryList"
        :pagination="false"
        row-key="key"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actions'">
            <a-space>
              <a-button type="link" size="small" @click="editCategory(record)">
                <EditOutlined />
                编辑
              </a-button>
              <a-popconfirm
                title="确定要删除这个分类吗？删除后该分类下的所有字典项也会被删除！"
                @confirm="deleteCategory(record)"
              >
                <a-button type="link" size="small" danger>
                  <DeleteOutlined />
                  删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-modal>

    <!-- 编辑分类弹窗 -->
    <a-modal
      v-model:open="editCategoryModalVisible"
      title="编辑字典分类"
      width="500px"
      @ok="handleUpdateCategory"
      @cancel="handleCancelEditCategory"
    >
      <a-form
        ref="editCategoryFormRef"
        :model="editCategoryFormData"
        :rules="categoryFormRules"
        layout="vertical"
      >
        <a-form-item label="分类键名" name="key">
          <a-input v-model:value="editCategoryFormData.key" disabled />
        </a-form-item>
        <a-form-item label="分类名称" name="label">
          <a-input v-model:value="editCategoryFormData.label" placeholder="输入分类显示名称" />
        </a-form-item>
        <a-form-item label="描述" name="description">
          <a-textarea 
            v-model:value="editCategoryFormData.description" 
            placeholder="输入分类描述"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { message } from 'ant-design-vue';
import { dictionaryAPI } from '@/api/index';
import {
  BookOutlined,
  PlusOutlined,
  ReloadOutlined,
  AppstoreOutlined,
  TagOutlined,
  DesktopOutlined,
  BellOutlined,
  GlobalOutlined,
  BarChartOutlined,
  SettingOutlined,
  DeleteOutlined,
  EditOutlined
} from '@ant-design/icons-vue';

// 响应式数据
const activeCategory = ref('user_category'); // 使用后端实际存在的分类
const searchText = ref('');
const loading = ref(false);
const initLoading = ref(false); // 初始化数据加载状态
const modalVisible = ref(false);
const isEditing = ref(false);
const formRef = ref(null);

// 分类管理相关状态
const categoryModalVisible = ref(false);
const manageCategoriesModalVisible = ref(false);
const editCategoryModalVisible = ref(false);
const categoryFormRef = ref(null);
const editCategoryFormRef = ref(null);

// 分类列表（从后端动态获取）
const categoryList = ref([]);
const allDictionaries = ref([]);

// 获取字典分类
const fetchCategories = async () => {
  try {
    const response = await dictionaryAPI.getDictionaryCategories();
    if (response.data && response.data.code === 200) {
      const categories = response.data.data || [];
      if (categories.length > 0) {
        categoryList.value = categories.map(cat => ({
          key: cat.key,
          name: cat.label,
          icon: getIconByCategory(cat.key),
          count: cat.count || 0
        }));
        
        // 设置默认激活分类
        // 如果当前激活分类不在有效分类中，则使用第一个分类
        const validKeys = categories.map(cat => cat.key);
        if (!validKeys.includes(activeCategory.value)) {
          activeCategory.value = categories[0].key;
        }
      } else {
        console.warn('后端返回的分类列表为空，使用默认分类');
      }
    } else {
      console.warn('获取字典分类响应异常:', response.data);
      message.warning('获取字典分类失败，使用默认分类');
    }
  } catch (error) {
    console.error('获取字典分类失败:', error);
    if (error.response && error.response.status === 404) {
      message.error('字典分类接口不存在，请检查后端配置');
    } else {
      message.error('获取字典分类失败，请检查网络连接');
    }
    // 使用默认分类作为备用
  }
};

// 根据分类键名获取图标
const getIconByCategory = (categoryKey) => {
  const iconMap = {
    'user_category': AppstoreOutlined,
    'system_config': TagOutlined,
    'asset_type': DesktopOutlined,
    'department': GlobalOutlined,
    'status': BellOutlined,
    'priority': BarChartOutlined,
    'environment': GlobalOutlined,
    // 兼容旧的分类名
    'asset_category': DesktopOutlined,
    'asset_status': BellOutlined,
    'device_type': DesktopOutlined,
    'alert_level': BellOutlined,
    'network_type': GlobalOutlined,
    'monitor_metric': BarChartOutlined
  };
  return iconMap[categoryKey] || AppstoreOutlined;
};

// 设置默认分类（备用方案）

// 获取字典数据
const fetchDictionaries = async () => {
  if (!activeCategory.value) {
    console.warn('没有选择分类，跳过获取字典数据');
    return;
  }
  
  loading.value = true;
  try {
    const response = await dictionaryAPI.getDictionaryByCategory(activeCategory.value, {
      simple: 'false' // 获取完整数据，不再过滤状态，让用户看到所有数据
    });
    
    if (response.data && response.data.code === 200) {
      allDictionaries.value = response.data.data || [];
      pagination.value.total = allDictionaries.value.length;
      
      if (allDictionaries.value.length === 0) {
        console.info(`分类 ${getCurrentCategoryName()} 暂无数据`);
      }
    } else if (response.data && response.data.code === 400) {
      // 处理无效分类错误
      console.error('无效的字典分类:', response.data);
      message.error(`分类 "${activeCategory.value}" 无效: ${response.data.message}`);
      
      // 如果是无效分类，回退到第一个有效分类
      if (categoryList.value.length > 0) {
        activeCategory.value = categoryList.value[0].key;
        return; // 会触发watch重新获取数据
      }
      
      allDictionaries.value = [];
      pagination.value.total = 0;
    } else {
      console.warn('获取字典数据响应异常:', response.data);
      message.warning(`获取${getCurrentCategoryName()}数据失败`);
      allDictionaries.value = [];
      pagination.value.total = 0;
    }
  } catch (error) {
    console.error('获取字典数据失败:', error);
    if (error.response && error.response.status === 404) {
      message.error('字典数据接口不存在，请检查后端配置');
    } else {
      message.error(`获取${getCurrentCategoryName()}数据失败，请检查网络连接`);
    }
    allDictionaries.value = [];
    pagination.value.total = 0;
  } finally {
    loading.value = false;
  }
};

// 表格配置
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`
});

// 表格列配置
const tableColumns = [
  {
    title: '键名',
    dataIndex: 'key',
    key: 'key',
    width: 150,
    fixed: 'left'
  },
  {
    title: '显示名称',
    dataIndex: 'label',
    key: 'label',
    width: 150
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    ellipsis: true
  },
  {
    title: '优先级',
    dataIndex: 'priority',
    key: 'priority',
    width: 100,
    sorter: (a, b) => a.priority - b.priority
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right'
  }
];

// 表单数据和验证规则
const formData = ref({
  category: '',
  key: '',
  label: '',
  description: '',
  priority: 0,
  status: 'active',
  config: ''
});

const formRules = {
  category: [{ required: true, message: '请选择字典分类' }],
  key: [
    { required: true, message: '请输入字典键名' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '键名只能包含字母、数字和下划线' }
  ],
  label: [{ required: true, message: '请输入显示名称' }],
  priority: [{ required: true, message: '请输入排序权重' }],
  status: [{ required: true, message: '请选择状态' }]
};

// 分类表单数据和验证规则
const categoryFormData = ref({
  key: '',
  label: '',
  description: ''
});

const editCategoryFormData = ref({
  key: '',
  label: '',
  description: ''
});

const categoryFormRules = {
  key: [
    { required: true, message: '请输入分类键名' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '键名只能包含字母、数字和下划线' }
  ],
  label: [{ required: true, message: '请输入分类名称' }]
};

// 分类管理表格列配置
const categoryTableColumns = [
  {
    title: '键名',
    dataIndex: 'key',
    key: 'key',
    width: 150
  },
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
    width: 150
  },
  {
    title: '字典项数量',
    dataIndex: 'count',
    key: 'count',
    width: 120
  },
  {
    title: '操作',
     key: 'actions',
     width: 150
   }
 ];

// 计算属性
const currentDictionaries = computed(() => {
  return allDictionaries.value;
});

const filteredDictionaries = computed(() => {
  if (!searchText.value) {
    return currentDictionaries.value;
  }
  return currentDictionaries.value.filter(item => 
    item.key.toLowerCase().includes(searchText.value.toLowerCase()) ||
    item.label.toLowerCase().includes(searchText.value.toLowerCase()) ||
    (item.description && item.description.toLowerCase().includes(searchText.value.toLowerCase()))
  );
});

// 初始化字典数据
const initDictionaryData = async () => {
  initLoading.value = true;
  try {
    const response = await dictionaryAPI.initDictionaryData();
    console.log('初始化字典数据响应:', response.data);
    
    if (response.data && response.data.code === 200) {
      // 新的批量创建接口响应格式
      const result = response.data.data || {};
      const createdItems = result.created || [];
      const updatedItems = result.updated || [];
      const errors = result.errors || [];
      
      const createdCount = createdItems.length;
      const updatedCount = updatedItems.length;
      const errorCount = errors.length;
      const totalSuccess = createdCount + updatedCount;
      
      if (totalSuccess > 0) {
        // 有成功的操作
        let successMessage = '初始化完成！';
        const details = [];
        if (createdCount > 0) details.push(`创建了 ${createdCount} 个`);
        if (updatedCount > 0) details.push(`更新了 ${updatedCount} 个`);
        if (errorCount > 0) details.push(`${errorCount} 个失败`);
        successMessage += details.join('，') + '字典项';
        
        message.success(successMessage);
        
        // 刷新数据
        await Promise.all([
          fetchCategories(),
          fetchDictionaries()
        ]);
        
        console.log('初始化结果:', { createdCount, updatedCount, errorCount });
      } else {
        // 全部失败
        message.error(`初始化失败，所有 ${errorCount} 个字典项都处理失败`);
        console.error('初始化全部失败:', errors);
      }
    } else {
      const errorMessage = response.data?.message || '初始化失败';
      message.error(errorMessage);
      console.error('初始化失败响应:', response.data);
    }
  } catch (error) {
    console.error('初始化字典数据失败:', error);
    if (error.response && error.response.status === 401) {
      message.error('需要登录认证，请重新登录');
    } else if (error.response && error.response.status === 403) {
      message.error('权限不足，需要管理员权限');
    } else if (error.response && error.response.data) {
      const errorData = error.response.data;
      if (errorData.message) {
        message.error(`初始化失败: ${errorData.message}`);
      } else {
        message.error('初始化失败，请检查网络连接');
      }
    } else {
      message.error('初始化失败，请检查网络连接');
    }
  } finally {
    initLoading.value = false;
  }
};

// 方法
const getCurrentCategoryName = () => {
  const category = categoryList.value.find(cat => cat.key === activeCategory.value);
  return category ? category.name : '未知分类';
};

const getPriorityColor = (priority) => {
  if (priority >= 90) return 'red';
  if (priority >= 70) return 'orange';
  if (priority >= 50) return 'blue';
  return 'default';
};

const handleCategoryChange = (key) => {
  activeCategory.value = key;
  searchText.value = '';
  pagination.value.current = 1;
  fetchDictionaries(); // 获取新分类的数据
};

const handleSearch = () => {
  pagination.value.current = 1;
};

const refreshData = async () => {
  await Promise.all([
    fetchCategories(),
    fetchDictionaries()
  ]);
  message.success('数据刷新成功');
};

const showAddModal = () => {
  isEditing.value = false;
  modalVisible.value = true;
  formData.value = {
    category: activeCategory.value,
    key: '',
    label: '',
    description: '',
    priority: 0,
    status: 'active',
    config: ''
  };
};

const editDictionary = (record) => {
  isEditing.value = true;
  modalVisible.value = true;
  formData.value = { ...record };
};

const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    
    // 验证config格式（如果有值）
    if (formData.value.config && formData.value.config.trim()) {
      try {
        JSON.parse(formData.value.config);
      } catch (e) {
        message.error('配置信息必须是有效的JSON格式');
        return;
      }
    }
    
    loading.value = true;
    
    // 准备提交数据，清理空值
    const submitData = { ...formData.value };
    if (!submitData.config || !submitData.config.trim()) {
      delete submitData.config;
    }
    
    if (isEditing.value) {
      // 更新字典项
      const response = await dictionaryAPI.updateDictionary(submitData.id, submitData);
      if (response.data && response.data.code === 200) {
        message.success('字典项更新成功');
        await fetchDictionaries(); // 刷新数据
        modalVisible.value = false;
      } else {
        const errorMsg = response.data?.message || response.data?.error || '更新失败';
        message.error(errorMsg);
      }
    } else {
      // 创建新字典项
      const response = await dictionaryAPI.createDictionary(submitData);
      if (response.data && response.data.code === 200) {
        message.success('字典项创建成功');
        await fetchDictionaries(); // 刷新数据
        modalVisible.value = false;
      } else {
        const errorMsg = response.data?.message || response.data?.error || '创建失败';
        message.error(errorMsg);
      }
    }
  } catch (error) {
    console.error('表单提交失败:', error);
    if (error.response && error.response.data) {
      const errorData = error.response.data;
      if (errorData.error && typeof errorData.error === 'object') {
        // 处理表单验证错误
        const firstError = Object.values(errorData.error)[0];
        message.error(Array.isArray(firstError) ? firstError[0] : firstError);
      } else {
        message.error(errorData.message || '操作失败');
      }
    } else {
      message.error('操作失败，请检查网络连接后重试');
    }
  } finally {
    loading.value = false;
  }
};

const handleCancel = () => {
  modalVisible.value = false;
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

const toggleStatus = async (record) => {
  const newStatus = record.status === 'active' ? 'inactive' : 'active';
  
  try {
    loading.value = true;
    const response = await dictionaryAPI.updateDictionary(record.id, {
      ...record,
      status: newStatus
    });
    
    if (response.data && response.data.code === 200) {
      // 更新本地数据
      const index = allDictionaries.value.findIndex(item => item.id === record.id);
      if (index !== -1) {
        allDictionaries.value[index].status = newStatus;
      }
      message.success(`字典项已${newStatus === 'active' ? '启用' : '禁用'}`);
    } else {
      message.error(response.data?.message || response.data?.error || '状态更新失败');
    }
  } catch (error) {
    console.error('状态更新失败:', error);
    message.error('状态更新失败，请检查网络连接');
  } finally {
    loading.value = false;
  }
};

const deleteDictionary = async (record) => {
  try {
    loading.value = true;
    const response = await dictionaryAPI.deleteDictionary(record.id);
    
    if (response.data && response.data.code === 200) {
      message.success('字典项删除成功');
      // 更新本地数据而不是重新获取
      allDictionaries.value = allDictionaries.value.filter(item => item.id !== record.id);
      pagination.value.total = allDictionaries.value.length;
    } else {
      message.error(response.data?.message || response.data?.error || '删除失败');
    }
  } catch (error) {
    console.error('删除字典项失败:', error);
    if (error.response && error.response.data) {
      message.error(error.response.data.message || '删除失败');
    } else {
      message.error('删除失败，请检查网络连接');
    }
  } finally {
    loading.value = false;
  }
};

// 分类管理方法
const showAddCategoryModal = () => {
  categoryModalVisible.value = true;
  categoryFormData.value = {
    key: '',
    label: '',
    description: ''
  };
};

const showManageCategoriesModal = () => {
  manageCategoriesModalVisible.value = true;
};

const handleCreateCategory = async () => {
  try {
    await categoryFormRef.value.validate();
    loading.value = true;
    
    const response = await dictionaryAPI.createDictionaryCategory(categoryFormData.value);
    
    if (response.data && response.data.code === 200) {
      message.success('分类创建成功');
      categoryModalVisible.value = false;
      await fetchCategories(); // 刷新分类列表
    } else {
      const errorMsg = response.data?.message || response.data?.error || '创建失败';
      message.error(errorMsg);
    }
  } catch (error) {
    console.error('创建分类失败:', error);
    if (error.response && error.response.data) {
      const errorData = error.response.data;
      if (errorData.error && typeof errorData.error === 'object') {
        const firstError = Object.values(errorData.error)[0];
        message.error(Array.isArray(firstError) ? firstError[0] : firstError);
      } else {
        message.error(errorData.message || '创建失败');
      }
    } else {
      message.error('创建失败，请检查网络连接');
    }
  } finally {
    loading.value = false;
  }
};

const handleCancelCategory = () => {
  categoryModalVisible.value = false;
  if (categoryFormRef.value) {
    categoryFormRef.value.resetFields();
  }
};

const editCategory = (record) => {
  editCategoryModalVisible.value = true;
  editCategoryFormData.value = {
    key: record.key,
    label: record.name,
    description: record.description || ''
  };
};

const handleUpdateCategory = async () => {
  try {
    await editCategoryFormRef.value.validate();
    loading.value = true;
    
    const response = await dictionaryAPI.updateDictionaryCategory(
      editCategoryFormData.value.key,
      editCategoryFormData.value
    );
    
    if (response.data && response.data.code === 200) {
      message.success('分类更新成功');
      editCategoryModalVisible.value = false;
      await fetchCategories(); // 刷新分类列表
    } else {
      const errorMsg = response.data?.message || response.data?.error || '更新失败';
      message.error(errorMsg);
    }
  } catch (error) {
    console.error('更新分类失败:', error);
    if (error.response && error.response.data) {
      const errorData = error.response.data;
      message.error(errorData.message || '更新失败');
    } else {
      message.error('更新失败，请检查网络连接');
    }
  } finally {
    loading.value = false;
  }
};

const handleCancelEditCategory = () => {
  editCategoryModalVisible.value = false;
  if (editCategoryFormRef.value) {
    editCategoryFormRef.value.resetFields();
  }
};

const deleteCategory = async (record) => {
  try {
    loading.value = true;
    const response = await dictionaryAPI.deleteDictionaryCategory(record.key);
    
    if (response.data && response.data.code === 200) {
      message.success('分类删除成功');
      await fetchCategories(); // 刷新分类列表
      
      // 如果删除的是当前激活的分类，切换到第一个分类
      if (activeCategory.value === record.key && categoryList.value.length > 0) {
        activeCategory.value = categoryList.value[0].key;
      }
    } else {
      const errorMsg = response.data?.message || response.data?.error || '删除失败';
      message.error(errorMsg);
    }
  } catch (error) {
    console.error('删除分类失败:', error);
    if (error.response && error.response.data) {
      const errorData = error.response.data;
      message.error(errorData.message || '删除失败');
    } else {
      message.error('删除失败，请检查网络连接');
    }
  } finally {
    loading.value = false;
  }
};

// 监听器
watch(() => filteredDictionaries.value, (newVal) => {
  pagination.value.total = newVal.length;
}, { immediate: true });

watch(() => activeCategory.value, (newCategory, oldCategory) => {
  console.log(`分类切换: ${oldCategory} -> ${newCategory}`);
  if (newCategory) {
    fetchDictionaries();
  }
}, { immediate: false });

// 生命周期
onMounted(async () => {
  console.log('AdminDictionary 组件已挂载，开始初始化');
  try {
    await fetchCategories();
    if (activeCategory.value) {
      await fetchDictionaries();
    } else {
      console.warn('没有可用的分类，无法获取字典数据');
    }
  } catch (error) {
    console.error('组件初始化失败:', error);
    message.error('页面初始化失败，请刷新重试');
  }
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 字典管理页面特有的样式 */
/* 所有通用样式已在 admin-common.css 中定义 */

.menu-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.menu-actions {
  opacity: 0.7;
  transition: opacity 0.3s;
}

.menu-actions:hover {
  opacity: 1;
}

.menu-count {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}
</style>