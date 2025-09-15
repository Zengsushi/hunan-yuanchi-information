from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
import uuid
import logging
import subprocess
import time
import platform
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
# 导入Zabbix自动发现模块
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ops_assets_backend'))
from ops_assets_backend.zabbix_api import zabbix_auto_discovery

from .models import IPRecord, ScanTask, ScanResult
from .serializers import (
    IPRecordSerializer, ScanTaskCreateSerializer, ScanTaskSerializer,
    ScanResultSerializer
)
import logging
logger = logging.getLogger(__name__)


class IPRecordPagination(PageNumberPagination):
    """
    自定义分页类，支持动态page_size参数
    """
    page_size = 10  # 默认页面大小
    page_size_query_param = 'page_size'  # URL参数名
    max_page_size = 200  # 最大页面大小
    
    def get_page_size(self, request):
        """
        获取页面大小，支持从请求参数中读取
        """
        logger.info(f"分页处理: 请求参数 = {dict(request.query_params)}")
        
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                logger.info(f"从请求中获取到 page_size = {page_size}")
                if page_size > 0:
                    final_page_size = min(page_size, self.max_page_size)
                    logger.info(f"最终使用的 page_size = {final_page_size}")
                    return final_page_size
            except (KeyError, ValueError) as e:
                logger.info(f"读取 page_size 参数失败: {e}，使用默认值 {self.page_size}")
                pass
        
        logger.info(f"使用默认 page_size = {self.page_size}")
        return self.page_size


