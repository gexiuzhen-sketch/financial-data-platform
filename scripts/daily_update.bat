@echo off
REM 每日数据更新脚本 (Windows)
REM 使用 Windows 任务计划程序设置每日自动执行

setlocal

REM 设置项目根目录
set PROJECT_ROOT=E:\Claude Code\financial_data_platform
set DATA_DIR=%PROJECT_ROOT%\data_import

REM 切换到项目目录
cd /d "%PROJECT_ROOT%"

REM 创建数据导入目录（如果不存在）
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

echo.
echo ========================================
echo 金融数据平台 - 每日数据更新
echo ========================================
echo 开始时间: %date% %time%
echo.

REM 激活虚拟环境（如果使用）
REM call venv\Scripts\activate.bat

REM 显示当前统计信息
echo 当前数据统计:
python scripts\auto_update.py stats

echo.
echo ========================================

REM 检查是否有新的数据文件需要导入
if exist "%DATA_DIR%\platform_data.json" (
    echo.
    echo 导入平台数据...
    python scripts\auto_update.py import platform --file "%DATA_DIR%\platform_data.json"
    if %errorlevel% equ 0 (
        echo 平台数据导入成功，移动文件到已处理目录...
        if not exist "%DATA_DIR%\processed" mkdir "%DATA_DIR%\processed"
        move "%DATA_DIR%\platform_data.json" "%DATA_DIR%\processed\platform_data_%date:~0,4%%date:~5,2%%date:~8,2%.json"
    )
)

if exist "%DATA_DIR%\bank_data.json" (
    echo.
    echo 导入银行数据...
    python scripts\auto_update.py import bank --file "%DATA_DIR%\bank_data.json"
    if %errorlevel% equ 0 (
        echo 银行数据导入成功，移动文件到已处理目录...
        if not exist "%DATA_DIR%\processed" mkdir "%DATA_DIR%\processed"
        move "%DATA_DIR%\bank_data.json" "%DATA_DIR%\processed\bank_data_%date:~0,4%%date:~5,2%%date:~8,2%.json"
    )
)

echo.
echo 更新后的统计信息:
python scripts\auto_update.py stats

echo.
echo ========================================
echo 更新完成时间: %date% %time%
echo ========================================
echo.

REM 按任意键退出（如果手动运行）
REM pause

endlocal
