# 金融数据聚合平台 - 项目总结

## 项目概述

本项目已完整实现一个金融数据聚合网站，支持抓取和展示中国头部互联网助贷平台的贷款规模数据，以及全国股份制银行与平台合作的互联网贷款业务数据。

**部署方式**:
- ✅ 本地开发运行
- ✅ 云端部署（Docker + Nginx）
- ✅ 外部访问支持

## 已完成功能

### 后端（Python Flask）

#### 1. 数据模型
- [x] `platform.py` - 平台数据模型
- [x] `bank.py` - 银行数据模型
- [x] `source.py` - 数据源配置模型

#### 2. 爬虫模块
- [x] `base.py` - 基础爬虫类（含反爬虫策略）
- [x] `research.py` - 研究报告爬虫（艾瑞、易观、零壹智库）
- [x] `corporate.py` - 上市公司财报爬虫（蚂蚁、京东、陆金所）
- [x] `official.py` - 官方监管数据爬虫（人行、银保监会）
- [x] `media.py` - 财经媒体爬虫（新浪、网易、搜狐）

#### 3. API接口
- [x] 平台数据API（查询、筛选、统计、详情、时间序列）
- [x] 银行数据API（查询、筛选、统计、详情、时间序列）
- [x] Excel导出API（支持XLS/XLSX格式）

#### 4. 定时任务
- [x] 研究报告爬虫 - 每周一10:00
- [x] 上市公司财报爬虫 - 每季度首月5日10:00
- [x] 官方监管数据爬虫 - 每月15日10:00
- [x] 财经媒体爬虫 - 每天09:00

### 前端（Vue.js 3）

#### 1. 页面组件
- [x] `App.vue` - 根组件
- [x] `Home.vue` - 首页数据概览
- [x] `PlatformData.vue` - 平台数据展示页（筛选、导出）
- [x] `BankData.vue` - 银行数据展示页（筛选、导出）

#### 2. 功能特性
- [x] 多维度筛选（集团、类型、用途、月份）
- [x] 数据分页
- [x] Excel导出
- [x] 数据概览统计

### 云端部署

#### 1. Docker配置
- [x] `Dockerfile` - 多阶段构建配置
- [x] `docker-compose.yml` - 服务编排
- [x] `nginx.conf` - Nginx反向代理配置

#### 2. 部署脚本
- [x] `deploy.sh` - Linux/Mac部署脚本
- [x] `deploy.bat` - Windows部署脚本
- [x] `quickstart.bat` - 一键启动脚本

#### 3. 配置文件
- [x] `.env.example` - 环境变量模板
- [x] `DEPLOYMENT.md` - 部署文档

## 项目文件结构

```
financial_data_platform/
├── backend/                          # 后端目录
│   ├── app/
│   │   ├── __init__.py              # Flask应用工厂
│   │   ├── config.py                # 配置文件
│   │   ├── models/                  # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── platform.py          # 平台模型
│   │   │   ├── bank.py              # 银行模型
│   │   │   └── source.py            # 数据源模型
│   │   ├── api/                     # API接口
│   │   │   ├── __init__.py
│   │   │   ├── platform.py          # 平台API
│   │   │   ├── bank.py              # 银行API
│   │   │   └── export.py            # 导出API
│   │   ├── scrapers/                # 爬虫模块
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # 基础爬虫
│   │   │   ├── research.py          # 研究报告爬虫
│   │   │   ├── corporate.py         # 财报爬虫
│   │   │   ├── official.py          # 官方数据爬虫
│   │   │   └── media.py             # 媒体爬虫
│   │   ├── services/                # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   └── scheduler.py         # 定时任务
│   │   └── utils/                   # 工具函数
│   ├── requirements.txt             # Python依赖
│   └── run.py                       # 启动脚本
│
├── frontend/                         # 前端目录
│   ├── index.html                   # HTML入口
│   ├── package.json                 # 依赖配置
│   ├── vite.config.js               # Vite配置
│   └── src/
│       ├── main.js                  # JS入口
│       ├── App.vue                  # 根组件
│       ├── router/
│       │   └── index.js             # 路由配置
│       ├── api/
│       │   └── index.js             # API封装
│       └── views/
│           ├── Home.vue             # 首页
│           ├── PlatformData.vue     # 平台数据页
│           └── BankData.vue         # 银行数据页
│
├── Dockerfile                        # Docker镜像配置
├── docker-compose.yml                # Docker编排
├── nginx.conf                        # Nginx配置
├── deploy.sh                         # Linux/Mac部署脚本
├── deploy.bat                        # Windows部署脚本
├── quickstart.bat                    # 快速启动脚本
├── .env.example                      # 环境变量模板
├── README.md                         # 项目说明
└── DEPLOYMENT.md                     # 部署文档
```

## 技术栈

### 后端
- Python 3.10+
- Flask 3.0
- SQLAlchemy 2.0
- Gunicorn 21.2
- APScheduler 3.10
- pandas 2.2
- requests 2.31
- BeautifulSoup4 4.12

### 前端
- Vue.js 3.4
- Element Plus 2.4
- Vite 5.0
- Axios 1.6
- ECharts 5.4

### 部署
- Docker
- Docker Compose
- Nginx (Alpine)

## 快速启动

### 本地开发

**Windows一键启动:**
```cmd
quickstart.bat
```

**手动启动:**
```bash
# 后端
cd backend
pip install -r requirements.txt
python run.py init_db
python run.py seed_data
python run.py

# 前端
cd frontend
npm install
npm run dev
```

### 云端部署

**Linux/Mac:**
```bash
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

部署完成后，网站将可通过 `http://your-server-ip` 外部访问

## API端点

### 平台数据
- `GET /api/v1/platforms` - 平台列表
- `GET /api/v1/platforms/data` - 平台数据（筛选）
- `GET /api/v1/platforms/stats/overview` - 数据概览

### 银行数据
- `GET /api/v1/banks` - 银行列表
- `GET /api/v1/banks/data` - 银行数据（筛选）
- `GET /api/v1/banks/stats/overview` - 数据概览

### 导出
- `POST /api/v1/export/platform` - 导出平台数据
- `POST /api/v1/export/bank` - 导出银行数据

## 数据源

| 类型 | 来源 | 频率 |
|-----|------|------|
| 研究报告 | 艾瑞、易观、零壹智库 | 每周一 |
| 财报 | 蚂蚁、京东、陆金所 | 每季度 |
| 官方 | 人行、银保监会 | 每月15日 |
| 媒体 | 新浪、网易、搜狐 | 每天 |

## 安全建议

1. 修改 `.env` 中的 `SECRET_KEY`
2. 配置HTTPS（使用Let's Encrypt）
3. 限制服务器防火墙规则
4. 定期备份数据库
5. 监控访问日志

## 维护命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 备份数据库
docker-compose exec backend cp data/database.db data/backup.db

# 更新代码后重新部署
docker-compose down
docker-compose build
docker-compose up -d
```

## 许可证

MIT License
