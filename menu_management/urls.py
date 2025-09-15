from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MenuViewSet, UserMenuConfigViewSet

router = DefaultRouter()
router.register(r'', MenuViewSet, basename='menu')
router.register(r'user-config', UserMenuConfigViewSet, basename='user-menu-config')

print(router.urls)
urlpatterns = [
    path('', include(router.urls)),
]