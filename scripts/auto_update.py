#!/usr/bin/env python3
"""
自动化数据更新脚本
用于每日批量更新金融数据平台数据
支持从CSV/Excel文件导入数据，也支持API方式导入
"""
import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app import create_app, db
from backend.app.models import Platform, Bank


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / 'backend' / 'logs' / 'auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataUpdater:
    """数据更新器"""

    def __init__(self, app):
        self.app = app

    def import_from_json(self, data_type, json_file):
        """
        从JSON文件导入数据

        Args:
            data_type: 数据类型 ('platform' 或 'bank')
            json_file: JSON文件路径
        """
        with self.app.app_context():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)

                count = 0
                for data in data_list:
                    try:
                        if data_type == 'platform':
                            self._create_platform(data)
                        elif data_type == 'bank':
                            self._create_bank(data)
                        count += 1
                    except Exception as e:
                        logger.warning(f"导入单条数据失败: {str(e)}")
                        continue

                db.session.commit()
                logger.info(f"成功导入 {count} 条{data_type}数据")
                return count

            except Exception as e:
                db.session.rollback()
                logger.error(f"导入失败: {str(e)}")
                return 0

    def _create_platform(self, data):
        """创建平台数据"""
        report_month = None
        if data.get('report_month'):
            report_month = datetime.strptime(data['report_month'], '%Y-%m')

        platform = Platform(
            name=data.get('name'),
            company_group=data.get('company_group'),
            platform_type=data.get('platform_type'),
            loan_type=data.get('loan_type'),
            report_month=report_month,
            loan_balance=data.get('loan_balance'),
            loan_issued=data.get('loan_issued'),
            yoy_growth=data.get('yoy_growth'),
            mom_growth=data.get('mom_growth'),
            data_source=data.get('data_source', '自动导入'),
            source_url=data.get('source_url')
        )
        db.session.add(platform)

    def _create_bank(self, data):
        """创建银行数据"""
        report_month = None
        if data.get('report_month'):
            report_month = datetime.strptime(data['report_month'], '%Y-%m')

        bank = Bank(
            name=data.get('name'),
            bank_type=data.get('bank_type'),
            report_month=report_month,
            total_internet_loan=data.get('total_internet_loan'),
            coop_platform_count=data.get('coop_platform_count'),
            top3_platform_share=data.get('top3_platform_share'),
            data_source=data.get('data_source', '自动导入'),
            source_url=data.get('source_url')
        )
        db.session.add(bank)

    def delete_by_date_range(self, data_type, start_month, end_month):
        """
        按日期范围删除数据

        Args:
            data_type: 数据类型 ('platform', 'bank', 'all')
            start_month: 开始月份 (YYYY-MM)
            end_month: 结束月份 (YYYY-MM)
        """
        with self.app.app_context():
            try:
                start_date = datetime.strptime(start_month, '%Y-%m')
                end_date = datetime.strptime(end_month, '%Y-%m')

                deleted_count = 0

                if data_type in ['platform', 'all']:
                    query = db.session.query(Platform).filter(
                        Platform.report_month >= start_date,
                        Platform.report_month <= end_date
                    )
                    deleted_count += query.count()
                    query.delete()

                if data_type in ['bank', 'all']:
                    query = db.session.query(Bank).filter(
                        Bank.report_month >= start_date,
                        Bank.report_month <= end_date
                    )
                    deleted_count += query.count()
                    query.delete()

                db.session.commit()
                logger.info(f"删除 {deleted_count} 条{data_type}数据")
                return deleted_count

            except Exception as e:
                db.session.rollback()
                logger.error(f"删除失败: {str(e)}")
                return 0

    def get_stats(self):
        """获取数据统计"""
        with self.app.app_context():
            platform_count = db.session.query(Platform).count()
            bank_count = db.session.query(Bank).count()

            from sqlalchemy import func
            latest_platform_month = db.session.query(func.max(Platform.report_month)).scalar()
            latest_bank_month = db.session.query(func.max(Bank.report_month)).scalar()

            return {
                'platform_count': platform_count,
                'bank_count': bank_count,
                'latest_platform_month': latest_platform_month.strftime('%Y-%m') if latest_platform_month else None,
                'latest_bank_month': latest_bank_month.strftime('%Y-%m') if latest_bank_month else None
            }


