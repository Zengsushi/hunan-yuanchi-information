from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Business, BusinessIP, BusinessMonthlyStats


class BusinessModelTest(TestCase):
    """业务模型测试"""
    
    def setUp(self):
        self.business = Business.objects.create(
            name="测试业务",
            department="技术部",
            responsible_person="张三",
            online_date="2024-01-01",
            description="测试用途"
        )
    
    def test_business_creation(self):
        """测试业务创建"""
        self.assertEqual(self.business.name, "测试业务")
        self.assertEqual(self.business.department, "技术部")
        self.assertEqual(self.business.status, "active")
    
    def test_business_str(self):
        """测试业务字符串表示"""
        self.assertEqual(str(self.business), "测试业务")


class BusinessIPModelTest(TestCase):
    """业务IP模型测试"""
    
    def setUp(self):
        self.business = Business.objects.create(
            name="测试业务",
            department="技术部",
            responsible_person="张三",
            online_date="2024-01-01",
            description="测试用途"
        )
        self.business_ip = BusinessIP.objects.create(
            business=self.business,
            ip_address="192.168.1.100",
            hostname="test-server",
            service_type="web"
        )
    
    def test_business_ip_creation(self):
        """测试业务IP创建"""
        self.assertEqual(self.business_ip.ip_address, "192.168.1.100")
        self.assertEqual(self.business_ip.business, self.business)
        self.assertEqual(self.business_ip.service_type, "web")
    
    def test_business_ip_str(self):
        """测试业务IP字符串表示"""
        expected = f"{self.business.name} - {self.business_ip.ip_address}"
        self.assertEqual(str(self.business_ip), expected)


class BusinessAPITest(APITestCase):
    """业务API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.business = Business.objects.create(
            name="测试业务",
            department="技术部",
            responsible_person="张三",
            online_date="2024-01-01",
            description="测试用途"
        )
    
    def test_get_business_list(self):
        """测试获取业务列表"""
        url = reverse('business-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_get_business_detail(self):
        """测试获取业务详情"""
        url = reverse('business-detail', kwargs={'pk': self.business.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "测试业务")
    
    def test_create_business_authenticated(self):
        """测试认证用户创建业务"""
        self.client.force_authenticate(user=self.user)
        url = reverse('business-list')
        data = {
            'name': '新业务',
            'department': '开发部',
            'responsible_person': '李四',
            'online_date': '2024-02-01',
            'description': '新功能'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Business.objects.count(), 2)


class BusinessStatisticsAPITest(APITestCase):
    """业务统计API测试"""
    
    def setUp(self):
        self.business1 = Business.objects.create(
            name="业务1",
            department="技术部",
            responsible_person="张三",
            online_date="2024-01-01",
            description="测试用途1"
        )
        self.business2 = Business.objects.create(
            name="业务2",
            department="产品部",
            responsible_person="李四",
            online_date="2024-01-01",
            description="测试用途2",
            status="inactive"
        )
    
    def test_business_statistics(self):
        """测试业务统计接口"""
        url = reverse('business-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_businesses'], 2)
        self.assertTrue('status_stats' in response.data)
        self.assertTrue('department_stats' in response.data)


class MonthlyStatsTest(TestCase):
    """月度统计测试"""
    
    def setUp(self):
        self.business = Business.objects.create(
            name="测试业务",
            department="技术部",
            responsible_person="张三",
            online_date="2024-01-01",
            description="测试用途"
        )
        self.monthly_stats = BusinessMonthlyStats.objects.create(
            business=self.business,
            year=2024,
            month=1,
            total_visits=10000,
            unique_visitors=5000,
            avg_response_time=200.5,
            uptime_percentage=99.9
        )
    
    def test_monthly_stats_creation(self):
        """测试月度统计创建"""
        self.assertEqual(self.monthly_stats.business, self.business)
        self.assertEqual(self.monthly_stats.year, 2024)
        self.assertEqual(self.monthly_stats.month, 1)
        self.assertEqual(self.monthly_stats.total_visits, 10000)
    
    def test_monthly_stats_str(self):
        """测试月度统计字符串表示"""
        expected = f"{self.business.name} - 2024年1月"
        self.assertEqual(str(self.monthly_stats), expected)