from rest_framework import serializers
from .models import Business, BusinessIP, BusinessMonthlyStats


class BusinessIPSerializer(serializers.ModelSerializer):
    """业务关联IP序列化器"""
    
    class Meta:
        model = BusinessIP
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'business')


class BusinessSerializer(serializers.ModelSerializer):
    """业务序列化器"""
    associated_ips = BusinessIPSerializer(many=True, read_only=True)
    associated_ips_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_associated_ips_count(self, obj):
        return obj.associated_ips.count()
    
    def validate_access_url(self, value):
        """验证访问地址"""
        if value is None or value == '':
            return None
        return value


class BusinessCreateSerializer(serializers.ModelSerializer):
    """业务创建序列化器"""
    
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def validate_access_url(self, value):
        """验证访问地址"""
        if value is None or value == '':
            return None
        return value


class BusinessMonthlyStatsSerializer(serializers.ModelSerializer):
    """业务月度统计序列化器"""
    business_name = serializers.CharField(source='business.name', read_only=True)
    
    class Meta:
        model = BusinessMonthlyStats
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BusinessMonthlyStatsCreateSerializer(serializers.ModelSerializer):
    """业务月度统计创建序列化器"""
    
    class Meta:
        model = BusinessMonthlyStats
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class BusinessDetailSerializer(serializers.ModelSerializer):
    """业务详情序列化器"""
    associated_ips = BusinessIPSerializer(many=True, read_only=True)
    monthly_stats = BusinessMonthlyStatsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Business
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')