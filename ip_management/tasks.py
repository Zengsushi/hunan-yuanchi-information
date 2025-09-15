import time
import threading
import logging
from django.utils import timezone
from django.conf import settings
from .models import ScanTask, IPRecord, ScanResult
from .ip_scanner import NetworkScanner, ScanResult as ScannerResult
import json

logger = logging.getLogger(__name__)

class PythonScanTaskManager:
    """纯Python扫描任务管理器 - 替代Zabbix自动发现"""
    
    def __init__(self):
        self.running_tasks = {}  # 存储正在运行的任务
        self.max_concurrent = 100  # 默认并发数
        self.timeout = 3.0  # 默认超时时间
        
    def add_task(self, task_id, scan_config=None):
        """添加任务到处理队列"""
        if task_id in self.running_tasks:
            logger.warning(f"任务 {task_id} 已在处理队列中")
            return
            
        logger.info(f"添加Python扫描任务 {task_id} 到处理队列")
        
        # 启动异步线程处理任务
        thread = threading.Thread(
            target=self._process_scan_task,
            args=(task_id, scan_config or {}),
            daemon=True
        )
        
        self.running_tasks[task_id] = {
            'thread': thread,
            'start_time': timezone.now(),
            'scanner': None
        }
        
        thread.start()
        
    def _process_scan_task(self, task_id, scan_config):
        """处理单个扫描任务"""
        try:
            task = ScanTask.objects.get(id=task_id)
            
            # 更新任务状态为运行中
            task.status = 'running'
            task.started_at = timezone.now()
            task.progress = 5
            task.save()
            
            logger.info(f"开始Python扫描任务 {task_id}")
            
            # 创建扫描器
            scanner = NetworkScanner(
                max_concurrent=scan_config.get('max_concurrent', self.max_concurrent),
                timeout=scan_config.get('timeout', self.timeout),
                ping_timeout=scan_config.get('ping_timeout', 1.0)
            )
            
            # 保存扫描器实例用于可能的取消操作
            self.running_tasks[task_id]['scanner'] = scanner
            
            # 添加进度回调
            def progress_callback(data):
                if task_id not in self.running_tasks:
                    return  # 任务已被停止
                    
                try:
                    # 更新进度 (5% 起始 + 85% 扫描进度)
                    progress = 5 + int(data['percentage'] * 0.85)
                    task.progress = min(progress, 90)
                    task.save(update_fields=['progress'])
                    
                    # 记录发现的在线主机
                    if data.get('result') and data['result'].status == 'online':
                        logger.info(f"任务 {task_id} 发现在线主机: {data['result'].ip_address}")
                except Exception as e:
                    logger.error(f"任务 {task_id} 进度回调失败: {e}")
            
            scanner.add_progress_callback(progress_callback)
            
            # 解析扫描参数
            ip_ranges = task.ip_ranges or []
            if isinstance(ip_ranges, str):
                ip_ranges = [ip_ranges]
            
            # 根据检查类型确定扫描模式
            scan_mode = self._get_scan_mode(task.check_type)
            ports = self._parse_ports(task.ports, task.check_type)
            
            logger.info(f"任务 {task_id} 扫描参数: IP范围={ip_ranges}, 模式={scan_mode}, 端口={ports}")
            
            # 执行扫描
            if scan_mode == 'ping_only':
                results = scanner.scan_network(ip_ranges, ping_only=True)
            else:
                results = scanner.scan_network(ip_ranges, ports=ports)
            
            # 检查任务是否被停止
            if task_id not in self.running_tasks:
                logger.info(f"任务 {task_id} 已被停止，终止处理")
                return
            
            # 保存扫描结果到数据库
            task.progress = 90
            task.save(update_fields=['progress'])
            
            saved_count = self._save_scan_results(task, results)
            
            # 任务完成
            task.status = 'completed'
            task.progress = 100
            task.completed_at = timezone.now()
            
            # 生成结果统计
            stats = scanner.get_stats()
            online_count = len([r for r in results if r.status == 'online'])
            
            # 处理stats中的datetime对象，转换为可JSON序列化的格式
            serializable_stats = {}
            for key, value in stats.items():
                if key in ['start_time', 'end_time'] and value:
                    # 将datetime对象转换为ISO格式字符串
                    serializable_stats[key] = value.isoformat()
                else:
                    serializable_stats[key] = value
            
            task.result_data = {
                'total_scanned': len(results),
                'online_hosts': online_count,
                'offline_hosts': len(results) - online_count,
                'saved_to_db': saved_count,
                'duration': stats.get('duration', 0),
                'scan_stats': serializable_stats
            }
            task.save()
            
            logger.info(f"任务 {task_id} 完成: 扫描 {len(results)} 个IP, 发现 {online_count} 个在线, 保存 {saved_count} 条记录")
            
        except ScanTask.DoesNotExist:
            logger.error(f"任务 {task_id} 不存在")
        except Exception as e:
            logger.error(f"任务 {task_id} 处理失败: {str(e)}")
            try:
                task = ScanTask.objects.get(id=task_id)
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = timezone.now()
                task.save()
            except Exception:
                pass
        finally:
            # 清理任务
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    def _get_scan_mode(self, check_type):
        """根据检查类型确定扫描模式"""
        # ICMP ping 只做ping扫描
        if check_type == 12:
            return 'ping_only'
        else:
            return 'comprehensive'
    
    def _parse_ports(self, ports_str, check_type):
        """解析端口配置"""
        if not ports_str or ports_str == '0':
            # 根据检查类型返回默认端口
            default_ports = {
                0: [22],        # SSH
                1: [389, 636], # LDAP
                2: [25],       # SMTP  
                3: [21],       # FTP
                4: [80],       # HTTP
                5: [110],      # POP3
                6: [119],      # NNTP
                7: [143],      # IMAP
                8: [80],       # TCP
                9: [10050],    # Zabbix agent
                10: [161],     # SNMPv1
                11: [161],     # SNMPv2
                12: [],        # ICMP (无端口)
                13: [161],     # SNMPv3
                14: [443],     # HTTPS
                15: [23]       # Telnet
            }
            return default_ports.get(check_type, [80, 443, 22, 21, 25])
        
        # 解析端口字符串
        ports = []
        try:
            for part in ports_str.split(','):
                part = part.strip()
                if '-' in part:
                    # 端口范围
                    start, end = map(int, part.split('-'))
                    ports.extend(range(start, end + 1))
                else:
                    # 单个端口
                    ports.append(int(part))
        except Exception as e:
            logger.error(f"解析端口字符串失败 '{ports_str}': {e}")
            return [80]  # 默认端口
        
        return ports
    
    def _save_scan_results(self, task, scan_results):
        """保存扫描结果到数据库"""
        saved_count = 0
        
        try:
            # 清理旧的扫描结果
            ScanResult.objects.filter(scan_task=task).delete()
            
            # 批量创建新结果
            scan_result_objects = []
            ip_record_objects = []
            
            for result in scan_results:
                # 创建扫描结果记录
                scan_result_obj = ScanResult(
                    scan_task=task,
                    ip_address=result.ip_address,
                    hostname=result.hostname,
                    mac_address=result.mac_address,
                    status=result.status,
                    response_time=result.response_time,
                    service_info={
                        'open_ports': result.open_ports,
                        'services': result.services,
                        'os_info': result.os_info
                    }
                )
                scan_result_objects.append(scan_result_obj)
                
                # 只为在线主机创建或更新IP记录
                if result.status == 'online':
                    try:
                        # 检查IP是否已存在
                        ip_record, created = IPRecord.objects.get_or_create(
                            ip_address=result.ip_address,
                            defaults={
                                'hostname': result.hostname,
                                'status': 'active',
                                'type': 'static',
                                'ping_status': 'online',
                                'last_seen': timezone.now(),
                                'description': f'Python扫描发现 - 任务ID: {task.id}',
                                'created_by': task.created_by
                            }
                        )
                        
                        if not created:
                            # 更新现有记录
                            ip_record.ping_status = 'online'
                            ip_record.last_seen = timezone.now()
                            if result.hostname and not ip_record.hostname:
                                ip_record.hostname = result.hostname
                            if not ip_record.description or 'Python扫描' not in ip_record.description:
                                ip_record.description = f'Python扫描发现 - 任务ID: {task.id}'
                            ip_record.save()
                        
                        saved_count += 1
                        
                    except Exception as e:
                        logger.error(f"保存IP记录失败 {result.ip_address}: {e}")
            
            # 批量保存扫描结果
            ScanResult.objects.bulk_create(scan_result_objects)
            
        except Exception as e:
            logger.error(f"保存扫描结果失败: {e}")
        
        return saved_count
    
    def stop_task(self, task_id):
        """停止正在运行的任务"""
        if task_id not in self.running_tasks:
            return False
        
        logger.info(f"正在停止任务 {task_id}")
        
        try:
            # 更新任务状态
            task = ScanTask.objects.get(id=task_id)
            task.status = 'cancelled'
            task.completed_at = timezone.now()
            task.save()
            
            # 从运行队列中移除
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            logger.info(f"任务 {task_id} 已停止")
            return True
            
        except Exception as e:
            logger.error(f"停止任务 {task_id} 失败: {e}")
            return False
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        if task_id in self.running_tasks:
            task_info = self.running_tasks[task_id]
            return {
                'status': 'running',
                'start_time': task_info['start_time'],
                'duration': (timezone.now() - task_info['start_time']).total_seconds()
            }
        return None
    
    def get_running_tasks(self):
        """获取所有运行中的任务"""
        return list(self.running_tasks.keys())


# 全局任务管理器实例
task_manager = PythonScanTaskManager()


# 兼容性函数，保持API不变
def create_scan_task(task_id, config=None):
    """创建扫描任务（兼容性函数）"""
    return task_manager.add_task(task_id, config)


def stop_scan_task(task_id):
    """停止扫描任务（兼容性函数）"""
    return task_manager.stop_task(task_id)