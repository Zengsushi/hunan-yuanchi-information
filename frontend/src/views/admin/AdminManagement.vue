<template>
  <div class="admin-management">
    <div class="page-header">
      <h2 class="page-title">
        <CrownOutlined class="title-icon" />
        管理员控制面板
      </h2>
      <p class="page-desc">管理系统用户权限、角色分配和系统设置</p>
    </div>

    <div class="admin-content">
      <!-- 用户管理 -->
      <a-card class="management-card" title="用户管理">
        <template #extra>
          <a-button type="primary" @click="showAddUserModal">
            <UserAddOutlined />
            添加用户
          </a-button>
        </template>
        
        <a-table 
          :columns="userColumns" 
          :data-source="users" 
          :pagination="{ pageSize: 10 }"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'role'">
              <a-tag :color="getRoleColor(record.role)">
                {{ getRoleText(record.role) }}
              </a-tag>
            </template>
            <template v-else-if="column.key === 'status'">
              <a-switch 
                v-model:checked="record.active" 
                :checked-children="'启用'" 
                :un-checked-children="'禁用'"
                @change="toggleUserStatus(record)"
              />
            </template>
            <template v-else-if="column.key === 'action'">
              <a-space>
                <a-button type="text" size="small" @click="editUser(record)">
                  <EditOutlined />
                </a-button>
                <a-button type="text" size="small" @click="resetPassword(record)">
                  <KeyOutlined />
                </a-button>
                <a-popconfirm
                  title="确定要删除这个用户吗？"
                  @confirm="deleteUser(record)"
                >
                  <a-button type="text" size="small" danger>
                    <DeleteOutlined />
                  </a-button>
                </a-popconfirm>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>

      <!-- 角色权限管理 -->
      <a-card class="management-card" title="角色权限管理">
        <template #extra>
          <a-button type="primary" @click="showAddRoleModal">
            <TeamOutlined />
            添加角色
          </a-button>
        </template>
        
        <div class="role-management">
          <div class="role-list">
            <div 
              v-for="role in roles" 
              :key="role.id"
              class="role-item"
              :class="{ active: selectedRole?.id === role.id }"
              @click="selectRole(role)"
            >
              <div class="role-info">
                <h4>{{ role.name }}</h4>
                <p>{{ role.description }}</p>
                <span class="user-count">{{ role.userCount }} 个用户</span>
              </div>
              <div class="role-actions">
                <a-button type="text" size="small" @click.stop="editRole(role)">
                  <EditOutlined />
                </a-button>
              </div>
            </div>
          </div>
          
          <div class="permissions-panel" v-if="selectedRole">
            <h3>{{ selectedRole.name }} 权限设置</h3>
            <a-tree
              v-model:checkedKeys="selectedPermissions"
              checkable
              :tree-data="permissionTree"
              :field-names="{ title: 'title', key: 'key', children: 'children' }"
              @check="onPermissionChange"
            />
            <div class="permission-actions">
              <a-button type="primary" @click="savePermissions">
                保存权限
              </a-button>
              <a-button @click="resetPermissions">
                重置
              </a-button>
            </div>
          </div>
        </div>
      </a-card>

      <!-- 系统设置 -->
      <a-card class="management-card" title="系统设置">
        <a-form :model="systemSettings" layout="vertical">
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="系统名称">
                <a-input v-model:value="systemSettings.systemName" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="系统版本">
                <a-input v-model:value="systemSettings.version" disabled />
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="会话超时时间（分钟）">
                <a-input-number 
                  v-model:value="systemSettings.sessionTimeout" 
                  :min="5" 
                  :max="1440"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="密码强度要求">
                <a-select v-model:value="systemSettings.passwordStrength">
                  <a-select-option value="low">低</a-select-option>
                  <a-select-option value="medium">中</a-select-option>
                  <a-select-option value="high">高</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-form-item>
            <a-space>
              <a-button type="primary" @click="saveSystemSettings">
                保存设置
              </a-button>
              <a-button @click="resetSystemSettings">
                重置设置
              </a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </a-card>
    </div>

    <!-- 添加/编辑用户弹窗 -->
    <a-modal
      v-model:open="userModalVisible"
      :title="editingUser ? '编辑用户' : '添加用户'"
      width="600px"
      @ok="saveUser"
      @cancel="cancelUserEdit"
    >
      <a-form :model="userForm" :rules="userRules" ref="userFormRef" layout="vertical">
        <a-form-item name="username" label="用户名">
          <a-input 
            v-model:value="userForm.username" 
            :disabled="!!editingUser"
            placeholder="请输入用户名"
          />
        </a-form-item>
        
        <a-form-item name="email" label="邮箱">
          <a-input v-model:value="userForm.email" placeholder="请输入邮箱" />
        </a-form-item>
        
        <a-form-item name="role" label="角色">
          <a-select v-model:value="userForm.role" placeholder="请选择角色">
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="operator">操作员</a-select-option>
            <a-select-option value="viewer">观察者</a-select-option>
          </a-select>
        </a-form-item>
        
        <a-form-item v-if="!editingUser" name="password" label="密码">
          <a-input-password v-model:value="userForm.password" placeholder="请输入密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { message } from 'ant-design-vue';
