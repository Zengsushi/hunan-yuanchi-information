from django.db import models
from django.utils import timezone


class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="分类名称")
    description = models.TextField(blank=True, null=True, verbose_name="分类描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "资产分类"
        verbose_name_plural = "资产分类"


class AssetStatus(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="状态名称")
    description = models.TextField(blank=True, null=True, verbose_name="状态描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "资产状态"
        verbose_name_plural = "资产状态"


class Asset(models.Model):
    ASSET_TYPE_CHOICES = (
        ('server', '服务器'),
        ('network', '网络设备'),
        ('storage', '存储设备'),
        ('security', '安全设备'),
        ('other', '其他设备'),
    )

    name = models.CharField(max_length=200, verbose_name="资产名称")
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, verbose_name="资产类型")
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="资产分类")
    status = models.ForeignKey(AssetStatus, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="资产状态")
    serial_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="序列号")
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name="制造商")
    model = models.CharField(max_length=100, blank=True, null=True, verbose_name="型号")
    purchase_date = models.DateField(blank=True, null=True, verbose_name="购买日期")
    warranty_period = models.IntegerField(blank=True, null=True, verbose_name="保修期限(月)")
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="价格")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="存放位置")
    owner = models.CharField(max_length=100, blank=True, null=True, verbose_name="负责人")
    description = models.TextField(blank=True, null=True, verbose_name="资产描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.name} ({self.get_asset_type_display()})"

    class Meta:
        verbose_name = "资产"
        verbose_name_plural = "资产"
        ordering = ['-created_at']


class Server(models.Model):
    SERVER_TYPE_CHOICES = (
        ('physical', '物理服务器'),
        ('virtual', '虚拟服务器'),
        ('cloud', '云服务器'),
    )

    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='server', verbose_name="关联资产")
    server_type = models.CharField(max_length=20, choices=SERVER_TYPE_CHOICES, verbose_name="服务器类型")
    hostname = models.CharField(max_length=200, verbose_name="主机名")
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    os = models.CharField(max_length=100, verbose_name="操作系统")
    os_version = models.CharField(max_length=100, blank=True, null=True, verbose_name="操作系统版本")
    cpu = models.CharField(max_length=100, verbose_name="CPU")
    memory = models.IntegerField(verbose_name="内存(GB)")
    disk = models.IntegerField(verbose_name="磁盘(GB)")
    kernel_version = models.CharField(max_length=100, blank=True, null=True, verbose_name="内核版本")
    ssh_port = models.IntegerField(default=22, verbose_name="SSH端口")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")

    def __str__(self):
        return self.hostname

    class Meta:
        verbose_name = "服务器"
        verbose_name_plural = "服务器"


class NetworkDevice(models.Model):
    NETWORK_DEVICE_TYPE_CHOICES = (
        ('router', '路由器'),
        ('switch', '交换机'),
        ('firewall', '防火墙'),
        ('load_balancer', '负载均衡器'),
        ('access_point', '无线接入点'),
    )

    asset = models.OneToOneField(Asset, on_delete=models.CASCADE, related_name='network_device', verbose_name="关联资产")
    device_type = models.CharField(max_length=20, choices=NETWORK_DEVICE_TYPE_CHOICES, verbose_name="设备类型")
    hostname = models.CharField(max_length=200, verbose_name="主机名")
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    firmware_version = models.CharField(max_length=100, blank=True, null=True, verbose_name="固件版本")
    port_count = models.IntegerField(blank=True, null=True, verbose_name="端口数量")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")

    def __str__(self):
        return self.hostname

    class Meta:
        verbose_name = "网络设备"
        verbose_name_plural = "网络设备"


class ZabbixTemplate(models.Model):
    """Zabbix模板模型"""
    templateid = models.CharField(max_length=50, unique=True, verbose_name="模板ID")
    name = models.CharField(max_length=255, verbose_name="模板名称")
    description = models.TextField(blank=True, null=True, verbose_name="模板描述")
    items_count = models.IntegerField(default=0, verbose_name="监控项数量")
    triggers_count = models.IntegerField(default=0, verbose_name="触发器数量")
    macros_count = models.IntegerField(default=0, verbose_name="宏数量")
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name="图标")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="分类")
    groups = models.JSONField(default=list, blank=True, verbose_name="主机组")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Zabbix模板"
        verbose_name_plural = "Zabbix模板"
        ordering = ['name']


class Supplier(models.Model):
    """供应商模型"""
    name = models.CharField(max_length=200, unique=True, verbose_name="供应商名称")
    contact_person = models.CharField(max_length=100, blank=True, null=True, verbose_name="联系人")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="联系电话")
    email = models.EmailField(blank=True, null=True, verbose_name="邮箱")
    address = models.TextField(blank=True, null=True, verbose_name="地址")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "供应商"
        verbose_name_plural = "供应商"
        ordering = ['name']


