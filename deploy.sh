#!/bin/bash

# 金融数据聚合平台 - 云端部署脚本

set -e

echo "========================================="
echo "金融数据聚合平台 - 云端部署"
echo "========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装${NC}"
        echo "请先安装Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker已安装${NC}"
}

# 检查Docker Compose是否安装
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}错误: Docker Compose未安装${NC}"
        echo "请先安装Docker Compose"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose已安装${NC}"
}

# 创建环境变量文件
create_env_file() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}创建环境变量文件 .env${NC}"
        cat > .env << EOF
# Flask配置
FLASK_CONFIG=production
SECRET_KEY=$(openssl rand -hex 32)

# 数据库配置
DATABASE_URL=sqlite:///data/database.db

# 日志级别
LOG_LEVEL=INFO
EOF
        echo -e "${GREEN}✓ 环境变量文件已创建${NC}"
    else
        echo -e "${YELLOW}环境变量文件已存在，跳过创建${NC}"
    fi
}

# 构建Docker镜像
build_images() {
    echo -e "${YELLOW}构建Docker镜像...${NC}"
    docker-compose build
    echo -e "${GREEN}✓ 镜像构建完成${NC}"
}

# 启动服务
start_services() {
    echo -e "${YELLOW}启动服务...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✓ 服务已启动${NC}"
}

# 初始化数据库
init_database() {
    echo -e "${YELLOW}初始化数据库...${NC}"
    docker-compose exec backend python run.py init_db
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
}

# 插入示例数据
seed_data() {
    echo -e "${YELLOW}插入示例数据...${NC}"
    docker-compose exec backend python run.py seed_data
    echo -e "${GREEN}✓ 示例数据已插入${NC}"
}

# 检查服务状态
check_status() {
    echo -e "${YELLOW}检查服务状态...${NC}"
    docker-compose ps
    echo ""
    echo -e "${GREEN}服务地址:${NC}"
    echo -e "  前端: http://localhost"
    echo -e "  后端API: http://localhost/api/v1"
}

# 显示日志
show_logs() {
    echo -e "${YELLOW}显示最近日志...${NC}"
    docker-compose logs --tail=20
}

# 主函数
main() {
    echo ""
    check_docker
    check_docker_compose
    echo ""

    create_env_file
    echo ""

    # 询问是否需要全新部署
    read -p "是否需要全新部署? (将删除现有数据) [y/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}停止并删除现有容器...${NC}"
        docker-compose down -v
    fi

    build_images
    echo ""

    start_services
    echo ""

    # 等待后端服务启动
    echo -e "${YELLOW}等待后端服务启动...${NC}"
    sleep 10

    # 初始化数据库
    read -p "是否需要初始化数据库? [Y/n]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        init_database
        echo ""

        # 插入示例数据
        read -p "是否需要插入示例数据? [Y/n]: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            seed_data
            echo ""
        fi
    fi

    check_status
    echo ""

    echo "========================================="
    echo -e "${GREEN}部署完成！${NC}"
    echo "========================================="
    echo ""
    echo "常用命令:"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose stop"
    echo "  启动服务: docker-compose start"
    echo "  重启服务: docker-compose restart"
    echo "  删除服务: docker-compose down"
    echo ""
}

# 运行主函数
main
