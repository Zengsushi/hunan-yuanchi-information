"""
WebSocket认证和权限验证中间件
"""

import logging
from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from .models import UserSession

User = get_user_model()
logger = logging.getLogger(__name__)


class WebSocketTokenAuthMiddleware:
    """
    WebSocket Token认证中间件
    从查询参数中获取token并验证用户身份
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # 解析查询参数
        query_params = parse_qs(scope['query_string'].decode())
        token = query_params.get('token')
        
        if token:
            token = token[0]  # 获取第一个token值
            user = await self.get_user_from_token(token)
            if user:
                scope['user'] = user
                scope['token'] = token
                logger.info(f"WebSocket认证成功: {user.username}")
            else:
                scope['user'] = AnonymousUser()
                scope['token'] = None
                logger.warning(f"WebSocket认证失败: 无效token {token}")
        else:
            scope['user'] = AnonymousUser()
            scope['token'] = None
            logger.warning("WebSocket认证失败: 缺少token")

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token):
        """根据token获取用户"""
        try:
            token_obj = Token.objects.select_related('user').get(key=token)
            user = token_obj.user
            
            # 检查用户是否活跃
            if not user.is_active:
                logger.warning(f"用户 {user.username} 已被禁用")
                return None
                
            # 检查用户profile是否活跃
            if hasattr(user, 'profile') and not user.profile.is_active:
                logger.warning(f"用户 {user.username} 的profile已被禁用")
                return None
                
            return user
        except Token.DoesNotExist:
            logger.warning(f"Token不存在: {token}")
            return None
        except Exception as e:
            logger.error(f"获取用户时出错: {str(e)}")
            return None


class WebSocketPermissionMiddleware:
    """
    WebSocket权限验证中间件
    验证用户对特定WebSocket端点的访问权限
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        user = scope.get('user')
        path = scope.get('path', '')
        
        # 如果用户未认证，拒绝连接
        if not user or user.is_anonymous:
            logger.warning(f"未认证用户尝试访问WebSocket: {path}")
            await self.close_connection(send, 4001, "认证失败")
            return

        # 检查特定路径的权限
        if not await self.check_permission(user, path):
            logger.warning(f"用户 {user.username} 没有访问 {path} 的权限")
            await self.close_connection(send, 4003, "权限不足")
            return

        # 权限验证通过，继续处理
        logger.info(f"用户 {user.username} 通过权限验证，访问 {path}")
        return await self.inner(scope, receive, send)

    async def close_connection(self, send, code, reason):
        """关闭WebSocket连接"""
        await send({
            'type': 'websocket.close',
            'code': code,
            'text': reason
        })

    @database_sync_to_async
    def check_permission(self, user, path):
        """检查用户权限"""
        try:
            # 用户会话路径权限检查
            if '/ws/users/session/' in path:
                # 所有已认证用户都可以访问自己的会话WebSocket
                return True
            
            # 管理员通知路径权限检查
            if '/ws/admin/' in path:
                # 只有管理员可以访问管理员WebSocket
                is_admin = user.is_superuser or (
                    hasattr(user, 'profile') and user.profile.role == 'admin'
                )
                return is_admin
            
            # 其他路径默认允许已认证用户访问
            return True
            
        except Exception as e:
            logger.error(f"检查权限时出错: {str(e)}")
            return False


class WebSocketSessionMiddleware:
    """
    WebSocket会话管理中间件
    管理WebSocket连接的会话状态
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        user = scope.get('user')
        token = scope.get('token')
        
        if user and not user.is_anonymous and token:
            # 获取或创建用户会话
            session = await self.get_or_create_session(user, token, scope)
            scope['user_session'] = session
            
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_or_create_session(self, user, token, scope):
        """获取或创建用户会话"""
        try:
            # 尝试获取现有会话
            # 使用token的前40个字符作为session_key进行查询
            session_key = token[:40] if len(token) >= 40 else token
            session = UserSession.objects.filter(
                user=user,
                session_key=session_key,
                is_active=True
            ).first()
            
            if session:
                logger.info(f"找到现有会话: {session.id}")
                return session
            else:
                # 获取客户端信息
                headers = dict(scope.get('headers', []))
                user_agent = headers.get(b'user-agent', b'').decode('utf-8')
                
                # 从WebSocket连接中获取IP地址比较复杂，这里简化处理
                ip_address = self.get_client_ip_from_scope(scope)
                
                # 创建新会话，使用token的前40个字符作为session_key
                session_key = token[:40] if len(token) >= 40 else token
                session = UserSession.objects.create(
                    user=user,
                    session_key=session_key,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    device_info=self.extract_device_info(user_agent)
                )
                
                logger.info(f"创建新会话: {session.id}")
                return session
                
        except Exception as e:
            logger.error(f"获取或创建会话时出错: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return None

    def get_client_ip_from_scope(self, scope):
        """从WebSocket scope中获取客户端IP"""
        try:
            # 获取客户端地址
            client = scope.get('client')
            if client:
                return client[0]
            
            # 从headers中获取转发的IP
            headers = dict(scope.get('headers', []))
            forwarded_for = headers.get(b'x-forwarded-for')
            if forwarded_for:
                return forwarded_for.decode('utf-8').split(',')[0].strip()
            
            real_ip = headers.get(b'x-real-ip')
            if real_ip:
                return real_ip.decode('utf-8')
            
            return '127.0.0.1'  # 默认值
            
        except Exception as e:
            logger.error(f"获取客户端IP时出错: {str(e)}")
            return '127.0.0.1'

    def extract_device_info(self, user_agent):
        """从User-Agent提取设备信息"""
        if not user_agent:
            return '未知设备'
        
        user_agent = user_agent.lower()
        
        # 检测操作系统
        if 'windows' in user_agent:
            os_info = 'Windows'
        elif 'mac' in user_agent:
            os_info = 'macOS'
        elif 'linux' in user_agent:
            os_info = 'Linux'
        elif 'android' in user_agent:
            os_info = 'Android'
        elif 'iphone' in user_agent or 'ipad' in user_agent:
            os_info = 'iOS'
        else:
            os_info = '未知系统'
        
        # 检测浏览器
        if 'chrome' in user_agent:
            browser = 'Chrome'
        elif 'firefox' in user_agent:
            browser = 'Firefox'
        elif 'safari' in user_agent:
            browser = 'Safari'
        elif 'edge' in user_agent:
            browser = 'Edge'
        else:
            browser = '未知浏览器'
        
        return f'{os_info} - {browser}'


def WebSocketAuthMiddlewareStack(inner):
    """
    WebSocket认证中间件栈
    组合多个中间件来处理认证、权限和会话
    """
    return WebSocketTokenAuthMiddleware(
        WebSocketPermissionMiddleware(
            WebSocketSessionMiddleware(inner)
        )
    )