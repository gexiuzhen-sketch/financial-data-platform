@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo =========================================
echo 金融数据聚合平台 - 云端部署
echo =========================================
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker未安装
    echo 请先安装Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [√] Docker已安装

REM 检查Docker Compose是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    docker compose version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [错误] Docker Compose未安装
        echo 请先安装Docker Compose
        pause
        exit /b 1
    )
)
echo [√] Docker Compose已安装
echo.

REM 创建环境变量文件
if not exist .env (
    echo [创建] 环境变量文件 .env
    (
        echo # Flask配置
        echo FLASK_CONFIG=production
        echo SECRET_KEY=please-change-this-secret-key-in-production
        echo.
        echo # 数据库配置
        echo DATABASE_URL=sqlite:///data/database.db
        echo.
        echo # 日志级别
        echo LOG_LEVEL=INFO
    ) > .env
    echo [√] 环境变量文件已创建
) else (
    echo [跳过] 环境变量文件已存在
)
echo.

REM 构建Docker镜像
echo [构建] Docker镜像...
docker-compose build
if %errorlevel% neq 0 (
    echo [错误] 镜像构建失败
    pause
    exit /b 1
)
echo [√] 镜像构建完成
echo.

REM 启动服务
echo [启动] 服务...
docker-compose up -d
if %errorlevel% neq 0 (
    echo [错误] 服务启动失败
    pause
    exit /b 1
)
echo [√] 服务已启动
echo.

REM 等待后端服务启动
echo [等待] 后端服务启动...
timeout /t 10 /nobreak >nul

REM 初始化数据库
set /p init_db="是否需要初始化数据库? [Y/n]: "
if /i not "%init_db%"=="n" (
    echo [初始化] 数据库...
    docker-compose exec backend python run.py init_db
    echo [√] 数据库初始化完成
    echo.

    REM 插入示例数据
    set /p seed_data="是否需要插入示例数据? [Y/n]: "
    if /i not "%seed_data%"=="n" (
        echo [插入] 示例数据...
        docker-compose exec backend python run.py seed_data
        echo [√] 示例数据已插入
        echo.
    )
)

REM 检查服务状态
echo [检查] 服务状态...
docker-compose ps
echo.
echo 服务地址:
echo   前端: http://localhost
echo   后端API: http://localhost/api/v1
echo.

echo =========================================
echo [完成] 部署完成！
echo =========================================
echo.
echo 常用命令:
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose stop
echo   启动服务: docker-compose start
echo   重启服务: docker-compose restart
echo   删除服务: docker-compose down
echo.

pause
