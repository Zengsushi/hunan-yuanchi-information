from django.db import models
from django.utils import timezone


class Business(models.Model):
    """业务模型"""
    name = models.CharField(max_length=200, verbose_name="业务名称")
    responsible_person = models.CharField(max_length=100, verbose_name="负责人")
    online_date = models.DateField(verbose_name="上线日期")
    access_url = models.URLField(blank=True, null=True, verbose_name="访问地址")
    function_purpose = models.TextField(blank=True, null=True, verbose_name="功能用途")
    description = models.TextField(blank=True, null=True, verbose_name="业务描述")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', '运行中'),
            ('inactive', '已停用'),
            ('maintenance', '维护中'),
            ('testing', '测试中')
        ],
        default='active',
        verbose_name="状态"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "业务"
        verbose_name_plural = "业务"
        ordering = ['-created_at']


class BusinessIP(models.Model):
    """业务关联IP模型"""
    business = models.ForeignKey(
        Business, 
        on_delete=models.CASCADE, 
        related_name='associated_ips',
        verbose_name="关联业务"
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    hostname = models.CharField(max_length=200, blank=True, null=True, verbose_name="主机名")
    port = models.IntegerField(blank=True, null=True, verbose_name="端口")
    service_type = models.CharField(
        max_length=50,
        choices=[
            ('web', 'Web服务'),
            ('database', '数据库'),
            ('cache', '缓存'),
            ('api', 'API服务'),
            ('other', '其他')
        ],
        default='web',
        verbose_name="服务类型"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('online', '在线'),
            ('offline', '离线'),
            ('unknown', '未知')
        ],
        default='unknown',
        verbose_name="状态"
    )
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.business.name} - {self.ip_address}"

    class Meta:
        verbose_name = "业务关联IP"
        verbose_name_plural = "业务关联IP"
        unique_together = ['business', 'ip_address']
        ordering = ['-created_at']


class BusinessMonthlyStats(models.Model):
    """业务月度统计模型"""
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='monthly_stats',
        verbose_name="关联业务"
    )
    year = models.IntegerField(verbose_name="年份")
    month = models.IntegerField(verbose_name="月份")
    total_visits = models.BigIntegerField(default=0, verbose_name="总访问量")
    unique_visitors = models.BigIntegerField(default=0, verbose_name="独立访客数")
    avg_response_time = models.FloatField(default=0.0, verbose_name="平均响应时间(ms)")
    uptime_percentage = models.FloatField(default=100.0, verbose_name="可用性百分比")
    error_count = models.IntegerField(default=0, verbose_name="错误次数")
    data_transfer_gb = models.FloatField(default=0.0, verbose_name="数据传输量(GB)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.business.name} - {self.year}年{self.month}月"

    class Meta:
        verbose_name = "业务月度统计"
        verbose_name_plural = "业务月度统计"
        unique_together = ['business', 'year', 'month']
        ordering = ['-year', '-month']