from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Menu, UserMenuConfig
from .serializers import (
    MenuSerializer, MenuTreeSerializer, MenuCreateSerializer, 
    MenuUpdateSerializer, UserMenuConfigSerializer, MenuSimpleSerializer
)


class MenuViewSet(viewsets.ModelViewSet):
    """菜单管理视图集"""
    queryset = Menu.objects.all().order_by('order_num', 'id')
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """根据不同的action设置不同的权限"""
        if self.action == 'user_menus':
            # user_menus接口允许未登录用户访问
            return [AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MenuCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MenuUpdateSerializer
        return MenuSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 搜索功能
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(title__icontains=search) |
                Q(path__icontains=search)
            )
        
        # 菜单类型过滤
        menu_type = self.request.query_params.get('menu_type', '')
        if menu_type:
            queryset = queryset.filter(menu_type=menu_type)
        
        # 状态过滤
        is_active = self.request.query_params.get('is_active', '')
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """获取菜单列表"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # 是否返回树形结构
            tree = request.query_params.get('tree', 'false').lower() == 'true'
            if tree:
                # 只返回根菜单，子菜单通过递归获取
                root_menus = queryset.filter(parent=None)
                serializer = self.get_serializer(root_menus, many=True)
            else:
                serializer = self.get_serializer(queryset, many=True)
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取菜单列表失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """创建菜单"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                menu = serializer.save()
                return Response({
                    'code': 200,
                    'message': '菜单创建成功',
                    'data': MenuSerializer(menu).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'code': 400,
                    'message': '数据验证失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'创建菜单失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """更新菜单"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                menu = serializer.save()
                return Response({
                    'code': 200,
                    'message': '菜单更新成功',
                    'data': MenuSerializer(menu).data
                })
            else:
                return Response({
                    'code': 400,
                    'message': '数据验证失败',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'更新菜单失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """删除菜单"""
        try:
            instance = self.get_object()
            
            # 检查是否有子菜单
            if instance.children.exists():
                return Response({
                    'code': 400,
                    'message': '该菜单下还有子菜单，请先删除子菜单'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            instance.delete()
            return Response({
                'code': 200,
                'message': '菜单删除成功'
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除菜单失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def user_menus(self, request):
        """获取用户菜单（用于前端导航）"""
        try:
            user = request.user
            
            # 如果用户未登录，直接返回默认菜单
            if not user.is_authenticated:
                menu_data = self.get_default_menus(None)
                return Response({
                    'code': 200,
                    'message': 'success',
                    'data': {
                        'results': menu_data
                    }
                })
            
            # 获取用户可访问的根菜单
            root_menus = Menu.objects.filter(
                parent=None, 
                is_active=True,
                menu_type='menu'
            ).order_by('order_num')
            
            if not user.is_superuser:
                user_permissions = Menu.get_user_permissions(user)
                root_menus = root_menus.filter(
                    Q(permission_code='') | 
                    Q(permission_code__in=user_permissions)
                )
            
            # 构建菜单数据
            menu_data = []
            for menu in root_menus:
                menu_item = {
                    'key': menu.path or f'menu_{menu.id}',
                    'title': menu.title,
                    'icon': menu.icon or 'MenuOutlined',
                    'path': menu.path,
                    'children': []
                }
                
                # 获取子菜单
                children = menu.children.filter(is_active=True).order_by('order_num')
                if not user.is_superuser:
                    children = children.filter(
                        Q(permission_code='') | 
                        Q(permission_code__in=user_permissions)
                    )
                
                for child in children:
                    child_item = {
                        'key': child.path or f'menu_{child.id}',
                        'title': child.title,
                        'icon': child.icon or 'MenuOutlined',
                        'path': child.path
                    }
                    menu_item['children'].append(child_item)
                
                menu_data.append(menu_item)
            
            # 如果没有配置菜单，返回默认菜单
            if not menu_data:
                menu_data = self.get_default_menus(user)
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': {
                    'results': menu_data
                }
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取用户菜单失败: {str(e)}',
                'data': {'results': []}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_default_menus(self, user):
        """获取默认菜单配置"""
        is_admin = user and (user.is_superuser or getattr(user, 'is_admin', False)) if user else False
        
        default_menus = [
            {
                'key': '/',
                'title': '监控概览',
                'icon': 'DashboardOutlined',
                'path': '/'
            },
            {
                'key': '/assets',
                'title': '资产管理',
                'icon': 'DatabaseOutlined',
                'path': '',
                'children': [
                    {
                        'key': '/assets/hardware',
                        'title': '硬件设施',
                        'icon': 'DesktopOutlined',
                        'path': '/assets/hardware'
                    },
                    {
                        'key': '/assets/software',
                        'title': '软件资产',
                        'icon': 'AppstoreOutlined',
                        'path': '/assets/software'
                    }
                ]
            },
            {
                'key': '/servers',
                'title': '服务器监控',
                'icon': 'CloudServerOutlined',
                'path': '/servers'
            },
            {
                'key': '/network',
                'title': '网络设备',
                'icon': 'GlobalOutlined',
                'path': '/network'
            },
            {
                'key': '/ip-management',
                'title': 'IP管理',
                'icon': 'NodeIndexOutlined',
                'path': '/ip-management'
            },
            {
                'key': '/business',
                'title': '业务管理',
                'icon': 'ProjectOutlined',
                'path': '/business'
            }
        ]
        
        # 如果是管理员，添加管理员菜单
        if is_admin:
            admin_menu = {
                'key': '/admin',
                'title': '系统管理',
                'icon': 'SettingOutlined',
                'path': '',
                'children': [
                    {
                        'key': '/admin/dashboard',
                        'title': '管理控制台',
                        'icon': 'ControlOutlined',
                        'path': '/admin/dashboard'
                    },
                    {
                        'key': '/admin/users',
                        'title': '用户管理',
                        'icon': 'TeamOutlined',
                        'path': '/admin/users'
                    },
                    {
                        'key': '/admin/roles',
                        'title': '角色权限',
                        'icon': 'SafetyOutlined',
                        'path': '/admin/roles'
                    },
                    {
                        'key': '/admin/dictionary',
                        'title': '字典管理',
                        'icon': 'BookOutlined',
                        'path': '/admin/dictionary'
                    },
                    {
                        'key': '/admin/departments',
                        'title': '部门管理',
                        'icon': 'ApartmentOutlined',
                        'path': '/admin/departments'
                    },
                    {
                        'key': '/admin/positions',
                        'title': '职位管理',
                        'icon': 'IdcardOutlined',
                        'path': '/admin/positions'
                    },
                    {
                        'key': '/admin/employees',
                        'title': '员工管理',
                        'icon': 'UserOutlined',
                        'path': '/admin/employees'
                    },
                    {
                        'key': '/admin/logs',
                        'title': '操作日志',
                        'icon': 'FileTextOutlined',
                        'path': '/admin/logs'
                    },
                    {
                        'key': '/admin/settings',
                        'title': '系统设置',
                        'icon': 'ToolOutlined',
                        'path': '/admin/settings'
                    }
                ]
            }
            default_menus.append(admin_menu)
        
        return default_menus
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取菜单树（用于前端路由）"""
        try:
            user = request.user
            menu_type = request.query_params.get('type', 'menu')
            
            # 获取菜单树
            menu_tree = Menu.get_menu_tree(user=user, menu_type=menu_type)
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': menu_tree
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取菜单树失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def routes(self, request):
        """获取前端路由配置"""
        try:
            user = request.user
            
            # 获取用户可访问的菜单
            root_menus = Menu.objects.filter(
                parent=None, 
                is_active=True,
                menu_type='menu'
            ).order_by('order_num')
            
            if not user.is_superuser:
                user_permissions = Menu.get_user_permissions(user)
                root_menus = root_menus.filter(
                    Q(permission_code='') | 
                    Q(permission_code__in=user_permissions)
                )
            
            serializer = MenuTreeSerializer(root_menus, many=True, context={'request': request})
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取路由配置失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def options(self, request):
        """获取菜单选项（用于下拉选择）"""
        try:
            menus = Menu.objects.filter(is_active=True, menu_type='menu').order_by('order_num')
            
            # 构建层级选项
            def build_options(parent=None, level=0):
                options = []
                children = menus.filter(parent=parent)
                for menu in children:
                    menu.level = level  # 临时设置层级
                    options.append(menu)
                    options.extend(build_options(menu, level + 1))
                return options
            
            menu_list = build_options()
            serializer = MenuSimpleSerializer(menu_list, many=True)
            
            return Response({
                'code': 200,
                'message': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取菜单选项失败: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """切换菜单状态"""
        try:
            menu = self.get_object()
            menu.is_active = not menu.is_active
            menu.save()
            
            return Response({
                'code': 200,
                'message': f'菜单已{"启用" if menu.is_active else "禁用"}',
                'data': MenuSerializer(menu).data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'切换菜单状态失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_update_order(self, request):
        """批量更新菜单排序"""
        try:
            menu_orders = request.data.get('menu_orders', [])
            
            for item in menu_orders:
                menu_id = item.get('id')
                order_num = item.get('order_num')
                if menu_id and order_num is not None:
                    Menu.objects.filter(id=menu_id).update(order_num=order_num)
            
            return Response({
                'code': 200,
                'message': '菜单排序更新成功'
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'更新菜单排序失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserMenuConfigViewSet(viewsets.ModelViewSet):
    """用户菜单配置视图集"""
    serializer_class = UserMenuConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return UserMenuConfig.objects.filter(user=self.request.user)
    
    def get_object(self):
        """获取或创建用户菜单配置"""
        config, created = UserMenuConfig.objects.get_or_create(
            user=self.request.user,
            defaults={
                'collapsed_menus': [],
                'pinned_menus': [],
                'custom_order': {},
                'theme_config': {}
            }
        )
        return config
    
    @action(detail=False, methods=['get', 'put'])
    def my_config(self, request):
        """获取或更新当前用户的菜单配置"""
        try:
            config = self.get_object()
            
            if request.method == 'GET':
                serializer = self.get_serializer(config)
                return Response({
                    'code': 200,
                    'message': 'success',
                    'data': serializer.data
                })
            
            elif request.method == 'PUT':
                serializer = self.get_serializer(config, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'code': 200,
                        'message': '菜单配置更新成功',
                        'data': serializer.data
                    })
                else:
                    return Response({
                        'code': 400,
                        'message': '数据验证失败',
                        'errors': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'操作失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)