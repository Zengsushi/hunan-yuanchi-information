"""
WebSocket路由配置
"""

from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # 用户会话管理WebSocket连接
    path('session/', consumers.UserSessionConsumer.as_asgi()),
]