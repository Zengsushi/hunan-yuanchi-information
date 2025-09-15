from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'roles', views.RoleViewSet)
router.register(r'permissions', views.PermissionViewSet)

# URL配置
urlpatterns = [
    # 认证相关API - 添加斜杠保持一致性
    path('auth/login/', views.login_api, name='login'),
    path('auth/logout/', views.logout_api, name='logout'),
    path('auth/me/', views.current_user_api, name='current_user'),
    path('auth/refresh/', views.refresh_token_api, name='refresh_token'),
    path('auth/change-password/', views.change_password_api, name='change_password'),
    
    # 包含视图集路由
    path('', include(router.urls)),
]