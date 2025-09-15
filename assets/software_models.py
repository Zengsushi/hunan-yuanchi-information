from django.db import models
from django.utils import timezone
from .models import Supplier


class SoftwareAsset(models.Model):
    """软件资产模型"""

    SOFTWARE_TYPE_CHOICES = [
        ('operating_system', '操作系统'),
        ('database', '数据库'),
        ('middleware', '中间件'),
        ('application', '应用软件'),
        ('development_tool', '开发工具'),
        ('security_software', '安全软件'),
        ('monitoring_tool', '监控工具'),
        ('backup_software', '备份软件'),
        ('other', '其他软件'),
    ]

    LICENSE_TYPE_CHOICES = [
        ('commercial', '商业许可'),
        ('open_source', '开源许可'),
        ('trial', '试用许可'),
        ('educational', '教育许可'),
        ('oem', 'OEM许可'),
    ]

    ASSET_STATUS_CHOICES = [
        ('in_use', '在用'),
    ]

    LICENSE_STATUS_CHOICES = [
        ('active', '有效'),
        ('expired', '已过期'),
        ('suspended', '已暂停'),
        ('terminated', '已终止'),
    ]

    WARRANTY_TYPE_CHOICES = [
        ('original', '原厂保修'),
        ('third_party', '第三方保修'),
    ]

    WARRANTY_STATUS_CHOICES = [
        ('original_warranty', '原厂保'),
        ('third_party_warranty', '第三方保'),
        ('out_of_warranty', '脱保'),
    ]

    # 基本信息
    name = models.CharField(max_length=200, verbose_name="软件名称", null=True)
    software_type = models.CharField(max_length=30, choices=SOFTWARE_TYPE_CHOICES, verbose_name="软件类型", null=True,
                                     default='other')
    vendor = models.CharField(max_length=200, verbose_name="软件厂商", null=True)
    version = models.CharField(max_length=100, verbose_name="软件版本", null=True)
    asset_tag = models.CharField(max_length=100, unique=True, verbose_name="资产标签", blank=True)
    asset_owner = models.CharField(max_length=100, verbose_name="资产责任人", blank=True)
    asset_status = models.CharField(max_length=20, choices=ASSET_STATUS_CHOICES, default='in_use',
                                    verbose_name="资产状态")

    # 保修信息
    warranty_type = models.CharField(max_length=20, choices=WARRANTY_TYPE_CHOICES, verbose_name="保修类型", null=True)
    warranty_status = models.CharField(max_length=20, choices=WARRANTY_STATUS_CHOICES, verbose_name="保修类型",
                                       null=True)
    warranty_start_date = models.DateField(verbose_name="保修开始日期", null=True)
    warranty_end_date = models.DateField(verbose_name="保修结束日期", null=True)

    # 许可证信息
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPE_CHOICES, verbose_name="许可证类型", null=True,
                                    blank=True)
    license_key = models.TextField(blank=True, null=True, verbose_name="许可证密钥")
    license_count = models.IntegerField(default=1, verbose_name="许可证数量")
    license_used = models.IntegerField(default=0, verbose_name="已使用许可证")
    license_status = models.CharField(max_length=20, choices=LICENSE_STATUS_CHOICES, default='active',
                                      verbose_name="许可证状态")
    license_start_date = models.DateField(blank=True, null=True, verbose_name="许可证开始日期")
    license_end_date = models.DateField(blank=True, null=True, verbose_name="许可证结束日期")

    # 采购信息
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="供应商")
    supplier_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="供应商联系人")
    purchase_date = models.DateField(blank=True, null=True, verbose_name="采购日期")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                         verbose_name="采购价格")
    project_source = models.CharField(max_length=200, blank=True, null=True, verbose_name="项目来源")

    # 技术信息
    installation_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="安装路径")
    configuration = models.JSONField(default=dict, blank=True, verbose_name="配置信息")
    dependencies = models.TextField(blank=True, null=True, verbose_name="依赖关系")
    supported_os = models.CharField(max_length=200, blank=True, null=True, verbose_name="支持的操作系统")
    minimum_requirements = models.JSONField(default=dict, blank=True, verbose_name="最低系统要求")

    # 维护信息
    support_end_date = models.DateField(blank=True, null=True, verbose_name="支持结束日期")
    last_update_date = models.DateField(blank=True, null=True, verbose_name="最后更新日期")
    update_frequency = models.CharField(max_length=100, blank=True, null=True, verbose_name="更新频率")

    # 使用信息
    deployment_servers = models.TextField(blank=True, null=True, verbose_name="部署服务器")
    usage_description = models.TextField(blank=True, null=True, verbose_name="使用说明")

    # 审计字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    @property
    def license_available(self):
        """可用许可证数量"""
        return self.license_count - self.license_used

    @property
    def license_utilization_rate(self):
        """许可证使用率"""
        if self.license_count == 0:
            return 0
        return round((self.license_used / self.license_count) * 100, 2)

    @property
    def is_license_expired(self):
        """许可证是否过期"""
        if not self.license_end_date:
            return False
        return timezone.now().date() > self.license_end_date

    @property
    def days_until_license_expiry(self):
        """许可证到期剩余天数"""
        if not self.license_end_date:
            return None
        delta = self.license_end_date - timezone.now().date()
        return delta.days if delta.days >= 0 else 0

    def __str__(self):
        return f"{self.software_name} v{self.version} - {self.asset_tag}"

    class Meta:
        verbose_name = "软件资产"
        verbose_name_plural = "软件资产"
        ordering = ['-created_at']


