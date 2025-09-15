from rest_framework import serializers
from .models import IPRecord, ScanTask, ScanResult


class IPRecordSerializer(serializers.ModelSerializer):
    """
    IP记录序列化器
    对自动发现的IP地址提供保护机制，防止编辑关键字段
    """
    
    class Meta:
        model = IPRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        """
        更新IP记录，对自动发现的IP地址进行保护
        """
        # 如果是自动发现的IP，限制可编辑的字段
        if instance.is_auto_discovered:
            # 定义自动发现IP允许编辑的字段
            allowed_fields = {
                'description',  # 允许修改备注
                'status',       # 允许修改状态（但有限制）
            }
            
            # 过滤掉不允许修改的字段
            protected_fields = set(validated_data.keys()) - allowed_fields
            
            if protected_fields:
                # 移除被保护的字段
                for field in protected_fields:
                    validated_data.pop(field, None)
                
                # 记录尝试修改的字段
                request = self.context.get('request')
                if request:
                    request._protected_fields_attempted = list(protected_fields)
        
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """
        序列化输出时添加保护状态信息
        """
        data = super().to_representation(instance)
        
        # 添加保护状态信息
        if instance.is_auto_discovered:
            data['is_protected'] = True
            data['protection_reason'] = 'Zabbix自动发现的IP地址'
            data['editable_fields'] = ['description', 'status']
        else:
            data['is_protected'] = False
            data['protection_reason'] = ''
            data['editable_fields'] = 'all'
        
        return data


class ScanTaskCreateSerializer(serializers.ModelSerializer):
    """扫描任务创建序列化器"""
    
    class Meta:
        model = ScanTask
        fields = [
            'task_name', 'ip_ranges', 'check_type', 'ports', 'key',
            'snmp_community', 'snmpv3_config', 'unique_check', 
            'host_source', 'name_source'
        ]


class ScanTaskSerializer(serializers.ModelSerializer):
    """扫描任务序列化器"""
    
    class Meta:
        model = ScanTask
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'started_at', 'completed_at']


class ScanResultSerializer(serializers.ModelSerializer):
    """扫描结果序列化器"""
    
    class Meta:
        model = ScanResult
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class IPStatisticsSerializer(serializers.Serializer):
    """IP统计信息序列化器"""
    
    total_count = serializers.IntegerField(help_text="总IP数量")
    active_count = serializers.IntegerField(help_text="在用IP数量")
    available_count = serializers.IntegerField(help_text="可用IP数量")
    reserved_count = serializers.IntegerField(help_text="预留IP数量")
    conflict_count = serializers.IntegerField(help_text="冲突IP数量")
    online_count = serializers.IntegerField(help_text="在线设备数量")
    offline_count = serializers.IntegerField(help_text="离线设备数量")
    static_count = serializers.IntegerField(help_text="静态IP数量")
    dynamic_count = serializers.IntegerField(help_text="动态IP数量")
    gateway_count = serializers.IntegerField(help_text="网关数量")
    dns_count = serializers.IntegerField(help_text="DNS服务器数量")


class ScanTaskStatusSerializer(serializers.Serializer):
    """扫描任务状态序列化器"""
    
    task_id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.IntegerField()
    message = serializers.CharField(required=False, allow_blank=True)
    error_message = serializers.CharField(required=False, allow_blank=True)
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    completed_at = serializers.DateTimeField(required=False, allow_null=True)
    results_count = serializers.IntegerField(required=False, default=0)