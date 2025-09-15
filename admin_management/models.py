from django.db import models
from django.utils import timezone
import json


class Dictionary(models.Model):
    """字典管理模型"""
    
    CATEGORY_CHOICES = []
    
    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '禁用'),
    ]
    
    category = models.CharField('字典分类', max_length=50, choices=CATEGORY_CHOICES)
    key = models.CharField('字典键', max_length=100)
    label = models.CharField('显示标签', max_length=200)
    description = models.TextField('描述', blank=True)
    priority = models.IntegerField('优先级', default=0, help_text='数值越大优先级越高')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    config = models.TextField('配置信息', blank=True, help_text='JSON格式的扩展配置')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'admin_dictionary'
        verbose_name = '字典'
        verbose_name_plural = verbose_name
        unique_together = [['category', 'key']]
        ordering = ['-priority', 'key']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.label}"
    
    @property
    def config_dict(self):
        """获取配置信息的字典格式"""
        if not self.config:
            return {}
        try:
            return json.loads(self.config)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @config_dict.setter
    def config_dict(self, value):
        """设置配置信息"""
        if isinstance(value, dict):
            self.config = json.dumps(value, ensure_ascii=False)
        else:
            self.config = str(value) if value else ''
    
    @classmethod
    def get_by_category(cls, category, status='active'):
        """根据分类获取字典数据"""
        queryset = cls.objects.filter(category=category)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-priority', 'key')
    
    @classmethod
    def get_categories(cls):
        """获取所有字典分类"""
        return [
            {
                'key': choice[0],
                'label': choice[1],
                'description': f'{choice[1]}相关的字典配置'
            }
            for choice in cls.CATEGORY_CHOICES
        ]


class SystemConfig(models.Model):
    """系统配置模型"""
    
    CONFIG_TYPE_CHOICES = [
        ('basic', '基本配置'),
        ('security', '安全配置'),
        ('notification', '通知配置'),
        ('integration', '集成配置'),
        ('performance', '性能配置'),
    ]
    
    name = models.CharField('配置名称', max_length=100, unique=True)
    key = models.CharField('配置键', max_length=100, unique=True)
    value = models.TextField('配置值')
    config_type = models.CharField('配置类型', max_length=20, choices=CONFIG_TYPE_CHOICES, default='basic')
    description = models.TextField('描述', blank=True)
    is_encrypted = models.BooleanField('是否加密', default=False)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'admin_system_config'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        ordering = ['config_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.key})"
    
    @property
    def value_dict(self):
        """尝试将值解析为JSON格式"""
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value


class AdminLog(models.Model):
    """管理后台操作日志"""
    
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('export', '导出'),
        ('import', '导入'),
        ('config', '配置'),
        ('login', '登录'),
        ('logout', '登出'),
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name='操作用户')
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField('模型名称', max_length=100, blank=True)
    object_id = models.CharField('对象ID', max_length=100, blank=True)
    description = models.TextField('操作描述')
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    user_agent = models.TextField('用户代理', blank=True)
    result = models.CharField('操作结果', max_length=20, choices=[('success', '成功'), ('failed', '失败')], default='success')
    error_message = models.TextField('错误信息', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        db_table = 'admin_log'
        verbose_name = '管理日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['model_name', 'created_at']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else '系统'
        return f"{username} - {self.get_action_display()} - {self.created_at}"


class DashboardWidget(models.Model):
    """仪表盘小组件配置"""
    
    WIDGET_TYPE_CHOICES = [
        ('chart', '图表'),
        ('counter', '计数器'),
        ('list', '列表'),
        ('progress', '进度条'),
        ('alert', '警告'),
    ]
    
    name = models.CharField('组件名称', max_length=100)
    title = models.CharField('显示标题', max_length=200)
    widget_type = models.CharField('组件类型', max_length=20, choices=WIDGET_TYPE_CHOICES)
    config = models.TextField('配置信息', help_text='JSON格式的组件配置')
    position_x = models.IntegerField('X位置', default=0)
    position_y = models.IntegerField('Y位置', default=0)
    width = models.IntegerField('宽度', default=4)
    height = models.IntegerField('高度', default=3)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'admin_dashboard_widget'
        verbose_name = '仪表盘组件'
        verbose_name_plural = verbose_name
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"
    
    @property
    def config_dict(self):
        """获取配置信息的字典格式"""
        try:
            return json.loads(self.config)
        except (json.JSONDecodeError, TypeError):
            return {}
