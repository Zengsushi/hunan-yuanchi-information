from django.db import models
from django.contrib.auth import get_user_model
import uuid
import json

User = get_user_model()

class IPRecord(models.Model):
    """IP记录模型"""
    
    STATUS_CHOICES = [
        ('active', '在用'),
        ('available', '可用'),
        ('reserved', '预留'),
        ('conflict', '冲突'),
    ]
    
    TYPE_CHOICES = [
        ('static', '静态IP'),
        ('dynamic', '动态IP'),
        ('gateway', '网关'),
        ('dns', 'DNS服务器'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField(verbose_name="IP地址", unique=True)
    hostname = models.CharField(max_length=255, verbose_name="主机名", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="IP状态")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='static', verbose_name="IP类型")
    mac_address = models.CharField(max_length=17, verbose_name="MAC地址", blank=True, null=True)
    device = models.CharField(max_length=255, verbose_name="关联设备", blank=True, null=True)
    subnet = models.CharField(max_length=50, verbose_name="所属网段", blank=True, null=True)
    description = models.TextField(verbose_name="备注", blank=True, null=True)
    is_auto_discovered = models.BooleanField(default=False, verbose_name="自动发现", help_text="标识此IP是否由Zabbix自动发现")
    zabbix_drule_id = models.CharField(max_length=50, verbose_name="Zabbix发现规则ID", blank=True, null=True, help_text="关联的Zabbix发现规则ID")
    ping_status = models.CharField(max_length=20, choices=[('online', '在线'), ('offline', '离线')], default='offline', verbose_name="Ping状态")
    monitoring_enabled = models.BooleanField(default=False, verbose_name="启用监控", help_text="是否启用对此IP的监控")
    last_seen = models.DateTimeField(verbose_name="最后在线时间", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")

    class Meta:
        db_table = 'ip_records'
        verbose_name = 'IP记录'
        verbose_name_plural = 'IP记录'
        ordering = ['ip_address']

    def __str__(self):
        return f"{self.ip_address} - {self.hostname or 'No hostname'}"


class ScanTask(models.Model):
    """扫描任务模型"""
    
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    CHECK_TYPE_CHOICES = [
        (0, 'SSH'),
        (1, 'LDAP'),
        (2, 'SMTP'),
        (3, 'FTP'),
        (4, 'HTTP'),
        (5, 'POP'),
        (6, 'NNTP'),
        (7, 'IMAP'),
        (8, 'TCP'),
        (9, 'Zabbix agent'),
        (10, 'SNMPv1 agent'),
        (11, 'SNMPv2 agent'),
        (12, 'ICMP ping'),
        (13, 'SNMPv3 agent'),
        (14, 'HTTPS'),
        (15, 'Telnet'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_name = models.CharField(max_length=255, verbose_name="任务名称", blank=True)
    ip_ranges = models.JSONField(verbose_name="IP范围列表")  # 存储IP范围数组
    check_type = models.IntegerField(choices=CHECK_TYPE_CHOICES, verbose_name="检查类型")
    ports = models.CharField(max_length=255, verbose_name="端口范围", blank=True, null=True)
    key = models.CharField(max_length=255, verbose_name="检查键值/SNMP OID", blank=True, null=True)
    snmp_community = models.CharField(max_length=255, verbose_name="SNMP社区", default='public', blank=True, null=True)
    snmpv3_config = models.JSONField(verbose_name="SNMPv3配置", blank=True, null=True)  # 存储SNMPv3配置对象
    unique_check = models.IntegerField(verbose_name="唯一性检查", default=0)
    host_source = models.IntegerField(verbose_name="主机名称来源", default=1)
    name_source = models.IntegerField(verbose_name="可见名称来源", default=0)
    
    # 任务状态和结果
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="任务状态")
    progress = models.IntegerField(default=0, verbose_name="进度百分比")
    result_data = models.JSONField(verbose_name="扫描结果数据", blank=True, null=True)
    error_message = models.TextField(verbose_name="错误信息", blank=True, null=True)
    
    # Zabbix相关
    zabbix_drule_id = models.CharField(max_length=50, verbose_name="Zabbix发现规则ID", blank=True, null=True)
    zabbix_task_id = models.CharField(max_length=50, verbose_name="Zabbix任务ID", blank=True, null=True)
    
    # 时间和用户信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    started_at = models.DateTimeField(verbose_name="开始时间", blank=True, null=True)
    completed_at = models.DateTimeField(verbose_name="完成时间", blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="创建者")

    class Meta:
        db_table = 'scan_tasks'
        verbose_name = '扫描任务'
        verbose_name_plural = '扫描任务'
        ordering = ['-created_at']

    def __str__(self):
        return f"扫描任务 {self.task_name or self.id} - {self.get_status_display()}"

    @property
    def check_type_name(self):
        """获取检查类型名称"""
        type_names = {
            0: 'SSH', 1: 'LDAP', 2: 'SMTP', 3: 'FTP', 4: 'HTTP',
            5: 'POP', 6: 'NNTP', 7: 'IMAP', 8: 'TCP', 9: 'Zabbix agent',
            10: 'SNMPv1', 11: 'SNMPv2', 12: 'ICMP ping', 13: 'SNMPv3',
            14: 'HTTPS', 15: 'Telnet'
        }
        return type_names.get(self.check_type, '未知类型')


class ScanResult(models.Model):
    """扫描结果模型"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan_task = models.ForeignKey(ScanTask, on_delete=models.CASCADE, related_name='results', verbose_name="扫描任务")
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    hostname = models.CharField(max_length=255, verbose_name="主机名", blank=True, null=True)
    mac_address = models.CharField(max_length=17, verbose_name="MAC地址", blank=True, null=True)
    status = models.CharField(max_length=20, verbose_name="检查状态")
    response_time = models.FloatField(verbose_name="响应时间(ms)", blank=True, null=True)
    service_info = models.JSONField(verbose_name="服务信息", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发现时间")

    class Meta:
        db_table = 'scan_results'
        verbose_name = '扫描结果'
        verbose_name_plural = '扫描结果'
        ordering = ['ip_address']
        unique_together = ['scan_task', 'ip_address']

    def __str__(self):
        return f"{self.ip_address} - {self.hostname or 'Unknown'}"
