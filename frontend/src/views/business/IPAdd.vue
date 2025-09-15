<template>
  <div class="ip-add-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <a-button type="text" @click="goBack" class="back-btn">
            <template #icon><ArrowLeftOutlined /></template>
            返回
          </a-button>
          <div class="page-title">
            <h2>
              <PlusOutlined class="title-icon" />
              新增IP地址
            </h2>
            <p class="page-description">添加新的IP地址记录到系统中</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 表单内容 -->
    <div class="form-container">
      <a-card :bordered="false" class="form-card">
        <a-form
          ref="formRef"
          :model="formData"
          :rules="formRules"
          layout="vertical"
          @finish="handleSubmit"
        >
          <a-row :gutter="24">
            <!-- 基本信息 -->
            <a-col :span="24">
              <div class="form-section">
                <h3 class="section-title">
                  <InfoCircleOutlined class="section-icon" />
                  基本信息
                </h3>
                <a-row :gutter="16">
                  <a-col :lg="12" :md="24">
                    <a-form-item label="IP地址" name="ip_address" required>
                      <a-input
                        v-model:value="formData.ip_address"
                        placeholder="请输入IP地址，如：192.168.1.100"
                        size="large"
                      >
                        <template #prefix><GlobalOutlined /></template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                  <a-col :lg="12" :md="24">
                    <a-form-item label="主机名" name="hostname">
                      <a-input
                        v-model:value="formData.hostname"
                        placeholder="请输入主机名（可选）"
                        size="large"
                      >
                        <template #prefix><DesktopOutlined /></template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                </a-row>
                <a-row :gutter="16">
                  <a-col :lg="12" :md="24">
                    <a-form-item label="IP状态" name="status" required>
                      <a-select
                        v-model:value="formData.status"
                        placeholder="请选择IP状态"
                        size="large"
                      >
                        <a-select-option value="active">
                          <CheckCircleOutlined style="color: #52c41a" /> 在用
                        </a-select-option>
                        <a-select-option value="available">
                          <ClockCircleOutlined style="color: #1890ff" /> 可用
                        </a-select-option>
                        <a-select-option value="reserved">
                          <LockOutlined style="color: #fa8c16" /> 预留
                        </a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                  <a-col :lg="12" :md="24">
                    <a-form-item label="IP类型" name="type" required>
                      <a-select
                        v-model:value="formData.type"
                        placeholder="请选择IP类型"
                        size="large"
                      >
                        <a-select-option value="static">
                          <DatabaseOutlined style="color: #1890ff" /> 静态IP
                        </a-select-option>
                        <a-select-option value="dynamic">
                          <ThunderboltOutlined style="color: #52c41a" /> 动态IP
                        </a-select-option>
                        <a-select-option value="gateway">
                          <NodeIndexOutlined style="color: #fa8c16" /> 网关
                        </a-select-option>
                        <a-select-option value="dns">
                          <CloudOutlined style="color: #722ed1" /> DNS服务器
                        </a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                </a-row>
              </div>
            </a-col>

            <!-- 网络信息 -->
            <a-col :span="24">
              <div class="form-section">
                <h3 class="section-title">
                  <NetworkOutlined class="section-icon" />
                  网络信息
                </h3>
                <a-row :gutter="16">
                  <a-col :lg="12" :md="24">
                    <a-form-item label="MAC地址" name="mac_address">
                      <a-input
                        v-model:value="formData.mac_address"
                        placeholder="请输入MAC地址（可选）"
                        size="large"
                      >
                        <template #prefix><WifiOutlined /></template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                  <a-col :lg="12" :md="24">
                    <a-form-item label="所属网段" name="subnet">
                      <a-input
                        v-model:value="formData.subnet"
                        placeholder="请输入所属网段（可选）"
                        size="large"
                      >
                        <template #prefix><ClusterOutlined /></template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                </a-row>
                <a-row :gutter="16">
                  <a-col :span="24">
                    <a-form-item label="关联设备" name="device">
                      <a-input
                        v-model:value="formData.device"
                        placeholder="请输入关联设备信息（可选）"
                        size="large"
                      >
                        <template #prefix><LaptopOutlined /></template>
                      </a-input>
                    </a-form-item>
                  </a-col>
                </a-row>
              </div>
            </a-col>

            <!-- 备注信息 -->
            <a-col :span="24">
              <div class="form-section">
                <h3 class="section-title">
                  <FileTextOutlined class="section-icon" />
                  备注信息
                </h3>
                <a-form-item label="备注" name="description">
                  <a-textarea
                    v-model:value="formData.description"
                    placeholder="请输入备注信息（可选）"
                    :rows="4"
                    size="large"
                  />
                </a-form-item>
              </div>
            </a-col>
          </a-row>

          <!-- 表单操作按钮 -->
          <div class="form-actions">
            <a-space size="large">
              <a-button size="large" @click="goBack">
                取消
              </a-button>
              <a-button 
                type="primary" 
                size="large" 
                html-type="submit"
                :loading="submitting"
              >
                <template #icon><SaveOutlined /></template>
                保存
              </a-button>
            </a-space>
          </div>
        </a-form>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { ipAPI } from '@/api';
