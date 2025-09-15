<template>
  <!-- 登录页面独立布局 -->
  <router-view v-if="$route.meta.hideLayout" />
  
  <!-- 管理员后台布局 -->
  <AdminLayout v-else-if="isAdminRoute" />
  
  <!-- 主应用布局 -->
  <div v-else class="monitor-layout">
    <!-- 顶部导航 -->
    <header class="monitor-header">
      <div class="header-container">
        <div class="brand">
          <div class="brand-icon">
            <svg t="1757646777321" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="8545">
              <path d="M453.6 679.904h100.8v113.408H453.6z" fill="#7FF298" p-id="8546"></path>
              <path d="M365.408 843.712V768.096h277.216v75.616z" fill="#226CFF" p-id="8547"></path>
              <path d="M151.2 176.416m192 0l321.6 0q192 0 192 192l0 141.088q0 192-192 192l-321.6 0q-192 0-192-192l0-141.088q0-192 192-192Z" fill="#226CFF" p-id="8548"></path>
              <path d="M576 378.272h50.4v214.208H576z" fill="#FFFFFF" p-id="8549"></path>
              <path d="M676.8 315.264h50.4v277.216H676.8z" fill="#FFFFFF" p-id="8550"></path>
              <path d="M462.592 340.48h50.4v252h-50.4z" fill="#FFFFFF" p-id="8551"></path>
              <path d="M361.792 466.464h50.4v126.016h-50.4z" fill="#FFFFFF" p-id="8552"></path>
            </svg>
          </div>
          <h1 class="brand-title">运维监控系统</h1>
        </div>
        
        <nav class="main-nav">
          <div class="custom-menu" v-if="!loading">
            <template v-for="item in menuItems" :key="item.key">
              <!-- 一级菜单项 -->
              <div 
                v-if="!item.children || item.children.length === 0" 
                class="menu-item"
                :class="{ 'menu-item-selected': selectedKeys.includes(item.key) }"
                @click="handleMenuSelect({ key: item.key })"
              >
                <component :is="getIconComponent(item.icon)" class="menu-icon" />
                <span class="menu-text">{{ item.title }}</span>
              </div>
              
              <!-- 带子菜单的菜单项 -->
              <div v-else class="menu-submenu" @mouseenter="showSubmenu(item.key)" @mouseleave="hideSubmenu(item.key)">
                <div 
                  class="menu-item submenu-title"
                  :class="{ 'menu-item-selected': isSubmenuSelected(item) }"
                >
                  <component :is="getIconComponent(item.icon)" class="menu-icon" />
                  <span class="menu-text">{{ item.title }}</span>
                  <DownOutlined class="submenu-arrow" />
                </div>
                <div 
                  class="submenu-popup"
                  :class="{ 'submenu-visible': visibleSubmenus[item.key] }"
                >
                  <div 
                    v-for="child in item.children" 
                    :key="child.key"
                    class="submenu-item"
                    :class="{ 'submenu-item-selected': selectedKeys.includes(child.key) }"
                    @click="handleMenuSelect({ key: child.key })"
                  >
                    <component :is="getIconComponent(child.icon)" class="menu-icon" />
                    <span class="menu-text">{{ child.title }}</span>
                  </div>
                </div>
              </div>
            </template>
          </div>
          <div v-else class="menu-loading">
            加载中...
          </div>
        </nav>
        
        <div class="header-actions">
          <a-badge :count="3" class="notification-badge">
            <a-button type="text" class="action-btn">
              <BellOutlined />
            </a-button>
          </a-badge>
          <a-dropdown>
            <a-button type="text" class="user-btn">
              <a-avatar size="small" class="user-avatar" :style="{ background: isAdmin ? '#faad14' : '#1890ff' }">
                {{ currentUserName.charAt(0).toUpperCase() }}
              </a-avatar>
              <span class="user-name">{{ currentUserName }} {{ isAdmin ? '(管理员)' : '(用户)' }}</span>
              <DownOutlined />
            </a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item key="1"><UserOutlined /> 个人中心</a-menu-item>
                <a-menu-item key="2"><SettingOutlined /> 系统设置</a-menu-item>
                <a-menu-divider />
                <a-menu-item key="3" @click="handleLogout">
                  <LogoutOutlined /> 退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="monitor-content">
      <div class="content-container">
        <div class="content-panel">
          <router-view />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { userAPI } from '@/api/users';
import { menuApi } from '@/api/menu';
import AdminLayout from '@/layouts/AdminLayout.vue';
import { 
  DatabaseOutlined, 
  UserOutlined,
  BellOutlined,
  DownOutlined,
  SettingOutlined,
  LogoutOutlined,
  HomeOutlined,
  CloudServerOutlined,
  BarChartOutlined,
  GlobalOutlined,
  AppstoreOutlined
} from '@ant-design/icons-vue';

const collapsed = ref(false);
const route = useRoute();
const router = useRouter();



const selectedKeys = ref([route.path || '/']);
const menuItems = ref([]);
const loading = ref(false);
const visibleSubmenus = ref({});

