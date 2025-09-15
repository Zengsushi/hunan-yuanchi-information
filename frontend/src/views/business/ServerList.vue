<template>
  <div class="server-list-container">
    <div class="page-header">
      <h1>服务器管理</h1>
      <p>管理所有服务器资产</p>
    </div>
    
    <a-card :bordered="false" class="search-card">
      <a-row gutter="[16, 16]">
        <a-col :span="6">
          <a-input v-model:value="searchKeyword" placeholder="服务器名称/IP" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="serverStatus" placeholder="服务器状态" allow-clear>
            <a-select-option value="online">在线</a-select-option>
            <a-select-option value="offline">离线</a-select-option>
            <a-select-option value="maintenance">维护中</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="serverType" placeholder="服务器类型" allow-clear>
            <a-select-option value="physical">物理服务器</a-select-option>
            <a-select-option value="virtual">虚拟服务器</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-row gutter="16">
            <a-col :span="12">
              <a-button type="primary" @click="handleSearch">搜索</a-button>
            </a-col>
            <a-col :span="12">
              <a-button @click="handleReset">重置</a-button>
            </a-col>
          </a-row>
        </a-col>
      </a-row>
    </a-card>
    
    <div class="action-bar">
      <a-button type="primary" icon="plus">新增服务器</a-button>
      <a-button icon="download">导出数据</a-button>
      <a-button icon="sync">刷新状态</a-button>
    </div>
    
    <a-card :bordered="false" class="table-card">
      <a-table 
        :columns="columns" 
        :data-source="serversData" 
        row-key="id" 
        :pagination="pagination" 
        @change="handleTableChange"
      >
        <template #headerCell="{ column }">
          <span v-if="column.key === 'id'">{{ column.title }} ({{ serversData.length }})</span>
          <span v-else>{{ column.title }}</span>
        </template>
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <span v-if="record.status === 'online'" class="status-tag online">在线</span>
            <span v-else-if="record.status === 'offline'" class="status-tag offline">离线</span>
            <span v-else-if="record.status === 'maintenance'" class="status-tag maintenance">维护中</span>
          </template>
          <template v-else-if="column.key === 'operation'">
            <a-button type="link" @click="handleView(record.id)">查看</a-button>
            <a-button type="link" @click="handleEdit(record.id)">编辑</a-button>
            <a-button type="link" danger @click="handleDelete(record.id)">删除</a-button>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Input, Select, Button, Table, Card, Row, Col } from 'ant-design-vue';
import { PlusOutlined, DownloadOutlined, ReloadOutlined } from '@ant-design/icons-vue';

// 搜索条件
const searchKeyword = ref('');
const serverStatus = ref('');
const serverType = ref('');

