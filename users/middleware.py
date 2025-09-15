"""
用户会话自动清理中间件
"""

import time
import logging
from django.utils import timezone
from django.core.cache import cache
from users.models import UserSession

logger = logging.getLogger(__name__)


class SessionCleanupMiddleware:
    """
    用户会话自动清理中间件
    定期清理过期会话，避免数据库中积累太多无效会话
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.cleanup_interval = 300  # 5分钟清理一次
        self.last_cleanup_cache_key = 'session_cleanup_last_run'
    
    def __call__(self, request):
        # 在处理请求前检查是否需要清理过期会话
        self.maybe_cleanup_sessions()
        
        response = self.get_response(request)
        
        return response
    
    def maybe_cleanup_sessions(self):
        """
        检查是否需要清理会话
        使用缓存避免频繁清理
        """
        now = time.time()
        last_cleanup = cache.get(self.last_cleanup_cache_key, 0)
        
        # 如果距离上次清理超过指定间隔，则执行清理
        if now - last_cleanup > self.cleanup_interval:
            try:
                self.cleanup_sessions()
                cache.set(self.last_cleanup_cache_key, now, timeout=self.cleanup_interval * 2)
            except Exception as e:
                logger.error(f"会话清理失败: {str(e)}")
    
    def cleanup_sessions(self):
        """执行会话清理"""
        try:
            # 清理过期会话
            expired_count = UserSession.cleanup_expired_sessions(timeout_minutes=5)
            
            # 定期清理旧的非活跃会话（每天清理一次）
            cleanup_old_cache_key = 'session_cleanup_old_last_run'
            last_old_cleanup = cache.get(cleanup_old_cache_key, 0)
            now = time.time()
            
            # 24小时清理一次旧记录
            if now - last_old_cleanup > 86400:  # 24小时
                old_count = UserSession.cleanup_old_inactive_sessions(days=30)
                cache.set(cleanup_old_cache_key, now, timeout=86400)
                logger.info(f"会话清理完成: 过期会话 {expired_count} 个, 旧记录 {old_count} 个")
            else:
                if expired_count > 0:
                    logger.info(f"会话清理完成: 过期会话 {expired_count} 个")
            
        except Exception as e:
            logger.error(f"执行会话清理时出错: {str(e)}")