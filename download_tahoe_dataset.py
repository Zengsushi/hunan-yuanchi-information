#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 tahoebio/Tahoe-100M 数据集脚本
使用 hf-mirror.com 镜像站点加速下载
"""

import os
import subprocess
import sys
from pathlib import Path

def download_dataset():
    """下载数据集"""
    print("=" * 60)
    print("Tahoe-100M 数据集下载脚本")
    print("镜像站点: https://hf-mirror.com")
    print("=" * 60)
    
    # 设置镜像站点环境变量和编码
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    os.environ['PYTHONIOENCODING'] = 'utf-8'  # 解决编码问题
    print("✓ 已设置镜像站点: https://hf-mirror.com")
    print("✓ 已设置UTF-8编码")
    
    # 数据集信息
    dataset_name = "tahoebio/Tahoe-100M"
    local_dir = "./datasets/Tahoe-100M"
    
    print(f"\n数据集: {dataset_name}")
    print(f"保存路径: {os.path.abspath(local_dir)}")
    
    # 创建本地目录
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    print(f"✓ 创建目录: {local_dir}")
    
    # 方法1: 使用 Python API (更稳定)
    try:
        print("\n使用 Python API 下载...")
        from huggingface_hub import snapshot_download
        import time
        
        print("开始下载数据集...")
        print("注意: 这是一个大型数据集，下载可能需要较长时间")
        
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                snapshot_download(
                    repo_id=dataset_name,
                    repo_type="dataset",
                    local_dir=local_dir,
                    resume_download=True,
                    max_workers=4  # 限制并发数
                )
                
                print(f"✓ 数据集下载完成！")
                print(f"保存位置: {os.path.abspath(local_dir)}")
                return True
                
            except Exception as e:
                print(f"✗ 第 {attempt + 1} 次尝试失败: {str(e)[:100]}...")
                if attempt < max_retries - 1:
                    print(f"等待 10 秒后重试...")
                    time.sleep(10)
                else:
                    print(f"✗ 所有重试都失败了")
                    break
        
    except ImportError:
        print("✗ 需要安装 huggingface_hub: pip install huggingface_hub")
        return False
    
    # 方法2: 使用新的 hf 命令 (如果Python API失败)
    try:
        print("\n尝试使用 hf 命令下载...")
        cmd = [
            "hf", "download",
            dataset_name,
            "--repo-type", "dataset",
            "--local-dir", local_dir
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        # 设置编码环境
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env, encoding='utf-8')
        
        if result.returncode == 0:
            print(f"✓ 数据集下载完成！")
            print(f"保存位置: {os.path.abspath(local_dir)}")
            return True
        else:
            print(f"✗ hf 命令下载失败: {result.stderr[:200]}...")
            
    except FileNotFoundError:
        print("✗ 未找到 hf 命令")
    except Exception as e:
        print(f"✗ hf 命令执行失败: {e}")
    
    return False

if __name__ == "__main__":
    success = download_dataset()
    
    if success:
        print("\n" + "=" * 60)
        print("✓ 下载任务完成！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("✗ 下载失败")
        print("请先安装依赖: pip install huggingface_hub")
        print("然后重新运行脚本")
        print("=" * 60)
        sys.exit(1)