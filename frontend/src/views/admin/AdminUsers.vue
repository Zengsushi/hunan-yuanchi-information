<template>
  <div class="admin-users admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <TeamOutlined />
          用户管理
        </h1>
        <p class="page-description">管理系统用户和权限</p>
      </div>
      <div class="header-actions">
        <a-space>
          <a-tooltip title="导出用户列表为Excel文件" placement="bottom">
            <a-button @click="exportUsers">
              <ExportOutlined />
              导出用户
            </a-button>
          </a-tooltip>
          <a-tooltip title="创建新的用户账户" placement="bottom">
            <a-button type="primary" @click="showAddModal">
              <PlusOutlined />
              新建用户
            </a-button>
          </a-tooltip>
        </a-space>
      </div>
    </div>

    <!-- 用户管理布局 -->
    <div class="users-layout admin-layout">
      <!-- 左侧菜单 -->
      <div class="users-menu admin-menu">
        <div class="menu-title">用户分类</div>
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
          <div class="stats-title">用户统计</div>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">总用户数</span>
              <span class="stat-value">{{ userStats.total }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">活跃用户</span>
              <span class="stat-value">{{ userStats.active }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">管理员</span>
              <span class="stat-value">{{ userStats.admin }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="users-content admin-content">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
            <a-space>
              <a-input-search
                v-model:value="searchText"
                placeholder="搜索用户..."
                style="width: 200px"
                @search="handleSearch"
                @change="handleSearch"
              />
              <a-select
                v-model:value="roleFilter"
                placeholder="角色筛选"
                style="width: 120px"
                @change="handleRoleFilter"
              >
                <a-select-option value="">全部角色</a-select-option>
                <a-select-option value="admin">管理员</a-select-option>
                <a-select-option value="operator">操作员</a-select-option>
                <a-select-option value="viewer">观察者</a-select-option>
              </a-select>
              <a-tooltip title="刷新用户列表数据" placement="bottom">
                <a-button @click="refreshData">
                  <ReloadOutlined />
                </a-button>
              </a-tooltip>
            </a-space>
          </template>

          <a-table
            :columns="tableColumns"
            :data-source="filteredUsers"
            :pagination="pagination"
            :loading="loading"
            :row-selection="rowSelection"
            row-key="id"
            size="middle"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'avatar'">
                <a-avatar :style="{ background: getAvatarColor(record.role) }">
                  {{ record.realName?.charAt(0) || record.username?.charAt(0) }}
                </a-avatar>
              </template>
              <template v-else-if="column.key === 'role'">
                <a-tag :color="getRoleColor(record.role)">
                  {{ getRoleText(record.role) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'onlineStatus'">
                <a-space>
                  <a-badge 
                    :status="record.isOnline ? 'processing' : 'default'" 
                    :text="record.isOnline ? '在线' : '离线'"
                  />
                  <a-tooltip v-if="record.onlineSessions && record.onlineSessions.length > 0" placement="top">
                    <template #title>
                      <div>
                        <div v-for="session in record.onlineSessions" :key="session.id">
                          IP: {{ session.ip_address }}<br>
                          设备: {{ session.device_info }}<br>
                          登录时间: {{ formatDate(session.login_time) }}
                        </div>
                      </div>
                    </template>
                  </a-tooltip>
                </a-space>
              </template>
              <template v-else-if="column.key === 'status'">
                <a-tag :color="record.isActive ? 'green' : 'red'">
                  {{ record.isActive ? '启用' : '禁用' }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'lastLogin'">      
                <span v-if="record.lastLogin">
                  {{ formatDate(record.lastLogin) }}
                </span>
                <span v-else class="text-gray">从未登录</span>
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-space>
                  <a-tooltip title="编辑用户信息" placement="top">
                    <a-button type="link" size="small" @click="editUser(record)">
                      <EditOutlined />
                    </a-button>
                  </a-tooltip>
                  <a-tooltip :title="record.isActive ? '禁用此用户' : '启用此用户'" placement="top">
                    <a-button 
                      type="link" 
                      size="small" 
                      @click="toggleUserStatus(record)"
                    >
                      <CheckCircleOutlined v-if="!record.isActive" />
                      <StopOutlined v-else />
                    </a-button>
                  </a-tooltip>
                  <a-tooltip v-if="record.isOnline && record.username !== currentUsername" title="踢出用户（关闭所有会话）" placement="top">
                    <a-popconfirm
                      :title="`确定要踢出用户 '${record.username}' 吗？这将关闭其所有在线会话。`"
                      @confirm="kickOutUser(record)"
                      placement="topRight"
                    >
                      <a-button type="link" size="small" danger>
                        <LogoutOutlined />
                      </a-button>
                    </a-popconfirm>
                  </a-tooltip>
                  <a-tooltip title="重置用户密码" placement="top">
                    <a-button 
                      type="link" 
                      size="small" 
                      @click="resetPassword(record)"
                    >
                      <KeyOutlined />
                    </a-button>
                  </a-tooltip>
                  <a-popconfirm
                    :title="getDeleteConfirmTitle(record)"
                    @confirm="deleteUser(record)"
                    placement="topRight"
                    :ok-type="record.username === currentUsername ? 'danger' : 'primary'"
                  >
                    <a-tooltip title="删除此用户" placement="top">
                      <a-button type="link" size="small" danger>
                        <DeleteOutlined />
                      </a-button>
                    </a-tooltip>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>

          <!-- 批量操作 -->
          <div v-if="selectedRowKeys.length > 0" class="batch-actions">
            <a-space>
              <span>已选择 {{ selectedRowKeys.length }} 项</span>
              <a-tooltip title="批量启用选中的用户" placement="top">
                <a-button @click="batchEnable">
                  <CheckOutlined />
                  批量启用
                </a-button>
              </a-tooltip>
              <a-tooltip title="批量禁用选中的用户" placement="top">
                <a-button @click="batchDisable">
                  <CloseOutlined />
                  批量禁用
                </a-button>
              </a-tooltip>
              <a-popconfirm
                :title="getBatchDeleteConfirmTitle()"
                @confirm="batchDelete"
                placement="topRight"
                :ok-type="getBatchDeleteConfirmTitle().includes('警告') ? 'danger' : 'primary'"
              >
                <a-tooltip title="批量删除选中的用户" placement="top">
                  <a-button danger>
                    <DeleteOutlined />
                    批量删除
                  </a-button>
                </a-tooltip>
              </a-popconfirm>
            </a-space>
          </div>
        </a-card>
      </div>
    </div>

    <!-- 添加/编辑用户弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      :title="isEditing ? '编辑用户' : '新建用户'"
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
            <a-form-item label="用户名" name="username">
              <a-input 
                v-model:value="formData.username" 
                placeholder="输入用户名"
                :disabled="isEditing"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="真实姓名" name="realName">
              <a-input v-model:value="formData.realName" placeholder="输入真实姓名" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="邮箱" name="email">
              <a-input v-model:value="formData.email" placeholder="输入邮箱地址" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="电话" name="phone">
              <a-input v-model:value="formData.phone" placeholder="输入电话号码" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="角色" name="role">
              <a-select v-model:value="formData.role" placeholder="选择用户角色">
                <a-select-option value="admin">管理员</a-select-option>
                <a-select-option value="operator">操作员</a-select-option>
                <a-select-option value="viewer">观察者</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="部门" name="department">
              <a-input v-model:value="formData.department" placeholder="输入所属部门" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item v-if="!isEditing" label="密码" name="password">
          <a-input-password v-model:value="formData.password" placeholder="输入密码" />
        </a-form-item>

        <a-form-item label="状态" name="isActive">
          <a-switch v-model:checked="formData.isActive" />
          <span class="switch-description">{{ formData.isActive ? '启用' : '禁用' }}</span>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { message } from 'ant-design-vue';
import { userAPI } from '@/api/users';
import { dictionaryAPI } from '@/api/index';
import {
  TeamOutlined,
  PlusOutlined,
  ExportOutlined,
  ReloadOutlined,
  UserOutlined,
  CrownOutlined,
  SafetyOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined,
  StopOutlined,
  CheckOutlined,
  CloseOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue';

// 响应式数据
const loading = ref(false);
const modalVisible = ref(false);
const isEditing = ref(false);
const searchText = ref('');
const roleFilter = ref('');
const activeCategory = ref('all');
const selectedRowKeys = ref([]);

// 表单数据
const formRef = ref();
const formData = ref({
  username: '',
  realName: '',
  email: '',
  phone: '',
  role: 'viewer',
  department: '',
  password: '',
  isActive: true
});

// 用户数据
const users = ref([]);
const userStats = ref({
  total: 0,
  active: 0,
  admin: 0
});

// 分类列表（从字典动态获取）
const categoryList = ref([]);

// 获取用户分类字典数据
const fetchUserCategories = async () => {
  try {
    const response = await dictionaryAPI.getDictionaryByCategory('user_category', {
      status: 'active',
      simple: 'true'  // 获取简化数据格式
    });
    
    if (response.data && response.data.code === 200) {
      const dictionary = response.data.data || [];
      
      // 转换字典数据为分类格式
      const dictionaryCategories = dictionary
        .sort((a, b) => (b.priority || 0) - (a.priority || 0))
        .map(item => {
          // 解析config中的配置
          let config = {};
          try {
            config = item.config ? JSON.parse(item.config) : {};
          } catch (e) {
            console.warn('解析字典配置失败:', item.config);
          }
          
          return {
            key: item.key,
            name: item.label,
            icon: config.icon || 'UserOutlined',
            count: 0
          };
        });
      
      // 始终包含默认分类
      const defaultCategories = [
        {
          key: 'all',
          name: '全部用户',
          icon: 'TeamOutlined',
          count: 0
        },
        {
          key: 'active',
          name: '活跃用户',
          icon: 'CheckCircleOutlined',
          count: 0
        },
        {
          key: 'inactive',
          name: '禁用用户',
          icon: 'CloseCircleOutlined',
          count: 0
        }
      ];
      
      // 合并默认分类和字典分类
      categoryList.value = [...defaultCategories, ...dictionaryCategories];
      
      console.log('用户分类字典加载成功:', categoryList.value);
    } else {
      console.warn('获取用户分类字典失败，使用默认分类');
      setDefaultCategories();
    }
  } catch (error) {
    console.error('获取用户分类字典失败:', error);
    // 如果获取字典失败，使用默认分类
    setDefaultCategories();
  }
};

// 设置默认分类（作为备用方案）
const setDefaultCategories = () => {
  categoryList.value = [
    {
      key: 'all',
      name: '全部用户',
      icon: 'TeamOutlined',
      count: 0
    },
    {
      key: 'admin',
      name: '管理员',
      icon: 'CrownOutlined',
      count: 0
    },
    {
      key: 'operator',
      name: '操作员',
      icon: 'SafetyOutlined',
      count: 0
    },
    {
      key: 'viewer',
      name: '观察者',
      icon: 'EyeOutlined',
      count: 0
    },
    {
      key: 'active',
      name: '活跃用户',
      icon: 'CheckCircleOutlined',
      count: 0
    },
    {
      key: 'inactive',
      name: '禁用用户',
      icon: 'CloseCircleOutlined',
      count: 0
    }
  ];
};

// 表格列配置
const tableColumns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '姓名',
    dataIndex: 'realName',
    key: 'realName'
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email'
  },
  {
    title: '角色',
    key: 'role',
    width: 100,
    filters: [
      { text: '管理员', value: 'admin' },
      { text: '操作员', value: 'operator' },
      { text: '观察者', value: 'viewer' }
    ]
  },
  {
    title: '部门',
    dataIndex: 'department',
    key: 'department'
  },
  {
    title: '在线状态',
    key: 'onlineStatus',
    width: 100,
    filters: [
      { text: '在线', value: true },
      { text: '离线', value: false }
    ]
  },
  {
    title: '状态',
    key: 'status',
    width: 80,
    filters: [
      { text: '启用', value: true },
      { text: '禁用', value: false }
    ]
  },
  // {
  //   title: '最后登录',
  //   key: 'lastLogin',
  //   width: 150,
  // },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right'
  }
];

// 分页配置
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条/共 ${total} 条`,
  onChange: (page, pageSize) => {
    pagination.value.current = page;
    pagination.value.pageSize = pageSize;
    fetchUsers();
  }
});

// 行选择配置
const rowSelection = {
  selectedRowKeys,
  onChange: (keys) => {
    selectedRowKeys.value = keys;
  }
};

// 表单验证规则
const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ]
};

// 计算属性
const filteredUsers = computed(() => {
  // 确保users.value是数组
  if (!Array.isArray(users.value)) {
    console.warn('users.value is not an array in filteredUsers:', users.value);
    return [];
  }
  
  let result = users.value;
  
  // 分类筛选
  if (activeCategory.value !== 'all') {
    if (activeCategory.value === 'active') {
      result = result.filter(user => user.isActive);
    } else if (activeCategory.value === 'inactive') {
      result = result.filter(user => !user.isActive);
    } else {
      result = result.filter(user => user.role === activeCategory.value);
    }
  }
  
  // 角色筛选
  if (roleFilter.value) {
    result = result.filter(user => user.role === roleFilter.value);
  }
  
  // 搜索筛选
  if (searchText.value) {
    const searchLower = searchText.value.toLowerCase();
    result = result.filter(user => 
      user.username?.toLowerCase().includes(searchLower) ||
      user.realName?.toLowerCase().includes(searchLower) ||
      user.email?.toLowerCase().includes(searchLower) ||
      user.department?.toLowerCase().includes(searchLower)
    );
  }
  
  return result;
});

// 获取当前分类名称
const getCurrentCategoryName = () => {
  const category = categoryList.value.find(cat => cat.key === activeCategory.value);
  return category ? category.name : '全部用户';
};

// 获取头像颜色
const getAvatarColor = (role) => {
  const colors = {
    admin: '#faad14',
    operator: '#1890ff', 
    viewer: '#52c41a'
  };
  return colors[role] || '#d9d9d9';
};

// 获取角色颜色
const getRoleColor = (role) => {
  const colors = {
    admin: 'gold',
    operator: 'blue',
    viewer: 'green'
  };
  return colors[role] || 'default';
};

// 获取角色文本
const getRoleText = (role) => {
  const texts = {
    admin: '管理员',
    operator: '操作员',
    viewer: '观察者'
  };
  return texts[role] || role;
};

// 获取当前用户名
const currentUsername = computed(() => {
  return localStorage.getItem('username') || '';
});

// 获取删除确认标题
const getDeleteConfirmTitle = (record) => {
  if (record.username === currentUsername.value) {
    return '警告：您将删除自己的账户！删除后您将被自动退出登录，确定继续吗？';
  }
  return `确定要删除用户 "${record.username}" 吗？`;
};

// 获取批量删除确认标题
const getBatchDeleteConfirmTitle = () => {
  // 确保users.value是数组
  if (!Array.isArray(users.value)) {
    console.warn('users.value is not an array:', users.value);
    return `确定要批量删除选中的 ${selectedRowKeys.value.length} 个用户吗？`;
  }
  
  const selectedUsers = users.value.filter(user => selectedRowKeys.value.includes(user.id));
  const isCurrentUserIncluded = selectedUsers.some(user => user.username === currentUsername.value);
  
  if (isCurrentUserIncluded) {
    return '警告：您在批量删除中包含了自己的账户！删除后您将被自动退出登录，确定继续吗？';
  }
  return `确定要批量删除选中的 ${selectedRowKeys.value.length} 个用户吗？`;
};

// 格式化日期
const formatDate = (date) => {
  if (!date) return '';
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 更新统计数据
const updateStats = () => {
  // 确保users.value是数组
  if (!Array.isArray(users.value)) {
    console.warn('users.value is not an array in updateStats:', users.value);
    users.value = []; // 重置为空数组
  }
  
  const stats = {
    total: users.value.length,
    active: users.value.filter(user => user.isActive).length,
    admin: users.value.filter(user => user.role === 'admin').length
  };
  
  userStats.value = stats;
  
  // 更新分类计数（支持动态分类）
  categoryList.value.forEach(category => {
    switch (category.key) {
      case 'all':
        category.count = stats.total;
        break;
      case 'active':
        category.count = stats.active;
        break;
      case 'inactive':
        category.count = stats.total - stats.active;
        break;
      case 'admin':
        category.count = users.value.filter(user => user.role === 'admin').length;
        break;
      case 'operator':
        category.count = users.value.filter(user => user.role === 'operator').length;
        break;
      case 'viewer':
        category.count = users.value.filter(user => user.role === 'viewer').length;
        break;
      default:
        // 对于其他动态分类，根据角色进行计数
        if (category.key === 'admin' || category.key === 'operator' || category.key === 'viewer') {
          category.count = users.value.filter(user => user.role === category.key).length;
        } else {
          // 其他类型的分类可以根据需要扩展
          category.count = 0;
        }
        break;
    }
  });
};

// 获取用户列表
const fetchUsers = async () => {
  try {
    loading.value = true;
    const params = {
      page: pagination.value.current,
      pageSize: pagination.value.pageSize,
      search: searchText.value,
      role: roleFilter.value
    };
    
    // 移除空参数
    Object.keys(params).forEach(key => {
      if (!params[key]) {
        delete params[key];
      }
    });
    
    const response = await userAPI.getUserList(params);
    
    if (response.data && response.data.code === 200) {
      const data = response.data.data;
      // 处理用户数据，统一字段格式
      users.value = (data.list || data.results || []).map(user => ({
        id: user.id,
        username: user.username,
        realName: user.profile?.real_name || user.real_name || user.first_name + ' ' + user.last_name,
        email: user.email,
        phone: user.profile?.phone || user.phone || '',
        role: user.profile?.role || 'viewer',
        department: user.profile?.department || '',
        isActive: user.is_active !== undefined ? user.is_active : true,
        lastLogin: user.last_login,
        createdAt: user.date_joined || user.created_at,
        // 新增在线状态相关字段
        isOnline: user.is_online || false,
        onlineSessions: user.online_sessions || []
      }));
      
      pagination.value.total = data.total || data.count || users.value.length;
      
      // 获取用户统计
      await fetchUserStats();
      updateStats();
    } else {
      console.error('API响应格式错误:', response.data);
      throw new Error('API响应格式错误');
    }
  } catch (error) {
    console.error('获取用户列表失败:', error);
    
    // 对于401错误，提供更友好的提示
    if (error.response?.status === 401) {
      message.error({
        content: '身份认证已过期，请重新登录',
        duration: 5
      });
      
      // 清除本地状态并跳转到登录页
      setTimeout(() => {
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
        localStorage.removeItem('isLoggedIn');
        localStorage.removeItem('userType');
        localStorage.removeItem('username');
        window.location.href = '/#/login';
      }, 2000);
    } else {
      // 其他错误的处理
      const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message;
      message.error(`获取用户列表失败: ${errorMsg}`);
    }
    
    // 如果API失败，使用空数组而不是模拟数据
    users.value = [];
    pagination.value.total = 0;
    updateStats();
  } finally {
    loading.value = false;
  }
};

// 获取用户统计数据
const fetchUserStats = async () => {
  try {
    const response = await userAPI.getUserStats();
    if (response.data && response.data.code === 200) {
      const stats = response.data.data;
      userStats.value = {
        total: stats.total || 0,
        active: stats.active || 0,
        admin: stats.admin || 0
      };
    }
  } catch (error) {
    console.error('获取用户统计失败:', error);
    // 统计失败时使用本地计算
    userStats.value = {
      total: users.value.length,
      active: users.value.filter(user => user.isActive).length,
      admin: users.value.filter(user => user.role === 'admin').length
    };
  }
};


// 分类切换
const handleCategoryChange = (key) => {
  activeCategory.value = key;
  selectedRowKeys.value = [];
  pagination.value.current = 1; // 重置页码
  // 分类筛选在前端处理，不需要重新获取数据
};

// 搜索处理
const handleSearch = () => {
  selectedRowKeys.value = [];
  pagination.value.current = 1; // 重置页码
  fetchUsers(); // 重新获取数据
};

// 角色筛选
const handleRoleFilter = () => {
  selectedRowKeys.value = [];
  pagination.value.current = 1; // 重置页码
  fetchUsers(); // 重新获取数据
};

// 刷新数据
const refreshData = () => {
  fetchUsers();
  message.success('数据刷新成功');
};

// 显示新建用户弹窗
const showAddModal = () => {
  isEditing.value = false;
  formData.value = {
    username: '',
    realName: '',
    email: '',
    phone: '',
    role: 'viewer',
    department: '',
    password: '',
    isActive: true
  };
  modalVisible.value = true;
};

// 编辑用户
const editUser = (record) => {
  isEditing.value = true;
  formData.value = {
    id: record.id,
    username: record.username,
    realName: record.realName,
    email: record.email,
    phone: record.phone,
    role: record.role,
    department: record.department,
    isActive: record.isActive
  };
  modalVisible.value = true;
};

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate();
    loading.value = true;
    
    // 准备API请求数据
    const apiData = {
      username: formData.value.username,
      email: formData.value.email,
      real_name: formData.value.realName,
      phone: formData.value.phone,
      role: formData.value.role,
      department: formData.value.department,
      is_active: formData.value.isActive
    };
    
    if (!isEditing.value) {
      apiData.password = formData.value.password;
    }
    
    let response;
    if (isEditing.value) {
      // 编辑用户
      response = await userAPI.updateUser(formData.value.id, apiData);
    } else {
      // 新建用户
      response = await userAPI.createUser(apiData);
    }
    
    if (response.data && response.data.code === 200) {
      message.success(isEditing.value ? '用户更新成功' : '用户创建成功');
      modalVisible.value = false;
      // 重新获取数据
      await fetchUsers();
    } else {
      throw new Error(response.data?.error || response.data?.message || '操作失败');
    }
  } catch (error) {
    console.error('用户操作失败:', error);
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '操作失败，请重试';
    message.error(errorMsg);
  } finally {
    loading.value = false;
  }
};

// 取消操作
const handleCancel = () => {
  modalVisible.value = false;
  formRef.value?.resetFields();
};

// 切换用户状态
const toggleUserStatus = async (record) => {
  try {
    loading.value = true;
    const response = await userAPI.toggleUserStatus(record.id, !record.isActive);
    
    if (response.data && response.data.code === 200) {
      message.success(`用户${!record.isActive ? '启用' : '禁用'}成功`);
      // 重新获取数据
      await fetchUsers();
    } else {
      throw new Error(response.data?.error || response.data?.message || '操作失败');
    }
  } catch (error) {
    console.error('切换用户状态失败:', error);
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '操作失败，请重试';
    message.error(errorMsg);
  } finally {
    loading.value = false;
  }
};

// 重置密码
const resetPassword = async (record) => {
  try {
    loading.value = true;
    const response = await userAPI.resetUserPassword(record.id);
    
    if (response.data && response.data.code === 200) {
      message.success('密码重置成功,新密码为: 123456');
    } else {
      throw new Error(response.data?.error || response.data?.message || '重置密码失败');
    }
  } catch (error) {
    console.error('重置密码失败:', error);
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '重置密码失败，请重试';
    message.error(errorMsg);
  } finally {
    loading.value = false;
  }
};

// 踢出用户
const kickOutUser = async (record) => {
  try {
    loading.value = true;
    const response = await userAPI.kickOutUser(record.id);
    
    if (response.data && response.data.code === 200) {
      const data = response.data.data;
      message.success({
        content: `成功踢出用户 ${data.username}，关闭了 ${data.kicked_sessions} 个会话`,
        duration: 3
      });
      
      // 重新获取数据以更新在线状态
      await fetchUsers();
    } else {
      throw new Error(response.data?.error || response.data?.message || '踢出用户失败');
    }
  } catch (error) {
    console.error('踢出用户失败:', error);
    
    if (error.response?.status === 403) {
      message.error('权限不足，只有管理员才能踢出用户');
    } else {
      const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '踢出用户失败，请重试';
      message.error(errorMsg);
    }
  } finally {
    loading.value = false;
  }
};

// 删除用户
const deleteUser = async (record) => {
  try {
    loading.value = true;
    
    // 检查是否删除当前登录用户
    const currentUsername = localStorage.getItem('username');
    const isCurrentUser = record.username === currentUsername;
    
    const response = await userAPI.deleteUser(record.id);
    
    if (response.data && response.data.code === 200) {
      message.success('用户删除成功');
      
      // 如果删除的是当前用户，提示用户并重定向到登录页
      if (isCurrentUser) {
        message.warning({
          content: '您删除了自己的账户，系统将在3秒后自动退出登录',
          duration: 3
        });
        
        // 3秒后清除登录状态并跳转到登录页
        setTimeout(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('userInfo');
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('userType');
          localStorage.removeItem('username');
          window.location.href = '/#/login';
        }, 3000);
        
        return; // 不执行后续的fetchUsers，避免401错误
      }
      
      // 重新获取数据（只有非当前用户时才执行）
      await fetchUsers();
    } else {
      throw new Error(response.data?.error || response.data?.message || '删除失败');
    }
  } catch (error) {
    console.error('删除用户失败:', error);
    
    // 如果是401错误且删除的是当前用户，给出特殊提示
    if (error.response?.status === 401) {
      const currentUsername = localStorage.getItem('username');
      const isCurrentUser = record.username === currentUsername;
      
      if (isCurrentUser) {
        message.success({
          content: '用户删除成功，您的账户已被删除，系统将自动退出登录',
          duration: 3
        });
        
        setTimeout(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('userInfo');
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('userType');
          localStorage.removeItem('username');
          window.location.href = '/#/login';
        }, 3000);
        
        return;
      } else {
        message.error('认证失败，请重新登录');
      }
    } else {
      const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '删除失败，请重试';
      message.error(errorMsg);
    }
  } finally {
    loading.value = false;
  }
};

// 批量启用
const batchEnable = async () => {
  try {
    loading.value = true;
    
    // 批量操作需要逐个调用API
    const promises = selectedRowKeys.value.map(id => {
      const user = users.value.find(u => u.id === id);
      if (user && !user.isActive) {
        return userAPI.toggleUserStatus(id, true);
      }
      return Promise.resolve();
    });
    
    await Promise.all(promises);
    
    selectedRowKeys.value = [];
    message.success('批量启用成功');
    // 重新获取数据
    await fetchUsers();
  } catch (error) {
    console.error('批量启用失败:', error);
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '批量启用失败，请重试';
    message.error(errorMsg);
  } finally {
    loading.value = false;
  }
};

// 批量禁用
const batchDisable = async () => {
  try {
    loading.value = true;
    
    // 批量操作需要逐个调用API
    const promises = selectedRowKeys.value.map(id => {
      const user = users.value.find(u => u.id === id);
      if (user && user.isActive) {
        return userAPI.toggleUserStatus(id, false);
      }
      return Promise.resolve();
    });
    
    await Promise.all(promises);
    
    selectedRowKeys.value = [];
    message.success('批量禁用成功');
    // 重新获取数据
    await fetchUsers();
  } catch (error) {
    console.error('批量禁用失败:', error);
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '批量禁用失败，请重试';
    message.error(errorMsg);
  } finally {
    loading.value = false;
  }
};

// 批量删除
const batchDelete = async () => {
  try {
    loading.value = true;
    
    // 检查是否包含当前登录用户
    const currentUsername = localStorage.getItem('username');
    
    // 确保users.value是数组
    if (!Array.isArray(users.value)) {
      console.warn('users.value is not an array in batchDelete:', users.value);
      message.error('数据异常，请刷新页面后重试');
      return;
    }
    
    const selectedUsers = users.value.filter(user => selectedRowKeys.value.includes(user.id));
    const isCurrentUserIncluded = selectedUsers.some(user => user.username === currentUsername);
    
    const response = await userAPI.batchDeleteUsers(selectedRowKeys.value);
    
    if (response.data && response.data.code === 200) {
      selectedRowKeys.value = [];
      message.success('批量删除成功');
      
      // 如果删除的用户中包含当前用户，提示用户并重定向到登录页
      if (isCurrentUserIncluded) {
        message.warning({
          content: '您在批量删除中包含了自己的账户，系统将在3秒后自动退出登录',
          duration: 3
        });
        
        // 3秒后清除登录状态并跳转到登录页
        setTimeout(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('userInfo');
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('userType');
          localStorage.removeItem('username');
          window.location.href = '/#/login';
        }, 3000);
        
        return; // 不执行后续的fetchUsers，避免401错误
      }
      
      // 重新获取数据（只有非当前用户时才执行）
      await fetchUsers();
    } else {
      throw new Error(response.data?.error || response.data?.message || '批量删除失败');
    }
  } catch (error) {
    console.error('批量删除失败:', error);
    
    // 如果是401错误，可能是删除了当前用户后的后续请求
    if (error.response?.status === 401) {
      const currentUsername = localStorage.getItem('username');
      
      // 确保users.value是数组
      if (!Array.isArray(users.value)) {
        console.warn('users.value is not an array in error handler:', users.value);
        message.error('认证失败，请重新登录');
        setTimeout(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('userInfo');
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('userType');
          localStorage.removeItem('username');
          window.location.href = '/#/login';
        }, 2000);
        return;
      }
      
      const selectedUsers = users.value.filter(user => selectedRowKeys.value.includes(user.id));
      const isCurrentUserIncluded = selectedUsers.some(user => user.username === currentUsername);
      
      if (isCurrentUserIncluded) {
        message.success({
          content: '批量删除成功，您的账户已被删除，系统将自动退出登录',
          duration: 3
        });
        
        setTimeout(() => {
          localStorage.removeItem('token');
          localStorage.removeItem('userInfo');
          localStorage.removeItem('isLoggedIn');
          localStorage.removeItem('userType');
          localStorage.removeItem('username');
          window.location.href = '/#/login';
        }, 3000);
        
        return;
      } else {
        message.error('认证失败，请重新登录');
      }
    } else {
      const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '批量删除失败，请重试';
      message.error(errorMsg);
    }
  } finally {
    loading.value = false;
  }
};

// 导出用户
const exportUsers = async () => {
  try {
    loading.value = true;
    const response = await userAPI.exportUsers();
    
    if (response.data) {
      // 创建下载链接
      const blob = new Blob([response.data], { 
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `用户列表_${new Date().toISOString().slice(0, 10)}.xlsx`;
      link.click();
      window.URL.revokeObjectURL(url);
      
      message.success('用户列表导出成功');
    } else {
      throw new Error('导出数据为空');
    }
  } catch (error) {
    console.error('导出用户列表失败:', error);
    const errorMsg = error.response?.data?.error || error.response?.data?.message || error.message || '导出失败，请重试';
    message.error(errorMsg);
  } finally {
    loading.value = false;
  }
};

// 组件挂载
onMounted(async () => {
  // 同时获取用户分类和用户数据
  await Promise.all([
    fetchUserCategories(),
    fetchUsers()
  ]);
});

// 监听搜索条件变化，实现实时搜索
watch([searchText, roleFilter], () => {
  // 使用防抖避免频繁请求
  clearTimeout(searchTimeout.value);
  searchTimeout.value = setTimeout(() => {
    pagination.value.current = 1; // 重置页码
    fetchUsers();
  }, 500);
});

// 搜索防抖定时器
const searchTimeout = ref(null);
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 用户管理页面特有的样式 */
/* 所有通用样式已在 admin-common.css 中定义 */
</style>