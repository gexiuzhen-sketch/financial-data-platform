# 多阶段构建 - 后端
FROM python:3.10-slim as backend

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=run.py
ENV FLASK_CONFIG=production
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "run:app"]


# 多阶段构建 - 前端
FROM node:18-alpine as frontend

WORKDIR /app

# 复制依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm install

# 复制前端代码
COPY frontend/ .

# 构建前端
RUN npm run build


# Nginx阶段
FROM nginx:alpine

# 复制前端构建产物
COPY --from=frontend /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 复制后端到单独目录
COPY --from=backend /app /backend

# 暴露端口
EXPOSE 80 443

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
