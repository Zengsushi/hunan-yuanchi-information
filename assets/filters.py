import django_filters
from django.db.models import Q, F
from .models import HardwareAsset, Supplier
from .software_models import SoftwareAsset
from django.utils import timezone


class HardwareAssetFilter(django_filters.FilterSet):
    """硬件设施过滤器"""
    
    # 基本信息过滤
    asset_tag = django_filters.CharFilter(lookup_expr='icontains', label='资产标签')
    model = django_filters.CharFilter(lookup_expr='icontains', label='型号')
    asset_owner = django_filters.CharFilter(lookup_expr='icontains', label='资产责任人')
    supplier = django_filters.ModelChoiceFilter(
        queryset=Supplier.objects.filter(is_active=True),
        label='供应商'
    )
    supplier_name = django_filters.CharFilter(
        field_name='supplier__name',
        lookup_expr='icontains',
        label='供应商名称'
    )
    
    # 日期范围过滤
    purchase_date_start = django_filters.DateFilter(
        field_name='purchase_date',
        lookup_expr='gte',
        label='采购日期开始'
    )
    purchase_date_end = django_filters.DateFilter(
        field_name='purchase_date',
        lookup_expr='lte',
        label='采购日期结束'
    )
    
    # 产品信息过滤
    manufacturer = django_filters.CharFilter(lookup_expr='icontains', label='制造商')
    serial_number = django_filters.CharFilter(lookup_expr='icontains', label='序列号')
    
    # 位置过滤
    room = django_filters.CharFilter(lookup_expr='icontains', label='机房')
    cabinet = django_filters.CharFilter(lookup_expr='icontains', label='机柜')
    
    # 保修信息过滤
    warranty_type = django_filters.ChoiceFilter(
        choices=HardwareAsset.WARRANTY_TYPE_CHOICES,
        label='保修类型'
    )
    
    warranty_start_date_start = django_filters.DateFilter(
        field_name='warranty_start_date',
        lookup_expr='gte',
        label='保修开始日期开始'
    )
    warranty_start_date_end = django_filters.DateFilter(
        field_name='warranty_start_date',
        lookup_expr='lte',
        label='保修开始日期结束'
    )
    
    warranty_end_date_start = django_filters.DateFilter(
        field_name='warranty_end_date',
        lookup_expr='gte',
        label='保修结束日期开始'
    )
    warranty_end_date_end = django_filters.DateFilter(
        field_name='warranty_end_date',
        lookup_expr='lte',
        label='保修结束日期结束'
    )
    
    # 保修状态过滤（自定义方法）
    warranty_status = django_filters.ChoiceFilter(
        choices=HardwareAsset.WARRANTY_STATUS_CHOICES,
        method='filter_warranty_status',
        label='保修状态'
    )
    
    # 资产状态过滤
    asset_status = django_filters.MultipleChoiceFilter(
        choices=HardwareAsset.ASSET_STATUS_CHOICES,
        label='资产状态'
    )
    
    # 监控状态过滤
    monitoring_status = django_filters.BooleanFilter(label='监控状态')
    
    # 即将到期保修过滤（30天内到期）
    warranty_expiring_soon = django_filters.BooleanFilter(
        method='filter_warranty_expiring_soon',
        label='保修即将到期'
    )
    
    # 已过保修期过滤
    warranty_expired = django_filters.BooleanFilter(
        method='filter_warranty_expired',
        label='已过保修期'
    )
    
    # 综合搜索（搜索多个字段）
    search = django_filters.CharFilter(
        method='filter_search',
        label='综合搜索'
    )
    
    class Meta:
        model = HardwareAsset
        fields = [
            'asset_tag', 'model', 'asset_owner', 'supplier', 'supplier_name',
            'purchase_date_start', 'purchase_date_end',
            'manufacturer', 'serial_number',
            'room', 'cabinet',
            'warranty_type', 'warranty_start_date_start', 'warranty_start_date_end',
            'warranty_end_date_start', 'warranty_end_date_end', 'warranty_status',
            'asset_status', 'monitoring_status',
            'warranty_expiring_soon', 'warranty_expired', 'search'
        ]
    
    def filter_warranty_status(self, queryset, name, value):
        """过滤保修状态"""
        today = timezone.now().date()
        
        if value == 'original_warranty':
            return queryset.filter(
                warranty_type='original',
                warranty_end_date__gte=today
            )
        elif value == 'third_party_warranty':
            return queryset.filter(
                warranty_type='third_party',
                warranty_end_date__gte=today
            )
        elif value == 'out_of_warranty':
            return queryset.filter(warranty_end_date__lt=today)
        
        return queryset