// 用户类型和信息
const userType = ref(localStorage.getItem('userType') || 'user');
const currentUserName = ref(localStorage.getItem('username') || '用户');
const isAdmin = computed(() => userType.value === 'admin');

// 判断是否为管理员路由
const isAdminRoute = computed(() => {
  return route.path.startsWith('/admin/');
});

// 图标组件映射
const iconComponents = {
  'HomeOutlined': HomeOutlined,
  'DatabaseOutlined': DatabaseOutlined,
  'CloudServerOutlined': CloudServerOutlined,
  'BellOutlined': BellOutlined,
  'BarChartOutlined': BarChartOutlined,
  'GlobalOutlined': GlobalOutlined,
  'AppstoreOutlined': AppstoreOutlined,
  'UserOutlined': UserOutlined,
  'SettingOutlined': SettingOutlined
};

// 获取图标组件
const getIconComponent = (iconName) => {
  return iconComponents[iconName] || HomeOutlined;
};

// 获取用户菜单
const fetchUserMenus = async () => {
  // 只在主应用布局时获取菜单，避免在登录页面或管理员页面调用
  if (route.meta.hideLayout || isAdminRoute.value) {
    return;
  }
  
  try {
    loading.value = true;
    const response = await menuApi.getUserMenus();
    if (response.data && response.data.data && response.data.data.results) {
      menuItems.value = response.data.data.results;
    } else {
      // 如果API返回失败，使用默认菜单
      menuItems.value = getDefaultMenus();
    }
  } catch (error) {
    console.error('获取菜单失败:', error);
    message.warning('获取菜单失败，使用默认菜单');
    // 使用默认菜单作为后备
    menuItems.value = getDefaultMenus();
  } finally {
    loading.value = false;
  }
};

// 默认菜单配置（空数组，菜单完全由后端提供）
const getDefaultMenus = () => {
  return [];
};

watch(() => route.path, (newPath) => {
  selectedKeys.value = [newPath];
});

const toggleCollapsed = () => {
  collapsed.value = !collapsed.value;
};

const handleMenuSelect = ({ key }) => {
  router.push(key);
};

// 显示子菜单
const showSubmenu = (key) => {
  visibleSubmenus.value[key] = true;
};

// 隐藏子菜单
const hideSubmenu = (key) => {
  visibleSubmenus.value[key] = false;
};

// 判断子菜单是否选中
const isSubmenuSelected = (item) => {
  if (!item.children) return false;
  return item.children.some(child => selectedKeys.value.includes(child.key));
};

// 处理用户登录事件
const handleUserLoggedIn = () => {
  // 延迟获取菜单，等待路由跳转完成
  setTimeout(() => {
    fetchUserMenus();
  }, 600); // 稍微延迟一点，确保路由跳转完成
};

// 组件挂载时检查登录状态后获取菜单
onMounted(() => {
  // 只在主应用布局时获取菜单，避免在登录页面调用
  if (!route.meta.hideLayout && !isAdminRoute.value) {
    // 检查用户登录状态
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    const token = localStorage.getItem('token');
    
    if (isLoggedIn === 'true' && token) {
      // 用户已登录，获取菜单
      fetchUserMenus();
    }
    // 移除未登录时也调用fetchUserMenus的逻辑
  }
  
  // 监听登录事件
  window.addEventListener('userLoggedIn', handleUserLoggedIn);
});

// 组件卸载时移除事件监听
onBeforeUnmount(() => {
  window.removeEventListener('userLoggedIn', handleUserLoggedIn);
});

const handleLogout = async () => {
  try {
    // 调用后端登出 API
    await userAPI.logout();
    
    // 清除本地存储的登录状态
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userType');
    localStorage.removeItem('username');
    localStorage.removeItem('isAdmin');
    localStorage.removeItem('userRole');
    localStorage.removeItem('remember_user');
    localStorage.removeItem('remember_mode');
    
    // 显示成功提示
    message.success({
      content: '已退出登录',
      duration: 1.5
    });
    
    // 延迟跳转，使用 window.location.href 强制刷新
    setTimeout(() => {
      window.location.href = '/#/login';
    }, 500);
    
  } catch (error) {
    console.error('登出错误:', error);
    
    // 即使登出 API 失败，也要清除本地状态
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userType');
    localStorage.removeItem('username');
    localStorage.removeItem('isAdmin');
    localStorage.removeItem('userRole');
    localStorage.removeItem('remember_user');
    localStorage.removeItem('remember_mode');
    
    // 显示警告提示
    message.warning({
      content: '登出请求失败，但已清除本地登录状态',
      duration: 1.5
    });
    
    // 强制跳转到登录页面
    setTimeout(() => {
      window.location.href = '/#/login';
    }, 500);
  }
};

</script>

<style scoped>
* {
  box-sizing: border-box;
}

.monitor-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f0f5ff;
}

