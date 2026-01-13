"""
Flask应用初始化
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import logging
import os
from logging.handlers import RotatingFileHandler
from .config import config, LOGS_DIR


# 初始化扩展
db = SQLAlchemy()


def create_app(config_name='default'):
    """
    创建Flask应用工厂

    Args:
        config_name: 配置名称（development/production/testing）

    Returns:
        Flask应用实例
    """
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    # 设置日志
    setup_logging(app)

    # 注册蓝图
    register_blueprints(app)

    # 创建数据库表并初始化示例数据
    with app.app_context():
        init_database(app)

    return app


def setup_logging(app):
    """设置日志"""
    log_level = getattr(logging, app.config['LOG_LEVEL'])
    log_format = logging.Formatter(app.config['LOG_FORMAT'], datefmt=app.config['LOG_DATE_FORMAT'])

    # 文件日志处理器
    log_file = os.path.join(app.config['LOGS_DIR'], 'app.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(log_format)

    # 控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_format)

    # 配置应用日志
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    app.logger.info('Flask应用初始化完成')


def register_blueprints(app):
    """注册蓝图"""
    from .api import api_bp, init_routes

    # 先初始化路由（在注册蓝图之前）
    init_routes()

    # 注册蓝图
    app.register_blueprint(api_bp)


def init_database(app):
    """初始化数据库表和示例数据"""
    from .models.platform import Base as PlatformBase
    from .models import Platform, Bank
    from datetime import datetime
    from sqlalchemy import select

    # 创建所有表
    PlatformBase.metadata.create_all(db.engine)
    app.logger.info('数据库表创建完成')

    # 检查是否需要初始化示例数据
    result = db.session.execute(select(Platform).limit(1))
    if not result.first():
        app.logger.info('初始化示例数据...')

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
        app.logger.info('示例数据初始化完成：5 条平台数据，3 条银行数据')