class HardwareAsset(models.Model):
    """硬件设施资产模型"""
    
    ASSET_STATUS_CHOICES = [
        ('in_use', '在用'),
        ('scrapped', '报废'),
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
    asset_tag = models.CharField(max_length=100, unique=True, verbose_name="资产标签")
    model = models.CharField(max_length=200, verbose_name="型号")
    asset_owner = models.CharField(max_length=100, verbose_name="资产责任人")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="供应商")
    supplier_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="供应商联系人")
    purchase_date = models.DateField(verbose_name="采购日期")
    project_source = models.CharField(max_length=200, blank=True, null=True, verbose_name="项目来源")
    asset_status = models.CharField(max_length=20, choices=ASSET_STATUS_CHOICES, default='in_use', verbose_name="资产状态")
    
    # 产品信息
    manufacturer = models.CharField(max_length=200, verbose_name="制造商")
    specifications = models.JSONField(default=dict, blank=True, verbose_name="规格参数")
    serial_number = models.CharField(max_length=200, unique=True, verbose_name="序列号")
    
    # 位置信息
    room = models.CharField(max_length=100, blank=True, null=True, verbose_name="机房")
    cabinet = models.CharField(max_length=100, blank=True, null=True, verbose_name="机柜")
    u_position = models.CharField(max_length=20, blank=True, null=True, verbose_name="U位")
    
    # 产品尺寸
    dimensions = models.CharField(max_length=200, blank=True, null=True, verbose_name="产品尺寸")
    
    # 保修信息
    warranty_type = models.CharField(max_length=20, choices=WARRANTY_TYPE_CHOICES, verbose_name="保修类型")
    warranty_start_date = models.DateField(verbose_name="保修开始日期")
    warranty_end_date = models.DateField(verbose_name="保修结束日期")
    
    # 监控状态
    monitoring_status = models.BooleanField(default=False, verbose_name="监控状态")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    @property
    def location(self):
        """获取完整位置信息"""
        location_parts = []
        if self.room:
            location_parts.append(self.room)
        if self.cabinet:
            location_parts.append(self.cabinet)
        if self.u_position:
            location_parts.append(f"U{self.u_position}")
        return "-".join(location_parts) if location_parts else ""
    
    @property
    def warranty_status(self):
        """获取保修状态"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if today <= self.warranty_end_date:
            if self.warranty_type == 'original':
                return 'original_warranty'
            else:
                return 'third_party_warranty'
        else:
            return 'out_of_warranty'
    
    @property
    def warranty_status_display(self):
        """获取保修状态显示文本"""
        status_map = {
            'original_warranty': '原厂保',
            'third_party_warranty': '第三方保',
            'out_of_warranty': '脱保'
        }
        return status_map.get(self.warranty_status, '未知')
    
    def __str__(self):
        return f"{self.asset_tag} - {self.model}"
    
    class Meta:
        verbose_name = "硬件设施"
        verbose_name_plural = "硬件设施"
        ordering = ['-created_at']


class SpecificationUpdateRecord(models.Model):
    """规格参数更新记录模型"""
    
    UPDATE_METHOD_CHOICES = [
        ('manual', '手动'),
        ('automatic', '自动'),
    ]
    
    hardware_asset = models.ForeignKey(HardwareAsset, on_delete=models.CASCADE, related_name='spec_updates', verbose_name="硬件资产")
    old_specifications = models.JSONField(default=dict, verbose_name="更新前规格参数")
    new_specifications = models.JSONField(default=dict, verbose_name="更新后规格参数")
    update_method = models.CharField(max_length=20, choices=UPDATE_METHOD_CHOICES, verbose_name="更新方式")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    updated_by = models.CharField(max_length=100, blank=True, null=True, verbose_name="更新人")
    remarks = models.TextField(blank=True, null=True, verbose_name="备注")
    
    def __str__(self):
        return f"{self.hardware_asset.asset_tag} - 规格更新 - {self.update_time}"
    
    class Meta:
        verbose_name = "规格参数更新记录"
        verbose_name_plural = "规格参数更新记录"
        ordering = ['-update_time']


class WarrantyUpdateRecord(models.Model):
    """保修更新记录模型"""
    
    hardware_asset = models.ForeignKey(HardwareAsset, on_delete=models.CASCADE, related_name='warranty_updates', verbose_name="硬件资产")
    old_warranty_type = models.CharField(max_length=20, verbose_name="更新前保修类型")
    new_warranty_type = models.CharField(max_length=20, verbose_name="更新后保修类型")
    old_warranty_start_date = models.DateField(verbose_name="更新前保修开始日期")
    new_warranty_start_date = models.DateField(verbose_name="更新后保修开始日期")
    old_warranty_end_date = models.DateField(verbose_name="更新前保修结束日期")
    new_warranty_end_date = models.DateField(verbose_name="更新后保修结束日期")
    update_time = models.DateTimeField(auto_now_add=True, verbose_name="更新时间")
    updated_by = models.CharField(max_length=100, blank=True, null=True, verbose_name="更新人")
    remarks = models.TextField(blank=True, null=True, verbose_name="备注")
    
    def __str__(self):
        return f"{self.hardware_asset.asset_tag} - 保修更新 - {self.update_time}"
    
    class Meta:
        verbose_name = "保修更新记录"
        verbose_name_plural = "保修更新记录"
        ordering = ['-update_time']
