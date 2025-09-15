from django.contrib import admin
from .models import Department, Position, Employee


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'level', 'manager', 'status', 'sort_order', 'created_at']
    list_filter = ['status', 'level', 'parent', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_editable = ['status', 'sort_order']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'parent', 'manager')
        }),
        ('详细信息', {
            'fields': ('description', 'level', 'sort_order', 'status')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent', 'manager')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'level', 'status', 'created_at']
    list_filter = ['status', 'level', 'department', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'code', 'department', 'level')
        }),
        ('详细信息', {
            'fields': ('description', 'responsibilities', 'requirements')
        }),
        ('薪资信息', {
            'fields': ('salary_range_min', 'salary_range_max')
        }),
        ('状态信息', {
            'fields': ('status',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'get_full_name', 'department', 'position', 
        'employment_status', 'hire_date', 'created_at'
    ]
    list_filter = [
        'employment_status', 'contract_type', 'department', 
        'position', 'hire_date', 'created_at'
    ]
    search_fields = [
        'employee_id', 'user__username', 'user__first_name', 
        'user__last_name', 'phone', 'mobile'
    ]
    list_editable = ['employment_status']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'employee_id', 'department', 'position', 'direct_supervisor')
        }),
        ('联系信息', {
            'fields': ('phone', 'mobile', 'office_location')
        }),
        ('工作信息', {
            'fields': (
                'hire_date', 'probation_end_date', 'contract_type', 'employment_status'
            )
        }),
        ('紧急联系人', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone'),
            'classes': ('collapse',)
        }),
        ('备注', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = '姓名'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'department', 'position', 'direct_supervisor__user'
        )