import {
  ArrowLeftOutlined,
  PlusOutlined,
  InfoCircleOutlined,
  GlobalOutlined,
  DesktopOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  LockOutlined,
  DatabaseOutlined,
  ThunderboltOutlined,
  NodeIndexOutlined,
  CloudOutlined,
  NetworkOutlined,
  WifiOutlined,
  ClusterOutlined,
  LaptopOutlined,
  FileTextOutlined,
  SaveOutlined
} from '@ant-design/icons-vue';

const router = useRouter();
const formRef = ref();
const submitting = ref(false);

// 表单数据
const formData = reactive({
  ip_address: '',
  hostname: '',
  status: 'available',
  type: 'static',
  mac_address: '',
  device: '',
  subnet: '',
  description: ''
});

// 表单验证规则
const formRules = {
  ip_address: [
    { required: true, message: '请输入IP地址', trigger: 'blur' },
    {
      pattern: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
      message: '请输入有效的IP地址格式',
      trigger: 'blur'
    }
  ],
  status: [
    { required: true, message: '请选择IP状态', trigger: 'change' }
  ],
  type: [
    { required: true, message: '请选择IP类型', trigger: 'change' }
  ],
  mac_address: [
    {
      pattern: /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/,
      message: '请输入有效的MAC地址格式',
      trigger: 'blur'
    }
  ]
};

// 返回上一页
const goBack = () => {
  router.go(-1);
};

// 提交表单
const handleSubmit = async () => {
  try {
    submitting.value = true;
    
    // 构造提交数据
    const submitData = {
      ip_address: formData.ip_address,
      hostname: formData.hostname || null,
      status: formData.status,
      type: formData.type,
      mac_address: formData.mac_address || null,
      device: formData.device || null,
      subnet: formData.subnet || null,
      description: formData.description || null
    };
    
    // 调用API创建IP记录
    await ipAPI.createIP(submitData);
    
    message.success('IP地址添加成功！');
    
    // 返回IP列表页面
    router.push({ name: 'ipManagement' });
    
  } catch (error) {
    console.error('创建IP失败:', error);
    
    // 处理错误信息
    if (error.response?.data?.detail) {
      message.error(error.response.data.detail);
    } else if (error.response?.data?.ip_address) {
      message.error(error.response.data.ip_address[0]);
    } else {
      message.error('添加IP地址失败，请稍后重试');
    }
  } finally {
    submitting.value = false;
  }
};

// 页面初始化
onMounted(() => {
  // 设置页面标题
  document.title = '新增IP地址 - 运维监控系统';
});
</script>

<style scoped>
.ip-add-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.page-header {
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  padding: 16px 24px;
  margin-bottom: 24px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #f0f0f0;
  color: #1890ff;
}

.page-title h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: #1890ff;
}

.page-description {
  margin: 4px 0 0 0;
  color: #8c8c8c;
  font-size: 14px;
}

.form-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.form-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.section-icon {
  color: #1890ff;
}

.form-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 12px 16px;
  }
  
  .form-container {
    padding: 0 16px;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .page-title h2 {
    font-size: 20px;
  }
}

/* 表单样式优化 */
:deep(.ant-form-item-label > label) {
  font-weight: 500;
  color: #262626;
}

:deep(.ant-input-affix-wrapper) {
  border-radius: 6px;
}

:deep(.ant-select-selector) {
  border-radius: 6px;
}

:deep(.ant-input) {
  border-radius: 6px;
}

:deep(.ant-btn) {
  border-radius: 6px;
}
</style>