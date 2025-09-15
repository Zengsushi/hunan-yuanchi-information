@echo off
chcp 65001 >nul
echo ========================================
echo Tahoe-100M 数据集下载脚本
echo 镜像站: https://hf-mirror.com
echo ========================================
echo.

REM 激活虚拟环境（如果存在）
if exist "myvenv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call myvenv\Scripts\activate.bat
)

REM 设置镜像站环境变量
set HF_ENDPOINT=https://hf-mirror.com
echo 已设置镜像站地址: %HF_ENDPOINT%
echo.

REM 运行Python脚本
echo 启动下载脚本...
python download_tahoe_dataset.py

echo.
echo 按任意键退出...
pause >nul