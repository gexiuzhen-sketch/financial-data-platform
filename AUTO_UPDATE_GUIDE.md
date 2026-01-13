# 自动化数据更新指南

本指南介绍如何使用自动化脚本进行数据批量更新。

## 目录

- [快速开始](#快速开始)
- [命令行工具](#命令行工具)
- [定时任务设置](#定时任务设置)
- [数据格式说明](#数据格式说明)

## 快速开始

### 1. 生成示例数据

```bash
# Python 方式
python scripts/auto_update.py sample --output ./data_import

# 查看统计信息
python scripts/auto_update.py stats
```

### 2. 导入数据

```bash
# 导入平台数据
python scripts/auto_update.py import platform --file ./data_import/sample_platform_data.json

# 导入银行数据
python scripts/auto_update.py import bank --file ./data_import/sample_bank_data.json
```

## 命令行工具

### auto_update.py

自动化数据更新脚本，支持导入、删除、统计等操作。

#### 命令格式

```bash
python scripts/auto_update.py <action> [options]
```

#### 操作类型

##### 1. 导入数据 (import)

从JSON文件导入平台或银行数据。

```bash
# 导入平台数据
python scripts/auto_update.py import platform --file ./data_import/platform_data.json

# 导入银行数据
python scripts/auto_update.py import bank --file ./data_import/bank_data.json
```

**参数:**
- `--type`: 数据类型 (platform/bank/all)
- `--file`: JSON文件路径

##### 2. 删除数据 (delete)

按日期范围删除数据。

```bash
# 删除指定月份的平台数据
python scripts/auto_update.py delete platform --start 2024-01 --end 2024-03

# 删除指定月份的所有数据
python scripts/auto_update.py delete all --start 2024-01 --end 2024-03
```

**参数:**
- `--type`: 数据类型 (platform/bank/all)
- `--start`: 开始月份 (YYYY-MM)
- `--end`: 结束月份 (YYYY-MM)

##### 3. 查看统计 (stats)

查看当前数据统计信息。

```bash
python scripts/auto_update.py stats
```

输出示例:
```
=== 数据统计 ===
平台数据: 15 条
银行数据: 6 条
最新平台数据月份: 2024-12
最新银行数据月份: 2024-12
```

##### 4. 生成示例数据 (sample)

创建示例数据文件用于测试。

```bash
# 使用默认输出目录
python scripts/auto_update.py sample

# 指定输出目录
python scripts/auto_update.py sample --output ./my_data
```

## 定时任务设置

### Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器（例如：每天上午9点）
4. 操作：启动程序
   - 程序：`python.exe`
   - 参数：`scripts\auto_update.py import platform --file data_import\platform_data.json`
   - 起始于：`E:\Claude Code\financial_data_platform`

或使用批处理脚本：

```batch
# 直接运行每日更新脚本
scripts\daily_update.bat
```

### Linux/Mac Cron

1. 编辑 crontab:
```bash
crontab -e
```

2. 添加定时任务（每天上午9点执行）:
```bash
0 9 * * * cd /path/to/financial_data_platform && ./scripts/daily_update.sh >> logs/cron.log 2>&1
```

3. 查看已设置的任务:
```bash
crontab -l
```

## 数据格式说明

### 平台数据 JSON 格式

```json
[
  {
    "name": "花呗",
    "company_group": "蚂蚁",
    "platform_type": "联合贷",
    "loan_type": "消费类",
    "report_month": "2024-12",
    "loan_balance": 1800.5,
    "loan_issued": 320.8,
    "yoy_growth": 15.2,
    "mom_growth": 2.5,
    "data_source": "月度更新",
    "source_url": ""
  }
]
```

**字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 平台名称 |
| company_group | string | 否 | 所属集团（蚂蚁/腾讯/字节/京东/美团/百度） |
| platform_type | string | 否 | 产品类别（助贷/联合贷） |
| loan_type | string | 否 | 贷款用途（消费类/经营类） |
| report_month | string | 是 | 报告月份 (YYYY-MM) |
| loan_balance | number | 否 | 贷款余额（亿元） |
| loan_issued | number | 否 | 发放规模（亿元） |
| yoy_growth | number | 否 | 同比增长率（%） |
| mom_growth | number | 否 | 环比增长率（%） |
| data_source | string | 否 | 数据来源 |
| source_url | string | 否 | 来源URL |

### 银行数据 JSON 格式

```json
[
  {
    "name": "招商银行",
    "bank_type": "股份制",
    "report_month": "2024-12",
    "total_internet_loan": 5800.5,
    "coop_platform_count": 12,
    "top3_platform_share": 65.5,
    "data_source": "月度更新",
    "source_url": ""
  }
]
```

**字段说明:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 银行名称 |
| bank_type | string | 否 | 银行类型（股份制/国有/城商行） |
| report_month | string | 是 | 报告月份 (YYYY-MM) |
| total_internet_loan | number | 否 | 互联网贷款总规模（亿元） |
| coop_platform_count | number | 否 | 合作平台数量 |
| top3_platform_share | number | 否 | 前3大平台占比（%） |
| data_source | string | 否 | 数据来源 |
| source_url | string | 否 | 来源URL |

## 使用场景

### 场景1: 每日自动更新

1. 将数据文件放到 `data_import` 目录
2. 设置定时任务执行 `daily_update.bat` 或 `daily_update.sh`
3. 脚本会自动导入数据并移动到已处理目录

### 场景2: 手动导入历史数据

1. 准备 JSON 格式的数据文件
2. 使用命令行工具导入:

```bash
python scripts/auto_update.py import platform --file ./my_data.json
```

### 场景3: 更新某个月份的数据

1. 先删除旧数据:

```bash
python scripts/auto_update.py delete platform --start 2024-11 --end 2024-11
```

2. 再导入新数据:

```bash
python scripts/auto_update.py import platform --file ./new_data.json
```

## 日志

自动化操作的日志保存在 `backend/logs/auto_update.log`。

查看日志:
```bash
# Windows
type backend\logs\auto_update.log

# Linux/Mac
tail -f backend/logs/auto_update.log
```

## 故障排除

### 问题1: 导入失败

检查 JSON 文件格式是否正确:
```bash
python -m json.tool data.json
```

### 问题2: 定时任务不执行

1. 检查任务是否正确设置
2. 检查日志文件查看错误信息
3. 确保Python路径正确

### 问题3: 数据重复

在导入前先删除对应月份的数据:
```bash
python scripts/auto_update.py delete platform --start 2024-12 --end 2024-12
```
