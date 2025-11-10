"""
Flask 主應用程式
整合所有模組並啟動服務
"""

import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 導入配置
from app.config import get_config

# 導入擴展
from app.extensions import cors, api

# 導入服務
from app.services.cache import init_cache
from app.services.finmind import FinMindClient

# 導入 API 路由
from app.api.v1 import etf, stock, search, stats


def create_app(config_name=None):
    """
    應用程式工廠函數

    Args:
        config_name: 配置名稱 (development/production/testing)

    Returns:
        Flask app 實例
    """
    # 創建 Flask 應用
    app = Flask(__name__)

    # 載入配置
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    config = get_config()
    app.config.from_object(config)

    # 設定日誌
    setup_logging(app)

    # 初始化擴展
    init_extensions(app)

    # 初始化服務
    init_services(app)

    # 註冊 API 路由
    register_blueprints(app)

    # 註冊錯誤處理
    register_error_handlers(app)

    # 啟動定時任務（生產環境）
    if app.config['SCHEDULER_ENABLED'] and not app.debug:
        init_scheduler(app)

    # 應用啟動日誌
    app.logger.info(f"應用啟動 - 環境: {config_name}")
    app.logger.info(f"Debug 模式: {app.debug}")
    app.logger.info(f"API 文件: http://localhost:5000/docs/")

    return app


def setup_logging(app):
    """設定日誌系統"""
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format=app.config['LOG_FORMAT']
    )

    # 設定 werkzeug 日誌級別
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def init_extensions(app):
    """初始化 Flask 擴展"""
    # CORS
    cors.init_app(app, origins=app.config['CORS_ORIGINS'])

    # Flask-RESTX API
    api.init_app(app)

    app.logger.info("Flask 擴展初始化完成")


def init_services(app):
    """初始化服務層"""
    with app.app_context():
        # 初始化快取
        redis_url = app.config.get('REDIS_URL')
        if redis_url:
            init_cache(redis_url)
            app.logger.info(f"Redis 快取已連接: {redis_url}")
        else:
            app.logger.warning("未設定 REDIS_URL，使用記憶體快取")

        # 驗證 FinMind Token
        token = app.config.get('FINMIND_TOKEN')
        if not token:
            app.logger.warning("未設定 FINMIND_TOKEN，API 請求可能受限")
        else:
            # 測試連接
            try:
                client = FinMindClient(token)
                if client.health_check():
                    app.logger.info("FinMind API 連接正常")
                else:
                    app.logger.error("FinMind API 連接失敗")
            except Exception as e:
                app.logger.error(f"FinMind API 測試失敗: {e}")


def register_blueprints(app):
    """註冊 API 藍圖"""
    # 註冊命名空間
    api.add_namespace(etf.api, path='/etf')
    api.add_namespace(stock.api, path='/stock')
    api.add_namespace(search.api, path='/search')
    api.add_namespace(stats.api, path='/stats')

    app.logger.info("API 路由註冊完成")


def register_error_handlers(app):
    """註冊錯誤處理器"""

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': '找不到請求的資源',
            'error': str(error)
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"內部錯誤: {error}")
        return jsonify({
            'success': False,
            'message': '伺服器內部錯誤',
            'error': str(error) if app.debug else '請稍後再試'
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f"未處理的異常: {error}", exc_info=True)
        return jsonify({
            'success': False,
            'message': '發生錯誤',
            'error': str(error) if app.debug else '請稍後再試'
        }), 500


def init_scheduler(app):
    """初始化定時任務"""
    try:
        from app.tasks.scheduler import init_scheduler as start_scheduler
        start_scheduler()
        app.logger.info("定時任務已啟動")
    except Exception as e:
        app.logger.error(f"啟動定時任務失敗: {e}")


# 創建應用實例（用於命令行啟動）
app = create_app()


# 首頁路由
@app.route('/')
def index():
    """API 首頁"""
    return jsonify({
        'message': '台股 ETF API',
        'version': '1.0',
        'docs': '/docs/',
        'endpoints': {
            'etfs': '/api/v1/etf/etfs',
            'etf_detail': '/api/v1/etf/etf/<code>',
            'stock_price': '/api/v1/stock/<code>',
            'search': '/api/v1/search?q=<keyword>'
        }
    })


# 健康檢查
@app.route('/health')
def health():
    """健康檢查端點"""
    from app.services.cache import cache
    from app.services.finmind import FinMindClient

    status = {
        'status': 'healthy',
        'services': {}
    }

    # 檢查 Redis
    try:
        if cache.redis_client:
            cache.redis_client.ping()
            status['services']['redis'] = 'connected'
        else:
            status['services']['redis'] = 'using_memory_cache'
    except Exception as e:
        status['services']['redis'] = f'error: {str(e)}'
        status['status'] = 'degraded'

    # 檢查 FinMind API
    try:
        client = FinMindClient(app.config.get('FINMIND_TOKEN'))
        if client.health_check():
            status['services']['finmind'] = 'connected'
        else:
            status['services']['finmind'] = 'unavailable'
            status['status'] = 'degraded'
    except Exception as e:
        status['services']['finmind'] = f'error: {str(e)}'
        status['status'] = 'degraded'

    return jsonify(status), 200 if status['status'] == 'healthy' else 503


if __name__ == '__main__':
    # 開發環境啟動
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )
