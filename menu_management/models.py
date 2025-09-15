from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Menu(models.Model):
    """菜单模型"""
    MENU_TYPE_CHOICES = [
        ('menu', '菜单'),
        ('button', '按钮'),
        ('link', '链接'),
    ]
    
    TARGET_CHOICES = [
        ('_self', '当前窗口'),
        ('_blank', '新窗口'),
    ]
    
    name = models.CharField('菜单名称', max_length=100)
    title = models.CharField('显示标题', max_length=100)
    path = models.CharField('路由路径', max_length=200, blank=True)
    component = models.CharField('组件路径', max_length=200, blank=True)
    icon = models.CharField('图标', max_length=50, blank=True)
    menu_type = models.CharField('菜单类型', max_length=20, choices=MENU_TYPE_CHOICES, default='menu')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name='父菜单')
    order_num = models.IntegerField('排序号', default=0)
    is_hidden = models.BooleanField('是否隐藏', default=False)
    is_cache = models.BooleanField('是否缓存', default=True)
    is_affix = models.BooleanField('是否固定标签', default=False)
    target = models.CharField('打开方式', max_length=10, choices=TARGET_CHOICES, default='_self')
    redirect = models.CharField('重定向路径', max_length=200, blank=True)
    permission_code = models.CharField('权限编码', max_length=100, blank=True, help_text='关联权限编码，用于权限控制')
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'menu_management'
        verbose_name = '菜单'
        verbose_name_plural = verbose_name
        ordering = ['order_num', 'id']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['order_num']),
            models.Index(fields=['permission_code']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def level(self):
        """获取菜单层级"""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level
    
    def get_children(self, user=None):
        """获取子菜单（支持权限过滤）"""
        children = self.children.filter(is_active=True).order_by('order_num')
        
        if user and not user.is_superuser:
            # 根据用户权限过滤菜单
            user_permissions = self.get_user_permissions(user)
            children = children.filter(
                models.Q(permission_code='') | 
                models.Q(permission_code__in=user_permissions)
            )
        
        return children
    
    @staticmethod
    def get_user_permissions(user):
        """获取用户权限列表"""
        permissions = set()
        
        # 超级管理员拥有所有权限
        if user.is_superuser:
            from users.models import Permission
            return Permission.objects.filter(is_active=True).values_list('code', flat=True)
        
        # 从用户角色获取权限
        if hasattr(user, 'profile') and user.profile:
            from users.models import Role
            try:
                # 假设用户profile中有role字段关联到Role模型
                role_code = user.profile.role
                role = Role.objects.filter(code=role_code, is_active=True).first()
                if role and role.permissions:
                    permissions.update(role.permissions)
            except:
                pass
        
        return list(permissions)
    
    @classmethod
    def get_menu_tree(cls, user=None, menu_type='menu'):
        """获取菜单树结构"""
        # 获取根菜单
        root_menus = cls.objects.filter(
            parent=None, 
            is_active=True,
            menu_type=menu_type
        ).order_by('order_num')
        
        if user and not user.is_superuser:
            # 根据用户权限过滤菜单
            user_permissions = cls.get_user_permissions(user)
            root_menus = root_menus.filter(
                models.Q(permission_code='') | 
                models.Q(permission_code__in=user_permissions)
            )
        
        def build_tree(menus):
            tree = []
            for menu in menus:
                menu_data = {
                    'id': menu.id,
                    'name': menu.name,
                    'title': menu.title,
                    'path': menu.path,
                    'component': menu.component,
                    'icon': menu.icon,
                    'menu_type': menu.menu_type,
                    'order_num': menu.order_num,
                    'is_hidden': menu.is_hidden,
                    'is_cache': menu.is_cache,
                    'is_affix': menu.is_affix,
                    'target': menu.target,
                    'redirect': menu.redirect,
                    'permission_code': menu.permission_code,
                    'level': menu.level,
                    'children': []
                }
                
                # 递归获取子菜单
                children = menu.get_children(user)
                if children.exists():
                    menu_data['children'] = build_tree(children)
                
                tree.append(menu_data)
            
            return tree
        
        return build_tree(root_menus)


class UserMenuConfig(models.Model):
    """用户菜单配置"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='menu_config', verbose_name='用户')
    collapsed_menus = models.JSONField('折叠的菜单', default=list, blank=True, help_text='存储用户折叠的菜单ID列表')
    pinned_menus = models.JSONField('固定的菜单', default=list, blank=True, help_text='存储用户固定的菜单ID列表')
    custom_order = models.JSONField('自定义排序', default=dict, blank=True, help_text='存储用户自定义的菜单排序')
    theme_config = models.JSONField('主题配置', default=dict, blank=True, help_text='存储用户的菜单主题配置')
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        db_table = 'user_menu_config'
        verbose_name = '用户菜单配置'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return f"{self.user.username} - 菜单配置"