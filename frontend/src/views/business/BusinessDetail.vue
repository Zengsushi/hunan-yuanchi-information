<template>
  <div class="business-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <a-button type="text" @click="goBack" class="back-btn">
            <template #icon><ArrowLeftOutlined /></template>
            返回
          </a-button>
          <h2 class="page-title">
            <AppstoreOutlined class="title-icon" />
            {{ businessInfo.name || '业务详情' }}
          </h2>
        </div>
        <div class="header-actions">
          <a-space>
            <a-button @click="editBusiness">
              <template #icon><EditOutlined /></template>
              编辑
            </a-button>
            <a-button type="primary" @click="refreshData">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
          </a-space>
        </div>
      </div>
    </div>

    <!-- 业务基本信息 -->
    <div class="info-section">
      <a-card title="基本信息" :bordered="false">
        <a-row :gutter="24">
          <a-col :span="12">
            <div class="info-item">
              <span class="label">业务名称：</span>
              <span class="value">{{ businessInfo.name }}</span>
            </div>
          </a-col>
          <a-col :span="12">
            <div class="info-item">
              <span class="label">责任人：</span>
              <span class="value">
                <UserOutlined class="icon" />
                {{ businessInfo.responsible_person }}
              </span>
            </div>
          </a-col>
        </a-row>
        <a-row :gutter="24" style="margin-top: 16px">
          <a-col :span="12">
            <div class="info-item">
              <span class="label">上线日期：</span>
              <span class="value">
                <CalendarOutlined class="icon" />
                {{ formatDate(businessInfo.online_date) }}
              </span>
            </div>
          </a-col>
          <a-col :span="12">
            <div class="info-item">
              <span class="label">访问地址：</span>
              <span class="value">
                <a-button
                  v-if="businessInfo.access_url"
                  type="link"
                  size="small"
                  @click="openUrl(businessInfo.access_url)"
                >
                  <template #icon><LinkOutlined /></template>
                  {{ businessInfo.access_url }}
                </a-button>
                <span v-else class="no-data">未设置</span>
              </span>
            </div>
          </a-col>
        </a-row>
        <a-row :gutter="24" style="margin-top: 16px">
          <a-col :span="24">
            <div class="info-item">
              <span class="label">功能用途：</span>
              <span class="value">
                <span v-if="businessInfo.description" class="function-purpose-text">
                  {{ businessInfo.description }}
                </span>
                <span v-else class="no-data">暂无功能用途描述</span>
              </span>
            </div>
          </a-col>
        </a-row>
      </a-card>
    </div>



    <!-- 关联IP列表 -->
    <div class="ip-section">
      <a-card :bordered="false">
        <template #title>
          <div class="section-title">
            <GlobalOutlined class="title-icon" />
            关联IP列表
            <a-badge :count="relatedIPs.length" class="count-badge" />
          </div>
        </template>
        <template #extra>
          <a-space>
            <a-button size="small" @click="showAddIPModal">
              <template #icon><PlusOutlined /></template>
              添加IP
            </a-button>
            <a-button size="small" @click="refreshIPs">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
          </a-space>
        </template>
        
        <a-table
          :columns="ipColumns"
          :data-source="relatedIPs"
          :loading="ipLoading"
          :pagination="false"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'ip_address'">
              <div class="ip-info">
                <a-tag color="blue">{{ record.ip_address }}</a-tag>
              </div>
            </template>
            
            <template v-else-if="column.dataIndex === 'status'">
              <a-tag :color="getStatusColor(record.status)">
                {{ getStatusText(record.status) }}
              </a-tag>
            </template>
            
            <template v-else-if="column.dataIndex === 'service_type'">
              <a-tag color="purple">
                {{ getServiceTypeText(record.service_type) }}
              </a-tag>
            </template>
            
            <template v-else-if="column.dataIndex === 'ping_status'">
              <div class="ping-status">
                <span :class="['status-dot', record.ping_status]" />
                {{ getPingStatusText(record.ping_status) }}
              </div>
            </template>
            
            <template v-else-if="column.dataIndex === 'action'">
              <a-space>
                <a-tooltip title="移除关联">
                  <a-button
                    type="text"
                    size="small"
                    danger
                    @click="removeIP(record)"
                  >
                    <template #icon><DeleteOutlined /></template>
                  </a-button>
                </a-tooltip>
              </a-space>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <!-- 业务拓扑 -->
    <div class="topology-section">
      <a-card title="业务拓扑" :bordered="false">
        <template #extra>
          <a-space>
            <a-button size="small" @click="refreshTopology">
              <template #icon><ReloadOutlined /></template>
              刷新拓扑
            </a-button>
            <a-button size="small" @click="exportTopology">
              <template #icon><ExportOutlined /></template>
              导出
            </a-button>
            <!-- 拓扑图控制面板 -->
            <a-divider type="vertical" v-if="relatedIPs.length > 0" />
            <a-tag v-if="relatedIPs.length > 0" color="green" @click="resetNodePositions" style="cursor: pointer">
              重置位置
            </a-tag>
            <a-tag v-if="isConnecting" color="orange" @click="cancelConnection" style="cursor: pointer">
              <CloseOutlined /> 取消连线
            </a-tag>
            <a-tag v-if="customConnections.length > 0" color="red" @click="clearAllConnections" style="cursor: pointer">
              <DeleteOutlined /> 清除自定义连线
            </a-tag>
            <a-tag v-if="isConnecting" color="purple" class="connecting-tip">
              点击节点完成连线
            </a-tag>
          </a-space>
        </template>
        
        <div class="topology-container">
          <div v-if="topologyLoading" class="topology-loading">
            <a-spin size="large" />
            <p>正在生成业务拓扑图...</p>
          </div>
          <div v-else-if="relatedIPs.length === 0" class="no-topology">
            <a-empty description="暂无关联IP，无法生成拓扑图" />
          </div>
          <div v-else class="topology-content">
            <!-- 业务拓扑图 -->
            <div class="topology-layout">
              <!-- 左侧IP节点列表 -->
              <div class="ip-nodes-sidebar">
                <div class="sidebar-header">
                  <h4 class="sidebar-title">IP节点列表</h4>
                  <span class="node-count">{{ relatedIPs.length }} 个节点</span>
                </div>
                <div class="sidebar-nodes">
                  <div
                    v-for="(ip, index) in relatedIPs"
                    :key="ip.id"
                    class="sidebar-ip-node"
                    :class="[ip.ping_status, { 
                      'connecting-from': connectingFrom && connectingFrom.type === 'ip' && connectingFrom.id === ip.id 
                    }]"
                    @mousedown="startDragFromSidebar($event, ip)"
                    @click="handleSidebarNodeClick($event, ip)"
                    @contextmenu.prevent="startConnection({ type: 'ip', id: ip.id, name: ip.ip_address, x: 50, y: 50 + index * 90 })"
                  >
                    <div class="node-icon">
                      <component :is="getServiceIcon(ip.service_type)" />
                    </div>
                    <div class="node-info">
                      <div class="node-title">{{ ip.ip_address }}</div>
                      <div class="node-subtitle">{{ getServiceTypeText(ip.service_type) }}</div>
                    </div>
                    <div class="node-status" :class="ip.ping_status">
                      <span class="status-dot" />
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 主画布区域 -->
              <div class="main-canvas" :class="{ 'connecting-mode': isConnecting }">
                <!-- 网络连接层 -->
                <div class="topology-network" @mousemove="onMouseMove">
                  <svg width="100%" height="100%" class="connection-svg">
                    <!-- 定义箭头标记和渐变 -->
                    <defs>
                      <!-- 科技风渐变 -->
                      <linearGradient id="techGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#00d4ff;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#0099ff;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#0066ff;stop-opacity:1" />
                      </linearGradient>
                      
                      <!-- 发光效果滤镜 -->
                      <filter id="glow">
                        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                        <feMerge> 
                          <feMergeNode in="coloredBlur"/>
                          <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                      </filter>
                      
                      <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                              refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#1890ff" />
                      </marker>
                      <marker id="custom-arrowhead" markerWidth="12" markerHeight="8" 
                              refX="11" refY="4" orient="auto">
                        <polygon points="0 0, 12 4, 0 8" fill="url(#techGradient)" filter="url(#glow)" />
                      </marker>
                    </defs>
                    
                    <!-- 自定义连线 -->
                    <g>
                      <!-- 背景连线 -->
                      <line
                        v-for="connection in customConnections"
                        :key="'bg-' + connection.id"
                        :x1="connection.from.x"
                        :y1="connection.from.y"
                        :x2="connection.to.x"
                        :y2="connection.to.y"
                        stroke="#1a1a2e"
                        stroke-width="6"
                        class="connection-background"
                      />
                      <!-- 主连线 -->
                      <line
                        v-for="connection in customConnections"
                        :key="'main-' + connection.id"
                        :x1="connection.from.x"
                        :y1="connection.from.y"
                        :x2="connection.to.x"
                        :y2="connection.to.y"
                        stroke="url(#techGradient)"
                        stroke-width="3"
                        marker-end="url(#custom-arrowhead)"
                        class="custom-connection-line tech-line"
                        @click="removeConnection(connection.id)"
                      />
                      <!-- 流动光效 -->
                      <line
                        v-for="connection in customConnections"
                        :key="'flow-' + connection.id"
                        :x1="connection.from.x"
                        :y1="connection.from.y"
                        :x2="connection.to.x"
                        :y2="connection.to.y"
                        stroke="#00ffff"
                        stroke-width="1"
                        stroke-dasharray="10,20"
                        class="flow-effect"
                      />
                    </g>
                    
                    <!-- 临时连线（连线过程中显示） -->
                    <g v-if="tempConnection">
                      <!-- 临时连线背景 -->
                      <line
                        :x1="tempConnection.from.x"
                        :y1="tempConnection.from.y"
                        :x2="tempConnection.to.x"
                        :y2="tempConnection.to.y"
                        stroke="#1a1a2e"
                        stroke-width="4"
                        class="temp-connection-bg"
                      />
                      <!-- 临时连线主体 -->
                      <line
                        :x1="tempConnection.from.x"
                        :y1="tempConnection.from.y"
                        :x2="tempConnection.to.x"
                        :y2="tempConnection.to.y"
                        stroke="url(#techGradient)"
                        stroke-width="2"
                        stroke-dasharray="8,4"
                        class="temp-connection-line tech-temp-line"
                        filter="url(#glow)"
                      />
                    </g>
                  </svg>
                </div>
                
                <!-- 业务中心节点 -->
                <div 
                  class="business-center-node"
                  :class="{ 'connecting-from': connectingFrom && connectingFrom.type === 'business' }"
                  :style="{ left: businessInfo.x + 'px', top: businessInfo.y + 'px' }"
                  @mousedown="startBusinessDrag($event)"
                  @click="handleBusinessNodeClick($event)"
                  @contextmenu.prevent="startConnection({ type: 'business', id: businessInfo.id, name: businessInfo.name })"
                >
                  <AppstoreOutlined class="node-icon" />
                  <div class="node-info">
                    <div class="node-title">{{ businessInfo.name }}</div>
                    <div class="node-subtitle">业务中心</div>
                  </div>
                  <div v-if="connectingFrom && connectingFrom.type === 'business'" class="connecting-indicator">
                    连线起点
                  </div>
                </div>
                
                <!-- 画布中的IP节点（从侧边栏拖拽过来的） -->
                <div
                  v-for="ip in canvasIPs"
                  :key="'canvas-' + ip.id"
                  class="canvas-ip-node"
                  :class="[ip.ping_status, { 
                    'connecting-from': connectingFrom && connectingFrom.type === 'ip' && connectingFrom.id === ip.id 
                  }]"
                  :style="{
                    left: ip.x + 'px',
                    top: ip.y + 'px'
                  }"
                  @mousedown="startDrag($event, ip)"
                  @click="handleCanvasNodeClick($event, ip)"
                  @contextmenu.prevent="startConnection({ type: 'ip', id: ip.id, name: ip.ip_address, x: ip.x + 60, y: ip.y + 40 })"
                >
                  <div class="node-icon">
                    <component :is="getServiceIcon(ip.service_type)" />
                  </div>
                  <div class="node-info">
                    <div class="node-title">{{ ip.ip_address }}</div>
                    <div class="node-subtitle">{{ getServiceTypeText(ip.service_type) }}</div>
                  </div>
                  <div class="node-status" :class="ip.ping_status">
                    <span class="status-dot" />
                    {{ getPingStatusText(ip.ping_status) }}
                  </div>
                  <div v-if="connectingFrom && connectingFrom.type === 'ip' && connectingFrom.id === ip.id" class="connecting-indicator">
                    连线起点
                  </div>
                  <!-- 删除按钮 -->
                  <div class="node-remove-btn" @click.stop="removeCanvasNode(ip.id)" title="从画布移除">
                    <CloseOutlined />
                  </div>
                </div>
              </div>
            </div>
            </div>
            </div>

      </a-card>
    </div>

    <!-- 添加IP模态框 -->
    <a-modal
      v-model:open="addIPModalVisible"
      title="添加关联IP"
      @ok="handleAddIP"
      @cancel="handleCancelAddIP"
    >
      <a-form layout="vertical">
        <a-form-item label="选择IP" required>
          <a-select
            v-model:value="ipForm.ip_id"
            placeholder="请选择要关联的IP"
            show-search
            :filter-option="false"
            @search="handleIPSearch"
            :loading="ipLoading"
          >
            <a-select-option
              v-for="ip in availableIPs"
              :key="ip.id"
              :value="ip.id"
            >
              {{ ip.ip_address }} - {{ ip.hostname || '未知主机' }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="服务类型">
          <a-select
            v-model:value="ipForm.service_type"
            placeholder="请选择服务类型"
          >
            <a-select-option value="web">Web服务</a-select-option>
            <a-select-option value="database">数据库</a-select-option>
            <a-select-option value="cache">缓存服务</a-select-option>
            <a-select-option value="message_queue">消息队列</a-select-option>
            <a-select-option value="file_storage">文件存储</a-select-option>
            <a-select-option value="monitoring">监控服务</a-select-option>
            <a-select-option value="other">其他</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="关联说明">
          <a-textarea
            v-model:value="ipForm.description"
            placeholder="请输入关联说明（可选）"
            :rows="3"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 编辑业务模态框 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑业务"
      width="800px"
      @ok="handleEditSubmit"
      @cancel="handleEditCancel"
    >
      <a-form
        ref="editFormRef"
        :model="editForm"
        :rules="editFormRules"
        layout="vertical"
      >
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="业务名称" name="name">
              <a-input
                v-model:value="editForm.name"
                placeholder="请输入业务名称"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="上线日期" name="online_date">
              <a-date-picker
                v-model:value="editForm.online_date"
                style="width: 100%"
                format="YYYY-MM-DD"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="责任人" name="responsible_person">
              <a-input
                v-model:value="editForm.responsible_person"
                placeholder="请输入责任人"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="访问地址" name="access_url">
              <a-input
                v-model:value="editForm.access_url"
                placeholder="请输入访问地址"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="功能用途" name="function_purpose">
          <a-textarea
            v-model:value="editForm.function_purpose"
            placeholder="请输入功能用途"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="业务描述" name="description">
          <a-textarea
            v-model:value="editForm.description"
            placeholder="请输入业务描述"
            :rows="4"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message, Modal } from 'ant-design-vue';
