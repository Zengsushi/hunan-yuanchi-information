from django.contrib import admin
from .models import Menu, UserMenuConfig


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'name', 'path', 'menu_type', 'parent', 'order_num', 'is_active', 'created_at']
    list_filter = ['menu_type', 'is_active', 'created_at']
    search_fields = ['name', 'title', 'path']
    ordering = ['order_num', 'id']
    list_editable = ['order_num', 'is_active']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'title', 'menu_type', 'parent')
        }),
        ('路由配置', {
            'fields': ('path', 'component', 'redirect', 'target')
        }),
        ('显示配置', {
            'fields': ('icon', 'order_num', 'is_hidden', 'is_cache', 'is_affix')
        }),
        ('权限配置', {
            'fields': ('permission_code', 'is_active')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(UserMenuConfig)
class UserMenuConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')