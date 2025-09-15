<template>
  <div class="font-demo-container">
    <a-card title="字体系统设计演示" class="demo-card">
      <!-- 标题层级演示 -->
      <div class="demo-section">
        <h3 class="section-title">标题层级</h3>
        <div class="demo-content">
          <h1>H1 主标题 - 20px Bold</h1>
          <h2>H2 大标题 - 18px Semibold</h2>
          <h3>H3 中标题 - 16px Semibold</h3>
          <h4>H4 小标题 - 14px Medium</h4>
        </div>
      </div>

      <!-- 文本大小演示 -->
      <div class="demo-section">
        <h3 class="section-title">文本大小</h3>
        <div class="demo-content">
          <p class="text-large">大文本 - 16px Normal (重要内容)</p>
          <p class="text-base">基础文本 - 14px Normal (正文内容)</p>
          <p class="text-small">小文本 - 13px Normal (表格内容)</p>
          <p class="text-xs">超小文本 - 12px Normal (辅助信息)</p>
        </div>
      </div>

      <!-- 字体重量演示 -->
      <div class="demo-section">
        <h3 class="section-title">字体重量</h3>
        <div class="demo-content">
          <p class="font-light">Light 300 - 轻量文字</p>
          <p class="font-normal">Normal 400 - 正常文字</p>
          <p class="font-medium">Medium 500 - 中等文字 (表单标签、按钮)</p>
          <p class="font-semibold">Semibold 600 - 半粗体 (表格表头、小标题)</p>
          <p class="font-bold">Bold 700 - 粗体 (重要标题)</p>
        </div>
      </div>

      <!-- 组件字体演示 -->
      <div class="demo-section">
        <h3 class="section-title">组件字体应用</h3>
        <div class="demo-content">
          <!-- 按钮 -->
          <div class="component-demo">
            <h4>按钮 (14px Medium)</h4>
            <a-space>
              <a-button type="primary">主要按钮</a-button>
              <a-button>默认按钮</a-button>
              <a-button type="dashed">虚线按钮</a-button>
            </a-space>
          </div>

          <!-- 表单 -->
          <div class="component-demo">
            <h4>表单 (标签14px Medium, 输入框14px Normal)</h4>
            <a-form layout="vertical">
              <a-row :gutter="16">
                <a-col :span="12">
                  <a-form-item label="用户名">
                    <a-input placeholder="请输入用户名" />
                  </a-form-item>
                </a-col>
                <a-col :span="12">
                  <a-form-item label="邮箱地址">
                    <a-input placeholder="请输入邮箱" />
                  </a-form-item>
                </a-col>
              </a-row>
            </a-form>
          </div>

          <!-- 表格 -->
          <div class="component-demo">
            <h4>表格 (表头14px Semibold, 内容13px Normal)</h4>
            <a-table 
              :columns="tableColumns" 
              :data-source="tableData" 
              :pagination="false"
              size="small"
            />
          </div>

          <!-- 标签 -->
          <div class="component-demo">
            <h4>标签 (12px Medium)</h4>
            <a-space>
              <a-tag color="blue">蓝色标签</a-tag>
              <a-tag color="green">绿色标签</a-tag>
              <a-tag color="orange">橙色标签</a-tag>
              <a-tag color="red">红色标签</a-tag>
            </a-space>
          </div>

          <!-- 卡片 -->
          <div class="component-demo">
            <h4>卡片 (标题16px Semibold, 内容14px Normal)</h4>
            <a-card title="卡片标题" style="width: 300px">
              <p>这是卡片的内容区域，展示了统一的字体设计。文字清晰易读，层次分明。</p>
            </a-card>
          </div>
        </div>
      </div>

      <!-- 字体变量参考 -->
      <div class="demo-section">
        <h3 class="section-title">CSS变量参考</h3>
        <div class="demo-content">
          <a-descriptions bordered size="small">
            <a-descriptions-item label="字体族">--font-family</a-descriptions-item>
            <a-descriptions-item label="超小字体">--font-size-xs (12px)</a-descriptions-item>
            <a-descriptions-item label="小字体">--font-size-sm (13px)</a-descriptions-item>
            <a-descriptions-item label="基础字体">--font-size-base (14px)</a-descriptions-item>
            <a-descriptions-item label="中等字体">--font-size-md (16px)</a-descriptions-item>
            <a-descriptions-item label="大字体">--font-size-lg (18px)</a-descriptions-item>
            <a-descriptions-item label="超大字体">--font-size-xl (20px)</a-descriptions-item>
            <a-descriptions-item label="轻量字重">--font-weight-light (300)</a-descriptions-item>
            <a-descriptions-item label="正常字重">--font-weight-normal (400)</a-descriptions-item>
            <a-descriptions-item label="中等字重">--font-weight-medium (500)</a-descriptions-item>
            <a-descriptions-item label="半粗字重">--font-weight-semibold (600)</a-descriptions-item>
            <a-descriptions-item label="粗体字重">--font-weight-bold (700)</a-descriptions-item>
          </a-descriptions>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 表格数据
const tableColumns = [
  {
    title: '姓名',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: '年龄',
    dataIndex: 'age',
    key: 'age',
  },
  {
    title: '职位',
    dataIndex: 'position',
    key: 'position',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
  },
];

const tableData = [
  {
    key: '1',
    name: '张三',
    age: 28,
    position: '前端工程师',
    status: '在职',
  },
  {
    key: '2',
    name: '李四',
    age: 32,
    position: '后端工程师',
    status: '在职',
  },
  {
    key: '3',
    name: '王五',
    age: 25,
    position: 'UI设计师',
    status: '试用期',
  },
];
</script>

<style scoped>
.font-demo-container {
  padding: 24px;
  background: #f5f5f5;
  min-height: 100vh;
}

.demo-card {
  max-width: 1200px;
  margin: 0 auto;
}

.demo-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.demo-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  color: var(--primary-color);
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid var(--primary-color);
}

.demo-content {
  padding-left: 16px;
}

.component-demo {
  margin-bottom: 24px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.component-demo h4 {
  margin-bottom: 12px;
  color: var(--gray-600);
}

/* 演示文本样式 */
.demo-content p {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #f0f0f0;
}

.demo-content h1,
.demo-content h2,
.demo-content h3,
.demo-content h4 {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #f0f0f0;
}
</style>