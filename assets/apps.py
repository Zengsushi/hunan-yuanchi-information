from django.apps import AppConfig


class AssetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "assets"  # 更新为正确的模块路径
    label = 'assets'  # 添加简短的标签名
    verbose_name = '资产管理'
