# 云端部署指南

本文档介绍如何将金融数据聚合平台部署到云服务器，使其可以被外部人员访问。

## 前置要求

- 云服务器（阿里云、腾讯云、AWS等）
- 服务器已安装 Docker 和 Docker Compose
- 域名（可选，但推荐）

## 快速部署

### 方法一：使用部署脚本（推荐）

**Linux/Mac:**
```bash
# 1. 上传项目文件到服务器
scp -r financial_data_platform user@your-server:/home/user/

# 2. 登录服务器
ssh user@your-server

# 3. 进入项目目录
cd financial_data_platform

# 4. 添加执行权限
chmod +x deploy.sh

# 5. 运行部署脚本
./deploy.sh
```

**Windows:**
```cmd
# 1. 上传项目文件到服务器（使用WinSCP、FileZilla等工具）

# 2. 登录服务器（使用PowerShell或SSH客户端）

# 3. 进入项目目录
cd financial_data_platform

# 4. 运行部署脚本
deploy.bat
```

### 方法二：手动部署

```bash
# 1. 创建环境变量文件
cp .env.example .env

# 2. 编辑.env文件，修改SECRET_KEY
nano .env

# 3. 构建镜像
docker-compose build

# 4. 启动服务
docker-compose up -d

# 5. 初始化数据库
docker-compose exec backend python run.py init_db

# 6. 插入示例数据（可选）
docker-compose exec backend python run.py seed_data
```

## 访问网站

部署成功后，可以通过以下方式访问：

- **HTTP访问**: `http://your-server-ip`
- **HTTPS访问**: 需要配置SSL证书（见下文）

## 配置域名和HTTPS

### 1. 配置域名解析

在域名提供商处添加A记录：
```
类型: A
主机记录: @
记录值: your-server-ip
```

### 2. 配置SSL证书（使用Let's Encrypt）

```bash
# 安装certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

### 3. 更新Nginx配置

修改 `nginx.conf` 添加HTTPS配置：

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # 其他配置...
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose stop

# 启动服务
docker-compose start

# 删除服务（保留数据）
docker-compose down

# 删除服务（删除数据）
docker-compose down -v

# 进入后端容器
docker-compose exec backend bash

# 数据库备份
docker-compose exec backend cp data/database.db data/database_backup_$(date +%Y%m%d).db
```

## 监控和维护

### 1. 查看资源使用情况

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker-compose exec backend df -h
```

### 2. 日志管理

```bash
# 查看后端日志
docker-compose exec backend tail -f logs/app.log

# 查看Nginx访问日志
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

### 3. 数据备份

```bash
# 备份数据库
docker-compose exec backend python -c "
import shutil
from datetime import datetime
shutil.copy('data/database.db', f'data/backup_{datetime.now().strftime(\"%Y%m%d\")}.db')
"

# 备份到本地
docker cp financial-data-backend:/app/data/database.db ./backup_$(date +%Y%m%d).db
```

## 性能优化

### 1. 调整Gunicorn配置

编辑 `Dockerfile` 中的Gunicorn启动命令：

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "run:app"]
```

### 2. 启用缓存

在后端添加Redis缓存（可选）：

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:alpine
    restart: always
```

### 3. CDN加速

将静态资源部署到CDN（如阿里云OSS、腾讯云COS等）。

## 故障排除

### 1. 服务无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查端口占用
netstat -tulpn | grep 5000
```

### 2. 数据库连接失败

```bash
# 检查数据库文件
docker-compose exec backend ls -la data/

# 重新初始化数据库
docker-compose exec backend python run.py init_db
```

### 3. 前端无法访问后端API

检查 `nginx.conf` 中的代理配置是否正确：

```nginx
location /api/ {
    proxy_pass http://backend;
    ...
}
```

## 安全建议

1. **修改默认SECRET_KEY**: 在 `.env` 文件中使用强随机密钥
2. **启用HTTPS**: 使用SSL证书加密通信
3. **限制访问**: 使用防火墙限制访问端口
4. **定期备份**: 定期备份数据库
5. **更新依赖**: 定期更新Docker镜像和依赖包
6. **监控日志**: 定期检查访问日志和错误日志

## 扩展部署

### 部署到Kubernetes

如果需要部署到K8s集群，可以参考以下配置：

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: financial-data-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/financial-data-backend:latest
        ports:
        - containerPort: 5000
```

## 联系支持

如有问题，请查看：
- 项目README.md
- 日志文件
- Docker文档: https://docs.docker.com/
