<template>
  <div class="admin-positions admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <IdcardOutlined />
          职位管理
        </h1>
        <p class="page-description">管理组织架构中的职位信息</p>
      </div>
      <div class="header-actions">
        <a-space>
          <a-tooltip title="导出职位列表为Excel文件" placement="bottom">
            <a-button @click="exportPositions">
              <ExportOutlined />
              导出职位
            </a-button>
          </a-tooltip>
          <a-tooltip title="创建新的职位" placement="bottom">
            <a-button type="primary" @click="showAddModal">
              <PlusOutlined />
              新建职位
            </a-button>
          </a-tooltip>
        </a-space>
      </div>
    </div>

    <!-- 职位管理内容区域 -->
    <div class="positions-content admin-content full-width">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
            <a-space>
              <a-select
                v-model:value="departmentFilter"
                placeholder="选择部门"
                style="width: 150px"
                allow-clear
                @change="handleFilterChange"
              >
                <a-select-option value="">全部部门</a-select-option>
                <a-select-option v-for="dept in departmentList" :key="dept.id" :value="dept.id">
                  {{ dept.name }}
                </a-select-option>
              </a-select>
              <a-input-search
                v-model:value="searchText"
                placeholder="搜索职位..."
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
              <a-tooltip title="刷新职位列表数据" placement="bottom">
                <a-button @click="refreshData">
                  <ReloadOutlined />
                </a-button>
              </a-tooltip>
            </a-space>
          </template>

          <!-- 职位表格 -->
          <a-table
            :columns="columns"
            :data-source="positionList"
            :loading="loading"
            :pagination="pagination"
            row-key="id"
            @change="handleTableChange"
          >
            <template #bodyCell="{ column, record }">
              <!-- 职位名称列 -->
              <template v-if="column.key === 'name'">
                <div class="position-name">
                  <IdcardOutlined class="position-icon" />
                  <span class="name-text">{{ record.name }}</span>
                  <a-tag v-if="record.level" :color="getLevelColor(record.level)" size="small">
                    {{ getLevelText(record.level) }}
                  </a-tag>
                </div>
              </template>

              <!-- 状态列 -->
              <template v-else-if="column.key === 'status'">
                <a-tag :color="record.status === 'active' ? 'green' : 'red'">
                  {{ record.status === 'active' ? '启用' : '禁用' }}
                </a-tag>
              </template>



              <!-- 操作列 -->
              <template v-else-if="column.key === 'action'">
              <a-space>
                <a-tooltip title="查看详情">
                  <a-button type="text" size="small" @click="viewPosition(record)">
                    <EyeOutlined />
                  </a-button>
                </a-tooltip>
                <a-tooltip title="编辑职位">
                  <a-button type="text" size="small" @click="editPosition(record)">
                    <EditOutlined />
                  </a-button>
                </a-tooltip>
                <a-popconfirm
                  title="确定要删除这个职位吗？"
                  @confirm="handleDeletePosition(record)"
                >
                  <a-tooltip title="删除职位">
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

    <!-- 新建/编辑职位弹窗 -->
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
            <a-form-item label="职位名称" name="name">
              <a-input v-model:value="formData.name" placeholder="请输入职位名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="职位编码" name="code">
              <a-input v-model:value="formData.code" placeholder="请输入职位编码" />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="所属部门" name="department">
              <a-select
                v-model:value="formData.department"
                placeholder="请选择所属部门"
                allow-clear
              >
                <a-select-option v-for="dept in departmentList" :key="dept.id" :value="dept.id">
                  {{ dept.name }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="职位级别" name="level">
              <a-select v-model:value="formData.level" placeholder="请选择职位级别">
                <a-select-option value="junior">初级</a-select-option>
                <a-select-option value="intermediate">中级</a-select-option>
                <a-select-option value="senior">高级</a-select-option>
                <a-select-option value="expert">专家</a-select-option>
                <a-select-option value="manager">管理</a-select-option>
                <a-select-option value="director">总监</a-select-option>
                <a-select-option value="vp">副总</a-select-option>
                <a-select-option value="ceo">总裁</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>



        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="排序" name="sort_order">
              <a-input-number
                v-model:value="formData.sort_order"
                :min="0"
                :max="999"
                placeholder="排序号"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态" name="status">
              <a-select v-model:value="formData.status" placeholder="请选择状态">
                <a-select-option value="active">启用</a-select-option>
                <a-select-option value="inactive">禁用</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="职位描述" name="description">
          <a-textarea
            v-model:value="formData.description"
            placeholder="请输入职位描述"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="职位要求" name="requirements">
          <a-textarea
            v-model:value="formData.requirements"
            placeholder="请输入职位要求"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 职位详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="职位详情"
      :width="800"
      :footer="null"
    >
      <div v-if="selectedPosition" class="position-detail">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="职位名称">
            {{ selectedPosition.name }}
          </a-descriptions-item>
          <a-descriptions-item label="职位编码">
            {{ selectedPosition.code }}
          </a-descriptions-item>
          <a-descriptions-item label="所属部门">
            {{ selectedPosition.department?.full_name || '未设置' }}
          </a-descriptions-item>
          <a-descriptions-item label="职位级别">
            <a-tag :color="getLevelColor(selectedPosition.level)">
              {{ getLevelText(selectedPosition.level) }}
            </a-tag>
          </a-descriptions-item>

          <a-descriptions-item label="状态">
            <a-tag :color="selectedPosition.status === 'active' ? 'green' : 'red'">
              {{ selectedPosition.status === 'active' ? '启用' : '禁用' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间" :span="2">
            {{ formatDate(selectedPosition.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item label="职位描述" :span="2">
            {{ selectedPosition.description || '无' }}
          </a-descriptions-item>
          <a-descriptions-item label="职位要求" :span="2">
            <div v-if="selectedPosition.requirements" class="requirements-text">
              {{ selectedPosition.requirements }}
            </div>
            <span v-else>无</span>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';
import {
  IdcardOutlined,
  ExportOutlined,
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';
import {
  getPositions,
  getPositionDetail,
  createPosition,
  updatePosition,
  deletePosition,
  getPositionsByDepartment
} from '@/api/organization';
import { getDepartments } from '@/api/organization';

// 响应式数据
const loading = ref(false);
const searchText = ref('');
const statusFilter = ref('');
const levelFilter = ref('');
const departmentFilter = ref('');

const modalVisible = ref(false);
const detailModalVisible = ref(false);
const isEdit = ref(false);
const selectedPosition = ref(null);
const formRef = ref();

// 表单数据
const formData = reactive({
  name: '',
  code: '',
  department: null,
  level: '',
  sort_order: 0,
  status: 'active',
  description: '',
  requirements: ''
});

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入职位名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入职位编码', trigger: 'blur' }],
  department: [{ required: true, message: '请选择所属部门', trigger: 'change' }],
  level: [{ required: true, message: '请选择职位级别', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
};

// 数据
const positionList = ref([]);
const departmentList = ref([]);



// 表格列定义
const columns = [
  {
    title: '职位名称',
    dataIndex: 'name',
    key: 'name',
    width: 200
  },
  {
    title: '职位编码',
    dataIndex: 'code',
    key: 'code',
    width: 120
  },
  {
    title: '所属部门',
    dataIndex: ['department', 'full_name'],
    key: 'department_full_name',
    width: 120
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
    width: 160,
    customRender: ({ text }) => formatDate(text)
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
  return isEdit.value ? '编辑职位' : '新建职位';
});

// 方法
const getLevelColor = (level) => {
  const colors = {
    'junior': 'blue',
    'intermediate': 'orange',
    'senior': 'red',
    'expert': 'purple',
    'manager': 'green',
    'director': 'gold',
    'vp': 'magenta',
    'ceo': 'volcano'
  };
  return colors[level] || 'default';
};

const getLevelText = (level) => {
  const texts = {
    'junior': '初级',
    'intermediate': '中级',
    'senior': '高级',
    'expert': '专家',
    'manager': '管理',
    'director': '总监',
    'vp': '副总',
    'ceo': '总裁'
  };
  return texts[level] || '未知';
};


// 时间格式化函数
const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-';
};

const handleSearch = () => {
  loadPositions();
};

const handleSearchChange = () => {
  if (!searchText.value) {
    loadPositions();
  }
};

const handleFilterChange = () => {
  loadPositions();
};

const resetFilters = () => {
  searchText.value = '';
  statusFilter.value = '';
  levelFilter.value = '';
  departmentFilter.value = '';
  loadPositions();
};

const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  loadPositions();
};

const loadPositions = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize
    };
    
    if (searchText.value) {
      params.search = searchText.value;
    }
    if (statusFilter.value && statusFilter.value !== 'all') {
      params.status = statusFilter.value;
    }
    if (levelFilter.value) {
      params.level = levelFilter.value;
    }
    if (departmentFilter.value) {
      params.department = departmentFilter.value;
    }
    
    const response = await getPositions(params);
    if (response.status == 200){
      const results = response.data.results || [];
      positionList.value = Array.isArray(results) ? results : [];
      pagination.total = response.count || response.total || 0;
      console.log(positionList.value)
    }
  } catch (error) {
    console.error('加载职位列表失败:', error);
    message.error('加载职位列表失败');
  } finally {
    loading.value = false;
  }
};

const showAddModal = () => {
  isEdit.value = false;
  resetForm();
  loadDepartments();
  modalVisible.value = true;
};

const editPosition = (record) => {
  isEdit.value = true;
  Object.assign(formData, {
    id: record.id,
    name: record.name,
    code: record.code,
    department: record.department,
    level: record.level,
    sort_order: record.sort_order,
    status: record.status,
    description: record.description,
    requirements: record.requirements
  });
  modalVisible.value = true;
};

const viewPosition = (record) => {
  selectedPosition.value = record;
  detailModalVisible.value = true;
};

const handleDeletePosition = async (record) => {
  try {
    await deletePosition(record.id);
    message.success('删除成功');
    loadPositions();
  } catch (error) {
    console.error('删除职位失败:', error);
    message.error('删除失败');
  }
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    
    // 准备提交数据，将department转换为department_id
    const submitData = { ...formData };
    if (submitData.department) {
      submitData.department_id = submitData.department;
      delete submitData.department;
    }
    
    if (isEdit.value) {
      await updatePosition(submitData.id, submitData);
      message.success('更新成功');
    } else {
      await createPosition(submitData);
      message.success('创建成功');
    }
    
    modalVisible.value = false;
    loadPositions();
  } catch (error) {
    console.error('保存职位失败:', error);
    
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
        message.error(`职位编码错误: ${errorData.code[0]}`);
        return;
      }
      
      if (errorData.name && Array.isArray(errorData.name)) {
        message.error(`职位名称错误: ${errorData.name[0]}`);
        return;
      }
      
      if (errorData.department && Array.isArray(errorData.department)) {
        message.error(`所属部门错误: ${errorData.department[0]}`);
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
    department: null,
    level: '',
    sort_order: 0,
    status: 'active',
    description: '',
    requirements: ''
  });
  if (formRef.value) {
    formRef.value.resetFields();
  }
};

const exportPositions = () => {
  // 导出功能实现
  message.info('导出功能开发中...');
};

const getCurrentCategoryName = () => {
  return '职位管理';
};

const refreshData = () => {
  loadDepartments();
  loadPositions();
};

// 加载部门列表
const loadDepartments = async () => {
  try {
    const response = await getDepartments();
    console.log(response)
    if (response.status == 200){
      const departments = response.data.results || [];
      departmentList.value = Array.isArray(departments) ? departments : [];
    }
  } catch (error) {
    console.error('加载部门列表失败:', error);
  }
};

// 生命周期
onMounted(() => {
  loadDepartments();
  loadPositions();
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

.positions-content.full-width {
  flex: 1;
  width: 100%;
  height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.positions-content.full-width .ant-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.positions-content.full-width .ant-card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.positions-content.full-width .ant-table-wrapper {
  flex: 1;
  height: 100%;
}

.positions-content.full-width .ant-table {
  height: 100%;
}

.positions-content.full-width .ant-table-tbody {
  height: calc(100% - 55px);
  overflow-y: auto;
}

/* 职位管理页面特有的样式 */
.position-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.position-icon {
  color: #1890ff;
}

.name-text {
  font-weight: 500;
}

.salary-range {
  display: flex;
  align-items: center;
}

.salary-text {
  font-weight: 500;
  color: #52c41a;
}

.no-salary {
  color: #999;
  font-style: italic;
}

.position-detail {
  padding: 16px 0;
}

.requirements-text {
  white-space: pre-wrap;
  line-height: 1.6;
}
</style>