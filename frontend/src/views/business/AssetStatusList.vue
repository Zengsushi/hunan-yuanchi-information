<template>
  <div class="asset-status-list-container">
    <div class="page-header">
      <h1>资产状态管理</h1>
      <p>管理资产状态信息</p>
    </div>
    
    <a-card :bordered="false" class="search-card">
      <a-row gutter="[16, 16]">
        <a-col :span="6">
          <a-input v-model:value="searchKeyword" placeholder="状态名称" allow-clear />
        </a-col>
        <a-col :span="18" style="text-align: right;">
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px;" @click="handleReset">重置</a-button>
        </a-col>
      </a-row>
    </a-card>
    
    <div class="action-bar">
      <a-button type="primary" icon="plus" @click="handleAddStatus">新增状态</a-button>
      <a-button icon="download">导出数据</a-button>
    </div>
    
    <a-card :bordered="false" class="table-card">
      <a-table 
        :columns="columns" 
        :data-source="statusData" 
        row-key="id" 
        :pagination="pagination" 
        @change="handleTableChange"
      >
        <template #headerCell="{ column }">
          <span v-if="column.key === 'id'">{{ column.title }} ({{ statusData.length }})</span>
          <span v-else>{{ column.title }}</span>
        </template>
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'color'">
            <span class="color-sample" :style="{ backgroundColor: record.color }"></span>
          </template>
          <template v-if="column.key === 'operation'">
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
import { Input, Button, Table, Card, Row, Col } from 'ant-design-vue';
import { PlusOutlined, DownloadOutlined } from '@ant-design/icons-vue';

// 搜索条件
const searchKeyword = ref('');

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
const statusData = [
  {
    id: '1',
    name: '在线',
    color: '#52c41a',
    description: '资产正常运行中',
    assetCount: 112,
    createTime: '2023-01-01 10:00:00',
    updateTime: '2023-01-01 10:00:00'
  },
  {
    id: '2',
    name: '离线',
    color: '#fa8c16',
    description: '资产当前不在线',
    assetCount: 8,
    createTime: '2023-01-01 10:00:00',
    updateTime: '2023-01-01 10:00:00'
  },
  {
    id: '3',
    name: '维护中',
    color: '#1890ff',
    description: '资产正在进行维护',
    assetCount: 4,
    createTime: '2023-01-01 10:00:00',
    updateTime: '2023-01-01 10:00:00'
  },
  {
    id: '4',
    name: '已下线',
    color: '#8c8c8c',
    description: '资产已停止使用',
    assetCount: 4,
    createTime: '2023-01-01 10:00:00',
    updateTime: '2023-01-01 10:00:00'
  },
  {
    id: '5',
    name: '故障',
    color: '#f5222d',
    description: '资产出现故障',
    assetCount: 0,
    createTime: '2023-01-01 10:00:00',
    updateTime: '2023-01-01 10:00:00'
  },
  {
    id: '6',
    name: '待上线',
    color: '#722ed1',
    description: '资产已采购但尚未上线',
    assetCount: 0,
    createTime: '2023-01-01 10:00:00',
    updateTime: '2023-01-01 10:00:00'
  }
];

// 表格列定义
const columns = [
  {
    title: '状态编号',
    dataIndex: 'id',
    key: 'id',
    fixed: 'left',
    width: 120
  },
  {
    title: '状态名称',
    dataIndex: 'name',
    key: 'name',
    width: 150
  },
  {
    title: '状态颜色',
    dataIndex: 'color',
    key: 'color',
    width: 100
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    width: 250
  },
  {
    title: '关联资产数',
    dataIndex: 'assetCount',
    key: 'assetCount',
    width: 120,
    sorter: (a, b) => a.assetCount - b.assetCount
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
    key: 'createTime',
    width: 180
  },
  {
    title: '更新时间',
    dataIndex: 'updateTime',
    key: 'updateTime',
    width: 180
  },
  {
    title: '操作',
    key: 'operation',
    fixed: 'right',
    width: 120
  }
];

// 处理搜索
const handleSearch = () => {
  console.log('搜索条件:', {
    keyword: searchKeyword.value
  });
  // 这里应该调用API获取数据
};

// 处理重置
const handleReset = () => {
  searchKeyword.value = '';
};

// 处理表格分页变化
const handleTableChange = (pagination, filters, sorter) => {
  console.log('分页变化:', pagination);
  // 这里应该根据分页信息重新获取数据
};

// 新增状态
const handleAddStatus = () => {
  console.log('新增状态');
  // 这里应该打开新增状态的模态框
};

// 处理编辑操作
const handleEdit = (id) => {
  console.log('编辑状态:', id);
  // 这里应该打开编辑状态的模态框
};

// 处理删除操作
const handleDelete = (id) => {
  console.log('删除状态:', id);
  // 这里应该显示确认删除的模态框，然后调用API删除状态
};
</script>

<style scoped>
.asset-status-list-container {
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

.color-sample {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #d9d9d9;
}
</style>