<template>
  <a-drawer
    v-model:open="dialogVisible"
    :title="formTitle"
    width="800px"
    placement="right"
    :closable="true"
    :mask-closable="false"
    @close="handleClose"
  >
    
    <a-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 18 }"
      @finish="handleSubmit"
      @finishFailed="handleSubmitFailed"
    >
      <!-- 基本信息 -->
      <div class="form-section basic-info">
        <h4 class="section-title">基本信息</h4>
          
          <a-row :gutter="24">
            <a-col :span="12">
              <a-form-item label="软件名称" name="name" class="form-item" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
                <a-input
                  v-model:value="formData.name"
                  placeholder="请输入软件名称"
                  :maxlength="50"
                  show-count
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="资产标签" name="asset_tag" class="form-item" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
                <a-input
                  v-model:value="formData.asset_tag"
                  placeholder="请输入资产标签"
                  :maxlength="50"
                  show-count
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="型号" name="software_type" class="form-item">
                <a-input 
                  v-model:value="formData.software_type" 
                  placeholder="请输入设施型号"
                  :maxlength="100"
                  show-count
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="资产责任人" name="asset_owner" class="form-item">
                <a-select
                  v-model:value="formData.asset_owner"
                  placeholder="请选择资产责任人"
                  show-search
                  :filter-option="false"
                  :loading="userLoading"
                  @search="searchUsers"
                  @focus="loadUsers"
                >
                  <a-select-option
                    v-for="user in userOptions"
                    :key="user.id"
                    :value="user.value"
                    :label="user.label"
                  >
                    {{ user.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="项目来源" name="project_source" class="form-item">
                <a-select
                  v-model:value="formData.project_source"
                  placeholder="请选择项目来源"
                  show-search
                  :filter-option="false"
                  :loading="userLoading"
                  @search="searchUsers"
                  @focus="loadUsers"
                >
                  <a-select-option
                    v-for="user in projectSource"
                    :key="user.id"
                    :value="user.value"
                    :label="user.label"
                  >
                    {{ user.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="采购日期" name="purchase_date" class="form-item">
                <a-date-picker
                  v-model:value="formData.purchase_date"
                  placeholder="请选择采购日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  :disabled-date="disabledDate"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
          </a-row>
          
          <a-row :gutter="16">


          </a-row>
        
        </div>
        
      <!-- 产品信息 -->
      <div class="form-section product-info">
        <h4 class="section-title">产品信息</h4>
          
          <a-row :gutter="24">            
            <a-col :span="12">
                <a-form-item label="制造商" name="vendor" class="form-item">
                <a-select
                  v-model:value="formData.vendor"
                  placeholder="请选择制造商"
                  show-search
                  :filter-option="false"
                  :loading="userLoading"
                  @search="searchUsers"
                  @focus="loadUsers"
                >
                  <a-select-option
                    v-for="user in manufacturers"
                    :key="user.id"
                    :value="user.value"
                    :label="user.label"
                  >
                    {{ user.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="序列号" name="license_key" class="form-item">
                <a-input 
                  v-model:value="formData.license_key" 
                  placeholder="请输入序列号"
                  :maxlength="100"
                  show-count
                />
              </a-form-item>
            </a-col>

            <a-col :span="12">
               <a-form-item label="保修类型" name="warranty_type" class="form-item">
                <a-select
                  v-model:value="formData.warranty_type"
                  placeholder="请选择保修类型"
                  show-search
                  :filter-option="false"
                  :loading="userLoading"
                  @search="searchUsers"
                  @focus="loadUsers"
                >
                  <a-select-option
                    v-for="user in warrantyTypes"
                    :key="user.id"
                    :value="user.value"
                    :label="user.label"
                  >
                    {{ user.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item label="规格参数" name="specification_parameter" class="form-item">
                <a-input 
                  v-model:value="formData.specification_parameter" 
                  placeholder="请输入规格参数"
                />
              </a-form-item>
            </a-col>

            <a-col :span="24">
              <a-form-item label="保修日期" name="warranty_date_range" class="form-item" :label-col="{ span: 3 }" :wrapper-col="{ span: 21 }">
                <a-range-picker
                  v-model:value="formData.warranty_date_range"
                  :placeholder="['开始日期', '结束日期']"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </div>
        <!-- 状态信息 -->
        <div class="form-section product-info"  v-if="isEdit">
        <h4 class="section-title">状态信息</h4>
          <a-row :gutter="24">            
            <a-col :span="12">
               <a-form-item label="软件状态" name="warranty_type" class="form-item">
                <a-select
                  v-model:value="formData.asset_status"
                  placeholder="请选择保修类型"
                  show-search
                  :filter-option="false"
                  :loading="userLoading"
                  @search="searchUsers"
                  @focus="loadUsers"
                >
                  <a-select-option
                    v-for="user in assetStatus"
                    :key="user.id"
                    :value="user.value"
                    :label="user.label"
                  >
                    {{ user.label }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
        </div>

    </a-form>
    
    <!-- 底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <a-button @click="handleClose" :disabled="submitLoading">取消</a-button>
        <a-button 
          type="primary" 
          @click="handleSubmit" 
          :loading="submitLoading"
          :disabled="!isFormValid"
        >
          {{ isEdit ? '更新设施' : '新增设施' }}
        </a-button>
      </div>
    </template>
  </a-drawer>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted  ,onBeforeUnmount, onBeforeMount } from 'vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'
import { hardwareAssetApi } from '@/api/hardwareAsset'
import { supplierApi } from '@/api/supplier'
import { userApi } from '@/api/user'
import softwareAssetApi from '@/api/softwareAsset'

// 移除了大量不必要的图标导入

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  assetData: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  currentItem : {
    type : Object ,
    default: null 
  }
})

// Emits
const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const formRef = ref()
const submitLoading = ref(false)
const userLoading = ref(false)
const supplierLoading = ref(false)
const supplierOptions = ref([])
const specifications = ref([{ key: '', value: '' }])

// 表单数据
const formData = reactive({
  name : '',
  asset_tag: '',
  software_type: '',
  asset_owner: '',
  project_source: '',
  purchase_date: '',
  manufacturer: '',
  specification_parameter: '',
  serial_number: '',
  warranty_type: '',
  warranty_date_range: null ,
  vendor : '' ,
  license_type : '' ,
  license_key : '' ,
  asset_status : ''
})


// 选项数据
const projectSource = ref([
  { label: '内部项目', value: 'internal' },
  { label: '外部项目', value: 'external' },
  { label: '研发项目', value: 'research' },
  { label: '其他', value: 'other' }
])

// 状态数据
const assetStatus = ref([
  { label: '在用', value: 'in_use' },
  { label: '停用', value: 'block_up' },
])
 
 // 资产责任人选项
 const userOptions = ref([
   { id:1,label: '张三', value: 'zhangsan' },
   { id:2,label: '李四', value: 'lisi' },
   { id:3,label: '王五', value: 'wangwu' },
   { id:4,label: '赵六', value: 'zhaoliu' }
 ])

const warrantyTypes = ref([
  { label: '原厂保修', value: 'original' },
  { label: '第三方保修', value: 'third_party' },
  { label: '无保修', value: 'none' }
])
 
const manufacturers = ref([
  { label: '戴尔 (Dell)', value: 'dell' },
  { label: '惠普 (HP)', value: 'hp' },
  { label: '联想 (Lenovo)', value: 'lenovo' },
  { label: '华为 (Huawei)', value: 'huawei' },
  { label: '思科 (Cisco)', value: 'cisco' },
  { label: '苹果 (Apple)', value: 'apple' },
  { label: '其他', value: 'other' }
])

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const formTitle = computed(() => {
  return props.isEdit ? '编辑硬件设施' : '新增硬件设施'
})


// 表单验证状态
const isFormValid = computed(() => {
  return formData.asset_tag && 
         formData.model && 
         formData.manufacturer && 
         formData.serial_number &&
         formData.asset_owner &&
         formData.purchase_date
})

// 表单验证规则
const formRules = {
  asset_tag: [
    { required: true, message: '请输入资产编号', trigger: 'blur' },
    { min: 2, max: 50, message: '资产编号长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  model: [
    { required: true, message: '请输入设备型号', trigger: 'blur' },
    { min: 2, max: 100, message: '设备型号长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  asset_owner: [
    { required: true, message: '请选择资产责任人', trigger: 'change' }
  ],
  project_source: [
    { required: true, message: '请选择项目来源', trigger: 'change' }
  ],
  purchase_date: [
    { required: true, message: '请选择采购日期', trigger: 'change' }
  ],
  manufacturer: [
    { required: true, message: '请选择制造商', trigger: 'change' }
  ],
  serial_number: [
    { required: true, message: '请输入序列号', trigger: 'blur' },
    { min: 2, max: 100, message: '序列号长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  warranty_type: [
    { required: true, message: '请选择保修类型', trigger: 'change' }
  ],
  warranty_date_range: [
    { required: true, message: '请选择保修日期', trigger: 'change' }
  ]
}

// 方法
const resetForm = () => {
  Object.keys(formData).forEach(key => {
    if (key === 'monitoring_status') {
      formData[key] = false
    } else if (key === 'warranty_type') {
      formData[key] = 'original'
    } else if (key === 'asset_status') {
      formData[key] = 'in_use'
    } else if (key === 'warranty_date_range') {
      formData[key] = []
    } else {
      formData[key] = ''
    }
  })
  specifications.value = [{ key: '', value: '' }]
  formRef.value?.resetFields()
}

// 编辑资产处理
const handleEdit = () => {
  Object.assign(formData, props.currentItem)
}

const loadFormData = () => {
  if (props.assetData && props.isEdit) {
    Object.keys(formData).forEach(key => {
      if (props.assetData[key] !== undefined) {
        formData[key] = props.assetData[key]
      }
    })
    
    // 处理规格参数
    if (props.assetData.specifications && typeof props.assetData.specifications === 'object') {
      const specs = Object.entries(props.assetData.specifications).map(([key, value]) => ({ key, value }))
      specifications.value = specs.length > 0 ? specs : [{ key: '', value: '' }]
    }
  }
}

const loadUsers = async () => {
  if (userOptions.value.length > 0) return
  
  userLoading.value = true
  try {
    const response = await userApi.search({ page_size: 100 })
    userOptions.value = response.data.results || []
  } catch (error) {
    console.error('Load users error:', error)
    message.error('加载用户列表失败')
  } finally {
    userLoading.value = false
  }
}

const searchUsers = async (query) => {
  if (!query) return
  
  userLoading.value = true
  try {
    const response = await userApi.search({ search: query, page_size: 50 })
    userOptions.value = response.data.results || []
  } catch (error) {
    console.error('Search users error:', error)
    message.error('搜索用户失败')
  } finally {
    userLoading.value = false
  }
}

const loadSuppliers = async () => {
  if (supplierOptions.value.length > 0) return
  
  supplierLoading.value = true
  try {
    const response = await supplierApi.getSimpleList({ page_size: 100 })
    supplierOptions.value = response.data || []
  } catch (error) {
    console.error('Load suppliers error:', error)
    message.error('加载供应商列表失败')
  } finally {
    supplierLoading.value = false
  }
}

const disabledDate = (current) => {
  // 禁用未来日期
  return current && current > dayjs().endOf('day')
}

const validateSpecifications = () => {
  // 新增模式下不需要验证规格参数
  if (!props.isEdit) {
    return true
  }
  
  const validSpecs = specifications.value.filter(spec => spec.key && spec.value)
  if (validSpecs.length === 0) {
    message.warning('请至少添加一个有效的规格参数')
    return false
  }
  return true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    if (!validateSpecifications()) {
      return
    }
    
    submitLoading.value = true
    
    // 显示加载提示
    const loadingMessage = message.loading(
      props.isEdit ? '正在更新设施信息...' : '正在创建设施...', 
      0
    )
    
    // 处理规格参数（仅在编辑模式下）
    const submitData = { ...formData }
    
    if (props.isEdit) {
      const specs = {}
      specifications.value.forEach(spec => {
        if (spec.key && spec.value) {
          specs[spec.key] = spec.value
        }
      })
      submitData.specifications = specs
    }
    
    if (props.isEdit && props.assetData?.id) {
      await softwareAssetApi.update(props.assetData.id, submitData)
      loadingMessage()
      message.success('资产信息更新成功！')
    } else {
      await softwareAssetApi.create(submitData)
      loadingMessage()
      message.success('资产创建成功！')
    }
    
    emit('success')
    handleClose()
  } catch (error) {
    console.error('Submit error:', error)
    
    // 详细的错误处理
    let errorMessage = '操作失败，请重试'
    if (error.response) {
      const { status, data } = error.response
      if (status === 400) {
        if (data && typeof data === 'object') {
          const errorMessages = []
          Object.entries(data).forEach(([field, messages]) => {
            if (Array.isArray(messages)) {
              errorMessages.push(...messages)
            } else {
              errorMessages.push(messages)
            }
          })
          errorMessage = errorMessages.join(', ') || '请检查输入的数据格式'
        } else {
          errorMessage = data?.message || '请检查输入的数据格式'
        }
      } else if (status === 409) {
        errorMessage = '资产编号或序列号已存在，请使用其他值'
      } else if (status === 500) {
        errorMessage = '服务器内部错误，请稍后重试'
      }
    } else if (error.message) {
      errorMessage = error.message
    }
    
    message.error(errorMessage)
  } finally {
    submitLoading.value = false
  }
}

const handleSubmitFailed = (errorInfo) => {
  console.log('Form validation failed:', errorInfo)
  message.error('请检查表单填写是否正确')
}

const handleClose = () => {
  dialogVisible.value = false
  formData.forEach(key => {
    formData[key] = ''
  })
  nextTick(() => {
    resetForm()
  })

}

const clearForm = () =>  {
  Object.keys(formData).forEach(key => {
    formData[key] = ''  // 或 null，根据需要
  })
}

// 监听器
watch(
  () => props.visible,
  (newVal) => {
    if (newVal) {
      nextTick(() => {
        if (props.isEdit) {
          loadFormData()
        } else {
          resetForm()
        }
      })
    } 
  },
)


// 生命周期
onMounted(() => {
  loadUsers()
  loadSuppliers()

})

</script>

<style scoped>
/* 表单容器 - 蓝白主题 */
.form-section {
  margin-bottom: 24px;
  padding: 24px;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e8f4fd;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.06);
  transition: all 0.3s ease;
}

.form-section:hover {
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.1);
}

/* 标题样式 - 蓝白主题 */
.section-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1890ff;
  position: relative;
  padding-left: 12px;
}

/* 规格参数样式 */
.spec-item {
  margin-bottom: 8px;
  padding: 8px;
  background: #fafafa;
  border-radius: 4px;
  border: 1px solid #f0f0f0;
}

.spec-item:hover {
  border-color: #d9d9d9;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 16px;
  background: #1890ff;
  border-radius: 2px;
}

/* 表单项美化 */
.form-item {
  margin-bottom: 20px;
}

.form-item .ant-form-item-label {
  text-align: left !important;
  font-weight: 600;
  color: #262626;
}

.form-item .ant-form-item-label > label {
  color: #262626;
  font-weight: 600;
}

/* 输入框样式 - 蓝白主题 */
.form-item .ant-input,
.form-item .ant-select-selector,
.form-item .ant-picker,
.form-item .ant-input-number {
  border-radius: 6px;
  border: 1px solid #d9d9d9;
  background: #ffffff;
}

.form-item .ant-input:hover,
.form-item .ant-select-selector:hover,
.form-item .ant-picker:hover,
.form-item .ant-input-number:hover {
  border-color: #40a9ff;
}

.form-item .ant-input:focus,
.form-item .ant-select-focused .ant-select-selector,
.form-item .ant-picker-focused,
.form-item .ant-input-number-focused {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

/* 底部按钮样式 - 蓝白主题 */
.dialog-footer {
  text-align: right;
  padding: 24px 0;
  background: #ffffff;
}

.dialog-footer .ant-btn {
  margin-left: 12px;
  border-radius: 6px;
}

.dialog-footer .ant-btn:first-child {
  border-color: #d9d9d9;
  color: #666;
}

.dialog-footer .ant-btn:first-child:hover {
  border-color: #40a9ff;
  color: #40a9ff;
}

.dialog-footer .ant-btn[type="primary"] {
  background: #1890ff;
  border-color: #1890ff;
}

.dialog-footer .ant-btn[type="primary"]:hover {
  background: #40a9ff;
  border-color: #40a9ff;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .form-section {
    padding: 20px;
    margin-bottom: 24px;
  }
  
  .section-title {
    font-size: 16px;
    margin-bottom: 20px;
  }
  
  .dialog-footer {
    padding: 20px 0;
  }
}
</style>