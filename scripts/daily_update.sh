#!/bin/bash
# 每日数据更新脚本 (Linux/Mac)
# 使用 crontab 设置每日自动执行

set -e

# 设置项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${PROJECT_ROOT}/data_import"

# 切换到项目目录
cd "${PROJECT_ROOT}"

# 创建数据导入目录（如果不存在）
mkdir -p "${DATA_DIR}"
mkdir -p "${DATA_DIR}/processed"
mkdir -p "${PROJECT_ROOT}/backend/logs"

echo ""
echo "========================================"
echo "金融数据平台 - 每日数据更新"
echo "========================================"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 激活虚拟环境（如果使用）
# if [ -f "venv/bin/activate" ]; then
#     source venv/bin/activate
# fi

# 显示当前统计信息
echo "当前数据统计:"
python3 scripts/auto_update.py stats

echo ""
echo "========================================"

# 检查是否有新的数据文件需要导入
TODAY=$(date '+%Y%m%d')

if [ -f "${DATA_DIR}/platform_data.json" ]; then
    echo ""
    echo "导入平台数据..."
    if python3 scripts/auto_update.py import platform --file "${DATA_DIR}/platform_data.json"; then
        echo "平台数据导入成功，移动文件到已处理目录..."
        mv "${DATA_DIR}/platform_data.json" "${DATA_DIR}/processed/platform_data_${TODAY}.json"
    fi
fi

if [ -f "${DATA_DIR}/bank_data.json" ]; then
    echo ""
    echo "导入银行数据..."
    if python3 scripts/auto_update.py import bank --file "${DATA_DIR}/bank_data.json"; then
        echo "银行数据导入成功，移动文件到已处理目录..."
        mv "${DATA_DIR}/bank_data.json" "${DATA_DIR}/processed/bank_data_${TODAY}.json"
    fi
fi

echo ""
echo "更新后的统计信息:"
python3 scripts/auto_update.py stats

echo ""
echo "========================================"
echo "更新完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""
