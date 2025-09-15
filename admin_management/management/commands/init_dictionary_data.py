from django.core.management.base import BaseCommand
from admin_management.models import Dictionary


class Command(BaseCommand):
    help = '初始化字典数据'

    def handle(self, *args, **options):
        """初始化字典数据"""
        
        # 定义初始字典数据
        dictionary_data = [
            # 用户分类
            {
                'category': 'user_category',
                'key': 'admin',
                'label': '管理员',
                'description': '系统管理员用户',
                'priority': 100,
                'status': 'active'
            },
            {
                'category': 'user_category',
                'key': 'operator',
                'label': '操作员',
                'description': '系统操作员用户',
                'priority': 80,
                'status': 'active'
            },
            {
                'category': 'user_category',
                'key': 'viewer',
                'label': '查看者',
                'description': '只读权限用户',
                'priority': 60,
                'status': 'active'
            },
            
            # 系统配置
            {
                'category': 'system_config',
                'key': 'session_timeout',
                'label': '会话超时时间',
                'description': '用户会话的超时时间设置',
                'priority': 90,
                'status': 'active',
                'config': '{"unit": "minutes", "default": 30, "min": 5, "max": 480}'
            },
            {
                'category': 'system_config',
                'key': 'password_policy',
                'label': '密码策略',
                'description': '用户密码复杂度要求',
                'priority': 80,
                'status': 'active',
                'config': '{"min_length": 8, "require_uppercase": true, "require_lowercase": true, "require_numbers": true}'
            },
            
            # 资产类型
            {
                'category': 'asset_type',
                'key': 'server',
                'label': '服务器',
                'description': '物理服务器或虚拟机',
                'priority': 100,
                'status': 'active'
            },
            {
                'category': 'asset_type',
                'key': 'network_device',
                'label': '网络设备',
                'description': '交换机、路由器等网络设备',
                'priority': 90,
                'status': 'active'
            },
            {
                'category': 'asset_type',
                'key': 'storage',
                'label': '存储设备',
                'description': '磁盘阵列、存储柜等',
                'priority': 80,
                'status': 'active'
            },
            
            # 部门
            {
                'category': 'department',
                'key': 'it',
                'label': 'IT部门',
                'description': '信息技术部门',
                'priority': 100,
                'status': 'active'
            },
            {
                'category': 'department',
                'key': 'ops',
                'label': '运维部门',
                'description': '系统运维部门',
                'priority': 90,
                'status': 'active'
            },
            {
                'category': 'department',
                'key': 'dev',
                'label': '开发部门',
                'description': '软件开发部门',
                'priority': 80,
                'status': 'active'
            },
            
            # 状态
            {
                'category': 'status',
                'key': 'active',
                'label': '活跃',
                'description': '正常活跃状态',
                'priority': 100,
                'status': 'active',
                'config': '{"color": "green", "icon": "check-circle"}'
            },
            {
                'category': 'status',
                'key': 'inactive',
                'label': '非活跃',
                'description': '暂时停用状态',
                'priority': 80,
                'status': 'active',
                'config': '{"color": "orange", "icon": "pause-circle"}'
            },
            {
                'category': 'status',
                'key': 'disabled',
                'label': '禁用',
                'description': '完全禁用状态',
                'priority': 60,
                'status': 'active',
                'config': '{"color": "red", "icon": "stop-circle"}'
            },
            
            # 优先级
            {
                'category': 'priority',
                'key': 'critical',
                'label': '严重',
                'description': '最高优先级',
                'priority': 100,
                'status': 'active',
                'config': '{"color": "red", "level": 1}'
            },
            {
                'category': 'priority',
                'key': 'high',
                'label': '高',
                'description': '高优先级',
                'priority': 80,
                'status': 'active',
                'config': '{"color": "orange", "level": 2}'
            },
            {
                'category': 'priority',
                'key': 'medium',
                'label': '中',
                'description': '中等优先级',
                'priority': 60,
                'status': 'active',
                'config': '{"color": "blue", "level": 3}'
            },
            {
                'category': 'priority',
                'key': 'low',
                'label': '低',
                'description': '低优先级',
                'priority': 40,
                'status': 'active',
                'config': '{"color": "green", "level": 4}'
            },
            
            # 环境
            {
                'category': 'environment',
                'key': 'production',
                'label': '生产环境',
                'description': '正式生产环境',
                'priority': 100,
                'status': 'active',
                'config': '{"color": "red", "protection_level": "high"}'
            },
            {
                'category': 'environment',
                'key': 'staging',
                'label': '预发布环境',
                'description': '预发布测试环境',
                'priority': 80,
                'status': 'active',
                'config': '{"color": "orange", "protection_level": "medium"}'
            },
            {
                'category': 'environment',
                'key': 'testing',
                'label': '测试环境',
                'description': '功能测试环境',
                'priority': 60,
                'status': 'active',
                'config': '{"color": "blue", "protection_level": "low"}'
            },
            {
                'category': 'environment',
                'key': 'development',
                'label': '开发环境',
                'description': '开发调试环境',
                'priority': 40,
                'status': 'active',
                'config': '{"color": "green", "protection_level": "low"}'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for data in dictionary_data:
            dictionary, created = Dictionary.objects.get_or_create(
                category=data['category'],
                key=data['key'],
                defaults=data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建字典项: {dictionary.category} - {dictionary.key}')
                )
            else:
                # 更新现有记录
                for field, value in data.items():
                    if field not in ['category', 'key']:
                        setattr(dictionary, field, value)
                dictionary.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新字典项: {dictionary.category} - {dictionary.key}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'字典数据初始化完成！创建 {created_count} 个，更新 {updated_count} 个'
            )
        )