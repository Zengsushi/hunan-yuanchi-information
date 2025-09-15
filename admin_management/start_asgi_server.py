#!/usr/bin/env python
"""
启动支持WebSocket的Django ASGI开发服务器
使用Uvicorn作为ASGI服务器，支持HTTP和WebSocket连接
"""

import os
import sys
import subprocess
import django
from django.core.management.base import BaseCommand
import time

def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    
    try:
        import uvicorn
        print("✅ Uvicorn ASGI服务器")
    except ImportError:
        print("❌ Uvicorn未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'uvicorn[standard]'])
            print("✅ Uvicorn安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ Uvicorn安装失败: {e}")
            return False
    
    try:
        import channels
        print("✅ Django Channels")
    except ImportError:
        print("❌ Django Channels未安装")
        return False
    
    try:
        import googletrans
        print("✅ Google翻译库")
    except ImportError:
        print("❌ Google翻译库未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'googletrans==4.0.0-rc1'])
            print("✅ Google翻译库安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ Google翻译库安装失败: {e}")
            return False
    
    return True

def setup_django():
    """设置Django环境"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ops_assets_backend.settings')
    django.setup()

def run_migrations():
    """运行数据库迁移"""
    print("\n🗄️  检查数据库迁移...")
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=1'])
        print("✅ 数据库迁移完成")
        return True
    except Exception as e:
        print(f"❌ 数据库迁移失败: {e}")
        return False

def start_asgi_server(host='127.0.0.1', port=8000):
    """启动ASGI开发服务器"""
    print(f"\n🚀 启动ASGI开发服务器...")
    print(f"📡 HTTP服务: http://{host}:{port}")
    print(f"🔌 WebSocket服务: ws://{host}:{port}/ws/")
    print("💡 按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        # 使用Uvicorn启动ASGI应用
        import uvicorn
        
        # 配置Uvicorn参数
        config = uvicorn.Config(
            "ops_assets_backend.asgi:application",
            host=host,
            port=port,
            reload=True,  # 启用自动重载
            log_level="info",
            workers=1,  # 开发环境使用单个工作进程
        )
        
        # 启动Uvicorn服务器
        server = uvicorn.Server(config)
        server.run()
        
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}")
        print("💡 请检查端口是否被占用或配置是否正确")

def sync_zabbix_templates():
    """从Zabbix同步模板到数据库"""
    print("\n🔄 正在同步Zabbix模板...")
    try:
        # 导入必要的模块
        from ops_assets_backend.zabbix_api import zabbix_auto_discovery
        from assets.models import ZabbixTemplate
        from googletrans import Translator
        import time
        
        # 创建翻译器实例，使用deep-translator库
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target='zh-CN')
        
        # 创建Zabbix API实例
        zabbix_api = zabbix_auto_discovery()
        
        # 检查Zabbix连接
        connection_status = zabbix_api.get_connection_status()
        if not connection_status.get('connected', False):
            print(f"❌ 无法连接到Zabbix服务器: {connection_status.get('error', '未知错误')}")
            return False
        
        # 获取所有模板
        result = zabbix_api.get_templates()
        
        if not result['success']:
            print(f"❌ 获取模板失败: {result['message']}")
            return False
        
        templates = result['data']
        zabbix_template_count = len(templates)
        print(f"✅ 成功获取 {zabbix_template_count} 个模板")
        
        # 检查数据库中的模板数量
        db_template_count = ZabbixTemplate.objects.count()
        
        # 如果数据库中的模板数量与Zabbix的模板数量相同，则跳过同步
        if db_template_count == zabbix_template_count and zabbix_template_count > 0:
            print(f"✅ 数据库中已有 {db_template_count} 个模板，与Zabbix模板数量相同，跳过同步")
            return True
        
        # 同步到数据库
        created_count = 0
        updated_count = 0
        
        for template_data in templates:
            # 只翻译模板描述，不翻译模板名称，增加重试机制
            translated_name = template_data['name']
            translated_description = template_data['description']
            
            # 最多重试3次
            for attempt in range(3):
                try:
                    # 只翻译描述，保留原始名称
                    translated_description = translator.translate(template_data['description'])
                    break  # 成功则跳出重试循环
                except Exception as e:
                    print(f"⚠️  翻译模板描述 '{template_data['name']}' 时出错 (尝试 {attempt + 1}/3): {e}")
                    if attempt == 2:  # 最后一次尝试失败
                        print(f"❌ 翻译模板描述 '{template_data['name']}' 失败，使用原始文本")
                    time.sleep(2)  # 增加等待时间避免请求过于频繁
            
            # 使用templateid作为唯一标识
            template, created = ZabbixTemplate.objects.update_or_create(
                templateid=template_data['templateid'],
                defaults={
                    'name': translated_name,
                    'description': translated_description,
                    'items_count': template_data['items_count'],
                    'triggers_count': template_data['triggers_count'],
                    'macros_count': template_data['macros_count'],
                    'icon': template_data['icon'],
                    'category': template_data['category'],
                    'groups': template_data['groups']
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        print(f"✅ 模板同步完成: 新增 {created_count} 个, 更新 {updated_count} 个")
        return True
        
    except Exception as e:
        print(f"❌ 模板同步失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🎯 Django ASGI开发服务器启动器")
    print("支持HTTP API和WebSocket连接")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装所需依赖")
        return 1
    
    # 设置Django环境
    try:
        setup_django()
        print("✅ Django环境已设置")
    except Exception as e:
        print(f"❌ Django环境设置失败: {e}")
        return 1
    
    # 运行数据库迁移
    if not run_migrations():
        print("❌ 数据库迁移失败，服务器可能无法正常运行")
        # 继续启动，但发出警告
        print("⚠️  继续启动服务器，但可能遇到数据库问题")
    
    # 同步Zabbix模板
    sync_zabbix_templates()
    
    # 启动ASGI服务器
    try:
        start_asgi_server(host='0.0.0.0', port=8001)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())