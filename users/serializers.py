from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile, Role, Permission, LoginLog, UserSession  # 使用自定义User模型


class BusinessUserSerializer(serializers.ModelSerializer):
    """业务管理模块专用的简化用户序列化器"""
    real_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    phone = serializers.CharField(source='phone', read_only=True)
    is_online = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'real_name', 'department', 
                 'role', 'phone', 'is_active', 'is_online', 'last_login']
        read_only_fields = ['id', 'username', 'email', 'last_login']
    
    def get_real_name(self, obj):
        """获取真实姓名"""
        if hasattr(obj, 'profile'):
            return obj.profile.real_name
        return ''
    
    def get_department(self, obj):
        """获取部门"""
        if hasattr(obj, 'profile'):
            return obj.profile.department
        return ''
    
    def get_role(self, obj):
        """获取角色"""
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return 'viewer'
    
    def get_is_online(self, obj):
        """获取在线状态"""
        active_sessions = obj.user_sessions.filter(is_active=True)
        return any(session.is_online for session in active_sessions)


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    profile = serializers.SerializerMethodField()
    is_online = serializers.SerializerMethodField()
    online_sessions = serializers.SerializerMethodField()
    
    # 添加profile字段以支持更新
    real_name = serializers.CharField(max_length=50, required=False, write_only=True)
    department = serializers.CharField(max_length=100, required=False, write_only=True)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=False, write_only=True)
    phone = serializers.CharField(max_length=11, required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'is_active', 'date_joined', 'last_login', 'profile', 
                 'is_online', 'online_sessions', 'real_name', 'department', 
                 'role', 'phone']
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return {
                'real_name': obj.profile.real_name,
                'department': obj.profile.department,
                'role': obj.profile.role,
                'phone': getattr(obj, 'phone', ''),
                'is_active': obj.profile.is_active,
                'login_count': obj.profile.login_count,
                'last_activity': obj.profile.last_activity
            }
        return None
    
    def get_is_online(self, obj):
        """获取用户在线状态"""
        active_sessions = obj.user_sessions.filter(is_active=True)
        return any(session.is_online for session in active_sessions)
    
    def get_online_sessions(self, obj):
        """获取用户在线会话信息"""
        active_sessions = obj.user_sessions.filter(is_active=True)
        online_sessions = [session for session in active_sessions if session.is_online]
        
        return [{
            'id': session.id,
            'ip_address': session.ip_address,
            'device_info': session.device_info,
            'login_time': session.login_time,
            'last_activity': session.last_activity
        } for session in online_sessions]
    
    def update(self, instance, validated_data):
        """更新用户信息，包括profile数据"""
        # 提取profile相关字段
        profile_data = {}
        for field in ['real_name', 'department', 'role']:
            if field in validated_data:
                profile_data[field] = validated_data.pop(field)
        
        phone = validated_data.pop('phone', None)
        
        # 更新用户基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if phone is not None:
            instance.phone = phone
        
        instance.save()
        
        # 更新或创建profile
        if profile_data:
            if hasattr(instance, 'profile'):
                # 更新已存在的profile
                for field, value in profile_data.items():
                    setattr(instance.profile, field, value)
                instance.profile.save()
            else:
                # 创建新的profile
                UserProfile.objects.create(user=instance, **profile_data)
        
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    real_name = serializers.CharField(max_length=50, required=False)
    department = serializers.CharField(max_length=100, required=False)
    role = serializers.ChoiceField(choices=UserProfile.ROLE_CHOICES, default='viewer')
    phone = serializers.CharField(max_length=11, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name',
                 'real_name', 'department', 'role', 'phone']
    
    def create(self, validated_data):
        # 提取用户资料字段
        profile_data = {
            'real_name': validated_data.pop('real_name', ''),
            'department': validated_data.pop('department', ''),
            'role': validated_data.pop('role', 'viewer'),
        }
        phone = validated_data.pop('phone', None)
        
        # 创建用户
        user = User.objects.create_user(**validated_data)
        if phone:
            user.phone = phone
            user.save()
        
        # 创建用户资料
        UserProfile.objects.create(user=user, **profile_data)
        
        return user


class UserStatsSerializer(serializers.Serializer):
    """用户统计序列化器"""
    total = serializers.IntegerField()
    active = serializers.IntegerField()
    newThisMonth = serializers.IntegerField()
    online = serializers.IntegerField()


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()
    remember = serializers.BooleanField(default=False)
    loginMode = serializers.CharField(default='user')
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('账户已被禁用')
                attrs['user'] = user
                return attrs
            else:
                # 当认证失败时，区分用户不存在和密码错误
                try:
                    existing_user = User.objects.get(username=username)
                    # 用户存在但密码错误
                    raise serializers.ValidationError('密码错误')
                except User.DoesNotExist:
                    # 用户不存在
                    raise serializers.ValidationError('用户不存在，请检查用户名是否正确')
        else:
            raise serializers.ValidationError('用户名和密码都是必填的')


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    oldPassword = serializers.CharField()
    newPassword = serializers.CharField(min_length=6)
    
    def validate_oldPassword(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    userCount = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 
                 'is_active', 'created_at', 'updated_at', 'userCount']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_userCount(self, obj):
        return UserProfile.objects.filter(role=obj.code).count()


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    children = serializers.SerializerMethodField()
    key = serializers.CharField(source='code')
    title = serializers.CharField(source='name')
    
    class Meta:
        model = Permission
        fields = ['id', 'key', 'title', 'name', 'code', 'description', 
                 'parent', 'icon', 'url', 'order', 'is_active', 'children']
    
    def get_children(self, obj):
        if obj.children.exists():
            return PermissionSerializer(obj.children.all(), many=True).data
        return []


class LoginLogSerializer(serializers.ModelSerializer):
    """登录日志序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = LoginLog
        fields = ['id', 'username', 'ip_address', 'user_agent', 
                 'login_time', 'logout_time', 'is_success', 'failure_reason']
        read_only_fields = ['id', 'login_time']


class UserSessionSerializer(serializers.ModelSerializer):
    """用户会话序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    is_online = serializers.ReadOnlyField()
    
    class Meta:
        model = UserSession
        fields = ['id', 'username', 'session_key', 'ip_address', 'user_agent',
                 'device_info', 'login_time', 'last_activity', 'is_active', 
                 'logout_reason', 'is_online']
        read_only_fields = ['id', 'login_time', 'last_activity', 'is_online']