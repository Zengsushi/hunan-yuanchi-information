from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, Role, Permission


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = '用户资料'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_real_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')
    search_fields = ('username', 'email', 'profile__real_name')
    
    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return '-'
    get_role.short_description = '角色'
    
    def get_real_name(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.real_name
        return '-'
    get_real_name.short_description = '真实姓名'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'created_at')
    search_fields = ('name', 'code', 'description')
    list_filter = ('parent', 'created_at')
    raw_id_fields = ('parent',)


# 注册自定义User模型
admin.site.register(User, UserAdmin)
