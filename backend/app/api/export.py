"""
导出API
提供Excel导出功能
"""
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from ..models import Platform, Bank
from .. import db
import pandas as pd
import tempfile

# 创建蓝图
export_bp = Blueprint('export', __name__)


@export_bp.route('/export/platform', methods=['POST'])
def export_platform_data():
    """
    导出平台数据为Excel

    Request Body:
        company_group: 集团筛选（可选）
        platform_type: 产品类型（可选）
        loan_type: 贷款用途（可选）
        start_month: 开始月份（可选）
        end_month: 结束月份（可选）

    Returns:
        Excel文件下载
    """
    try:
        # 获取请求参数
        data = request.get_json() or {}
        company_group = data.get('company_group')
        platform_type = data.get('platform_type')
        loan_type = data.get('loan_type')
        start_month = data.get('start_month')
        end_month = data.get('end_month')

        # 构建查询
        query = db.session.query(Platform)

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

        # 获取数据
        data = query.order_by(Platform.report_month.desc()).all()

        if not data:
            return jsonify({
                'code': -1,
                'message': '没有找到符合条件的数据',
                'data': None
            }), 404

        # 转换为DataFrame
        df = pd.DataFrame([item.to_dict() for item in data])

        # 选择和排序列
        columns_order = [
            'report_month', 'name', 'company_group',
            'platform_type', 'loan_type',
            'loan_balance', 'loan_issued',
            'yoy_growth', 'mom_growth',
            'data_source'
        ]

        # 确保列存在
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]

        # 列名映射（中文）
        column_mapping = {
            'report_month': '报告月份',
            'name': '平台名称',
            'company_group': '所属集团',
            'platform_type': '产品类别',
            'loan_type': '贷款用途',
            'loan_balance': '贷款余额(亿元)',
            'loan_issued': '发放规模(亿元)',
            'yoy_growth': '同比增长(%)',
            'mom_growth': '环比增长(%)',
            'data_source': '数据来源'
        }
        df.rename(columns=column_mapping, inplace=True)

        # 创建临时文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'platform_data_{timestamp}.xlsx'

        # 使用临时目录
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)

        # 导出为Excel（支持xls格式）
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 数据表
            df.to_excel(writer, sheet_name='平台数据', index=False)

            # 汇总表
            summary_data = create_platform_summary(df)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='数据汇总', index=False)

        # 发送文件
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'导出失败: {str(e)}',
            'data': None
        }), 500


@export_bp.route('/export/bank', methods=['POST'])
def export_bank_data():
    """
    导出银行数据为Excel

    Request Body:
        bank_type: 银行类型（可选）
        start_month: 开始月份（可选）
        end_month: 结束月份（可选）

    Returns:
        Excel文件下载
    """
    try:
        # 获取请求参数
        data = request.get_json() or {}
        bank_type = data.get('bank_type')
        start_month = data.get('start_month')
        end_month = data.get('end_month')

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

        # 获取数据
        data = query.order_by(Bank.report_month.desc()).all()

        if not data:
            return jsonify({
                'code': -1,
                'message': '没有找到符合条件的数据',
                'data': None
            }), 404

        # 转换为DataFrame
        df = pd.DataFrame([item.to_dict() for item in data])

        # 选择和排序列
        columns_order = [
            'report_month', 'name', 'bank_type',
            'total_internet_loan', 'coop_platform_count',
            'top3_platform_share', 'data_source'
        ]

        # 确保列存在
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]

        # 列名映射（中文）
        column_mapping = {
            'report_month': '报告月份',
            'name': '银行名称',
            'bank_type': '银行类型',
            'total_internet_loan': '互联网贷款规模(亿元)',
            'coop_platform_count': '合作平台数量',
            'top3_platform_share': '前3大平台占比(%)',
            'data_source': '数据来源'
        }
        df.rename(columns=column_mapping, inplace=True)

        # 创建临时文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bank_data_{timestamp}.xlsx'

        # 使用临时目录
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)

        # 导出为Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 数据表
            df.to_excel(writer, sheet_name='银行数据', index=False)

            # 排行榜表
            ranking_data = create_bank_ranking(df)
            ranking_df = pd.DataFrame(ranking_data)
            ranking_df.to_excel(writer, sheet_name='银行排行榜', index=False)

        # 发送文件
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return jsonify({
            'code': -1,
            'message': f'导出失败: {str(e)}',
            'data': None
        }), 500


def create_platform_summary(df):
    """创建平台数据汇总"""
    summary = []

    # 最新月份
    if '报告月份' in df.columns:
        latest_month = df['报告月份'].max()
        latest_data = df[df['报告月份'] == latest_month]

        summary.append(['指标', '数值'])
        summary.append(['最新月份', latest_month])
        summary.append(['平台数量', len(latest_data)])
        summary.append(['总贷款余额(亿元)', f"{latest_data['贷款余额(亿元)'].sum():.2f}"])
        summary.append(['总发放规模(亿元)', f"{latest_data['发放规模(亿元)'].sum():.2f}"])
        summary.append(['', ''])
        summary.append(['按集团统计', ''])

        # 按集团统计
        if '所属集团' in df.columns:
            group_stats = latest_data.groupby('所属集团')['贷款余额(亿元)'].agg(['sum', 'count'])
            for group, row in group_stats.iterrows():
                summary.append([f'  {group}', f"{row['sum']:.2f} 亿元 ({int(row['count'])}个平台)"])

    return summary


def create_bank_ranking(df):
    """创建银行排行榜"""
    ranking = []

    if '互联网贷款规模(亿元)' in df.columns:
        # 按规模排序
        sorted_df = df.sort_values('互联网贷款规模(亿元)', ascending=False)

        ranking.append(['排名', '银行名称', '互联网贷款规模(亿元)', '合作平台数量'])

        for idx, (_, row) in enumerate(sorted_df.iterrows(), 1):
            ranking.append([
                idx,
                row.get('银行名称', ''),
                f"{row.get('互联网贷款规模(亿元)', 0):.2f}",
                int(row.get('合作平台数量', 0)) if pd.notna(row.get('合作平台数量')) else '-'
            ])

    return ranking


# 将导出路由注册到API蓝图的辅助函数
def init_export_routes(api_bp):
    """初始化导出路由"""
    api_bp.add_url_rule('/export/platform', view_func=export_platform_data)
    api_bp.add_url_rule('/export/bank', view_func=export_bank_data)
