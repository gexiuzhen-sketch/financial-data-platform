"""
初始化数据API
提供数据库初始化和示例数据插入功能
"""
from flask import Blueprint, jsonify
from datetime import datetime
from ..models import Platform, Bank
from .. import db

# 创建蓝图
init_bp = Blueprint('init', __name__)


@init_bp.route('/init/seed', methods=['POST'])
def seed_data():
    """
    插入示例数据

    Returns:
        JSON响应
    """
    try:
        # 检查是否已有数据
        if Platform.query.first() or Bank.query.first():
            return jsonify({
                'code': 0,
                'message': '数据库已有数据，无需初始化',
                'data': None
            })

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

        return jsonify({
            'code': 0,
            'message': f'成功初始化 {len(platforms)} 条平台数据和 {len(banks)} 条银行数据',
            'data': {
                'platforms': len(platforms),
                'banks': len(banks)
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'初始化数据失败: {str(e)}',
            'data': None
        }), 500


def init_init_routes(api_bp):
    """初始化数据路由"""
    api_bp.add_url_rule('/init/seed', view_func=seed_data)
