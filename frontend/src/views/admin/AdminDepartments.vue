<template>
  <div class="admin-departments admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <BankOutlined />
          部门管理
        </h1>
        <p class="page-description">管理组织架构中的部门信息</p>
      </div>
      <div class="header-actions">
        <a-space>
          <a-tooltip title="导出部门列表为Excel文件" placement="bottom">
            <a-button @click="exportDepartments">
              <ExportOutlined />
              导出部门
            </a-button>
          </a-tooltip>
          <a-tooltip title="创建新的部门" placement="bottom">
            <a-button type="primary" @click="showAddModal">
              <PlusOutlined />
              新建部门
            </a-button>
          </a-tooltip>
        </a-space>
      </div>
    </div>

    <!-- 部门管理布局 -->
    <div class="departments-layout admin-layout">
      <!-- 内容区域 -->
      <div class="departments-content admin-content full-width">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
             <a-space>
               <a-input-search
                 v-model:value="searchText"
                 placeholder="搜索部门..."
                 style="width: 200px"
                 @search="handleSearch"
                 @change="handleSearch"
               />
               <a-select
                 v-model:value="statusFilter"
                 placeholder="状态筛选"
                 style="width: 120px"
                 @change="handleFilterChange"
               >
                 <a-select-option value="">全部状态</a-select-option>
                 <a-select-option value="active">启用</a-select-option>
                 <a-select-option value="inactive">禁用</a-select-option>
               </a-select>
               <a-tooltip title="刷新部门列表数据" placement="bottom">
                 <a-button @click="refreshData">
                   <ReloadOutlined />
                 </a-button>
               </a-tooltip>
             </a-space>
           </template>

          <!-- 部门表格 -->
          <a-table
            :columns="columns"
            :data-source="departmentTreeData"
            :loading="loading"
            :pagination="false"
            row-key="id"
            :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
            :default-expand-all="false"
            :expand-row-by-click="false"
            @change="handleTableChange"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'name'">
                <div class="department-name">
                  <FolderOutlined v-if="record.children && record.children.length > 0" class="folder-icon" />
                  <FileOutlined v-else class="file-icon" />
                  <span class="name-text">{{ record.name }}</span>
                </div>
              </template>
              <template v-else-if="column.key === 'manager'">
                <div class="manager-info" v-if="record.manager">
                  <span class="manager-name">{{ record.manager }}</span>
                </div>
                <span v-else class="no-manager">未设置</span>
              </template>
              <template v-else-if="column.key === 'status'">
                <a-tag :color="record.status === 'active' ? 'green' : 'red'">
                  {{ record.status === 'active' ? '启用' : '禁用' }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'action'">
                <a-space>
                  <a-tooltip title="查看详情">
                    <a-button type="text" size="small" @click="viewDepartment(record)">
                      <EyeOutlined />
                    </a-button>
                  </a-tooltip>
                  <a-tooltip title="编辑部门">
                    <a-button type="text" size="small" @click="editDepartment(record)">
                      <EditOutlined />
                    </a-button>
                  </a-tooltip>
                  <a-tooltip title="添加子部门">
                    <a-button type="text" size="small" @click="addSubDepartment(record)">
                      <PlusOutlined />
                    </a-button>
                  </a-tooltip>
                  <a-popconfirm
                    title="确定要删除这个部门吗？"
                    @confirm="handleDeleteDepartment(record)"
                  >
                    <a-tooltip title="删除部门">
                      <a-button type="text" size="small" danger>
                        <DeleteOutlined />
                      </a-button>
                    </a-tooltip>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>
    </div>

    <!-- 新建/编辑部门弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      :width="600"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="部门名称" name="name">
              <a-input v-model:value="formData.name" placeholder="请输入部门名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="部门编码" name="code">
              <a-input v-model:value="formData.code" placeholder="请输入部门编码" />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="上级部门" name="parent">
              <a-tree-select
                v-model:value="formData.parent"
                :tree-data="departmentOptions"
                placeholder="请选择上级部门"
                allow-clear
                tree-default-expand-all
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="部门负责人" name="manager">
              <a-select
                v-model:value="formData.manager"
                placeholder="请选择部门负责人"
                allow-clear
                show-search
                :filter-option="filterOption"
              >
                <a-select-option v-for="user in userList" :key="user.id" :value="user.id">
                  {{ user.username }} - {{ user.first_name }} {{ user.last_name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="状态" name="status">
              <a-select v-model:value="formData.status" placeholder="请选择状态">
                <a-select-option value="active">启用</a-select-option>
                <a-select-option value="inactive">禁用</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="部门描述" name="description">
          <a-textarea
            v-model:value="formData.description"
            placeholder="请输入部门描述"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 部门详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="部门详情"
      :width="800"
      :footer="null"
    >
      <div v-if="selectedDepartment" class="department-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="部门名称">
            {{ selectedDepartment.name }}
          </a-descriptions-item>
          <a-descriptions-item label="部门编码">
            {{ selectedDepartment.code }}
          </a-descriptions-item>
          <a-descriptions-item label="上级部门">
            {{ selectedDepartment.parent_name || '无' }}
          </a-descriptions-item>
          <a-descriptions-item label="部门负责人">
            {{ selectedDepartment.manager || '未设置' }}
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="selectedDepartment.status === 'active' ? 'green' : 'red'">
              {{ selectedDepartment.status === 'active' ? '启用' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间" :span="2">
            {{ selectedDepartment.created_at }}
          </a-descriptions-item>
          <a-descriptions-item label="部门描述" :span="2">
            {{ selectedDepartment.description || '无' }}
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import {
  BankOutlined,
  ExportOutlined,
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  FolderOutlined,
  FileOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';
import {
  getDepartments,
  getDepartmentTree,
  createDepartment,
  updateDepartment,
  deleteDepartment,
  getDepartmentStatistics
} from '@/api/organization';
import { userAPI } from '@/api/users';

// 响应式数据
const loading = ref(false);
const searchText = ref('');
const statusFilter = ref('');
const levelFilter = ref('');

const modalVisible = ref(false);
const detailModalVisible = ref(false);
const isEdit = ref(false);
const selectedDepartment = ref(null);
const formRef = ref();

// 表单数据
const formData = reactive({
  name: '',
  code: '',
  parent: null,
  manager: null,
  sort_order: 0,
  status: 'active',
  description: ''
});

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
};

// 数据
const departmentList = ref([]);
const userList = ref([]);
const departmentTreeDataRef = ref([]);



// 表格列定义
const columns = [
  {
    title: '部门名称',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '部门编码',
    dataIndex: 'code',
    key: 'code'
  },
  {
    title: '上级部门',
    dataIndex: 'parent_name',
    key: 'parent_name'
  },
  {
    title: '负责人',
    dataIndex: 'manager',
    key: 'manager',
    width: 100
  },
  {
    title: '状态',
    key: 'status',
    width: 80
  },
  {
    title: '操作',
    key: 'action',
    width: 200,
    fixed: 'right'
  }
];

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
});

// 计算属性
const modalTitle = computed(() => {
  return isEdit.value ? '编辑部门' : '新建部门';
});

// 构建树形数据
const departmentTreeData = computed(() => {
  // 直接返回从API获取的树形数据
  return departmentTreeDataRef.value;
});

const departmentOptions = computed(() => {
  // 构建部门选择器数据
  const buildOptions = (departments) => {
    if (!Array.isArray(departments)) {
      return [];
    }
    return departments.map(dept => ({
      title: dept.name,
      value: dept.id,
      key: dept.id,
      children: dept.children && dept.children.length > 0 ? buildOptions(dept.children) : []
    }));
  };
  return buildOptions(departmentTreeData.value);
});

// 方法

const handleSearch = () => {
  loadDepartments();
};

const handleSearchChange = () => {
  if (!searchText.value) {
    loadDepartments();
  }
};

const handleFilterChange = () => {
  loadDepartments();
};

const resetFilters = () => {
  searchText.value = '';
  statusFilter.value = '';
  levelFilter.value = '';
  loadDepartments();
};

const handleTableChange = (pag, filters, sorter) => {
  // 树形表格不需要分页处理
  loadDepartments();
};

const loadDepartments = async () => {
  loading.value = true;
  try {
    // 获取树形结构数据
    const response = await getDepartmentTree();
    if (response.status == 200){
      const results = response.data || [];
      console.log('部门树形数据:', results);
      // 直接使用树形数据
      departmentTreeDataRef.value = results;
      // 同时保存扁平化数据用于其他功能
      departmentList.value = flattenTreeData(results);
    }
  } catch (error) {
    console.error('加载部门列表失败:', error);
    message.error('加载部门列表失败');
  } finally {
    loading.value = false;
  }
};

// 将树形数据扁平化
const flattenTreeData = (treeData) => {
  const result = [];
  const flatten = (nodes, level = 1) => {
    nodes.forEach(node => {
      result.push({
        ...node,
        level: level
      });
      if (node.children && node.children.length > 0) {
        flatten(node.children, level + 1);
      }
    });
  };
  flatten(treeData);
  return result;
};

const showAddModal = () => {
  isEdit.value = false;
  resetForm();
  modalVisible.value = true;
};

const addSubDepartment = (record) => {
  isEdit.value = false;
  resetForm();
  formData.parent = record.id;
  modalVisible.value = true;
};

const editDepartment = (record) => {
  isEdit.value = true;
  Object.assign(formData, {
    id: record.id,
    name: record.name,
    code: record.code,
    parent: record.parent,
    manager: record.manager,
    sort_order: record.sort_order,
    status: record.status,
    description: record.description
  });
  modalVisible.value = true;
};

const viewDepartment = (record) => {
  selectedDepartment.value = record;
  detailModalVisible.value = true;
};

const handleDeleteDepartment = async (record) => {
  try {
    await deleteDepartment(record.id);
    message.success('删除成功');
    loadDepartments();
  } catch (error) {
    console.error('删除部门失败:', error);
    message.error('删除失败');
  }
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    
    // 准备提交数据，将parent转换为parent_id
    const submitData = { ...formData };
    if (submitData.parent) {
      submitData.parent_id = submitData.parent;
      delete submitData.parent;
    }
    
    if (isEdit.value) {
      await updateDepartment(submitData.id, submitData);
      message.success('更新成功');
    } else {
      await createDepartment(submitData);
      message.success('创建成功');
    }
    
    modalVisible.value = false;
    loadDepartments();
    loadDepartmentTree();
  } catch (error) {
    console.error('保存部门失败:', error);
    
    // 处理表单验证错误
    if (error.errorFields) {
      message.error('请检查表单输入');
      return;
    }
    
    // 处理API返回的错误
    if (error.response && error.response.data) {
      const errorData = error.response.data;
      
      // 处理字段特定错误
      if (errorData.code && Array.isArray(errorData.code)) {
        message.error(`部门编码错误: ${errorData.code[0]}`);
        return;
      }
      
      if (errorData.name && Array.isArray(errorData.name)) {
        message.error(`部门名称错误: ${errorData.name[0]}`);
        return;
      }
      
      // 处理其他字段错误
      const firstErrorField = Object.keys(errorData)[0];
      if (firstErrorField && Array.isArray(errorData[firstErrorField])) {
        message.error(`${firstErrorField}: ${errorData[firstErrorField][0]}`);
        return;
      }
      
      // 处理通用错误消息
      if (errorData.detail) {
        message.error(errorData.detail);
        return;
      }
      
      if (errorData.message) {
        message.error(errorData.message);
        return;
      }
    }
    
    // 默认错误消息
    message.error(isEdit.value ? '更新失败' : '创建失败');
  }
};

const handleModalCancel = () => {
  modalVisible.value = false;
  resetForm();
};

const resetForm = () => {
  Object.assign(formData, {
    name: '',
    code: '',
    parent: null,
    manager: null,
    sort_order: 0,
    status: 'active',
    description: ''
  });
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

const exportDepartments = () => {
  // 导出功能实现
  message.info('导出功能开发中...');
};

const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0;
};

const getCurrentCategoryName = () => {
  return '部门管理';
};

const refreshData = () => {
  loadDepartments();
};

// 加载部门树形数据
const loadDepartmentTree = async () => {
  try {
    const response = await getDepartmentTree();
    const treeData = response.data || response || [];
    departmentTreeData.value = Array.isArray(treeData) ? treeData : [];
  } catch (error) {
    console.error('加载部门树失败:', error);
  }
};

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await userAPI.getUserList();
    const users = response.data?.results || response.data?.data || [];
    userList.value = Array.isArray(users) ? users : [];
  } catch (error) {
    console.error('加载用户列表失败:', error);
  }
};

// 生命周期
onMounted(() => {
  loadDepartments();
  loadDepartmentTree();
  loadUsers();
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 部门管理页面特有的样式 */
.departments-layout {
  display: flex;
  gap: 24px;
  min-height: calc(100vh - 200px);
}

.departments-content.full-width {
  flex: 1;
  width: 100%;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.departments-content.full-width .ant-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.departments-content.full-width .ant-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.departments-content.full-width .ant-table-wrapper {
  flex: 1;
  height: 100%;
}

.departments-content.full-width .ant-table {
  height: 100%;
}

.departments-content.full-width .ant-table-tbody {
  height: calc(100% - 55px);
  overflow-y: auto;
}

.department-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-indent {
  display: inline-block;
}

.folder-icon,
.file-icon {
  color: #1890ff;
}

.name-text {
  font-weight: 500;
}

.manager-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.manager-name {
  font-size: 13px;
}

.no-manager {
  color: #999;
  font-style: italic;
}

.department-detail {
  padding: 16px 0;
}
</style>