# 金融数据聚合平台

一个用于抓取和展示中国头部互联网助贷平台贷款规模数据的数据聚合网站。

## 功能特性

- **数据抓取**: 自动从研究报告、上市公司财报、官方监管数据、财经媒体等多渠道抓取数据
- **数据展示**: 支持按平台、集团、产品类型、贷款用途等多维度筛选和展示
- **数据导出**: 支持将数据导出为Excel格式（.xlsx/.xls）
- **定时更新**: 内置定时任务，自动执行数据抓取和更新
- **统计分析**: 提供数据概览、趋势分析等统计功能

## 技术栈

**后端**:
- Python 3.8+
- Flask - Web框架
- SQLAlchemy - ORM
- APScheduler - 定时任务
- pandas - 数据处理
- requests/BeautifulSoup4 - 数据抓取

**前端**:
- Vue.js 3
- Element Plus - UI组件库
- ECharts - 数据可视化
- Vite - 构建工具

## 项目结构

```
financial_data_platform/
├── backend/                      # Flask后端
│   ├── app/
│   │   ├── models/              # 数据模型
│   │   ├── api/                 # API接口
│   │   ├── scrapers/            # 爬虫模块
│   │   ├── services/            # 业务逻辑
│   │   └── utils/               # 工具函数
│   ├── data/                    # 数据存储
│   ├── logs/                    # 日志目录
│   ├── requirements.txt         # Python依赖
│   └── run.py                   # 启动脚本
│
└── frontend/                     # Vue.js前端
    └── src/
        ├── components/          # 组件
        ├── views/               # 页面
        ├── api/                 # API调用
        └── router/              # 路由配置
```

## 快速开始

### 方式一：一键启动（Windows）

```cmd
quickstart.bat
```

### 方式二：Docker云端部署

```bash
# 部署到云端服务器（外部访问）
./deploy.sh        # Linux/Mac
deploy.bat         # Windows
```

详见 [DEPLOYMENT.md](DEPLOYMENT.md) 云端部署指南

### 方式三：手动启动

#### 后端设置

1. 安装Python依赖:
```bash
cd backend
pip install -r requirements.txt
```

2. 初始化数据库:
```bash
python run.py init_db
python run.py seed_data
```

3. 启动后端服务:
```bash
python run.py
```

后端服务将在 `http://localhost:5000` 启动

#### 前端设置

1. 安装依赖:
```bash
cd frontend
npm install
```

2. 启动开发服务器:
```bash
npm run dev
```

前端服务将在 `http://localhost:5173` 启动

## API接口

### 平台数据接口

- `GET /api/v1/platforms` - 获取所有平台列表
- `GET /api/v1/platforms/data` - 获取平台数据（支持筛选）
- `GET /api/v1/platforms/stats/overview` - 获取数据概览
- `GET /api/v1/platforms/{id}` - 获取单个平台详情
- `GET /api/v1/platforms/{id}/timeline` - 获取平台时间序列数据

### 银行数据接口

- `GET /api/v1/banks` - 获取所有银行列表
- `GET /api/v1/banks/data` - 获取银行数据（支持筛选）
- `GET /api/v1/banks/stats/overview` - 获取银行数据概览
- `GET /api/v1/banks/{id}` - 获取单个银行详情
- `GET /api/v1/banks/{id}/timeline` - 获取银行时间序列数据

### 导出接口

- `POST /api/v1/export/platform` - 导出平台数据为Excel
- `POST /api/v1/export/bank` - 导出银行数据为Excel

## 爬虫数据源

### 优先级1: 研究报告
- 艾瑞咨询
- 易观分析
- 零壹智库

### 优先级2: 上市公司财报
- 蚂蚁集团
- 京东科技
- 陆金所

### 优先级3: 官方监管数据
- 中国人民银行
- 银保监会

### 优先级4: 财经媒体
- 新浪财经
- 网易财经
- 搜狐财经

## 定时任务配置

| 数据源 | 更新频率 | 执行时间 |
|--------|----------|----------|
| 研究报告爬虫 | 周度 | 每周一 10:00 |
| 上市公司财报爬虫 | 季度 | 每季度首月5日 10:00 |
| 官方监管数据爬虫 | 月度 | 每月15日 10:00 |
| 财经媒体爬虫 | 每日 | 每天 09:00 |

## 数据模型

### 平台数据 (platforms)

| 字段 | 类型 | 说明 |
|------|------|------|
| name | String | 平台名称 |
| company_group | String | 所属集团（蚂蚁/腾讯/字节/京东/美团/百度） |
| platform_type | String | 产品类别（助贷/联合贷） |
| loan_type | String | 贷款用途（消费类/经营类） |
| report_month | Date | 报告月份 |
| loan_balance | Float | 贷款余额（亿元） |
| loan_issued | Float | 发放规模（亿元） |
| yoy_growth | Float | 同比增长率（%） |
| mom_growth | Float | 环比增长率（%） |
| data_source | String | 数据来源 |

### 银行数据 (banks)

| 字段 | 类型 | 说明 |
|------|------|------|
| name | String | 银行名称 |
| bank_type | String | 银行类型（股份制/国有/城商行等） |
| report_month | Date | 报告月份 |
| total_internet_loan | Float | 互联网贷款总规模（亿元） |
| coop_platform_count | Integer | 合作平台数量 |
| top3_platform_share | Float | 前3大平台占比（%） |
| data_source | String | 数据来源 |

## 环境变量

创建 `.env` 文件（可选）:

```env
FLASK_CONFIG=development
SECRET_KEY=your-secret-key
```

## 注意事项

1. **反爬虫策略**: 爬虫内置了随机User-Agent、延迟请求等反爬虫策略，但仍需注意控制请求频率
2. **数据质量**: 由于数据来源多样，建议对抓取的数据进行人工审核
3. **法律合规**: 请遵守相关网站的robots.txt协议，合理使用抓取的数据
4. **备份建议**: 定期备份数据库文件 `backend/data/database.db`

## 许可证

MIT License
