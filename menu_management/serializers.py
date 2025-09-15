from rest_framework import serializers
from .models import Menu, UserMenuConfig


class MenuSerializer(serializers.ModelSerializer):
    """菜单序列化器"""
    children = serializers.SerializerMethodField()
    level = serializers.ReadOnlyField()
    
    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'title', 'path', 'component', 'icon', 'menu_type',
            'parent', 'order_num', 'is_hidden', 'is_cache', 'is_affix', 'target',
            'redirect', 'permission_code', 'is_active', 'level', 'children',
            'created_at', 'updated_at'
        ]
    
    def get_children(self, obj):
        """获取子菜单"""
        request = self.context.get('request')
        user = request.user if request else None
        
        children = obj.get_children(user)
        if children.exists():
            return MenuSerializer(children, many=True, context=self.context).data
        return []


class MenuTreeSerializer(serializers.ModelSerializer):
    """菜单树序列化器（用于前端路由）"""
    children = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = ['id', 'name', 'path', 'component', 'redirect', 'meta', 'children']
    
    def get_meta(self, obj):
        """获取路由元信息"""
        return {
            'title': obj.title,
            'icon': obj.icon,
            'hidden': obj.is_hidden,
            'cache': obj.is_cache,
            'affix': obj.is_affix,
            'target': obj.target,
            'permission': obj.permission_code,
        }
    
    def get_children(self, obj):
        """获取子菜单"""
        request = self.context.get('request')
        user = request.user if request else None
        
        children = obj.get_children(user)
        if children.exists():
            return MenuTreeSerializer(children, many=True, context=self.context).data
        return []


class MenuCreateSerializer(serializers.ModelSerializer):
    """菜单创建序列化器"""
    
    class Meta:
        model = Menu
        fields = [
            'name', 'title', 'path', 'component', 'icon', 'menu_type',
            'parent', 'order_num', 'is_hidden', 'is_cache', 'is_affix', 'target',
            'redirect', 'permission_code', 'is_active'
        ]
    
    def validate_path(self, value):
        """验证路由路径"""
        if value and not value.startswith('/'):
            raise serializers.ValidationError('路由路径必须以 / 开头')
        return value
    
    def validate_parent(self, value):
        """验证父菜单"""
        if value:
            # 检查是否会形成循环引用
            current = value
            while current.parent:
                if current.parent == value:
                    raise serializers.ValidationError('不能选择自己或子菜单作为父菜单')
                current = current.parent
        return value


class MenuUpdateSerializer(serializers.ModelSerializer):
    """菜单更新序列化器"""
    
    class Meta:
        model = Menu
        fields = [
            'name', 'title', 'path', 'component', 'icon', 'menu_type',
            'parent', 'order_num', 'is_hidden', 'is_cache', 'is_affix', 'target',
            'redirect', 'permission_code', 'is_active'
        ]
    
    def validate_path(self, value):
        """验证路由路径"""
        if value and not value.startswith('/'):
            raise serializers.ValidationError('路由路径必须以 / 开头')
        return value
    
    def validate_parent(self, value):
        """验证父菜单"""
        if value and self.instance:
            # 检查是否会形成循环引用
            if value == self.instance:
                raise serializers.ValidationError('不能选择自己作为父菜单')
            
            # 检查是否选择了自己的子菜单作为父菜单
            def is_descendant(menu, target):
                for child in menu.children.all():
                    if child == target or is_descendant(child, target):
                        return True
                return False
            
            if is_descendant(self.instance, value):
                raise serializers.ValidationError('不能选择子菜单作为父菜单')
        
        return value


class UserMenuConfigSerializer(serializers.ModelSerializer):
    """用户菜单配置序列化器"""
    
    class Meta:
        model = UserMenuConfig
        fields = ['collapsed_menus', 'pinned_menus', 'custom_order', 'theme_config', 'updated_at']
        read_only_fields = ['updated_at']


class MenuSimpleSerializer(serializers.ModelSerializer):
    """菜单简单序列化器（用于下拉选择）"""
    label = serializers.CharField(source='title', read_only=True)
    value = serializers.IntegerField(source='id', read_only=True)
    level_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Menu
        fields = ['value', 'label', 'level_display']
    
    def get_level_display(self, obj):
        """获取层级显示"""
        prefix = '　' * obj.level + ('├─ ' if obj.level > 0 else '')
        return f"{prefix}{obj.title}"