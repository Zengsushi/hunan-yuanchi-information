<template>
  <a-layout class="admin-layout">
    <!-- 顶部导航栏 -->
    <a-layout-header class="admin-header">
      <div class="header-container">
        <!-- 左侧Logo和品牌 -->
        <div class="header-brand">
          <div class="brand-logo">
            <CrownOutlined class="brand-icon" />
            <span class="brand-title">管理后台</span>
          </div>
        </div>
        
        <!-- 中间导航菜单 -->
        <nav class="header-nav">
          <a-menu
            v-model:selectedKeys="selectedKeys"
            mode="horizontal"
            theme="light"
            class="admin-nav-menu"
            @select="handleMenuSelect"
          >
            <a-menu-item key="/admin/dashboard">
              <template #icon><DashboardOutlined /></template>
              <span>控制台</span>
            </a-menu-item>
            
            <a-sub-menu key="users">
              <template #icon><TeamOutlined /></template>
              <template #title>用户管理</template>
              <a-menu-item key="/admin/users">
                <template #icon><UserOutlined /></template>
                <span>用户列表</span>
              </a-menu-item>
              <a-menu-item key="/admin/roles">
                <template #icon><SafetyOutlined /></template>
                <span>角色权限</span>
              </a-menu-item>
            </a-sub-menu>
            
            <a-sub-menu key="organization">
              <template #icon><ApartmentOutlined /></template>
              <template #title>组织架构</template>
              <a-menu-item key="/admin/departments">
                <template #icon><BankOutlined /></template>
                <span>部门管理</span>
              </a-menu-item>
              <a-menu-item key="/admin/positions">
                <template #icon><IdcardOutlined /></template>
                <span>职位管理</span>
              </a-menu-item>
              <a-menu-item key="/admin/employees">
                <template #icon><ContactsOutlined /></template>
                <span>员工管理</span>
              </a-menu-item>
            </a-sub-menu>
            
            <a-sub-menu key="assets">
              <template #icon><LaptopOutlined /></template>
              <template #title>资产管理</template>
              <a-menu-item key="/assets/hardware">
                <template #icon><DesktopOutlined /></template>
                <span>硬件设施</span>
              </a-menu-item>
              <a-menu-item key="/assets/software">
                <template #icon><CodeOutlined /></template>
                <span>软件资产</span>
              </a-menu-item>
            </a-sub-menu>
            
            <a-sub-menu key="system">
              <template #icon><SettingOutlined /></template>
              <template #title>系统管理</template>
              <a-menu-item key="/admin/dictionary">
                <template #icon><BookOutlined /></template>
                <span>字典管理</span>
              </a-menu-item>
              <a-menu-item key="/admin/font-demo">
                <template #icon><FontSizeOutlined /></template>
                <span>字体设计</span>
              </a-menu-item>
              <a-menu-item key="/admin/settings">
                <template #icon><ToolOutlined /></template>
                <span>系统设置</span>
              </a-menu-item>
              <a-menu-item key="/admin/logs">
                <template #icon><FileTextOutlined /></template>
                <span>操作日志</span>
              </a-menu-item>
            </a-sub-menu>
            
            <a-menu-item key="/admin/backup">
              <template #icon><CloudDownloadOutlined /></template>
              <span>数据备份</span>
            </a-menu-item>
          </a-menu>
        </nav>
        
        <!-- 右侧操作区域 -->
        <div class="header-actions">
          <a-space size="large">
            <!-- 切换到用户界面 -->
            
            <!-- 通知铃铛 -->
            <a-badge :count="5" class="notification-badge">
              <a-button type="text" class="header-btn">
                <BellOutlined />
              </a-button>
            </a-badge>
            
            <!-- 全屏切换 -->
            <a-button type="text" class="header-btn" @click="toggleFullscreen">
              <FullscreenOutlined v-if="!isFullscreen" />
              <FullscreenExitOutlined v-else />
            </a-button>
            
            <!-- 用户信息下拉菜单 -->
            <a-dropdown>
              <a-button type="text" class="user-info">
                <a-avatar class="user-avatar" :style="{ background: '#faad14' }">
                  {{ currentUserName.charAt(0).toUpperCase() }}
                </a-avatar>
                <span class="user-name">{{ currentUserName }}</span>
                <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item key="profile">
                    <UserOutlined />
                    <span>个人资料</span>
                  </a-menu-item>
                  <a-menu-item key="security">
                    <LockOutlined />
                    <span>安全设置</span>
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item key="logout" @click="handleLogout">
                    <LogoutOutlined />
                    <span>退出登录</span>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </a-space>
        </div>
      </div>
    </a-layout-header>
    
    <!-- 面包屑导航 -->
    <div class="breadcrumb-container">
      <div class="breadcrumb-wrapper">
        <a-breadcrumb class="breadcrumb">
          <a-breadcrumb-item>管理后台</a-breadcrumb-item>
          <a-breadcrumb-item>{{ currentPageTitle }}</a-breadcrumb-item>
        </a-breadcrumb>
      </div>
    </div>
    
    <!-- 主内容区 -->
    <a-layout-content class="admin-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </a-layout-content>
    
    <!-- 底部信息 -->
    <a-layout-footer class="admin-footer">
      <div class="footer-content">
        <span>© 2024 运维监控系统管理后台</span>
        <span class="version">Version 1.0.0</span>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { userAPI } from '@/api/users';
