from django.shortcuts import render
from django.db.models import Q, Count
from django.utils import timezone
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

from .models import Dictionary, SystemConfig, AdminLog, DashboardWidget
from .serializers import (
    DictionarySerializer, DictionaryListSerializer, DictionaryCategorySerializer,
    SystemConfigSerializer, AdminLogSerializer, DashboardWidgetSerializer,
    DashboardStatsSerializer
)

# 导入其他应用的模型用于统计
from users.models import User, UserSession
try:
    from assets.models import Asset
except ImportError:
    Asset = None
try:
    from ip_management.models import IPAddress
except ImportError:
    IPAddress = None


class AdminPagination(PageNumberPagination):
    """管理后台分页类"""
    page_size = 20
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


class DictionaryViewSet(viewsets.ModelViewSet):
    """字典管理视图集"""
    
    queryset = Dictionary.objects.all().order_by('-priority', 'key')
    serializer_class = DictionarySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AdminPagination
    
    def get_queryset(self):
        """获取查询集，支持筛选"""
        queryset = super().get_queryset()
        
        # 分类筛选
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # 状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 关键词搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(key__icontains=search) |
                Q(label__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """获取字典列表"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 检查是否只需要简化的数据格式
        simple = request.query_params.get('simple', 'false').lower() == 'true'
        if simple:
            serializer = DictionaryListSerializer(queryset, many=True)
            print(serializer.data)
            return Response({
                'code': 200,
                'message': 'success',
                'data': serializer.data
            })
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """创建字典项"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            dictionary = serializer.save()
            
            # 记录操作日志
            self._log_action(request, 'create', dictionary, f'创建字典项: {dictionary.label}')
            
            return Response({
                'code': 200,
                'message': '字典项创建成功',
                'data': DictionarySerializer(dictionary).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """更新字典项"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            dictionary = serializer.save()
            
            # 记录操作日志
            self._log_action(request, 'update', dictionary, f'更新字典项: {dictionary.label}')
            
            return Response({
                'code': 200,
                'message': '字典项更新成功',
                'data': DictionarySerializer(dictionary).data
            })
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    #创建字典分类
    @action(detail=False, methods=['post'], url_path='categories')
    def create_category(self, request):
        """创建字典分类"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response({
                'code': 200,
                'message': '字典分类创建成功',
                'data': CategorySerializer(category).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)




    @action(detail=False, methods=['delete'], url_path='categories/(?P<category>[^/.]+)')
    def delete_category(self, request, category=None):
        """删除指定分类下的所有字典项"""
        if not category:
            return Response({
                'code': 400,
                'message': '请指定要删除的字典分类',
                'error': 'category参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 检查分类是否有效，如果无效则返回空数据
        valid_categories = [choice[0] for choice in Dictionary.CATEGORY_CHOICES]
        if category not in valid_categories:
            return Response({
                'code': 200,
                'message': 'success',
                'data': [],
                'meta': {
                    'category': category,
                    'category_label': category,
                    'total': 0,
                    'status_filter': 'active'
                }
            })

        try:
            # 获取该分类下的所有字典项
            items = Dictionary.objects.filter(category=category)
            count = items.count()
            
            if count == 0:
                return Response({
                    'code': 404,
                    'message': f'分类 {category} 下没有字典项',
                }, status=status.HTTP_404_NOT_FOUND)

            # 记录删除操作
            self._log_action(request, 'delete', None, f'删除分类 {category} 下的所有字典项({count}个)')
            
            # 执行删除
            items.delete()
            

            return Response({
                'code': 200,
                'message': f'成功删除分类 {category} 下的 {count} 个字典项',
                'data': {
                    'category': category,
                    'deleted_count': count
                }
            })

        except Exception as e:
            return Response({
                'code': 500,
                'message': f'删除分类 {category} 时发生错误',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def destroy(self, request, *args, **kwargs):
        """删除字典项"""
        instance = self.get_object()
        label = instance.label
        
        # 记录操作日志
        self._log_action(request, 'delete', instance, f'删除字典项: {label}')
        
        instance.delete()
        return Response({
            'code': 200,
            'message': '字典项删除成功'
        })
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有字典分类"""
        categories = Dictionary.get_categories()
        
        # 添加每个分类的统计信息
        for category in categories:
            count = Dictionary.objects.filter(category=category['key']).count()
            category['count'] = count
        
        serializer = DictionaryCategorySerializer(categories, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='categories')
    def create_category(self, request):
        """创建字典分类"""
        category_key = request.data.get('key')
        category_label = request.data.get('label')
        description = request.data.get('description', '')
        
        if not category_key or not category_label:
            return Response({
                'code': 400,
                'message': '分类键名和标签不能为空',
                'error': 'key和label参数是必需的'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查分类是否已存在
        valid_categories = [choice[0] for choice in Dictionary.CATEGORY_CHOICES]
        if category_key in valid_categories:
            return Response({
                'code': 400,
                'message': f'分类 {category_key} 已存在',
                'error': '分类键名重复'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 记录操作日志
            self._log_action(request, 'create', None, f'尝试创建新分类: {category_key} - {category_label}')
            
            # 创建分类数据
            category_data = {
                'key': category_key,
                'label': category_label,
                'description': description,
                'count': 0
            }
            
            # 使用DictionaryCategorySerializer验证数据
            from .serializers import DictionaryCategorySerializer
            serializer = DictionaryCategorySerializer(data=category_data)
            
            if serializer.is_valid():
                return Response({
                    'code': 200,
                    'message': '字典分类创建成功',
                    'data': serializer.validated_data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'code': 400,
                    'message': '数据验证失败',
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'code': 500,
                'message': '创建分类时发生错误',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='by-category/(?P<category>[^/.]+)')
    def by_category(self, request, category=None):
        """根据分类获取字典数据"""
        if not category:
            return Response({
                'code': 400,
                'message': '请指定字典分类',
                'error': 'category参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查分类是否有效，如果无效则返回空数据
        valid_categories = [choice[0] for choice in Dictionary.CATEGORY_CHOICES]
        if category not in valid_categories:
            return Response({
                'code': 200,
                'message': 'success',
                'data': [],
                'meta': {
                    'category': category,
                    'category_label': category,
                    'total': 0,
                    'status_filter': request.query_params.get('status', 'active')
                }
            })
        
        # 获取指定分类的字典数据
        status_filter = request.query_params.get('status', 'active')
        dictionaries = Dictionary.get_by_category(category, status_filter)
        
        # 检查是否需要简化的数据格式
        simple = request.query_params.get('simple', 'false').lower() == 'true'
        if simple:
            serializer = DictionaryListSerializer(dictionaries, many=True)
        else:
            serializer = DictionarySerializer(dictionaries, many=True)
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data,
            'meta': {
                'category': category,
                'category_label': dict(Dictionary.CATEGORY_CHOICES).get(category, category),
                'total': dictionaries.count(),
                'status_filter': status_filter
            }
        })
    
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """批量创建或更新字典项"""
        logger.info(f"批量创建字典项，数据: {request.data}")
        if not isinstance(request.data, list):
            return Response({
                'code': 400,
                'message': '请提供字典项数组',
                'error': '数据格式错误，应该是数组格式'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        created_items = []
        updated_items = []
        errors = []
        
        for index, item_data in enumerate(request.data):
            try:
                # 使用get_or_create逻辑处理重复数据
                category = item_data.get('category')
                key = item_data.get('key')
                
                if not category or not key:
                    errors.append({
                        'index': index,
                        'data': item_data,
                        'errors': {'category': ['分类不能为空'], 'key': ['键名不能为空']}
                    })
                    continue
                
                # 尝试获取现有记录
                existing_dict = Dictionary.objects.filter(
                    category=category,
                    key=key
                ).first()
                
                if existing_dict:
                    # 更新现有记录
                    serializer = DictionarySerializer(existing_dict, data=item_data, partial=True)
                    if serializer.is_valid():
                        dictionary = serializer.save()
                        updated_items.append(DictionarySerializer(dictionary).data)
                        logger.info(f"更新字典项: {category} - {key}")
                    else:
                        errors.append({
                            'index': index,
                            'data': item_data,
                            'errors': serializer.errors
                        })
                else:
                    # 创建新记录
                    serializer = DictionarySerializer(data=item_data)
                    if serializer.is_valid():
                        dictionary = serializer.save()
                        created_items.append(DictionarySerializer(dictionary).data)
                        logger.info(f"创建字典项: {category} - {key}")
                    else:
                        errors.append({
                            'index': index,
                            'data': item_data,
                            'errors': serializer.errors
                        })
                        
            except Exception as e:
                logger.error(f"处理字典项时出错: {str(e)}")
                errors.append({
                    'index': index,
                    'data': item_data,
                    'errors': {'general': [str(e)]}
                })
        
        # 记录批量操作日志
        total_success = len(created_items) + len(updated_items)
        self._log_action(request, 'create', None, f'批量处理字典项: 创建{len(created_items)}个，更新{len(updated_items)}个，失败{len(errors)}个')
        
        # 如果没有任何成功的操作，返回错误
        if total_success == 0 and errors:
            return Response({
                'code': 400,
                'message': f'批量处理失败，{len(errors)}个项目处理失败',
                'data': {
                    'created': created_items,
                    'updated': updated_items,
                    'errors': errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果有成功的操作，总是返回成功响应
        success_message = []
        if len(created_items) > 0:
            success_message.append(f'创建{len(created_items)}个')
        if len(updated_items) > 0:
            success_message.append(f'更新{len(updated_items)}个')
        if len(errors) > 0:
            success_message.append(f'失败{len(errors)}个')
            
        message = f'批量处理完成，' + '，'.join(success_message) + '字典项'
        
        return Response({
            'code': 200,
            'message': message,
            'data': {
                'created': created_items,
                'updated': updated_items,
                'errors': errors,
                'total_processed': len(request.data),
                'total_success': total_success
            }
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='init-data')
    def init_data(self, request):
        """初始化字典数据"""
        logger.info("init_data action called")
        print(f"init_data action called, method: {request.method}")
        print(f"user: {request.user}")
        print(f"is_authenticated: {request.user.is_authenticated}")
        
        try:
            # 定义初始字典数据
            dictionary_data = [
                # 用户分类
                {
                    'category': 'user_category',
                    'key': 'admin',
                    'label': '管理员',
                    'description': '系统管理员用户',
                    'priority': 100,
                    'status': 'active'
                },
                {
                    'category': 'user_category',
                    'key': 'operator',
                    'label': '操作员',
                    'description': '系统操作员用户',
                    'priority': 80,
                    'status': 'active'
                },
                {
                    'category': 'user_category',
                    'key': 'viewer',
                    'label': '查看者',
                    'description': '只读权限用户',
                    'priority': 60,
                    'status': 'active'
                },
                
                # 系统配置
                {
                    'category': 'system_config',
                    'key': 'session_timeout',
                    'label': '会话超时时间',
                    'description': '用户会话的超时时间设置',
                    'priority': 90,
                    'status': 'active',
                    'config': '{"unit": "minutes", "default": 30, "min": 5, "max": 480}'
                },
                {
                    'category': 'system_config',
                    'key': 'password_policy',
                    'label': '密码策略',
                    'description': '用户密码复杂度要求',
                    'priority': 80,
                    'status': 'active',
                    'config': '{"min_length": 8, "require_uppercase": true, "require_lowercase": true, "require_numbers": true}'
                },
                
                # 资产类型
                {
                    'category': 'asset_type',
                    'key': 'server',
                    'label': '服务器',
                    'description': '物理服务器或虚拟机',
                    'priority': 100,
                    'status': 'active'
                },
                {
                    'category': 'asset_type',
                    'key': 'network_device',
                    'label': '网络设备',
                    'description': '交换机、路由器等网络设备',
                    'priority': 90,
                    'status': 'active'
                },
                {
                    'category': 'asset_type',
                    'key': 'storage',
                    'label': '存储设备',
                    'description': '磁盘阵列、存储柜等',
                    'priority': 80,
                    'status': 'active'
                },
                
                # 部门
                {
                    'category': 'department',
                    'key': 'it',
                    'label': 'IT部门',
                    'description': '信息技术部门',
                    'priority': 100,
                    'status': 'active'
                },
                {
                    'category': 'department',
                    'key': 'ops',
                    'label': '运维部门',
                    'description': '系统运维部门',
                    'priority': 90,
                    'status': 'active'
                },
                {
                    'category': 'department',
                    'key': 'dev',
                    'label': '开发部门',
                    'description': '软件开发部门',
                    'priority': 80,
                    'status': 'active'
                },
                
                # 状态
                {
                    'category': 'status',
                    'key': 'active',
                    'label': '活跃',
                    'description': '正常活跃状态',
                    'priority': 100,
                    'status': 'active',
                    'config': '{"color": "green", "icon": "check-circle"}'
                },
                {
                    'category': 'status',
                    'key': 'inactive',
                    'label': '非活跃',
                    'description': '暂时停用状态',
                    'priority': 80,
                    'status': 'active',
                    'config': '{"color": "orange", "icon": "pause-circle"}'
                },
                {
                    'category': 'status',
                    'key': 'disabled',
                    'label': '禁用',
                    'description': '完全禁用状态',
                    'priority': 60,
                    'status': 'active',
                    'config': '{"color": "red", "icon": "stop-circle"}'
                }
            ]
            
            created_count = 0
            updated_count = 0
            
            for data in dictionary_data:
                dictionary, created = Dictionary.objects.get_or_create(
                    category=data['category'],
                    key=data['key'],
                    defaults=data
                )
                
                if created:
                    created_count += 1
                else:
                    # 更新现有记录
                    for field, value in data.items():
                        if field not in ['category', 'key']:
                            setattr(dictionary, field, value)
                    dictionary.save()
                    updated_count += 1
            
            # 记录操作日志
            self._log_action(request, 'create', None, f'初始化字典数据: 创建{created_count}个，更新{updated_count}个')
            
            # 统计每个分类的数量
            category_stats = {}
            for category_key, category_label in Dictionary.CATEGORY_CHOICES:
                count = Dictionary.objects.filter(category=category_key).count()
                category_stats[category_key] = {
                    'label': category_label,
                    'count': count
                }
            
            return Response({
                'code': 200,
                'message': '字典数据初始化成功',
                'data': {
                    'created_count': created_count,
                    'updated_count': updated_count,
                    'total_count': created_count + updated_count,
                    'category_stats': category_stats
                }
            })
            
        except Exception as e:
            # 记录错误日志
            self._log_action(request, 'create', None, f'初始化字典数据失败: {str(e)}')
            
            return Response({
                'code': 500,
                'message': '初始化字典数据失败',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _log_action(self, request, action, instance, description):
        """记录操作日志"""
        try:
            AdminLog.objects.create(
                user=request.user,
                action=action,
                model_name='Dictionary',
                object_id=str(instance.id) if instance else '',
                description=description,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                result='success'
            )
        except Exception as e:
            pass  # 日志记录失败不影响主要操作
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SystemConfigViewSet(viewsets.ModelViewSet):
    """系统配置管理视图集"""
    
    queryset = SystemConfig.objects.all().order_by('config_type', 'name')
    serializer_class = SystemConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AdminPagination
    
    def get_queryset(self):
        """获取查询集，支持筛选"""
        queryset = super().get_queryset()
        
        # 配置类型筛选
        config_type = self.request.query_params.get('config_type')
        if config_type:
            queryset = queryset.filter(config_type=config_type)
        
        # 状态筛选
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # 关键词搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(key__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """创建系统配置"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            config = serializer.save()
            
            # 记录操作日志
            self._log_action(request, 'create', config, f'创建系统配置: {config.name}')
            
            return Response({
                'code': 200,
                'message': '系统配置创建成功',
                'data': SystemConfigSerializer(config).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'code': 400,
            'message': '数据验证失败',
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _log_action(self, request, action, instance, description):
        """记录操作日志"""
        try:
            AdminLog.objects.create(
                user=request.user,
                action=action,
                model_name='SystemConfig',
                object_id=str(instance.id) if instance else '',
                description=description,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                result='success'
            )
        except Exception as e:
            pass
    
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AdminLogViewSet(viewsets.ReadOnlyModelViewSet):
    """管理日志视图集（只读）"""
    
    queryset = AdminLog.objects.all().select_related('user').order_by('-created_at')
    serializer_class = AdminLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AdminPagination
    
    def get_queryset(self):
        """获取查询集，支持筛选"""
        queryset = super().get_queryset()
        
        # 用户筛选
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # 操作类型筛选
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # 模型名称筛选
        model_name = self.request.query_params.get('model_name')
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        # 时间范围筛选
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """仪表盘组件管理视图集"""
    
    queryset = DashboardWidget.objects.all().order_by('position_y', 'position_x')
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """获取仪表盘统计数据"""
    try:
        # 用户统计
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        online_users = UserSession.get_online_users_count()
        
        # 资产统计（安全处理可能不存在的模型）
        try:
            total_assets = Asset.objects.count()
            active_assets = Asset.objects.filter(status='active').count()
        except:
            total_assets = 0
            active_assets = 0
        
        # IP统计（安全处理可能不存在的模型）
        try:
            if IPAddress:
                total_ips = IPAddress.objects.count()
                used_ips = IPAddress.objects.filter(status='used').count()
            else:
                total_ips = 0
                used_ips = 0
        except:
            total_ips = 0
            used_ips = 0
        
        # 系统健康状态（简单示例）
        system_health = 'good'
        if online_users > total_users * 0.8:
            system_health = 'excellent'
        elif online_users < total_users * 0.2:
            system_health = 'warning'
        
        # 最近活动
        recent_activities = AdminLog.objects.select_related('user').order_by('-created_at')[:10]
        activities_data = [{
            'user': log.user.username if log.user else '系统',
            'action': log.get_action_display(),
            'description': log.description,
            'time': log.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for log in recent_activities]
        
        stats_data = {
            'total_users': total_users,
            'active_users': active_users,
            'online_users': online_users,
            'total_assets': total_assets,
            'active_assets': active_assets,
            'total_ips': total_ips,
            'used_ips': used_ips,
            'system_health': system_health,
            'recent_activities': activities_data
        }
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': stats_data
        })
        
    except Exception as e:
        return Response({
            'code': 500,
            'message': '获取统计数据失败',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 为了兼容性，添加一个简单的函数视图
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dictionary_by_category(request, category):
    """根据分类获取字典数据的简化接口"""
    try:
        status_filter = request.query_params.get('status', 'active')
        dictionaries = Dictionary.get_by_category(category, status_filter)
        serializer = DictionaryListSerializer(dictionaries, many=True)
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })
    except Exception as e:
        return Response({
            'code': 500,
            'message': '获取字典数据失败',
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
