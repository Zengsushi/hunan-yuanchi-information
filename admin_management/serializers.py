from rest_framework import serializers
from .models import Dictionary, SystemConfig, AdminLog, DashboardWidget


class DictionarySerializer(serializers.ModelSerializer):
    """字典序列化器"""
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    config_dict = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = ['id', 'category', 'category_label', 'key', 'label', 'description', 
                 'priority', 'status', 'status_label', 'config', 'config_dict', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_config_dict(self, obj):
        """获取配置信息的字典格式"""
        return obj.config_dict
    
    def validate(self, attrs):
        """验证数据"""
        category = attrs.get('category')
        key = attrs.get('key')
        
        # 检查唯一性（更新时排除当前实例）
        queryset = Dictionary.objects.filter(category=category, key=key)
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)
        
        if queryset.exists():
            raise serializers.ValidationError({
                'key': f'在分类"{dict(Dictionary.CATEGORY_CHOICES).get(category, category)}"中，键"{key}"已存在'
            })
        
        return attrs


class DictionaryListSerializer(serializers.ModelSerializer):
    """字典列表序列化器（简化版）"""
    config_dict = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = ['id', 'key', 'label', 'description', 'priority', 'config_dict']
    
    def get_config_dict(self, obj):
        """获取配置信息的字典格式"""
        return obj.config_dict


class DictionaryCategorySerializer(serializers.Serializer):
    """字典分类序列化器"""
    key = serializers.CharField()
    label = serializers.CharField()
    description = serializers.CharField()
    count = serializers.IntegerField(default=0)


class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    config_type_label = serializers.CharField(source='get_config_type_display', read_only=True)
    value_dict = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemConfig
        fields = ['id', 'name', 'key', 'value', 'value_dict', 'config_type', 
                 'config_type_label', 'description', 'is_encrypted', 'is_active', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_value_dict(self, obj):
        """获取值的字典格式（如果是JSON）"""
        return obj.value_dict


class AdminLogSerializer(serializers.ModelSerializer):
    """管理日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    action_label = serializers.CharField(source='get_action_display', read_only=True)
    result_label = serializers.CharField(source='get_result_display', read_only=True)
    
    class Meta:
        model = AdminLog
        fields = ['id', 'username', 'action', 'action_label', 'model_name', 
                 'object_id', 'description', 'ip_address', 'user_agent', 
                 'result', 'result_label', 'error_message', 'created_at']
        read_only_fields = ['id', 'created_at']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """仪表盘组件序列化器"""
    widget_type_label = serializers.CharField(source='get_widget_type_display', read_only=True)
    config_dict = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardWidget
        fields = ['id', 'name', 'title', 'widget_type', 'widget_type_label', 
                 'config', 'config_dict', 'position_x', 'position_y', 
                 'width', 'height', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_config_dict(self, obj):
        """获取配置信息的字典格式"""
        return obj.config_dict


class DashboardStatsSerializer(serializers.Serializer):
    """仪表盘统计序列化器"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    online_users = serializers.IntegerField()
    total_assets = serializers.IntegerField()
    active_assets = serializers.IntegerField()
    total_ips = serializers.IntegerField()
    used_ips = serializers.IntegerField()
    system_health = serializers.CharField()
    recent_activities = serializers.ListField()