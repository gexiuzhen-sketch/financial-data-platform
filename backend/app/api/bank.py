"""
银行数据API
提供银行数据的查询和筛选接口
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import Bank
from .. import db

# 创建蓝图
bank_bp = Blueprint('banks', __name__)


@bank_bp.route('/banks', methods=['GET'])
def get_banks():
    """
    获取所有银行列表

    Query Parameters:
        bank_type: 银行类型（可选）

    Returns:
        JSON响应
    """
    try:
        bank_type_filter = request.args.get('bank_type')

        query = db.session.query(Bank)

        if bank_type_filter:
            query = query.filter(Bank.bank_type == bank_type_filter)

        banks = query.distinct(Bank.name).all()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': [
                {
                    'id': b.id,
                    'name': b.name,
                    'bank_type': b.bank_type
                }
                for b in banks
            ]
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取银行列表失败: {str(e)}',
            'data': None
        }), 500


@bank_bp.route('/banks/data', methods=['GET'])
def get_bank_data():
    """
    获取银行数据（支持筛选）

    Query Parameters:
        bank_type: 银行类型（股份制/国有/城商行等）
        start_month: 开始月份（YYYY-MM）
        end_month: 结束月份（YYYY-MM）
        page: 页码（默认1）
        per_page: 每页数量（默认20）
        sort_by: 排序字段（默认report_month）
        sort_order: 排序方向（asc/desc，默认desc）

    Returns:
        JSON响应
    """
    try:
        # 获取查询参数
        bank_type = request.args.get('bank_type')
        start_month = request.args.get('start_month')
        end_month = request.args.get('end_month')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'report_month')
        sort_order = request.args.get('sort_order', 'desc')

        # 构建查询
        query = db.session.query(Bank)

        # 应用筛选条件
        if bank_type:
            query = query.filter(Bank.bank_type == bank_type)
        if start_month:
            start_date = datetime.strptime(start_month, '%Y-%m')
            query = query.filter(Bank.report_month >= start_date)
        if end_month:
            end_date = datetime.strptime(end_month, '%Y-%m')
            query = query.filter(Bank.report_month <= end_date)

        # 排序
        if sort_order == 'desc':
            query = query.order_by(db.desc(getattr(Bank, sort_by)))
        else:
            query = query.order_by(db.asc(getattr(Bank, sort_by)))

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
            'message': f'获取银行数据失败: {str(e)}',
            'data': None
        }), 500


@bank_bp.route('/banks/<int:bank_id>', methods=['GET'])
def get_bank_detail(bank_id):
    """
    获取单个银行详情

    Args:
        bank_id: 银行ID

    Returns:
        JSON响应
    """
    try:
        bank = db.session.query(Bank).filter_by(id=bank_id).first()

        if not bank:
            return jsonify({
                'code': -1,
                'message': '银行不存在',
                'data': None
            }), 404

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': bank.to_dict()
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取银行详情失败: {str(e)}',
            'data': None
        }), 500


@bank_bp.route('/banks/<int:bank_id>/timeline', methods=['GET'])
def get_bank_timeline(bank_id):
    """
    获取银行的时间序列数据

    Args:
        bank_id: 银行ID

    Returns:
        JSON响应，包含按时间排序的数据
    """
    try:
        bank = db.session.query(Bank).filter_by(id=bank_id).first()

        if not bank:
            return jsonify({
                'code': -1,
                'message': '银行不存在',
                'data': None
            }), 404

        data = db.session.query(Bank).filter(
            Bank.name == bank.name
        ).order_by(Bank.report_month.asc()).all()

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'bank_name': bank.name,
                'bank_type': bank.bank_type,
                'timeline': [item.to_dict() for item in data]
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取时间序列数据失败: {str(e)}',
            'data': None
        }), 500


@bank_bp.route('/banks/stats/overview', methods=['GET'])
def get_bank_overview():
    """
    获取银行数据概览

    Returns:
        JSON响应，包含最新的总体统计数据
    """
    try:
        from sqlalchemy import func

        # 获取最新月份
        latest_month = db.session.query(func.max(Bank.report_month)).scalar()

        if not latest_month:
            return jsonify({
                'code': 0,
                'message': 'success',
                'data': {
                    'latest_month': None,
                    'total_loan': 0,
                    'bank_count': 0,
                    'avg_platforms': 0
                }
            })

        # 最新月份数据
        latest_data = db.session.query(Bank).filter(
            Bank.report_month == latest_month
        ).all()

        total_loan = sum(item.total_internet_loan or 0 for item in latest_data)
        total_platforms = sum(item.coop_platform_count or 0 for item in latest_data)
        avg_platforms = total_platforms / len(latest_data) if latest_data else 0

        # 按银行类型统计
        type_stats = db.session.query(
            Bank.bank_type,
            func.count(Bank.id).label('count'),
            func.sum(Bank.total_internet_loan).label('total_loan')
        ).filter(
            Bank.report_month == latest_month
        ).group_by(Bank.bank_type).all()

        by_type = [
            {
                'type': item.bank_type or '未知',
                'count': item.count,
                'total_loan': float(item.total_loan or 0)
            }
            for item in type_stats
        ]

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'latest_month': latest_month.strftime('%Y-%m'),
                'total_loan': round(total_loan, 2),
                'bank_count': len(latest_data),
                'avg_platforms': round(avg_platforms, 1),
                'by_type': by_type
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取统计概览失败: {str(e)}',
            'data': None
        }), 500


# 将银行路由注册到API蓝图的辅助函数
def init_bank_routes(api_bp):
    """初始化银行路由"""
    api_bp.add_url_rule('/banks', view_func=get_banks)
    api_bp.add_url_rule('/banks/data', view_func=get_bank_data)
    api_bp.add_url_rule('/banks/<int:bank_id>', view_func=get_bank_detail)
    api_bp.add_url_rule('/banks/<int:bank_id>/timeline', view_func=get_bank_timeline)
    api_bp.add_url_rule('/banks/stats/overview', view_func=get_bank_overview)
