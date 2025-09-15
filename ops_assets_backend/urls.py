"""
URL configuration for ops_assets_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def test_cors(request):
    """测试CORS是否正常工作"""
    return JsonResponse({
        'message': 'CORS is working!',
        'origin': request.META.get('HTTP_ORIGIN', 'No origin'),
        'method': request.method
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("assets.urls")),  # 更新为正确的模块路径
    path("api/", include("users.urls")),  # 更新为正确的模块路径
    path("api/", include("admin_management.urls")),  # 管理后台API路由（直接在api/下）
    path("api/ip-management/", include("ip_management.urls")),  # IP管理API路由
    path("api/business/", include("business.urls")),  # 业务管理API路由
    path("api/organization/", include("organization.urls")),  # 组织架构API路由
    path("api/admin/", include("admin_management.urls")),  # 管理后台API路由（兼容性）
    path("api/menus/", include("menu_management.urls")),  # 菜单管理API路由
    path("test-cors/", test_cors, name="test_cors"),
]