class IPRecordViewSet(viewsets.ModelViewSet):
    """IP记录管理视图集"""
    
    queryset = IPRecord.objects.all()
    serializer_class = IPRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = IPRecordPagination  # 使用自定义分页类
    
    def perform_create(self, serializer):
        """创建IP记录时设置创建者"""
        serializer.save(created_by=self.request.user)
    
    def get_queryset(self):
        """获取查询集，支持筛选"""
        queryset = IPRecord.objects.all().order_by('ip_address')
        
        # 搜索筛选（IP地址或主机名）
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(ip_address__icontains=search) | 
                Q(hostname__icontains=search)
            )
        
        # 状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 类型筛选
        type_filter = self.request.query_params.get('type')
        if type_filter:
            queryset = queryset.filter(type=type_filter)
        
        return queryset
    
    def update(self, request, *args, **kwargs):
        """
        更新IP记录，对自动发现的IP提供保护机制
        """
        try:
            instance = self.get_object()
            
            # 检查是否是自动发现的IP
            if instance.is_auto_discovered:
                # 检查请求中是否包含被保护的字段
                protected_fields = {
                    'ip_address', 'hostname', 'type', 'mac_address', 
                    'device', 'subnet', 'ping_status', 'last_seen',
                    'is_auto_discovered', 'zabbix_drule_id'
                }
                
                attempted_fields = set(request.data.keys())
                blocked_fields = attempted_fields.intersection(protected_fields)
                
                if blocked_fields:
                    return Response({
                        'code': 403,
                        'message': f'不允许修改Zabbix自动发现的IP地址的以下字段：{list(blocked_fields)}',
                        'data': {
                            'ip_address': instance.ip_address,
                            'is_auto_discovered': True,
                            'blocked_fields': list(blocked_fields),
                            'allowed_fields': ['description', 'status'],
                            'protection_reason': 'Zabbix自动发现的IP地址只能修改部分字段'
                        }
                    }, status=status.HTTP_403_FORBIDDEN)
            
            # 执行正常更新
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # 检查是否有被保护的字段被尝试修改
            protected_fields_attempted = getattr(request, '_protected_fields_attempted', [])
            
            response_data = {
                'code': 200,
                'message': 'IP记录更新成功',
                'data': serializer.data
            }
            
            if protected_fields_attempted:
                response_data['warning'] = f'以下字段因保护机制未被修改：{protected_fields_attempted}'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"更新IP记录失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'更新IP记录失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='check-deletion-impact')
    def check_deletion_impact(self, request, pk=None):
        """检查删除IP的影响范围"""
        try:
            ip_record = self.get_object()
            related_data = self._check_related_data(ip_record)
            
            # 构建删除影响报告
            impact_report = {
                'ip_address': ip_record.ip_address,
                'hostname': ip_record.hostname,
                'is_auto_discovered': ip_record.is_auto_discovered,
                'zabbix_drule_id': ip_record.zabbix_drule_id,
                'scan_results_count': related_data['scan_results_count'],
                'related_tasks': related_data['related_tasks'],
                'will_cleanup_zabbix': ip_record.is_auto_discovered and ip_record.zabbix_drule_id is not None,
                'deletion_warnings': self._generate_deletion_warnings(ip_record, related_data)
            }
            
            return Response({
                'code': 200,
                'message': '获取删除影响评估成功',
                'data': impact_report
            })
            
        except Exception as e:
            logger.error(f"检查删除影响失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'检查删除影响失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_deletion_warnings(self, ip_record, related_data):
        """生成删除警告信息"""
        warnings = []
        
        # IP记录警告
        if ip_record.is_auto_discovered:
            warnings.append(f"⚠️ 将永久性删除自动发现的IP地址 {ip_record.ip_address} 的所有信息")
        else:
            warnings.append(f"将永久性删除IP地址 {ip_record.ip_address} 的所有信息")
        
        # 扫描结果警告
        if related_data['scan_results_count'] > 0:
            warnings.append(f"将删除 {related_data['scan_results_count']} 条相关的扫描结果记录")
            
        # 相关任务警告
        if related_data['related_tasks']:
            task_names = [task['task_name'] for task in related_data['related_tasks']]
            warnings.append(f"将从以下扫描任务中删除相关记录: {', '.join(task_names)}")
        
        # Zabbix警告 - 更加详细和明确
        if ip_record.is_auto_discovered:
            warnings.append("⚠️ 特别警告：此IP为Zabbix自动发现，删除后可能影响监控系统的正常运行")
            
            if ip_record.zabbix_drule_id:
                warnings.append(f"将自动从 Zabbix 监控系统中删除相关主机记录（规则ID: {ip_record.zabbix_drule_id}）")
                warnings.append("• 将查找Zabbix中以此IP为主机名或接口IP的主机")
                warnings.append("• 找到的主机将被自动删除，包括所有监控项和历史数据")
                warnings.append("• 如果此主机正在被监控，将丢失所有监控配置和报警设置")
            else:
                warnings.append("此IP为自动发现，但未关联Zabbix规则，建议手动检查Zabbix中是否存在相关主机")
            
            warnings.append("⚠️ 强烈建议：删除前请确认此IP不再需要监控，否则可能导致监控盲区")
        
        return warnings

    def destroy(self, request, *args, **kwargs):
        """删除IP记录及相关数据（包括自动发现的IP）"""
        try:
            instance = self.get_object()
            ip_address = instance.ip_address
            
            logger.info(f"开始删除IP记录: {ip_address}, 自动发现: {instance.is_auto_discovered}")
            
            # 检查相关数据
            related_data = self._check_related_data(instance)
            
            # 如果是自动发现的IP，尝试从Zabbix中删除相关主机
            zabbix_cleanup_result = None
            if instance.is_auto_discovered:
                logger.info(f"检测到自动发现的IP，将尝试清理Zabbix数据: {ip_address}")
                zabbix_cleanup_result = self._cleanup_zabbix_data(instance)
            
            # 删除相关的扫描结果
            deleted_scan_results = self._cleanup_scan_results(ip_address)
            
            # 删除IP记录
            self.perform_destroy(instance)
            
            # 构建删除结果消息
            cleanup_summary = {
                'ip_address': ip_address,
                'scan_results_deleted': deleted_scan_results,
                'zabbix_cleanup': zabbix_cleanup_result,
                'related_tasks': related_data['related_tasks'],
                'was_auto_discovered': instance.is_auto_discovered
            }
            
            success_message = f'IP记录 {ip_address} 及相关数据已成功删除'
            if instance.is_auto_discovered:
                success_message += ' (包括Zabbix自动发现数据)'
            
            logger.info(f"删除完成: {cleanup_summary}")
            
            return Response({
                'code': 200,
                'message': success_message,
                'data': cleanup_summary
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"删除IP记录失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'删除IP记录失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _check_related_data(self, ip_record):
        """检查IP记录的相关数据"""
        ip_address = ip_record.ip_address
        
        # 检查扫描结果
        scan_results = ScanResult.objects.filter(ip_address=ip_address)
        scan_results_count = scan_results.count()
        
        # 检查相关的扫描任务
        related_tasks = []
        for result in scan_results:
            task_info = {
                'task_id': str(result.scan_task.id),
                'task_name': result.scan_task.task_name or '未命名任务',
                'created_at': result.scan_task.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            if task_info not in related_tasks:
                related_tasks.append(task_info)
        
        return {
            'scan_results_count': scan_results_count,
            'related_tasks': related_tasks,
            'is_auto_discovered': ip_record.is_auto_discovered,
            'zabbix_drule_id': ip_record.zabbix_drule_id
        }
    
    def _cleanup_scan_results(self, ip_address):
        """清理扫描结果数据"""
        try:
            deleted_count = ScanResult.objects.filter(ip_address=ip_address).delete()[0]
            logger.info(f"删除了 {deleted_count} 条扫描结果记录，IP: {ip_address}")
            return deleted_count
        except Exception as e:
            logger.error(f"清理扫描结果失败: {str(e)}")
            return 0
    
    def _cleanup_zabbix_data(self, ip_record):
        """清理Zabbix相关数据"""
        try:
            # 导入Zabbix API
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ops_assets_backend'))
            from ops_assets_backend.zabbix_api import zabbix_auto_discovery
            
            zabbix_discovery = zabbix_auto_discovery()
            
            if not zabbix_discovery.connection_status.get('connected'):
                logger.warning(f"Zabbix API连接不可用，跳过Zabbix数据清理")
                return {
                    'success': False,
                    'message': 'Zabbix API连接不可用，无法清理Zabbix数据',
                    'skipped': True
                }
            
            # 尝试查找并删除Zabbix中的主机
            cleanup_result = self._remove_zabbix_host(zabbix_discovery, ip_record.ip_address)
            
            return cleanup_result
            
        except Exception as e:
            logger.error(f"Zabbix数据清理失败: {str(e)}")
            return {
                'success': False,
                'message': f'Zabbix数据清理失败: {str(e)}',
                'error': str(e)
            }
    
    def _remove_zabbix_host(self, zabbix_discovery, ip_address):
        """从Zabbix中删除主机"""
        try:
            # 查找主机
            hosts = zabbix_discovery.zapi.host.get({
                'filter': {'host': ip_address},
                'output': ['hostid', 'host', 'name']
            })
            
            if not hosts:
                # 尝试通过接口IP查找
                hosts = zabbix_discovery.zapi.host.get({
                    'selectInterfaces': ['ip'],
                    'filter': {'interfaces': {'ip': ip_address}},
                    'output': ['hostid', 'host', 'name']
                })
            
            if hosts:
                deleted_hosts = []
                for host in hosts:
                    try:
                        # 删除主机
                        result = zabbix_discovery.zapi.host.delete([host['hostid']])
                        deleted_hosts.append({
                            'hostid': host['hostid'],
                            'hostname': host.get('name', host.get('host', 'Unknown')),
                            'deleted': True
                        })
                        logger.info(f"从Zabbix删除主机: {host['hostid']} ({host.get('name', host.get('host'))})")
                    except Exception as e:
                        logger.error(f"删除Zabbix主机失败: {host['hostid']}, 错误: {str(e)}")
                        deleted_hosts.append({
                            'hostid': host['hostid'],
                            'hostname': host.get('name', host.get('host', 'Unknown')),
                            'deleted': False,
                            'error': str(e)
                        })
                
                return {
                    'success': True,
                    'message': f'处理了 {len(deleted_hosts)} 个Zabbix主机',
                    'hosts': deleted_hosts
                }
            else:
                return {
                    'success': True,
                    'message': '在Zabbix中未找到对应的主机',
                    'hosts': []
                }
                
        except Exception as e:
            logger.error(f"查询或删除Zabbix主机失败: {str(e)}")
            return {
                'success': False,
                'message': f'查询或删除Zabbix主机失败: {str(e)}',
                'error': str(e)
            }
    
    def _ping_single_ip(self, ip_address, timeout=3):
        """执行单个IP的ping测试"""
        try:
            # 验证IP地址格式
            ipaddress.ip_address(ip_address)
            
            # 根据操作系统选择ping命令
            system = platform.system().lower()
            if system == "windows":
                # Windows ping命令
                cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), ip_address]
            else:
                # Linux/Unix ping命令
                cmd = ["ping", "-c", "1", "-W", str(timeout), ip_address]
            
            start_time = time.time()
            
            # 执行ping命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 2  # 给子进程额外的超时时间
            )
            
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)  # 转换为毫秒
            
            # 判断ping是否成功
            is_online = result.returncode == 0
            
            return {
                'ip_address': ip_address,
                'is_online': is_online,
                'response_time': response_time if is_online else None,
                'status': 'online' if is_online else 'offline',
                'message': 'Ping成功' if is_online else 'Ping失败',
                'raw_output': result.stdout if result.stdout else result.stderr
            }
            
        except ipaddress.AddressValueError:
            return {
                'ip_address': ip_address,
                'is_online': False,
                'response_time': None,
                'status': 'offline',
                'message': '无效的IP地址格式',
                'raw_output': ''
            }
        except subprocess.TimeoutExpired:
            return {
                'ip_address': ip_address,
                'is_online': False,
                'response_time': None,
                'status': 'offline',
                'message': f'Ping超时（{timeout}秒）',
                'raw_output': ''
            }
        except Exception as e:
            return {
                'ip_address': ip_address,
                'is_online': False,
                'response_time': None,
                'status': 'offline',
                'message': f'Ping执行失败: {str(e)}',
                'raw_output': ''
            }
    
    @action(detail=True, methods=['post'], url_path='ping')
    def ping(self, request, pk=None):
        """对单个IP记录执行ping测试"""
        try:
            ip_record = self.get_object()
            ip_address = ip_record.ip_address
            
            # 获取超时参数，默认3秒
            timeout = int(request.data.get('timeout', 3))
            timeout = max(1, min(timeout, 10))  # 限制在1-10秒之间
            
            logger.info(f"开始ping测试 IP: {ip_address}, 超时: {timeout}秒")
            
            # 执行ping测试
            ping_result = self._ping_single_ip(ip_address, timeout)
            
            # 更新IP记录的ping状态
            ip_record.ping_status = ping_result['status']
            if ping_result['is_online']:
                ip_record.last_seen = timezone.now()
            ip_record.save()
            
            logger.info(f"IP {ip_address} ping测试完成: {ping_result['message']}")
            
            return Response({
                'code': 200,
                'message': f'IP {ip_address} ping测试完成',
                'data': {
                    'ip_id': ip_record.id,
                    'ip_address': ip_address,
                    'is_online': ping_result['is_online'],
                    'response_time': ping_result['response_time'],
                    'status': ping_result['status'],
                    'message': ping_result['message'],
                    'last_seen': ip_record.last_seen.isoformat() if ip_record.last_seen else None,
                    'test_time': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Ping测试失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'Ping测试失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='batch-ping')
    def batch_ping(self, request):
        """批量ping测试"""
        try:
            # 获取IP ID列表
            ip_ids = request.data.get('ipIds', [])
            timeout = int(request.data.get('timeout', 3))
            timeout = max(1, min(timeout, 10))  # 限制在1-10秒之间
            max_workers = int(request.data.get('maxWorkers', 10))  # 最大并发数
            max_workers = max(1, min(max_workers, 20))  # 限制在1-20之间
            
            if not ip_ids:
                return Response({
                    'code': 400,
                    'message': '请提供要测试的IP ID列表',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取IP记录
            ip_records = IPRecord.objects.filter(id__in=ip_ids)
            if not ip_records.exists():
                return Response({
                    'code': 400,
                    'message': '未找到指定的IP记录',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"开始批量ping测试，IP数量: {len(ip_records)}, 超时: {timeout}秒, 并发数: {max_workers}")
            
            # 使用线程池并发执行ping测试
            ping_results = []
            updated_records = []
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有ping任务
                future_to_record = {
                    executor.submit(self._ping_single_ip, record.ip_address, timeout): record 
                    for record in ip_records
                }
                
                # 收集结果
                for future in as_completed(future_to_record):
                    record = future_to_record[future]
                    try:
                        ping_result = future.result()
                        
                        # 更新数据库记录
                        record.ping_status = ping_result['status']
                        if ping_result['is_online']:
                            record.last_seen = timezone.now()
                        updated_records.append(record)
                        
                        # 添加到结果列表
                        ping_results.append({
                            'ip_id': record.id,
                            'ip_address': record.ip_address,
                            'hostname': record.hostname,
                            'is_online': ping_result['is_online'],
                            'response_time': ping_result['response_time'],
                            'status': ping_result['status'],
                            'message': ping_result['message']
                        })
                        
                    except Exception as e:
                        logger.error(f"处理IP {record.ip_address} ping结果时出错: {str(e)}")
                        ping_results.append({
                            'ip_id': record.id,
                            'ip_address': record.ip_address,
                            'hostname': record.hostname,
                            'is_online': False,
                            'response_time': None,
                            'status': 'offline',
                            'message': f'处理结果时出错: {str(e)}'
                        })
            
            # 批量更新数据库
            if updated_records:
                IPRecord.objects.bulk_update(
                    updated_records, 
                    ['ping_status', 'last_seen'], 
                    batch_size=100
                )
            
            # 统计结果
            online_count = sum(1 for result in ping_results if result['is_online'])
            offline_count = len(ping_results) - online_count
            
            logger.info(f"批量ping测试完成，在线: {online_count}, 离线: {offline_count}")
            
            return Response({
                'code': 200,
                'message': f'批量ping测试完成，共测试 {len(ping_results)} 个IP',
                'data': {
                    'results': ping_results,
                    'summary': {
                        'total': len(ping_results),
                        'online': online_count,
                        'offline': offline_count,
                        'timeout': timeout,
                        'test_time': timezone.now().isoformat()
                    }
                }
            })
            
        except Exception as e:
            logger.error(f"批量ping测试失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'批量ping测试失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'], url_path='batch')
    def batch_delete(self, request):
        """批量删除IP记录"""
        try:
            ip_ids = request.data.get('ipIds', [])
            
            if not ip_ids:
                return Response({
                    'code': 400,
                    'message': '请提供IP ID列表',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取要删除的IP记录
            ip_records = IPRecord.objects.filter(id__in=ip_ids)
            
            if not ip_records.exists():
                return Response({
                    'code': 404,
                    'message': '未找到指定的IP记录',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 统计将要删除的记录
            total_count = ip_records.count()
            auto_discovered_count = ip_records.filter(is_auto_discovered=True).count()
            
            logger.info(f"开始批量删除IP记录，总数: {total_count}, 自动发现: {auto_discovered_count}")
            
            deleted_count = 0
            failed_count = 0
            failed_ips = []
            
            # 逐个删除IP记录
            for ip_record in ip_records:
                try:
                    ip_address = ip_record.ip_address
                    
                    # 清理相关数据
                    if ip_record.is_auto_discovered:
                        self._cleanup_zabbix_data(ip_record)
                    
                    # 清理扫描结果
                    self._cleanup_scan_results(ip_address)
                    
                    # 删除IP记录
                    ip_record.delete()
                    deleted_count += 1
                    
                    logger.info(f"成功删除IP记录: {ip_address}")
                    
                except Exception as e:
                    failed_count += 1
                    failed_ips.append({
                        'ip_address': ip_record.ip_address,
                        'error': str(e)
                    })
                    logger.error(f"删除IP记录失败 {ip_record.ip_address}: {str(e)}")
            
            # 构建响应
            response_data = {
                'deleted_count': deleted_count,
                'failed_count': failed_count,
                'total_requested': total_count,
                'auto_discovered_cleaned': auto_discovered_count
            }
            
            if failed_ips:
                response_data['failed_items'] = failed_ips
            
            if failed_count > 0:
                message = f"批量删除部分成功，成功: {deleted_count}，失败: {failed_count}"
            else:
                message = f"批量删除全部成功，共删除 {deleted_count} 个IP记录"
            
            return Response({
                'code': 200,
                'message': message,
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"批量删除IP记录失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'批量删除失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['patch'], url_path='monitoring')
    def toggle_monitoring(self, request, pk=None):
        """切换单个IP的监控状态"""
        try:
            ip_record = self.get_object()
            enabled = request.data.get('enabled', False)
            
            # 更新监控状态
            ip_record.monitoring_enabled = enabled
            ip_record.save()
            
            action_text = '启用' if enabled else '禁用'
            logger.info(f"IP {ip_record.ip_address} 监控状态已{action_text}")
            
            return Response({
                'code': 200,
                'message': f'IP {ip_record.ip_address} 监控{action_text}成功',
                'data': {
                    'ip_id': ip_record.id,
                    'ip_address': ip_record.ip_address,
                    'monitoring_enabled': ip_record.monitoring_enabled
                }
            })
            
        except Exception as e:
            logger.error(f"切换监控状态失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'切换监控状态失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='zabbix-templates')
    def get_zabbix_templates(self, request, pk=None):
        """获取Zabbix监控模板列表"""
        try:
            search_name = request.query_params.get('search', '')
            
            # 直接从数据库获取模板数据
            from assets.models import ZabbixTemplate
            
            # 构建查询
            if search_name:
                templates = ZabbixTemplate.objects.filter(name__icontains=search_name)
            else:
                templates = ZabbixTemplate.objects.all()
            
            # 转换为字典列表
            template_data = []
            for template in templates:
                template_data.append({
                    'templateid': template.templateid,
                    'name': template.name,
                    'description': template.description or '',
                    'items_count': template.items_count,
                    'triggers_count': template.triggers_count,
                    'macros_count': template.macros_count,
                    'icon': template.icon or 'setting',
                    'category': template.category or '📝 其他',
                    'groups': template.groups
                })
            
            # 按名称排序
            template_data.sort(key=lambda x: x['name'])
            
            return Response({
                'code': 200,
                'message': '获取模板列表成功',
                'data': {
                    'templates': template_data,
                    'count': len(template_data)
                }
            })
            
        except Exception as e:
            logger.error(f"获取Zabbix模板列表失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取模板列表失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='create-monitoring')
    def create_monitoring(self, request, pk=None):
        """为IP创建Zabbix监控主机"""
        try:
            ip_record = self.get_object()
            template_ids = request.data.get('template_ids', [])
            host_name = request.data.get('host_name', ip_record.hostname or ip_record.ip_address)
            group_ids = request.data.get('group_ids', [])
            
            if not template_ids:
                return Response({
                    'code': 400,
                    'message': '请选择至少一个监控模板',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 初始化Zabbix自动发现实例
            zabbix_discovery = zabbix_auto_discovery()
            
            # 创建主机
            result = zabbix_discovery.create_host_with_template(
                host_name=host_name,
                ip_address=ip_record.ip_address,
                template_ids=template_ids,
                group_ids=group_ids if group_ids else None
            )
            
            if result['success']:
                # 更新IP记录的监控状态
                ip_record.monitoring_enabled = True
                if not ip_record.hostname:
                    ip_record.hostname = host_name
                ip_record.save()
                
                return Response({
                    'code': 200,
                    'message': '监控主机创建成功',
                    'data': {
                        'hostid': result['hostid'],
                        'host_name': result['host_name'],
                        'ip_address': result['ip_address'],
                        'template_count': result['template_count']
                    }
                })
            else:
                # 如果主机已存在，也认为是成功的
                if result.get('error') == 'HOST_ALREADY_EXISTS':
                    ip_record.monitoring_enabled = True
                    ip_record.save()
                    
                    return Response({
                        'code': 200,
                        'message': '主机已存在，监控状态已启用',
                        'data': {
                            'hostid': result.get('hostid'),
                            'host_name': host_name,
                            'ip_address': ip_record.ip_address,
                            'already_exists': True
                        }
                    })
                
                return Response({
                    'code': 500,
                    'message': result.get('message', '创建监控主机失败'),
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"创建Zabbix监控主机失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'创建Zabbix监控主机失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['patch'], url_path='batch-monitoring')
    def batch_toggle_monitoring(self, request):
        """批量切换监控状态"""
        try:
            ip_ids = request.data.get('ipIds', [])
            enabled = request.data.get('enabled', False)
            
            if not ip_ids:
                return Response({
                    'code': 400,
                    'message': '请提供IP ID列表',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取IP记录
            ip_records = IPRecord.objects.filter(id__in=ip_ids)
            
            if not ip_records.exists():
                return Response({
                    'code': 404,
                    'message': '未找到指定的IP记录',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 批量更新监控状态
            updated_count = ip_records.update(monitoring_enabled=enabled)
            
            action_text = '启用' if enabled else '禁用'
            logger.info(f"批量{action_text}监控成功，影响 {updated_count} 个IP")
            
            return Response({
                'code': 200,
                'message': f'批量{action_text}监控成功，共 {updated_count} 个IP',
                'data': {
                    'success_count': updated_count,
                    'failed_count': 0,
                    'monitoring_enabled': enabled
                }
            })
            
        except Exception as e:
            logger.error(f"批量切换监控状态失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'批量切换监控状态失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScanTaskViewSet(viewsets.ModelViewSet):
    """扫描任务管理视图集"""
    
    queryset = ScanTask.objects.all().order_by('-created_at')
    serializer_class = ScanTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集，支持筛选"""
        queryset = super().get_queryset()
        
        # 状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 搜索筛选（任务名称）
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(task_name__icontains=search)
        
        # 时间范围筛选
        created_after = self.request.query_params.get('created_after')
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
            
        created_before = self.request.query_params.get('created_before')
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """获取任务列表（支持分页）"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # 简单处理，不使用复杂的分页
            page_size = int(request.query_params.get('page_size', 10))
            page = int(request.query_params.get('page', 1))
            
            start = (page - 1) * page_size
            end = start + page_size
            
            total_count = queryset.count()
            page_data = queryset[start:end]
            
            serializer = self.get_serializer(page_data, many=True)
            
            return Response({
                'code': 200,
                'message': '获取任务列表成功',
                'data': {
                    'results': serializer.data,
                    'count': total_count,
                    'next': None,
                    'previous': None
                }
            })
        except Exception as e:
            logger.error(f"获取任务列表失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取任务列表失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        """创建扫描任务"""
        serializer.save(created_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """删除扫描任务"""
        try:
            instance = self.get_object()
            task_id = str(instance.id)
            task_name = instance.task_name or task_id
            
            # 检查任务状态，不允许删除正在运行的任务
            if instance.status in ['running', 'pending']:
                return Response({
                    'code': 400,
                    'message': '不能删除正在运行或等待中的任务，请先取消任务',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_destroy(instance)
            return Response({
                'code': 200,
                'message': f'任务 "{task_name}" 已成功删除',
                'data': {'taskId': task_id}
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"删除扫描任务失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'删除任务失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """获取任务状态"""
        try:
            task = self.get_object()
            return Response({
                'code': 200,
                'message': '获取任务状态成功',
                'data': {
                    'taskId': str(task.id),
                    'status': task.status,
                    'progress': task.progress,
                    'message': task.error_message or '',
                    'startedAt': task.started_at,
                    'completedAt': task.completed_at,
                    'resultsCount': task.results.count()
                }
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取任务状态失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """获取任务扫描结果"""
        try:
            task = self.get_object()
            results = task.results.all().order_by('ip_address')
            serializer = ScanResultSerializer(results, many=True)
            return Response({
                'code': 200,
                'message': '获取扫描结果成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取扫描结果失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['delete'])
    def cancel(self, request, pk=None):
        """取消任务"""
        try:
            task = self.get_object()
            if task.status in ['completed', 'failed', 'cancelled']:
                return Response({
                    'code': 400,
                    'message': '任务已结束，无法取消',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            task.status = 'cancelled'
            task.completed_at = timezone.now()
            task.save()
            
            return Response({
                'code': 200,
                'message': '任务已成功取消',
                'data': {'taskId': str(task.id), 'status': task.status}
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'取消任务失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='create-test-data')
    def create_test_data(self, request):
        """创建测试数据"""
        try:
            # 先清除旧数据
            ScanTask.objects.filter(task_name__startswith='测试任务').delete()
            
            # 创建一些测试任务
            test_tasks_data = [
                {
                    'task_name': '测试任务-网络扫描-001',
                    'ip_ranges': ['192.168.1.0/24'],
                    'check_type': 12,  # ICMP ping
                    'ports': '0',
                    'status': 'completed',
                    'progress': 100,
                    'started_at': timezone.now(),
                    'completed_at': timezone.now(),
                },
                {
                    'task_name': '测试任务-SNMP扫描-002',
                    'ip_ranges': ['192.168.2.0/24', '10.0.1.0/24'],
                    'check_type': 10,  # SNMPv1
                    'ports': '161',
                    'status': 'running',
                    'progress': 65,
                    'started_at': timezone.now(),
                    'snmp_community': 'public',
                },
                {
                    'task_name': '测试任务-HTTP扫描-003',
                    'ip_ranges': ['10.0.0.0/16'],
                    'check_type': 4,  # HTTP
                    'ports': '80',
                    'status': 'pending',
                    'progress': 0,
                },
                {
                    'task_name': '测试任务-SSH扫描-004',
                    'ip_ranges': ['172.16.0.0/24'],
                    'check_type': 0,  # SSH
                    'ports': '22',
                    'status': 'failed',
                    'progress': 25,
                    'error_message': '连接超时',
                    'started_at': timezone.now(),
                    'completed_at': timezone.now(),
                }
            ]
            
            created_tasks = []
            for task_data in test_tasks_data:
                task_data['created_by'] = request.user
                task = ScanTask.objects.create(**task_data)
                created_tasks.append(str(task.id))
            
            return Response({
                'code': 200,
                'message': f'测试数据创建成功，共创建 {len(created_tasks)} 个任务',
                'data': {'taskIds': created_tasks}
            })
        except Exception as e:
            logger.error(f"创建测试数据失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'创建测试数据失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """获取扫描历史"""
        try:
            queryset = self.get_queryset()
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response({
                    'code': 200,
                    'message': '获取扫描历史成功',
                    'data': serializer.data
                })
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'code': 200,
                'message': '获取扫描历史成功',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': f'获取扫描历史失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='sync-zabbix-ips')
    def sync_zabbix_ips(self, request, pk=None):
        """同步特定任务的Zabbix发现IP到数据库"""
        try:
            task = self.get_object()
            
            # 检查任务是否有Zabbix发现规则ID
            if not task.zabbix_drule_id:
                return Response({
                    'code': 400,
                    'message': '该任务没有关联的Zabbix发现规则ID，无法同步IP',
                    'data': {
                        'task_id': str(task.id),
                        'zabbix_drule_id': task.zabbix_drule_id,
                        'suggestion': '请先创建成功的Zabbix发现检查'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 检查任务状态
            if task.status not in ['completed', 'running']:
                return Response({
                    'code': 400,
                    'message': f'任务状态为 {task.get_status_display()}，只有完成或运行中的任务才能同步IP',
                    'data': {
                        'task_id': str(task.id),
                        'status': task.status,
                        'zabbix_drule_id': task.zabbix_drule_id
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"开始同步任务 {task.id} 的Zabbix发现IP，规则ID: {task.zabbix_drule_id}")
            
            # ... existing code ...
            
            # 初始化Zabbix发现实例
            try:
                zabbix_discovery = zabbix_auto_discovery()
                
                # 执行同步操作
                sync_result = zabbix_discovery.save_discovered_ips_to_database(
                    druleid=task.zabbix_drule_id,
                    task_id=str(task.id),
                    created_by=request.user
                )
                
                logger.info(f"任务 {task.id} Zabbix IP同步结果: {sync_result}")
                
                if sync_result.get('success'):
                    return Response({
                        'code': 200,
                        'message': sync_result.get('message', 'IP同步成功'),
                        'data': {
                            'task_id': str(task.id),
                            'saved_count': sync_result.get('saved_count', 0),
                            'updated_count': sync_result.get('updated_count', 0),
                            'skipped_count': sync_result.get('skipped_count', 0),
                            'total_hosts': sync_result.get('total_hosts', 0),
                            'errors': sync_result.get('errors', [])
                        }
                    })
                else:
                    return Response({
                        'code': 500,
                        'message': sync_result.get('message', 'Zabbix IP同步失败'),
                        'data': None
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
            except Exception as zabbix_error:
                logger.error(f"任务 {task.id} Zabbix IP同步失败: {str(zabbix_error)}")
                return Response({
                    'code': 500,
                    'message': f'Zabbix IP同步失败: {str(zabbix_error)}',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"任务IP同步失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'任务IP同步失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], url_path='async-status')
    def async_status(self, request, pk=None):
        """获取Python扫描任务状态"""
        try:
            task = self.get_object()
            
            # 获取Python任务管理器状态
            from .tasks import task_manager
            runtime_status = task_manager.get_task_status(str(task.id))
            
            # 构建响应数据，处理runtime_status为None的情况
            response_data = {
                'task_id': str(task.id),
                'status': task.status,
                'progress': task.progress,
                'scan_engine': 'python',
                'error_message': task.error_message,
                'result_data': task.result_data or {}
            }
            
            # 如果任务在运行队列中，添加运行时信息
            if runtime_status:
                response_data.update({
                    'is_running': True,
                    'runtime_status': runtime_status.get('status', 'unknown'),
                    'start_time': runtime_status.get('start_time').isoformat() if runtime_status.get('start_time') else None,
                    'duration': runtime_status.get('duration', 0)
                })
            else:
                response_data.update({
                    'is_running': False,
                    'runtime_status': 'not_in_queue',
                    'start_time': None,
                    'duration': 0
                })
            
            return Response({
                'code': 200,
                'message': '获取Python扫描任务状态成功',
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"获取Python扫描任务状态失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取任务状态失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='stop-async')
    def stop_async(self, request, pk=None):
        """停止Python扫描任务"""
        try:
            task = self.get_object()
            
            # 停止Python扫描任务
            from .tasks import task_manager
            stopped = task_manager.stop_task(str(task.id))
            
            if stopped:
                return Response({
                    'code': 200,
                    'message': 'Python扫描任务已停止',
                    'data': {
                        'task_id': str(task.id),
                        'status': 'cancelled',
                        'scan_engine': 'python'
                    }
                })
            else:
                return Response({
                    'code': 400,
                    'message': '任务未在扫描队列中或已经结束',
                    'data': {
                        'task_id': str(task.id),
                        'current_status': task.status
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"停止Python扫描任务失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'停止扫描任务失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScanAPIView(APIView):
    """纯Python扫描API视图 - 不再依赖Zabbix"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """创建Python扫描任务"""
        try:
            # 获取请求参数
            ip_ranges = request.data.get('ipRanges', [])
            check_type = request.data.get('checkType', 12)  # 默认ICMP ping
            ports = request.data.get('ports', '0')
            key = request.data.get('key', '')  # 保留字段，用于服务检测
            max_concurrent = request.data.get('maxConcurrent', 100)  # 最大并发数
            timeout = request.data.get('timeout', 3.0)  # 超时时间
            ping_timeout = request.data.get('pingTimeout', 1.0)  # Ping超时时间
            
            # 验证IP范围参数
            if not ip_ranges:
                return Response({
                    'code': 400,
                    'message': '请提供有效的IP范围',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 处理IP范围格式
            if isinstance(ip_ranges, str):
                # 前端可能发送字符串格式，按换行分割
                ip_ranges = [line.strip() for line in ip_ranges.split('\n') if line.strip()]
            
            logger.info(f"接收到Python扫描任务请求: IP范围={ip_ranges}, 检查类型={check_type}, 端口={ports}")
            
            # 生成任务名称
            check_type_names = {
                0: 'SSH', 1: 'LDAP', 2: 'SMTP', 3: 'FTP', 4: 'HTTP', 5: 'POP3',
                6: 'NNTP', 7: 'IMAP', 8: 'TCP', 9: 'Zabbix Agent', 10: 'SNMPv1',
                11: 'SNMPv2', 12: 'ICMP Ping', 13: 'SNMPv3', 14: 'HTTPS', 15: 'Telnet'
            }
            check_name = check_type_names.get(check_type, f'Type-{check_type}')
            task_name = f'Python扫描 - {check_name}'
            
            # 创建任务
            task = ScanTask.objects.create(
                task_name=task_name,
                ip_ranges=ip_ranges,
                check_type=check_type,
                ports=ports,
                key=key,
                status='pending',
                created_by=request.user,
                # 保存扫描配置
                result_data={
                    'scan_config': {
                        'max_concurrent': max_concurrent,
                        'timeout': timeout,
                        'ping_timeout': ping_timeout,
                        'scan_engine': 'python'
                    }
                }
            )
            
            logger.info(f"创建Python扫描任务成功: {task.id} - {task_name}")
            
            # 添加到Python任务管理器
            from .tasks import task_manager
            scan_config = {
                'max_concurrent': max_concurrent,
                'timeout': timeout,
                'ping_timeout': ping_timeout
            }
            task_manager.add_task(str(task.id), scan_config)
            
            logger.info(f"任务 {task.id} 已添加到Python扫描队列")
            
            # 构建响应数据
            response_data = {
                'taskId': str(task.id),
                'taskName': task_name,
                'status': 'pending',
                'scanEngine': 'python',
                'message': 'Python扫描任务创建成功并开始执行',
                'config': {
                    'ip_ranges': ip_ranges,
                    'check_type': check_type,
                    'check_name': check_name,
                    'ports': ports,
                    'max_concurrent': max_concurrent,
                    'timeout': timeout
                }
            }
            
            return Response({
                'code': 200,
                'message': 'Python扫描任务创建成功',
                'data': response_data
            })
            
        except Exception as e:
            logger.error(f"创建Python扫描任务失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'创建扫描任务失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """查询Python扫描任务状态和结果"""
        try:
            # 获取查询参数
            task_id = request.query_params.get('taskId')
            status_filter = request.query_params.get('status')
            
            if task_id:
                # 查询特定任务的详细信息
                try:
                    task = ScanTask.objects.get(id=task_id)
                    
                    # 获取运行时状态
                    from .tasks import task_manager
                    runtime_status = task_manager.get_task_status(task_id)
                    
                    # 获取扫描结果
                    scan_results = ScanResult.objects.filter(scan_task=task).order_by('ip_address')
                    
                    # 构建详细信息
                    task_detail = {
                        'taskId': str(task.id),
                        'taskName': task.task_name or f'Python扫描任务-{task.id}',
                        'status': task.status,
                        'progress': task.progress,
                        'scanEngine': 'python',
                        'ipRanges': task.ip_ranges,
                        'checkType': task.check_type,
                        'ports': task.ports,
                        'createdAt': task.created_at.isoformat() if task.created_at else None,
                        'startedAt': task.started_at.isoformat() if task.started_at else None,
                        'completedAt': task.completed_at.isoformat() if task.completed_at else None,
                        'createdBy': task.created_by.username if task.created_by else None,
                        'errorMessage': task.error_message,
                        'resultData': task.result_data or {},
                        'isRunning': runtime_status.get('status') == 'running' if runtime_status else False,
                        'resultsCount': scan_results.count()
                    }
                    
                    # 添加统计信息
                    if task.result_data:
                        stats = task.result_data.get('scan_stats', {})
                        task_detail['statistics'] = {
                            'totalScanned': task.result_data.get('total_scanned', 0),
                            'onlineHosts': task.result_data.get('online_hosts', 0),
                            'offlineHosts': task.result_data.get('offline_hosts', 0),
                            'savedToDb': task.result_data.get('saved_to_db', 0),
                            'duration': task.result_data.get('duration', 0)
                        }
                    
                    return Response({
                        'code': 200,
                        'message': '获取任务详情成功',
                        'data': task_detail
                    })
                    
                except ScanTask.DoesNotExist:
                    return Response({
                        'code': 404,
                        'message': f'任务 {task_id} 不存在',
                        'data': None
                    }, status=status.HTTP_404_NOT_FOUND)
            
            else:
                # 查询任务列表
                queryset = ScanTask.objects.all().order_by('-created_at')
                
                # 状态过滤
                if status_filter:
                    queryset = queryset.filter(status=status_filter)
                
                # 获取运行中的任务
                from .tasks import task_manager
                running_task_ids = task_manager.get_running_tasks()
                
                # 构建任务列表
                tasks_data = []
                for task in queryset[:50]:  # 限制返50条
                    task_info = {
                        'taskId': str(task.id),
                        'taskName': task.task_name or f'Python扫描任务-{task.id}',
                        'status': task.status,
                        'progress': task.progress,
                        'scanEngine': 'python',
                        'checkType': task.check_type,
                        'ipRanges': task.ip_ranges,
                        'createdAt': task.created_at.isoformat() if task.created_at else None,
                        'createdBy': task.created_by.username if task.created_by else None,
                        'isRunning': str(task.id) in running_task_ids,
                        'resultsCount': task.results.count() if hasattr(task, 'results') else 0
                    }
                    
                    # 添加结果统计
                    if task.result_data:
                        task_info['onlineHosts'] = task.result_data.get('online_hosts', 0)
                        task_info['totalScanned'] = task.result_data.get('total_scanned', 0)
                    
                    tasks_data.append(task_info)
                
                return Response({
                    'code': 200,
                    'message': '获取扫描任务列表成功',
                    'data': {
                        'tasks': tasks_data,
                        'count': len(tasks_data),
                        'runningTasks': len(running_task_ids),
                        'scanEngine': 'python'
                    }
                })
                
        except Exception as e:
            logger.error(f"查询扫描任务失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'查询扫描任务失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """停止或重启Python扫描任务"""
        try:
            # 获取参数
            task_id = request.data.get('taskId')
            action = request.data.get('action', 'stop')  # stop, restart
            
            if not task_id:
                return Response({
                    'code': 400,
                    'message': '必须提供 taskId 参数',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                task = ScanTask.objects.get(id=task_id)
            except ScanTask.DoesNotExist:
                return Response({
                    'code': 404,
                    'message': f'任务 {task_id} 不存在',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)
            
            from .tasks import task_manager
            
            if action == 'stop':
                # 停止任务
                if task.status in ['completed', 'failed', 'cancelled']:
                    return Response({
                        'code': 400,
                        'message': f'任务已经结束，当前状态: {task.status}',
                        'data': {'taskId': task_id, 'status': task.status}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 停止任务
                stopped = task_manager.stop_task(task_id)
                
                if stopped:
                    return Response({
                        'code': 200,
                        'message': f'任务 {task_id} 已成功停止',
                        'data': {
                            'taskId': task_id,
                            'status': 'cancelled',
                            'action': 'stopped',
                            'stopTime': timezone.now().isoformat()
                        }
                    })
                else:
                    return Response({
                        'code': 400,
                        'message': f'任务 {task_id} 不在运行队列中，可能已经结束',
                        'data': {'taskId': task_id}
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            elif action == 'restart':
                # 重启任务
                if task.status in ['running', 'pending']:
                    return Response({
                        'code': 400,
                        'message': f'任务正在运行中，无法重启',
                        'data': {'taskId': task_id, 'status': task.status}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # 重置任务状态
                task.status = 'pending'
                task.progress = 0
                task.started_at = None
                task.completed_at = None
                task.error_message = None
                task.save()
                
                # 重新添加到任务队列
                scan_config = task.result_data.get('scan_config', {}) if task.result_data else {}
                task_manager.add_task(task_id, scan_config)
                
                return Response({
                    'code': 200,
                    'message': f'任务 {task_id} 已重新启动',
                    'data': {
                        'taskId': task_id,
                        'status': 'pending',
                        'action': 'restarted',
                        'restartTime': timezone.now().isoformat()
                    }
                })
            
            else:
                return Response({
                    'code': 400,
                    'message': f'不支持的操作: {action}',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"任务操作失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'任务操作失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        """处理Python扫描任务的特殊操作"""
        action = request.data.get('action')
        
        if action == 'stop_all_tasks':
            try:
                # 停止所有运行中的任务
                from .tasks import task_manager
                running_tasks = task_manager.get_running_tasks()
                
                if not running_tasks:
                    return Response({
                        'code': 200,
                        'message': '没有正在运行的任务',
                        'data': {
                            'stopped_count': 0,
                            'total_checked': 0
                        }
                    })
                
                stopped_count = 0
                for task_id in running_tasks:
                    if task_manager.stop_task(task_id):
                        stopped_count += 1
                
                return Response({
                    'code': 200,
                    'message': f'成功停止 {stopped_count} 个任务',
                    'data': {
                        'stopped_count': stopped_count,
                        'total_checked': len(running_tasks),
                        'action': 'stop_all_tasks'
                    }
                })
                    
            except Exception as e:
                logger.error(f"停止所有任务失败: {str(e)}")
                return Response({
                    'code': 500,
                    'message': f'停止所有任务失败: {str(e)}',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif action == 'cleanup_failed_tasks':
            try:
                # 清理失败的任务记录
                failed_tasks = ScanTask.objects.filter(status='failed')
                deleted_count = failed_tasks.count()
                failed_tasks.delete()
                
                return Response({
                    'code': 200,
                    'message': f'成功清理 {deleted_count} 个失败任务',
                    'data': {
                        'deleted_count': deleted_count,
                        'action': 'cleanup_failed_tasks'
                    }
                })
                
            except Exception as e:
                logger.error(f"清理失败任务失败: {str(e)}")
                return Response({
                    'code': 500,
                    'message': f'清理失败任务失败: {str(e)}',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        elif action == 'get_scan_statistics':
            try:
                # 获取扫描统计信息
                from .tasks import task_manager
                
                total_tasks = ScanTask.objects.count()
                running_tasks = len(task_manager.get_running_tasks())
                completed_tasks = ScanTask.objects.filter(status='completed').count()
                failed_tasks = ScanTask.objects.filter(status='failed').count()
                
                # 获取最近扫描结果
                recent_tasks = ScanTask.objects.filter(
                    status='completed',
                    result_data__isnull=False
                ).order_by('-completed_at')[:10]
                
                total_ips_scanned = sum(
                    task.result_data.get('total_scanned', 0) 
                    for task in recent_tasks
                )
                total_online_hosts = sum(
                    task.result_data.get('online_hosts', 0)
                    for task in recent_tasks
                )
                
                return Response({
                    'code': 200,
                    'message': '获取扫描统计成功',
                    'data': {
                        'task_statistics': {
                            'total_tasks': total_tasks,
                            'running_tasks': running_tasks,
                            'completed_tasks': completed_tasks,
                            'failed_tasks': failed_tasks
                        },
                        'scan_statistics': {
                            'total_ips_scanned': total_ips_scanned,
                            'total_online_hosts': total_online_hosts,
                            'recent_tasks_count': len(recent_tasks)
                        },
                        'scan_engine': 'python'
                    }
                })
                
            except Exception as e:
                logger.error(f"获取扫描统计失败: {str(e)}")
                return Response({
                    'code': 500,
                    'message': f'获取扫描统计失败: {str(e)}',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 如果不是识别的action，返回400错误
        return Response({
            'code': 400,
            'message': f'不支持的操作类型: {action}',
            'data': {
                'supported_actions': [
                    'stop_all_tasks',
                    'cleanup_failed_tasks', 
                    'get_scan_statistics'
                ]
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class ZabbixManagementAPIView(APIView):
    """Zabbix管理API视图 - 用于管理Zabbix发现规则"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """强制启用所有禁用的Zabbix发现规则"""
        try:
            # 初始化Zabbix发现实例
            zabbix_discovery = zabbix_auto_discovery()
            
            if not zabbix_discovery.connection_status.get('connected'):
                return Response({
                    'code': 500,
                    'message': 'Zabbix API连接不可用，请检查Zabbix服务器状态',
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 强制启用所有禁用的规则
            result = zabbix_discovery.force_enable_all_discovery_rules()
            
            logger.info(f"强制启用Zabbix规则结果: {result}")
            
            if result.get('success') or result.get('enabled_count', 0) > 0:
                return Response({
                    'code': 200,
                    'message': result.get('message'),
                    'data': {
                        'enabled_count': result.get('enabled_count', 0),
                        'total_checked': result.get('total_checked', 0),
                        'failed_rules': result.get('failed_rules', []),
                        'operation_time': timezone.now().isoformat()
                    }
                })
            else:
                return Response({
                    'code': 200,  # 没有禁用规则也是成功情况
                    'message': result.get('message', '没有找到需要启用的规则'),
                    'data': {
                        'enabled_count': 0,
                        'total_checked': result.get('total_checked', 0),
                        'failed_rules': [],
                        'operation_time': timezone.now().isoformat()
                    }
                })
                
        except Exception as e:
            logger.error(f"强制启用发现规则失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'强制启用发现规则失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """获取所有Zabbix发现规则的状态信息"""
        try:
            # 初始化Zabbix发现实例
            zabbix_discovery = zabbix_auto_discovery()
            
            if not zabbix_discovery.connection_status.get('connected'):
                # 返回详细的诊断信息
                diagnosis = zabbix_discovery.diagnose_connection()
                return Response({
                    'code': 500,
                    'message': 'Zabbix API连接不可用',
                    'data': {
                        'connection_status': 'disconnected',
                        'diagnosis': diagnosis
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 获取所有发现规则
            result = zabbix_discovery.query_discovery_info()
            
            if result.get('success'):
                rules = result.get('data', [])
                
                # 统计规则状态
                enabled_count = sum(1 for rule in rules if rule.get('status') == 0)
                disabled_count = sum(1 for rule in rules if rule.get('status') == 1)
                
                return Response({
                    'code': 200,
                    'message': '获取Zabbix规则状态成功',
                    'data': {
                        'connection_status': 'connected',
                        'version': zabbix_discovery.connection_status.get('version'),
                        'rules': rules,
                        'statistics': {
                            'total_rules': len(rules),
                            'enabled_rules': enabled_count,
                            'disabled_rules': disabled_count
                        }
                    }
                })
            else:
                return Response({
                    'code': 500,
                    'message': result.get('message', '获取Zabbix规则信息失败'),
                    'data': None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"获取Zabbix规则状态失败: {str(e)}")
            return Response({
                'code': 500,
                'message': f'获取Zabbix规则状态失败: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
