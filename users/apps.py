from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'  # 更新为正确的模块路径
    label = 'users'  # 添加简短的标签名用于AUTH_USER_MODEL
    verbose_name = '用户管理'
    
    def ready(self):
        """应用准备就绪时执行"""
        # 导入信号处理器
        try:
            from . import signals
        except ImportError:
            pass