def create_sample_data(output_dir):
    """创建示例数据文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 示例平台数据
    platform_data = [
        {
            "name": "花呗",
            "company_group": "蚂蚁",
            "platform_type": "联合贷",
            "loan_type": "消费类",
            "report_month": datetime.now().strftime('%Y-%m'),
            "loan_balance": 1850.5,
            "loan_issued": 330.8,
            "yoy_growth": 16.2,
            "mom_growth": 2.8,
            "data_source": "月度更新"
        },
        {
            "name": "借呗",
            "company_group": "蚂蚁",
            "platform_type": "助贷",
            "loan_type": "消费类",
            "report_month": datetime.now().strftime('%Y-%m'),
            "loan_balance": 1250.3,
            "loan_issued": 260.6,
            "yoy_growth": 13.8,
            "mom_growth": 2.1,
            "data_source": "月度更新"
        },
        {
            "name": "微粒贷",
            "company_group": "腾讯",
            "platform_type": "联合贷",
            "loan_type": "消费类",
            "report_month": datetime.now().strftime('%Y-%m'),
            "loan_balance": 2150.8,
            "loan_issued": 390.2,
            "yoy_growth": 19.5,
            "mom_growth": 3.5,
            "data_source": "月度更新"
        },
        {
            "name": "京东金条",
            "company_group": "京东",
            "platform_type": "联合贷",
            "loan_type": "消费类",
            "report_month": datetime.now().strftime('%Y-%m'),
            "loan_balance": 780.3,
            "loan_issued": 175.4,
            "yoy_growth": 23.1,
            "mom_growth": 4.8,
            "data_source": "月度更新"
        },
        {
            "name": "美团借钱",
            "company_group": "美团",
            "platform_type": "助贷",
            "loan_type": "消费类",
            "report_month": datetime.now().strftime('%Y-%m'),
            "loan_balance": 450.8,
            "loan_issued": 95.2,
            "yoy_growth": 38.6,
            "mom_growth": 6.2,
            "data_source": "月度更新"
        }
    ]

    # 示例银行数据
    bank_data = [
        {
            "name": "招商银行",
            "bank_type": "股份制",
            "report_month": datetime.now().strftime('%Y-%m'),
            "total_internet_loan": 5950.5,
            "coop_platform_count": 13,
            "top3_platform_share": 65.5,
            "data_source": "月度更新"
        },
        {
            "name": "兴业银行",
            "bank_type": "股份制",
            "report_month": datetime.now().strftime('%Y-%m'),
            "total_internet_loan": 4350.3,
            "coop_platform_count": 11,
            "top3_platform_share": 62.3,
            "data_source": "月度更新"
        },
        {
            "name": "平安银行",
            "bank_type": "股份制",
            "report_month": datetime.now().strftime('%Y-%m'),
            "total_internet_loan": 5250.8,
            "coop_platform_count": 12,
            "top3_platform_share": 68.2,
            "data_source": "月度更新"
        }
    ]

    # 写入文件
    with open(output_dir / 'sample_platform_data.json', 'w', encoding='utf-8') as f:
        json.dump(platform_data, f, ensure_ascii=False, indent=2)

    with open(output_dir / 'sample_bank_data.json', 'w', encoding='utf-8') as f:
        json.dump(bank_data, f, ensure_ascii=False, indent=2)

    logger.info(f"示例数据已创建到: {output_dir}")
    return output_dir


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='金融数据平台自动化更新脚本')
    parser.add_argument('action', choices=['import', 'delete', 'stats', 'sample'],
                        help='操作类型: import(导入数据), delete(删除数据), stats(统计信息), sample(创建示例数据)')
    parser.add_argument('--type', choices=['platform', 'bank', 'all'], default='platform',
                        help='数据类型')
    parser.add_argument('--file', help='JSON文件路径')
    parser.add_argument('--start', help='开始月份 (YYYY-MM)')
    parser.add_argument('--end', help='结束月份 (YYYY-MM)')
    parser.add_argument('--output', default='./data_import',
                        help='示例数据输出目录 (用于sample命令)')

    args = parser.parse_args()

    # 创建Flask应用
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    updater = DataUpdater(app)

    if args.action == 'import':
        if not args.file:
            logger.error("导入操作需要指定 --file 参数")
            return 1

        if not os.path.exists(args.file):
            logger.error(f"文件不存在: {args.file}")
            return 1

        count = updater.import_from_json(args.type, args.file)
        return 0 if count > 0 else 1

    elif args.action == 'delete':
        if not args.start or not args.end:
            logger.error("删除操作需要指定 --start 和 --end 参数")
            return 1

        count = updater.delete_by_date_range(args.type, args.start, args.end)
        return 0 if count >= 0 else 1

    elif args.action == 'stats':
        stats = updater.get_stats()
        print("\n=== 数据统计 ===")
        print(f"平台数据: {stats['platform_count']} 条")
        print(f"银行数据: {stats['bank_count']} 条")
        print(f"最新平台数据月份: {stats['latest_platform_month'] or '无'}")
        print(f"最新银行数据月份: {stats['latest_bank_month'] or '无'}")
        print()
        return 0

    elif args.action == 'sample':
        create_sample_data(args.output)
        return 0


if __name__ == '__main__':
    sys.exit(main())
