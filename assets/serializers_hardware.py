from rest_framework import serializers
from .models import HardwareAsset, Supplier, SpecificationUpdateRecord, WarrantyUpdateRecord
from django.utils import timezone


class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""

    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SupplierSimpleSerializer(serializers.ModelSerializer):
    """供应商简单序列化器（用于下拉选择）"""

    class Meta:
        model = Supplier
        fields = ('id', 'name', 'contact_person')


class HardwareAssetSerializer(serializers.ModelSerializer):
    """硬件设施序列化器"""

    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_contact_person = serializers.CharField(source='supplier.contact_person', read_only=True)
    location = serializers.CharField(read_only=True)
    warranty_status = serializers.CharField(read_only=True)
    warranty_status_display = serializers.CharField(read_only=True)

    class Meta:
        model = HardwareAsset
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate_warranty_dates(self, attrs):
        """验证保修日期"""
        warranty_start = attrs.get('warranty_start_date')
        warranty_end = attrs.get('warranty_end_date')

        if warranty_start and warranty_end:
            if warranty_start >= warranty_end:
                raise serializers.ValidationError("保修结束日期必须晚于开始日期")

        return attrs

    def validate(self, attrs):
        attrs = self.validate_warranty_dates(attrs)
        return attrs


class HardwareAssetListSerializer(serializers.ModelSerializer):
    """硬件设施列表序列化器（用于列表展示）"""

    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    supplier_contact_person = serializers.CharField(source='supplier.contact_person', read_only=True)
    location = serializers.CharField(read_only=True)
    warranty_status_display = serializers.CharField(read_only=True)

    class Meta:
        model = HardwareAsset
        fields = (
            'id', 'asset_tag', 'model', 'manufacturer', 'serial_number',
            'asset_status', 'warranty_status_display', 'monitoring_status',
            'location', 'asset_owner', 'supplier_name', 'supplier_contact_person',
            'purchase_date', 'project_source', 'room', 'cabinet', 'u_position',
            'dimensions', 'warranty_type'
        )


class HardwareAssetCreateSerializer(serializers.ModelSerializer):
    """硬件设施创建序列化器"""

    warranty_type = serializers.ChoiceField(choices=HardwareAsset.WARRANTY_TYPE_CHOICES)
    asset_status = serializers.ChoiceField(choices=HardwareAsset.ASSET_STATUS_CHOICES, default='in_use')
    warranty_date_range = serializers.ListField(
        child=serializers.DateField(),
        write_only=True,
        required=True,
        min_length=2,
        max_length=2,
        help_text="保修日期范围，格式：[开始日期, 结束日期]"
    )

    class Meta:
        model = HardwareAsset
        exclude = ('created_at', 'updated_at', 'warranty_start_date', 'warranty_end_date')

    def validate_warranty_dates(self, attrs):
        """验证保修日期"""
        warranty_start = attrs.get('warranty_start_date')
        warranty_end = attrs.get('warranty_end_date')

        if warranty_start and warranty_end:
            if warranty_start >= warranty_end:
                raise serializers.ValidationError("保修结束日期必须晚于开始日期")

        return attrs
    
    def validate(self, attrs):
        # 处理warranty_date_range
        warranty_date_range = attrs.pop('warranty_date_range', None)
        if warranty_date_range:
            attrs['warranty_start_date'] = warranty_date_range[0]
            attrs['warranty_end_date'] = warranty_date_range[1]

        attrs = self.validate_warranty_dates(attrs)
        return attrs


class HardwareAssetUpdateSerializer(serializers.ModelSerializer):
    """硬件设施更新序列化器"""

    class Meta:
        model = HardwareAsset
        exclude = ('created_at', 'updated_at')

    def validate_warranty_dates(self, attrs):
        """验证保修日期"""
        warranty_start = attrs.get('warranty_start_date')
        warranty_end = attrs.get('warranty_end_date')

        if warranty_start and warranty_end:
            if warranty_start >= warranty_end:
                raise serializers.ValidationError("保修结束日期必须晚于开始日期")

        return attrs

    def validate(self, attrs):
        attrs = self.validate_warranty_dates(attrs)
        return attrs

    def update(self, instance, validated_data):
        """更新硬件设施，记录规格参数和保修信息变更"""
        # 记录规格参数变更
        old_specifications = instance.specifications
        new_specifications = validated_data.get('specifications', instance.specifications)

        if old_specifications != new_specifications:
            SpecificationUpdateRecord.objects.create(
                hardware_asset=instance,
                old_specifications=old_specifications,
                new_specifications=new_specifications,
                update_method='manual',
                updated_by=self.context.get('request').user.username if self.context.get('request') else None
            )

        # 记录保修信息变更
        warranty_fields = ['warranty_type', 'warranty_start_date', 'warranty_end_date']
        warranty_changed = any(
            validated_data.get(field) != getattr(instance, field)
            for field in warranty_fields
            if field in validated_data
        )

        if warranty_changed:
            WarrantyUpdateRecord.objects.create(
                hardware_asset=instance,
                old_warranty_type=instance.warranty_type,
                new_warranty_type=validated_data.get('warranty_type', instance.warranty_type),
                old_warranty_start_date=instance.warranty_start_date,
                new_warranty_start_date=validated_data.get('warranty_start_date', instance.warranty_start_date),
                old_warranty_end_date=instance.warranty_end_date,
                new_warranty_end_date=validated_data.get('warranty_end_date', instance.warranty_end_date),
                updated_by=self.context.get('request').user.username if self.context.get('request') else None
            )

        return super().update(instance, validated_data)


