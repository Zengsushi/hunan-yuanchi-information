"""
清理过期用户会话的Django管理命令
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import UserSession


class Command(BaseCommand):
    help = '清理过期的用户会话记录'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            help='会话超时时间（分钟），默认5分钟'
        )
        
        parser.add_argument(
            '--cleanup-old',
            type=int,
            default=30,
            help='清理多少天前的非活跃会话记录，默认30天'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='模拟运行，不实际删除数据'
        )

    def handle(self, *args, **options):
        timeout_minutes = options['timeout']
        cleanup_days = options['cleanup_old']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'开始清理用户会话 (超时: {timeout_minutes}分钟, 旧记录: {cleanup_days}天)')
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('*** 模拟运行模式 - 不会实际删除数据 ***'))
        
        # 1. 清理过期会话
        timeout_threshold = timezone.now() - timezone.timedelta(minutes=timeout_minutes)
        expired_sessions = UserSession.objects.filter(
            is_active=True,
            last_activity__lte=timeout_threshold
        )
        
        expired_count = expired_sessions.count()
        self.stdout.write(f'找到 {expired_count} 个过期会话')
        
        if not dry_run and expired_count > 0:
            for session in expired_sessions:
                session.mark_offline('timeout')
            self.stdout.write(
                self.style.SUCCESS(f'成功标记 {expired_count} 个过期会话为离线')
            )
        
        # 2. 清理旧的非活跃会话记录
        cutoff_date = timezone.now() - timezone.timedelta(days=cleanup_days)
        old_sessions = UserSession.objects.filter(
            is_active=False,
            last_activity__lte=cutoff_date
        )
        
        old_count = old_sessions.count()
        self.stdout.write(f'找到 {old_count} 个旧的非活跃会话记录')
        
        if not dry_run and old_count > 0:
            old_sessions.delete()
            self.stdout.write(
                self.style.SUCCESS(f'成功删除 {old_count} 个旧的会话记录')
            )
        
        # 3. 统计当前状态
        total_sessions = UserSession.objects.count()
        active_sessions = UserSession.objects.filter(is_active=True).count()
        online_users = UserSession.get_online_users_count()
        
        self.stdout.write('\n当前会话统计:')
        self.stdout.write(f'  总会话数: {total_sessions}')
        self.stdout.write(f'  活跃会话: {active_sessions}')
        self.stdout.write(f'  在线用户: {online_users}')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\n*** 模拟运行完成 - 实际运行请移除 --dry-run 参数 ***')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n清理完成！')
            )