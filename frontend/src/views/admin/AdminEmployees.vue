<template>
  <div class="admin-employees admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <ContactsOutlined />
          员工管理
        </h1>
        <p class="page-description">管理组织架构中的员工信息</p>
      </div>
      <div class="header-actions">
        <a-space>
          <a-tooltip title="导出员工列表为Excel文件" placement="bottom">
            <a-button @click="exportEmployees">
              <ExportOutlined />
              导出员工
            </a-button>
          </a-tooltip>
          <a-tooltip title="创建新的员工" placement="bottom">
            <a-button type="primary" @click="showAddModal">
              <PlusOutlined />
              新建员工
            </a-button>
          </a-tooltip>
        </a-space>
      </div>
    </div>

    <!-- 员工管理布局 -->
    <div class="employees-layout admin-layout">
      <!-- 左侧菜单 -->
      <div class="employees-menu admin-menu">
        <div class="menu-title">部门分类</div>
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
      </div>

      <!-- 右侧内容区域 -->
      <div class="employees-content admin-content">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
            <a-space>
              <a-input-search
                v-model:value="searchText"
                placeholder="搜索员工..."
                style="width: 200px"
                @search="handleSearch"
                @change="handleSearch"
              />
              <a-tooltip title="刷新员工列表数据" placement="bottom">
                <a-button @click="refreshData">
                  <ReloadOutlined />
                </a-button>
              </a-tooltip>
            </a-space>
          </template>

          <!-- 员工表格 -->
          <a-table
            :columns="columns"
            :data-source="employeeList"
            :loading="loading"
            :pagination="pagination"
            row-key="id"
            @change="handleTableChange"
          >
            <template #bodyCell="{ column, record }">
              <!-- 员工信息列 -->
              <template v-if="column.key === 'employee_info'">
                <div class="employee-info">
                  <a-avatar :size="40" :style="{ background: getAvatarColor(record.name) }">
                    {{ record.name.charAt(0) }}
                  </a-avatar>
                  <div class="info-text">
                    <div class="name">{{ record.name }}</div>
                    <div class="employee-no">工号: {{ record.employee_id }}</div>
                  </div>
                </div>
              </template>

              <!-- 状态列 -->
              <template v-else-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.employment_status)">
                  {{ getStatusText(record.employment_status) }}
                </a-tag>
              </template>

              <!-- 部门列 -->
              <template v-else-if="column.key === 'department_name'">
                <span>{{ record.department?.name || '-' }}</span>
              </template>

              <!-- 职位列 -->
              <template v-else-if="column.key === 'position_name'">
                <span>{{ record.position?.name || '-' }}</span>
              </template>

              <!-- 直属上级列 -->
              <template v-else-if="column.key === 'supervisor_name'">
                <span>{{ record.direct_supervisor?.name || '-' }}</span>
              </template>

              <!-- 联系方式列 -->
              <template v-else-if="column.key === 'contact'">
                <div class="contact-info">
                  <div v-if="record.mobile || record.phone" class="contact-item">
                    <PhoneOutlined class="contact-icon" />
                    <span>{{ record.mobile || record.phone }}</span>
                  </div>
                  <div v-if="record.email" class="contact-item">
                    <MailOutlined class="contact-icon" />
                    <span>{{ record.email }}</span>
                  </div>
                </div>
              </template>

              <!-- 操作列 -->
              <template v-else-if="column.key === 'action'">
              <a-space>
                <a-tooltip title="查看详情">
                  <a-button type="text" size="small" @click="viewEmployee(record)">
                    <EyeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="编辑员工">
                  <a-button type="text" size="small" @click="editEmployee(record)">
                    <EditOutlined />
                  </a-button>
                </a-tooltip>
                <a-popconfirm
                  title="确定要删除这个员工吗？"
                  @confirm="handleDeleteEmployee(record)"
                >
                  <a-tooltip title="删除员工">
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

    <!-- 新建/编辑员工弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      :width="800"
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
          <a-col :span="8">
            <a-form-item label="员工姓名" name="name">
              <a-input v-model:value="formData.name" placeholder="请输入员工姓名" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="员工工号" name="employee_id">
              <a-input v-model:value="formData.employee_id" placeholder="请输入员工工号" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="关联用户" name="user">
              <a-select
                v-model:value="formData.user"
                placeholder="请选择关联用户"
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
          <a-col :span="8">
            <a-form-item label="所属部门" name="department">
              <a-select
                v-model:value="formData.department"
                placeholder="请选择所属部门"
                allow-clear
                @change="handleDepartmentChange"
              >
                <a-select-option v-for="dept in departmentList" :key="dept.id" :value="dept.id">
                  {{ dept.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="职位" name="position">
              <a-select
                v-model:value="formData.position"
                placeholder="请选择职位"
                allow-clear
              >
                <a-select-option v-for="pos in filteredPositions" :key="pos.id" :value="pos.id">
                  {{ pos.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="直属上级" name="supervisor">
              <a-select
                v-model:value="formData.supervisor"
                placeholder="请选择直属上级"
                allow-clear
                show-search
                :filter-option="filterOption"
              >
                <a-select-option v-for="emp in employeeList" :key="emp.id" :value="emp.id">
                  {{ emp.name }} - {{ emp.employee_no }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="8">
            <a-form-item label="手机号码" name="phone">
              <a-input v-model:value="formData.phone" placeholder="请输入手机号码" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="邮箱地址" name="email">
              <a-input v-model:value="formData.email" placeholder="请输入邮箱地址" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="入职日期" name="hire_date">
              <a-date-picker
                v-model:value="formData.hire_date"
                placeholder="请选择入职日期"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>



        <a-form-item label="备注" name="notes">
          <a-textarea
            v-model:value="formData.notes"
            placeholder="请输入备注信息"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 员工详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="员工详情"
      :width="900"
      :footer="null"
    >
      <div v-if="selectedEmployee" class="employee-detail">
        <a-descriptions :column="3" bordered>
          <a-descriptions-item label="员工姓名">
            {{ selectedEmployee.name }}
          </a-descriptions-item>
          <a-descriptions-item label="员工工号">
            {{ selectedEmployee.employee_id }}
          </a-descriptions-item>
          <a-descriptions-item label="关联用户">
            {{ selectedEmployee.user?.username || '未关联' }}
          </a-descriptions-item>
          <a-descriptions-item label="所属部门">
            {{ selectedEmployee.department?.name || '未设置' }}
          </a-descriptions-item>
          <a-descriptions-item label="职位">
            {{ selectedEmployee.position?.name || '未设置' }}
          </a-descriptions-item>
          <a-descriptions-item label="直属上级">
            {{ selectedEmployee.direct_supervisor?.name || '无' }}
          </a-descriptions-item>
          <a-descriptions-item label="手机号码">
            {{ selectedEmployee.mobile || selectedEmployee.phone || '未填写' }}
          </a-descriptions-item>
          <a-descriptions-item label="邮箱地址">
            {{ selectedEmployee.email || '未填写' }}
          </a-descriptions-item>
          <a-descriptions-item label="入职日期">
            {{ selectedEmployee.hire_date || '未设置' }}
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">
            {{ selectedEmployee.created_at ? dayjs(selectedEmployee.created_at).format('YYYY-MM-DD HH:mm:ss') : '未知' }}
          </a-descriptions-item>
          <a-descriptions-item label="备注" :span="3">
            {{ selectedEmployee.notes || '无' }}
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
  ContactsOutlined,
  ExportOutlined,
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  PhoneOutlined,
  MailOutlined,
  ApartmentOutlined
} from '@ant-design/icons-vue';
import dayjs from 'dayjs';
import {
  getEmployees,
  getEmployeeDetail,
  createEmployee,
  updateEmployee,
  deleteEmployee,
  getDepartmentEmployees,
  getPositionEmployees,
  getAvailableUsers,
  changeEmployeeStatus
} from '@/api/organization';
import { getDepartments, getPositions } from '@/api/organization';

// 响应式数据
const loading = ref(false);
const searchText = ref('');
const statusFilter = ref('');
const departmentFilter = ref('');
const positionFilter = ref('');
const activeCategory = ref('all');
const modalVisible = ref(false);
const detailModalVisible = ref(false);
const isEdit = ref(false);
const selectedEmployee = ref(null);
const formRef = ref();

// 表单数据
const formData = reactive({
  name: '',
  employee_id: '',
  user: null,
  department: null,
  position: null,
  supervisor: null,
  phone: '',
  email: '',
  hire_date: null,
  notes: ''
});

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入员工姓名', trigger: 'blur' }],
  employee_id: [{ required: true, message: '请输入员工工号', trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
  position: [{ required: true, message: '请选择职位', trigger: 'change' }],
  status: [{ required: true, message: '请选择员工状态', trigger: 'change' }],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
};

// 数据
const employeeList = ref([]);
const userList = ref([]);
const departmentList = ref([]);
const positionList = ref([]);

// 分类列表
const categoryList = ref([]);

// 表格列定义
const columns = [
  {
    title: '员工姓名',
    key: 'employee_info',
    width: 200
  },
  {
    title: '所属部门',
    dataIndex: 'department_name',
    key: 'department_name',
    width: 120
  },
  {
    title: '职位',
    dataIndex: 'position_name',
    key: 'position_name',
    width: 150
  },
  {
    title: '直属上级',
    dataIndex: 'supervisor_name',
    key: 'supervisor_name',
    width: 120
  },
  {
    title: '联系方式',
    key: 'contact',
    width: 180
  },
  {
    title: '入职日期',
    dataIndex: 'hire_date',
    key: 'hire_date',
    width: 120
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
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
  return isEdit.value ? '编辑员工' : '新建员工';
});

const filteredPositions = computed(() => {
  console.log('positionList:', positionList.value);
  console.log('formData.department:', formData.department);
  
  if (!Array.isArray(positionList.value)) return [];
  
  // 如果没有选择部门，返回所有职位
  if (!formData.department) {
    return positionList.value;
  }
  
  // 根据选择的部门过滤职位
  const filtered = positionList.value.filter(pos => {
    console.log('pos.department:', pos.department, 'pos.department?.id:', pos.department?.id);
    return pos.department?.id === formData.department;
  });
  
  console.log('filtered positions:', filtered);
  return filtered;
});

// 方法
const getAvatarColor = (name) => {
  const colors = ['#f56a00', '#7265e6', '#ffbf00', '#00a2ae', '#87d068'];
  const index = name.charCodeAt(0) % colors.length;
  return colors[index];
};

const getStatusColor = (status) => {
  const colors = {
    'active': 'green',
    'inactive': 'red',
    'probation': 'orange'
  };
  return colors[status] || 'default';
};

const getStatusText = (status) => {
  const texts = {
    'active': '在职',
    'inactive': '离职',
    'probation': '试用期'
  };
  return texts[status] || '未知';
};

const handleCategoryChange = (key) => {
  activeCategory.value = key;
  // 根据选择的分类设置部门筛选
  if (key === 'all') {
    departmentFilter.value = '';
  } else {
    departmentFilter.value = key;
  }
  loadEmployees();
};

const handleSearch = () => {
  loadEmployees();
};

const handleSearchChange = () => {
  if (!searchText.value) {
    loadEmployees();
  }
};

const handleFilterChange = () => {
  loadEmployees();
};

const handleDepartmentChange = () => {
  formData.position = null; // 清空职位选择
  console.log('部门选择变更:', formData.department);
};

const resetFilters = () => {
  searchText.value = '';
  statusFilter.value = '';
  departmentFilter.value = '';
  positionFilter.value = '';
  activeCategory.value = 'all';
  // 重置部门分类时也要重置部门筛选
  departmentFilter.value = '';
  loadEmployees();
};

const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  loadEmployees();
};

const loadEmployees = async () => {
  loading.value = true;
  try {
    const response = await getEmployees({
      page: pagination.current,
      page_size: pagination.pageSize,
      search: searchText.value,
      status: statusFilter.value,
      department: departmentFilter.value,
      position: positionFilter.value
    });
    
    const results = response.data?.results || response.results || [];
    employeeList.value = Array.isArray(results) ? results : [];
    pagination.total = response.data?.total || response.total || response.count || 0;
  } catch (error) {
    console.error('加载员工列表失败:', error);
    message.error('加载员工列表失败');
  } finally {
    loading.value = false;
  }
};

const showAddModal = () => {
  isEdit.value = false;
  resetForm();
  modalVisible.value = true;
};

const editEmployee = (record) => {
  isEdit.value = true;
  Object.assign(formData, {
    id: record.id,
    name: record.name,
    employee_id: record.employee_id,
    user: record.user?.id || null,
    department: record.department?.id || null,
    position: record.position?.id || null,
    supervisor: record.direct_supervisor?.id || null,
    phone: record.phone || record.mobile,
    email: record.email,
    hire_date: record.hire_date ? dayjs(record.hire_date) : null,
    notes: record.notes
  });
  modalVisible.value = true;
};

const viewEmployee = (record) => {
  selectedEmployee.value = record;
  detailModalVisible.value = true;
};

const handleDeleteEmployee = async (record) => {
  try {
    await deleteEmployee(record.id);
    
    message.success('删除成功');
    loadEmployees();
  } catch (error) {
    console.error('删除员工失败:', error);
    message.error('删除失败');
  }
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    
    console.log('提交前的formData:', formData);
    
    // 格式化数据，将前端字段名转换为后端API期望的字段名
    const submitData = {
      name: formData.name,
      employee_id: formData.employee_id,
      user_id: formData.user,
      department_id: formData.department,
      position_id: formData.position,
      direct_supervisor_id: formData.supervisor,
      phone: formData.phone,
      mobile: formData.phone, // 后端使用mobile字段
      email: formData.email,
      office_location: null,
      hire_date: formData.hire_date ? formData.hire_date.format('YYYY-MM-DD') : null,
      probation_end_date: null,
      contract_type: 'full_time',
      employment_status: 'probation',
      emergency_contact_name: null,
      emergency_contact_phone: null,
      notes: formData.notes || ''
    };
    
    if (isEdit.value) {
      // 编辑时需要包含ID
      const updateData = { ...submitData, id: formData.id };
      await updateEmployee(formData.id, updateData);
      message.success('更新成功');
    } else {
      await createEmployee(submitData);
      message.success('创建成功');
    }
    
    modalVisible.value = false;
    loadEmployees();
  } catch (error) {
    console.error('保存员工失败:', error);
    
    // 处理表单验证错误
    if (error.errorFields) {
      message.error('请检查表单输入');
      return;
    }
    
    // 处理API返回的错误
    if (error.response && error.response.data) {
      const errorData = error.response.data;
      
      // 处理字段特定错误
      if (errorData.employee_id && Array.isArray(errorData.employee_id)) {
        message.error(`员工工号错误: ${errorData.employee_id[0]}`);
        return;
      }
      
      if (errorData.name && Array.isArray(errorData.name)) {
        message.error(`员工姓名错误: ${errorData.name[0]}`);
        return;
      }
      
      if (errorData.user && Array.isArray(errorData.user)) {
        message.error(`关联用户错误: ${errorData.user[0]}`);
        return;
      }
      
      if (errorData.phone && Array.isArray(errorData.phone)) {
        message.error(`手机号码错误: ${errorData.phone[0]}`);
        return;
      }
      
      if (errorData.email && Array.isArray(errorData.email)) {
        message.error(`邮箱地址错误: ${errorData.email[0]}`);
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
    employee_id: '',
    user: null,
    department: null,
    position: null,
    supervisor: null,
    phone: '',
    email: '',
    hire_date: null,
    notes: ''
  });
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

const exportEmployees = () => {
  // 导出功能实现
  message.info('导出功能开发中...');
};

const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0;
};

const getCurrentCategoryName = () => {
  const category = categoryList.value.find(cat => cat.key === activeCategory.value);
  return category ? category.name : '员工管理';
};

const refreshData = () => {
  loadDepartments();
  loadPositions();
  loadEmployees();
};

const loadDepartments = async () => {
  try {
    const response = await getDepartments();
    console.log(response.data.results)
    if (response.status == 200){
      const departments = response.data.results || response.results || [];
      console.log(departments)
      departmentList.value = Array.isArray(departments) ? departments : [];
      
      // 生成部门分类列表
      const categories = [
        { key: 'all', name: '全部员工', icon: 'ContactsOutlined', count: 0 }
      ];
      
      departments.forEach(dept => {
        categories.push({
          key: dept.id.toString(),
          name: dept.name,
          icon: 'ApartmentOutlined',
          count: dept.employee_count || 0
        });
      });
      
      categoryList.value = categories;
    }
  } catch (error) {
    console.error('加载部门列表失败:', error);
    message.error('加载部门列表失败');
  }
};

const loadPositions = async () => {
  try {
    const response = await getPositions();
    if (response.status == 200 ){
      console.log(response.data.results)
      const positions = response.data?.results || response.results || [];
      positionList.value = Array.isArray(positions) ? positions : [];
    }
  } catch (error) {
    console.error('加载职位列表失败:', error);
    message.error('加载职位列表失败');
  }
};

// 生命周期
onMounted(() => {
  loadEmployees();
  loadDepartments();
  loadPositions();
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 员工管理页面特有的样式 */
.employees-content {
  height: calc(100vh - 200px);
  overflow: hidden;
}

:deep(.ant-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.ant-card-body) {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}

:deep(.ant-table-wrapper) {
  height: 100%;
}

:deep(.ant-table) {
  height: 100%;
}

.employee-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.name {
  font-weight: 500;
  font-size: 14px;
}

.employee-no {
  font-size: 12px;
  color: #999;
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

.contact-icon {
  color: #1890ff;
}

.employee-detail {
  padding: 16px 0;
}

.salary-text {
  font-weight: 500;
  color: #52c41a;
}
</style>