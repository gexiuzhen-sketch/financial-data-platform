"""
Flask应用配置
"""
import os
from pathlib import Path

# 基础目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
EXPORTS_DIR = BASE_DIR / 'exports'
LOGS_DIR = BASE_DIR / 'logs'

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class Config:
    """基础配置"""

    # Flask配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATA_DIR}/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # CORS配置
    CORS_HEADERS = 'Content-Type'

    # 导出文件配置
    EXPORTS_DIR = str(EXPORTS_DIR)
    MAX_EXPORT_RECORDS = 10000

    # 日志配置
    LOGS_DIR = str(LOGS_DIR)
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    # 爬虫配置
    SCRAPER_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    SCRAPER_TIMEOUT = 30
    SCRAPER_MAX_RETRIES = 3
    SCRAPER_DELAY_MIN = 1
    SCRAPER_DELAY_MAX = 3

    # 定时任务配置
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    # 是否启用爬虫功能（可通过环境变量 ENABLE_SCRAPERS 控制）
    ENABLE_SCRAPERS = os.environ.get('ENABLE_SCRAPERS', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # 生产环境应该使用环境变量设置SECRET_KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)

    # Render 上使用数据库 URL 或默认 SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # 如果提供 PostgreSQL 等 URL
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    # 否则使用默认的 SQLite 配置


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
