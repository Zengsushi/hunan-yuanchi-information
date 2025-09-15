#调用zabbix api
try:
    from pyzabbix import ZabbixAPI
except ImportError:
    try:
        from zabbix_api import ZabbixAPI
    except ImportError:
        # 如果都没有安装，创建一个模拟类
        class ZabbixAPI:
            def __init__(self, url):
                self.url = url
                print(f"警告: 未找到Zabbix API库，使用模拟模式。URL: {url}")
            
            def login(self, user, password):
                print(f"模拟登录: {user}")
                return True

# 初始化Zabbix API连接
try:
    zapi = ZabbixAPI("http://192.168.10.128/zabbix")
    zapi.login("Admin", "zabbix")
    print("✓ Zabbix API连接成功")
except ImportError as ie:
    print(f"警告: Zabbix API库未安装: {str(ie)}")
    print("建议安装: pip install pyzabbix")
    zapi = None
except Exception as e:
    print(f"警告: Zabbix API连接失败: {str(e)}")
    print("原因可能包括:")
    print("1. Zabbix服务器不可达 (http://192.168.0.134/zabbix)")
    print("2. 用户名或密码错误 (Admin/zabbix)")
    print("3. Zabbix服务器未启动或配置错误")
    print("系统将在无Zabbix连接的情况下运行，相关功能将被跳过")
    zapi = None