import {
  CrownOutlined,
  UserAddOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined,
  TeamOutlined
} from '@ant-design/icons-vue';

// 用户管理
const users = ref([
  {
    id: 1,
    username: 'admin',
    email: 'admin@system.com',
    role: 'admin',
    active: true,
    lastLogin: '2024-01-20 14:30:00'
  },
  {
    id: 2,
    username: 'user1',
    email: 'user1@system.com',
    role: 'operator',
    active: true,
    lastLogin: '2024-01-20 10:15:00'
  },
  {
    id: 3,
    username: 'user2',
    email: 'user2@system.com',
    role: 'viewer',
    active: false,
    lastLogin: '2024-01-19 16:45:00'
  }
]);

const userColumns = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: '角色',
    dataIndex: 'role',
    key: 'role',
  },
  {
    title: '状态',
    dataIndex: 'active',
    key: 'status',
  },
  {
    title: '最后登录',
    dataIndex: 'lastLogin',
    key: 'lastLogin',
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
  },
];

// 角色管理
const roles = ref([
  {
    id: 1,
    name: '管理员',
    description: '拥有系统所有权限',
    userCount: 1,
    permissions: ['dashboard', 'assets', 'users', 'settings']
  },
  {
    id: 2,
    name: '操作员',
    description: '可以查看和操作资产信息',
    userCount: 1,
    permissions: ['dashboard', 'assets']
  },
  {
    id: 3,
    name: '观察者',
    description: '只能查看监控数据',
    userCount: 1,
    permissions: ['dashboard']
  }
]);

const selectedRole = ref(null);
const selectedPermissions = ref([]);

const permissionTree = [
  {
    title: '监控概览',
    key: 'dashboard',
    children: [
      { title: '查看监控数据', key: 'dashboard.view' },
      { title: '导出报表', key: 'dashboard.export' }
    ]
  },
  {
    title: '资产管理',
    key: 'assets',
    children: [
      { title: '查看资产', key: 'assets.view' },
      { title: '添加资产', key: 'assets.create' },
      { title: '编辑资产', key: 'assets.edit' },
      { title: '删除资产', key: 'assets.delete' }
    ]
  },
  {
    title: '用户管理',
    key: 'users',
    children: [
      { title: '查看用户', key: 'users.view' },
      { title: '添加用户', key: 'users.create' },
      { title: '编辑用户', key: 'users.edit' },
      { title: '删除用户', key: 'users.delete' }
    ]
  },
  {
    title: '系统设置',
    key: 'settings',
    children: [
      { title: '查看设置', key: 'settings.view' },
      { title: '修改设置', key: 'settings.edit' }
    ]
  }
];

// 用户表单
const userModalVisible = ref(false);
const editingUser = ref(null);
const userForm = reactive({
  username: '',
  email: '',
  role: '',
  password: ''
});

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
};

