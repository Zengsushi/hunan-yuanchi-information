from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Department, Position, Employee


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简单序列化器"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class DepartmentSimpleSerializer(serializers.ModelSerializer):
    """部门简单序列化器"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'level', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name()


class DepartmentSerializer(serializers.ModelSerializer):
    """部门序列化器"""
    manager = UserSimpleSerializer(read_only=True)
    manager_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    parent = DepartmentSimpleSerializer(read_only=True)
    parent_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    children = DepartmentSimpleSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    position_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'parent', 'parent_id', 'manager', 'manager_id',
            'description', 'level', 'sort_order', 'status', 'children', 'full_name',
            'employee_count', 'position_count', 'created_at', 'updated_at'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_employee_count(self, obj):
        return obj.employees.filter(employment_status='active').count()

    def get_position_count(self, obj):
        return obj.positions.filter(status='active').count()

    def validate_parent_id(self, value):
        if value and value == self.instance.id if self.instance else False:
            raise serializers.ValidationError("部门不能设置自己为上级部门")
        return value


class DepartmentTreeSerializer(serializers.ModelSerializer):
    """部门树形结构序列化器"""
    children = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()
    manager = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'level', 'sort_order', 'status',
            'manager', 'employee_count', 'children'
        ]

    def get_children(self, obj):
        children = obj.children.filter(status='active').order_by('sort_order', 'name')
        return DepartmentTreeSerializer(children, many=True).data

    def get_employee_count(self, obj):
        return obj.employees.filter(employment_status='active').count()


class PositionSerializer(serializers.ModelSerializer):
    """职位序列化器"""
    department = DepartmentSimpleSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    employee_count = serializers.SerializerMethodField()
    level_display = serializers.CharField(source='get_level_display', read_only=True)

    class Meta:
        model = Position
        fields = [
            'id', 'name', 'code', 'department', 'department_id', 'level', 'level_display',
            'description', 'responsibilities', 'requirements', 'salary_range_min',
            'salary_range_max', 'status', 'employee_count', 'created_at', 'updated_at'
        ]

    def get_employee_count(self, obj):
        return obj.employees.filter(employment_status='active').count()


class EmployeeSimpleSerializer(serializers.ModelSerializer):
    """员工简单序列化器"""
    user = UserSimpleSerializer(read_only=True)
    department = DepartmentSimpleSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'name', 'user', 'department', 'full_name',
            'employment_status', 'hire_date'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()


class EmployeeSerializer(serializers.ModelSerializer):
    """员工序列化器"""
    user = UserSimpleSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    department = DepartmentSimpleSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    position = PositionSerializer(read_only=True)
    position_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    direct_supervisor = EmployeeSimpleSerializer(read_only=True)
    direct_supervisor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    subordinates = EmployeeSimpleSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()
    subordinates_count = serializers.SerializerMethodField()
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    employment_status_display = serializers.CharField(source='get_employment_status_display', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'user', 'user_id', 'name', 'employee_id', 'department', 'department_id',
            'position', 'position_id', 'direct_supervisor', 'direct_supervisor_id',
            'phone', 'mobile', 'email', 'office_location', 'hire_date', 'probation_end_date',
            'contract_type', 'contract_type_display', 'employment_status',
            'employment_status_display', 'emergency_contact_name', 'emergency_contact_phone',
            'salary', 'sort_order', 'notes', 'subordinates', 'full_name', 'subordinates_count',
            'created_at', 'updated_at'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_subordinates_count(self, obj):
        return obj.get_subordinates_count()

    def validate_user_id(self, value):
        # 如果 value 为 None，直接返回
        if value is None:
            return value
        # 检查用户是否已经关联其他员工
        if Employee.objects.filter(user_id=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("该用户已经关联其他员工记录")
        return value

    def validate_employee_id(self, value):
        # 检查工号是否重复
        if Employee.objects.filter(employee_id=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("工号已存在")
        return value

    def validate_direct_supervisor_id(self, value):
        if value and value == self.instance.id if self.instance else False:
            raise serializers.ValidationError("员工不能设置自己为直接上级")
        return value


class EmployeeCreateSerializer(serializers.ModelSerializer):
    """员工创建序列化器"""
    user_id = serializers.IntegerField(required=False, allow_null=True)
    department_id = serializers.IntegerField(required=False, allow_null=True)
    position_id = serializers.IntegerField(required=False, allow_null=True)
    direct_supervisor_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Employee
        fields = [
            'user_id', 'name', 'employee_id', 'department_id', 'position_id',
            'direct_supervisor_id', 'phone', 'mobile', 'email', 'office_location',
            'hire_date', 'probation_end_date', 'contract_type',
            'employment_status', 'emergency_contact_name',
            'emergency_contact_phone', 'salary', 'sort_order', 'notes'
        ]

    def validate_user_id(self, value):
        if value is None:
            return value
        if Employee.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("该用户已经关联其他员工记录")
        return value

    def validate_employee_id(self, value):
        if Employee.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("工号已存在")
        return value

    def create(self, validated_data):
        """自定义创建方法，确保外键字段正确保存"""
        print(f"创建员工，接收到的数据: {validated_data}")
        
        # 处理外键字段
        user_id = validated_data.pop('user_id', None)
        department_id = validated_data.pop('department_id', None)
        position_id = validated_data.pop('position_id', None)
        direct_supervisor_id = validated_data.pop('direct_supervisor_id', None)
        
        # 创建员工实例
        employee = Employee.objects.create(**validated_data)
        
        # 设置外键关系
        if user_id:
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=user_id)
                employee.user = user
            except User.DoesNotExist:
                pass
        
        if department_id:
            try:
                department = Department.objects.get(id=department_id)
                employee.department = department
            except Department.DoesNotExist:
                pass
        
        if position_id:
            try:
                position = Position.objects.get(id=position_id)
                employee.position = position
            except Position.DoesNotExist:
                pass
        
        if direct_supervisor_id:
            try:
                supervisor = Employee.objects.get(id=direct_supervisor_id)
                employee.direct_supervisor = supervisor
            except Employee.DoesNotExist:
                pass
        
        employee.save()
        print(f"员工创建完成，ID: {employee.id}, 部门ID: {employee.department_id}, 职位ID: {employee.position_id}")
        return employee