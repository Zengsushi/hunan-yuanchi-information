from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.contrib.auth.models import User

from .models import Department, Position, Employee
from .serializers import (
    DepartmentSerializer, DepartmentTreeSerializer, DepartmentSimpleSerializer,
    PositionSerializer, EmployeeSerializer, EmployeeCreateSerializer,
    EmployeeSimpleSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """部门管理视图集"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['level', 'sort_order', 'name', 'created_at']
    ordering = ['level', 'sort_order', 'name']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DepartmentSerializer
        elif self.action == 'tree':
            return DepartmentTreeSerializer
        return DepartmentSerializer

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取部门树形结构"""
        # 只获取根部门（没有父部门的部门）
        root_departments = Department.objects.filter(
            parent__isnull=True,
            status='active'
        ).order_by('sort_order', 'name')
        
        serializer = DepartmentTreeSerializer(root_departments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """获取部门下的员工"""
        department = self.get_object()
        employees = department.employees.filter(employment_status='active')
        
        # 支持搜索
        search = request.query_params.get('search')
        if search:
            employees = employees.filter(
                Q(user__username__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        serializer = EmployeeSimpleSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def positions(self, request, pk=None):
        """获取部门下的职位"""
        department = self.get_object()
        positions = department.positions.filter(status='active')
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """部门统计信息"""
        stats = {
            'total_departments': Department.objects.filter(status='active').count(),
            'total_employees': Employee.objects.filter(employment_status='active').count(),
            'total_positions': Position.objects.filter(status='active').count(),
            'departments_by_level': list(
                Department.objects.filter(status='active')
                .values('level')
                .annotate(count=Count('id'))
                .order_by('level')
            )
        }
        return Response(stats)


class PositionViewSet(viewsets.ModelViewSet):
    """职位管理视图集"""
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['level', 'name', 'created_at']
    ordering = ['department', 'level', 'name']

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        """获取职位下的员工"""
        position = self.get_object()
        employees = position.employees.filter(employment_status='active')
        serializer = EmployeeSimpleSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """按部门分组获取职位"""
        department_id = request.query_params.get('department_id')
        if not department_id:
            return Response({'error': '请提供部门ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        positions = Position.objects.filter(
            department_id=department_id,
            status='active'
        ).order_by('level', 'name')
        
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    """员工管理视图集"""
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'employee_id', 'phone', 'mobile']
    ordering_fields = ['employee_id', 'hire_date', 'created_at']
    ordering = ['department', 'position', 'employee_id']

    def get_serializer_class(self):
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer

    @action(detail=True, methods=['get'])
    def subordinates(self, request, pk=None):
        """获取员工的下属"""
        employee = self.get_object()
        subordinates = employee.subordinates.filter(employment_status='active')
        serializer = EmployeeSimpleSerializer(subordinates, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_supervisor(self, request):
        """按上级获取员工"""
        supervisor_id = request.query_params.get('supervisor_id')
        if not supervisor_id:
            return Response({'error': '请提供上级ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        employees = Employee.objects.filter(
            direct_supervisor_id=supervisor_id,
            employment_status='active'
        )
        
        serializer = EmployeeSimpleSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def available_users(self, request):
        """获取可用的用户（未关联员工的用户）"""
        # 获取已经关联员工的用户ID
        linked_user_ids = Employee.objects.values_list('user_id', flat=True)
        
        # 获取未关联的用户
        available_users = User.objects.exclude(id__in=linked_user_ids)
        
        # 支持搜索
        search = request.query_params.get('search')
        if search:
            available_users = available_users.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # 简单序列化用户信息
        users_data = [{
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'full_name': user.get_full_name() or user.username
        } for user in available_users[:50]]  # 限制返回数量
        
        return Response(users_data)

    @action(detail=False, methods=['get'])
    def for_business(self, request):
        """获取业务管理所需的员工列表"""
        employees = Employee.objects.filter(employment_status='active')
        
        # 支持搜索
        search = request.query_params.get('search')
        if search:
            employees = employees.filter(
                Q(user__username__icontains=search) |
                Q(name__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        # 返回简化的员工数据，适合业务管理使用
        employees_data = []
        for emp in employees:
            employees_data.append({
                'id': emp.id,
                'username': emp.user.username if emp.user else emp.employee_id,
                'real_name': emp.name or (emp.user.get_full_name() if emp.user else ''),
                'department': emp.department.name if emp.department else '',
                'position': emp.position.name if emp.position else '',
                'employee_id': emp.employee_id,
                'phone': emp.mobile or emp.phone
            })
        
        return Response(employees_data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """员工统计信息"""
        stats = {
            'total_employees': Employee.objects.filter(employment_status='active').count(),
            'by_employment_status': list(
                Employee.objects.values('employment_status')
                .annotate(count=Count('id'))
                .order_by('employment_status')
            ),
            'by_contract_type': list(
                Employee.objects.filter(employment_status='active')
                .values('contract_type')
                .annotate(count=Count('id'))
                .order_by('contract_type')
            ),
            'by_department': list(
                Employee.objects.filter(employment_status='active')
                .values('department__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]  # 前10个部门
            )
        }
        return Response(stats)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """更改员工状态"""
        employee = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response({'error': '请提供新状态'}, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = [choice[0] for choice in Employee._meta.get_field('employment_status').choices]
        if new_status not in valid_statuses:
            return Response({'error': '无效的状态'}, status=status.HTTP_400_BAD_REQUEST)
        
        employee.employment_status = new_status
        employee.save()
        
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)