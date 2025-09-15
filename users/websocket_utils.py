"""
WebSocket工具模块
处理用户会话和WebSocket连接的关联管理
"""

import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserSession

User = get_user_model()
logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_to_user(self, user_id, message_type, data=None):
        """
        向指定用户发送WebSocket消息
        
        Args:
            user_id: 用户ID
            message_type: 消息类型
            data: 消息数据
        """
        if data is None:
            data = {}
            
        group_name = f"user_{user_id}"
        
        logger.info(f"准备向用户组 {group_name} 发送消息，消息类型: {message_type}")
        logger.info(f"原始消息数据: {data}")
        
        try:
            # 确保消息数据中包含正确的type字段
            message_data = {
                'type': message_type,
                **{k: v for k, v in data.items() if k != 'type'}  # 排除data中的type字段
            }
            
            logger.info(f"最终发送的消息数据: {message_data}")
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                message_data
            )
            logger.info(f"向用户 {user_id} 发送WebSocket消息成功: {message_type}")
            return True
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {str(e)}")
            logger.exception("详细错误信息:")
            return False
    
    def kick_out_user(self, user_id, kicked_by_user=None, reason="管理员操作"):
        """
        踢出用户（通过WebSocket）
        
        Args:
            user_id: 被踢出的用户ID
            kicked_by_user: 操作者用户对象
            reason: 踢出原因
        """
        try:
            user = User.objects.get(id=user_id)
            
            # 准备消息数据（不包含type字段）
            message_data = {
                'message': f'您已被管理员踢出系统',
                'reason': reason,
                'kicked_by': kicked_by_user.username if kicked_by_user else 'admin',
                'timestamp': str(timezone.now())
            }
            
            logger.info(f"准备踢出用户 {user.username} (ID: {user_id})，原因: {reason}")
            logger.info(f"准备发送的消息数据: {message_data}")
            
            # 发送踢出消息，使用正确的消息类型
            # 注意：在Django Channels中，点号需要转换为下划线
            success = self.send_to_user(user_id, 'user_kicked_out', message_data)
            
            logger.info(f"向用户 {user.username} 发送踢出消息结果: {'成功' if success else '失败'}")
            
            # 获取用户的活跃会话
            user_sessions = UserSession.objects.filter(
                user_id=user_id,
                is_active=True
            )
            
            # 记录有多少个活跃会话
            active_sessions_count = user_sessions.count()
            logger.info(f"用户 {user.username} 有 {active_sessions_count} 个活跃会话")
            
            # 如果没有活跃会话，记录警告信息
            if active_sessions_count == 0:
                logger.warning(f"用户 {user.username} 没有活跃会话，可能未建立WebSocket连接")
            
            # 更新用户会话状态（无论是否有WebSocket连接）
            kicked_sessions = 0
            for session in user_sessions:
                session.mark_offline('kicked')
                kicked_sessions += 1
            
            logger.info(f"成功踢出用户 {user.username}，关闭了 {kicked_sessions} 个会话")
            
            # 返回结果，包含是否有WebSocket连接的信息
            return {
                'success': True,
                'user_id': user_id,
                'username': user.username,
                'kicked_sessions': kicked_sessions,
                'had_active_sessions': active_sessions_count > 0,
                'had_websocket_connection': active_sessions_count > 0 and 
                    any(session.has_websocket for session in user_sessions)
            }
                
        except User.DoesNotExist:
            logger.error(f"踢出用户失败：用户ID {user_id} 不存在")
            return {
                'success': False,
                'error': '用户不存在'
            }
        except Exception as e:
            logger.error(f"踢出用户时发生错误: {str(e)}")
            logger.exception("详细错误信息:")
            return {
                'success': False,
                'error': str(e)
            }
    
    def force_logout_user(self, user_id, reason="会话过期"):
        """
        强制用户登出
        
        Args:
            user_id: 用户ID
            reason: 登出原因
        """
        message_data = {
            'message': '您的会话已过期，请重新登录',
            'reason': reason,
            'timestamp': str(timezone.now())
        }
        
        return self.send_to_user(user_id, 'force_logout', message_data)
    
    def notify_user_status_change(self, user_id, status_data):
        """
        通知用户状态变化
        
        Args:
            user_id: 用户ID
            status_data: 状态数据
        """
        return self.send_to_user(user_id, 'user_status_change', status_data)
    
    def broadcast_system_notification(self, message, level='info'):
        """
        广播系统通知
        
        Args:
            message: 通知消息
            level: 消息级别 (info, warning, error)
        """
        try:
            async_to_sync(self.channel_layer.group_send)(
                "notifications",
                {
                    'type': 'system_notification',
                    'message': message,
                    'level': level,
                    'timestamp': str(timezone.now())
                }
            )
            return True
        except Exception as e:
            logger.error(f"广播系统通知失败: {str(e)}")
            return False
    
    def get_user_websocket_status(self, user_id):
        """
        获取用户WebSocket连接状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 连接状态信息
        """
        try:
            sessions = UserSession.objects.filter(
                user_id=user_id,
                is_active=True,
                has_websocket=True
            )
            
            total_channels = 0
            session_data = []
            
            for session in sessions:
                channels = session.get_websocket_channels()
                total_channels += len(channels)
                
                session_data.append({
                    'session_id': session.id,
                    'ip_address': session.ip_address,
                    'login_time': session.login_time.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'channels_count': len(channels)
                })
            
            return {
                'user_id': user_id,
                'has_websocket': total_channels > 0,
                'total_channels': total_channels,
                'active_sessions': len(session_data),
                'sessions': session_data
            }
            
        except Exception as e:
            logger.error(f"获取用户WebSocket状态失败: {str(e)}")
            return {
                'user_id': user_id,
                'has_websocket': False,
                'total_channels': 0,
                'active_sessions': 0,
                'sessions': [],
                'error': str(e)
            }


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()


def kick_out_user_via_websocket(user_id, kicked_by_user=None, reason="管理员操作"):
    """
    通过WebSocket踢出用户的便捷函数
    """
    return websocket_manager.kick_out_user(user_id, kicked_by_user, reason)


def force_logout_user_via_websocket(user_id, reason="会话过期"):
    """
    通过WebSocket强制用户登出的便捷函数
    """
    return websocket_manager.force_logout_user(user_id, reason)