from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IPRecordViewSet, ScanTaskViewSet, ScanAPIView, ZabbixManagementAPIView

# 创建路由器
router = DefaultRouter()
router.register(r'records', IPRecordViewSet, basename='iprecord')
router.register(r'scan-tasks', ScanTaskViewSet, basename='scantask')

urlpatterns = [
    # RESTful API路由
    path('', include(router.urls)),
    
    # 兼容前端的扫描API
    path('scan/', ScanAPIView.as_view(), name='scan-api'),
    
    # 扫描任务状态和结果API（兼容前端）
    path('scan/<uuid:pk>/status/', 
         ScanTaskViewSet.as_view({'get': 'status'}), 
         name='scan-task-status'),
    path('scan/<uuid:pk>/results/', 
         ScanTaskViewSet.as_view({'get': 'results'}), 
         name='scan-task-results'),
    path('scan/<uuid:pk>/', 
         ScanTaskViewSet.as_view({'delete': 'cancel'}), 
         name='scan-task-cancel'),
    
    # 扫描历史
    path('scan/history/', 
         ScanTaskViewSet.as_view({'get': 'history'}), 
         name='scan-history'),
    
    # 同步Zabbix IP
    path('scan-tasks/<uuid:pk>/sync-zabbix-ips/', 
         ScanTaskViewSet.as_view({'post': 'sync_zabbix_ips'}), 
         name='sync-zabbix-ips'),
    
    # 异步任务状态查询
    path('scan-tasks/<uuid:pk>/async-status/', 
         ScanTaskViewSet.as_view({'get': 'async_status'}), 
         name='async-task-status'),
    
    # 停止异步任务
    path('scan-tasks/<uuid:pk>/stop-async/', 
         ScanTaskViewSet.as_view({'post': 'stop_async'}), 
         name='stop-async-task'),
    
    # Zabbix管理API
    path('zabbix/management/', 
         ZabbixManagementAPIView.as_view(), 
         name='zabbix-management'),
]