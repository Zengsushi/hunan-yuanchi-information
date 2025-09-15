<template>
  <div class="network-device-list-container">
    <div class="page-header">
      <h1>网络设备管理</h1>
      <p>管理所有网络设备资产</p>
    </div>
    
    <a-card :bordered="false" class="search-card">
      <a-row gutter="[16, 16]">
        <a-col :span="6">
          <a-input v-model:value="searchKeyword" placeholder="设备名称/IP" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="deviceStatus" placeholder="设备状态" allow-clear>
            <a-select-option value="online">在线</a-select-option>
            <a-select-option value="offline">离线</a-select-option>
            <a-select-option value="maintenance">维护中</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="deviceType" placeholder="设备类型" allow-clear>
            <a-select-option value="switch">交换机</a-select-option>
            <a-select-option value="router">路由器</a-select-option>
            <a-select-option value="firewall">防火墙</a-select-option>
            <a-select-option value="ap">无线AP</a-select-option>
            <a-select-option value="other">其他网络设备</a-select-option>
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
      <a-button type="primary" icon="plus">新增网络设备</a-button>
      <a-button icon="download">导出数据</a-button>
      <a-button icon="sync">刷新状态</a-button>
    </div>
    
    <a-card :bordered="false" class="table-card">
      <a-table 
        :columns="columns" 
        :data-source="networkDevicesData" 
        row-key="id" 
        :pagination="pagination" 
        @change="handleTableChange"
      >
        <template #headerCell="{ column }">
          <span v-if="column.key === 'id'">{{ column.title }} ({{ networkDevicesData.length }})</span>
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
const deviceStatus = ref('');
const deviceType = ref('');

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
const networkDevicesData = [
  {
    id: 'N001',
    name: '交换机B-001',
    type: '交换机',
    model: 'Cisco Catalyst 9300',
    serialNumber: 'SN20230002',
    ipAddress: '192.168.1.2',
    location: '数据中心A-1楼',
    department: '技术部',
    owner: '李四',
    status: 'online',
    purchaseDate: '2023-02-10',
    warrantyEndDate: '2026-02-09'
  },
  {
    id: 'N002',
    name: '防火墙C-001',
    type: '防火墙',
    model: 'Palo Alto PA-220',
    serialNumber: 'SN20230004',
    ipAddress: '192.168.1.1',
    location: '数据中心A-1楼',
    department: '技术部',
    owner: '王五',
    status: 'maintenance',
    purchaseDate: '2023-03-05',
    warrantyEndDate: '2026-03-04'
  },
  {
    id: 'N003',
    name: '路由器D-001',
    type: '路由器',
    model: 'Cisco ISR 4331',
    serialNumber: 'SN20230006',
    ipAddress: '192.168.0.1',
    location: '数据中心A-1楼',
    department: '技术部',
    owner: '赵六',
    status: 'online',
    purchaseDate: '2023-02-15',
    warrantyEndDate: '2026-02-14'
  },
  {
    id: 'N004',
    name: '无线AP-E001',
    type: '无线AP',
    model: 'Cisco Catalyst 9120AX',
    serialNumber: 'SN20230007',
    ipAddress: '192.168.1.10',
    location: '办公楼1层',
    department: '行政部',
    owner: '钱七',
    status: 'online',
    purchaseDate: '2023-03-10',
    warrantyEndDate: '2026-03-09'
  },
  {
    id: 'N005',
    name: '交换机B-002',
    type: '交换机',
    model: 'H3C S5800-56C-POE+',
    serialNumber: 'SN20230008',
    ipAddress: '192.168.1.3',
    location: '数据中心A-2楼',
    department: '技术部',
    owner: '孙八',
    status: 'offline',
    purchaseDate: '2023-02-20',
    warrantyEndDate: '2026-02-19'
  }
];

// 表格列定义
const columns = [
  {
    title: '设备编号',
    dataIndex: 'id',
    key: 'id',
    fixed: 'left',
    width: 120
  },
  {
    title: '设备名称',
    dataIndex: 'name',
    key: 'name',
    width: 180
  },
  {
    title: '设备类型',
    dataIndex: 'type',
    key: 'type',
    width: 100
  },
  {
    title: '型号',
    dataIndex: 'model',
    key: 'model',
    width: 150
  },
  {
    title: 'IP地址',
    dataIndex: 'ipAddress',
    key: 'ipAddress',
    width: 150
  },
  {
    title: '所在位置',
    dataIndex: 'location',
    key: 'location',
    width: 150
  },
  {
    title: '所属部门',
    dataIndex: 'department',
    key: 'department',
    width: 100
  },
  {
    title: '负责人',
    dataIndex: 'owner',
    key: 'owner',
    width: 80
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
    status: deviceStatus.value,
    type: deviceType.value
  });
  // 这里应该调用API获取数据
};

// 处理重置
const handleReset = () => {
  searchKeyword.value = '';
  deviceStatus.value = '';
  deviceType.value = '';
};

// 处理表格分页变化
const handleTableChange = (pagination, filters, sorter) => {
  console.log('分页变化:', pagination);
  // 这里应该根据分页信息重新获取数据
};

// 处理查看操作
const handleView = (id) => {
  console.log('查看网络设备:', id);
  // 这里应该跳转到网络设备详情页面
};

// 处理编辑操作
const handleEdit = (id) => {
  console.log('编辑网络设备:', id);
  // 这里应该跳转到网络设备编辑页面
};

// 处理删除操作
const handleDelete = (id) => {
  console.log('删除网络设备:', id);
  // 这里应该调用API删除网络设备
};
</script>

<style scoped>
.network-device-list-container {
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