// 分页配置
const pagination = {
  current: 1,
  pageSize: 10,
  pageSizeOptions: ['10', '20', '50', '100'],
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`,
};

// 模拟数据
const serversData = [
  {
    id: 'S001',
    name: '服务器A-001',
    type: '物理服务器',
    model: 'Dell R740',
    serialNumber: 'SN20230001',
    ipAddress: '192.168.1.101',
    cpu: 'Intel Xeon Gold 6230 2.1GHz',
    memory: '64GB DDR4',
    storage: '2x 1TB SSD + 4x 4TB HDD',
    os: 'CentOS 7.9',
    location: '数据中心A-1楼',
    department: '技术部',
    owner: '张三',
    status: 'online',
    purchaseDate: '2023-01-15',
    warrantyEndDate: '2026-01-14'
  },
  {
    id: 'S002',
    name: '服务器A-002',
    type: '物理服务器',
    model: 'HP ProLiant DL380 Gen10',
    serialNumber: 'SN20230003',
    ipAddress: '192.168.1.102',
    cpu: 'Intel Xeon Silver 4210 2.2GHz',
    memory: '32GB DDR4',
    storage: '2x 500GB SSD + 2x 2TB HDD',
    os: 'Ubuntu 20.04',
    location: '数据中心A-1楼',
    department: '技术部',
    owner: '张三',
    status: 'offline',
    purchaseDate: '2023-01-15',
    warrantyEndDate: '2026-01-14'
  },
  {
    id: 'S003',
    name: '虚拟服务器A-001',
    type: '虚拟服务器',
    model: 'VMware ESXi',
    serialNumber: 'VM20230001',
    ipAddress: '192.168.1.201',
    cpu: '4 vCPUs',
    memory: '16GB',
    storage: '100GB',
    os: 'Windows Server 2019',
    location: '虚拟化平台',
    department: '财务部',
    owner: '李四',
    status: 'online',
    purchaseDate: '2023-03-01',
    warrantyEndDate: '2026-02-28'
  },
  {
    id: 'S004',
    name: '虚拟服务器A-002',
    type: '虚拟服务器',
    model: 'VMware ESXi',
    serialNumber: 'VM20230002',
    ipAddress: '192.168.1.202',
    cpu: '8 vCPUs',
    memory: '32GB',
    storage: '200GB',
    os: 'CentOS 8',
    location: '虚拟化平台',
    department: '市场部',
    owner: '王五',
    status: 'maintenance',
    purchaseDate: '2023-03-01',
    warrantyEndDate: '2026-02-28'
  },
  {
    id: 'S005',
    name: '服务器B-001',
    type: '物理服务器',
    model: 'IBM x3650 M5',
    serialNumber: 'SN20230005',
    ipAddress: '192.168.1.103',
    cpu: 'Intel Xeon E5-2680 v4 2.4GHz',
    memory: '128GB DDR4',
    storage: '4x 2TB SSD + 8x 8TB HDD',
    os: 'Red Hat Enterprise Linux 8',
    location: '数据中心A-2楼',
    department: '技术部',
    owner: '赵六',
    status: 'online',
    purchaseDate: '2023-02-10',
    warrantyEndDate: '2026-02-09'
  }
];

// 表格列定义
const columns = [
  {
    title: '服务器编号',
    dataIndex: 'id',
    key: 'id',
    fixed: 'left',
    width: 120
  },
  {
    title: '服务器名称',
    dataIndex: 'name',
    key: 'name',
    width: 180
  },
  {
    title: '类型',
    dataIndex: 'type',
    key: 'type',
    width: 100
  },
  {
    title: 'IP地址',
    dataIndex: 'ipAddress',
    key: 'ipAddress',
    width: 150
  },
  {
    title: 'CPU',
    dataIndex: 'cpu',
    key: 'cpu',
    width: 200
  },
  {
    title: '内存',
    dataIndex: 'memory',
    key: 'memory',
    width: 100
  },
  {
    title: '操作系统',
    dataIndex: 'os',
    key: 'os',
    width: 150
  },
  {
    title: '所在位置',
    dataIndex: 'location',
    key: 'location',
    width: 150
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 80
  },
  {
    title: '操作',
    key: 'operation',
    fixed: 'right',
    width: 150
  }
];

// 处理搜索
const handleSearch = () => {
  console.log('搜索条件:', {
    keyword: searchKeyword.value,
    status: serverStatus.value,
    type: serverType.value
  });
  // 这里应该调用API获取数据
};

// 处理重置
const handleReset = () => {
  searchKeyword.value = '';
  serverStatus.value = '';
  serverType.value = '';
};

// 处理表格分页变化
const handleTableChange = (pagination, filters, sorter) => {
  console.log('分页变化:', pagination);
  // 这里应该根据分页信息重新获取数据
};

// 处理查看操作
const handleView = (id) => {
  console.log('查看服务器:', id);
  // 这里应该跳转到服务器详情页面
};

// 处理编辑操作
const handleEdit = (id) => {
  console.log('编辑服务器:', id);
  // 这里应该跳转到服务器编辑页面
};

// 处理删除操作
const handleDelete = (id) => {
  console.log('删除服务器:', id);
  // 这里应该调用API删除服务器
};
</script>

<style scoped>
.server-list-container {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: rgba(0, 0, 0, 0.45);
}

.search-card {
  margin-bottom: 16px;
  padding: 16px;
}

.action-bar {
  margin-bottom: 16px;
}

.table-card {
  overflow: hidden;
}

.status-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-tag.online {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.status-tag.offline {
  background-color: #fff2e8;
  color: #fa8c16;
  border: 1px solid #ffd591;
}

.status-tag.maintenance {
  background-color: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}
</style>