from django.contrib import admin
from .models import (
    Asset, ZabbixTemplate, NetworkDevice,
    HardwareAsset, Supplier, SpecificationUpdateRecord, WarrantyUpdateRecord
)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_type', 'manufacturer', 'model', 'created_at']
    list_filter = ['asset_type', 'category', 'status', 'created_at']
    search_fields = ['name', 'serial_number', 'description']
    ordering = ['-created_at']





@admin.register(ZabbixTemplate)
class ZabbixTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'templateid', 'category', 'items_count', 'triggers_count', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'templateid', 'description']
    ordering = ['name']


@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'device_type', 'ip_address', 'is_active']
    list_filter = ['device_type', 'is_active']
    search_fields = ['hostname', 'ip_address']
    ordering = ['hostname']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'phone', 'email']
    ordering = ['name']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'contact_person', 'phone', 'email')
        }),
        ('详细信息', {
            'fields': ('address', 'description', 'is_active')
        }),
    )


@admin.register(HardwareAsset)
class HardwareAssetAdmin(admin.ModelAdmin):
    list_display = [
        'asset_tag', 'model', 'manufacturer', 'asset_owner',
        'supplier', 'asset_status', 'warranty_status_display',
        'monitoring_status', 'created_at'
    ]
    list_filter = [
        'asset_status', 'warranty_type', 'monitoring_status',
        'manufacturer', 'supplier', 'created_at'
    ]
    search_fields = [
        'asset_tag', 'model', 'manufacturer', 'serial_number',
        'asset_owner', 'supplier__name'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'asset_tag', 'model', 'asset_owner', 'supplier',
                'supplier_contact', 'purchase_date', 'project_source', 'asset_status'
            )
        }),
        ('产品信息', {
            'fields': (
                'manufacturer', 'specifications', 'serial_number',
                'room', 'cabinet', 'u_position', 'dimensions'
            )
        }),
        ('保修信息', {
            'fields': (
                'warranty_type', 'warranty_start_date', 'warranty_end_date'
            )
        }),
        ('其他信息', {
            'fields': ('monitoring_status',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:  # 编辑时
            readonly_fields.extend(['created_at', 'updated_at'])
        return readonly_fields


class SpecificationUpdateRecordInline(admin.TabularInline):
    model = SpecificationUpdateRecord
    extra = 0
    readonly_fields = ('update_time',)
    
    def has_add_permission(self, request, obj=None):
        return False


class WarrantyUpdateRecordInline(admin.TabularInline):
    model = WarrantyUpdateRecord
    extra = 0
    readonly_fields = ('update_time',)
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SpecificationUpdateRecord)
class SpecificationUpdateRecordAdmin(admin.ModelAdmin):
    list_display = [
        'hardware_asset', 'update_method', 'update_time', 'updated_by'
    ]
    list_filter = ['update_method', 'update_time']
    search_fields = ['hardware_asset__asset_tag', 'updated_by']
    ordering = ['-update_time']
    readonly_fields = ('update_time',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(WarrantyUpdateRecord)
class WarrantyUpdateRecordAdmin(admin.ModelAdmin):
    list_display = [
        'hardware_asset', 'old_warranty_type', 'new_warranty_type',
        'update_time', 'updated_by'
    ]
    list_filter = ['old_warranty_type', 'new_warranty_type', 'update_time']
    search_fields = ['hardware_asset__asset_tag', 'updated_by']
    ordering = ['-update_time']
    readonly_fields = ('update_time',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
