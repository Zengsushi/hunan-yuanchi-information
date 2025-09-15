from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings


class Department(models.Model):
    """部门模型"""
    name = models.CharField(max_length=100, verbose_name="部门名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="部门编码")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="上级部门"
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name="部门负责人"
    )
    description = models.TextField(blank=True, null=True, verbose_name="部门描述")
    level = models.IntegerField(default=1, verbose_name="部门层级")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', '正常'),
            ('inactive', '停用'),
        ],
        default='active',
        verbose_name="状态"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    def get_full_name(self):
        """获取完整部门路径"""
        if self.parent:
            return f"{self.parent.get_full_name()} > {self.name}"
        return self.name

    def get_all_children(self):
        """获取所有子部门"""
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children())
        return children

    def save(self, *args, **kwargs):
        """保存时自动计算层级"""
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1
        super().save(*args, **kwargs)
        
        # 更新所有子部门的层级
        self._update_children_level()
    
    def _update_children_level(self):
        """递归更新子部门层级"""
        for child in self.children.all():
            child.level = self.level + 1
            child.save(update_fields=['level'])
            child._update_children_level()

    class Meta:
        verbose_name = "部门"
        verbose_name_plural = "部门"
        ordering = ['level', 'sort_order', 'name']


class Position(models.Model):
    """职位模型"""
    name = models.CharField(max_length=100, verbose_name="职位名称")
    code = models.CharField(max_length=50, unique=True, verbose_name="职位编码")
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name="所属部门"
    )
    level = models.CharField(
        max_length=20,
        choices=[
            ('junior', '初级'),
            ('intermediate', '中级'),
            ('senior', '高级'),
            ('expert', '专家'),
            ('manager', '管理'),
            ('director', '总监'),
            ('vp', '副总'),
            ('ceo', '总裁'),
        ],
        default='junior',
        verbose_name="职位级别"
    )
    description = models.TextField(blank=True, null=True, verbose_name="职位描述")
    responsibilities = models.TextField(blank=True, null=True, verbose_name="岗位职责")
    requirements = models.TextField(blank=True, null=True, verbose_name="任职要求")
    salary_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="薪资范围最低"
    )
    salary_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="薪资范围最高"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', '正常'),
            ('inactive', '停用'),
        ],
        default='active',
        verbose_name="状态"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.department.name} - {self.name}"

    class Meta:
        verbose_name = "职位"
        verbose_name_plural = "职位"
        ordering = ['department', 'level', 'name']


class Employee(models.Model):
    """员工模型"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name="关联用户"
    )
    name = models.CharField(max_length=100, verbose_name="员工姓名", default="未命名员工")
    employee_id = models.CharField(max_length=50, unique=True, verbose_name="工号")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name="所属部门"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name="职位"
    )
    direct_supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name="直接上级"
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="联系电话")
    mobile = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号码")
    email = models.EmailField(blank=True, null=True, verbose_name="邮箱地址")
    office_location = models.CharField(max_length=200, blank=True, null=True, verbose_name="办公地点")
    hire_date = models.DateField(verbose_name="入职日期",blank=True, null=True)
    probation_end_date = models.DateField(null=True, blank=True, verbose_name="试用期结束日期")
    contract_type = models.CharField(
        max_length=20,
        choices=[
            ('full_time', '全职'),
            ('part_time', '兼职'),
            ('contract', '合同工'),
            ('intern', '实习生'),
        ],
        default='full_time',
        verbose_name="合同类型"
    )
    employment_status = models.CharField(
        max_length=20,
        choices=[
            ('active', '在职'),
            ('probation', '试用期'),
            ('leave', '请假'),
            ('resigned', '离职'),
            ('terminated', '解雇'),
        ],
        default='probation',
        verbose_name="就业状态"
    )
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="紧急联系人")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="紧急联系电话")
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="薪资"
    )
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    notes = models.TextField(blank=True, null=True, verbose_name="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.employee_id} - {self.name}"

    def get_full_name(self):
        return self.name

    def get_subordinates_count(self):
        """获取下属数量"""
        return self.subordinates.filter(employment_status='active').count()

    class Meta:
        verbose_name = "员工"
        verbose_name_plural = "员工"
        ordering = ['department', 'position', 'employee_id']