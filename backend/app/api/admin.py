"""
管理后台API
提供数据管理、手动更新、批量导入等功能
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from ..models import Platform, Bank
from .. import db
from ..services import scheduler

# 创建蓝图
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/platforms', methods=['GET'])
def get_admin_platforms():
    """
    获取平台数据列表（管理后台）
    支持分页、筛选、排序
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
        sort_by = request.args.get('sort_by', 'created_at')
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


@admin_bp.route('/admin/platforms', methods=['POST'])
def create_platform():
    """
    创建平台数据
    """
    try:
        data = request.get_json()

        # 解析报告月份
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
            data_source=data.get('data_source', '手动录入'),
            source_url=data.get('source_url')
        )

        db.session.add(platform)
        db.session.commit()

        return jsonify({
            'code': 0,
            'message': '创建成功',
            'data': platform.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'创建失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/platforms/<int:platform_id>', methods=['PUT'])
def update_platform(platform_id):
    """
    更新平台数据
    """
    try:
        data = request.get_json()
        platform = db.session.query(Platform).filter_by(id=platform_id).first()

        if not platform:
            return jsonify({
                'code': -1,
                'message': '数据不存在',
                'data': None
            }), 404

        # 更新字段
        if 'name' in data:
            platform.name = data['name']
        if 'company_group' in data:
            platform.company_group = data['company_group']
        if 'platform_type' in data:
            platform.platform_type = data['platform_type']
        if 'loan_type' in data:
            platform.loan_type = data['loan_type']
        if 'report_month' in data and data['report_month']:
            platform.report_month = datetime.strptime(data['report_month'], '%Y-%m')
        if 'loan_balance' in data:
            platform.loan_balance = data['loan_balance']
        if 'loan_issued' in data:
            platform.loan_issued = data['loan_issued']
        if 'yoy_growth' in data:
            platform.yoy_growth = data['yoy_growth']
        if 'mom_growth' in data:
            platform.mom_growth = data['mom_growth']
        if 'data_source' in data:
            platform.data_source = data['data_source']
        if 'source_url' in data:
            platform.source_url = data['source_url']

        platform.updated_at = datetime.now()
        db.session.commit()

        return jsonify({
            'code': 0,
            'message': '更新成功',
            'data': platform.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'更新失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/platforms/<int:platform_id>', methods=['DELETE'])
def delete_platform(platform_id):
    """
    删除平台数据
    """
    try:
        platform = db.session.query(Platform).filter_by(id=platform_id).first()

        if not platform:
            return jsonify({
                'code': -1,
                'message': '数据不存在',
                'data': None
            }), 404

        db.session.delete(platform)
        db.session.commit()

        return jsonify({
            'code': 0,
            'message': '删除成功',
            'data': {'id': platform_id}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/platforms/batch', methods=['POST'])
def batch_create_platforms():
    """
    批量创建平台数据
    """
    try:
        data_list = request.get_json().get('data', [])

        created_count = 0
        for data in data_list:
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
                data_source=data.get('data_source', '批量导入'),
                source_url=data.get('source_url')
            )
            db.session.add(platform)
            created_count += 1

        db.session.commit()

        return jsonify({
            'code': 0,
            'message': f'成功导入 {created_count} 条数据',
            'data': {'count': created_count}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'批量导入失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/banks', methods=['GET'])
def get_admin_banks():
    """
    获取银行数据列表（管理后台）
    """
    try:
        # 获取查询参数
        bank_type = request.args.get('bank_type')
        start_month = request.args.get('start_month')
        end_month = request.args.get('end_month')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')

        # 构建查询
        query = db.session.query(Bank)

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


@admin_bp.route('/admin/banks', methods=['POST'])
def create_bank():
    """
    创建银行数据
    """
    try:
        data = request.get_json()

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
            data_source=data.get('data_source', '手动录入'),
            source_url=data.get('source_url')
        )

        db.session.add(bank)
        db.session.commit()

        return jsonify({
            'code': 0,
            'message': '创建成功',
            'data': bank.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'创建失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/banks/<int:bank_id>', methods=['PUT'])
def update_bank(bank_id):
    """
    更新银行数据
    """
    try:
        data = request.get_json()
        bank = db.session.query(Bank).filter_by(id=bank_id).first()

        if not bank:
            return jsonify({
                'code': -1,
                'message': '数据不存在',
                'data': None
            }), 404

        # 更新字段
        if 'name' in data:
            bank.name = data['name']
        if 'bank_type' in data:
            bank.bank_type = data['bank_type']
        if 'report_month' in data and data['report_month']:
            bank.report_month = datetime.strptime(data['report_month'], '%Y-%m')
        if 'total_internet_loan' in data:
            bank.total_internet_loan = data['total_internet_loan']
        if 'coop_platform_count' in data:
            bank.coop_platform_count = data['coop_platform_count']
        if 'top3_platform_share' in data:
            bank.top3_platform_share = data['top3_platform_share']
        if 'data_source' in data:
            bank.data_source = data['data_source']
        if 'source_url' in data:
            bank.source_url = data['source_url']

        bank.updated_at = datetime.now()
        db.session.commit()

        return jsonify({
            'code': 0,
            'message': '更新成功',
            'data': bank.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'更新失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/banks/<int:bank_id>', methods=['DELETE'])
def delete_bank(bank_id):
    """
    删除银行数据
    """
    try:
        bank = db.session.query(Bank).filter_by(id=bank_id).first()

        if not bank:
            return jsonify({
                'code': -1,
                'message': '数据不存在',
                'data': None
            }), 404

        db.session.delete(bank)
        db.session.commit()

        return jsonify({
            'code': 0,
            'message': '删除成功',
            'data': {'id': bank_id}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/banks/batch', methods=['POST'])
def batch_create_banks():
    """
    批量创建银行数据
    """
    try:
        data_list = request.get_json().get('data', [])

        created_count = 0
        for data in data_list:
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
                data_source=data.get('data_source', '批量导入'),
                source_url=data.get('source_url')
            )
            db.session.add(bank)
            created_count += 1

        db.session.commit()

        return jsonify({
            'code': 0,
            'message': f'成功导入 {created_count} 条数据',
            'data': {'count': created_count}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'批量导入失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/stats', methods=['GET'])
def get_admin_stats():
    """
    获取管理后台统计数据
    """
    try:
        platform_count = db.session.query(Platform).count()
        bank_count = db.session.query(Bank).count()

        # 获取最新数据月份
        from sqlalchemy import func
        latest_platform_month = db.session.query(func.max(Platform.report_month)).scalar()
        latest_bank_month = db.session.query(func.max(Bank.report_month)).scalar()

        # 获取调度器任务状态
        jobs = scheduler.get_jobs() if scheduler.scheduler else []

        return jsonify({
            'code': 0,
            'message': 'success',
            'data': {
                'platform_count': platform_count,
                'bank_count': bank_count,
                'latest_platform_month': latest_platform_month.strftime('%Y-%m') if latest_platform_month else None,
                'latest_bank_month': latest_bank_month.strftime('%Y-%m') if latest_bank_month else None,
                'scheduled_jobs': jobs
            }
        })

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'获取统计数据失败: {str(e)}',
            'data': None
        }), 500


@admin_bp.route('/admin/data/delete-by-date', methods=['POST'])
def delete_data_by_date():
    """
    按日期范围删除数据
    """
    try:
        data = request.get_json()
        data_type = data.get('data_type')  # 'platform' 或 'bank'
        start_month = data.get('start_month')
        end_month = data.get('end_month')

        if not start_month or not end_month:
            return jsonify({
                'code': -1,
                'message': '请提供开始和结束月份',
                'data': None
            }), 400

        start_date = datetime.strptime(start_month, '%Y-%m')
        end_date = datetime.strptime(end_month, '%Y-%m')

        deleted_count = 0

        if data_type == 'platform' or data_type == 'all':
            query = db.session.query(Platform).filter(
                Platform.report_month >= start_date,
                Platform.report_month <= end_date
            )
            deleted_count += query.count()
            query.delete()

        if data_type == 'bank' or data_type == 'all':
            query = db.session.query(Bank).filter(
                Bank.report_month >= start_date,
                Bank.report_month <= end_date
            )
            deleted_count += query.count()
            query.delete()

        db.session.commit()

        return jsonify({
            'code': 0,
            'message': f'成功删除 {deleted_count} 条数据',
            'data': {'count': deleted_count}
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': -1,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500


# 初始化管理后台路由
def init_admin_routes(api_bp):
    """初始化管理后台路由"""
    api_bp.add_url_rule('/admin/platforms', view_func=get_admin_platforms)
    api_bp.add_url_rule('/admin/platforms', view_func=create_platform)
    api_bp.add_url_rule('/admin/platforms/<int:platform_id>', view_func=update_platform)
    api_bp.add_url_rule('/admin/platforms/<int:platform_id>', view_func=delete_platform)
    api_bp.add_url_rule('/admin/platforms/batch', view_func=batch_create_platforms)

    api_bp.add_url_rule('/admin/banks', view_func=get_admin_banks)
    api_bp.add_url_rule('/admin/banks', view_func=create_bank)
    api_bp.add_url_rule('/admin/banks/<int:bank_id>', view_func=update_bank)
    api_bp.add_url_rule('/admin/banks/<int:bank_id>', view_func=delete_bank)
    api_bp.add_url_rule('/admin/banks/batch', view_func=batch_create_banks)

    api_bp.add_url_rule('/admin/stats', view_func=get_admin_stats)
    api_bp.add_url_rule('/admin/data/delete-by-date', view_func=delete_data_by_date)
