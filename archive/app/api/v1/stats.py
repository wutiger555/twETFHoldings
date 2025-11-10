"""
統計資料 API 路由
提供市場統計、熱門股票排行等功能
"""

from flask import request
from flask_restx import Namespace, Resource, fields
import logging

from app.services.cache import cache, CacheKeys, CacheTTL

logger = logging.getLogger(__name__)

# 創建 Namespace
api = Namespace('stats', description='統計資料')

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

@api.route('/popular')
class PopularStocks(Resource):
    """熱門股票排行"""

    @api.doc('get_popular_stocks')
    @api.param('limit', '數量限制', type=int, default=20)
    @api.response(200, 'Success')
    def get(self):
        """取得熱門股票排行（被最多 ETF 持有）"""
        try:
            limit = int(request.args.get('limit', 20))

            # 從快取取得
            popular = cache.get(CacheKeys.STATS_POPULAR)

            if not popular:
                # 暫時返回空資料
                # 實際需要統計所有 ETF 持股
                popular = []

            return success_response({
                'popular_stocks': popular[:limit],
                'note': '需要資料庫支援統計功能'
            })

        except Exception as e:
            logger.error(f"取得熱門股票失敗: {e}")
            error_response(str(e), 500)


@api.route('/market')
class MarketStats(Resource):
    """市場統計"""

    @api.doc('get_market_stats')
    @api.response(200, 'Success')
    def get(self):
        """取得市場統計資訊"""
        try:
            # 統計資訊
            etf_list = cache.get(CacheKeys.ETF_LIST)

            stats = {
                'total_etfs': len(etf_list) if etf_list else 0,
                'cache_stats': {
                    'etf_list_cached': cache.get(CacheKeys.ETF_LIST) is not None,
                    'search_index_cached': cache.get(CacheKeys.SEARCH_INDEX) is not None
                }
            }

            return success_response(stats)

        except Exception as e:
            logger.error(f"取得市場統計失敗: {e}")
            error_response(str(e), 500)