import dayjs from 'dayjs';
import { businessAPI } from '@/api/businessManagement';
import { ipAPI } from '@/api/ipManagement';
import {
  ArrowLeftOutlined,
  AppstoreOutlined,
  EditOutlined,
  ReloadOutlined,
  TeamOutlined,
  UserOutlined,
  CalendarOutlined,
  LinkOutlined,
  GlobalOutlined,
  PlusOutlined,
  EyeOutlined,
  DeleteOutlined,
  ExportOutlined,
  NodeIndexOutlined,
  CloseOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
  MessageOutlined,
  FolderOutlined,
  SettingOutlined
} from '@ant-design/icons-vue';

const route = useRoute();
const router = useRouter();

// 响应式数据
const businessInfo = ref({});
const relatedIPs = ref([]);
const availableIPs = ref([]);
const loading = ref(false);
const ipLoading = ref(false);
const topologyLoading = ref(false);
const addIPModalVisible = ref(false);
const editModalVisible = ref(false);
const editFormRef = ref();

// 表单数据
const ipForm = reactive({
  ip_id: undefined,
  description: '',
  service_type: 'web'
});

// 拓扑图相关数据
const showConnections = ref(true);
const customConnections = ref([]);
const isConnecting = ref(false);
const connectingFrom = ref(null);
const tempConnection = ref(null);
const mousePosition = ref({ x: 0, y: 0 });
const isDragging = ref(false);
const dragTarget = ref(null);
const dragOffset = ref({ x: 0, y: 0 });
const canvasIPs = ref([]); // 画布中的IP节点