/* 顶部导航 */
.monitor-header {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  border-bottom: 1px solid #e6f7ff;
  box-shadow: 0 2px 16px rgba(24, 144, 255, 0.08);
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(10px);
}

.header-container {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 64px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 255, 0.8) 100%);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 20px rgba(24, 144, 255, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.brand::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(24, 144, 255, 0.1), transparent);
  transition: left 0.6s ease;
}

.brand:hover::before {
  left: 100%;
}

.brand:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(24, 144, 255, 0.15);
  border-color: rgba(24, 144, 255, 0.2);
}

.brand-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 1;
}

.brand-icon svg {
  width: 100%;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.brand:hover .brand-icon {
  transform: scale(1.1) rotate(5deg);
  filter: drop-shadow(0 4px 8px rgba(24, 144, 255, 0.4));
}

.brand-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
  background: linear-gradient(135deg, #1a1a1a 0%, #2d3748 50%, #4a5568 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 0.8px;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.brand:hover .brand-title {
  transform: translateX(2px);
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.main-nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.custom-menu {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 20px;
  height: 87px;
}

.menu-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 64px;
  color: #64748b;
  font-size: 14px;
}

.menu-item {
  margin: 0 4px;
  padding: 0 16px;
  border-radius: 8px;
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  height: 40px;
  line-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid transparent;
  cursor: pointer;
  user-select: none;
}

.menu-item:hover {
  color: #3b82f6;
  transform: translateY(-1px);
  background-color: rgba(59, 130, 246, 0.05);
  border-color: transparent;
}

/* .menu-item:hover:not(.menu-item-selected) .menu-text {
  color: #3b82f6 !important;
}

.menu-item:hover:not(.menu-item-selected) .menu-icon {
  color: #3b82f6 !important;
} */



.menu-item-selected {
  color: #ffffff !important;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
  font-weight: 600;
  border-color: transparent;
  transform: translateY(-1px);
}

.menu-item-selected .menu-text {
  color: #ffffff !important;
}

.menu-item-selected .menu-icon {
  color: #ffffff !important;
}

.menu-item-selected:hover {
  color: #ffffff !important;
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%) !important;
}

.menu-item-selected:hover .menu-text {
  color: #ffffff !important;
}

.menu-item-selected:hover .menu-icon {
  color: #ffffff !important;
}

/* 子菜单样式 */
.menu-submenu {
  margin: 0 4px;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.submenu-title {
  position: relative;
}

.submenu-arrow {
  margin-left: 4px;
  font-size: 12px;
  transition: transform 0.3s ease;
}

.menu-submenu:hover .submenu-arrow {
  transform: rotate(180deg);
}

.submenu-popup {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 160px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(0, 0, 0, 0.06);
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  padding: 8px 0;
}

.submenu-visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.submenu-item {
  padding: 8px 16px;
  color: #64748b;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
}

.submenu-item:hover {
  color: #3b82f6;
  background-color: rgba(59, 130, 246, 0.05);
}

.submenu-item-selected {
  color: #3b82f6 !important;
  background-color: rgba(59, 130, 246, 0.1) !important;
  font-weight: 600;
}

/* 图标样式优化 */
.menu-icon {
  font-size: 16px;
  margin-right: 8px;
  transition: all 0.3s ease;
}

.menu-item:hover .menu-icon {
  transform: scale(1.1);
}

.menu-item-selected .menu-icon {
  color: #ffffff;
  transform: scale(1.05);
}

.menu-text {
  transition: all 0.3s ease;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.notification-badge {
  cursor: pointer;
}

.action-btn {
  color: #595959;
  transition: color 0.3s ease;
}

.action-btn:hover {
  color: #1890ff;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #595959;
  transition: color 0.3s ease;
}

.user-btn:hover {
  color: #1890ff;
}

.user-avatar {
  background: #1890ff;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

/* 主内容区域 */
.monitor-content {
  flex: 1;
  padding: 32px 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #f8faff 50%, #ffffff 100%);
  position: relative;
}

.monitor-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(180deg, rgba(24, 144, 255, 0.02) 0%, transparent 100%);
  pointer-events: none;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #262626;
}

.page-subtitle {
  margin: 0;
  font-size: 14px;
  color: #595959;
}

.content-panel {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(24, 144, 255, 0.08);
  padding: 20px;
  min-height: 600px;
  border: 1px solid rgba(24, 144, 255, 0.08);
  position: relative;
  overflow: hidden;
}

.content-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(24, 144, 255, 0.2), transparent);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-container {
    padding: 0 16px;
    flex-direction: column;
    height: auto;
    gap: 12px;
  }
  
  .main-nav {
    width: 100%;
    margin: 0;
  }
  
  .custom-menu {
    width: 100%;
    justify-content: center;
    height: 48px;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .menu-item {
    height: 36px;
    line-height: 36px;
    padding: 0 12px;
    font-size: 13px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .monitor-content {
    padding: 16px;
  }
  
  .content-panel {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .brand-title {
    font-size: 16px;
  }
  
  .user-name {
    display: none;
  }
}
</style>
