from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BusinessViewSet,
    BusinessIPViewSet,
    BusinessMonthlyStatsViewSet,
    business_statistics,
    monthly_data_summary,
    yearly_trend
)

router = DefaultRouter()
# 业务管理相关路由
router.register(r'businesses', BusinessViewSet)
router.register(r'business-ips', BusinessIPViewSet)
router.register(r'monthly-stats', BusinessMonthlyStatsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 统计接口
    path('statistics/', business_statistics, name='business-statistics'),
    path('monthly-summary/', monthly_data_summary, name='monthly-data-summary'),
    path('yearly-trend/', yearly_trend, name='yearly-trend'),
]