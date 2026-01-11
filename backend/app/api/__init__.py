"""
API蓝图初始化
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# 导入路由模块
from . import platform, bank, export

# 注册路由
def init_routes():
    """初始化所有API路由"""
    platform.init_platform_routes(api_bp)
    bank.init_bank_routes(api_bp)
    export.init_export_routes(api_bp)