import {
  CrownOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  TeamOutlined,
  UserOutlined,
  SafetyOutlined,
  ApartmentOutlined,
  BankOutlined,
  IdcardOutlined,
  ContactsOutlined,
  SettingOutlined,
  ToolOutlined,
  FileTextOutlined,
  CloudDownloadOutlined,
  BookOutlined,
  FontSizeOutlined,
  SwapOutlined,
  BellOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
  DownOutlined,
  LockOutlined,
  LogoutOutlined,
  LaptopOutlined,
  DesktopOutlined,
  CodeOutlined
} from '@ant-design/icons-vue';

const route = useRoute();
const router = useRouter();

// 响应式数据
const collapsed = ref(false);
const selectedKeys = ref([route.path]);
const currentUserName = ref(localStorage.getItem('username') || '管理员');
const isFullscreen = ref(false);

// 监听 localStorage 变化，确保登出后能正确更新界面
const updateUserInfo = () => {
  currentUserName.value = localStorage.getItem('username') || '管理员';
};

// 监听存储变化
window.addEventListener('storage', updateUserInfo);

// 计算属性
const currentPageTitle = computed(() => {
  const titles = {
    '/admin': '控制台',
    '/admin/dashboard': '控制台',
    '/admin/users': '用户管理',
    '/admin/roles': '角色权限',
    '/admin/departments': '部门管理',
    '/admin/positions': '职位管理',
    '/admin/employees': '员工管理',
    '/admin/dictionary': '字典管理',
    '/admin/settings': '系统设置',
    '/admin/logs': '操作日志',
    '/admin/backup': '数据备份'
  };
  return titles[route.path] || '管理后台';
});

// 监听路由变化
watch(() => route.path, (newPath) => {
  selectedKeys.value = [newPath];
});

// 方法
const toggleCollapsed = () => {
  collapsed.value = !collapsed.value;
  
  // 在移动端，折叠侧边栏实际上是隐藏它
  const isMobile = window.innerWidth <= 768;
  if (isMobile) {
    const siderElement = document.querySelector('.admin-sider');
    if (siderElement) {
      if (collapsed.value) {
        siderElement.style.transform = 'translateX(-100%)';
      } else {
        siderElement.style.transform = 'translateX(0)';
      }
    }
  }
};

