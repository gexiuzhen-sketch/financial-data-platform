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

    # 创建数据库表
    with app.app_context():
        db.create_all()

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

    # 注册蓝图
    app.register_blueprint(api_bp)

    # 初始化路由
    init_routes()
