"""
Flask应用启动脚本
"""
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import Platform, Bank, DataSource

# 创建应用实例
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# 初始化调度器
from app.services import scheduler
scheduler.init_app(app)


@app.shell_context_processor
def make_shell_context():
    """注册shell上下文"""
    return {
        'db': db,
        'Platform': Platform,
        'Bank': Bank,
        'DataSource': DataSource
    }


@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成')


@app.cli.command()
def seed_data():
    """插入示例数据"""
    from datetime import datetime

    # 检查是否已有数据
    if Platform.query.first():
        print('数据库已有数据，跳过插入')
        return

    # 插入平台示例数据
    platforms = [
        Platform(
            name='花呗',
            company_group='蚂蚁',
            platform_type='联合贷',
            loan_type='消费类',
            report_month=datetime(2024, 12, 1),
            loan_balance=1800.5,
            loan_issued=320.8,
            yoy_growth=15.2,
            mom_growth=2.5,
            data_source='示例数据'
        ),
        Platform(
            name='借呗',
            company_group='蚂蚁',
            platform_type='助贷',
            loan_type='消费类',
            report_month=datetime(2024, 12, 1),
            loan_balance=1200.3,
            loan_issued=250.6,
            yoy_growth=12.8,
            mom_growth=1.8,
            data_source='示例数据'
        ),
        Platform(
            name='微粒贷',
            company_group='腾讯',
            platform_type='联合贷',
            loan_type='消费类',
            report_month=datetime(2024, 12, 1),
            loan_balance=2100.8,
            loan_issued=380.2,
            yoy_growth=18.5,
            mom_growth=3.2,
            data_source='示例数据'
        ),
        Platform(
            name='京东金条',
            company_group='京东',
            platform_type='联合贷',
            loan_type='消费类',
            report_month=datetime(2024, 12, 1),
            loan_balance=750.3,
            loan_issued=165.4,
            yoy_growth=22.1,
            mom_growth=4.5,
            data_source='示例数据'
        ),
        Platform(
            name='美团借钱',
            company_group='美团',
            platform_type='助贷',
            loan_type='消费类',
            report_month=datetime(2024, 12, 1),
            loan_balance=420.8,
            loan_issued=85.2,
            yoy_growth=35.6,
            mom_growth=5.8,
            data_source='示例数据'
        ),
    ]

    # 插入银行示例数据
    banks = [
        Bank(
            name='招商银行',
            bank_type='股份制',
            report_month=datetime(2024, 12, 1),
            total_internet_loan=5800.5,
            coop_platform_count=12,
            data_source='示例数据'
        ),
        Bank(
            name='兴业银行',
            bank_type='股份制',
            report_month=datetime(2024, 12, 1),
            total_internet_loan=4200.3,
            coop_platform_count=10,
            data_source='示例数据'
        ),
        Bank(
            name='平安银行',
            bank_type='股份制',
            report_month=datetime(2024, 12, 1),
            total_internet_loan=5100.8,
            coop_platform_count=11,
            data_source='示例数据'
        ),
    ]

    # 保存数据
    for platform in platforms:
        db.session.add(platform)

    for bank in banks:
        db.session.add(bank)

    db.session.commit()
    print(f'已插入 {len(platforms)} 条平台数据和 {len(banks)} 条银行数据')


if __name__ == '__main__':
    print('=' * 50)
    print('金融数据聚合平台 - 后端服务')
    print('=' * 50)
    print('启动开发服务器...')
    print('API地址: http://localhost:5000/api/v1')
    print('按 Ctrl+C 停止服务器')
    print('=' * 50)

    # 启动调度器
    scheduler.start()

    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True
        )
    finally:
        # 停止调度器
        scheduler.stop()