const handleMenuSelect = ({ key }) => {
  if (key !== 'back-to-user') {
    const contentWrapper = document.querySelector('.content-wrapper');
    
    if (contentWrapper) {
      // 第一步：渐出当前内容
      contentWrapper.style.transition = 'all 0.3s ease-out';
      contentWrapper.style.opacity = '0';
      contentWrapper.style.transform = 'translateY(-10px)';
      
      // 第二步：延迟后进行路由跳转
      setTimeout(async () => {
        await router.push(key);
        
        // 第三步：等待路由切换完成后渐入新内容
        await nextTick();
        
        // 使用轮询方式确保找到新的DOM元素
        const waitForElement = (selector, maxAttempts = 10) => {
          return new Promise((resolve) => {
            let attempts = 0;
            const checkElement = () => {
              const element = document.querySelector(selector);
              if (element || attempts >= maxAttempts) {
                resolve(element);
              } else {
                attempts++;
                setTimeout(checkElement, 50);
              }
            };
            checkElement();
          });
        };
        
        const newContentWrapper = await waitForElement('.content-wrapper');
        if (newContentWrapper) {
          // 设置初始渐入状态
          newContentWrapper.style.transition = 'none';
          newContentWrapper.style.opacity = '0';
          newContentWrapper.style.transform = 'translateY(20px)';
          
          // 滚动到顶部
          newContentWrapper.scrollTo({
            top: 0,
            behavior: 'auto'
          });
          
          // 强制重绘后应用渐入效果
          newContentWrapper.offsetHeight; // 触发重绘
          
          newContentWrapper.style.transition = 'all 0.4s ease-out';
          newContentWrapper.style.opacity = '1';
          newContentWrapper.style.transform = 'translateY(0)';
        }
      }, 300); // 等待渐出动画完成
    } else {
      // 如果找不到容器，直接跳转
      router.push(key);
    }
  }
};



const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen();
    isFullscreen.value = true;
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
      isFullscreen.value = false;
    }
  }
};

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

// 监听全屏状态变化
onMounted(() => {
  document.addEventListener('fullscreenchange', () => {
    isFullscreen.value = !!document.fullscreenElement;
  });
  
  // 监听窗口大小变化，处理移动端侧边栏
  const handleResize = () => {
    const isMobile = window.innerWidth <= 768;
    const siderElement = document.querySelector('.admin-sider');
    
    if (isMobile && !collapsed.value) {
      collapsed.value = true;
      if (siderElement) {
        siderElement.style.transform = 'translateX(-100%)';
      }
    } else if (!isMobile) {
      if (siderElement) {
        siderElement.style.transform = '';
      }
    }
  };
  
  window.addEventListener('resize', handleResize);
  handleResize(); // 初始化检查
  
  // 清理事件监听器
  return () => {
    window.removeEventListener('resize', handleResize);
  };
});
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden; /* 防止水平滚动条 */
}

/* 顶部导航栏样式 */
.admin-header {
  background: linear-gradient(135deg, #001529 0%, #002140 100%);
  padding: 0;
  height: 72px;
  box-shadow: 0 4px 16px rgba(0, 21, 41, 0.35);
  z-index: 100;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

/* 左侧品牌区域 */
.header-brand {
  display: flex;
  align-items: center;
  min-width: 200px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  position: relative;
  overflow: hidden;
}

.brand-icon {
  font-size: 28px;
  color: #faad14;
  filter: drop-shadow(0 0 12px rgba(250, 173, 20, 0.6));
  animation: pulse 3s ease-in-out infinite;
}

.brand-title {
  color: #fff;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-tight);
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

/* 中间导航区域 */
.header-nav {
  flex: 1;
  display: flex;
  justify-content: center;
  max-width: 800px;
}

/* 水平导航菜单样式 */
:deep(.admin-nav-menu) {
  background: transparent;
  border-bottom: none;
  line-height: 72px;
  font-weight: 500;
}

:deep(.admin-nav-menu .ant-menu-item) {
  color: rgba(255, 255, 255, 0.85) !important;
  border-radius: 8px;
  margin: 0 4px;
  padding: 0 16px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.admin-nav-menu .ant-menu-item:hover) {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08)) !important;
  color: #fff !important;
  transform: translateY(-1px);
}

:deep(.admin-nav-menu .ant-menu-item:hover span) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-item:hover .anticon) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-item-selected) {
  background: linear-gradient(135deg, #1890ff, #40a9ff) !important;
  color: #fff !important;
  font-weight: 600;
}

:deep(.admin-nav-menu .ant-menu-item-selected span) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-item-selected .anticon) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-item-selected::after) {
  border-bottom: none !important;
  display: none !important;
  content: none !important;
}