const editForm = reactive({
  name: '',
  responsible_person: '',
  online_date: null,
  access_url: '',
  function_purpose: '',
  description: ''
});

// 编辑表单验证规则
const editFormRules = {
  name: [{ required: true, message: '请输入业务名称', trigger: 'blur' }],
  responsible_person: [{ required: true, message: '请输入责任人', trigger: 'blur' }],
  online_date: [{ required: true, message: '请选择上线日期', trigger: 'change' }],
  access_url: [
    { 
      validator: (rule, value) => {
        if (!value || value.trim() === '') {
          return Promise.resolve();
        }
        return Promise.resolve();
      },
      trigger: 'blur'
    }
  ]
};

// IP列表表格列配置
const ipColumns = [
  {
    title: 'IP地址',
    dataIndex: 'ip_address',
    key: 'ip_address',
    width: 150
  },
  {
    title: '主机名',
    dataIndex: 'hostname',
    key: 'hostname',
    width: 150
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100
  },
  {
    title: '服务类型',
    dataIndex: 'service_type',
    key: 'service_type',
    width: 120
  },
  {
    title: 'Ping状态',
    dataIndex: 'ping_status',
    key: 'ping_status',
    width: 120
  },
  {
    title: '最后检测',
    dataIndex: 'last_seen',
    key: 'last_seen',
    width: 150,
    customRender: ({ text }) => formatDate(text)
  },
  {
    title: '关联说明',
    dataIndex: 'description',
    key: 'description',
    ellipsis: true
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    width: 100,
    fixed: 'right'
  }
];

// 方法
const fetchBusinessDetail = async () => {
  loading.value = true;
  try {
    const response = await businessAPI.getBusinessDetail(route.params.id);
    businessInfo.value = response.data;
    
    // 确保业务中心节点的坐标是数值类型
    if (!businessInfo.value.x || typeof businessInfo.value.x !== 'number') {
      businessInfo.value.x = 400; // 默认X坐标
    }
    if (!businessInfo.value.y || typeof businessInfo.value.y !== 'number') {
      businessInfo.value.y = 260; // 默认Y坐标
    }
  } catch (error) {
    message.error('获取业务详情失败');
  } finally {
    loading.value = false;
  }
};

const fetchRelatedIPs = async () => {
  ipLoading.value = true;
  try {
    const response = await businessAPI.getBusinessIPs(route.params.id);
    relatedIPs.value = response.data || [];
    
    // 数据加载完成后，重置IP节点位置
    nextTick(() => {
      resetNodePositions();
    });
  } catch (error) {
    message.error('获取关联IP失败');
  } finally {
    ipLoading.value = false;
  }
};

