@echo off
chcp 65001 >nul
echo ==========================================
echo           Git推送脚本启动器
echo ==========================================
echo.
echo 请选择要运行的脚本:
echo 1. 完整版Git推送脚本 (推荐)
echo 2. 简化版Git推送脚本
echo 3. 退出
echo.
set /p choice=请输入选择 (1-3): 

if "%choice%"=="1" (
    echo.
    echo 启动完整版Git推送脚本...
    python git_push_script.py
) else if "%choice%"=="2" (
    echo.
    echo 启动简化版Git推送脚本...
    python git_push_simple.py
) else if "%choice%"=="3" (
    echo 再见!
    exit /b 0
) else (
    echo 无效选择，请重新运行脚本
)

echo.
echo 按任意键退出...
pause >nul