/* 子菜单样式 */
:deep(.admin-nav-menu .ant-menu-submenu) {
  color: rgba(255, 255, 255, 0.85) !important;
  margin: 0 4px;
}

:deep(.admin-nav-menu .ant-menu-submenu-title) {
  color: rgba(255, 255, 255, 0.85) !important;
  border-radius: 8px;
  padding: 0 16px;
  height: 48px;
  line-height: 48px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 子菜单标题文字和图标默认颜色 */
:deep(.admin-nav-menu .ant-menu-submenu-title span) {
  color: rgba(255, 255, 255, 0.85) !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-title .anticon) {
  color: rgba(255, 255, 255, 0.85) !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-title .ant-menu-submenu-arrow) {
  color: rgba(255, 255, 255, 0.85) !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-title:hover) {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08)) !important;
  color: #fff !important;
  transform: translateY(-1px);
}

:deep(.admin-nav-menu .ant-menu-submenu-title:hover span) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-title:hover .anticon) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-title:hover .ant-menu-submenu-arrow) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-open > .ant-menu-submenu-title) {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08)) !important;
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-open > .ant-menu-submenu-title span) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-open > .ant-menu-submenu-title .anticon) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-open > .ant-menu-submenu-title .ant-menu-submenu-arrow) {
  color: #fff !important;
}

/* 当子菜单被选中时的样式（当子菜单中有选中项时） */
:deep(.admin-nav-menu .ant-menu-submenu-selected > .ant-menu-submenu-title) {
  background: linear-gradient(135deg, #1890ff, #40a9ff) !important;
  color: #fff !important;
  font-weight: 600;
}

:deep(.admin-nav-menu .ant-menu-submenu-selected > .ant-menu-submenu-title span) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-selected > .ant-menu-submenu-title .anticon) {
  color: #fff !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-selected > .ant-menu-submenu-title .ant-menu-submenu-arrow) {
  color: #fff !important;
}

/* 移除子菜单选中状态的下方线条 */
:deep(.admin-nav-menu .ant-menu-submenu-selected::after) {
  border-bottom: none !important;
  display: none !important;
  content: none !important;
}

:deep(.admin-nav-menu .ant-menu-submenu-selected > .ant-menu-submenu-title::after) {
  border-bottom: none !important;
  display: none !important;
  content: none !important;
}

/* 右侧操作区域 */
.header-actions {
  display: flex;
  align-items: center;
  min-width: 300px;
  justify-content: flex-end;
}

.switch-btn {
  color: rgba(255, 255, 255, 0.85);
  border-radius: 8px;
  padding: 8px 16px;
  height: 40px;
  transition: all 0.3s ease;
}

.switch-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
  color: #fff;
  transform: translateY(-1px);
}

.switch-text {
  margin-left: 8px;
}

.header-btn {
  color: rgba(255, 255, 255, 0.85);
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.header-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
  color: #fff;
  transform: translateY(-1px);
}

.notification-badge {
  cursor: pointer;
}

:deep(.notification-badge .ant-badge-count) {
  background: #ff4757;
  border: 2px solid #fff;
}

