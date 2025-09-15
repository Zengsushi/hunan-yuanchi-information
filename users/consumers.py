"""
WebSocket消费者处理用户连接和会话管理
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authtoken.models import Token
from .models import UserSession

User = get_user_model()
logger = logging.getLogger(__name__)


class UserSessionConsumer(AsyncWebsocketConsumer):
    """
    用户会话WebSocket消费者
    处理用户连接、断开连接和踢出用户消息
    """

    async def connect(self):
        """处理WebSocket连接"""
        # 从中间件获取用户信息
        self.user = self.scope.get('user')
        self.token = self.scope.get('token')
        self.user_session = self.scope.get('user_session')
        self.user_group_name = None
        
        # 检查用户是否已认证
        if not self.user or self.user.is_anonymous:
            logger.warning("未认证用户尝试连接WebSocket")
            await self.close(code=4001)
            return
        
        # 设置用户组名
        self.user_group_name = f"user_{self.user.id}"
        
        # 将当前连接加入用户组
        if hasattr(self, 'channel_layer') and self.channel_layer:
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
        
        # 接受WebSocket连接
        await self.accept()
        
        # 记录WebSocket连接到会话
        if self.user_session:
            await self.add_websocket_to_session(self.user_session, self.channel_name)
        else:
            # 如果没有找到对应的会话，尝试创建或查找
            logger.warning(f"用户 {self.user.username} 的WebSocket连接没有对应的会话")
            self.user_session = await self.find_or_create_user_session()
            if self.user_session:
                await self.add_websocket_to_session(self.user_session, self.channel_name)
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': '已连接到用户会话管理服务',
            'user_id': self.user.id,
            'username': self.user.username,
            'session_id': self.user_session.id if self.user_session else None
        }))
        
        logger.info(f"用户 {self.user.username} 建立WebSocket连接")

    async def disconnect(self, close_code):
        """处理WebSocket断开连接"""
        if self.user and self.user_group_name:
            # 从用户组移除连接
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
            
            # 清理WebSocket连接记录
            if self.user_session:
                await self.remove_websocket_from_session(self.user_session, self.channel_name)
            
            logger.info(f"用户 {self.user.username} 断开WebSocket连接，代码: {close_code}")

    @database_sync_to_async
    def add_websocket_to_session(self, session, channel_name):
        """将WebSocket通道添加到会话"""
        try:
            if session:
                session.add_websocket_channel(channel_name)
                logger.info(f"将WebSocket通道 {channel_name} 添加到会话 {session.id}")
        except Exception as e:
            logger.error(f"添加WebSocket通道到会话时出错: {str(e)}")

    @database_sync_to_async
    def find_or_create_user_session(self):
        """查找或创建用户会话"""
        try:
            # 先查找最近的活跃会话
            session = UserSession.objects.filter(
                user=self.user,
                is_active=True
            ).order_by('-last_activity').first()
            
            if session:
                logger.info(f"找到用户 {self.user.username} 的活跃会话: {session.id}")
                return session
            
            # 如果没有活跃会话，创建一个新的
            logger.info(f"为用户 {self.user.username} 创建新的WebSocket会话")
            
            # 从 token 获取基本信息
            token_key = self.token[:40] if self.token else f"ws_{self.user.id}_{timezone.now().timestamp()}"
            
            session = UserSession.objects.create(
                user=self.user,
                session_key=token_key,
                ip_address=self.scope.get('client', ['unknown', None])[0],
                user_agent='WebSocket Connection',
                device_info='WebSocket Client'
            )
            
            logger.info(f"为用户 {self.user.username} 创建了新会话: {session.id}")
            return session
            
        except Exception as e:
            logger.error(f"查找或创建用户会话时出错: {str(e)}")
            return None

    @database_sync_to_async
    def remove_websocket_from_session(self, session, channel_name):
        """从会话中移除WebSocket通道"""
        try:
            if session:
                session.remove_websocket_channel(channel_name)
                logger.info(f"从会话 {session.id} 移除WebSocket通道 {channel_name}")
        except Exception as e:
            logger.error(f"从会话移除WebSocket通道时出错: {str(e)}")

    async def receive(self, text_data):
        """处理接收到的WebSocket消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # 心跳消息
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': data.get('timestamp')
                }))
            elif message_type == 'user_status_check':
                # 检查用户状态
                if self.user:
                    is_online = await self.check_user_online_status(self.user)
                    await self.send(text_data=json.dumps({
                        'type': 'user_status',
                        'is_online': is_online,
                        'user_id': self.user.id
                    }))
            else:
                logger.warning(f"收到未知消息类型: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("收到无效的JSON消息")
        except Exception as e:
            logger.error(f"处理WebSocket消息时出错: {str(e)}")

    async def user_kicked_out(self, event):
        """处理用户被踢出的消息"""
        logger.info(f"=== 开始处理用户被踢出消息 ===")
        logger.info(f"收到踢出用户消息: {event}")
        logger.info(f"准备向客户端发送踢出通知: {event}")
        
        # 向客户端发送踢出通知
        try:
            await self.send(text_data=json.dumps({
                'type': 'kicked_out',  # 修复消息类型，与前端处理一致
                'message': event['message'],
                'reason': event.get('reason', '管理员操作'),
                'kicked_by': event.get('kicked_by', 'system')
            }))
            logger.info("踢出通知发送成功")
        except Exception as e:
            logger.error(f"发送踢出通知时出错: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
        
        logger.info(f"已向客户端发送踢出通知，准备关闭WebSocket连接")
        
        # 关闭WebSocket连接
        try:
            await self.close(code=4000)
            logger.info(f"WebSocket连接已关闭")
        except Exception as e:
            logger.error(f"关闭WebSocket连接时出错: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")

    async def force_logout(self, event):
        """处理强制登出消息"""
        logger.info(f"=== 开始处理强制登出消息 ===")
        logger.info(f"收到强制登出消息: {event}")
        logger.info(f"准备向客户端发送强制登出通知: {event}")
        
        # 向客户端发送强制登出通知
        try:
            await self.send(text_data=json.dumps({
                'type': 'force_logout',  # 保持与前端处理一致
                'message': event['message'],
                'reason': event.get('reason', '会话过期或管理员操作')
            }))
            logger.info("强制登出通知发送成功")
        except Exception as e:
            logger.error(f"发送强制登出通知时出错: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
        
        logger.info(f"已向客户端发送强制登出通知，准备关闭WebSocket连接")
        
        # 关闭WebSocket连接
        try:
            await self.close(code=4000)
            logger.info(f"WebSocket连接已关闭")
        except Exception as e:
            logger.error(f"关闭WebSocket连接时出错: {str(e)}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
    
    @database_sync_to_async
    def check_user_online_status(self, user):
        """检查用户在线状态"""
        try:
            return UserSession.objects.filter(
                user=user,
                is_active=True
            ).exists()
        except Exception:
            return False


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    通知消费者
    处理系统通知和实时消息推送
    """

    async def connect(self):
        """处理WebSocket连接"""
        # 获取通知组名
        self.notification_group_name = "notifications"
        
        # 认证逻辑（可以根据需要实现）
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        """处理WebSocket断开连接"""
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """处理接收到的消息"""
        pass

    async def system_notification(self, event):
        """处理系统通知"""
        await self.send(text_data=json.dumps({
            'type': 'system_notification',
            'message': event['message'],
            'level': event.get('level', 'info'),
            'timestamp': event.get('timestamp')
        }))