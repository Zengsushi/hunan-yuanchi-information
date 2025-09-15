from django.contrib import admin
from .models import Business, BusinessIP, BusinessMonthlyStats


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'responsible_person', 'status', 'online_date', 'created_at')
    list_filter = ('status', 'online_date', 'created_at')
    search_fields = ('name', 'responsible_person')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'responsible_person', 'status')
        }),
        ('业务详情', {
            'fields': ('online_date', 'access_url', 'description')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(BusinessIP)
class BusinessIPAdmin(admin.ModelAdmin):
    list_display = ('business', 'ip_address', 'hostname', 'service_type', 'status', 'created_at')
    list_filter = ('service_type', 'status', 'created_at')
    search_fields = ('business__name', 'ip_address', 'hostname')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('关联信息', {
            'fields': ('business',)
        }),
        ('IP信息', {
            'fields': ('ip_address', 'hostname', 'port', 'service_type', 'status')
        }),
        ('其他信息', {
            'fields': ('description',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(BusinessMonthlyStats)
class BusinessMonthlyStatsAdmin(admin.ModelAdmin):
    list_display = ('business', 'year', 'month', 'total_visits', 'unique_visitors', 'uptime_percentage', 'created_at')
    list_filter = ('year', 'month', 'created_at')
    search_fields = ('business__name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('business', 'year', 'month')
        }),
        ('访问统计', {
            'fields': ('total_visits', 'unique_visitors', 'data_transfer_gb')
        }),
        ('性能统计', {
            'fields': ('avg_response_time', 'uptime_percentage', 'error_count')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('business')