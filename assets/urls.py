from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetViewSet,
    AssetCategoryViewSet,
    AssetStatusViewSet,
    ServerViewSet,
    NetworkDeviceViewSet
)
from .views_hardware import (
    HardwareAssetViewSet,
    SupplierViewSet,
    SpecificationUpdateRecordViewSet,
    WarrantyUpdateRecordViewSet
)
from .views_software import (
    SoftwareAssetViewSet,
    SoftwareLicenseUpdateRecordViewSet,
    SoftwareVersionUpdateRecordViewSet,
    SoftwareDeploymentViewSet
)

router = DefaultRouter()
# 资产管理相关路由
router.register(r'assets', AssetViewSet)
router.register(r'categories', AssetCategoryViewSet)
router.register(r'statuses', AssetStatusViewSet)
router.register(r'servers', ServerViewSet)
router.register(r'network-devices', NetworkDeviceViewSet)

# 硬件设施相关路由
router.register(r'hardware-assets', HardwareAssetViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'spec-update-records', SpecificationUpdateRecordViewSet)
router.register(r'warranty-update-records', WarrantyUpdateRecordViewSet)

# 软件资产相关路由
router.register(r'software-assets', SoftwareAssetViewSet)
router.register(r'software-license-records', SoftwareLicenseUpdateRecordViewSet)
router.register(r'software-version-records', SoftwareVersionUpdateRecordViewSet)
router.register(r'software-deployments', SoftwareDeploymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]