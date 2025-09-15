<template>
  <div class="business-table-container">
    <!-- 表格头部 -->
    <div class="table-header">
      <div class="table-title">
        <h3>
          <AppstoreOutlined />
          业务列表
        </h3>
        <div class="stats-inline">
          <span class="stat-item total">
            总业务 <strong>{{ businessList.length || 0 }}</strong>个
          </span>
        </div>
      </div>
      <div class="table-actions">
        <a-space size="middle">
          <a-button type="primary" @click="showAddModal">
            <template #icon><PlusOutlined /></template>
            新增业务
          </a-button>
          <a-button @click="handleExport">
            <template #icon><ExportOutlined /></template>
            导出数据
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- 查询筛选区域 -->
    <div class="filter-section">
      <div class="filter-header">
        <h4 class="filter-title">
          <SearchOutlined class="title-icon" />
          查询筛选
        </h4>
        <div class="filter-actions">
          <a-space size="middle">
            <a-button type="primary" @click="handleSearch">
              <template #icon><SearchOutlined /></template>
              搜索
            </a-button>
            <a-button @click="handleReset">
              <template #icon><ReloadOutlined /></template>
              重置
            </a-button>
          </a-space>
        </div>
      </div>
      <div class="filter-content">
        <a-row :gutter="[12, 8]">
          <a-col :xl="8" :lg="8" :md="12" :sm="24">
            <div class="filter-item">
              <label class="filter-label">业务名称</label>
              <a-input
                v-model:value="searchForm.name"
                placeholder="输入业务名称"
                allow-clear
              >
                <template #prefix><SearchOutlined /></template>
              </a-input>
            </div>
          </a-col>

          <a-col :xl="8" :lg="8" :md="12" :sm="24">
            <div class="filter-item">
              <label class="filter-label">上线日期</label>
              <a-range-picker
                v-model:value="searchForm.dateRange"
                format="YYYY-MM-DD"
                style="width: 100%"
              />
            </div>
          </a-col>
        </a-row>
      </div>
    </div>

    <!-- 业务列表表格 -->
    <a-table
      :columns="columns"
      :data-source="businessList"
      :pagination="pagination"
      :row-selection="rowSelection"
      :scroll="{ x: 1200 }"
      size="middle"
      @change="handleTableChange"
    >
      <!-- 业务名称列 -->
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'name'">
          <div class="business-name">
            <a-button type="link" @click="viewDetail(record)">
              {{ record.name }}
            </a-button>
          </div>
        </template>

        <!-- 责任部门|责任人列 -->
        <template v-else-if="column.dataIndex === 'responsibility'">
          <div class="responsibility-info">
            <div class="department">
                  <TeamOutlined class="icon" />
                  {{ record.department_name }}
                </div>
                <div class="person">
                  <UserOutlined class="icon" />
                  {{ record.responsible_person }}
                </div>
              </div>
            </template>

            <!-- 上线日期列 -->
            <template v-else-if="column.dataIndex === 'online_date'">
              <div class="date-info">
                <CalendarOutlined class="icon" />
                {{ formatDate(record.online_date) }}
              </div>
            </template>

            <!-- 访问地址列 -->
            <template v-else-if="column.dataIndex === 'access_url'">
              <div class="url-info">
                <a-button
                  v-if="record.access_url"
                  type="link"
                  size="small"
                  @click="openUrl(record.access_url)"
                >
                  <template #icon><LinkOutlined /></template>
                  {{record.access_url}}
                </a-button>
                <span v-else class="no-url">-</span>
              </div>
            </template>

            <!-- 操作列 -->
            <template v-else-if="column.dataIndex === 'action'">
              <div class="action-buttons">
                <a-tooltip title="查看详情">
                  <a-button 
                    type="text" 
                    size="small" 
                    @click="viewDetail(record)"
                    class="action-btn"
                  >
                    <template #icon><EyeOutlined /></template>
                  </a-button>
                </a-tooltip>
                <a-tooltip title="编辑">
                  <a-button 
                    type="text" 
                    size="small" 
                    @click="editBusiness(record)"
                    class="action-btn"
                  >
                    <template #icon><EditOutlined /></template>
                  </a-button>
                </a-tooltip>
                <a-popconfirm
                  title="确定要删除这个业务吗？"
                  @confirm="deleteBusiness(record)"
                  ok-text="确定"
                  cancel-text="取消"
                >
                  <a-tooltip title="删除">
                    <a-button 
                      type="text" 
                      size="small" 
                      danger
                      class="action-btn"
                    >
                      <template #icon><DeleteOutlined /></template>
                    </a-button>
                  </a-tooltip>
                </a-popconfirm>
              </div>
            </template>
          </template>
        </a-table>

    <!-- 新增/编辑业务模态框 -->
    <a-modal
      v-model:open="modalVisible"
      :title="modalTitle"
      width="800px"
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
            <a-form-item label="业务名称" name="name">
              <a-input
                v-model:value="formData.name"
                placeholder="请输入业务名称"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="上线日期" name="online_date">
              <a-date-picker
                v-model:value="formData.online_date"
                style="width: 100%"
                format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="责任人" name="responsible_person">
              <a-select
                v-model:value="formData.responsible_person"
                placeholder="请选择责任人"
                show-search
                :filter-option="filterOption"
              >
                <a-select-option
                  v-for="user in users"
                  :key="user.id"
                  :value="user.name"
                >
                  {{ user.name }} ({{ user.employee_id }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="访问地址" name="access_url">
          <a-input
            v-model:value="formData.access_url"
            placeholder="请输入访问地址，如：https://example.com"
          />
        </a-form-item>

        <a-form-item label="业务描述" name="description">
          <a-textarea
            v-model:value="formData.description"
            placeholder="请输入业务描述"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import dayjs from 'dayjs';
import { businessAPI } from '@/api/businessManagement';
import {
  AppstoreOutlined,
  PlusOutlined,
  ExportOutlined,
  SearchOutlined,
  ReloadOutlined,
  TeamOutlined,
  UserOutlined,
  CalendarOutlined,
  LinkOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue';

const router = useRouter();

// 响应式数据
const businessList = ref([]);
const selectedRowKeys = ref([]);
const modalVisible = ref(false);
const isEdit = ref(false);
const currentRecord = ref(null);
const users = ref([]);
const formRef = ref();

// 搜索表单
const searchForm = reactive({
  name: '',
  dateRange: []
});

// 表单数据
const formData = reactive({
  name: '',
  responsible_person: '',
  online_date: null,
  access_url: '',
  description: '',
  status: 'active'
});

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入业务名称', trigger: 'blur' }],
  responsible_person: [{ required: true, message: '请选择责任人', trigger: 'change' }],
  online_date: [{ required: true, message: '请选择上线日期', trigger: 'change' }],
  access_url: [
    { 
      validator: (rule, value) => {
        if (!value || value.trim() === '') {
          return Promise.resolve();
        }
        const urlPattern = /^(https?:\/\/)([\da-z.-]+\.[a-z.]{2,6}|127.0.0.1|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(:\d+)?([/\w .-]*)*\/?$/;
        if (!urlPattern.test(value)) {
          return Promise.reject(new Error('请输入有效的URL地址'));
        }
        return Promise.resolve();
      },
      trigger: 'blur'
    }
  ]
};

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`
});

// 表格列配置
const columns = [
  {
    title: '业务名称',
    dataIndex: 'name',
    key: 'name',
    width: 200,
    sorter: true
  },
  {
    title: '责任人',
    dataIndex: 'responsible_person',
    key: 'responsible_person',
    width: 120
  },
  {
    title: '上线日期',
    dataIndex: 'online_date',
    key: 'online_date',
    width: 150,
    sorter: true
  },
  {
    title: '访问地址',
    dataIndex: 'access_url',
    key: 'access_url',
    width: 150
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 150,
    sorter: true,
    customRender: ({ text }) => formatDate(text)
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    width: 120,
    fixed: 'right'
  }
];

// 行选择配置
const rowSelection = {
  selectedRowKeys,
  onChange: (keys) => {
    selectedRowKeys.value = keys;
  }
};

// 计算属性
const modalTitle = computed(() => {
  return isEdit.value ? '编辑业务' : '新增业务';
});

// 方法
const fetchBusinessList = async () => {
  try {
    const params = {
      page: pagination.current,
      page_size: pagination.pageSize,
      ...searchForm
    };
    
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = dayjs(searchForm.dateRange[0]).format('YYYY-MM-DD');
      params.end_date = dayjs(searchForm.dateRange[1]).format('YYYY-MM-DD');
    }
    
    const response = await businessAPI.getBusinessList(params);
    businessList.value = response.data.results || [];
    pagination.total = response.data.count || 0;
  } catch (error) {
    message.error('获取业务列表失败');
  }
};



const fetchUsers = async () => {
  try {
    const response = await businessAPI.getUsers();
    // 处理分页数据结构
    users.value = response.data?.results || response.results || response.data || [];
  } catch (error) {
    console.error('获取用户列表失败:', error);
  }
};



const handleSearch = () => {
  pagination.current = 1;
  fetchBusinessList();
};

const handleReset = () => {
  Object.assign(searchForm, {
    name: '',
    dateRange: []
  });
  handleSearch();
};

const handleTableChange = (pag, filters, sorter) => {
  pagination.current = pag.current;
  pagination.pageSize = pag.pageSize;
  fetchBusinessList();
};

const showAddModal = () => {
  isEdit.value = false;
  currentRecord.value = null;
  resetForm();
  modalVisible.value = true;
};

const editBusiness = (record) => {
  isEdit.value = true;
  currentRecord.value = record;
  Object.assign(formData, {
    name: record.name,
    responsible_person: record.responsible_person,
    online_date: record.online_date ? dayjs(record.online_date) : null,
    access_url: record.access_url,
    description: record.description,
    status: record.status || 'active'
  });
  modalVisible.value = true;
};

const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    
    const submitData = {
      ...formData,
      online_date: formData.online_date ? dayjs(formData.online_date).format('YYYY-MM-DD') : null,
      access_url: formData.access_url && formData.access_url.trim() ? formData.access_url.trim() : null
    };
    
    if (isEdit.value) {
      await businessAPI.updateBusiness(currentRecord.value.id, submitData);
      message.success('业务更新成功');
    } else {
      await businessAPI.createBusiness(submitData);
      message.success('业务创建成功');
    }
    
    modalVisible.value = false;
    fetchBusinessList();
  } catch (error) {
    if (error.errorFields) {
      message.error('请检查表单输入');
    } else {
      message.error(isEdit.value ? '业务更新失败' : '业务创建失败');
    }
  }
};

const handleCancel = () => {
  modalVisible.value = false;
  resetForm();
};

const resetForm = () => {
  Object.assign(formData, {
    name: '',
    responsible_person: '',
    online_date: null,
    access_url: '',
    description: '',
    status: 'active'
  });
  formRef.value?.resetFields();
};

const deleteBusiness = async (record) => {
  try {
    await businessAPI.deleteBusiness(record.id);
    message.success('删除成功');
    fetchBusinessList();
  } catch (error) {
    message.error('删除失败');
  }
};

const viewDetail = (record) => {
  router.push({
    name: 'businessDetail',
    params: { id: record.id }
  });
};

const openUrl = (url) => {
  if (url) {
    window.open(url, '_blank');
  }
};

const handleExport = async () => {
  try {
    const response = await businessAPI.exportBusiness(searchForm);
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `业务列表_${dayjs().format('YYYY-MM-DD')}.xlsx`;
    link.click();
    window.URL.revokeObjectURL(url);
    message.success('导出成功');
  } catch (error) {
    message.error('导出失败');
  }
};

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD') : '-';
};

const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0;
};

// 组件挂载时获取数据
onMounted(() => {
  fetchBusinessList();
  fetchUsers();
});

</script>

<style scoped>
.business-table-container {
  min-height: 100vh;
}

/* 表格头部样式 */
.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  margin-bottom: 0;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.table-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-inline {
  display: flex;
  gap: 16px;
}

.stat-item {
  font-size: 13px;
  color: #8c8c8c;
}

.stat-item strong {
  color: #1890ff;
}

.table-actions {
  display: flex;
  align-items: center;
}

/* 筛选区域样式 */
.filter-section {
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e8e8e8;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.filter-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #262626;
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  color: #1890ff;
}

.filter-actions {
  display: flex;
  align-items: center;
}

.filter-content {
  margin: 0;
}

.filter-item {
  margin-bottom: 0;
}

.filter-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #262626;
  font-size: 13px;
}

/* 业务信息样式 */
.business-name {
  font-weight: 500;
}

.responsibility-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.department,
.person {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.department {
  color: #1890ff;
}

.person {
  color: #52c41a;
}

.icon {
  margin-right: 4px;
  font-size: 12px;
}

.date-info {
  display: flex;
  align-items: center;
  color: #666;
}

.url-info {
  text-align: center;
}

.no-url {
  color: #ccc;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  gap: 4px;
  align-items: center;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #f5f5f5;
  transform: scale(1.1);
}

.action-btn.danger:hover {
  background-color: #fff2f0;
  color: #ff4d4f;
}

.action-btn .anticon {
  font-size: 14px;
}

/* 表格样式优化 */
:deep(.ant-table) {
  font-size: 13px;
}

:deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
  color: #262626;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #f5f5f5;
}

:deep(.ant-table-row-selected) {
  background: #e6f7ff;
}

:deep(.ant-table-row-selected:hover > td) {
  background: #bae7ff;
}

:deep(.ant-pagination) {
  margin: 16px 0;
  text-align: right;
}

:deep(.ant-tag) {
  margin: 0;
  border-radius: 4px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .business-table-container {
    padding: 12px;
  }
  
  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .table-title {
    justify-content: center;
  }
  
  .responsibility-info {
    font-size: 11px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
}
</style>