// 系统设置
const systemSettings = reactive({
  systemName: '运维监控系统',
  version: 'v1.0.0',
  sessionTimeout: 30,
  passwordStrength: 'medium'
});

// 辅助函数
const getRoleColor = (role) => {
  const colors = {
    admin: 'red',
    operator: 'blue',
    viewer: 'green'
  };
  return colors[role] || 'default';
};

const getRoleText = (role) => {
  const texts = {
    admin: '管理员',
    operator: '操作员',
    viewer: '观察者'
  };
  return texts[role] || role;
};

// 用户管理方法
const showAddUserModal = () => {
  editingUser.value = null;
  Object.assign(userForm, {
    username: '',
    email: '',
    role: '',
    password: ''
  });
  userModalVisible.value = true;
};

const editUser = (user) => {
  editingUser.value = user;
  Object.assign(userForm, {
    username: user.username,
    email: user.email,
    role: user.role,
    password: ''
  });
  userModalVisible.value = true;
};

const saveUser = () => {
  if (editingUser.value) {
    // 编辑用户
    const index = users.value.findIndex(u => u.id === editingUser.value.id);
    if (index !== -1) {
      users.value[index] = {
        ...users.value[index],
        email: userForm.email,
        role: userForm.role
      };
    }
    message.success('用户信息更新成功');
  } else {
    // 添加新用户
    const newUser = {
      id: Date.now(),
      username: userForm.username,
      email: userForm.email,
      role: userForm.role,
      active: true,
      lastLogin: '-'
    };
    users.value.push(newUser);
    message.success('用户添加成功');
  }
  
  userModalVisible.value = false;
};

const cancelUserEdit = () => {
  userModalVisible.value = false;
};

const toggleUserStatus = (user) => {
  message.success(`用户${user.username}已${user.active ? '启用' : '禁用'}`);
};

const resetPassword = (user) => {
  message.success(`已重置用户${user.username}的密码`);
};

const deleteUser = (user) => {
  const index = users.value.findIndex(u => u.id === user.id);
  if (index !== -1) {
    users.value.splice(index, 1);
    message.success('用户删除成功');
  }
};

// 角色权限管理方法
const selectRole = (role) => {
  selectedRole.value = role;
  selectedPermissions.value = [...role.permissions];
};

const onPermissionChange = (checkedKeys) => {
  selectedPermissions.value = checkedKeys;
};

const savePermissions = () => {
  if (selectedRole.value) {
    selectedRole.value.permissions = [...selectedPermissions.value];
    message.success('权限保存成功');
  }
};

const resetPermissions = () => {
  if (selectedRole.value) {
    selectedPermissions.value = [...selectedRole.value.permissions];
  }
};

// 系统设置方法
const saveSystemSettings = () => {
  message.success('系统设置保存成功');
};

const resetSystemSettings = () => {
  Object.assign(systemSettings, {
    systemName: '运维监控系统',
    version: 'v1.0.0',
    sessionTimeout: 30,
    passwordStrength: 'medium'
  });
  message.info('系统设置已重置');
};
</script>

<style scoped>
.admin-management {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 8px;
}

.title-icon {
  font-size: 28px;
  color: #faad14;
}

.page-desc {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.admin-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.management-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

:deep(.management-card .ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
}

:deep(.management-card .ant-card-head-title) {
  font-weight: 600;
  color: #262626;
}

/* 角色管理样式 */
.role-management {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  min-height: 400px;
}

.role-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.role-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.role-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.role-item.active {
  border-color: #1890ff;
  background: #f0f8ff;
}

.role-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 500;
}

.role-info p {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 12px;
}

.user-count {
  background: #f0f0f0;
  color: #666;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

.permissions-panel {
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 16px;
}

.permissions-panel h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
}

.permission-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-management {
    padding: 16px;
  }
  
  .role-management {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .role-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .role-actions {
    align-self: flex-end;
  }
}
</style>