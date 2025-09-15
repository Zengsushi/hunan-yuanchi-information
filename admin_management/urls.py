from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'dictionaries', views.DictionaryViewSet)
router.register(r'system-configs', views.SystemConfigViewSet)
router.register(r'logs', views.AdminLogViewSet)
router.register(r'dashboard-widgets', views.DashboardWidgetViewSet)

# URL配置
urlpatterns = [
    # 仪表盘统计API
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # 包含视图集路由
    path('', include(router.urls)),
]