import { createRouter, createWebHashHistory } from 'vue-router';
import { beforeRouteLeave, afterRouteEnter } from '../utils/routeGuard';

// 引入管理页面组件
import UserLogin from '../views/admin/UserLogin.vue';
// 引入业务页面组件
import AssetDashboard from '../views/business/AssetDashboard.vue';
import ServerList from '../views/business/ServerList.vue';
import NetworkDeviceList from '../views/business/NetworkDeviceList.vue';
import AssetCategoryList from '../views/business/AssetCategoryList.vue';
import AssetStatusList from '../views/business/AssetStatusList.vue';
import IPList from '../views/business/IPList.vue';
import IPAdd from '../views/business/IPAdd.vue';
import BusinessList from '../views/business/BusinessList.vue';
import BusinessDetail from '../views/business/BusinessDetail.vue';
// 管理员组件
import AdminDashboard from '../views/admin/AdminDashboard.vue';
import AdminUsers from '../views/admin/AdminUsers.vue';
import AdminRoles from '../views/admin/AdminRoles.vue';
import AdminDictionary from '../views/admin/AdminDictionary.vue';
import AdminSettings from '../views/admin/AdminSettings.vue';
import AdminLogs from '../views/admin/AdminLogs.vue';
import AdminBackup from '../views/admin/AdminBackup.vue';
import AdminManagement from '../views/admin/AdminManagement.vue';
import FontDemo from '../views/admin/FontDemo.vue';
// 组织架构组件
import AdminDepartments from '../views/admin/AdminDepartments.vue';
import AdminPositions from '../views/admin/AdminPositions.vue';
import AdminEmployees from '../views/admin/AdminEmployees.vue';

const routes = [
  {
    path: '/login',
    name: 'login',
    component: UserLogin,
    meta: { 
      title: '用户登录',
      hideLayout: true 
    }
  },
  {    path: '/',    name: 'dashboard',    component: AssetDashboard, meta: { title: '监控概览', requiresAuth: true }  },
  {
    path: '/assets/hardware',
    name: 'HardwareAssetList',
    component: () => import('../views/business/HardwareAssetList.vue'),
    meta: { title: '硬件设施管理', requiresAuth: true }
  },
  {
    path: '/assets/software',
    name: 'SoftwareAssetList',
    component: () => import('../views/business/SoftwareAssetList.vue'),
    meta: { title: '软件资产管理', requiresAuth: true }
  },
  {
    path: '/assets/software/add',
    name: 'SoftwareAssetAdd',
    component: () => import('@/components/business/SoftwareAssetForm.vue'),
    meta: { title: '新增软件资产', requiresAuth: true }
  },
  {
    path: '/assets/software/edit/:id',
    name: 'SoftwareAssetEdit',
    component: () => import('../components/business/SoftwareAssetForm.vue'),
    meta: { title: '编辑软件资产', requiresAuth: true }
  },
  {
    path: '/servers',
    name: 'servers',
    component: ServerList,
    meta: { title: '服务器监控', requiresAuth: true }
  },
  {
    path: '/network',
    name: 'network',
    component: NetworkDeviceList,
    meta: { title: '网络设备', requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'categories',
    component: AssetCategoryList,
    meta: { title: '资产分类', requiresAuth: true }
  },
  {
    path: '/status',
    name: 'status',
    component: AssetStatusList,
    meta: { title: '资产状态', requiresAuth: true }
  },
  {
    path: '/ip-management',
    name: 'ipManagement',
    component: IPList,
    meta: { title: 'IP管理', requiresAuth: true }
  },
  {
    path: '/ip-management/add',
    name: 'ipAdd',
    component: IPAdd,
    meta: { title: '新增IP地址', requiresAuth: true }
  },
  {
    path: '/business',
    name: 'businessList',
    component: BusinessList,
    meta: { title: '业务列表', requiresAuth: true }
  },
  {
    path: '/business/:id',
    name: 'businessDetail',
    component: BusinessDetail,
    meta: { title: '业务详情', requiresAuth: true }
  },
  // 管理员路由
  {
    path: '/admin/dashboard',
    name: 'adminDashboard',
    component: AdminDashboard,
    meta: { title: '管理控制台', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'adminUsers',
    component: AdminUsers,
    meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/roles',
    name: 'adminRoles',
    component: AdminRoles,
    meta: { title: '角色权限', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/dictionary',
    name: 'adminDictionary',
    component: AdminDictionary,
    meta: { title: '字典管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/settings',
    name: 'adminSettings',
    component: AdminSettings,
    meta: { title: '系统设置', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/logs',
    name: 'adminLogs',
    component: AdminLogs,
    meta: { title: '操作日志', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/backup',
    name: 'adminBackup',
    component: AdminBackup,
    meta: { title: '数据备份', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/management',
    name: 'adminManagement',
    component: AdminManagement,
    meta: { title: '管理员管理', requiresAuth: true, requiresAdmin: true }
  },
  // 组织架构路由
  {
    path: '/admin/departments',
    name: 'adminDepartments',
    component: AdminDepartments,
    meta: { title: '部门管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/positions',
    name: 'adminPositions',
    component: AdminPositions,
    meta: { title: '职位管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/employees',
    name: 'adminEmployees',
    component: AdminEmployees,
    meta: { title: '员工管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/font-demo',
    name: 'fontDemo',
    component: FontDemo,
    meta: { title: '字体设计演示', requiresAuth: true, requiresAdmin: true }
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

// 路由守卫 - 检查登录状态和权限
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn');
  const isAdmin = localStorage.getItem('isAdmin') === 'true';
  
  // ResizeObserver 清理处理
  try {
    beforeRouteLeave(to, from, () => {});
  } catch (error) {
    console.debug('ResizeObserver清理失败:', error.message);
  }
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 运维监控系统`;
  }
  
  // 如果访问登录页面且已登录，根据权限跳转
  if (to.path === '/login' && isLoggedIn) {
    if (isAdmin) {
      next('/admin/dashboard');
    } else {
      next('/');
    }
    return;
  }
  
  // 如果需要认证且未登录，跳转到登录页
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login');
    return;
  }
  
  // 如果需要管理员权限且不是管理员，禁止访问
  if (to.meta.requiresAdmin && !isAdmin) {
    // 如果是普通用户试图访问管理员页面，跳转到主页
    next('/');
    return;
  }
  
  next();
});

// 路由后置守卫 - 处理进入页面后的初始化
router.afterEach((to, from) => {
  try {
    afterRouteEnter(to, from);
  } catch (error) {
    console.debug('ResizeObserver初始化失败:', error.message);
  }
});

export default router;