class SoftwareAssetFilter(django_filters.FilterSet):
    """软件资产过滤器"""
    
    # 基本信息过滤
    software_name = django_filters.CharFilter(lookup_expr='icontains', label='软件名称')
    version = django_filters.CharFilter(lookup_expr='icontains', label='版本')
    vendor = django_filters.CharFilter(lookup_expr='icontains', label='厂商')
    asset_owner = django_filters.CharFilter(lookup_expr='icontains', label='资产责任人')
    
    # 供应商过滤
    supplier = django_filters.ModelChoiceFilter(
        queryset=Supplier.objects.filter(is_active=True),
        label='供应商'
    )
    supplier_name = django_filters.CharFilter(
        field_name='supplier__name',
        lookup_expr='icontains',
        label='供应商名称'
    )
    
    # 软件类型过滤
    software_type = django_filters.ChoiceFilter(
        choices=SoftwareAsset.SOFTWARE_TYPE_CHOICES,
        label='软件类型'
    )
    
    # 许可证类型过滤
    license_type = django_filters.ChoiceFilter(
        choices=SoftwareAsset.LICENSE_TYPE_CHOICES,
        label='许可证类型'
    )
    
    # 软件状态过滤
    software_status = django_filters.ChoiceFilter(
        choices=SoftwareAsset.ASSET_STATUS_CHOICES,
        label='软件状态'
    )
    
    # 许可证密钥过滤
    license_key = django_filters.CharFilter(lookup_expr='icontains', label='许可证密钥')
    
    # 日期范围过滤
    purchase_date_start = django_filters.DateFilter(
        field_name='purchase_date',
        lookup_expr='gte',
        label='采购日期开始'
    )
    purchase_date_end = django_filters.DateFilter(
        field_name='purchase_date',
        lookup_expr='lte',
        label='采购日期结束'
    )
    
    # 许可证日期范围过滤
    license_start_date_start = django_filters.DateFilter(
        field_name='license_start_date',
        lookup_expr='gte',
        label='许可证开始日期开始'
    )
    license_start_date_end = django_filters.DateFilter(
        field_name='license_start_date',
        lookup_expr='lte',
        label='许可证开始日期结束'
    )
    
    license_end_date_start = django_filters.DateFilter(
        field_name='license_end_date',
        lookup_expr='gte',
        label='许可证结束日期开始'
    )
    license_end_date_end = django_filters.DateFilter(
        field_name='license_end_date',
        lookup_expr='lte',
        label='许可证结束日期结束'
    )
    
    # 许可证数量范围过滤
    license_count_min = django_filters.NumberFilter(
        field_name='license_count',
        lookup_expr='gte',
        label='许可证数量最小值'
    )
    license_count_max = django_filters.NumberFilter(
        field_name='license_count',
        lookup_expr='lte',
        label='许可证数量最大值'
    )
    
    # 已使用许可证数量范围过滤
    used_license_count_min = django_filters.NumberFilter(
        field_name='used_license_count',
        lookup_expr='gte',
        label='已使用许可证数量最小值'
    )
    used_license_count_max = django_filters.NumberFilter(
        field_name='used_license_count',
        lookup_expr='lte',
        label='已使用许可证数量最大值'
    )
    
    # 项目来源过滤
    project_source = django_filters.CharFilter(lookup_expr='icontains', label='项目来源')
    
    # 描述过滤
    description = django_filters.CharFilter(lookup_expr='icontains', label='描述')
    
    # 许可证状态过滤（基于计算属性）
    license_status = django_filters.ChoiceFilter(
        choices=[
            ('valid', '有效'),
            ('expired', '已过期'),
            ('exhausted', '许可证用尽'),
            ('expiring_soon', '即将过期'),
        ],
        method='filter_license_status',
        label='许可证状态'
    )
    
    # 即将过期许可证过滤（30天内到期）
    license_expiring_soon = django_filters.BooleanFilter(
        method='filter_license_expiring_soon',
        label='许可证即将过期'
    )
    
    # 已过期许可证过滤
    license_expired = django_filters.BooleanFilter(
        method='filter_license_expired',
        label='许可证已过期'
    )
    
    # 许可证用尽过滤
    license_exhausted = django_filters.BooleanFilter(
        method='filter_license_exhausted',
        label='许可证用尽'
    )
    
    # 综合搜索（搜索多个字段）
    search = django_filters.CharFilter(
        method='filter_search',
        label='综合搜索'
    )
    
    class Meta:
        model = SoftwareAsset
        fields = [
            'software_name', 'version', 'vendor', 'asset_owner',
            'supplier', 'supplier_name',
            'software_type', 'license_type', 'software_status',
            'license_key',
            'purchase_date_start', 'purchase_date_end',
            'license_start_date_start', 'license_start_date_end',
            'license_end_date_start', 'license_end_date_end',
            'license_count_min', 'license_count_max',
            'used_license_count_min', 'used_license_count_max',
            'project_source', 'description',
            'license_status', 'license_expiring_soon', 'license_expired', 'license_exhausted',
            'search'
        ]
    
    def filter_license_status(self, queryset, name, value):
        """根据许可证状态过滤"""
        today = timezone.now().date()
        
        if value == 'valid':
            # 有效：未过期且有剩余许可证
            return queryset.filter(
                Q(license_end_date__isnull=True) | Q(license_end_date__gte=today)
            ).filter(
                Q(license_count__gt=0) & 
                (Q(used_license_count__lt=F('license_count')) | Q(used_license_count__isnull=True))
            )
        elif value == 'expired':
            # 过期
            return queryset.filter(license_end_date__lt=today)
        elif value == 'exhausted':
            # 许可证用尽
            return queryset.filter(
                used_license_count__gte=F('license_count'),
                license_count__gt=0
            )
        elif value == 'expiring_soon':
            # 即将过期（30天内）
            expiring_date = today + timezone.timedelta(days=30)
            return queryset.filter(
                license_end_date__gte=today,
                license_end_date__lte=expiring_date
            )
        
        return queryset
    
    def filter_license_expiring_soon(self, queryset, name, value):
        """过滤即将到期的许可证（30天内）"""
        if value:
            today = timezone.now().date()
            expiring_date = today + timezone.timedelta(days=30)
            return queryset.filter(
                license_end_date__gte=today,
                license_end_date__lte=expiring_date
            )
        return queryset
    
    def filter_license_expired(self, queryset, name, value):
        """过滤已过期的许可证"""
        if value:
            today = timezone.now().date()
            return queryset.filter(license_end_date__lt=today)
        return queryset
    
    def filter_license_exhausted(self, queryset, name, value):
        """过滤许可证用尽的软件"""
        if value:
            return queryset.filter(
                used_license_count__gte=F('license_count'),
                license_count__gt=0
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        """综合搜索过滤"""
        if value:
            return queryset.filter(
                Q(software_name__icontains=value) |
                Q(version__icontains=value) |
                Q(vendor__icontains=value) |
                Q(license_key__icontains=value) |
                Q(asset_owner__icontains=value) |
                Q(supplier__name__icontains=value) |
                Q(project_source__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset
    
    def filter_warranty_expiring_soon(self, queryset, name, value):
        """过滤即将到期的保修（30天内）"""
        if value:
            today = timezone.now().date()
            expiring_date = today + timezone.timedelta(days=30)
            return queryset.filter(
                warranty_end_date__gte=today,
                warranty_end_date__lte=expiring_date
            )
        return queryset
    
    def filter_warranty_expired(self, queryset, name, value):
        """过滤已过保修期的资产"""
        if value:
            today = timezone.now().date()
            return queryset.filter(warranty_end_date__lt=today)
        return queryset
    
    def filter_search(self, queryset, name, value):
        """综合搜索过滤"""
        if value:
            return queryset.filter(
                Q(asset_tag__icontains=value) |
                Q(model__icontains=value) |
                Q(manufacturer__icontains=value) |
                Q(serial_number__icontains=value) |
                Q(asset_owner__icontains=value) |
                Q(supplier__name__icontains=value) |
                Q(room__icontains=value) |
                Q(cabinet__icontains=value)
            )
        return queryset


class SupplierFilter(django_filters.FilterSet):
    """供应商过滤器"""
    
    name = django_filters.CharFilter(lookup_expr='icontains', label='供应商名称')
    contact_person = django_filters.CharFilter(lookup_expr='icontains', label='联系人')
    is_active = django_filters.BooleanFilter(label='是否启用')
    
    # 综合搜索
    search = django_filters.CharFilter(
        method='filter_search',
        label='综合搜索'
    )
    
    class Meta:
        model = Supplier
        fields = ['name', 'contact_person', 'is_active', 'search']
    
    def filter_search(self, queryset, name, value):
        """综合搜索过滤"""
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(contact_person__icontains=value) |
                Q(phone__icontains=value) |
                Q(email__icontains=value)
            )
        return queryset