<template>
  <a-collapse-transition>
    <div class="template-container">
      <a-card 
        v-for="(template, index) in templates" 
        :key="getTemplateKey(template)"
        class="template-card"
        hoverable
      >
        <div class="card-header">
          <component :is="getIcon(template.icon)" class="card-icon" />
          <h4 class="card-title">{{ template.name }}</h4>
        </div>
        <div class="card-content">
          <p class="card-description">{{ truncateDescription(template.description) }}</p>
        </div>
      </a-card>
    </div>
  </a-collapse-transition>
</template>

<script>
export default {
  props: {
    templates: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getTemplateKey(template) {
      return template.templateid || template.id || Math.random().toString();
    },
    getIcon(iconName) {
      // 根据实际项目中的图标组件调整
      return iconName === 'router' ? 'RouterOutlined' : 'AppstoreOutlined';
    },
    truncateDescription(desc) {
      return desc.length > 100 ? desc.substring(0, 100) + '...' : desc;
    }
  }
}
</script>

<style scoped>
.template-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding: 8px;
}

.template-card {
  transition: all 0.3s ease;
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.card-icon {
  font-size: 20px;
  margin-right: 8px;
  color: #1890ff;
}

.card-title {
  margin: 0;
  font-size: 16px;
}

.card-description {
  color: #666;
  margin-bottom: 12px;
}
</style>