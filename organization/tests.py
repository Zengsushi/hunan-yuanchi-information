from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Department, Position, Employee


class DepartmentModelTest(TestCase):
    """部门模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_department_creation(self):
        """测试部门创建"""
        department = Department.objects.create(
            name='技术部',
            code='TECH',
            manager=self.user,
            description='技术开发部门'
        )
        self.assertEqual(department.name, '技术部')
        self.assertEqual(department.code, 'TECH')
        self.assertEqual(str(department), '技术部')
        
    def test_department_hierarchy(self):
        """测试部门层级关系"""
        parent_dept = Department.objects.create(
            name='技术中心',
            code='TECH_CENTER',
            level=1
        )
        child_dept = Department.objects.create(
            name='前端开发部',
            code='FRONTEND',
            parent=parent_dept,
            level=2
        )
        
        self.assertEqual(child_dept.parent, parent_dept)
        self.assertIn(child_dept, parent_dept.children.all())
        self.assertEqual(child_dept.get_full_name(), '技术中心 > 前端开发部')


class PositionModelTest(TestCase):
    """职位模型测试"""
    
    def setUp(self):
        self.department = Department.objects.create(
            name='技术部',
            code='TECH'
        )
        
    def test_position_creation(self):
        """测试职位创建"""
        position = Position.objects.create(
            name='高级工程师',
            code='SENIOR_ENG',
            department=self.department,
            level='senior'
        )
        self.assertEqual(position.name, '高级工程师')
        self.assertEqual(position.department, self.department)
        self.assertEqual(str(position), '技术部 - 高级工程师')


class EmployeeModelTest(TestCase):
    """员工模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='employee1',
            first_name='张',
            last_name='三',
            email='zhangsan@example.com',
            password='testpass123'
        )
        self.department = Department.objects.create(
            name='技术部',
            code='TECH'
        )
        self.position = Position.objects.create(
            name='工程师',
            code='ENGINEER',
            department=self.department
        )
        
    def test_employee_creation(self):
        """测试员工创建"""
        employee = Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            department=self.department,
            position=self.position,
            hire_date='2024-01-01'
        )
        self.assertEqual(employee.user, self.user)
        self.assertEqual(employee.employee_id, 'EMP001')
        self.assertEqual(employee.get_full_name(), '张三')
        self.assertEqual(str(employee), 'EMP001 - 张三')


class OrganizationAPITest(APITestCase):
    """组织架构API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.department = Department.objects.create(
            name='技术部',
            code='TECH',
            manager=self.user
        )
        
    def test_department_list(self):
        """测试部门列表API"""
        response = self.client.get('/api/organization/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_department_create(self):
        """测试部门创建API"""
        data = {
            'name': '产品部',
            'code': 'PRODUCT',
            'description': '产品管理部门'
        }
        response = self.client.post('/api/organization/departments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)
        
    def test_department_tree(self):
        """测试部门树形结构API"""
        response = self.client.get('/api/organization/departments/tree/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_position_list(self):
        """测试职位列表API"""
        Position.objects.create(
            name='工程师',
            code='ENGINEER',
            department=self.department
        )
        response = self.client.get('/api/organization/positions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
    def test_employee_list(self):
        """测试员工列表API"""
        Employee.objects.create(
            user=self.user,
            employee_id='EMP001',
            department=self.department,
            hire_date='2024-01-01'
        )
        response = self.client.get('/api/organization/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)