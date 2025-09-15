"""
ASGI config for ops_assets_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ops_assets_backend.settings")

# 初始化Django ASGI应用
django_asgi_app = get_asgi_application()

# 导入WebSocket路由和认证中间件
from users import routing as users_routing
from users.websocket_auth import WebSocketAuthMiddlewareStack

application = ProtocolTypeRouter({
    # Django的HTTP处理程序
    "http": django_asgi_app,
    
    # WebSocket处理程序
    "websocket": AllowedHostsOriginValidator(
        WebSocketAuthMiddlewareStack(
            URLRouter([
                # 用户相关的WebSocket路由
                path("ws/users/", URLRouter(users_routing.websocket_urlpatterns)),
            ])
        )
    ),
})