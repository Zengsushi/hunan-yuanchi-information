#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
纯 Python 实现的 IP 扫描模块
替代 Zabbix 自动发现，提供更快速、灵活的网络扫描能力
"""

import asyncio
import socket
import ipaddress
import time
import logging
import platform
import subprocess
import struct
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timezone
import json

# 异步库导入
try:
    import aiohttp
    import asyncssh
    HAS_ASYNC_LIBS = True
except ImportError:
    HAS_ASYNC_LIBS = False
    
# SNMP库导入  
try:
    from pysnmp.hlapi import *
    HAS_SNMP = True
except ImportError:
    HAS_SNMP = False

logger = logging.getLogger(__name__)


@dataclass
class ScanResult:
    """扫描结果数据类"""
    ip_address: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    status: str = 'offline'  # online, offline, filtered
    response_time: Optional[float] = None
    open_ports: List[int] = None
    services: Dict[int, str] = None
    os_info: Optional[str] = None
    vendor: Optional[str] = None
    discovered_at: datetime = None
    
    def __post_init__(self):
        if self.open_ports is None:
            self.open_ports = []
        if self.services is None:
            self.services = {}
        if self.discovered_at is None:
            self.discovered_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'mac_address': self.mac_address,
            'status': self.status,
            'response_time': self.response_time,
            'open_ports': self.open_ports,
            'services': self.services,
            'os_info': self.os_info,
            'vendor': self.vendor,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None
        }


class NetworkScanner:
    """网络扫描器主类"""
    
    def __init__(self, 
                 max_concurrent: int = 100,
                 timeout: float = 3.0,
                 ping_timeout: float = 1.0):
        """
        初始化网络扫描器
        
        Args:
            max_concurrent: 最大并发数
            timeout: 连接超时时间（秒）
            ping_timeout: ping超时时间（秒）
        """
        self.max_concurrent = max_concurrent
        self.timeout = timeout  
        self.ping_timeout = ping_timeout
        self.is_windows = platform.system().lower() == 'windows'
        
        # 扫描统计信息
        self.stats = {
            'total_ips': 0,
            'scanned': 0,
            'online': 0,
            'offline': 0,
            'start_time': None,
            'end_time': None
        }
        
        # 结果存储
        self.results: List[ScanResult] = []
        self.scan_callbacks = []  # 进度回调函数列表
        
    def add_progress_callback(self, callback):
        """添加进度回调函数"""
        self.scan_callbacks.append(callback)
        
    def _notify_progress(self, current: int, total: int, result: ScanResult = None):
        """通知进度更新"""
        # 处理stats中的datetime对象，避免序列化问题
        serializable_stats = {}
        for key, value in self.stats.items():
            if key in ['start_time', 'end_time'] and value:
                # 将datetime对象转换为ISO格式字符串
                serializable_stats[key] = value.isoformat()
            else:
                serializable_stats[key] = value
        
        progress_data = {
            'current': current,
            'total': total,
            'percentage': round((current / total) * 100, 2) if total > 0 else 0,
            'stats': serializable_stats,
            'result': result
        }
        
        for callback in self.scan_callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                logger.error(f"进度回调函数执行失败: {e}")
    
    def parse_ip_ranges(self, ip_ranges: List[str]) -> List[str]:
        """
        解析IP范围，支持多种格式
        
        Args:
            ip_ranges: IP范围列表，支持格式：
                - 单个IP: "192.168.1.1"
                - CIDR: "192.168.1.0/24"
                - 范围: "192.168.1.1-192.168.1.100"
                
        Returns:
            解析后的IP地址列表
        """
        ips = []
        
        for ip_range in ip_ranges:
            ip_range = ip_range.strip()
            
            try:
                if '/' in ip_range:
                    # CIDR格式
                    network = ipaddress.ip_network(ip_range, strict=False)
                    ips.extend([str(ip) for ip in network.hosts()])
                    
                elif '-' in ip_range:
                    # 范围格式
                    start_ip, end_ip = ip_range.split('-', 1)
                    start_ip = start_ip.strip()
                    end_ip = end_ip.strip()
                    
                    # 处理简化范围格式 (192.168.1.1-100)
                    if '.' not in end_ip:
                        # 简化格式，取起始IP的前缀
                        start_parts = start_ip.split('.')
                        if len(start_parts) == 4:
                            end_ip = '.'.join(start_parts[:3]) + '.' + end_ip
                    
                    start = ipaddress.ip_address(start_ip)
                    end = ipaddress.ip_address(end_ip)
                    
                    # 生成范围内的所有IP
                    current = int(start)
                    end_int = int(end)
                    while current <= end_int:
                        ips.append(str(ipaddress.ip_address(current)))
                        current += 1
                        
                else:
                    # 单个IP
                    ipaddress.ip_address(ip_range)  # 验证格式
                    ips.append(ip_range)
                    
            except Exception as e:
                logger.error(f"解析IP范围失败 '{ip_range}': {e}")
                continue
        
        # 去重并排序
        unique_ips = sorted(list(set(ips)), key=lambda x: ipaddress.ip_address(x))
        logger.info(f"解析IP范围完成: {len(ip_ranges)} 个范围 -> {len(unique_ips)} 个IP地址")
        return unique_ips
    
    def ping_host(self, ip: str) -> Tuple[bool, Optional[float]]:
        """
        Ping单个主机
        
        Args:
            ip: 目标IP地址
            
        Returns:
            (是否在线, 响应时间ms)
        """
        try:
            if self.is_windows:
                cmd = ['ping', '-n', '1', '-w', str(int(self.ping_timeout * 1000)), ip]
            else:
                cmd = ['ping', '-c', '1', '-W', str(int(self.ping_timeout)), ip]
            
            start_time = time.time()
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=self.ping_timeout + 1
            )
            end_time = time.time()
            
            if result.returncode == 0:
                response_time = (end_time - start_time) * 1000
                return True, response_time
            else:
                return False, None
                
        except subprocess.TimeoutExpired:
            return False, None
        except Exception as e:
            logger.debug(f"Ping {ip} 失败: {e}")
            return False, None
    
    def scan_port(self, ip: str, port: int) -> bool:
        """
        扫描单个端口
        
        Args:
            ip: 目标IP
            port: 端口号
            
        Returns:
            端口是否开放
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except Exception:
            return False
    
    def scan_ports(self, ip: str, ports: List[int]) -> Dict[int, bool]:
        """
        扫描多个端口
        
        Args:
            ip: 目标IP
            ports: 端口列表
            
        Returns:
            端口扫描结果字典
        """
        results = {}
        
        # 使用线程池并发扫描端口
        with ThreadPoolExecutor(max_workers=min(50, len(ports))) as executor:
            future_to_port = {
                executor.submit(self.scan_port, ip, port): port 
                for port in ports
            }
            
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    results[port] = future.result()
                except Exception as e:
                    logger.debug(f"扫描端口 {ip}:{port} 失败: {e}")
                    results[port] = False
                    
        return results
    
    def get_hostname(self, ip: str) -> Optional[str]:
        """
        获取主机名
        
        Args:
            ip: IP地址
            
        Returns:
            主机名或None
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname if hostname != ip else None
        except Exception:
            return None
    
    def detect_service(self, ip: str, port: int) -> Optional[str]:
        """
        检测端口服务类型
        
        Args:
            ip: IP地址
            port: 端口号
            
        Returns:
            服务名称或None
        """
        # 常见服务端口映射
        common_services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
            443: 'HTTPS', 993: 'IMAPS', 995: 'POP3S',
            3389: 'RDP', 5432: 'PostgreSQL', 3306: 'MySQL',
            6379: 'Redis', 27017: 'MongoDB', 9200: 'Elasticsearch'
        }
        
        service_name = common_services.get(port)
        if service_name:
            return service_name
            
        # 尝试banner抓取
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2.0)
                sock.connect((ip, port))
                
                # 发送HTTP请求尝试
                if port in [80, 8080, 8000, 8888]:
                    sock.send(b'GET / HTTP/1.0\r\n\r\n')
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                    if 'HTTP/' in banner:
                        return 'HTTP'
                
                # 接收banner
                banner = sock.recv(1024).decode('utf-8', errors='ignore')
                if 'SSH' in banner:
                    return 'SSH'
                elif 'FTP' in banner:
                    return 'FTP'
                elif 'HTTP' in banner:
                    return 'HTTP'
                    
        except Exception:
            pass
            
        return f'Unknown/{port}'
    
    def scan_host_comprehensive(self, ip: str, ports: List[int] = None) -> ScanResult:
        """
        综合扫描单个主机
        
        Args:
            ip: 目标IP地址
            ports: 要扫描的端口列表，默认扫描常用端口
            
        Returns:
            扫描结果
        """
        if ports is None:
            # 默认扫描常用端口
            ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 3389, 5432, 3306]
        
        result = ScanResult(ip_address=ip)
        
        # 1. Ping检测
        is_alive, ping_time = self.ping_host(ip)
        if is_alive:
            result.status = 'online'
            result.response_time = ping_time
            
            # 2. 获取主机名
            result.hostname = self.get_hostname(ip)
            
            # 3. 端口扫描
            if ports:
                port_results = self.scan_ports(ip, ports)
                open_ports = [port for port, is_open in port_results.items() if is_open]
                result.open_ports = open_ports
                
                # 4. 服务检测
                for port in open_ports:
                    service = self.detect_service(ip, port)
                    if service:
                        result.services[port] = service
        else:
            result.status = 'offline'
            
        return result
    
    def scan_network(self, 
                    ip_ranges: List[str], 
                    ports: List[int] = None,
                    ping_only: bool = False) -> List[ScanResult]:
        """
        扫描网络范围
        
        Args:
            ip_ranges: IP范围列表
            ports: 端口列表，None表示使用默认端口
            ping_only: 是否只进行ping扫描
            
        Returns:
            扫描结果列表
        """
        # 解析IP地址
        ips = self.parse_ip_ranges(ip_ranges)
        self.stats['total_ips'] = len(ips)
        self.stats['start_time'] = datetime.now(timezone.utc)
        
        if not ips:
            logger.warning("没有有效的IP地址需要扫描")
            return []
        
        logger.info(f"开始扫描 {len(ips)} 个IP地址")
        
        # 重置结果
        self.results.clear()
        self.stats['scanned'] = 0
        self.stats['online'] = 0
        self.stats['offline'] = 0
        
        # 使用线程池并发扫描
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # 提交任务
            if ping_only:
                future_to_ip = {
                    executor.submit(self._ping_scan_single, ip): ip 
                    for ip in ips
                }
            else:
                future_to_ip = {
                    executor.submit(self.scan_host_comprehensive, ip, ports): ip 
                    for ip in ips
                }
            
            # 处理结果
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    # 更新统计
                    self.stats['scanned'] += 1
                    if result.status == 'online':
                        self.stats['online'] += 1
                    else:
                        self.stats['offline'] += 1
                    
                    # 通知进度
                    self._notify_progress(self.stats['scanned'], self.stats['total_ips'], result)
                    
                except Exception as e:
                    logger.error(f"扫描IP {ip} 失败: {e}")
                    # 创建失败结果
                    error_result = ScanResult(ip_address=ip, status='offline')
                    self.results.append(error_result)
                    self.stats['scanned'] += 1
                    self.stats['offline'] += 1
                    
                    self._notify_progress(self.stats['scanned'], self.stats['total_ips'], error_result)
        
        self.stats['end_time'] = datetime.now(timezone.utc)
        elapsed = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        logger.info(f"扫描完成: {self.stats['online']} 在线, {self.stats['offline']} 离线, 耗时 {elapsed:.2f} 秒")
        
        # 按IP地址排序结果
        self.results.sort(key=lambda x: ipaddress.ip_address(x.ip_address))
        
        return self.results
    
    def _ping_scan_single(self, ip: str) -> ScanResult:
        """单个IP的ping扫描"""
        result = ScanResult(ip_address=ip)
        is_alive, ping_time = self.ping_host(ip)
        
        if is_alive:
            result.status = 'online'
            result.response_time = ping_time
            result.hostname = self.get_hostname(ip)
        else:
            result.status = 'offline'
            
        return result
    
    def get_stats(self) -> Dict:
        """获取扫描统计信息"""
        stats = self.stats.copy()
        if stats['start_time'] and stats['end_time']:
            stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
        elif stats['start_time']:
            stats['duration'] = (datetime.now(timezone.utc) - stats['start_time']).total_seconds()
        else:
            stats['duration'] = 0
            
        return stats
    
    def export_results(self, format: str = 'json') -> str:
        """
        导出扫描结果
        
        Args:
            format: 导出格式 ('json', 'csv')
            
        Returns:
            格式化的结果字符串
        """
        if format.lower() == 'json':
            return json.dumps([result.to_dict() for result in self.results], 
                            indent=2, ensure_ascii=False)
        elif format.lower() == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow(['IP地址', '主机名', 'MAC地址', '状态', '响应时间(ms)', 
                           '开放端口', '服务', '发现时间'])
            
            # 写入数据
            for result in self.results:
                writer.writerow([
                    result.ip_address,
                    result.hostname or '',
                    result.mac_address or '',
                    result.status,
                    result.response_time or '',
                    ','.join(map(str, result.open_ports)),
                    ','.join(f"{port}:{service}" for port, service in result.services.items()),
                    result.discovered_at.isoformat() if result.discovered_at else ''
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"不支持的导出格式: {format}")


class AsyncNetworkScanner:
    """异步网络扫描器（需要安装aiohttp等异步库）"""
    
    def __init__(self, max_concurrent: int = 200, timeout: float = 3.0):
        if not HAS_ASYNC_LIBS:
            raise ImportError("异步扫描需要安装: pip install aiohttp asyncssh")
            
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def async_ping(self, ip: str) -> Tuple[bool, Optional[float]]:
        """异步ping"""
        async with self.semaphore:
            # 这里可以实现异步ping逻辑
            # 当前使用同步版本作为占位符
            loop = asyncio.get_event_loop()
            scanner = NetworkScanner()
            return await loop.run_in_executor(None, scanner.ping_host, ip)
    
    async def async_scan_network(self, ip_ranges: List[str]) -> List[ScanResult]:
        """异步扫描网络"""
        scanner = NetworkScanner()
        ips = scanner.parse_ip_ranges(ip_ranges)
        
        tasks = [self.async_ping(ip) for ip in ips]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        scan_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                scan_results.append(ScanResult(ip_address=ips[i], status='offline'))
            else:
                is_alive, response_time = result
                status = 'online' if is_alive else 'offline'
                scan_results.append(ScanResult(
                    ip_address=ips[i], 
                    status=status, 
                    response_time=response_time
                ))
        
        return scan_results


def create_scanner(async_mode: bool = False, **kwargs) -> Union[NetworkScanner, AsyncNetworkScanner]:
    """
    创建扫描器实例
    
    Args:
        async_mode: 是否使用异步模式
        **kwargs: 扫描器参数
        
    Returns:
        扫描器实例
    """
    if async_mode:
        return AsyncNetworkScanner(**kwargs)
    else:
        return NetworkScanner(**kwargs)


# 示例用法
if __name__ == "__main__":
    # 创建扫描器
    scanner = NetworkScanner(max_concurrent=50, timeout=2.0)
    
    # 添加进度回调
    def progress_callback(data):
        print(f"进度: {data['percentage']}% ({data['current']}/{data['total']})")
        if data['result'] and data['result'].status == 'online':
            print(f"  发现在线主机: {data['result'].ip_address} - {data['result'].hostname}")
    
    scanner.add_progress_callback(progress_callback)
    
    # 扫描网络
    ip_ranges = ['192.168.1.0/24', '10.0.0.1-10']
    results = scanner.scan_network(ip_ranges, ping_only=True)
    
    # 输出结果
    print(f"\n扫描完成！统计信息:")
    stats = scanner.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 显示在线主机
    online_hosts = [r for r in results if r.status == 'online']
    print(f"\n发现 {len(online_hosts)} 个在线主机:")
    for host in online_hosts:
        print(f"  {host.ip_address} - {host.hostname or 'Unknown'} ({host.response_time:.2f}ms)")