from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.sessions.models import Session
import json


class User(AbstractUser):
    """扩展用户模型"""
    email = models.EmailField('邮箱地址', unique=True)
    phone = models.CharField('手机号码', max_length=11, blank=True, null=True)
    avatar = models.URLField('头像', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    last_login_ip = models.GenericIPAddressField('最后登录IP', blank=True, null=True)
    
    class Meta:
        db_table = 'custom_user'  # 使用自定义表名避免冲突
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class UserProfile(models.Model):
    """用户资料扩展"""
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('operator', '操作员'),
        ('viewer', '观察者'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    real_name = models.CharField('真实姓名', max_length=50, blank=True)
    department = models.CharField('部门', max_length=100, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='viewer')
    is_active = models.BooleanField('是否激活', default=True)
    login_count = models.IntegerField('登录次数', default=0)
    last_activity = models.DateTimeField('最后活动时间', auto_now=True)
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} - {self.real_name}"


class Role(models.Model):
    """角色模型"""
    name = models.CharField('角色名称', max_length=50, unique=True)
    code = models.CharField('角色编码', max_length=50, unique=True)
    description = models.TextField('描述', blank=True)
    permissions = models.JSONField('权限列表', default=list)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user_role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Permission(models.Model):
    """权限模型"""
    name = models.CharField('权限名称', max_length=100)
    code = models.CharField('权限编码', max_length=100, unique=True)
    description = models.TextField('描述', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    icon = models.CharField('图标', max_length=50, blank=True)
    url = models.CharField('URL路径', max_length=200, blank=True)
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'user_permission'
        verbose_name = '权限'
        verbose_name_plural = verbose_name
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class LoginLog(models.Model):
    """登录日志"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    ip_address = models.GenericIPAddressField('IP地址')
    user_agent = models.TextField('用户代理', blank=True)
    login_time = models.DateTimeField('登录时间', auto_now_add=True)
    logout_time = models.DateTimeField('登出时间', null=True, blank=True)
    is_success = models.BooleanField('是否成功', default=True)
    failure_reason = models.CharField('失败原因', max_length=200, blank=True)
    
    class Meta:
        db_table = 'user_login_log'
        verbose_name = '登录日志'
        verbose_name_plural = verbose_name
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"


class UserSession(models.Model):
    """用户会话管理"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    session_key = models.CharField('会话密钥', max_length=40, unique=True)
    ip_address = models.GenericIPAddressField('IP地址')
    user_agent = models.TextField('用户代理', blank=True)
    device_info = models.CharField('设备信息', max_length=200, blank=True)
    login_time = models.DateTimeField('登录时间', auto_now_add=True)
    last_activity = models.DateTimeField('最后活动时间', auto_now=True)
    is_active = models.BooleanField('是否活跃', default=True)
    logout_reason = models.CharField('登出原因', max_length=50, blank=True,
                                   choices=[
                                       ('normal', '正常登出'),
                                       ('kicked', '被管理员踢出'),
                                       ('timeout', '会话超时'),
                                       ('force', '强制登出'),
                                       ('replaced', '被新会话替换'),
                                       ('limit_exceeded', '超出会话限制'),
                                       ('admin_clear', '管理员清理'),
                                   ])
    # WebSocket连接相关字段
    websocket_channels = models.JSONField('WebSocket通道', default=list, blank=True)
    has_websocket = models.BooleanField('是否有WebSocket连接', default=False)
    
    class Meta:
        db_table = 'user_session'
        verbose_name = '用户会话'
        verbose_name_plural = verbose_name
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.ip_address} - {self.login_time}"
    
    @property
    def is_online(self):
        """判断用户是否在线（5分钟内有活动且会话激活）"""
        if not self.is_active:
            return False
        
        # 检查会话是否过期（5分钟无活动认为离线）
        timeout_threshold = timezone.now() - timezone.timedelta(minutes=5)
        return self.last_activity > timeout_threshold
    
    def mark_offline(self, reason='normal'):
        """标记会话为离线"""
        self.is_active = False
        self.logout_reason = reason
        self.websocket_channels = []  # 清空WebSocket通道
        self.has_websocket = False
        self.save()
        
        # 删除对应的Django session
        try:
            session = Session.objects.get(session_key=self.session_key)
            session.delete()
        except Session.DoesNotExist:
            pass
    
    def add_websocket_channel(self, channel_name):
        """添加WebSocket通道"""
        if not self.websocket_channels:
            self.websocket_channels = []
        if channel_name not in self.websocket_channels:
            self.websocket_channels.append(channel_name)
            self.has_websocket = True
            self.save(update_fields=['websocket_channels', 'has_websocket'])
    
    def remove_websocket_channel(self, channel_name):
        """移除WebSocket通道"""
        if self.websocket_channels and channel_name in self.websocket_channels:
            self.websocket_channels.remove(channel_name)
            self.has_websocket = len(self.websocket_channels) > 0
            self.save(update_fields=['websocket_channels', 'has_websocket'])
    
    def get_websocket_channels(self):
        """获取所有WebSocket通道"""
        return self.websocket_channels or []
    
    @classmethod
    def get_online_users_count(cls):
        """获取在线用户数量"""
        timeout_threshold = timezone.now() - timezone.timedelta(minutes=5)
        return cls.objects.filter(
            is_active=True,
            last_activity__gt=timeout_threshold
        ).values('user').distinct().count()
    
    @classmethod
    def cleanup_expired_sessions(cls, timeout_minutes=5):
        """清理过期的会话记录"""
        timeout_threshold = timezone.now() - timezone.timedelta(minutes=timeout_minutes)
        expired_sessions = cls.objects.filter(
            is_active=True,
            last_activity__lte=timeout_threshold
        )
        
        count = 0
        for session in expired_sessions:
            session.mark_offline('timeout')
            count += 1
        
        return count
    
    @classmethod
    def cleanup_duplicate_sessions(cls, user, session_key):
        """清理用户的重复会话，避免唯一性约束冲突"""
        existing_sessions = cls.objects.filter(
            user=user,
            session_key=session_key
        )
        
        count = 0
        for session in existing_sessions:
            session.mark_offline('replaced')
            count += 1
            
        return count
    
    @classmethod
    def cleanup_old_inactive_sessions(cls, days=30):
        """清理旧的非活跃会话记录（物理删除）"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        old_sessions = cls.objects.filter(
            is_active=False,
            last_activity__lte=cutoff_date
        )
        
        count = old_sessions.count()
        old_sessions.delete()
        return count
    
    @classmethod
    def safe_create_session(cls, user, session_key, ip_address, user_agent, device_info=''):
        """安全创建会话，自动处理重复和过期会话"""
        # 1. 清理过期会话
        expired_count = cls.cleanup_expired_sessions()
        
        # 2. 清理重复会话
        duplicate_count = cls.cleanup_duplicate_sessions(user, session_key)
        
        # 3. 限制最大活跃会话数
        active_sessions = cls.objects.filter(user=user, is_active=True)
        max_sessions = 5
        if active_sessions.count() >= max_sessions:
            # 清理最旧的会话
            oldest_sessions = active_sessions.order_by('last_activity')[:active_sessions.count() - max_sessions + 1]
            for session in oldest_sessions:
                session.mark_offline('limit_exceeded')
        
        # 4. 创建新会话
        try:
            session = cls.objects.create(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                device_info=device_info
            )
            return session, {'expired': expired_count, 'duplicates': duplicate_count}
        except Exception as e:
            # 如果仍然有重复，再次清理
            cls.cleanup_duplicate_sessions(user, session_key)
            session = cls.objects.create(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                device_info=device_info
            )
            return session, {'expired': expired_count, 'duplicates': duplicate_count, 'retry': True}