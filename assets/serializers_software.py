from rest_framework import serializers
from .software_models import SoftwareAsset, SoftwareLicenseUpdateRecord, SoftwareVersionUpdateRecord, SoftwareDeployment
from .models import Supplier
from django.utils import timezone


class SoftwareAssetSerializer(serializers.ModelSerializer):
    """软件资产序列化器"""

    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_contact_person = serializers.CharField(source='supplier.contact_person', read_only=True)
    license_status = serializers.CharField(read_only=True)
    license_status_display = serializers.CharField(read_only=True)
    license_available = serializers.IntegerField(read_only=True)
    license_utilization_rate = serializers.FloatField(read_only=True)
    days_until_license_expiry = serializers.IntegerField(read_only=True)

    class Meta:
        model = SoftwareAsset
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_license_dates(self, attrs):
        """验证许可证日期"""
        license_start = attrs.get('license_start_date')
        license_end = attrs.get('license_end_date')

        if license_start and license_end:
            if license_start >= license_end:
                raise serializers.ValidationError("许可证结束日期必须晚于开始日期")

        return attrs

    def validate_license_count(self, attrs):
        """验证许可证数量"""
        license_count = attrs.get('license_count', 0)
        license_used = attrs.get('license_used', 0)

        if license_count < 0:
            raise serializers.ValidationError("许可证数量不能为负数")

        if license_used < 0:
            raise serializers.ValidationError("已使用许可证数量不能为负数")

        if license_used > license_count:
            raise serializers.ValidationError("已使用许可证数量不能超过总数量")

        return attrs

    def validate(self, attrs):
        attrs = self.validate_license_dates(attrs)
        attrs = self.validate_license_count(attrs)
        return attrs


class SoftwareAssetListSerializer(serializers.ModelSerializer):
    """软件资产列表序列化器（用于列表显示）"""

    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    license_status_display = serializers.CharField(read_only=True)
    license_utilization_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = SoftwareAsset
        fields = (
            'id', 'name', 'version', 'software_type', 'vendor',
            'license_type', 'license_count', 'license_used', 'license_utilization_rate',
            'license_status_display', 'asset_status', 'supplier_name',
            "asset_tag", "asset_owner", "supplier", "warranty_status"
        )


class SoftwareAssetCreateSerializer(serializers.ModelSerializer):
    """软件资产创建序列化器"""

    class Meta:
        model = SoftwareAsset
        exclude = ('created_at', 'updated_at')

    def validate_license_dates(self, attrs):
        """验证许可证日期"""
        license_start = attrs.get('license_start_date')
        license_end = attrs.get('license_end_date')

        if license_start and license_end:
            if license_start >= license_end:
                raise serializers.ValidationError("许可证结束日期必须晚于开始日期")

        return attrs

    def validate_license_count(self, attrs):
        """验证许可证数量"""
        license_count = attrs.get('license_count', 1)
        license_used = attrs.get('license_used', 0)

        if license_count < 0:
            raise serializers.ValidationError("许可证数量不能为负数")

        if license_used < 0:
            raise serializers.ValidationError("已使用许可证数量不能为负数")

        if license_used > license_count:
            raise serializers.ValidationError("已使用许可证数量不能超过总数量")

        return attrs

    def to_representation(self, instance):
        # 获取 request 对象
        request = self.context.get("request")
        if request:
            print("前端传入的数据：", request.data)

        # 调用原始的实现
        rep = super().to_representation(instance)

        # 你可以根据前端传的数据来动态修改返回内容
        if request and request.data.get("custom_display") == "short":
            rep.pop("some_large_field", None)

        return rep

    def validate(self, attrs):
        attrs = self.validate_license_dates(attrs)
        attrs = self.validate_license_count(attrs)
        attrs = self.to_representation(attrs)
        return attrs


