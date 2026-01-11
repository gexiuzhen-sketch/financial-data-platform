"""
平台数据API
提供平台数据的查询、筛选和统计接口
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import Platform
from .. import db

# 创建蓝图
platform_bp = Blueprint('platforms', __name__)


@platform_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """
    获取所有平台列表

    Query Parameters:
        name: 平台名称（可选）

    Returns:
        JSON响应
    """
    try:
        name_filter = request.args.get('name')

        query = db.session.query(Platform)

        if name_filter:
            query = query.filter(Platform.name.like(f'%{name_filter}%'))

        platforms = query.distinct(Platform.name).all()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': [
                {
                    'id': p.id,
                    'name': p.name,
                    'company_group': p.company_group
                }
                for p in platforms
            ]
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取平台列表失败: {str(e)}',
            'data': None
        }), 500


@platform_bp.route('/platforms/data', methods=['GET'])
def get_platform_data():
    """
    获取平台数据（支持筛选）

    Query Parameters:
        company_group: 集团筛选（蚂蚁/腾讯/字节/京东/美团/百度）
        platform_type: 产品类型（助贷/联合贷）
        loan_type: 贷款用途（消费类/经营类）
        start_month: 开始月份（YYYY-MM）
        end_month: 结束月份（YYYY-MM）
        page: 页码（默认1）
        per_page: 每页数量（默认20）

    Returns:
        JSON响应
    """
    try:
        # 获取查询参数
        company_group = request.args.get('company_group')
        platform_type = request.args.get('platform_type')
        loan_type = request.args.get('loan_type')
        start_month = request.args.get('start_month')
        end_month = request.args.get('end_month')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'report_month')
        sort_order = request.args.get('sort_order', 'desc')

        # 构建查询
        query = db.session.query(Platform)

        # 应用筛选条件
        if company_group:
            query = query.filter(Platform.company_group == company_group)
        if platform_type:
            query = query.filter(Platform.platform_type == platform_type)
        if loan_type:
            query = query.filter(Platform.loan_type == loan_type)
        if start_month:
            start_date = datetime.strptime(start_month, '%Y-%m')
            query = query.filter(Platform.report_month >= start_date)
        if end_month:
            end_date = datetime.strptime(end_month, '%Y-%m')
            query = query.filter(Platform.report_month <= end_date)

        # 排序
        if sort_order == 'desc':
            query = query.order_by(db.desc(getattr(Platform, sort_by)))
        else:
            query = query.order_by(db.asc(getattr(Platform, sort_by)))

        # 分页查询
        total = query.count()
        data = query.offset((page - 1) * per_page).limit(per_page).all()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'items': [item.to_dict() for item in data],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取平台数据失败: {str(e)}',
            'data': None
        }), 500


@platform_bp.route('/platforms/stats/overview', methods=['GET'])
def get_platform_overview():
    """
    获取平台数据概览

    Returns:
        JSON响应，包含最新的总体统计数据
    """
    try:
        from sqlalchemy import func

        # 获取最新月份
        latest_month = db.session.query(func.max(Platform.report_month)).scalar()

        if not latest_month:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'latest_month': None,
                    'total_balance': 0,
                    'total_issued': 0,
                    'platform_count': 0,
                    'by_group': []
                }
            })

        # 最新月份数据
        latest_data = db.session.query(Platform).filter(
            Platform.report_month == latest_month
        ).all()

        total_balance = sum(item.loan_balance or 0 for item in latest_data)
        total_issued = sum(item.loan_issued or 0 for item in latest_data)

        # 按集团分组统计
        group_stats = db.session.query(
            Platform.company_group,
            func.sum(Platform.loan_balance).label('total_balance'),
            func.count(Platform.id).label('platform_count')
        ).filter(
            Platform.report_month == latest_month
        ).group_by(Platform.company_group).all()

        by_group = [
            {
                'group': item.company_group or '未知',
                'total_balance': float(item.total_balance or 0),
                'platform_count': item.platform_count
            }
            for item in group_stats
        ]

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'latest_month': latest_month.strftime('%Y-%m'),
                'total_balance': round(total_balance, 2),
                'total_issued': round(total_issued, 2),
                'platform_count': len(latest_data),
                'by_group': by_group
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取统计概览失败: {str(e)}',
            'data': None
        }), 500


@platform_bp.route('/platforms/<int:platform_id>', methods=['GET'])
def get_platform_detail(platform_id):
    """
    获取单个平台详情

    Args:
        platform_id: 平台ID

    Returns:
        JSON响应
    """
    try:
        platform = db.session.query(Platform).filter_by(id=platform_id).first()

        if not platform:
            return jsonify({
                'code': -1,
                'message': '平台不存在',
                'data': None
            }), 404

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': platform.to_dict()
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取平台详情失败: {str(e)}',
            'data': None
        }), 500


@platform_bp.route('/platforms/<int:platform_id>/timeline', methods=['GET'])
def get_platform_timeline(platform_id):
    """
    获取平台的时间序列数据

    Args:
        platform_id: 平台ID

    Query Parameters:
        platform_type: 产品类型（可选）
        loan_type: 贷款用途（可选）

    Returns:
        JSON响应，包含按时间排序的数据
    """
    try:
        platform = db.session.query(Platform).filter_by(id=platform_id).first()

        if not platform:
            return jsonify({
                'code': -1,
                'message': '平台不存在',
                'data': None
            }), 404

        platform_type = request.args.get('platform_type')
        loan_type = request.args.get('loan_type')

        query = db.session.query(Platform).filter(Platform.name == platform.name)

        if platform_type:
            query = query.filter(Platform.platform_type == platform_type)
        if loan_type:
            query = query.filter(Platform.loan_type == loan_type)

        data = query.order_by(Platform.report_month.asc()).all()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'platform_name': platform.name,
                'company_group': platform.company_group,
                'timeline': [item.to_dict() for item in data]
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取时间序列数据失败: {str(e)}',
            'data': None
        }), 500


# 将平台路由注册到API蓝图
def init_platform_routes(api_bp):
    """初始化平台路由"""
    api_bp.add_url_rule('/platforms', view_func=get_platforms)
    api_bp.add_url_rule('/platforms/data', view_func=get_platform_data)
    api_bp.add_url_rule('/platforms/stats/overview', view_func=get_platform_overview)
    api_bp.add_url_rule('/platforms/<int:platform_id>', view_func=get_platform_detail)
    api_bp.add_url_rule('/platforms/<int:platform_id>/timeline', view_func=get_platform_timeline)
    api_bp.add_url_rule('/seed', view_func=seed_sample_data)


@platform_bp.route('/seed', methods=['POST'])
def seed_sample_data():
    """插入示例数据"""
    try:
        from ..models import Bank
        
        if Platform.query.first() or Bank.query.first():
            return jsonify({'code': 0, 'message': '数据库已有数据，无需初始化', 'data': None})
        
        platforms = [
            Platform(name='花呗', company_group='蚂蚁', platform_type='联合贷', loan_type='消费类',
                    report_month=datetime(2024, 12, 1), loan_balance=1800.5, loan_issued=320.8,
                    yoy_growth=15.2, mom_growth=2.5, data_source='示例数据'),
            Platform(name='借呗', company_group='蚂蚁', platform_type='助贷', loan_type='消费类',
                    report_month=datetime(2024, 12, 1), loan_balance=1200.3, loan_issued=250.6,
                    yoy_growth=12.8, mom_growth=1.8, data_source='示例数据'),
            Platform(name='微粒贷', company_group='腾讯', platform_type='联合贷', loan_type='消费类',
                    report_month=datetime(2024, 12, 1), loan_balance=2100.8, loan_issued=380.2,
                    yoy_growth=18.5, mom_growth=3.2, data_source='示例数据'),
            Platform(name='京东金条', company_group='京东', platform_type='联合贷', loan_type='消费类',
                    report_month=datetime(2024, 12, 1), loan_balance=750.3, loan_issued=165.4,
                    yoy_growth=22.1, mom_growth=4.5, data_source='示例数据'),
            Platform(name='美团借钱', company_group='美团', platform_type='助贷', loan_type='消费类',
                    report_month=datetime(2024, 12, 1), loan_balance=420.8, loan_issued=85.2,
                    yoy_growth=35.6, mom_growth=5.8, data_source='示例数据'),
        ]
        
        banks = [
            Bank(name='招商银行', bank_type='股份制', report_month=datetime(2024, 12, 1),
                 total_internet_loan=5800.5, coop_platform_count=12, data_source='示例数据'),
            Bank(name='兴业银行', bank_type='股份制', report_month=datetime(2024, 12, 1),
                 total_internet_loan=4200.3, coop_platform_count=10, data_source='示例数据'),
            Bank(name='平安银行', bank_type='股份制', report_month=datetime(2024, 12, 1),
                 total_internet_loan=5100.8, coop_platform_count=11, data_source='示例数据'),
        ]
        
        for p in platforms:
            db.session.add(p)
        for b in banks:
            db.session.add(b)
        
        db.session.commit()
        
        return jsonify({'code': 0, 'message': f'成功初始化 {len(platforms)} 条平台数据和 {len(banks)} 条银行数据', 'data': {'platforms': len(platforms), 'banks': len(banks)}})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': -1, 'message': f'初始化失败: {str(e)}', 'data': None}), 500
