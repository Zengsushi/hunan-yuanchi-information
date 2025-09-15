from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, UserProfile, Role, Permission, LoginLog, UserSession  # 使用自定义User模型
from .serializers import (
    UserSerializer, UserCreateSerializer, UserStatsSerializer,
    RoleSerializer, PermissionSerializer, LoginSerializer,
    ChangePasswordSerializer, LoginLogSerializer, UserSessionSerializer,
    BusinessUserSerializer
)
from .websocket_utils import kick_out_user_via_websocket  # 导入WebSocket工具


class UserPagination(PageNumberPagination):
    """用户分页类"""
    page_size = 10
    page_size_query_param = 'pageSize'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'list': data,
                'total': self.page.paginator.count,
                'current': self.page.number,
                'pageSize': self.page_size
            }
        })


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all().select_related('profile').order_by('-date_joined')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = UserPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 搜索功能
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(profile__real_name__icontains=search)
            )
        
        # 角色筛选
        role = self.request.query_params.get('role', '')
        if role:
            queryset = queryset.filter(profile__role=role)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """获取用户列表"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'list': serializer.data,
                'total': len(serializer.data)
            }
        })

    def create(self, request, *args, **kwargs):
        """创建新用户"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'code': 200,
                'message': '用户创建成功',
                'data': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'error': 提取错误信息(serializer.errors)
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """更新用户信息"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'code': 200,
                'message': '用户更新成功',
                'data': UserSerializer(user).data
            })
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'error': 提取错误信息(serializer.errors)
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """删除用户"""
        instance = self.get_object()
        instance.delete()
        return Response({
            'code': 200,
            'message': '用户删除成功'
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取用户统计信息"""
        total_users = User.objects.count()
        active_users = User.objects.filter(profile__is_active=True).count()
        
        # 本月新增用户
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_this_month = User.objects.filter(date_joined__gte=start_of_month).count()
        
        # 在线用户（使用UserSession的is_online方法）
        online_users = UserSession.get_online_users_count()
        
        # 清理过期会话
        UserSession.cleanup_expired_sessions()
        
        stats_data = {
            'total': total_users,
            'active': active_users,
            'newThisMonth': new_this_month,
            'online': online_users
        }
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': stats_data
        })

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        """切换用户状态"""
        user = self.get_object()
        active = request.data.get('active', True)
        
        # 检查是否尝试禁用管理员
        if not active:  # 如果是要禁用用户
            user_is_admin = user.is_superuser or (
                hasattr(user, 'profile') and user.profile.role == 'admin'
            )
            
            if user_is_admin:
                # 检查是否还有其他活跃的管理员
                other_active_admins = User.objects.filter(
                    Q(is_superuser=True) | Q(profile__role='admin'),
                    is_active=True
                ).exclude(id=user.id).count()
                
                if other_active_admins == 0:
                    return Response({
                        'code': 400,
                        'message': '操作失败',
                        'error': '不能禁用最后一个管理员账户，系统至少需要一个活跃的管理员'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(user, 'profile'):
            user.profile.is_active = active
            user.profile.save()
        
        user.is_active = active
        user.save()
        
        return Response({
            'code': 200,
            'message': f'用户已{"启用" if active else "禁用"}',
            'data': UserSerializer(user).data
        })

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """重置用户密码"""
        user = self.get_object()
        
        # 生成新密码
        new_password = '123456'  # 可以使用更复杂的密码生成逻辑
        user.set_password(new_password)
        user.save()
        
        return Response({
            'code': 200,
            'message': f'密码重置成功，新密码为: {new_password}',
            'data': {'new_password': new_password}
        })

    @action(detail=False, methods=['delete'])
    def batch(self, request):
        """批量删除用户"""
        user_ids = request.data.get('userIds', [])
        
        if not user_ids:
            return Response({
                'code': 400,
                'message': '请提供要删除的用户ID列表'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_count = User.objects.filter(id__in=user_ids).delete()[0]
        
        return Response({
            'code': 200,
            'message': f'成功删除 {deleted_count} 个用户'
        })

    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出用户列表"""
        # 这里可以实现CSV或Excel导出功能
        return Response({
            'code': 200,
            'message': '导出功能待实现'
        })

    @action(detail=False, methods=['post'])
    def import_users(self, request):
        """导入用户列表"""
        # 这里可以实现CSV或Excel导入功能
        return Response({
            'code': 200,
            'message': '导入功能待实现'
        })

    @action(detail=True, methods=['post'])
    def kick_out(self, request, pk=None):
        """踢出用户（管理员功能）"""
        user = self.get_object()
        
        # 检查当前用户是否为管理员
        current_user = request.user
        is_admin = current_user.is_superuser or (
            hasattr(current_user, 'profile') and current_user.profile.role == 'admin'
        )
        
        if not is_admin:
            return Response({
                'code': 403,
                'message': '权限不足',
                'error': '只有管理员才能踢出用户'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 不能踢出自己
        if user.id == current_user.id:
            return Response({
                'code': 400,
                'message': '操作失败',
                'error': '不能踢出自己'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 获取用户的所有活跃会话
            active_sessions = user.user_sessions.filter(is_active=True)
            kicked_sessions = active_sessions.count()
            
            # 标记所有会话为离线
            for session in active_sessions:
                session.mark_offline('kicked')
            
            # 删除用户的所有token（强制退出）
            deleted_tokens = Token.objects.filter(user=user).delete()[0]
            
            # 尝试WebSocket通知（如果可用）
            websocket_notified = False
            try:
                reason = request.data.get('reason', '管理员操作')
                result = kick_out_user_via_websocket(
                    user_id=user.id,
                    kicked_by_user=current_user,
                    reason=reason
                )
                websocket_notified = result.get('success', False)
                
                import logging
                logger = logging.getLogger(__name__)
                if websocket_notified:
                    logger.info(f"WebSocket通知成功: 踢出用户 {user.username}")
                else:
                    logger.warning(f"WebSocket通知失败: {result.get('error', 'Unknown error')}")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"WebSocket通知失败: {str(e)}")
            
            return Response({
                'code': 200,
                'message': f'成功踢出用户 {user.username}，关闭了 {kicked_sessions} 个会话，删除了 {deleted_tokens} 个token',
                'data': {
                    'username': user.username,
                    'kicked_sessions': kicked_sessions,
                    'deleted_tokens': deleted_tokens,
                    'websocket_notified': websocket_notified
                }
            })
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"踢出用户时发生错误: {str(e)}")
            return Response({
                'code': 500,
                'message': '踢出用户失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def online_sessions(self, request):
        """获取所有在线会话信息（管理员功能）"""
        # 检查权限
        current_user = request.user
        is_admin = current_user.is_superuser or (
            hasattr(current_user, 'profile') and current_user.profile.role == 'admin'
        )
        
        if not is_admin:
            return Response({
                'code': 403,
                'message': '权限不足',
                'error': '只有管理员才能查看在线会话'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 清理过期会话
        UserSession.cleanup_expired_sessions()
        
        # 获取所有在线会话
        active_sessions = UserSession.objects.filter(is_active=True).select_related('user')
        online_sessions = [session for session in active_sessions if session.is_online]
        
        serializer = UserSessionSerializer(online_sessions, many=True)
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'sessions': serializer.data,
                'total': len(online_sessions)
            }
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索用户"""
        try:
            queryset = self.get_queryset()
            
            # 应用分页
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'list': serializer.data,
                    'total': len(serializer.data)
                }
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'搜索用户失败: {str(e)}',
                'data': {'list': [], 'total': 0}
            })

    @action(detail=False, methods=['get'])
    def for_business(self, request):
        """获取用于业务管理的用户列表"""
        try:
            queryset = User.objects.filter(is_active=True).select_related('profile').order_by('username')
            
            # 搜索功能
            search = request.query_params.get('search', '')
            if search:
                queryset = queryset.filter(
                    Q(username__icontains=search) |
                    Q(profile__real_name__icontains=search)
                )
            
            serializer = BusinessUserSerializer(queryset, many=True)
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': serializer.data
            })
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取用户列表失败: {str(e)}',
                'data': []
            })


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    queryset = Role.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """获取角色权限"""
        role = self.get_object()
        return Response({
            'code': 200,
            'message': 'success',
            'data': role.permissions
        })

    @action(detail=True, methods=['put'])
    def permissions(self, request, pk=None):
        """更新角色权限"""
        role = self.get_object()
        permissions = request.data.get('permissions', [])
        
        role.permissions = permissions
        role.save()
        
        return Response({
            'code': 200,
            'message': '权限更新成功',
            'data': RoleSerializer(role).data
        })


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """权限管理视图集（只读）"""
    queryset = Permission.objects.filter(parent=None).order_by('name')
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取权限树结构"""
        permissions = self.get_queryset()
        serializer = self.get_serializer(permissions, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    def list(self, request, *args, **kwargs):
        """获取所有权限"""
        queryset = Permission.objects.all().order_by('name')
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })


# 认证相关API
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """用户登录API"""
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        remember = serializer.validated_data.get('remember', False)
        login_mode = request.data.get('loginMode', 'user')
        
        # 检查管理员权限
        is_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')
        user_role = getattr(user.profile, 'role', 'viewer') if hasattr(user, 'profile') else 'viewer'
        
        # 如果是管理员模式登录，但用户不是管理员，则阻止登录
        if login_mode == 'admin' and not is_admin:
            return Response({
                'code': 403,
                'message': '权限不足',
                'error': '您没有管理员权限，无法使用管理员模式登录。请使用普通用户模式登录。'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 获取或创建token
        token, created = Token.objects.get_or_create(user=user)
        
        # 获取请求信息
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 生成会话密钥
        session_key = request.session.session_key or token.key[:40]
        
        # 使用安全方法创建会话（自动处理重复和过期问题）
        device_info = extract_device_info(user_agent)
        try:
            user_session, cleanup_info = UserSession.safe_create_session(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                device_info=device_info
            )
            
            # 记录清理信息
            if cleanup_info.get('expired', 0) > 0:
                print(f'清理了 {cleanup_info["expired"]} 个过期会话')
            if cleanup_info.get('duplicates', 0) > 0:
                print(f'清理了 {cleanup_info["duplicates"]} 个重复会话')
                
        except Exception as e:
            print(f'创建会话失败: {str(e)}')
            # 如果仍然失败，尝试直接清理所有相关会话
            UserSession.objects.filter(
                Q(user=user) | Q(session_key=session_key)
            ).delete()
            
            # 重新创建
            user_session = UserSession.objects.create(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                device_info=device_info
            )
        
        # 记录登录日志
        LoginLog.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            is_success=True
        )
        
        # 更新用户资料
        if hasattr(user, 'profile'):
            profile = user.profile
            profile.login_count += 1
            profile.last_activity = timezone.now()
            profile.save()
        else:
            UserProfile.objects.create(user=user)
        
        # 更新用户最后登录信息
        user.last_login = timezone.now()
        user.save()
        
        return Response({
            'code': 200,
            'message': '登录成功',
            'data': {
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'real_name': getattr(user.profile, 'real_name', '') if hasattr(user, 'profile') else '',
                    'role': user_role,
                    'is_admin': is_admin,
                    'is_superuser': user.is_superuser,
                    'login_mode': login_mode
                }
            }
        })
    return Response({
        'code': 400,
        'message': '登录失败',
        'error': 提取错误信息(serializer.errors)
    }, status=status.HTTP_400_BAD_REQUEST)


def 提取错误信息(errors):
    """提取友好的错误信息"""
    if 'non_field_errors' in errors:
        return errors['non_field_errors'][0] if errors['non_field_errors'] else '登录失败'
    
    # 处理其他字段错误
    for field, field_errors in errors.items():
        if field_errors:
            return field_errors[0] if isinstance(field_errors, list) else str(field_errors)
    
    return '登录失败'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """用户登出API"""
    try:
        user = request.user
        
        # 清理用户会话
        current_token = request.auth.key if hasattr(request.auth, 'key') else None
        if current_token:
            # 标记当前会话为离线
            user_sessions = user.user_sessions.filter(
                session_key=current_token[:40],
                is_active=True
            )
            for session in user_sessions:
                session.mark_offline('normal')
        
        # 删除用户的token
        Token.objects.filter(user=user).delete()
        
        # 记录登出时间
        LoginLog.objects.filter(
            user=user,
            logout_time__isnull=True
        ).update(logout_time=timezone.now())
        
        return Response({
            'code': 200,
            'message': '登出成功'
        })
    except Exception as e:
        return Response({
            'code': 500,
            'message': f'登出失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    """获取当前用户信息API"""
    user = request.user
    serializer = UserSerializer(user)
    
    return Response({
        'code': 200,
        'message': 'success',
        'data': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token_api(request):
    """刷新Token API"""
    user = request.user
    
    # 删除旧token并创建新token
    Token.objects.filter(user=user).delete()
    new_token = Token.objects.create(user=user)
    
    return Response({
        'code': 200,
        'message': 'Token刷新成功',
        'data': {'token': new_token.key}
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password_api(request):
    """修改密码API"""
    serializer = ChangePasswordSerializer(
        data=request.data, 
        context={'user': request.user}
    )
    
    if serializer.is_valid():
        user = request.user
        new_password = serializer.validated_data['newPassword']
        
        user.set_password(new_password)
        user.save()
        
        # 删除所有token，强制重新登录
        Token.objects.filter(user=user).delete()
        
        return Response({
            'code': 200,
            'message': '密码修改成功，请重新登录'
        })
    
    return Response({
        'code': 400,
        'message': '密码修改失败',
        'error': 提取错误信息(serializer.errors)
    }, status=status.HTTP_400_BAD_REQUEST)


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def extract_device_info(user_agent):
    """从 User-Agent 提取设备信息"""
    if not user_agent:
        return '未知设备'
    
    user_agent = user_agent.lower()
    
    # 检测操作系统
    if 'windows' in user_agent:
        os_info = 'Windows'
    elif 'mac' in user_agent:
        os_info = 'macOS'
    elif 'linux' in user_agent:
        os_info = 'Linux'
    elif 'android' in user_agent:
        os_info = 'Android'
    elif 'iphone' in user_agent or 'ipad' in user_agent:
        os_info = 'iOS'
    else:
        os_info = '未知系统'
    
    # 检测浏览器
    if 'chrome' in user_agent:
        browser = 'Chrome'
    elif 'firefox' in user_agent:
        browser = 'Firefox'
    elif 'safari' in user_agent:
        browser = 'Safari'
    elif 'edge' in user_agent:
        browser = 'Edge'
    elif 'opera' in user_agent:
        browser = 'Opera'
    else:
        browser = '未知浏览器'
    
    return f'{os_info} - {browser}'
