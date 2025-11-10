"""
Flask 應用程式配置管理
"""

import os
from datetime import timedelta


class Config:
    """基礎配置"""

    # Flask 基本配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JSON_AS_ASCII = False  # 支援中文
    JSON_SORT_KEYS = False

    # API 配置
    API_TITLE = '台股 ETF API'
    API_VERSION = '1.0'
    OPENAPI_VERSION = '3.0.2'
    API_SPEC_OPTIONS = {
        'x-internal-id': '1',
    }

    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # FinMind API
    FINMIND_TOKEN = os.getenv('FINMIND_TOKEN')
    FINMIND_BASE_URL = 'https://api.finmindtrade.com/api/v4/data'

    # Redis 快取
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis' if REDIS_URL else 'simple'

    # 資料庫
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///etf_app.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 生產環境關閉 SQL 日誌

    # 快取 TTL 設定（秒）
    CACHE_TTL = {
        'ETF_LIST': 86400,      # 24 小時
        'ETF_HOLDINGS': 86400,  # 24 小時
        'STOCK_PRICE': 3600,    # 1 小時
        'SEARCH_INDEX': 86400,  # 24 小時
    }

    # 定時任務設定
    SCHEDULER_ENABLED = os.getenv('SCHEDULER_ENABLED', 'true').lower() == 'true'
    SCHEDULER_TIMEZONE = 'Asia/Taipei'

    # 日誌設定
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - [%(levelname)s] - [%(name)s] - %(message)s'

    # 速率限制
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'false').lower() == 'true'
    RATELIMIT_DEFAULT = "100 per hour"


class DevelopmentConfig(Config):
    """開發環境配置"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # 開發環境顯示 SQL


class ProductionConfig(Config):
    """生產環境配置"""
    DEBUG = False
    TESTING = False

    # 生產環境必須設定 SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")

    # 啟用速率限制
    RATELIMIT_ENABLED = True


class TestingConfig(Config):
    """測試環境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CACHE_TYPE = 'simple'
    SCHEDULER_ENABLED = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """取得當前配置"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