class SoftwareLicenseUpdateRecord(models.Model):
    """软件许可证更新记录模型"""

    UPDATE_TYPE_CHOICES = [
        ('renewal', '续费'),
        ('upgrade', '升级'),
        ('downgrade', '降级'),
        ('transfer', '转移'),
        ('termination', '终止'),
    ]

    software_asset = models.ForeignKey(SoftwareAsset, on_delete=models.CASCADE, related_name='license_updates',
                                       verbose_name="软件资产")
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPE_CHOICES, verbose_name="更新类型")

    # 更新前信息
    old_license_type = models.CharField(max_length=20, verbose_name="更新前许可证类型")
    old_license_count = models.IntegerField(verbose_name="更新前许可证数量")
    old_license_start_date = models.DateField(blank=True, null=True, verbose_name="更新前开始日期")
    old_license_end_date = models.DateField(blank=True, null=True, verbose_name="更新前结束日期")

    # 更新后信息
    new_license_type = models.CharField(max_length=20, verbose_name="更新后许可证类型")
    new_license_count = models.IntegerField(verbose_name="更新后许可证数量")
    new_license_start_date = models.DateField(blank=True, null=True, verbose_name="更新后开始日期")
    new_license_end_date = models.DateField(blank=True, null=True, verbose_name="更新后结束日期")

    # 更新信息
    update_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="更新费用")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    updated_by = models.CharField(max_length=100, blank=True, null=True, verbose_name="更新人")
    remarks = models.TextField(blank=True, null=True, verbose_name="备注")

    def __str__(self):
        return f"{self.software_asset.software_name} - {self.get_update_type_display()} - {self.update_time}"

    class Meta:
        verbose_name = "软件许可证更新记录"
        verbose_name_plural = "软件许可证更新记录"
        ordering = ['-update_time']


class SoftwareVersionUpdateRecord(models.Model):
    """软件版本更新记录模型"""

    UPDATE_METHOD_CHOICES = [
        ('manual', '手动更新'),
        ('automatic', '自动更新'),
        ('scheduled', '计划更新'),
    ]

    software_asset = models.ForeignKey(SoftwareAsset, on_delete=models.CASCADE, related_name='version_updates',
                                       verbose_name="软件资产")
    old_version = models.CharField(max_length=100, verbose_name="更新前版本")
    new_version = models.CharField(max_length=100, verbose_name="更新后版本")
    update_method = models.CharField(max_length=20, choices=UPDATE_METHOD_CHOICES, verbose_name="更新方式")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    updated_by = models.CharField(max_length=100, blank=True, null=True, verbose_name="更新人")
    update_notes = models.TextField(blank=True, null=True, verbose_name="更新说明")
    rollback_available = models.BooleanField(default=True, verbose_name="是否可回滚")

    def __str__(self):
        return f"{self.software_asset.software_name} - {self.old_version} → {self.new_version}"

    class Meta:
        verbose_name = "软件版本更新记录"
        verbose_name_plural = "软件版本更新记录"
        ordering = ['-update_time']


class SoftwareDeployment(models.Model):
    """软件部署记录模型"""

    DEPLOYMENT_STATUS_CHOICES = [
        ('deployed', '已部署'),
        ('undeployed', '已卸载'),
        ('failed', '部署失败'),
        ('pending', '待部署'),
    ]

    software_asset = models.ForeignKey(SoftwareAsset, on_delete=models.CASCADE, related_name='deployments',
                                       verbose_name="软件资产")
    server_hostname = models.CharField(max_length=200, verbose_name="服务器主机名")
    server_ip = models.GenericIPAddressField(verbose_name="服务器IP")
    deployment_path = models.CharField(max_length=500, verbose_name="部署路径")
    deployment_status = models.CharField(max_length=20, choices=DEPLOYMENT_STATUS_CHOICES, verbose_name="部署状态")
    deployment_date = models.DateTimeField(verbose_name="部署时间")
    deployed_by = models.CharField(max_length=100, verbose_name="部署人")
    configuration_details = models.JSONField(default=dict, blank=True, verbose_name="配置详情")
    remarks = models.TextField(blank=True, null=True, verbose_name="备注")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.software_asset.software_name} - {self.server_hostname}"

    class Meta:
        verbose_name = "软件部署记录"
        verbose_name_plural = "软件部署记录"
        ordering = ['-deployment_date']
        unique_together = ['software_asset', 'server_hostname']