class SpecificationUpdateRecordSerializer(serializers.ModelSerializer):
    """规格参数更新记录序列化器"""

    hardware_asset_tag = serializers.CharField(source='hardware_asset.asset_tag', read_only=True)

    class Meta:
        model = SpecificationUpdateRecord
        fields = '__all__'
        read_only_fields = ('update_time',)


class WarrantyUpdateRecordSerializer(serializers.ModelSerializer):
    """保修更新记录序列化器"""

    hardware_asset_tag = serializers.CharField(source='hardware_asset.asset_tag', read_only=True)
    old_warranty_type_display = serializers.SerializerMethodField()
    new_warranty_type_display = serializers.SerializerMethodField()

    class Meta:
        model = WarrantyUpdateRecord
        fields = '__all__'
        read_only_fields = ('update_time',)

    def get_old_warranty_type_display(self, obj):
        """获取旧保修类型显示文本"""
        warranty_choices = dict(HardwareAsset.WARRANTY_TYPE_CHOICES)
        return warranty_choices.get(obj.old_warranty_type, obj.old_warranty_type)

    def get_new_warranty_type_display(self, obj):
        """获取新保修类型显示文本"""
        warranty_choices = dict(HardwareAsset.WARRANTY_TYPE_CHOICES)
        return warranty_choices.get(obj.new_warranty_type, obj.new_warranty_type)


class HardwareAssetImportSerializer(serializers.Serializer):
    """硬件设施导入序列化器"""

    asset_tag = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=200)
    asset_owner = serializers.CharField(max_length=100)
    supplier_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    supplier_contact = serializers.CharField(max_length=100, required=False, allow_blank=True)
    purchase_date = serializers.DateField()
    project_source = serializers.CharField(max_length=200, required=False, allow_blank=True)
    asset_status = serializers.ChoiceField(choices=HardwareAsset.ASSET_STATUS_CHOICES, default='in_use')
    manufacturer = serializers.CharField(max_length=200)
    serial_number = serializers.CharField(max_length=200)
    room = serializers.CharField(max_length=100, required=False, allow_blank=True)
    cabinet = serializers.CharField(max_length=100, required=False, allow_blank=True)
    u_position = serializers.CharField(max_length=20, required=False, allow_blank=True)
    dimensions = serializers.CharField(max_length=200, required=False, allow_blank=True)
    warranty_type = serializers.ChoiceField(choices=HardwareAsset.WARRANTY_TYPE_CHOICES)
    warranty_start_date = serializers.DateField()
    warranty_end_date = serializers.DateField()

    def validate(self, attrs):
        """验证导入数据"""
        # 验证资产标签唯一性
        asset_tag = attrs.get('asset_tag')
        if HardwareAsset.objects.filter(asset_tag=asset_tag).exists():
            raise serializers.ValidationError(f"资产标签 {asset_tag} 已存在")

        # 验证序列号唯一性
        serial_number = attrs.get('serial_number')
        if HardwareAsset.objects.filter(serial_number=serial_number).exists():
            raise serializers.ValidationError(f"序列号 {serial_number} 已存在")

        # 验证保修日期
        warranty_start = attrs.get('warranty_start_date')
        warranty_end = attrs.get('warranty_end_date')
        if warranty_start and warranty_end and warranty_start >= warranty_end:
            raise serializers.ValidationError("保修结束日期必须晚于开始日期")

        return attrs

    def create(self, validated_data):
        """创建硬件设施记录"""
        supplier_name = validated_data.pop('supplier_name', None)
        supplier = None

        if supplier_name:
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_name,
                defaults={'is_active': True}
            )

        validated_data['supplier'] = supplier
        return HardwareAsset.objects.create(**validated_data)
