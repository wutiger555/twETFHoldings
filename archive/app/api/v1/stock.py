"""
股票 API 路由
提供個股價格、歷史資料、技術指標等功能
"""

from flask import request
from flask_restx import Namespace, Resource, fields
import logging

from app.services.finmind import FinMindClient
from app.services.cache import cache, CacheKeys, CacheTTL

logger = logging.getLogger(__name__)

# 創建 Namespace
api = Namespace('stock', description='個股相關操作')

# ============================================================
# API Models
# ============================================================

stock_model = api.model('Stock', {
    'code': fields.String(required=True, description='股票代碼'),
    'name': fields.String(required=True, description='股票名稱'),
    'price': fields.Float(description='目前價格'),
    'change': fields.Float(description='漲跌'),
    'change_percent': fields.Float(description='漲跌幅(%)'),
    'volume': fields.Integer(description='成交量'),
})

price_history_model = api.model('PriceHistory', {
    'date': fields.String(description='日期'),
    'open': fields.Float(description='開盤價'),
    'high': fields.Float(description='最高價'),
    'low': fields.Float(description='最低價'),
    'close': fields.Float(description='收盤價'),
    'volume': fields.Integer(description='成交量'),
})

# ============================================================
# Helper Functions
# ============================================================

def success_response(data, message="Success"):
    """統一成功回應格式"""
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(message, status_code=400):
    """統一錯誤回應格式"""
    api.abort(status_code, message)


# ============================================================
# API Routes
# ============================================================

@api.route('/<string:code>')
@api.param('code', '股票代碼')
class StockDetail(Resource):
    """個股詳情"""

    @api.doc('get_stock')
    @api.response(200, 'Success', stock_model)
    @api.response(404, '找不到股票')
    def get(self, code):
        """取得個股基本資訊與最新價格"""
        try:
            # 從快取取得
            cache_key = CacheKeys.STOCK_PRICE_DAILY.format(code=code)
            stock_data = cache.get(cache_key)

            if not stock_data:
                logger.info(f"快取未命中，從 FinMind 取得 {code}")
                client = FinMindClient()
                price_data = client.get_latest_price(code)

                if not price_data:
                    error_response(f"找不到股票 {code} 的資料", 404)

                stock_data = {
                    'code': code,
                    'name': price_data.get('stock_id', code),
                    'price': price_data.get('close'),
                    'volume': price_data.get('Trading_Volume'),
                    'date': price_data.get('date')
                }

                # 計算漲跌（需要前一日資料）
                history = client.get_stock_price(code, days=2)
                if len(history) >= 2:
                    today = history[-1]
                    yesterday = history[-2]
                    stock_data['change'] = today['close'] - yesterday['close']
                    stock_data['change_percent'] = (
                        (today['close'] - yesterday['close']) / yesterday['close'] * 100
                    )

                cache.set(cache_key, stock_data, CacheTTL.HOUR_1)

            return success_response(stock_data)

        except Exception as e:
            logger.error(f"取得股票 {code} 失敗: {e}")
            error_response(str(e), 500)


@api.route('/<string:code>/history')
@api.param('code', '股票代碼')
class StockHistory(Resource):
    """個股歷史資料"""

    @api.doc('get_stock_history')
    @api.param('period', '時間範圍', type=str, enum=['7d', '30d', '90d', '1y'], default='30d')
    @api.response(200, 'Success')
    def get(self, code):
        """取得個股歷史價格"""
        try:
            period = request.args.get('period', '30d')

            # 轉換期間為天數
            period_days = {
                '7d': 7,
                '30d': 30,
                '90d': 90,
                '1y': 365
            }
            days = period_days.get(period, 30)

            # 從快取取得
            cache_key = CacheKeys.STOCK_PRICE_HISTORY.format(code=code, days=days)
            history = cache.get(cache_key)

            if not history:
                logger.info(f"快取未命中，從 FinMind 取得 {code} 歷史資料")
                client = FinMindClient()
                history = client.get_stock_price(code, days=days)

                if not history:
                    error_response(f"找不到股票 {code} 的歷史資料", 404)

                cache.set(cache_key, history, CacheTTL.HOUR_1)

            return success_response({
                'stock_code': code,
                'period': period,
                'prices': history
            })

        except Exception as e:
            logger.error(f"取得股票 {code} 歷史資料失敗: {e}")
            error_response(str(e), 500)


@api.route('/<string:code>/held_by')
@api.param('code', '股票代碼')
class StockHeldBy(Resource):
    """持有此股票的 ETF"""

    @api.doc('get_stock_held_by')
    @api.response(200, 'Success')
    def get(self, code):
        """查詢哪些 ETF 持有此股票"""
        try:
            # 這需要查詢所有 ETF 的持股
            # 暫時返回空資料
            return success_response({
                'stock_code': code,
                'held_by_etfs': [],
                'note': '需要資料庫支援跨 ETF 查詢'
            })

        except Exception as e:
            logger.error(f"查詢股票 {code} 被哪些 ETF 持有失敗: {e}")
            error_response(str(e), 500)


@api.route('/batch')
class StockBatch(Resource):
    """批次查詢股票"""

    @api.doc('get_stocks_batch')
    @api.expect(api.model('BatchRequest', {
        'codes': fields.List(fields.String, required=True, description='股票代碼列表')
    }))
    @api.response(200, 'Success')
    def post(self):
        """批次取得多個股票的價格"""
        try:
            data = request.get_json()
            codes = data.get('codes', [])

            if not codes:
                error_response("請提供股票代碼列表", 400)

            if len(codes) > 50:
                error_response("單次最多查詢 50 檔股票", 400)

            client = FinMindClient()
            prices = client.get_batch_prices(codes, days=1)

            result = []
            for code, price_data in prices.items():
                result.append({
                    'code': code,
                    'price': price_data.get('close'),
                    'volume': price_data.get('Trading_Volume'),
                    'date': price_data.get('date')
                })

            return success_response(result)

        except Exception as e:
            logger.error(f"批次查詢股票失敗: {e}")
            error_response(str(e), 500)