.user-info {
  color: rgba(255, 255, 255, 0.85);
  padding: 8px 16px;
  border-radius: 8px;
  height: auto;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.08));
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.user-avatar {
  background: linear-gradient(135deg, #faad14, #ffc53d);
  color: #fff;
  font-weight: 600;
}

.user-name {
  color: inherit;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
  margin: 0 8px;
}

/* 面包屑导航 */
.breadcrumb-container {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  padding: 12px 0;
  border-bottom: 1px solid rgba(24, 144, 255, 0.08);
  position: fixed;
  top: 72px;
  left: 0;
  right: 0;
  z-index: 99;
  height: 48px;
}

.breadcrumb-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.breadcrumb {
  margin: 0;
}

:deep(.breadcrumb .ant-breadcrumb-link) {
  color: #595959;
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
}

:deep(.breadcrumb .ant-breadcrumb-separator) {
  color: #d9d9d9;
}

/* 主内容区域 */
.admin-content {
  flex: 1;
  margin-top: 120px; /* 顶部导航(72px) + 面包屑(48px) */
  margin-bottom: 60px; /* 底部高度 */
  min-height: calc(100vh - 180px);
  overflow-y: auto; /* 允许垂直滚动 */
  overflow-x: hidden; /* 防止水平滚动 */
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(24, 144, 255, 0.08);
  min-height: calc(100vh - 260px); /* 调整内容区域最小高度 */
  overflow-y: auto; /* 允许垂直滚动 */
  overflow-x: hidden; /* 防止水平滚动 */
  max-height: calc(100vh - 260px); /* 限制最大高度以启用滚动 */
  /* 移除自动动画，由JavaScript控制 */
}

/* 底部区域 */
.admin-footer {
  background: linear-gradient(135deg, #ffffff 0%, #f8faff 100%);
  padding: 16px 24px;
  border-top: 1px solid rgba(24, 144, 255, 0.08);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 99;
  height: 60px;
  display: flex;
  align-items: center;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #666;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-normal);
}

.version {
  background: linear-gradient(135deg, #e6f7ff, #bae7ff);
  color: #1890ff;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
  border: 1px solid rgba(24, 144, 255, 0.2);
}

/* 动画效果 */
/* fadeInUp动画已移除，由JavaScript控制渐入渐出效果 */

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 12px rgba(250, 173, 20, 0.6));
  }
  50% {
    transform: scale(1.08);
    filter: drop-shadow(0 0 16px rgba(250, 173, 20, 0.8));
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-container {
    padding: 0 16px;
  }
  
  .breadcrumb-wrapper {
    padding: 0 16px;
  }
  
  .content-wrapper {
    padding: 24px;
  }
}

@media (max-width: 768px) {
  .header-container {
    flex-wrap: wrap;
    height: auto;
    padding: 12px 16px;
  }
  
  .header-brand {
    min-width: auto;
  }
  
  .header-nav {
    order: 3;
    flex-basis: 100%;
    margin-top: 12px;
  }
  
  .header-actions {
    min-width: auto;
  }
  
  .switch-text {
    display: none;
  }
  
  .user-name {
    display: none;
  }
  
  .admin-content {
    margin-top: 140px; /* 增加移动端顶部间距 */
    margin-bottom: 70px; /* 增加移动端底部间距 */
    overflow-y: auto; /* 移动端也允许滚动 */
  }
  
  .content-wrapper {
    padding: 20px;
    min-height: calc(100vh - 320px);
  }
  
  .footer-content {
    flex-direction: column;
    gap: 8px;
  }
  
  .admin-footer {
    height: 70px; /* 移动端底部高度增加 */
  }
}

@media (max-width: 480px) {
  .header-container {
    padding: 8px 12px;
  }
  
  .brand-title {
    font-size: var(--font-size-base);
  }
  
  .admin-content {
    margin-top: 150px; /* 小屏幕顶部间距进一步增加 */
    margin-bottom: 80px; /* 小屏幕底部间距增加 */
    overflow-y: auto; /* 小屏幕也允许滚动 */
  }
  
  .content-wrapper {
    padding: 16px;
    min-height: calc(100vh - 350px);
  }
  
  .header-btn {
    width: 36px;
    height: 36px;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
  }
  
  .admin-footer {
    height: 80px; /* 小屏幕底部高度进一步增加 */
  }
}
</style>