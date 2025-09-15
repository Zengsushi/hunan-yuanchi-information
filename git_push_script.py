#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git推送脚本
功能：将文件夹中的所有文件推送到Git仓库，支持分支选择
作者：自动生成
"""

import os
import subprocess
import sys
from typing import List, Optional


class GitPushManager:
    def __init__(self, repo_path: str = "."):
        """
        初始化Git推送管理器
        
        Args:
            repo_path: Git仓库路径，默认为当前目录
        """
        self.repo_path = os.path.abspath(repo_path)
        self.current_branch = None
        
    def run_command(self, command: List[str]) -> tuple[bool, str]:
        """
        执行命令并返回结果
        
        Args:
            command: 要执行的命令列表
            
        Returns:
            tuple: (是否成功, 输出信息)
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def check_git_repo(self) -> bool:
        """
        检查当前目录是否为Git仓库
        
        Returns:
            bool: 是否为Git仓库
        """
        success, _ = self.run_command(["git", "status"])
        return success
    
    def get_current_branch(self) -> Optional[str]:
        """
        获取当前分支名称
        
        Returns:
            str: 当前分支名称，如果获取失败返回None
        """
        success, output = self.run_command(["git", "branch", "--show-current"])
        if success:
            self.current_branch = output.strip()
            return self.current_branch
        return None
    
    def get_all_branches(self) -> List[str]:
        """
        获取所有分支列表
        
        Returns:
            List[str]: 分支列表
        """
        success, output = self.run_command(["git", "branch", "-a"])
        if not success:
            return []
        
        branches = []
        for line in output.split('\n'):
            line = line.strip()
            if line and not line.startswith('*'):
                # 移除远程分支前缀
                if line.startswith('remotes/origin/'):
                    branch_name = line.replace('remotes/origin/', '')
                    if branch_name != 'HEAD':
                        branches.append(branch_name)
                else:
                    branches.append(line)
            elif line.startswith('*'):
                # 当前分支
                current = line.replace('*', '').strip()
                branches.append(current)
        
        # 去重并排序
        return sorted(list(set(branches)))
    
    def switch_branch(self, branch_name: str) -> bool:
        """
        切换到指定分支
        
        Args:
            branch_name: 分支名称
            
        Returns:
            bool: 是否切换成功
        """
        success, output = self.run_command(["git", "checkout", branch_name])
        if success:
            print(f"✅ 成功切换到分支: {branch_name}")
            self.current_branch = branch_name
            return True
        else:
            print(f"❌ 切换分支失败: {output}")
            return False
    
    def add_all_files(self) -> bool:
        """
        添加所有文件到暂存区
        
        Returns:
            bool: 是否添加成功
        """
        success, output = self.run_command(["git", "add", "."])
        if success:
            print("✅ 成功添加所有文件到暂存区")
            return True
        else:
            print(f"❌ 添加文件失败: {output}")
            return False
    
    def commit_changes(self, commit_message: str) -> bool:
        """
        提交更改
        
        Args:
            commit_message: 提交信息
            
        Returns:
            bool: 是否提交成功
        """
        success, output = self.run_command(["git", "commit", "-m", commit_message])
        if success:
            print(f"✅ 成功提交更改: {commit_message}")
            return True
        else:
            if "nothing to commit" in output:
                print("ℹ️ 没有需要提交的更改")
                return True
            else:
                print(f"❌ 提交失败: {output}")
                return False
    
    def push_to_remote(self, branch_name: str) -> bool:
        """
        推送到远程仓库
        
        Args:
            branch_name: 分支名称
            
        Returns:
            bool: 是否推送成功
        """
        success, output = self.run_command(["git", "push", "origin", branch_name])
        if success:
            print(f"✅ 成功推送到远程分支: {branch_name}")
            return True
        else:
            print(f"❌ 推送失败: {output}")
            return False
    
    def get_status(self) -> str:
        """
        获取Git状态
        
        Returns:
            str: Git状态信息
        """
        success, output = self.run_command(["git", "status", "--porcelain"])
        if success:
            return output
        return ""


def select_branch(git_manager: GitPushManager) -> Optional[str]:
    """
    让用户选择分支
    
    Args:
        git_manager: Git管理器实例
        
    Returns:
        str: 选择的分支名称，如果取消返回None
    """
    branches = git_manager.get_all_branches()
    current_branch = git_manager.get_current_branch()
    
    if not branches:
        print("❌ 未找到任何分支")
        return None
    
    print("\n📋 可用分支列表:")
    print("-" * 40)
    for i, branch in enumerate(branches, 1):
        marker = " (当前)" if branch == current_branch else ""
        print(f"{i}. {branch}{marker}")
    
    print("\n请选择要推送的分支:")
    while True:
        try:
            choice = input(f"请输入分支编号 (1-{len(branches)}) 或 'q' 退出: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(branches):
                return branches[index]
            else:
                print(f"❌ 请输入有效的编号 (1-{len(branches)})")
        except ValueError:
            print("❌ 请输入有效的数字")


def main():
    """
    主函数
    """
    print("🚀 Git推送脚本启动")
    print("=" * 50)
    
    # 初始化Git管理器
    git_manager = GitPushManager()
    
    # 检查是否为Git仓库
    if not git_manager.check_git_repo():
        print("❌ 当前目录不是Git仓库，请先初始化Git仓库")
        sys.exit(1)
    
    print(f"📁 工作目录: {git_manager.repo_path}")
    
    # 获取当前分支
    current_branch = git_manager.get_current_branch()
    if current_branch:
        print(f"🌿 当前分支: {current_branch}")
    
    # 显示当前状态
    status = git_manager.get_status()
    if status:
        print(f"\n📊 当前状态:")
        print(status)
    else:
        print("\n✨ 工作目录干净，没有未提交的更改")
    
    # 选择分支
    selected_branch = select_branch(git_manager)
    if not selected_branch:
        print("\n👋 操作已取消")
        sys.exit(0)
    
    # 切换分支（如果需要）
    if selected_branch != current_branch:
        if not git_manager.switch_branch(selected_branch):
            sys.exit(1)
    
    # 添加所有文件
    print("\n📦 添加所有文件到暂存区...")
    if not git_manager.add_all_files():
        sys.exit(1)
    
    # 获取提交信息
    commit_message = input("\n💬 请输入提交信息 (默认: 'Update files'): ").strip()
    if not commit_message:
        commit_message = "Update files"
    
    # 提交更改
    print("\n💾 提交更改...")
    if not git_manager.commit_changes(commit_message):
        sys.exit(1)
    
    # 推送到远程
    print("\n🚀 推送到远程仓库...")
    if git_manager.push_to_remote(selected_branch):
        print("\n🎉 所有操作完成！文件已成功推送到Git仓库")
    else:
        print("\n❌ 推送失败，请检查网络连接和权限")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)