<template>
  <div class="admin-roles admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <SafetyOutlined />
          角色权限
        </h1>
        <p class="page-description">管理系统角色和权限分配</p>
      </div>
      <div class="header-actions">
        <a-space>
          <a-button @click="exportRoles">
            <ExportOutlined />
            导出角色
          </a-button>
          <a-button type="primary" @click="showAddModal">
            <PlusOutlined />
            新建角色
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- 角色权限布局 -->
    <div class="roles-layout admin-layout">
      <!-- 左侧菜单 -->
      <div class="roles-menu admin-menu">
        <div class="menu-title">角色分类</div>
        <div class="menu-list">
          <div 
            v-for="category in categoryList" 
            :key="category.key"
            :class="['menu-item', { 'active': activeCategory === category.key }]"
            @click="handleCategoryChange(category.key)"
          >
            <component :is="category.icon" class="menu-icon" />
            <span class="menu-text">{{ category.name }}</span>
            <a-badge 
              v-if="category.count" 
              :count="category.count" 
              class="menu-badge"
            />
          </div>
        </div>
        
        <!-- 统计信息 -->
        <div class="menu-stats">
          <div class="stats-title">权限统计</div>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">总角色数</span>
              <span class="stat-value">{{ roleStats.total }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">启用角色</span>
              <span class="stat-value">{{ roleStats.active }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">权限节点</span>
              <span class="stat-value">{{ roleStats.permissions }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="roles-content admin-content">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
            <a-space>
              <a-input-search
                v-model:value="searchText"
                placeholder="搜索角色..."
                style="width: 200px"
                @search="handleSearch"
                @change="handleSearch"
              />
              <a-select
                v-model:value="statusFilter"
                placeholder="状态筛选"
                style="width: 120px"
                @change="handleStatusFilter"
              >
                <a-select-option value="">全部状态</a-select-option>
                <a-select-option value="true">启用</a-select-option>
                <a-select-option value="false">禁用</a-select-option>
              </a-select>
              <a-button @click="refreshData">
                <ReloadOutlined />
              </a-button>
            </a-space>
          </template>

          <a-table
            :columns="tableColumns"
            :data-source="filteredRoles"
            :pagination="pagination"
            :loading="loading"
            :row-selection="rowSelection"
            row-key="id"
            size="middle"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'level'">
                <a-tag :color="getLevelColor(record.level)">
                  {{ getLevelText(record.level) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'status'">
                <a-tag :color="record.status ? 'green' : 'red'">
                  {{ record.status ? '启用' : '禁用' }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'permissions'">
                <span>{{ record.permissions.length }}</span>
              </template>
              <template v-else-if="column.key === 'users'">
                <span>{{ record.userCount }}</span>
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-space>
                  <a-button type="link" size="small" @click="editRole(record)">
                    编辑
                  </a-button>
                  <a-button type="link" size="small" @click="configPermissions(record)">
                    权限配置
                  </a-button>
                  <a-button 
                    type="link" 
                    size="small" 
                    @click="toggleRoleStatus(record)"
                  >
                    {{ record.status ? '禁用' : '启用' }}
                  </a-button>
                  <a-popconfirm
                    title="确定要删除这个角色吗？"
                    @confirm="deleteRole(record)"
                  >
                    <a-button type="link" size="small" danger>
                      删除
                    </a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>

          <!-- 批量操作 -->
          <div v-if="selectedRowKeys.length > 0" class="batch-actions">
            <a-space>
              <span>已选择 {{ selectedRowKeys.length }} 项</span>
              <a-button @click="batchEnable">批量启用</a-button>
              <a-button @click="batchDisable">批量禁用</a-button>
              <a-popconfirm
                title="确定要删除选中的角色吗？"
                @confirm="batchDelete"
              >
                <a-button danger>批量删除</a-button>
              </a-popconfirm>
            </a-space>
          </div>
        </a-card>
      </div>
    </div>

    <!-- 添加/编辑角色弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEditing ? '编辑角色' : '新建角色'"
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
            <a-form-item label="角色名称" name="name">
              <a-input v-model:value="formData.name" placeholder="输入角色名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="角色编码" name="code">
              <a-input 
                v-model:value="formData.code" 
                placeholder="输入角色编码"
                :disabled="isEditing"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="角色级别" name="level">
              <a-select v-model:value="formData.level" placeholder="选择角色级别">
                <a-select-option value="high">高级</a-select-option>
                <a-select-option value="medium">中级</a-select-option>
                <a-select-option value="low">初级</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="角色类型" name="type">
              <a-select v-model:value="formData.type" placeholder="选择角色类型">
                <a-select-option value="system">系统角色</a-select-option>
                <a-select-option value="business">业务角色</a-select-option>
                <a-select-option value="custom">自定义角色</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="角色描述" name="description">
          <a-textarea 
            v-model:value="formData.description" 
            placeholder="输入角色描述"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="状态" name="status">
          <a-switch v-model:checked="formData.status" />
          <span class="switch-description">{{ formData.status ? '启用' : '禁用' }}</span>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 权限配置弹窗 -->
    <a-modal
      v-model:open="permissionModalVisible"
      title="权限配置"
      width="800px"
      @ok="handlePermissionSubmit"
      @cancel="handlePermissionCancel"
    >
      <div class="permission-config">
        <div class="permission-header">
          <h3>为角色 "{{ selectedRole?.name }}" 配置权限</h3>
          <a-space>
            <a-button size="small" @click="expandAll">全部展开</a-button>
            <a-button size="small" @click="collapseAll">全部收起</a-button>
            <a-button size="small" @click="selectAll">全选</a-button>
            <a-button size="small" @click="unselectAll">全不选</a-button>
          </a-space>
        </div>
        
        <a-tree
          ref="permissionTreeRef"
          v-model:checkedKeys="checkedPermissions"
          :tree-data="permissionTree"
          :expanded-keys="expandedKeys"
          checkable
          :check-strictly="false"
          @expand="onExpand"
          @check="onCheck"
        >
          <template #title="{ title, icon }">
            <span class="permission-node">
              <component :is="icon" v-if="icon" class="permission-icon" />
              {{ title }}
            </span>
          </template>
        </a-tree>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { roleAPI } from '@/api/users';
import {
  SafetyOutlined,
  PlusOutlined,
  ExportOutlined,
  ReloadOutlined,
  CrownOutlined,
  UserOutlined,
  TeamOutlined,
  SettingOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  FolderOutlined,
  FileOutlined,
  DatabaseOutlined,
  MonitorOutlined,
  SecurityScanOutlined,
  ToolOutlined,
  FileTextOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';

// 响应式数据
const loading = ref(false);
const modalVisible = ref(false);
const permissionModalVisible = ref(false);
const isEditing = ref(false);
const searchText = ref('');
const statusFilter = ref('');
const activeCategory = ref('all');
const selectedRowKeys = ref([]);
const selectedRole = ref(null);
const checkedPermissions = ref([]);
const expandedKeys = ref(['1', '2', '3']);

// 表单数据
const formRef = ref();
const permissionTreeRef = ref();
const formData = ref({
  name: '',
  code: '',
  level: 'medium',
  type: 'business',
  description: '',
  status: true
});

// 角色数据
const roles = ref([]);
const roleStats = ref({
  total: 0,
  active: 0,
  permissions: 24
});

// 分类列表
const categoryList = ref([
  { key: 'all', name: '全部角色', icon: 'TeamOutlined', count: 0 },
  { key: 'system', name: '系统角色', icon: 'CrownOutlined', count: 0 },
  { key: 'business', name: '业务角色', icon: 'UserOutlined', count: 0 },
  { key: 'custom', name: '自定义角色', icon: 'SettingOutlined', count: 0 },
  { key: 'active', name: '启用角色', icon: 'CheckCircleOutlined', count: 0 },
  { key: 'inactive', name: '禁用角色', icon: 'CloseCircleOutlined', count: 0 }
]);

// 表格列配置
const tableColumns = [
  { title: '角色名称', dataIndex: 'name', key: 'name', sorter: true,width: 150 },
  { title: '角色编码', dataIndex: 'code', key: 'code' },
  { title: '角色级别', key: 'level', width: 100 },
  { title: '角色类型', dataIndex: 'type', key: 'type', width: 100 },
  { title: '权限数量', key: 'permissions', width: 120 },
  { title: '用户数量', key: 'users', width: 120 },
  { title: '状态', key: 'status', width: 80 },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt', width: 150, sorter: true },
  { title: '操作', key: 'actions', width: 250, fixed: 'right' }
];

// 分页配置
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
});

// 行选择配置
const rowSelection = {
  selectedRowKeys,
  onChange: (keys) => { selectedRowKeys.value = keys; }
};

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 50, message: '角色名称长度在2-50个字符', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[A-Z_][A-Z0-9_]*$/, message: '角色编码只能包含大写字母、数字和下划线', trigger: 'blur' }
  ],
  level: [{ required: true, message: '请选择角色级别', trigger: 'change' }],
  type: [{ required: true, message: '请选择角色类型', trigger: 'change' }]
};

// 权限树数据
const permissionTree = ref([
  {
    title: '系统管理', key: '1', icon: 'SettingOutlined',
    children: [
      {
        title: '用户管理', key: '1-1', icon: 'UserOutlined',
        children: [
          { title: '查看用户', key: '1-1-1', icon: 'EyeOutlined' },
          { title: '创建用户', key: '1-1-2', icon: 'PlusOutlined' },
          { title: '编辑用户', key: '1-1-3', icon: 'EditOutlined' },
          { title: '删除用户', key: '1-1-4', icon: 'DeleteOutlined' }
        ]
      },
      {
        title: '角色权限', key: '1-2', icon: 'SafetyOutlined',
        children: [
          { title: '查看角色', key: '1-2-1', icon: 'EyeOutlined' },
          { title: '创建角色', key: '1-2-2', icon: 'PlusOutlined' },
          { title: '编辑角色', key: '1-2-3', icon: 'EditOutlined' },
          { title: '删除角色', key: '1-2-4', icon: 'DeleteOutlined' },
          { title: '权限分配', key: '1-2-5', icon: 'SecurityScanOutlined' }
        ]
      }
    ]
  },
  {
    title: '业务管理', key: '2', icon: 'DatabaseOutlined',
    children: [
      {
        title: '资产管理', key: '2-1', icon: 'FolderOutlined',
        children: [
          { title: '查看资产', key: '2-1-1', icon: 'EyeOutlined' },
          { title: '创建资产', key: '2-1-2', icon: 'PlusOutlined' }
        ]
      }
    ]
  }
]);

// 计算属性
const filteredRoles = computed(() => {
  let result = roles.value;
  
  if (activeCategory.value !== 'all') {
    if (activeCategory.value === 'active') {
      result = result.filter(role => role.status);
    } else if (activeCategory.value === 'inactive') {
      result = result.filter(role => !role.status);
    } else {
      result = result.filter(role => role.type === activeCategory.value);
    }
  }
  
  if (statusFilter.value !== '') {
    const status = statusFilter.value === 'true';
    result = result.filter(role => role.status === status);
  }
  
  if (searchText.value) {
    const searchLower = searchText.value.toLowerCase();
    result = result.filter(role => 
      role.name?.toLowerCase().includes(searchLower) ||
      role.code?.toLowerCase().includes(searchLower) ||
      role.description?.toLowerCase().includes(searchLower)
    );
  }
  
  return result;
});

// 获取当前分类名称
const getCurrentCategoryName = () => {
  const category = categoryList.value.find(cat => cat.key === activeCategory.value);
  return category ? category.name : '全部角色';
};

// 获取级别颜色
const getLevelColor = (level) => {
  const colors = { high: 'red', medium: 'orange', low: 'green' };
  return colors[level] || 'default';
};

// 获取级别文本
const getLevelText = (level) => {
  const texts = { high: '高级', medium: '中级', low: '初级' };
  return texts[level] || level;
};

// 更新统计数据
const updateStats = () => {
  const stats = {
    total: roles.value.length,
    active: roles.value.filter(role => role.status).length,
    permissions: 24
  };
  
  roleStats.value = stats;
  
  categoryList.value.forEach(category => {
    switch (category.key) {
      case 'all': category.count = stats.total; break;
      case 'system': category.count = roles.value.filter(role => role.type === 'system').length; break;
      case 'business': category.count = roles.value.filter(role => role.type === 'business').length; break;
      case 'custom': category.count = roles.value.filter(role => role.type === 'custom').length; break;
      case 'active': category.count = stats.active; break;
      case 'inactive': category.count = stats.total - stats.active; break;
    }
  });
};

// 生成模拟数据
const generateMockRoles = () => {
  return [
    {
      id: 1, name: '超级管理员', code: 'SUPER_ADMIN', level: 'high', type: 'system',
      description: '系统超级管理员，拥有所有权限', status: true,
      permissions: ['1', '1-1', '1-1-1', '1-1-2', '1-1-3'], userCount: 1,
      createdAt: '2024-01-01 10:00:00'
    },
    {
      id: 2, name: '系统管理员', code: 'SYS_ADMIN', level: 'high', type: 'system',
      description: '系统管理员，负责系统配置', status: true,
      permissions: ['1', '1-1', '1-1-1'], userCount: 2,
      createdAt: '2024-01-02 11:30:00'
    },
    {
      id: 3, name: '业务管理员', code: 'BIZ_ADMIN', level: 'medium', type: 'business',
      description: '业务管理员，负责业务数据管理', status: true,
      permissions: ['2', '2-1', '2-1-1'], userCount: 5,
      createdAt: '2024-01-03 09:15:00'
    },
    {
      id: 4, name: '访客', code: 'GUEST', level: 'low', type: 'custom',
      description: '访客角色，只有基本查看权限', status: false,
      permissions: ['2-1-1'], userCount: 0,
      createdAt: '2024-01-06 08:30:00'
    }
  ];
};

// 获取角色列表
const fetchRoles = async () => {
  try {
    loading.value = true;
    roles.value = generateMockRoles();
    updateStats();
    message.warning('数据加载失败，显示模拟数据');
  } finally {
    loading.value = false;
  }
};

// 分类切换
const handleCategoryChange = (key) => {
  activeCategory.value = key;
  selectedRowKeys.value = [];
};

// 搜索处理
const handleSearch = () => { selectedRowKeys.value = []; };
const handleStatusFilter = () => { selectedRowKeys.value = []; };

// 刷新数据
const refreshData = () => {
  fetchRoles();
  message.success('数据刷新成功');
};

// 显示新建角色弹窗
const showAddModal = () => {
  isEditing.value = false;
  formData.value = { name: '', code: '', level: 'medium', type: 'business', description: '', status: true };
  modalVisible.value = true;
};

// 编辑角色
const editRole = (record) => {
  isEditing.value = true;
  formData.value = { ...record };
  modalVisible.value = true;
};

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    loading.value = true;
    
    if (isEditing.value) {
      const index = roles.value.findIndex(role => role.id === formData.value.id);
      if (index !== -1) {
        roles.value[index] = { ...roles.value[index], ...formData.value };
      }
      message.success('角色更新成功');
    } else {
      const newRole = { 
        id: Date.now(), ...formData.value, permissions: [], userCount: 0,
        createdAt: new Date().toLocaleString('zh-CN')
      };
      roles.value.unshift(newRole);
      message.success('角色创建成功');
    }
    
    updateStats();
    modalVisible.value = false;
  } catch (error) {
    message.error('操作失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 取消操作
const handleCancel = () => {
  modalVisible.value = false;
  formRef.value?.resetFields();
};

// 配置权限
const configPermissions = (record) => {
  selectedRole.value = record;
  checkedPermissions.value = [...record.permissions];
  permissionModalVisible.value = true;
};

// 权限树操作
const expandAll = () => {
  expandedKeys.value = ['1', '2', '3', '1-1', '1-2', '2-1'];
};
const collapseAll = () => { expandedKeys.value = []; };
const selectAll = () => {
  checkedPermissions.value = ['1', '1-1', '1-1-1', '1-1-2', '1-1-3', '1-1-4', '1-2', '1-2-1', '1-2-2', '1-2-3', '1-2-4', '1-2-5', '2', '2-1', '2-1-1', '2-1-2'];
};
const unselectAll = () => { checkedPermissions.value = []; };
const onExpand = (keys) => { expandedKeys.value = keys; };
const onCheck = (keys) => { checkedPermissions.value = keys; };

// 提交权限配置
const handlePermissionSubmit = async () => {
  try {
    loading.value = true;
    
    if (selectedRole.value) {
      const index = roles.value.findIndex(role => role.id === selectedRole.value.id);
      if (index !== -1) {
        roles.value[index].permissions = [...checkedPermissions.value];
      }
      message.success('权限配置成功');
      permissionModalVisible.value = false;
    }
  } catch (error) {
    message.error('权限配置失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 取消权限配置
const handlePermissionCancel = () => {
  permissionModalVisible.value = false;
  selectedRole.value = null;
  checkedPermissions.value = [];
};

// 切换角色状态
const toggleRoleStatus = async (record) => {
  try {
    loading.value = true;
    record.status = !record.status;
    updateStats();
    message.success(`角色${record.status ? '启用' : '禁用'}成功`);
  } catch (error) {
    message.error('操作失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 删除角色
const deleteRole = async (record) => {
  try {
    loading.value = true;
    const index = roles.value.findIndex(role => role.id === record.id);
    if (index !== -1) {
      roles.value.splice(index, 1);
    }
    updateStats();
    message.success('角色删除成功');
  } catch (error) {
    message.error('删除失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 批量操作
const batchEnable = () => {
  selectedRowKeys.value.forEach(id => {
    const role = roles.value.find(r => r.id === id);
    if (role) role.status = true;
  });
  updateStats();
  selectedRowKeys.value = [];
  message.success('批量启用成功');
};

const batchDisable = () => {
  selectedRowKeys.value.forEach(id => {
    const role = roles.value.find(r => r.id === id);
    if (role) role.status = false;
  });
  updateStats();
  selectedRowKeys.value = [];
  message.success('批量禁用成功');
};

const batchDelete = () => {
  roles.value = roles.value.filter(role => !selectedRowKeys.value.includes(role.id));
  updateStats();
  selectedRowKeys.value = [];
  message.success('批量删除成功');
};

// 导出角色
const exportRoles = () => {
  message.success('角色列表导出成功');
};

// 组件挂载
onMounted(() => {
  fetchRoles();
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 角色权限页面特有的样式 */
.permission-config {
  max-height: 500px;
  overflow-y: auto;
}

.permission-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.permission-header h3 {
  margin: 0;
  color: #262626;
}

.permission-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.permission-icon {
  color: #1890ff;
  font-size: 14px;
}

/* 权限树样式优化 */
:deep(.ant-tree) {
  background: transparent;
}

:deep(.ant-tree-treenode) {
  padding: 2px 0;
}

:deep(.ant-tree-node-content-wrapper) {
  border-radius: 4px;
  transition: all 0.2s;
}

:deep(.ant-tree-node-content-wrapper:hover) {
  background-color: #f5f5f5;
}

:deep(.ant-tree-node-selected) {
  background-color: #e6f7ff !important;
}

:deep(.ant-tree-checkbox) {
  margin-right: 8px;
}
</style>