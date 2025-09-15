<template>
  <div class="admin-backup admin-page">
    <!-- 页面标题区域 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <CloudDownloadOutlined />
          数据备份
        </h1>
        <p class="page-description">管理系统数据备份和恢复操作</p>
      </div>
      <div class="header-actions">
        <a-space>
          <a-button @click="downloadBackup">
            <DownloadOutlined />
            下载备份
          </a-button>
          <a-button type="primary" @click="showCreateBackupModal">
            <CloudDownloadOutlined />
            创建备份
          </a-button>
        </a-space>
      </div>
    </div>

    <!-- 备份管理布局 -->
    <div class="backup-layout admin-layout">
      <!-- 左侧菜单 -->
      <div class="backup-menu admin-menu">
        <div class="menu-title">备份类型</div>
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
        
        <!-- 备份统计 -->
        <div class="menu-stats">
          <div class="stats-title">备份统计</div>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">总备份数</span>
              <span class="stat-value">{{ backupStats.total }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">今日备份</span>
              <span class="stat-value">{{ backupStats.today }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">存储大小</span>
              <span class="stat-value">{{ backupStats.totalSize }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="backup-content admin-content">
        <a-card>
          <template #title>
            {{ getCurrentCategoryName() }}
          </template>
          <template #extra>
            <a-space>
              <a-input-search
                v-model:value="searchText"
                placeholder="搜索备份..."
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
                <a-select-option value="success">成功</a-select-option>
                <a-select-option value="failed">失败</a-select-option>
                <a-select-option value="running">进行中</a-select-option>
              </a-select>
              <a-button @click="refreshData">
                <ReloadOutlined />
              </a-button>
            </a-space>
          </template>

          <a-table
            :columns="tableColumns"
            :data-source="filteredBackups"
            :pagination="pagination"
            :loading="loading"
            :row-selection="rowSelection"
            row-key="id"
            size="middle"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'type'">
                <a-tag :color="getTypeColor(record.type)">
                  {{ getTypeText(record.type) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.status)">
                  <component :is="getStatusIcon(record.status)" />
                  {{ getStatusText(record.status) }}
                </a-tag>
              </template>
              <template v-else-if="column.key === 'size'">
                <span>{{ formatFileSize(record.size) }}</span>
              </template>
              <template v-else-if="column.key === 'actions'">
                <a-space>
                  <a-button 
                    type="link" 
                    size="small" 
                    @click="downloadSingleBackup(record)"
                    :disabled="record.status !== 'success'"
                  >
                    下载
                  </a-button>
                  <a-button 
                    type="link" 
                    size="small" 
                    @click="restoreBackup(record)"
                    :disabled="record.status !== 'success'"
                  >
                    恢复
                  </a-button>
                  <a-button type="link" size="small" @click="viewBackupDetail(record)">
                    详情
                  </a-button>
                  <a-popconfirm
                    title="确定要删除这个备份吗？"
                    @confirm="deleteBackup(record)"
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
              <a-button @click="batchDownload">批量下载</a-button>
              <a-popconfirm
                title="确定要删除选中的备份吗？"
                @confirm="batchDelete"
              >
                <a-button danger>批量删除</a-button>
              </a-popconfirm>
            </a-space>
          </div>
        </a-card>
      </div>
    </div>

    <!-- 创建备份弹窗 -->
    <a-modal
      v-model:open="createBackupModalVisible"
      title="创建数据备份"
      width="600px"
      @ok="handleCreateBackup"
      @cancel="handleCreateBackupCancel"
    >
      <a-form
        ref="backupFormRef"
        :model="backupFormData"
        :rules="backupFormRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="备份名称" name="name">
              <a-input v-model:value="backupFormData.name" placeholder="输入备份名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="备份类型" name="type">
              <a-select v-model:value="backupFormData.type" placeholder="选择备份类型">
                <a-select-option value="full">完整备份</a-select-option>
                <a-select-option value="incremental">增量备份</a-select-option>
                <a-select-option value="differential">差异备份</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="备份范围" name="scope">
          <a-checkbox-group v-model:value="backupFormData.scope">
            <a-row :gutter="[16, 16]">
              <a-col :span="8">
                <a-checkbox value="database">数据库</a-checkbox>
              </a-col>
              <a-col :span="8">
                <a-checkbox value="config">配置文件</a-checkbox>
              </a-col>
              <a-col :span="8">
                <a-checkbox value="logs">日志文件</a-checkbox>
              </a-col>
              <a-col :span="8">
                <a-checkbox value="uploads">上传文件</a-checkbox>
              </a-col>
              <a-col :span="8">
                <a-checkbox value="assets">静态资源</a-checkbox>
              </a-col>
              <a-col :span="8">
                <a-checkbox value="cache">缓存数据</a-checkbox>
              </a-col>
            </a-row>
          </a-checkbox-group>
        </a-form-item>

        <a-form-item label="备份描述" name="description">
          <a-textarea 
            v-model:value="backupFormData.description" 
            placeholder="输入备份描述"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="压缩选项" name="compression">
          <a-switch v-model:checked="backupFormData.compression" />
          <span class="switch-description">启用压缩以减少备份文件大小</span>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 备份详情弹窗 -->
    <a-modal
      v-model:open="detailModalVisible"
      title="备份详情"
      width="800px"
      :footer="null"
    >
      <a-descriptions
        v-if="selectedBackup"
        :column="2"
        bordered
        size="small"
      >
        <a-descriptions-item label="备份名称" :span="2">
          {{ selectedBackup.name }}
        </a-descriptions-item>
        <a-descriptions-item label="备份类型">
          <a-tag :color="getTypeColor(selectedBackup.type)">
            {{ getTypeText(selectedBackup.type) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="备份状态">
          <a-tag :color="getStatusColor(selectedBackup.status)">
            <component :is="getStatusIcon(selectedBackup.status)" />
            {{ getStatusText(selectedBackup.status) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="文件大小">
          {{ formatFileSize(selectedBackup.size) }}
        </a-descriptions-item>
        <a-descriptions-item label="创建时间">
          {{ selectedBackup.createdAt }}
        </a-descriptions-item>
        <a-descriptions-item label="完成时间">
          {{ selectedBackup.completedAt || '未完成' }}
        </a-descriptions-item>
        <a-descriptions-item label="备份路径">
          {{ selectedBackup.filePath }}
        </a-descriptions-item>
        <a-descriptions-item label="备份范围" :span="2">
          <a-space>
            <a-tag v-for="scope in selectedBackup.scope" :key="scope">
              {{ getScopeText(scope) }}
            </a-tag>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="备份描述" :span="2">
          {{ selectedBackup.description || '无描述' }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  CloudDownloadOutlined,
  DownloadOutlined,
  ReloadOutlined,
  DatabaseOutlined,
  FileOutlined,
  FolderOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  PlusOutlined
} from '@ant-design/icons-vue';

// 响应式数据
const loading = ref(false);
const createBackupModalVisible = ref(false);
const detailModalVisible = ref(false);
const searchText = ref('');
const statusFilter = ref('');
const activeCategory = ref('all');
const selectedRowKeys = ref([]);
const selectedBackup = ref(null);

// 表单数据
const backupFormRef = ref();
const backupFormData = ref({
  name: '',
  type: 'full',
  scope: ['database', 'config'],
  description: '',
  compression: true
});

// 备份数据
const backups = ref([]);
const backupStats = ref({
  total: 0,
  today: 0,
  totalSize: '0 MB'
});

// 分类列表
const categoryList = ref([
  { key: 'all', name: '全部备份', icon: 'FolderOutlined', count: 0 },
  { key: 'full', name: '完整备份', icon: 'DatabaseOutlined', count: 0 },
  { key: 'incremental', name: '增量备份', icon: 'FileOutlined', count: 0 },
  { key: 'differential', name: '差异备份', icon: 'SettingOutlined', count: 0 },
  { key: 'success', name: '成功备份', icon: 'CheckCircleOutlined', count: 0 },
  { key: 'failed', name: '失败备份', icon: 'CloseCircleOutlined', count: 0 }
]);

// 表格列配置
const tableColumns = [
  { title: '备份名称', dataIndex: 'name', key: 'name', sorter: true },
  { title: '备份类型', key: 'type', width: 100 },
  { title: '文件大小', key: 'size', width: 100, sorter: true },
  { title: '状态', key: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt', width: 180, sorter: true },
  { title: '完成时间', dataIndex: 'completedAt', key: 'completedAt', width: 180 },
  { title: '操作', key: 'actions', width: 200, fixed: 'right' }
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
const backupFormRules = {
  name: [
    { required: true, message: '请输入备份名称', trigger: 'blur' },
    { min: 2, max: 50, message: '备份名称长度在2-50个字符', trigger: 'blur' }
  ],
  type: [{ required: true, message: '请选择备份类型', trigger: 'change' }],
  scope: [{ required: true, message: '请选择备份范围', trigger: 'change' }]
};

// 计算属性
const filteredBackups = computed(() => {
  let result = backups.value;
  
  if (activeCategory.value !== 'all') {
    if (['success', 'failed', 'running'].includes(activeCategory.value)) {
      result = result.filter(backup => backup.status === activeCategory.value);
    } else {
      result = result.filter(backup => backup.type === activeCategory.value);
    }
  }
  
  if (statusFilter.value) {
    result = result.filter(backup => backup.status === statusFilter.value);
  }
  
  if (searchText.value) {
    const searchLower = searchText.value.toLowerCase();
    result = result.filter(backup => 
      backup.name?.toLowerCase().includes(searchLower) ||
      backup.description?.toLowerCase().includes(searchLower)
    );
  }
  
  return result;
});

// 获取当前分类名称
const getCurrentCategoryName = () => {
  const category = categoryList.value.find(cat => cat.key === activeCategory.value);
  return category ? category.name : '全部备份';
};

// 获取类型颜色和文本
const getTypeColor = (type) => {
  const colors = { full: 'blue', incremental: 'green', differential: 'orange' };
  return colors[type] || 'default';
};

const getTypeText = (type) => {
  const texts = { full: '完整备份', incremental: '增量备份', differential: '差异备份' };
  return texts[type] || type;
};

// 获取状态颜色、图标和文本
const getStatusColor = (status) => {
  const colors = { success: 'green', failed: 'red', running: 'blue' };
  return colors[status] || 'default';
};

const getStatusIcon = (status) => {
  const icons = { success: 'CheckCircleOutlined', failed: 'CloseCircleOutlined', running: 'LoadingOutlined' };
  return icons[status] || 'CheckCircleOutlined';
};

const getStatusText = (status) => {
  const texts = { success: '成功', failed: '失败', running: '进行中' };
  return texts[status] || status;
};

// 获取范围文本
const getScopeText = (scope) => {
  const texts = {
    database: '数据库',
    config: '配置文件',
    logs: '日志文件',
    uploads: '上传文件',
    assets: '静态资源',
    cache: '缓存数据'
  };
  return texts[scope] || scope;
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 更新统计数据
const updateStats = () => {
  const today = new Date().toISOString().split('T')[0];
  const todayBackups = backups.value.filter(backup => 
    backup.createdAt.startsWith(today)
  ).length;
  
  const totalSize = backups.value.reduce((sum, backup) => sum + (backup.size || 0), 0);
  
  backupStats.value = {
    total: backups.value.length,
    today: todayBackups,
    totalSize: formatFileSize(totalSize)
  };
  
  // 更新分类计数
  categoryList.value.forEach(category => {
    switch (category.key) {
      case 'all':
        category.count = backups.value.length;
        break;
      case 'full':
      case 'incremental':
      case 'differential':
        category.count = backups.value.filter(backup => backup.type === category.key).length;
        break;
      case 'success':
      case 'failed':
        category.count = backups.value.filter(backup => backup.status === category.key).length;
        break;
    }
  });
};

// 生成模拟数据
const generateMockBackups = () => {
  return [
    {
      id: 1,
      name: '完整系统备份_20240120',
      type: 'full',
      status: 'success',
      size: 1073741824, // 1GB
      scope: ['database', 'config', 'uploads'],
      description: '定期完整系统备份',
      filePath: '/backups/full_backup_20240120.tar.gz',
      createdAt: '2024-01-20 02:00:00',
      completedAt: '2024-01-20 02:45:30'
    },
    {
      id: 2,
      name: '数据库增量备份_20240121',
      type: 'incremental',
      status: 'success',
      size: 52428800, // 50MB
      scope: ['database'],
      description: '每日数据库增量备份',
      filePath: '/backups/incremental_db_20240121.tar.gz',
      createdAt: '2024-01-21 02:00:00',
      completedAt: '2024-01-21 02:05:15'
    },
    {
      id: 3,
      name: '配置文件备份_20240121',
      type: 'differential',
      status: 'failed',
      size: 0,
      scope: ['config'],
      description: '系统配置文件差异备份',
      filePath: '/backups/config_diff_20240121.tar.gz',
      createdAt: '2024-01-21 03:00:00',
      completedAt: null
    },
    {
      id: 4,
      name: '应急备份_20240121',
      type: 'full',
      status: 'running',
      size: 0,
      scope: ['database', 'config', 'logs'],
      description: '系统维护前的应急备份',
      filePath: '/backups/emergency_20240121.tar.gz',
      createdAt: '2024-01-21 10:30:00',
      completedAt: null
    }
  ];
};

// 获取备份列表
const fetchBackups = async () => {
  try {
    loading.value = true;
    backups.value = generateMockBackups();
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

// 搜索和筛选
const handleSearch = () => { selectedRowKeys.value = []; };
const handleStatusFilter = () => { selectedRowKeys.value = []; };

// 刷新数据
const refreshData = () => {
  fetchBackups();
  message.success('数据刷新成功');
};

// 显示创建备份弹窗
const showCreateBackupModal = () => {
  const now = new Date();
  const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, 19);
  backupFormData.value = {
    name: `系统备份_${timestamp}`,
    type: 'full',
    scope: ['database', 'config'],
    description: '',
    compression: true
  };
  createBackupModalVisible.value = true;
};

// 创建备份
const handleCreateBackup = async () => {
  try {
    await backupFormRef.value.validate();
    loading.value = true;
    
    const newBackup = {
      id: Date.now(),
      ...backupFormData.value,
      status: 'running',
      size: 0,
      filePath: `/backups/${backupFormData.value.name.toLowerCase().replace(/\s+/g, '_')}.tar.gz`,
      createdAt: new Date().toLocaleString('zh-CN'),
      completedAt: null
    };
    
    backups.value.unshift(newBackup);
    updateStats();
    createBackupModalVisible.value = false;
    message.success('备份任务已启动');
    
    // 模拟备份完成
    setTimeout(() => {
      const backup = backups.value.find(b => b.id === newBackup.id);
      if (backup) {
        backup.status = 'success';
        backup.size = Math.floor(Math.random() * 1073741824) + 52428800; // 50MB - 1GB
        backup.completedAt = new Date().toLocaleString('zh-CN');
        updateStats();
        message.success('备份完成');
      }
    }, 3000);
  } catch (error) {
    message.error('创建备份失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 取消创建备份
const handleCreateBackupCancel = () => {
  createBackupModalVisible.value = false;
  backupFormRef.value?.resetFields();
};

// 查看备份详情
const viewBackupDetail = (record) => {
  selectedBackup.value = record;
  detailModalVisible.value = true;
};

// 下载单个备份
const downloadSingleBackup = (record) => {
  message.success(`开始下载备份：${record.name}`);
};

// 批量下载
const batchDownload = () => {
  message.success(`开始批量下载 ${selectedRowKeys.value.length} 个备份`);
  selectedRowKeys.value = [];
};

// 下载备份
const downloadBackup = () => {
  message.success('开始下载最新备份');
};

// 恢复备份
const restoreBackup = (record) => {
  message.warning(`恢复备份功能需要谨慎操作：${record.name}`);
};

// 删除备份
const deleteBackup = async (record) => {
  try {
    loading.value = true;
    const index = backups.value.findIndex(backup => backup.id === record.id);
    if (index !== -1) {
      backups.value.splice(index, 1);
    }
    updateStats();
    message.success('备份删除成功');
  } catch (error) {
    message.error('删除失败，请重试');
  } finally {
    loading.value = false;
  }
};

// 批量删除
const batchDelete = () => {
  backups.value = backups.value.filter(backup => !selectedRowKeys.value.includes(backup.id));
  updateStats();
  selectedRowKeys.value = [];
  message.success('批量删除成功');
};

// 组件挂载
onMounted(() => {
  fetchBackups();
});
</script>

<style scoped>
@import '@/assets/admin-common.css';

/* 数据备份页面特有的样式 */
/* 所有通用样式已在 admin-common.css 中定义 */
</style>