const fetchAvailableIPs = async (searchKeyword = '') => {
  try {
    const response = await ipAPI.getIPList({
      search: searchKeyword,
      page_size: 100 // 获取更多IP供选择
    });
    
    let allIPs = response.data.results || response.data || [];
    
    // 过滤掉已经关联到当前业务的IP
    const relatedIPIds = relatedIPs.value.map(ip => ip.ip_address);
    availableIPs.value = allIPs.filter(ip => !relatedIPIds.includes(ip.ip_address));
  } catch (error) {
    console.error('获取可用IP列表失败:', error);
    message.error('获取可用IP列表失败');
  }
};

const handleIPSearch = (value) => {
  fetchAvailableIPs(value);
};

const goBack = () => {
  router.go(-1);
};

const editBusiness = () => {
  // 将当前业务信息填充到编辑表单
  Object.assign(editForm, {
    name: businessInfo.value.name || '',
    responsible_person: businessInfo.value.responsible_person || '',
    online_date: businessInfo.value.online_date ? dayjs(businessInfo.value.online_date) : null,
    access_url: businessInfo.value.access_url || '',
    description: businessInfo.value.description || ''
  });
  editModalVisible.value = true;
};

const refreshData = () => {
  fetchBusinessDetail();
  fetchRelatedIPs();
};

const refreshIPs = () => {
  fetchRelatedIPs();
};

const refreshTopology = () => {
  topologyLoading.value = true;
  // 模拟拓扑图刷新
  setTimeout(() => {
    topologyLoading.value = false;
    message.success('拓扑图已刷新');
  }, 1500);
};

const exportTopology = () => {
  message.info('拓扑图导出功能开发中...');
};

const showAddIPModal = () => {
  fetchAvailableIPs();
  addIPModalVisible.value = true;
};

const handleAddIP = async () => {
  if (!ipForm.ip_id) {
    message.error('请选择要关联的IP');
    return;
  }
  
  try {
    // 找到选中的IP信息
    const selectedIP = availableIPs.value.find(ip => ip.id === ipForm.ip_id);
    if (!selectedIP) {
      message.error('选中的IP信息无效');
      return;
    }
    
    // 构造后端所需的数据格式
    const submitData = {
      ip_address: selectedIP.ip_address,
      hostname: selectedIP.hostname || '',
      description: ipForm.description || '',
      service_type: ipForm.service_type || 'web',
      status: 'unknown'
    };
    
    await businessAPI.addBusinessIP(route.params.id, submitData);
    message.success('IP关联成功');
    addIPModalVisible.value = false;
    Object.assign(ipForm, { ip_id: undefined, description: '', service_type: 'web' });
    fetchRelatedIPs();
  } catch (error) {
    console.error('IP关联失败:', error);
    message.error('IP关联失败');
  }
};

const handleCancelAddIP = () => {
  addIPModalVisible.value = false;
  Object.assign(ipForm, { ip_id: undefined, description: '', service_type: 'web' });
};

const handleEditSubmit = async () => {
  try {
    await editFormRef.value.validate();
    
    const submitData = {
      name: editForm.name,
      responsible_person: editForm.responsible_person,
      online_date: editForm.online_date ? dayjs(editForm.online_date).format('YYYY-MM-DD') : null,
      access_url: editForm.access_url && editForm.access_url.trim() ? editForm.access_url.trim() : null,
      function_purpose: editForm.function_purpose || '',
      description: editForm.description || ''
    };
    
    await businessAPI.updateBusiness(route.params.id, submitData);
    message.success('业务更新成功');
    editModalVisible.value = false;
    fetchBusinessDetail(); // 重新获取业务详情
  } catch (error) {
    if (error.errorFields) {
      message.error('请检查表单输入');
    } else {
      message.error('业务更新失败');
    }
  }
};

const handleEditCancel = () => {
  editModalVisible.value = false;
  editFormRef.value?.resetFields();
};

