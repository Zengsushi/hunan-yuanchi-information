<template>
  <div class="asset-category-list-container">
    <div class="page-header">
      <h1>资产分类管理</h1>
      <p>管理资产分类信息</p>
    </div>
    
    <a-card :bordered="false" class="search-card">
      <a-row gutter="[16, 16]">
        <a-col :span="6">
          <a-input v-model:value="searchKeyword" placeholder="分类名称" allow-clear />
        </a-col>
        <a-col :span="6">
          <a-select v-model:value="parentCategory" placeholder="父级分类" allow-clear>
            <a-select-option value="">无父级分类</a-select-option>
            <a-select-option v-for="category in parentCategories" :key="category.id" :value="category.id">{{ category.name }}</a-select-option>
          </a-select>
        </a-col>
        <a-col :span="12" style="text-align: right;">
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px;" @click="handleReset">重置</a-button>
        </a-col>
      </a-row>
    </a-card>
    
    <div class="action-bar">
      <a-button type="primary" icon="plus" @click="handleAddCategory">新增分类</a-button>
      <a-button icon="download">导出数据</a-button>
    </div>
    
    <a-card :bordered="false" class="table-card">
      <a-table 
        :columns="columns" 
        :data-source="categoriesData" 
        row-key="id" 
        :pagination="pagination" 
        @change="handleTableChange"
      >
        <template #headerCell="{ column }">
          <span v-if="column.key === 'id'">{{ column.title }} ({{ categoriesData.length }})</span>
          <span v-else>{{ column.title }}</span>
        </template>
        <template #bodyCell="{ column, record }">
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
import { Input, Select, Button, Table, Card, Row, Col, Modal, Form } from 'ant-design-vue';
import { PlusOutlined, DownloadOutlined } from '@ant-design/icons-vue';

// 搜索条件
const searchKeyword = ref('');
const parentCategory = ref('');

// 分页配置
const pagination = {
  current: 1,
  pageSize: 10,
  pageSizeOptions: ['10', '20', '50', '100'],
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`,
};

// 父级分类数据
const parentCategories = [
  { id: '1', name: '服务器' },
  { id: '2', name: '网络设备' },
  { id: '3', name: '存储设备' },
  { id: '4', name: '办公设备' }
];

// 模拟数据
const categoriesData = [
  {
    id: '1',
    name: '服务器',
    parentId: null,
    parentName: '',
    description: '包括物理服务器和虚拟服务器',
    assetCount: 64,
    createTime: '2023-01-01 10:00:00',
    updateTime: '2023-01-01 10:00:00'
  },
  {
    id: '1-1',
    name: '物理服务器',
    parentId: '1',
    parentName: '服务器',
    description: '实体服务器设备',
    assetCount: 32,
    createTime: '2023-01-01 10:05:00',
    updateTime: '2023-01-01 10:05:00'
  },
  {
    id: '1-2',
    name: '虚拟服务器',
    parentId: '1',
    parentName: '服务器',
    description: '虚拟化平台上的虚拟服务器',
    assetCount: 32,
    createTime: '2023-01-01 10:05:00',
    updateTime: '2023-01-01 10:05:00'
  },
  {
    id: '2',
    name: '网络设备',
    parentId: null,
    parentName: '',
    description: '包括交换机、路由器、防火墙等网络设备',
    assetCount: 32,
    createTime: '2023-01-01 10:10:00',
    updateTime: '2023-01-01 10:10:00'
  },
  {
    id: '2-1',
    name: '交换机',
    parentId: '2',
    parentName: '网络设备',
    description: '网络交换设备',
    assetCount: 16,
    createTime: '2023-01-01 10:15:00',
    updateTime: '2023-01-01 10:15:00'
  },
  {
    id: '2-2',
    name: '路由器',
    parentId: '2',
    parentName: '网络设备',
    description: '网络路由设备',
    assetCount: 8,
    createTime: '2023-01-01 10:15:00',
    updateTime: '2023-01-01 10:15:00'
  },
  {
    id: '2-3',
    name: '防火墙',
    parentId: '2',
    parentName: '网络设备',
    description: '网络安全防护设备',
    assetCount: 8,
    createTime: '2023-01-01 10:15:00',
    updateTime: '2023-01-01 10:15:00'
  },
  {
    id: '3',
    name: '存储设备',
    parentId: null,
    parentName: '',
    description: '包括磁盘阵列、磁带库等存储设备',
    assetCount: 16,
    createTime: '2023-01-01 10:20:00',
    updateTime: '2023-01-01 10:20:00'
  },
  {
    id: '4',
    name: '办公设备',
    parentId: null,
    parentName: '',
    description: '包括电脑、打印机、扫描仪等办公设备',
    assetCount: 16,
    createTime: '2023-01-01 10:25:00',
    updateTime: '2023-01-01 10:25:00'
  }
];

// 表格列定义
const columns = [
  {
    title: '分类编号',
    dataIndex: 'id',
    key: 'id',
    fixed: 'left',
    width: 120
  },
  {
    title: '分类名称',
    dataIndex: 'name',
    key: 'name',
    width: 180
  },
  {
    title: '父级分类',
    dataIndex: 'parentName',
    key: 'parentName',
    width: 150
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    width: 250
  },
  {
    title: '资产数量',
    dataIndex: 'assetCount',
    key: 'assetCount',
    width: 100,
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
    keyword: searchKeyword.value,
    parentId: parentCategory.value
  });
  // 这里应该调用API获取数据
};

// 处理重置
const handleReset = () => {
  searchKeyword.value = '';
  parentCategory.value = '';
};

// 处理表格分页变化
const handleTableChange = (pagination, filters, sorter) => {
  console.log('分页变化:', pagination);
  // 这里应该根据分页信息重新获取数据
};

// 新增分类
const handleAddCategory = () => {
  console.log('新增分类');
  // 这里应该打开新增分类的模态框
};

// 处理编辑操作
const handleEdit = (id) => {
  console.log('编辑分类:', id);
  // 这里应该打开编辑分类的模态框
};

// 处理删除操作
const handleDelete = (id) => {
  console.log('删除分类:', id);
  // 这里应该显示确认删除的模态框，然后调用API删除分类
};
</script>

<style scoped>
.asset-category-list-container {
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
</style>