from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Business, BusinessIP, BusinessMonthlyStats
from .serializers import (
    BusinessSerializer, BusinessCreateSerializer, BusinessDetailSerializer,
    BusinessIPSerializer,
    BusinessMonthlyStatsSerializer, BusinessMonthlyStatsCreateSerializer
)


class BusinessViewSet(viewsets.ModelViewSet):
    """业务管理视图集"""
    queryset = Business.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BusinessCreateSerializer
        elif self.action == 'retrieve':
            return BusinessDetailSerializer
        return BusinessSerializer
    
    def get_queryset(self):
        queryset = Business.objects.all()
        
        # 搜索过滤
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(department__icontains=search) |
                Q(responsible_person__icontains=search)
            )
        
        # 部门过滤
        department = self.request.query_params.get('department', None)
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        # 状态过滤
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 日期范围过滤
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            queryset = queryset.filter(online_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(online_date__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def associated_ips(self, request, pk=None):
        """获取业务关联的IP列表"""
        business = self.get_object()
        ips = business.associated_ips.all()
        serializer = BusinessIPSerializer(ips, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_ip(self, request, pk=None):
        """为业务添加关联IP"""
        business = self.get_object()
        serializer = BusinessIPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(business=business)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def monthly_stats(self, request, pk=None):
        """获取业务月度统计数据"""
        business = self.get_object()
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', None)
        
        queryset = business.monthly_stats.filter(year=year)
        if month:
            queryset = queryset.filter(month=month)
        
        serializer = BusinessMonthlyStatsSerializer(queryset, many=True)
        return Response(serializer.data)


class BusinessIPViewSet(viewsets.ModelViewSet):
    """业务关联IP视图集"""
    queryset = BusinessIP.objects.all()
    serializer_class = BusinessIPSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = BusinessIP.objects.all()
        business_id = self.request.query_params.get('business_id', None)
        if business_id:
            queryset = queryset.filter(business_id=business_id)
        return queryset


class BusinessMonthlyStatsViewSet(viewsets.ModelViewSet):
    """业务月度统计视图集"""
    queryset = BusinessMonthlyStats.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BusinessMonthlyStatsCreateSerializer
        return BusinessMonthlyStatsSerializer
    
    def get_queryset(self):
        queryset = BusinessMonthlyStats.objects.all()
        
        # 业务过滤
        business_id = self.request.query_params.get('business_id', None)
        if business_id:
            queryset = queryset.filter(business_id=business_id)
        
        # 年份过滤
        year = self.request.query_params.get('year', None)
        if year:
            queryset = queryset.filter(year=year)
        
        # 月份过滤
        month = self.request.query_params.get('month', None)
        if month:
            queryset = queryset.filter(month=month)
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def business_statistics(request):
    """业务统计接口"""
    # 总业务数
    total_businesses = Business.objects.count()
    
    # 按状态统计
    status_stats = Business.objects.values('status').annotate(count=Count('id'))
    
    # 按部门统计
    department_stats = Business.objects.values('department').annotate(count=Count('id'))
    
    # 本月新增业务
    current_month = timezone.now().replace(day=1)
    monthly_new = Business.objects.filter(created_at__gte=current_month).count()
    
    # 关联IP总数
    total_ips = BusinessIP.objects.count()
    
    return Response({
        'total_businesses': total_businesses,
        'status_stats': list(status_stats),
        'department_stats': list(department_stats),
        'monthly_new': monthly_new,
        'total_ips': total_ips
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def monthly_data_summary(request):
    """月度数据汇总接口"""
    year = request.GET.get('year', timezone.now().year)
    month = request.GET.get('month', timezone.now().month)
    
    # 获取指定月份的所有统计数据
    monthly_stats = BusinessMonthlyStats.objects.filter(year=year, month=month)
    
    if not monthly_stats.exists():
        return Response({
            'year': year,
            'month': month,
            'total_visits': 0,
            'total_unique_visitors': 0,
            'avg_response_time': 0,
            'avg_uptime': 0,
            'total_errors': 0,
            'total_data_transfer': 0,
            'business_count': 0
        })
    
    # 汇总统计
    total_visits = sum(stat.total_visits for stat in monthly_stats)
    total_unique_visitors = sum(stat.unique_visitors for stat in monthly_stats)
    avg_response_time = sum(stat.avg_response_time for stat in monthly_stats) / len(monthly_stats)
    avg_uptime = sum(stat.uptime_percentage for stat in monthly_stats) / len(monthly_stats)
    total_errors = sum(stat.error_count for stat in monthly_stats)
    total_data_transfer = sum(stat.data_transfer_gb for stat in monthly_stats)
    
    return Response({
        'year': year,
        'month': month,
        'total_visits': total_visits,
        'total_unique_visitors': total_unique_visitors,
        'avg_response_time': round(avg_response_time, 2),
        'avg_uptime': round(avg_uptime, 2),
        'total_errors': total_errors,
        'total_data_transfer': round(total_data_transfer, 2),
        'business_count': len(monthly_stats)
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def yearly_trend(request):
    """年度趋势数据接口"""
    year = request.GET.get('year', timezone.now().year)
    business_id = request.GET.get('business_id', None)
    
    queryset = BusinessMonthlyStats.objects.filter(year=year)
    if business_id:
        queryset = queryset.filter(business_id=business_id)
    
    # 按月份分组统计
    monthly_data = []
    for month in range(1, 13):
        month_stats = queryset.filter(month=month)
        if month_stats.exists():
            total_visits = sum(stat.total_visits for stat in month_stats)
            avg_response_time = sum(stat.avg_response_time for stat in month_stats) / len(month_stats)
            avg_uptime = sum(stat.uptime_percentage for stat in month_stats) / len(month_stats)
        else:
            total_visits = 0
            avg_response_time = 0
            avg_uptime = 0
        
        monthly_data.append({
            'month': month,
            'total_visits': total_visits,
            'avg_response_time': round(avg_response_time, 2),
            'avg_uptime': round(avg_uptime, 2)
        })
    
    return Response({
        'year': year,
        'monthly_data': monthly_data
    })