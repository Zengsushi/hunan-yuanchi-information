#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Git推送脚本
快速推送所有文件到指定分支
"""

import os
import subprocess
import sys


def run_git_command(command):
    """执行Git命令"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8')
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def main():
    print("🚀 简化版Git推送脚本")
    print("=" * 30)
    
    # 检查Git仓库
    success, _, _ = run_git_command("git status")
    if not success:
        print("❌ 当前目录不是Git仓库")
        return
    
    # 获取当前分支
    success, current_branch, _ = run_git_command("git branch --show-current")
    if success:
        print(f"🌿 当前分支: {current_branch}")
    
    # 获取所有分支
    success, branches_output, _ = run_git_command("git branch")
    if success:
        branches = []
        for line in branches_output.split('\n'):
            branch = line.strip().replace('* ', '')
            if branch:
                branches.append(branch)
        
        print("\n📋 可用分支:")
        for i, branch in enumerate(branches, 1):
            marker = " (当前)" if branch == current_branch else ""
            print(f"{i}. {branch}{marker}")
        
        # 选择分支
        try:
            choice = input(f"\n选择分支编号 (1-{len(branches)}) 或回车使用当前分支: ").strip()
            
            if choice:
                index = int(choice) - 1
                if 0 <= index < len(branches):
                    target_branch = branches[index]
                    if target_branch != current_branch:
                        print(f"🔄 切换到分支: {target_branch}")
                        success, _, error = run_git_command(f"git checkout {target_branch}")
                        if not success:
                            print(f"❌ 切换分支失败: {error}")
                            return
                else:
                    print("❌ 无效的分支编号")
                    return
            else:
                target_branch = current_branch
        except ValueError:
            print("❌ 请输入有效数字")
            return
    else:
        target_branch = current_branch
    
    # 添加所有文件
    print("\n📦 添加所有文件...")
    success, _, error = run_git_command("git add .")
    if not success:
        print(f"❌ 添加文件失败: {error}")
        return
    
    # 获取提交信息
    commit_msg = input("💬 提交信息 (默认: 'Update files'): ").strip()
    if not commit_msg:
        commit_msg = "Update files"
    
    # 提交
    print("💾 提交更改...")
    success, output, error = run_git_command(f'git commit -m "{commit_msg}"')
    if not success and "nothing to commit" not in error:
        print(f"❌ 提交失败: {error}")
        return
    elif "nothing to commit" in error:
        print("ℹ️ 没有需要提交的更改")
    
    # 推送
    print(f"🚀 推送到 {target_branch} 分支...")
    success, _, error = run_git_command(f"git push origin {target_branch}")
    if success:
        print("✅ 推送成功！")
    else:
        print(f"❌ 推送失败: {error}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 操作已取消")
    except Exception as e:
        print(f"❌ 错误: {e}")