class SoftwareAssetUpdateSerializer(serializers.ModelSerializer):
    """软件资产更新序列化器"""

    class Meta:
        model = SoftwareAsset
        exclude = ('created_at', 'updated_at')

    def validate_license_dates(self, attrs):
        """验证许可证日期"""
        license_start = attrs.get('license_start_date')
        license_end = attrs.get('license_end_date')

        if license_start and license_end:
            if license_start >= license_end:
                raise serializers.ValidationError("许可证结束日期必须晚于开始日期")

        return attrs

    def validate_license_count(self, attrs):
        """验证许可证数量"""
        license_count = attrs.get('license_count')
        license_used = attrs.get('license_used')

        # 如果没有提供新值，使用实例的当前值
        if license_count is None:
            license_count = self.instance.license_count
        if license_used is None:
            license_used = self.instance.license_used

        if license_count < 0:
            raise serializers.ValidationError("许可证数量不能为负数")

        if license_used < 0:
            raise serializers.ValidationError("已使用许可证数量不能为负数")

        if license_used > license_count:
            raise serializers.ValidationError("已使用许可证数量不能超过总数量")

        return attrs

    def validate(self, attrs):
        attrs = self.validate_license_dates(attrs)
        attrs = self.validate_license_count(attrs)
        return attrs


class SoftwareAssetImportSerializer(serializers.Serializer):
    """软件资产导入序列化器"""

    name = serializers.CharField(max_length=200)
    version = serializers.CharField(max_length=100)
    software_type = serializers.ChoiceField(choices=SoftwareAsset.SOFTWARE_TYPE_CHOICES)
    vendor = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)

    license_type = serializers.ChoiceField(choices=SoftwareAsset.LICENSE_TYPE_CHOICES)
    license_key = serializers.CharField(max_length=500, required=False, allow_blank=True)
    license_count = serializers.IntegerField(default=1)
    license_start_date = serializers.DateField(required=False, allow_null=True)
    license_end_date = serializers.DateField(required=False, allow_null=True)

    purchase_date = serializers.DateField(required=False, allow_null=True)
    purchase_price = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    supplier_name = serializers.CharField(max_length=200, required=False, allow_blank=True)

    status = serializers.ChoiceField(choices=SoftwareAsset.ASSET_STATUS_CHOICES, default='in_use')
    installation_path = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate(self, attrs):
        """验证导入数据"""
        # 验证许可证日期
        license_start = attrs.get('license_start_date')
        license_end = attrs.get('license_end_date')

        if license_start and license_end:
            if license_start >= license_end:
                raise serializers.ValidationError("许可证结束日期必须晚于开始日期")

        # 验证许可证数量
        license_count = attrs.get('license_count', 1)
        if license_count < 0:
            raise serializers.ValidationError("许可证数量不能为负数")

        return attrs

    def create(self, validated_data):
        """创建软件资产实例"""
        supplier_name = validated_data.pop('supplier_name', None)
        supplier = None

        if supplier_name:
            try:
                supplier = Supplier.objects.get(name=supplier_name)
            except Supplier.DoesNotExist:
                # 如果供应商不存在，创建新的供应商
                supplier = Supplier.objects.create(
                    name=supplier_name,
                    is_active=True
                )

        validated_data['supplier'] = supplier

        # 生成唯一的资产标签
        import uuid
        validated_data['asset_tag'] = f"SW-{uuid.uuid4().hex[:8].upper()}"

        return SoftwareAsset.objects.create(**validated_data)


class SoftwareLicenseUpdateRecordSerializer(serializers.ModelSerializer):
    """软件许可证更新记录序列化器"""

    software_asset_name = serializers.CharField(source='software_asset.software_name', read_only=True)

    class Meta:
        model = SoftwareLicenseUpdateRecord
        fields = '__all__'
        read_only_fields = ('update_time',)


class SoftwareVersionUpdateRecordSerializer(serializers.ModelSerializer):
    """软件版本更新记录序列化器"""

    software_asset_name = serializers.CharField(source='software_asset.software_name', read_only=True)

    class Meta:
        model = SoftwareVersionUpdateRecord
        fields = '__all__'
        read_only_fields = ('update_time',)


class SoftwareDeploymentSerializer(serializers.ModelSerializer):
    """软件部署记录序列化器"""

    software_asset_name = serializers.CharField(source='software_asset.software_name', read_only=True)

    class Meta:
        model = SoftwareDeployment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