const removeIP = (record) => {
  Modal.confirm({
    title: '确认移除',
    content: `确定要移除IP "${record.ip_address}" 的关联吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        await businessAPI.removeBusinessIP(route.params.id, record.id);
        message.success('移除成功');
        fetchRelatedIPs();
      } catch (error) {
        message.error('移除失败');
      }
    }
  });
};

const viewIPDetail = (record) => {
  router.push({
    name: 'ipManagement',
    query: { highlight: record.ip_address }
  });
};

const openUrl = (url) => {
  if (url) {
    window.open(url, '_blank');
  }
};

const formatDate = (date) => {
  return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-';
};

const getStatusColor = (status) => {
  const colors = {
    'active': 'green',
    'inactive': 'red',
    'pending': 'orange',
    'unknown': 'default'
  };
  return colors[status] || 'default';
};

const getStatusText = (status) => {
  const texts = {
    'active': '活跃',
    'inactive': '非活跃',
    'pending': '待确认',
    'unknown': '未知'
  };
  return texts[status] || '未知';
};

const getPingStatusText = (status) => {
  const texts = {
    'online': '在线',
    'offline': '离线',
    'timeout': '超时'
  };
  return texts[status] || '未知';
};

const getServiceTypeText = (serviceType) => {
  const texts = {
    'web': 'Web服务',
    'database': '数据库',
    'cache': '缓存服务',
    'message_queue': '消息队列',
    'file_storage': '文件存储',
    'monitoring': '监控服务',
    'other': '其他'
  };
  return texts[serviceType] || '其他';
};

const filterOption = (input, option) => {
  return option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0;
};

// 计算节点中心点坐标的统一方法
const getNodeCenterCoordinates = (node) => {
  if (node.type === 'business') {
    // 业务中心节点：120x80px，中心点偏移60,40
    return {
      x: businessInfo.value.x + 60,
      y: businessInfo.value.y + 40
    };
  } else {
    // IP节点：120x80px，中心点偏移60,40
    return {
      x: (node.x || 0) + 60,
      y: (node.y || 0) + 40
    };
  }
};

// 自定义连线相关方法
const startConnection = (node) => {
  if (isConnecting.value) {
    // 如果已经在连线模式，完成连线
    finishConnection(node);
  } else {
    // 开始连线
    isConnecting.value = true;
    connectingFrom.value = { ...node };
    
    // 计算起点坐标
    const centerCoords = getNodeCenterCoordinates(node);
    connectingFrom.value.x = centerCoords.x;
    connectingFrom.value.y = centerCoords.y;
  }
};

const finishConnection = (toNode) => {
  if (!connectingFrom.value || !toNode) return;
  
  // 不能连接到自己
  if (connectingFrom.value.type === toNode.type && connectingFrom.value.id === toNode.id) {
    return;
  }
  
  // 计算目标节点的中心点坐标
  const toCenterCoords = getNodeCenterCoordinates(toNode);
  const toX = toCenterCoords.x;
  const toY = toCenterCoords.y;
  
  // 创建连线
  const connection = {
    id: Date.now() + Math.random(),
    from: {
      type: connectingFrom.value.type,
      id: connectingFrom.value.id,
      name: connectingFrom.value.name,
      x: connectingFrom.value.x,
      y: connectingFrom.value.y
    },
    to: {
      type: toNode.type,
      id: toNode.id,
      name: toNode.name,
      x: toX,
      y: toY
    }
  };
  
  customConnections.value.push(connection);
  
  // 重置连线状态
  isConnecting.value = false;
  connectingFrom.value = null;
  tempConnection.value = null;
  
  message.success(`已创建从 ${connection.from.name} 到 ${connection.to.name} 的连线`);
};

const cancelConnection = () => {
  isConnecting.value = false;
  connectingFrom.value = null;
  tempConnection.value = null;
};

const removeConnection = (connectionId) => {
  const index = customConnections.value.findIndex(conn => conn.id === connectionId);
  if (index > -1) {
    customConnections.value.splice(index, 1);
    message.success('连线已删除');
  }
};

const clearAllConnections = () => {
  Modal.confirm({
    title: '确认清除',
    content: '确定要清除所有自定义连线吗？',
    onOk() {
      customConnections.value = [];
      message.success('已清除所有自定义连线');
    }
  });
};

const getNodeCenter = (node) => {
  return {
    x: node.x + 60, // 节点宽度的一半
    y: node.y + 40  // 节点高度的一半
  };
};

const onMouseMove = (event) => {
  if (isConnecting.value && connectingFrom.value) {
    const rect = event.currentTarget.getBoundingClientRect();
    mousePosition.value = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
    
    tempConnection.value = {
      from: {
        x: connectingFrom.value.x,
        y: connectingFrom.value.y
      },
      to: {
        x: mousePosition.value.x,
        y: mousePosition.value.y
      }
    };
  }
};

// 获取节点默认位置（围绕中心点排列）
const getDefaultNodePosition = (index) => {
  // 获取业务中心节点的中心坐标
  const businessCenter = getNodeCenterCoordinates({ type: 'business' });
  const centerX = businessCenter.x;
  const centerY = businessCenter.y;
  const radius = 150; // 围绕中心的半径
  const totalNodes = relatedIPs.value.length;
  
  if (totalNodes === 1) {
    // 单个节点放在中心右侧
    return { x: centerX + 120, y: centerY - 40 };
  }
  
  // 多个节点围绕中心排列
  const angle = (2 * Math.PI * index) / totalNodes;
  const x = centerX + radius * Math.cos(angle) - 60; // 减去节点宽度的一半
  const y = centerY + radius * Math.sin(angle) - 40; // 减去节点高度的一半
  
  return { x: Math.max(0, x), y: Math.max(0, y) };
};

const resetNodePositions = () => {
  relatedIPs.value.forEach((ip, index) => {
    const pos = getDefaultNodePosition(index);
    ip.x = pos.x;
    ip.y = pos.y;
  });
  message.success('节点位置已重置');
};

// 处理侧边栏节点点击事件
const handleSidebarNodeClick = (event, ip) => {
  // 如果刚刚完成拖拽，不触发连线
  if (isDragging.value) {
    return;
  }
  
  // 检查是否已在画布中
  const existsInCanvas = canvasIPs.value.find(canvasIP => canvasIP.id === ip.id);
  if (existsInCanvas) {
    message.info('该IP节点已在画布中');
    return;
  }
  
  // 显示IP详情或其他操作
  console.log('点击侧边栏IP节点:', ip);
};

// 处理画布节点点击事件
const handleCanvasNodeClick = (event, ip) => {
  // 如果刚刚完成拖拽，不触发连线
  if (isDragging.value) {
    return;
  }
  
  // 触发连线
  startConnection({ 
    type: 'ip', 
    id: ip.id, 
    name: ip.ip_address, 
    x: ip.x, 
    y: ip.y 
  });
};

// 从画布移除IP节点
const removeCanvasNode = (ipId) => {
  const index = canvasIPs.value.findIndex(ip => ip.id === ipId);
  if (index !== -1) {
    canvasIPs.value.splice(index, 1);
    
    // 移除相关连线
    customConnections.value = customConnections.value.filter(conn => 
      !(conn.from.id === ipId || conn.to.id === ipId)
    );
    
    message.success('已从画布移除IP节点');
  }
};

// 处理业务节点点击事件
const handleBusinessNodeClick = (event) => {
  // 如果刚刚完成拖拽，不触发连线
  if (isDragging.value) {
    return;
  }
  
  // 触发连线
  startConnection({ type: 'business', id: businessInfo.value.id, name: businessInfo.value.name });
};

const startDrag = (event, ip) => {
  if (isConnecting.value) return; // 连线模式下不允许拖拽
  
  isDragging.value = true;
  dragTarget.value = ip;
  
  // 获取容器的位置
  const container = document.querySelector('.main-canvas');
  if (!container) return;
  
  const containerRect = container.getBoundingClientRect();
  
  // 设置较小的偏移，让节点中心跟随鼠标
  dragOffset.value = {
    x: 60, // 节点宽度的一半
    y: 40  // 节点高度的一半
  };
  
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('mouseup', stopDrag);
  event.preventDefault();
  event.stopPropagation();
};

// 从侧边栏拖拽IP节点到画布
const startDragFromSidebar = (event, ip) => {
  if (isConnecting.value) return; // 连线模式下不允许拖拽
  
  // 检查IP是否已经在画布中
  const existingIndex = canvasIPs.value.findIndex(canvasIP => canvasIP.id === ip.id);
  if (existingIndex !== -1) {
    message.warning('该IP节点已在画布中');
    return;
  }
  
  // 创建新的画布IP节点
  const newCanvasIP = {
    ...ip,
    x: 100, // 默认位置
    y: 100
  };
  
  canvasIPs.value.push(newCanvasIP);
  
  isDragging.value = true;
  dragTarget.value = newCanvasIP;
  
  // 设置较小的偏移，让节点中心跟随鼠标
  dragOffset.value = {
    x: 60, // 节点宽度的一半
    y: 40  // 节点高度的一半
  };
  
  document.addEventListener('mousemove', onCanvasDrag);
  document.addEventListener('mouseup', stopCanvasDrag);
  event.preventDefault();
  event.stopPropagation();
};

// 业务中心节点拖拽处理
const startBusinessDrag = (event) => {
  if (isConnecting.value) return; // 连线模式下不允许拖拽
  
  isDragging.value = true;
  dragTarget.value = { type: 'business', data: businessInfo.value };
  
  // 获取容器的位置
  const container = document.querySelector('.enhanced-topology');
  if (!container) return;
  
  const containerRect = container.getBoundingClientRect();
  
  // 设置较小的偏移，让节点中心跟随鼠标
  dragOffset.value = {
    x: 60, // 节点宽度的一半
    y: 40  // 节点高度的一半
  };
  
  document.addEventListener('mousemove', onBusinessDrag);
  document.addEventListener('mouseup', stopBusinessDrag);
  event.preventDefault();
  event.stopPropagation();
};

const onDrag = (event) => {
  if (!isDragging.value || !dragTarget.value) return;
  
  const container = document.querySelector('.main-canvas');
  if (!container) return;
  
  const rect = container.getBoundingClientRect();
  
  // 计算新位置（鼠标位置减去偏移量）
  const newX = event.clientX - rect.left - dragOffset.value.x;
  const newY = event.clientY - rect.top - dragOffset.value.y;
  
  // 限制在容器范围内
  dragTarget.value.x = Math.max(0, Math.min(newX, rect.width - 120));
  dragTarget.value.y = Math.max(0, Math.min(newY, rect.height - 80));
  
  // 更新相关的自定义连线
  const centerCoords = getNodeCenterCoordinates(dragTarget.value);
  customConnections.value.forEach(connection => {
    if (connection.from.type === 'ip' && connection.from.id === dragTarget.value.id) {
      connection.from.x = centerCoords.x;
      connection.from.y = centerCoords.y;
    }
    if (connection.to.type === 'ip' && connection.to.id === dragTarget.value.id) {
      connection.to.x = centerCoords.x;
      connection.to.y = centerCoords.y;
    }
  });
};

const stopDrag = () => {
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('mouseup', stopDrag);
  
  // 延迟重置拖拽状态，避免立即触发点击事件
  setTimeout(() => {
    isDragging.value = false;
    dragTarget.value = null;
  }, 100);
};

// 画布IP节点拖拽移动
const onCanvasDrag = (event) => {
  if (!isDragging.value || !dragTarget.value) return;
  
  const container = document.querySelector('.main-canvas');
  if (!container) return;
  
  const rect = container.getBoundingClientRect();
  
  // 计算新位置（鼠标位置减去偏移量）
  const newX = event.clientX - rect.left - dragOffset.value.x;
  const newY = event.clientY - rect.top - dragOffset.value.y;
  
  // 限制在容器范围内
  dragTarget.value.x = Math.max(0, Math.min(newX, rect.width - 120));
  dragTarget.value.y = Math.max(0, Math.min(newY, rect.height - 80));
  
  // 更新相关的自定义连线
  const centerCoords = getNodeCenterCoordinates(dragTarget.value);
  customConnections.value.forEach(connection => {
    if (connection.from.type === 'ip' && connection.from.id === dragTarget.value.id) {
      connection.from.x = centerCoords.x;
      connection.from.y = centerCoords.y;
    }
    if (connection.to.type === 'ip' && connection.to.id === dragTarget.value.id) {
      connection.to.x = centerCoords.x;
      connection.to.y = centerCoords.y;
    }
  });
};

// 停止画布IP节点拖拽
const stopCanvasDrag = () => {
  document.removeEventListener('mousemove', onCanvasDrag);
  document.removeEventListener('mouseup', stopCanvasDrag);
  
  // 延迟重置拖拽状态，避免立即触发点击事件
  setTimeout(() => {
    isDragging.value = false;
    dragTarget.value = null;
  }, 100);
};

// 业务中心节点拖拽移动
const onBusinessDrag = (event) => {
  if (!isDragging.value || !dragTarget.value || dragTarget.value.type !== 'business') return;
  
  const container = document.querySelector('.main-canvas');
  if (!container) return;
  
  const rect = container.getBoundingClientRect();
  
  // 计算新位置（鼠标位置减去偏移量）
  const newX = event.clientX - rect.left - dragOffset.value.x;
  const newY = event.clientY - rect.top - dragOffset.value.y;
  
  // 限制在容器范围内
  businessInfo.value.x = Math.max(0, Math.min(newX, rect.width - 120));
  businessInfo.value.y = Math.max(0, Math.min(newY, rect.height - 80));
  
  // 更新相关的自定义连线
  const centerCoords = getNodeCenterCoordinates({ type: 'business' });
  customConnections.value.forEach(connection => {
    if (connection.from.type === 'business') {
      connection.from.x = centerCoords.x;
      connection.from.y = centerCoords.y;
    }
    if (connection.to.type === 'business') {
      connection.to.x = centerCoords.x;
      connection.to.y = centerCoords.y;
    }
  });
};

// 业务中心节点停止拖拽
const stopBusinessDrag = () => {
  document.removeEventListener('mousemove', onBusinessDrag);
  document.removeEventListener('mouseup', stopBusinessDrag);
  
  // 延迟重置拖拽状态，避免立即触发点击事件
  setTimeout(() => {
    isDragging.value = false;
    dragTarget.value = null;
  }, 100);
};

const getServiceIcon = (serviceType) => {
  const icons = {
    'web': 'GlobalOutlined',
    'database': 'DatabaseOutlined',
    'cache': 'ThunderboltOutlined',
    'message_queue': 'MessageOutlined',
    'file_storage': 'FolderOutlined',
    'monitoring': 'EyeOutlined',
    'other': 'SettingOutlined'
  };
  return icons[serviceType] || 'SettingOutlined';
};

// 生命周期
onMounted(() => {
  fetchBusinessDetail();
  fetchRelatedIPs();
});
</script>

<style scoped>
.business-detail {
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 24px;
  border-radius: 8px;
}

.header-left {
  display: flex;
  align-items: center;
}

.back-btn {
  margin-right: 16px;
  color: #666;
}

.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #262626;
  display: flex;
  align-items: center;
}

.title-icon {
  margin-right: 8px;
  color: #1890ff;
}

.info-section,
.ip-section,
.topology-section {
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.label {
  font-weight: 500;
  color: #666;
  margin-right: 8px;
  min-width: 80px;
}

.value {
  color: #262626;
  display: flex;
  align-items: center;
}

.icon {
  margin-right: 4px;
  color: #1890ff;
}

.no-data {
  color: #ccc;
}

.function-purpose-text {
  line-height: 1.6;
  color: #262626;
}

.section-title {
  display: flex;
  align-items: center;
}

.count-badge {
  margin-left: 8px;
}

.ip-info {
  display: flex;
  align-items: center;
}

.ping-status {
  display: flex;
  align-items: center;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  animation: pulse 2s infinite;
}

.status-dot.online {
  background-color: #52c41a;
}

.status-dot.offline {
  background-color: #ff4d4f;
}

.status-dot.timeout {
  background-color: #faad14;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(82, 196, 26, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(82, 196, 26, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(82, 196, 26, 0);
  }
}

.topology-container {
  min-height: 300px;
  width: 100%;
  overflow-x: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.topology-loading {
  text-align: center;
  color: #666;
}

.topology-placeholder {
  text-align: center;
  color: #666;
}

.topology-icon {
  font-size: 48px;
  color: #1890ff;
  margin-bottom: 16px;
}

.topology-desc {
  color: #999;
  margin-bottom: 24px;
}

.simple-topology {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.business-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: #e6f7ff;
  border: 2px solid #1890ff;
  border-radius: 8px;
  font-weight: 500;
}

/* 增强拓扑图样式 - 蓝色简约风格 */
.topology-layout {
  display: flex;
  width: 100%;
  height: 600px;
  border: 2px solid #1890ff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.1);
  margin: 16px 0;
}

.ip-nodes-sidebar {
  width: 250px;
  background: linear-gradient(180deg, #f0f8ff 0%, #e6f3ff 100%);
  border-right: 1px solid #d9d9d9;
  padding: 16px;
  overflow-y: auto;
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: #1890ff;
  margin-bottom: 12px;
  text-align: center;
}

.sidebar-ip-node {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s ease;
}

.sidebar-ip-node:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.sidebar-ip-node:active {
  cursor: grabbing;
}

.main-canvas {
  flex: 1;
  position: relative;
  background: linear-gradient(135deg, #f8fbff 0%, #f0f7ff 50%, #e8f3ff 100%);
  overflow: visible;
}

.enhanced-topology {
  position: relative;
  width: 100%;
  height: 600px;
  background: linear-gradient(135deg, #f8fbff 0%, #f0f7ff 50%, #e8f3ff 100%);
  border: 1px solid rgba(0, 102, 255, 0.2);
  border-radius: 20px;
  overflow: visible;
  box-shadow: 0 8px 32px rgba(0, 102, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.8);
  margin: 16px 0;
  backdrop-filter: blur(10px);
}



.topology-network {
  position: relative;
  width: 100%;
  height: 100%;
}

.connection-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.connection-lines line {
  pointer-events: stroke;
}

.connection-line {
  transition: all 0.3s ease;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.connection-line.success {
  stroke: #52c41a;
  animation: pulse-success 2s infinite;
}

.connection-line.failed {
  stroke: #ff4d4f;
  animation: pulse-failed 2s infinite;
}

.connection-line.timeout {
  stroke: #faad14;
  animation: pulse-timeout 2s infinite;
}

@keyframes pulse-success {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes pulse-failed {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

@keyframes pulse-timeout {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.9; }
}

.center-node {
  position: absolute;
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.3);
  border: 3px solid #ffffff;
  transition: all 0.3s ease;
  z-index: 10;
}

.center-node:hover {
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.4);
}

.business-center {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
}

.ip-topology-node {
  position: absolute;
  width: 80px;
  height: 80px;
  background: #ffffff;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #1890ff;
  font-size: 11px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.15);
  border: 2px solid #1890ff;
  transition: all 0.3s ease;
  cursor: move;
  user-select: none;
  z-index: 5;
}

.ip-topology-node:hover {
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.25);
  background: #f0f8ff;
}

.ip-topology-node.success {
  background: #f6ffed;
  border-color: #52c41a;
  color: #52c41a;
}

.ip-topology-node.failed {
  background: #fff2f0;
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.ip-topology-node.timeout {
  background: #fffbe6;
  border-color: #faad14;
  color: #faad14;
}

.node-icon {
  font-size: 24px;
  margin-bottom: 4px;
  opacity: 0.8;
}

.center-node .node-icon {
  font-size: 32px;
  color: rgba(255, 255, 255, 0.9);
}

.node-info {
  text-align: center;
  line-height: 1.2;
}

.node-title {
  font-weight: 600;
  font-size: 12px;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70px;
}

.center-node .node-title {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.95);
  max-width: 100px;
}

.node-subtitle {
  font-size: 10px;
  opacity: 0.7;
  white-space: nowrap;
}

.center-node .node-subtitle {
  color: rgba(255, 255, 255, 0.8);
}

.node-type {
  font-size: 9px;
  opacity: 0.6;
  margin-top: 2px;
}

.node-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  margin-top: 4px;
  padding: 2px 6px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
}

.node-status.success {
  color: #52c41a;
  background: rgba(82, 196, 26, 0.1);
}

.node-status.failed {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
}

.node-status.timeout {
  color: #faad14;
  background: rgba(250, 173, 20, 0.1);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.success {
  background-color: #52c41a;
  box-shadow: 0 0 6px rgba(82, 196, 26, 0.6);
}

.status-dot.failed {
  background-color: #ff4d4f;
  box-shadow: 0 0 6px rgba(255, 77, 79, 0.6);
}

.status-dot.timeout {
  background-color: #faad14;
  box-shadow: 0 0 6px rgba(250, 173, 20, 0.6);
}

/* 自定义连线相关样式 */
.connecting-mode {
  cursor: crosshair !important;
  transition: all 0.3s ease;
}

.connecting-mode:hover {
  box-shadow: 0 0 15px rgba(24, 144, 255, 0.5);
}

.connecting-from {
  border: 2px solid #1890ff;
  box-shadow: 0 0 10px rgba(24, 144, 255, 0.6);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 10px rgba(24, 144, 255, 0.6);
  }
  50% {
    box-shadow: 0 0 20px rgba(24, 144, 255, 0.8);
  }
  100% {
    box-shadow: 0 0 10px rgba(24, 144, 255, 0.6);
  }
}

.connecting-indicator {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  background: #1890ff;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
  z-index: 1000;
}

.connecting-indicator::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: #1890ff;
}

/* 连线背景样式 */
.connection-background {
  opacity: 0.3;
}

/* 主连线样式 */
.custom-connection-line {
  transition: all 0.3s ease;
  filter: url(#glow);
}

.custom-connection-line:hover {
  stroke-width: 4;
  filter: url(#glow) brightness(1.5);
}

/* 科技风连线动画 */
.tech-line {
  animation: techPulse 2s ease-in-out infinite;
}

@keyframes techPulse {
  0%, 100% {
    opacity: 0.8;
    stroke-width: 3;
  }
  50% {
    opacity: 1;
    stroke-width: 3.5;
  }
}

/* 流动光效动画 */
.flow-effect {
  animation: flowAnimation 2s linear infinite;
  opacity: 0.7;
}

@keyframes flowAnimation {
  0% {
    stroke-dashoffset: 0;
  }
  100% {
    stroke-dashoffset: 30;
  }
}

/* 临时连线样式 */
.temp-connection-line {
  pointer-events: none;
}

.temp-connection-bg {
  opacity: 0.2;
}

.tech-temp-line {
  animation: tempLineFlow 1s linear infinite;
}

@keyframes tempLineFlow {
  0% {
    stroke-dashoffset: 0;
    opacity: 0.6;
  }
  100% {
    stroke-dashoffset: 12;
    opacity: 0.9;
  }
}

.topology-controls .ant-tag {
  margin: 0;
  animation: blink 1s infinite;
}

/* 头部控制标签样式 */
.ant-card-extra .ant-tag {
  margin: 2px;
  font-size: 12px;
  border-radius: 6px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.ant-card-extra .ant-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.ant-card-extra .connecting-tip {
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0.5;
  }
}

.ip-nodes {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
  max-width: 600px;
}

.ip-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 12px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 6px;
  font-size: 12px;
  min-width: 80px;
}

.ip-node.offline {
  background: #fff2f0;
  border-color: #ffccc7;
}

.ip-node.timeout {
  background: #fffbe6;
  border-color: #ffe58f;
}

.more-nodes {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  background: #fafafa;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  color: #666;
  font-size: 12px;
}

@media (max-width: 768px) {
  .business-detail {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left {
    justify-content: center;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .label {
    margin-bottom: 4px;
  }
  
  .ip-nodes {
    max-width: 100%;
  }
}

/* 自定义连线功能样式 */
.connecting-mode {
  cursor: crosshair;
}

.connecting-mode .ip-topology-node:hover,
.connecting-mode .business-center-node:hover {
  box-shadow: 0 0 20px rgba(0, 102, 255, 0.6);
  border-color: rgba(0, 102, 255, 0.8);
}

.connecting-from {
  animation: pulse 1.5s infinite;
  box-shadow: 0 0 20px rgba(24, 144, 255, 0.8) !important;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 20px rgba(24, 144, 255, 0.8);
  }
  50% {
    box-shadow: 0 0 30px rgba(24, 144, 255, 1);
  }
  100% {
    box-shadow: 0 0 20px rgba(24, 144, 255, 0.8);
  }
}

.connecting-indicator {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  background: #1890ff;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
  z-index: 10;
}

.connecting-indicator::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: #1890ff;
}

.custom-connection-line {
  cursor: pointer;
  transition: stroke-width 0.2s;
}

.custom-connection-line:hover {
  stroke-width: 5;
  stroke: #ff4d4f;
}

.temp-connection-line {
  pointer-events: none;
}



@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0.5;
  }
}

.business-center-node {
  position: absolute;
  width: 120px;
  height: 80px;
  background: #1890ff;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #1890ff;
  z-index: 5;
}

.business-center-node:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

.business-center-node .node-icon {
  font-size: 24px;
  margin-bottom: 4px;
}

.business-center-node .node-info {
  text-align: center;
}

.business-center-node .node-title {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 2px;
}

.business-center-node .node-subtitle {
  font-size: 10px;
  opacity: 0.8;
}
.topology-content{
  width: 100%;
}

/* 画布中的IP节点样式 */
.canvas-ip-node {
  position: absolute;
  width: 120px;
  height: 80px;
  background: #f0f8ff;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #1890ff;
  font-size: 11px;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #d9d9d9;
  transition: all 0.2s ease;
  cursor: move;
  user-select: none;
  z-index: 5;
}



.canvas-ip-node:hover {
  background: #e6f7ff;
  border-color: #1890ff;
}

.canvas-ip-node.success {
  background: #f6ffed;
  border-color: #52c41a;
  color: #389e0d;
}

.canvas-ip-node.failed {
  background: #fff2f0;
  border-color: #ff4d4f;
  color: #cf1322;
}

.canvas-ip-node.timeout {
  background: #fffbe6;
  border-color: #faad14;
  color: #d48806;
}

.canvas-ip-node.connecting-from {
  background: #e6f7ff;
  border-color: #1890ff;
  color: #1890ff;
  border-width: 2px;
}

.canvas-ip-node .node-icon {
  font-size: 24px;
  margin-bottom: 4px;
  opacity: 0.8;
}

.canvas-ip-node .node-info {
  text-align: center;
  line-height: 1.2;
}

.canvas-ip-node .node-title {
  font-weight: 600;
  font-size: 12px;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}

.canvas-ip-node .node-subtitle {
  font-size: 10px;
  opacity: 0.7;
  white-space: nowrap;
}

.canvas-ip-node .node-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  margin-top: 4px;
  padding: 2px 6px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
}

.canvas-ip-node .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.canvas-ip-node.success .status-dot {
  background: #52c41a;
}

.canvas-ip-node.failed .status-dot {
  background: #ff4d4f;
}

.canvas-ip-node.timeout .status-dot {
  background: #faad14;
}

.canvas-ip-node .connecting-indicator {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  background: #1890ff;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 10px;
  white-space: nowrap;
  z-index: 10;
}

.canvas-ip-node .connecting-indicator::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 4px solid transparent;
  border-top-color: #1890ff;
}

/* 删除按钮样式 */
.node-remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  background: #ff4d4f;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
  z-index: 10;
}

.canvas-ip-node:hover .node-remove-btn {
  opacity: 1;
}

.node-remove-btn:hover {
  background: #ff7875;
  transform: scale(1.1);
}

/* 优化侧边栏样式 */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-title {
  margin: 0;
  color: #1890ff;
  font-size: 14px;
  font-weight: 600;
}

.node-count {
  color: #666;
  font-size: 12px;
  background: #f0f0f0;
  padding: 2px 8px;
  border-radius: 12px;
}

.sidebar-ip-node:hover {
  transform: translateY(-1px);
}
</style>