#zabbix自动发现模块
class zabbix_auto_discovery():
    def __init__(self, zapi_instance=None):
        """初始化Zabbix自动发现类"""
        self.zapi = zapi_instance or zapi
        self.connection_status = {
            'connected': False,
            'version': None,
            'error': None
        }
        
        # 检查API连接是否有效
        if self.zapi is None:
            print("⚠️ 警告: Zabbix API连接不可用")
            self.connection_status['error'] = 'API实例为空'
        else:
            try:
                # 尝试进行一个简单的API调用来检验连接
                if hasattr(self.zapi, 'apiinfo'):
                    version_info = self.zapi.apiinfo.version()
                    self.connection_status['connected'] = True
                    self.connection_status['version'] = version_info
                    print(f"✓ Zabbix API连接正常，版本: {version_info}")
                else:
                    print("⚠️ 警告: Zabbix API实例无效（缺少apiinfo属性）")
                    self.connection_status['error'] = 'API实例无apiinfo属性'
            except Exception as e:
                print(f"⚠️ 警告: Zabbix API连接测试失败: {str(e)}")
                self.connection_status['error'] = str(e)
    
    def _convert_ip_range_format(self, ip_ranges):
        """
        将前端IP范围格式转换为Zabbix API支持的格式
        
        支持的输入格式:
        - 单个IP: 192.168.1.1
        - CIDR: 192.168.1.0/24
        - 完整范围: 192.168.1.1-192.168.1.254
        
        转换为Zabbix支持的格式:
        - 单个IP: 192.168.1.1
        - CIDR: 192.168.1.0/24  
        - 简化范围: 192.168.1.1-254
        """
        converted_ranges = []
        
        for ip_range in ip_ranges:
            ip_range = ip_range.strip()
            
            # 单个IP或CIDR格式，直接使用
            if '/' in ip_range or '-' not in ip_range:
                converted_ranges.append(ip_range)
                continue
            
            # 处理完整IP范围格式 (x.x.x.x-y.y.y.y)
            if '-' in ip_range:
                try:
                    start_ip, end_ip = ip_range.split('-')
                    start_ip = start_ip.strip()
                    end_ip = end_ip.strip()
                    
                    # 验证IP格式
                    import re
                    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
                    if not re.match(ip_pattern, start_ip) or not re.match(ip_pattern, end_ip):
                        print(f"[WARNING] 无效的IP范围格式: {ip_range}")
                        converted_ranges.append(ip_range)  # 保持原格式
                        continue
                    
                    # 分解IP地址
                    start_parts = start_ip.split('.')
                    end_parts = end_ip.split('.')
                    
                    # 检查是否在同一网段
                    if start_parts[:3] == end_parts[:3]:
                        # 同一网段，转换为简化格式
                        network_base = '.'.join(start_parts[:3])
                        start_host = start_parts[3]
                        end_host = end_parts[3]
                        converted_range = f"{network_base}.{start_host}-{end_host}"
                        converted_ranges.append(converted_range)
                        print(f"[INFO] IP范围格式转换: {ip_range} -> {converted_range}")
                    else:
                        # 跨网段，尝试转换为CIDR或保持原格式
                        print(f"[WARNING] 跨网段IP范围，保持原格式: {ip_range}")
                        converted_ranges.append(ip_range)
                        
                except Exception as e:
                    print(f"[ERROR] IP范围格式转换失败: {ip_range}, 错误: {e}")
                    converted_ranges.append(ip_range)  # 保持原格式
            else:
                converted_ranges.append(ip_range)
        
        return converted_ranges

    def get_connection_status(self):
        """获取连接状态信息"""
        return self.connection_status.copy()
    
    def diagnose_connection(self):
        """
        诊断Zabbix API连接问题
        
        返回:
        dict: 详细的诊断信息
        """
        diagnosis = {
            'success': False,
            'connected': False,
            'version': None,
            'error': None,
            'suggestions': [],
            'config_info': {
                'url': 'http://192.168.0.134/zabbix',
                'username': 'Admin',
                'password': '隐藏'
            }
        }
        
        # 检查基本连接
        if self.zapi is None:
            diagnosis['error'] = 'Zabbix API实例为空'
            diagnosis['suggestions'] = [
                '检查Zabbix服务器是否正常运行',
                '验证Zabbix服务器URL是否可访问: http://192.168.0.134/zabbix',
                '检查网络连接和防火墙设置',
                '验证用户名和密码是否正确',
                '检查pyzabbix库是否正确安装'
            ]
            return diagnosis
        
        # 尝试连接测试
        try:
            if hasattr(self.zapi, 'apiinfo'):
                version_info = self.zapi.apiinfo.version()
                diagnosis['success'] = True
                diagnosis['connected'] = True
                diagnosis['version'] = version_info
                diagnosis['suggestions'] = ['连接正常，可以使用Zabbix相关功能']
            else:
                diagnosis['error'] = 'Zabbix API实例无效（缺apiinfo属性）'
                diagnosis['suggestions'] = [
                    '重新安装pyzabbix库: pip install --upgrade pyzabbix',
                    '检查Zabbix服务器版本兼容性'
                ]
        except Exception as e:
            diagnosis['error'] = str(e)
            error_msg = str(e).lower()
            
            if 'connection' in error_msg or 'timeout' in error_msg:
                diagnosis['suggestions'] = [
                    '检查Zabbix服务器是否运行在 http://192.168.0.134/zabbix',
                    '验证网络连接和防火墙设置',
                    '检查Zabbix Web界面是否可访问'
                ]
            elif 'login' in error_msg or 'auth' in error_msg:
                diagnosis['suggestions'] = [
                    '检查用户名和密码是否正确 (Admin/zabbix)',
                    '确认用户账号未被禁用',
                    '检查Zabbix用户权限设置'
                ]
            else:
                diagnosis['suggestions'] = [
                    '检查Zabbix服务器日志获取更多信息',
                    '检查Zabbix API配置是否正确',
                    '尝试重启 Zabbix 服务'
                ]
        
        return diagnosis
    
    def create_discovery_rule_with_check(self, name, ip_ranges, check_type, **kwargs):
        """
        创建包含发现检查的发现规则
        
        必需参数:
        name (string): 发现规则名称
        ip_ranges (list): IP地址范围列表
        check_type (int): 检查类型（唯一必需参数）
            0 - SSH; 1 - LDAP; 2 - SMTP; 3 - FTP; 4 - HTTP; 5 - POP;
            6 - NNTP; 7 - IMAP; 8 - TCP; 9 - Zabbix agent; 10 - SNMPv1 agent;
            11 - SNMPv2 agent; 12 - ICMP ping; 13 - SNMPv3 agent; 14 - HTTPS; 15 - Telnet
        
        可选参数（所有参数都有默认值）:
        key_ (string): 查询键值或SNMP OID，默认由系统根据类型提供
        ports (string): 逗号分隔的端口范围，默认: "0"
        snmp_community (string): SNMP社区，默认: "public"
        snmpv3_* : SNMPv3相关参数，全部可选
        uniq (int): 是否作为设备唯一性标准，默认: 0
        host_source (int): 主机名称来源，默认: 1 (DNS)
        name_source (int): 可见名称来源，默认: 0 (未指定)
        delay (string): 检查间隔，默认: "1h"
        status (int): 规则状态，强制设置为 0 (启用)，不允许前端修改
        
        返回:
        dict: 创建的发现规则信息
        """
        
        # 检查API连接是否可用
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，跳过发现规则创建'
            }
        
        # 构建发现检查参数
        dcheck_params = {
            'type': check_type,
            'ports': kwargs.get('ports', '0'),
            'uniq': kwargs.get('uniq', 0),
            'host_source': kwargs.get('host_source', 1),
            'interval': kwargs.get('interval', 10),
            'name_source': kwargs.get('name_source', 0)
        }
        
        # 添加可选参数
        optional_params = [
            'key_', 'snmp_community', 'snmpv3_authpassphrase', 'snmpv3_authprotocol',
            'snmpv3_contextname', 'snmpv3_privpassphrase', 'snmpv3_privprotocol',
            'snmpv3_securitylevel', 'snmpv3_securityname'
        ]
        
        for param in optional_params:
            if param in kwargs:
                dcheck_params[param] = kwargs[param]
        
        # 验证必需参数
        self._validate_discovery_check_params(check_type, dcheck_params)
        
        # 转换IP范围格式
        if isinstance(ip_ranges, list):
            converted_ranges = self._convert_ip_range_format(ip_ranges)
        else:
            converted_ranges = self._convert_ip_range_format([str(ip_ranges)])
        
        # 构建发现规则参数
        drule_params = {
            'name': name,
            'iprange': ','.join(converted_ranges),
            'delay': kwargs.get('delay', '1h'),  # 检查间隔，默认5秒
            'status': 0,  # 强制启用状态，不允许前端控制
            'dchecks': [dcheck_params]  # 发现检查列表
        }
        
        print(f"[DEBUG] 原始IP范围: {ip_ranges}")
        print(f"[DEBUG] 转换后IP范围: {converted_ranges}")
        print(f"[DEBUG] Zabbix API参数: {drule_params}")
        
        try:
            # 创建发现规则
            result = self.zapi.drule.create(drule_params)
            druleid = result['druleids'][0] if result.get('druleids') else None
            
            if druleid:
                print(f"[DEBUG] 成功创建发现规则 ID: {druleid}")
                
                # 双重保险：检查并确保规则状态为启用
                try:
                    # 检查规则状态
                    rule_status = self.zapi.drule.get({
                        'output': ['status'],
                        'druleids': [druleid]
                    })
                    
                    if rule_status and len(rule_status) > 0:
                        current_status = int(rule_status[0].get('status', 1))
                        if current_status != 0:  # 如果不是启用状态
                            print(f"[WARNING] 发现规则 {druleid} 状态为禁用({current_status})，强制启用...")
                            # 强制启用规则
                            self.zapi.drule.update({
                                'druleid': druleid,
                                'status': 0  # 强制启用
                            })
                            print(f"[SUCCESS] 发现规则 {druleid} 已强制启用")
                        else:
                            print(f"[SUCCESS] 发现规则 {druleid} 状态正常：启用")
                    
                except Exception as status_error:
                    print(f"[WARNING] 检查规则状态失败: {status_error}")
                
                # 尝试立即触发发现检查（如果可能的话）
                try:
                    # 使用安全的方法触发立即执行：短暂修改delay
                    import time
                    print(f"[DEBUG] 尝试触发发现规则 {druleid} 的立即检查")
                    
                    # 短暂修改delay然后恢复，这会触发规则重新调度
                    current_delay = kwargs.get('delay', '1h')
                    temp_delay = '3s' if current_delay != '3s' else '4s'
                    
                    # 修改delay触发重新调度
                    self.zapi.drule.update({
                        'druleid': druleid,
                        'delay': temp_delay,
                        'status': 0  # 再次确保启用状态
                    })
                    
                    # 等待0.5秒
                    time.sleep(0.5)
                    
                    # 恢复原始delay
                    self.zapi.drule.update({
                        'druleid': druleid,
                        'delay': current_delay,
                        'status': 0  # 再次确保启用状态
                    })
                    print(f"[DEBUG] 已触发发现规则 {druleid} 的立即检查并确保启用")
                except Exception as trigger_error:
                    print(f"[WARNING] 无法立即触发发现检查: {trigger_error}")
                    # 不影响主流程，继续返回成功
            
            return {
                'success': True,
                'druleid': druleid,
                'message': f'发现规则创建成功，检查类型: {self._get_check_type_name(check_type)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'发现规则创建失败: {str(e)}'
            }
    
    def add_check_to_existing_rule(self, druleid, check_type, **kwargs):
        """
        向现有发现规则添加检查
        
        参数:
        druleid (string): 现有发现规则的 ID
        check_type (int): 检查类型
        **kwargs: 其他检查参数
        
        返回:
        dict: 操作结果
        """
        
        # 检查API连接是否可用
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，跳过添加发现检查'
            }
        
        try:
            # 先获取现有的发现规则
            existing_rule = self.zapi.drule.get({
                'output': 'extend',
                'druleids': [druleid],
                'selectDChecks': 'extend'
            })
            
            if not existing_rule:
                return {
                    'success': False,
                    'error': f'发现规则 {druleid} 不存在',
                    'message': f'发现规则 {druleid} 不存在'
                }
            
            rule = existing_rule[0]
            
            # 构建新的检查参数
            dcheck_params = {
                'type': check_type,
                'ports': kwargs.get('ports', '0'),
                'uniq': kwargs.get('uniq', 0),
                'host_source': kwargs.get('host_source', 1),
                'name_source': kwargs.get('name_source', 0)
            }
            
            # 添加可选参数
            optional_params = [
                'key_', 'snmp_community', 'snmpv3_authpassphrase', 'snmpv3_authprotocol',
                'snmpv3_contextname', 'snmpv3_privpassphrase', 'snmpv3_privprotocol',
                'snmpv3_securitylevel', 'snmpv3_securityname'
            ]
            
            for param in optional_params:
                if param in kwargs:
                    dcheck_params[param] = kwargs[param]
            
            # 验证必需参数
            self._validate_discovery_check_params(check_type, dcheck_params)
            
            # 获取现有的检查并添加新检查
            existing_dchecks = rule.get('dchecks', [])
            updated_dchecks = existing_dchecks.copy()
            updated_dchecks.append(dcheck_params)
            
            # 更新发现规则，确保保持启用状态
            update_result = self.zapi.drule.update({
                'druleid': druleid,
                'dchecks': updated_dchecks,
                'status': 0  # 明确设置为启用状态，防止被重置为禁用
            })
            
            # 双重保险：检查并确保规则状态为启用（与create方法保持一致）
            try:
                # 检查规则状态
                rule_status = self.zapi.drule.get({
                    'output': ['status'],
                    'druleids': [druleid]
                })
                
                if rule_status and len(rule_status) > 0:
                    current_status = int(rule_status[0].get('status', 1))
                    if current_status != 0:  # 如果不是启用状态
                        print(f"[WARNING] 发现规则 {druleid} 添加检查后状态为禁用({current_status})，强制启用...")
                        # 强制启用规则
                        self.zapi.drule.update({
                            'druleid': druleid,
                            'status': 0  # 强制启用
                        })
                        print(f"[SUCCESS] 发现规则 {druleid} 已强制启用")
                    else:
                        print(f"[SUCCESS] 发现规则 {druleid} 添加检查后状态正常：启用")
                
            except Exception as status_error:
                print(f"[WARNING] 添加检查后检查规则状态失败: {status_error}")
            
            return {
                'success': True,
                'druleid': druleid,
                'message': f'成功向发现规则添加{self._get_check_type_name(check_type)}检查'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'添加发现检查失败: {str(e)}'
            }
    
    def create_discovery_check(self, druleid, check_type, **kwargs):
        """
        创建Zabbix自动发现检查（兼容性方法）
        如果druleid存在则向现有规则添加检查，否则创建新规则
        
        参数:
        druleid (string): 检查所属发现规则的 ID (如果为空或不存在则创建新规则)
        check_type (int): 检查类型
        **kwargs: 其他参数
        
        返回:
        dict: 创建的发现检查信息
        """
        # 检查API连接是否可用
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，跳过发现检查创建'
            }
        
        try:
            # 如果提供了druleid，尝试向现有规则添加检查
            if druleid:
                # 检查规则是否存在
                existing_rules = self.zapi.drule.get({
                    'output': ['druleid', 'name'],
                    'druleids': [druleid]
                })
                
                if existing_rules:
                    return self.add_check_to_existing_rule(druleid, check_type, **kwargs)
            
            # 如果druleid不存在或为空，创建新的发现规则
            rule_name = kwargs.get('rule_name', f'Auto Discovery Rule - {self._get_check_type_name(check_type)}')
            ip_ranges = kwargs.get('ip_ranges', ['192.168.1.1-254'])  # 默认IP范围
            
            return self.create_discovery_rule_with_check(
                name=rule_name,
                ip_ranges=ip_ranges,
                check_type=check_type,
                **kwargs
            )
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'发现检查创建失败: {str(e)}'
            }
            
    def create_simple_discovery_check(self, check_type, ip_ranges=None, rule_name=None):
        """
        简化的发现检查创建方法，只需要type参数
        系统会自动提供合适的默认值
        
        必需参数:
        check_type (int): 检查类型 (0-15)
        
        可选参数:
        ip_ranges (list): IP范围列表，默认使用通用范围
        rule_name (string): 规则名称，默认自动生成
        
        返回:
        dict: 操作结果
        """
        
        # 检查API连接是否可用
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，跳过简化发现检查创建'
            }
        
        try:
            # 默认参数
            if ip_ranges is None:
                ip_ranges = ['192.168.1.1-254', '10.0.0.1-254', '172.16.0.1-254']
            
            # 转换IP范围格式
            if isinstance(ip_ranges, list):
                converted_ranges = self._convert_ip_range_format(ip_ranges)
            else:
                converted_ranges = self._convert_ip_range_format([str(ip_ranges)])
            
            if rule_name is None:
                rule_name = f'自动发现规则 - {self._get_check_type_name(check_type)}'
            
            print(f"[DEBUG] 简化方法 - 原始IP范围: {ip_ranges}")
            print(f"[DEBUG] 简化方法 - 转换后IP范围: {converted_ranges}")
            
            # 根据检查类型提供智能默认值
            smart_defaults = self._get_smart_defaults_for_check_type(check_type)
            
            return self.create_discovery_rule_with_check(
                name=rule_name,
                ip_ranges=converted_ranges,
                check_type=check_type,
                **smart_defaults
            )
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'简化发现检查创建失败: {str(e)}'
            }
    
    def _get_smart_defaults_for_check_type(self, check_type):
        """
        根据检查类型提供智能默认参数
        """
        defaults = {
            'delay': '1h',  # 默认检查间隔5秒
            'status': 0     # 强制启用状态，不允许前端控制
        }
        
        # 根据类型设置默认端口
        port_defaults = {
            0: '22',     # SSH
            1: '389',    # LDAP
            2: '25',     # SMTP
            3: '21',     # FTP
            4: '80',     # HTTP
            5: '110',    # POP
            6: '119',    # NNTP
            7: '143',    # IMAP
            8: '80',     # TCP
            9: '10050',  # Zabbix agent
            10: '161',   # SNMPv1
            11: '161',   # SNMPv2
            12: '0',     # ICMP ping
            13: '161',   # SNMPv3
            14: '443',   # HTTPS
            15: '23'     # Telnet
        }
        
        defaults['ports'] = port_defaults.get(check_type, '0')
        
        # 为Zabbix agent提供默认key
        if check_type == 9:
            defaults['key_'] = 'system.uname'
        
        # 为SNMP检查提供默认参数
        elif check_type in [10, 11, 13]:  # SNMP类型
            defaults['key_'] = '1.3.6.1.2.1.1.1.0'  # 系统描述OID
            
            if check_type in [10, 11]:  # SNMPv1/v2
                defaults['snmp_community'] = 'public'
            
            elif check_type == 13:  # SNMPv3
                defaults.update({
                    'snmpv3_securityname': 'zabbix',
                    'snmpv3_securitylevel': 0,  # noAuthNoPriv
                })
        
        return defaults
    
    def query_discovery_info(self, druleid=None, rule_name=None, check_type=None):
        """
        查询发现规则和检查信息
        
        参数:
        druleid (string): 发现规则ID (可选)
        rule_name (string): 规则名称模糊查询 (可选)
        check_type (int): 检查类型过滤 (可选)
        
        返回:
        dict: 详细的发现信息
        """
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，无法查询发现信息'
            }
            
        try:
            # 构建查询参数
            params = {
                'output': 'extend',
                'selectDChecks': 'extend'
            }
            
            # 根据提供的条件过滤
            if druleid:
                params['druleids'] = [druleid]
            
            # 获取所有发现规则
            rules = self.zapi.drule.get(params)
            
            if not rules:
                return {
                    'success': True,
                    'data': [],
                    'message': '未找到匹配的发现规则',
                    'count': 0
                }
            
            # 处理查询结果
            processed_rules = []
            
            for rule in rules:
                # 名称过滤
                if rule_name and rule_name.lower() not in rule.get('name', '').lower():
                    continue
                
                # 处理检查信息
                checks = rule.get('dchecks', [])
                processed_checks = []
                
                for check in checks:
                    # 类型过滤
                    if check_type is not None and int(check.get('type', -1)) != check_type:
                        continue
                    
                    processed_check = {
                        'dcheckid': check.get('dcheckid'),
                        'type': int(check.get('type', 0)),
                        'type_name': self._get_check_type_name(int(check.get('type', 0))),
                        'ports': check.get('ports', '0'),
                        'key_': check.get('key_', ''),
                        'snmp_community': check.get('snmp_community', ''),
                        'uniq': int(check.get('uniq', 0)),
                        'host_source': int(check.get('host_source', 1)),
                        'name_source': int(check.get('name_source', 0)),
                        'host_source_name': self._get_source_name(int(check.get('host_source', 1))),
                        'name_source_name': self._get_source_name(int(check.get('name_source', 0)))
                    }
                    
                    # 添加SNMPv3信息（如果有）
                    if int(check.get('type', 0)) == 13:  # SNMPv3
                        processed_check.update({
                            'snmpv3_securityname': check.get('snmpv3_securityname', ''),
                            'snmpv3_securitylevel': int(check.get('snmpv3_securitylevel', 0)),
                            'snmpv3_authprotocol': int(check.get('snmpv3_authprotocol', 0)),
                            'snmpv3_privprotocol': int(check.get('snmpv3_privprotocol', 0)),
                            'snmpv3_contextname': check.get('snmpv3_contextname', '')
                        })
                    
                    processed_checks.append(processed_check)
                
                # 如果指定了检查类型但没有匹配的检查，跳过这个规则
                if check_type is not None and not processed_checks:
                    continue
                
                processed_rule = {
                    'druleid': rule.get('druleid'),
                    'name': rule.get('name', ''),
                    'iprange': rule.get('iprange', ''),
                    'delay': rule.get('delay', '1h'),
                    'status': 0,
                    'status_name': '启用' if int(rule.get('status', 0)) == 0 else '禁用',
                    'nextcheck': rule.get('nextcheck', ''),
                    'checks_count': len(processed_checks),
                    'checks': processed_checks
                }
                
                processed_rules.append(processed_rule)
            
            return {
                'success': True,
                'data': processed_rules,
                'count': len(processed_rules),
                'message': f'成功查询到 {len(processed_rules)} 个发现规则'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'查询发现信息失败: {str(e)}'
            }
    
    def _get_source_name(self, source_code):
        """
        获取数据来源名称
        """
        source_names = {
            0: '未指定',
            1: 'DNS',
            2: 'IP',
            3: '发现值'
        }
        return source_names.get(source_code, f'未知({source_code})')
    
    def query_discovery_by_task(self, task_id):
        """
        根据IP扫描任务ID查询对应的Zabbix发现规则
        
        参数:
        task_id (string): IP扫描任务ID
        
        返回:
        dict: 查询结果
        """
        rule_name_pattern = f'IP扫描任务 - {task_id}'
        return self.query_discovery_info(rule_name=rule_name_pattern)
    
    def force_discovery_rule_execution(self, druleid):
        """
        强制触发发现规则的立即执行
        使用兼容性更好的方法，避免使用可能不支持的nextcheck参数
        
        参数:
        druleid (string): 发现规则ID
        
        返回:
        dict: 执行结果
        """
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，无法强制执行发现规则'
            }
        
        try:
            # 获取规则信息
            rule_params = {
                'output': ['druleid', 'name', 'status', 'delay'],
                'druleids': [druleid]
            }
            
            rules = self.zapi.drule.get(rule_params)
            if not rules:
                return {
                    'success': False,
                    'message': f'发现规则 {druleid} 不存在'
                }
            
            rule = rules[0]
            rule_status = int(rule.get('status', 0))
            rule_name = rule.get('name', f'规则{druleid}')
            
            if rule_status != 0:
                print(f"[WARNING] 发现规则 {druleid} ({rule_name}) 当前是禁用状态，先启用...")
                # 先启用规则
                try:
                    self.zapi.drule.update({
                        'druleid': druleid,
                        'status': 0  # 启用
                    })
                    print(f"[SUCCESS] 发现规则 {druleid} ({rule_name}) 已启用")
                except Exception as enable_error:
                    return {
                        'success': False,
                        'message': f'无法启用发现规则 {druleid}：{str(enable_error)}'
                    }
            
            # 使用安全的方法触发执行：通过重新应用规则配置
            import time
            current_time = int(time.time())
            
            try:
                # 方法1: 更新delay来触发重新调度（最兼容的方法）
                current_delay = rule.get('delay', '1h')
                print(f"[DEBUG] 尝试通过更新delay触发发现规则 {druleid} ({rule_name}) 的重新调度")
                
                # 临时修改delay然后恢复，这会触发规则重新调度
                temp_delay = '4s' if current_delay != '4s' else '1h'
                
                # 先设置临时delay
                self.zapi.drule.update({
                    'druleid': druleid,
                    'delay': temp_delay,
                    'status': 0  # 确保启用
                })
                
                # 等待0.5秒
                time.sleep(0.5)
                
                # 恢复原始delay
                self.zapi.drule.update({
                    'druleid': druleid,
                    'delay': current_delay,
                    'status': 0  # 确保启用
                })
                
                print(f"[SUCCESS] 通过delay更新成功触发发现规则 {druleid} ({rule_name}) 的重新调度")
                
                return {
                    'success': True,
                    'message': f'成功触发发现规则 {druleid} ({rule_name}) 的重新调度执行',
                    'method': 'delay_update',
                    'triggered_time': current_time
                }
                
            except Exception as delay_error:
                print(f"[WARNING] delay更新方法失败: {delay_error}")
                
                try:
                    # 方法2: 短暂禁用再启用（触发重新初始化）
                    print(f"[DEBUG] 尝试通过禁用/启用方式触发发现规则 {druleid} ({rule_name}) 重启")
                    
                    # 禁用
                    self.zapi.drule.update({
                        'druleid': druleid,
                        'status': 1  # 禁用
                    })
                    print(f"[DEBUG] 短暂禁用发现规则 {druleid} ({rule_name})")
                    
                    # 等待1秒
                    time.sleep(1)
                    
                    # 重新启用
                    self.zapi.drule.update({
                        'druleid': druleid,
                        'status': 0  # 启用
                    })
                    print(f"[SUCCESS] 重新启用发现规则 {druleid} ({rule_name})")
                    
                    return {
                        'success': True,
                        'message': f'通过重启方式成功触发发现规则 {druleid} ({rule_name}) 的重新执行',
                        'method': 'restart',
                        'triggered_time': current_time
                    }
                    
                except Exception as restart_error:
                    print(f"[WARNING] 重启方法也失败: {restart_error}")
                    
                    # 方法3: 简单地确保规则处于启用状态并返回成功
                    try:
                        self.zapi.drule.update({
                            'druleid': druleid,
                            'status': 0  # 确保启用
                        })
                        
                        return {
                            'success': True,
                            'message': f'发现规则 {druleid} ({rule_name}) 已确保处于启用状态，将按照设定的间隔自动执行',
                            'method': 'ensure_enabled',
                            'note': '由于API限制，无法强制立即执行，但规则已启用并将正常运行'
                        }
                        
                    except Exception as final_error:
                        return {
                            'success': False,
                            'message': f'无法操作发现规则 {druleid}: {str(final_error)}'
                        }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'强制执行发现规则失败: {str(e)}'
            }

    def check_discovery_rule_status(self, druleid):
        """
        检查发现规则的状态和活动情况
        
        参数:
        druleid (string): 发现规则ID
        
        返回:
        dict: 规则状态信息
        """
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，无法检查发现规则状态'
            }
        
        try:
            # 获取发现规则详细信息
            rule_params = {
                'output': 'extend',
                'druleids': [druleid],
                'selectDChecks': 'extend'
            }
            
            rules = self.zapi.drule.get(rule_params)
            if not rules:
                return {
                    'success': False,
                    'message': f'发现规则 {druleid} 不存在',
                    'rule_exists': False
                }
            
            rule = rules[0]
            
            # 检查规则状态
            rule_status = int(rule.get('status', 0))
            status_name = '启用' if rule_status == 0 else '禁用'
            
            # 获取检查配置
            checks = rule.get('dchecks', [])
            check_count = len(checks)
            
            # 检查下次执行时间
            nextcheck = rule.get('nextcheck', '')
            
            # 查询该规则下的发现主机数量
            host_params = {
                'output': 'extend',
                'druleids': [druleid]
            }
            
            discovered_hosts = self.zapi.dhost.get(host_params)
            host_count = len(discovered_hosts) if discovered_hosts else 0
            
            # 查询该规则下的发现服务数量
            service_params = {
                'output': 'extend',
                'druleids': [druleid]
            }
            
            discovered_services = self.zapi.dservice.get(service_params)
            service_count = len(discovered_services) if discovered_services else 0
            
            print(f"[DEBUG] 规则 {druleid} 状态检查结果:")
            print(f"[DEBUG] - 规则名称: {rule.get('name')}")
            print(f"[DEBUG] - 状态: {status_name} ({rule_status})")
            print(f"[DEBUG] - IP范围: {rule.get('iprange')}")
            print(f"[DEBUG] - 检查间隔: {rule.get('delay')}")
            print(f"[DEBUG] - 检查数量: {check_count}")
            print(f"[DEBUG] - 下次检查: {nextcheck}")
            print(f"[DEBUG] - 发现主机数: {host_count}")
            print(f"[DEBUG] - 发现服务数: {service_count}")
            
            return {
                'success': True,
                'rule_exists': True,
                'rule_info': {
                    'druleid': druleid,
                    'name': rule.get('name'),
                    'status': rule_status,
                    'status_name': status_name,
                    'iprange': rule.get('iprange'),
                    'delay': rule.get('delay'),
                    'nextcheck': nextcheck,
                    'check_count': check_count,
                    'checks': checks
                },
                'discovery_stats': {
                    'host_count': host_count,
                    'service_count': service_count,
                    'hosts': discovered_hosts,
                    'services': discovered_services
                },
                'message': f'规则 {druleid} 状态: {status_name}, 发现 {host_count} 个主机, {service_count} 个服务'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'检查发现规则状态失败: {str(e)}'
            }
    
    def force_enable_all_discovery_rules(self):
        """
        强制启用所有禁用的发现规则
        这个方法用于修复现有规则被错误设置为禁用状态的问题
        
        返回:
        dict: 操作结果
        """
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，无法启用发现规则'
            }
        
        try:
            # 获取所有发现规则
            rules_params = {
                'output': ['druleid', 'name', 'status'],
                'filter': {
                    'status': 1  # 只获取禁用的规则
                }
            }
            
            disabled_rules = self.zapi.drule.get(rules_params)
            
            if not disabled_rules:
                return {
                    'success': True,
                    'message': '没有找到禁用的发现规则，所有规则已经是启用状态',
                    'enabled_count': 0,
                    'total_checked': 0
                }
            
            enabled_count = 0
            failed_rules = []
            
            print(f"[INFO] 找到 {len(disabled_rules)} 个禁用的发现规则，开始启用...")
            
            for rule in disabled_rules:
                druleid = rule.get('druleid')
                rule_name = rule.get('name', '未知规则')
                
                try:
                    # 强制启用规则
                    self.zapi.drule.update({
                        'druleid': druleid,
                        'status': 0,  # 启用
                        'delay': '1h'  # 同时确保间隔为5秒
                    })
                    
                    enabled_count += 1
                    print(f"[SUCCESS] 规则 {druleid} ({rule_name}) 已启用")
                    
                except Exception as enable_error:
                    failed_rules.append({
                        'druleid': druleid,
                        'name': rule_name,
                        'error': str(enable_error)
                    })
                    print(f"[ERROR] 启用规则 {druleid} ({rule_name}) 失败: {enable_error}")
            
            result = {
                'success': enabled_count > 0,
                'enabled_count': enabled_count,
                'total_checked': len(disabled_rules),
                'failed_rules': failed_rules,
                'message': f'成功启用 {enabled_count}/{len(disabled_rules)} 个发现规则'
            }
            
            if failed_rules:
                result['message'] += f'\uff0c{len(failed_rules)}个规则启用失败'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'强制启用发现规则失败: {str(e)}'
            }

    def get_discovered_hosts(self, druleid=None, rule_name=None):
        """
        获取Zabbix自动发现的主机
        
        参数:
        druleid (string): 发现规则ID (可选)
        rule_name (string): 规则名称模糊查询 (可选)
        
        返回:
        dict: 发现的主机信息
        """
        if self.zapi is None:
            return {
                'success': False,
                'error': 'Zabbix API 连接不可用',
                'message': 'Zabbix API 连接不可用，无法获取发现的主机'
            }
        
        try:
            # 构建查询参数
            params = {
                'output': 'extend',
                'selectInterfaces': 'extend',
                'selectDRules': 'extend',
                'selectDServices': 'extend'  # 添加服务信息
            }
            
            print(f"[DEBUG] Zabbix API查询参数: {params}")
            
            # 根据提供的条件过滤
            if druleid:
                params['druleids'] = [druleid]
            
            # 获取发现的主机
            print(f"[DEBUG] 调用 Zabbix API dhost.get，参数: {params}")
            discovered_hosts = self.zapi.dhost.get(params)
            print(f"[DEBUG] Zabbix API 返回了 {len(discovered_hosts) if discovered_hosts else 0} 个主机")
            
            # 如果指定了druleid，严格过滤只属于该规则的主机
            if druleid and discovered_hosts:
                print(f"[DEBUG] 过滤前主机数量: {len(discovered_hosts)}")
                filtered_hosts = []
                for host in discovered_hosts:
                    host_druleid = host.get('druleid')
                    print(f"[DEBUG] 主机 dhostid={host.get('dhostid')} 的druleid={host_druleid}, 期望druleid={druleid}")
                    if str(host_druleid) == str(druleid):
                        filtered_hosts.append(host)
                        print(f"[DEBUG] 主机 dhostid={host.get('dhostid')} 匹配规则ID {druleid}，保留")
                    else:
                        print(f"[DEBUG] 主机 dhostid={host.get('dhostid')} 不匹配规则ID {druleid}，过滤掉")
                
                discovered_hosts = filtered_hosts
                print(f"[DEBUG] 过滤后主机数量: {len(discovered_hosts)}")
            
            # 如果获取到主机，打印原始数据结构用于调试
            if discovered_hosts:
                for idx, host in enumerate(discovered_hosts):
                    print(f"[DEBUG] 原始主机 {idx+1} 数据结构: {host}")
                    print(f"[DEBUG] 主机 {idx+1} 的所有字段: {list(host.keys())}")
                    print(f"[DEBUG] 主机 {idx+1} 的druleid: {host.get('druleid')}")
                    
                    # 专门通过dhostid查询这个主机的完整信息
                    dhostid = host.get('dhostid')
                    if dhostid:
                        try:
                            print(f"[DEBUG] 专门查询dhostid={dhostid}的详细信息")
                            detailed_host_params = {
                                'output': 'extend',
                                'dhostids': [dhostid],
                                'selectInterfaces': 'extend',
                                'selectDServices': 'extend'
                            }
                            detailed_hosts = self.zapi.dhost.get(detailed_host_params)
                            if detailed_hosts:
                                print(f"[DEBUG] dhostid={dhostid} 详细信息: {detailed_hosts[0]}")
                            else:
                                print(f"[DEBUG] dhostid={dhostid} 查询详细信息失败")
                        except Exception as detail_error:
                            print(f"[WARNING] 查询dhostid={dhostid}详细信息失败: {detail_error}")
            
            if not discovered_hosts:
                print(f"[DEBUG] dhost.get 没有返回结果，尝试使用 dservice.get")
                # 尝试使用 dservice.get 获取发现的服务
                service_params = {
                    'output': 'extend',
                    'selectDHosts': 'extend'
                }
                if druleid:
                    service_params['druleids'] = [druleid]
                
                discovered_services = self.zapi.dservice.get(service_params)
                print(f"[DEBUG] dservice.get 返回了 {len(discovered_services) if discovered_services else 0} 个服务")
                
                # 从服务中提取主机信息
                host_map = {}
                for service in discovered_services:
                    dhostid = service.get('dhostid')
                    ip = service.get('ip')
                    service_druleid = service.get('druleid')
                    
                    print(f"[DEBUG] 服务信息: dhostid={dhostid}, druleid={service_druleid}, ip={ip}")
                    
                    # 如果指定了druleid，严格过滤只属于该规则的服务
                    if druleid and str(service_druleid) != str(druleid):
                        print(f"[DEBUG] 服务 dhostid={dhostid} druleid={service_druleid} 不匹配期望的 {druleid}，跳过")
                        continue
                    
                    if dhostid and ip:
                        if dhostid not in host_map:
                            host_map[dhostid] = {
                                'dhostid': dhostid,
                                'druleid': service_druleid,
                                'status': 0,  # 服务可用认为主机在线
                                'ip_addresses': [],
                                'interfaces': []
                            }
                        
                        # 添加IP地址
                        if ip not in host_map[dhostid]['ip_addresses']:
                            host_map[dhostid]['ip_addresses'].append(ip)
                            host_map[dhostid]['interfaces'].append({
                                'ip': ip,
                                'port': service.get('port'),
                                'type': service.get('type'),
                                'dns': service.get('dns', '')
                            })
                
                discovered_hosts = list(host_map.values())
                print(f"[DEBUG] 从服务中提取到 {len(discovered_hosts)} 个主机")
            
            if not discovered_hosts:
                return {
                    'success': True,
                    'data': [],
                    'message': '未找到发现的主机',
                    'count': 0
                }
            
            # 处理发现的主机数据
            processed_hosts = []
            
            for host in discovered_hosts:
                # 获取主机接口信息
                interfaces = host.get('interfaces', [])
                ip_addresses = []
                
                print(f"[DEBUG] 处理主机: dhostid={host.get('dhostid')}, 接口数量={len(interfaces)}")
                print(f"[DEBUG] 主机完整信息: {host}")
                
                # 首先尝试从主机对象的直接字段获取IP（最可能的情况）
                direct_ip_fields = ['ip', 'ip_address', 'addr', 'host', 'dns', 'value']
                for field in direct_ip_fields:
                    field_value = host.get(field)
                    if field_value and field_value not in ip_addresses:
                        # 验证是否是有效的IP地址格式
                        import re
                        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
                        if re.match(ip_pattern, str(field_value)):
                            ip_addresses.append(field_value)
                            print(f"[DEBUG] 从主机{field}字段提取到IP: {field_value}")
                            break
                
                # 方法1: 从接口信息提取IP
                for interface in interfaces:
                    print(f"[DEBUG] 接口信息: {interface}")
                    # 尝试多种可能的IP字段名
                    ip_value = interface.get('ip') or interface.get('ip_address') or interface.get('addr') or interface.get('host')
                    if ip_value and ip_value not in ip_addresses:
                        ip_addresses.append(ip_value)
                        print(f"[DEBUG] 从接口提取到IP: {ip_value}")
                
                # 方法1.5: 从主机的dservices信息提取IP
                dservices = host.get('dservices', []) or host.get('services', [])
                for service in dservices:
                    print(f"[DEBUG] 服务信息: {service}")
                    service_ip = service.get('ip') or service.get('ip_address')
                    if service_ip and service_ip not in ip_addresses:
                        ip_addresses.append(service_ip)
                        print(f"[DEBUG] 从主机服务提取到IP: {service_ip}")
                        
                        # 更新接口信息
                        interfaces.append({
                            'ip': service_ip,
                            'port': service.get('port'),
                            'dns': service.get('dns', ''),
                            'type': service.get('type')
                        })
                
                # 方法2: 直接从主机信息获取IP
                if not ip_addresses:
                    host_ip = host.get('ip') or host.get('ip_address') or host.get('host')
                    if host_ip and host_ip not in ip_addresses:
                        ip_addresses.append(host_ip)
                        print(f"[DEBUG] 从主机信息提取到IP: {host_ip}")
                
                # 方法3: 如果还是没有IP，通过dhostid查询dservice获取IP
                if not ip_addresses and host.get('dhostid'):
                    print(f"[DEBUG] 尝试通过dhostid={host.get('dhostid')}查询dservice获取IP")
                    try:
                        dhostid = host.get('dhostid')
                        # 使用更完整的参数查询服务
                        service_params = {
                            'output': 'extend',  # 获取所有字段
                            'dhostids': [dhostid],
                            'selectDRules': 'extend'  # 同时获取发现规则信息
                        }
                        services = self.zapi.dservice.get(service_params)
                        print(f"[DEBUG] 为dhostid={dhostid}查询到{len(services) if services else 0}个服务")
                        
                        if services:
                            for svc_idx, service in enumerate(services):
                                print(f"[DEBUG] 服务 {svc_idx+1} 完整信息: {service}")
                                print(f"[DEBUG] 服务 {svc_idx+1} 所有字段: {list(service.keys())}")
                                
                                # 尝试多种字段名提取IP
                                service_ip_fields = ['ip', 'ip_address', 'addr', 'host', 'dns', 'value']
                                for field in service_ip_fields:
                                    service_ip = service.get(field)
                                    if service_ip and service_ip not in ip_addresses:
                                        # 验证IP格式
                                        import re
                                        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
                                        if re.match(ip_pattern, str(service_ip)):
                                            ip_addresses.append(service_ip)
                                            print(f"[DEBUG] 从服务{field}字段获取到IP: {service_ip}")
                                            
                                            # 同时更新接口信息
                                            interfaces.append({
                                                'ip': service_ip,
                                                'port': service.get('port'),
                                                'dns': service.get('dns', ''),
                                                'type': service.get('type'),
                                                'service_type': service.get('type')
                                            })
                                            break
                        else:
                            print(f"[DEBUG] dhostid={dhostid}没有对应的服务")
                            
                    except Exception as service_error:
                        print(f"[WARNING] 查询dservice失败: {service_error}")
                
                # 方法4: 如果仍然没有IP，尝试从发现规则信息推断
                if not ip_addresses:
                    print(f"[DEBUG] 尝试从发现规则信息推断IP")
                    druleid = host.get('druleid')
                    if druleid:
                        try:
                            rule_params = {
                                'output': ['iprange'],
                                'druleids': [druleid]
                            }
                            rules = self.zapi.drule.get(rule_params)
                            if rules and rules[0].get('iprange'):
                                iprange = rules[0]['iprange']
                                print(f"[DEBUG] 发现规则IP范围: {iprange}")
                                # 这里可以进一步解析IP范围，但通常不应该走到这一步
                        except Exception as rule_error:
                            print(f"[WARNING] 查询发现规则失败: {rule_error}")
                
                # 方法5: 最后的尝试 - 直接查询同一规则下的所有服务
                if not ip_addresses:
                    print(f"[DEBUG] 最后尝试：查询同一规则下的所有服务")
                    try:
                        dhostid = host.get('dhostid')
                        druleid = host.get('druleid')
                        
                        # 查询同一规则下的所有服务
                        if druleid:
                            rule_services_params = {
                                'output': 'extend',
                                'druleids': [druleid]
                            }
                            rule_services = self.zapi.dservice.get(rule_services_params)
                            print(f"[DEBUG] 规则{druleid}下查询到{len(rule_services) if rule_services else 0}个服务")
                            
                            # 在规则服务中查找匹配的dhostid
                            for service in rule_services:
                                service_dhostid = service.get('dhostid')
                                service_druleid = service.get('druleid')
                                print(f"[DEBUG] 检查服务: dhostid={service_dhostid}, druleid={service_druleid}, 目标dhostid={dhostid}, 目标druleid={druleid}")
                                
                                # 严格检查dhostid和druleid都匹配
                                if (service_dhostid == dhostid and str(service_druleid) == str(druleid)):
                                    print(f"[DEBUG] 在规则服务中找到匹配的服务: {service}")
                                    service_ip = service.get('ip')
                                    if service_ip and service_ip not in ip_addresses:
                                        import re
                                        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
                                        if re.match(ip_pattern, str(service_ip)):
                                            ip_addresses.append(service_ip)
                                            print(f"[DEBUG] 从规则服务获取到IP: {service_ip}")
                                            break
                                else:
                                    print(f"[DEBUG] 服务不匹配: dhostid {service_dhostid}!={dhostid} 或 druleid {service_druleid}!={druleid}")
                                            
                    except Exception as global_error:
                        print(f"[WARNING] 查询规则服务失败: {global_error}")

                print(f"[DEBUG] 主机 {host.get('dhostid')} 最终IP列表: {ip_addresses}")
                
                processed_host = {
                    'dhostid': host.get('dhostid'),
                    'druleid': host.get('druleid'),
                    'status': int(host.get('status', 0)),
                    'status_name': '在线' if int(host.get('status', 0)) == 0 else '离线',
                    'lastup': host.get('lastup', ''),
                    'lastdown': host.get('lastdown', ''),
                    'ip_addresses': ip_addresses,
                    'interfaces': interfaces
                }
                
                processed_hosts.append(processed_host)
            
            return {
                'success': True,
                'data': processed_hosts,
                'count': len(processed_hosts),
                'message': f'成功获取到 {len(processed_hosts)} 个发现的主机'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'获取发现主机失败: {str(e)}'
            }
    
    def save_discovered_ips_to_database(self, druleid=None, task_id=None, created_by=None):
        """
        将Zabbix发现的IP地址保存到IP数据库
        
        参数:
        druleid (string): 发现规则ID (可选)
        task_id (string): 扫描任务ID (可选)
        created_by (User): 创建者 (可选)
        
        返回:
        dict: 保存结果
        """
        try:
            # 动态导入模型，避免循环导入
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            from ip_management.models import IPRecord, ScanTask
            from django.utils import timezone
            
            # 获取发现的主机
            hosts_result = self.get_discovered_hosts(druleid=druleid)
            
            print(f"[DEBUG] 获取发现主机结果: {hosts_result}")
            
            if not hosts_result.get('success'):
                print(f"[ERROR] 获取发现主机失败: {hosts_result.get('message')}")
                return hosts_result
            
            discovered_hosts = hosts_result.get('data', [])
            
            print(f"[DEBUG] 发现了 {len(discovered_hosts)} 个主机")
            
            if not discovered_hosts:
                print(f"[INFO] 没有发现的主机需要保存")
                return {
                    'success': True,
                    'message': '没有发现的主机需要保存',
                    'saved_count': 0,
                    'updated_count': 0,
                    'skipped_count': 0
                }
            
            saved_count = 0
            updated_count = 0
            skipped_count = 0
            save_errors = []
            
            # 获取相关的扫描任务（如果有）
            scan_task = None
            if task_id:
                try:
                    scan_task = ScanTask.objects.get(id=task_id)
                except ScanTask.DoesNotExist:
                    pass
            
            # 遍历发现的主机
            for host_idx, host in enumerate(discovered_hosts):
                ip_addresses = host.get('ip_addresses', [])
                print(f"[DEBUG] 处理主机 {host_idx + 1}/{len(discovered_hosts)}: dhostid={host.get('dhostid')}, IP地址={ip_addresses}")
                
                for ip_address in ip_addresses:
                    if not ip_address or ip_address.strip() == '':
                        print(f"[SKIP] 空的IP地址，跳过")
                        continue
                    
                    # 清理IP地址格式
                    ip_address = ip_address.strip()
                    print(f"[DEBUG] 处理IP地址: '{ip_address}'")
                    
                    try:
                        print(f"[DEBUG] 开始处理IP {ip_address}")
                        
                        # 检查IP是否已存在
                        existing_ip = IPRecord.objects.filter(ip_address=ip_address).first()
                        print(f"[DEBUG] IP {ip_address} 查询结果: {'exists' if existing_ip else 'not exists'}")
                        
                        if existing_ip:
                            print(f"[UPDATE] IP {ip_address} 已存在，更新记录")
                            # 更新现有记录，但不修改自动发现标记和关键字段
                            if not hasattr(existing_ip, 'is_auto_discovered') or not existing_ip.is_auto_discovered:
                                existing_ip.is_auto_discovered = True
                                existing_ip.zabbix_drule_id = druleid
                            
                            existing_ip.ping_status = 'online'
                            existing_ip.last_seen = timezone.now()
                            existing_ip.status = 'active'  # 发现的IP设为在用
                            
                            # 如果没有主机名，尝试从接口信息获取
                            if not existing_ip.hostname:
                                interfaces = host.get('interfaces', [])
                                for interface in interfaces:
                                    if interface.get('ip') == ip_address and interface.get('dns'):
                                        existing_ip.hostname = interface['dns']
                                        print(f"[UPDATE] 为IP {ip_address} 设置主机名: {interface['dns']}")
                                        break
                            
                            # 设置发现来源
                            if not existing_ip.description:
                                existing_ip.description = f'Zabbix自动发现 - 规则ID: {druleid}'
                            elif 'Zabbix自动发现' not in existing_ip.description:
                                existing_ip.description += f' | Zabbix自动发现 - 规则ID: {druleid}'
                            
                            existing_ip.updated_at = timezone.now()
                            existing_ip.save()
                            updated_count += 1
                            print(f"[SUCCESS] IP {ip_address} 更新成功")
                            
                        else:
                            print(f"[CREATE] IP {ip_address} 不存在，创建新记录")
                            # 创建新记录
                            hostname = None
                            interfaces = host.get('interfaces', [])
                            for interface in interfaces:
                                if interface.get('ip') == ip_address and interface.get('dns'):
                                    hostname = interface['dns']
                                    print(f"[CREATE] 为IP {ip_address} 找到主机名: {hostname}")
                                    break
                            
                            try:
                                new_ip = IPRecord.objects.create(
                                    ip_address=ip_address,
                                    hostname=hostname,
                                    status='active',  # 发现的IP设为在用
                                    type='static',  # 默认为静态IP
                                    ping_status='online',
                                    last_seen=timezone.now(),
                                    is_auto_discovered=True,  # 标记为自动发现
                                    zabbix_drule_id=druleid,  # 记录发现规则ID
                                    description=f'Zabbix自动发现 - 规则ID: {druleid}',
                                    created_by=created_by
                                )
                                saved_count += 1
                                print(f"[SUCCESS] IP {ip_address} 创建成功，ID: {new_ip.id}")
                            except Exception as create_error:
                                error_msg = f'IP {ip_address} 创建失败: {str(create_error)}'
                                save_errors.append(error_msg)
                                skipped_count += 1
                                print(f"[ERROR] {error_msg}")
                                continue
                            
                            # 如果有扫描任务，创建扫描结果记录
                            if scan_task:
                                from ip_management.models import ScanResult
                                ScanResult.objects.get_or_create(
                                    scan_task=scan_task,
                                    ip_address=ip_address,
                                    defaults={
                                        'hostname': hostname,
                                        'status': 'online',
                                        'service_info': {
                                            'zabbix_dhostid': host.get('dhostid'),
                                            'discovery_status': host.get('status_name', 'unknown')
                                        }
                                    }
                                )
                            
                    except Exception as e:
                        error_msg = f'IP {ip_address} 保存失败: {str(e)}'
                        save_errors.append(error_msg)
                        skipped_count += 1
                        print(f"错误: {error_msg}")
            
            # 更新扫描任务状态（如果有）
            if scan_task:
                scan_task.status = 'completed'
                scan_task.completed_at = timezone.now()
                scan_task.progress = 100
                if save_errors:
                    scan_task.error_message = '; '.join(save_errors[:5])  # 只保存前5个错误
                scan_task.save()
            
            print(f"[SUMMARY] IP处理总结 - 主机数: {len(discovered_hosts)}, 新增: {saved_count}, 更新: {updated_count}, 跳过: {skipped_count}, 错误: {len(save_errors)}")
            if save_errors:
                print(f"[ERRORS] 错误列表: {save_errors}")
            
            return {
                'success': True,
                'message': f'成功处理Zabbix发现的IP地址',
                'saved_count': saved_count,
                'updated_count': updated_count,
                'skipped_count': skipped_count,
                'total_hosts': len(discovered_hosts),
                'errors': save_errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'保存发现IP到数据库失败: {str(e)}'
            }
    
    def _validate_discovery_check_params(self, check_type, params):
        """
        验证发现检查参数
        只有type是必需的，其他参数都是可选的
        """
        # 检查type参数是否在有效范围内
        valid_types = list(range(16))  # 0-15
        if check_type not in valid_types:
            raise ValueError(f"检查类型必须在0-15范围内，当前值: {check_type}")
        
        # 可选的最佳实践验证（不强制要求）
        warnings = []
        
        # Zabbix agent检查建议提供key_参数
        if check_type == 9 and 'key_' not in params:
            warnings.append("建议为Zabbix agent检查提供key_参数")
        
        # SNMP检查建议提供相应参数
        snmp_types = [10, 11, 13]  # SNMPv1, SNMPv2, SNMPv3
        if check_type in snmp_types:
            if 'key_' not in params:
                warnings.append("建议为SNMP检查提供key_参数(SNMP OID)")
            
            # SNMPv1和SNMPv2建议提供community
            if check_type in [10, 11] and 'snmp_community' not in params:
                warnings.append("建议为SNMPv1和SNMPv2检查提供snmp_community参数")
            
            # SNMPv3建议提供安全参数
            if check_type == 13 and 'snmpv3_securityname' not in params:
                warnings.append("建议为SNMPv3检查提供snmpv3_securityname参数")
        
        # 如果有警告，可以记录但不抛出异常
        if warnings:
            print(f"参数建议: {'; '.join(warnings)}")
    
    def _get_check_type_name(self, check_type):
        """
        获取检查类型名称
        """
        type_names = {
            0: 'SSH', 1: 'LDAP', 2: 'SMTP', 3: 'FTP', 4: 'HTTP', 5: 'POP',
            6: 'NNTP', 7: 'IMAP', 8: 'TCP', 9: 'Zabbix agent', 10: 'SNMPv1 agent',
            11: 'SNMPv2 agent', 12: 'ICMP ping', 13: 'SNMPv3 agent', 14: 'HTTPS', 15: 'Telnet'
        }
        return type_names.get(check_type, f'未知类型({check_type})')
    
    def get_discovery_checks(self, druleid=None, dcheckid=None):
        """
        获取发现检查信息
        
        参数:
        druleid (string): 发现规则ID (可选)
        dcheckid (string): 发现检查ID (可选)
        
        返回:
        dict: 发现检查信息
        """
        try:
            if druleid:
                # 获取特定发现规则的检查
                params = {
                    'output': 'extend',
                    'druleids': [druleid],
                    'selectDChecks': 'extend'
                }
                result = self.zapi.drule.get(params)
                
                # 提取所有检查
                all_checks = []
                for rule in result:
                    if 'dchecks' in rule:
                        for check in rule['dchecks']:
                            check['druleid'] = rule['druleid']
                            check['rule_name'] = rule.get('name', '')
                            all_checks.append(check)
                
                return {
                    'success': True,
                    'data': all_checks,
                    'count': len(all_checks)
                }
            else:
                # 获取所有发现规则及其检查
                params = {
                    'output': 'extend',
                    'selectDChecks': 'extend'
                }
                result = self.zapi.drule.get(params)
                
                # 提取所有检查
                all_checks = []
                for rule in result:
                    if 'dchecks' in rule:
                        for check in rule['dchecks']:
                            check['druleid'] = rule['druleid']
                            check['rule_name'] = rule.get('name', '')
                            all_checks.append(check)
                
                return {
                    'success': True,
                    'data': all_checks,
                    'count': len(all_checks)
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'获取发现检查失败: {str(e)}'
            }
    
    def get_discovery_rules(self, druleid=None):
        """
        获取发现规则信息
        
        参数:
        druleid (string): 发现规则ID (可选)
        
        返回:
        dict: 发现规则信息
        """
        try:
            params = {
                'output': 'extend',
                'selectDChecks': 'extend'
            }
            
            if druleid:
                params['druleids'] = [druleid]
            
            result = self.zapi.drule.get(params)
            return {
                'success': True,
                'data': result,
                'count': len(result)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'获取发现规则失败: {str(e)}'
            }
    
    def zabbix_auto_discovery(self):
        """原有的自动发现方法"""
        hosts = self.zapi.host.get(output=["hostid", "host", "name"],
                              selectInterfaces=["interfaceid", "ip", "dns", "useip", "port"],
                              selectGroups=["groupid", "name"],
                              selectParentTemplates=["templateid", "name"],
                              selectItems=[]
        )
        return hosts
    
    def get_templates(self, search_name=None):
        """
        获取Zabbix监控模板列表
        
        参数:
        search_name (string): 搜索模板名称 (可选)
        
        返回:
        dict: 模板列表信息
        """
        try:
            if self.zapi is None:
                return {
                    'success': False,
                    'error': 'Zabbix API连接不可用',
                    'message': 'Zabbix API连接不可用，无法获取模板列表'
                }
            
            params = {
                'output': ['templateid', 'name', 'description'],
                'selectGroups': ['groupid', 'name'],
                'selectMacros': 'count',
                'selectItems': 'count',
                'selectTriggers': 'count'
            }
            
            if search_name:
                params['search'] = {'name': search_name}
                params['searchWildcardsEnabled'] = True
            
            templates = self.zapi.template.get(params)
            
            # 处理模板数据，添加额外信息
            processed_templates = []
            for template in templates:
                processed_template = {
                    'templateid': template['templateid'],
                    'name': template['name'],
                    'description': template.get('description', ''),
                    'groups': template.get('groups', []),
                    'items_count': template.get('items', 0) if isinstance(template.get('items'), int) else len(template.get('items', [])),
                    'triggers_count': template.get('triggers', 0) if isinstance(template.get('triggers'), int) else len(template.get('triggers', [])),
                    'macros_count': template.get('macros', 0) if isinstance(template.get('macros'), int) else len(template.get('macros', [])),
                    'icon': self._get_template_icon(template['name']),  # 根据模板名称确定图标
                    'category': self._get_template_category(template['name'])  # 根据模板名称确定分类
                }
                # 移除了未定义的logger和category变量的使用
                # logger.info(category)
                processed_templates.append(processed_template)
            
            # 按名称排序
            processed_templates.sort(key=lambda x: x['name'])
            
            return {
                'success': True,
                'data': processed_templates,
                'count': len(processed_templates)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'获取模板列表失败: {str(e)}'
            }
    
    def _get_template_icon(self, template_name):
        """根据模板名称确定图标"""
        template_name_lower = template_name.lower()
        
        icon_mapping = {
            # 操作系统
            'linux': 'desktop',
            'windows': 'windows',
            'ubuntu': 'desktop', 
            'centos': 'desktop',
            'debian': 'desktop',
            'unix': 'desktop',
            'macos': 'laptop',
            
            # 数据库
            'mysql': 'database',
            'postgresql': 'database',
            'mongodb': 'database',
            'redis': 'database',
            'oracle': 'database',
            'mariadb': 'database',
            'elasticsearch': 'search',
            
            # Web服务器
            'nginx': 'global',
            'apache': 'global',
            'tomcat': 'fire',
            'iis': 'windows',
            'lighttpd': 'global',
            
            # 容器和编排
            'docker': 'container',
            'kubernetes': 'cluster',
            'openshift': 'cluster',
            'k8s': 'cluster',
            
            # 网络设备
            'cisco': 'router',
            'huawei': 'router',
            'juniper': 'router',
            'switch': 'partition',
            'router': 'router',
            'firewall': 'safety',
            'network': 'wifi',
            
            # 虚拟化
            'vmware': 'cloud',
            'hyper-v': 'cloud',
            'kvm': 'cloud',
            'xen': 'cloud',
            'virtualbox': 'cloud',
            
            # 监控协议
            'snmp': 'api',
            'icmp': 'thunderbolt',
            'tcp': 'link',
            'udp': 'link',
            'ssh': 'key',
            'telnet': 'console-sql',
            
            # 应用服务
            'java': 'coffee',
            'python': 'code',
            'node': 'node-index',
            'php': 'file-text',
            'dotnet': 'dot-chart',
            
            # 存储
            'storage': 'inbox',
            'disk': 'hdd',
            'nas': 'folder',
            'san': 'cloud-server',
            
            # 消息队列
            'rabbitmq': 'message',
            'kafka': 'deployment-unit',
            'activemq': 'message',
            
            # 缓存
            'memcached': 'dashboard',
            'varnish': 'dashboard'
        }
        
        for keyword, icon in icon_mapping.items():
            if keyword in template_name_lower:
                return icon
        
        return 'setting'  # 默认图标
    
    def _get_template_category(self, template_name):
        """根据模板名称确定分类"""
        template_name_lower = template_name.lower()
        
        category_mapping = {
            # 操作系统
            ('linux', 'windows', 'unix', 'centos', 'ubuntu', 'debian', 'rhel', 'suse', 'macos', 'freebsd'): '💻 操作系统',
            
            # 数据库
            ('mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'mariadb', 'sqlite', 'cassandra', 'elasticsearch', 'influxdb'): '🗄 数据库',
            
            # Web服务器
            ('nginx', 'apache', 'tomcat', 'iis', 'lighttpd', 'caddy', 'haproxy'): '🌐 Web服务器',
            
            # 容器和编排
            ('docker', 'kubernetes', 'openshift', 'k8s', 'containerd', 'podman'): '📦 容器平台',
            
            # 网络设备
            ('cisco', 'huawei', 'juniper', 'switch', 'router', 'firewall', 'f5', 'netscaler', 'palo alto'): '🌐 网络设备',
            
            # 虚拟化
            ('vmware', 'hyper-v', 'kvm', 'xen', 'virtualbox', 'esxi', 'vcenter'): '☁️ 虚拟化',
            
            # 网络监控
            ('snmp', 'icmp', 'tcp', 'udp', 'ping', 'ssh', 'telnet', 'ftp'): '📊 网络监控',
            
            # 云服务
            ('aws', 'azure', 'gcp', 'alibaba cloud', 'tencent cloud', 's3', 'ec2', 'rds'): '☁️ 云服务',
            
            # 应用服务
            ('java', 'python', 'node', 'php', 'dotnet', '.net', 'golang', 'jvm'): '🚀 应用服务',
            
            # 消息队列
            ('rabbitmq', 'kafka', 'activemq', 'rocketmq', 'pulsar', 'mqtt'): '📬 消息队列',
            
            # 缓存系统
            ('memcached', 'varnish', 'squid', 'cloudflare'): '⚡ 缓存系统',
            
            # 存储系统
            ('storage', 'disk', 'nas', 'san', 'ceph', 'glusterfs', 'nfs'): '💾 存储系统',
            
            # 安全监控
            ('security', 'ids', 'ips', 'antivirus', 'malware', 'vulnerability'): '🔒 安全监控',
            
            # IoT设备
            ('iot', 'sensor', 'mqtt', 'zigbee', 'lora'): '🌡️ IoT设备'
        }
        
        for keywords, category in category_mapping.items():
            if any(keyword in template_name_lower for keyword in keywords):
                return category
        
        return '📝 其他'  # 默认分类
    
    def create_host_with_template(self, host_name, ip_address, template_ids, group_ids=None):
        """
        创建主机并关联模板
        
        参数:
        host_name (string): 主机名称
        ip_address (string): IP地址
        template_ids (list): 模板ID列表
        group_ids (list): 主机组ID列表 (可选，默认使用"Linux servers"组)
        
        返回:
        dict: 创建结果
        """
        try:
            if self.zapi is None:
                return {
                    'success': False,
                    'error': 'Zabbix API连接不可用',
                    'message': 'Zabbix API连接不可用，无法创建主机'
                }
            
            # 如果没有指定主机组，使用默认的"Linux servers"组
            if not group_ids:
                try:
                    # 查找默认主机组
                    groups = self.zapi.hostgroup.get({
                        'output': ['groupid', 'name'],
                        'filter': {'name': ['Linux servers', 'Templates']}
                    })
                    
                    if groups:
                        group_ids = [groups[0]['groupid']]
                    else:
                        # 如果找不到默认组，创建一个
                        new_group = self.zapi.hostgroup.create({
                            'name': 'Auto Monitoring'
                        })
                        group_ids = [new_group['groupids'][0]]
                        
                except Exception as e:
                    print(f"获取或创建主机组失败: {e}，使用默认组ID 1")
                    group_ids = ['1']  # 使用默认组ID
            
            # 检查主机是否已存在
            existing_hosts = self.zapi.host.get({
                'output': ['hostid', 'host'],
                'filter': {'host': [host_name]}
            })
            
            if existing_hosts:
                return {
                    'success': False,
                    'error': 'HOST_ALREADY_EXISTS',
                    'message': f'主机 {host_name} 已存在',
                    'hostid': existing_hosts[0]['hostid']
                }
            
            # 准备模板列表
            templates = []
            for template_id in template_ids:
                templates.append({'templateid': template_id})
            
            # 准备主机组列表
            groups = []
            for group_id in group_ids:
                groups.append({'groupid': group_id})
            
            # 创建主机
            host_params = {
                'host': host_name,
                'name': host_name,  # 可见名称
                'interfaces': [{
                    'type': 1,  # Agent接口
                    'main': 1,
                    'useip': 1,
                    'ip': ip_address,
                    'dns': '',
                    'port': '10050'
                }],
                'groups': groups,
                'templates': templates
            }
            
            result = self.zapi.host.create(host_params)
            
            if result and 'hostids' in result:
                hostid = result['hostids'][0]
                return {
                    'success': True,
                    'message': f'主机 {host_name} 创建成功',
                    'hostid': hostid,
                    'host_name': host_name,
                    'ip_address': ip_address,
                    'template_count': len(template_ids)
                }
            else:
                return {
                    'success': False,
                    'error': 'CREATE_FAILED',
                    'message': '主机创建失败：未返回主机ID'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'创建主机失败: {str(e)}'
            }
    
    def get_host_groups(self):
        """
        获取主机组列表
        
        返回:
        dict: 主机组列表
        """
        try:
            if self.zapi is None:
                return {
                    'success': False,
                    'error': 'Zabbix API连接不可用',
                    'message': 'Zabbix API连接不可用，无法获取主机组列表'
                }
            
            groups = self.zapi.hostgroup.get({
                'output': ['groupid', 'name'],
                'selectHosts': 'count'
            })
            
            return {
                'success': True,
                'data': groups,
                'count': len(groups)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'获取主机组列表失败: {str(e)}'
            }