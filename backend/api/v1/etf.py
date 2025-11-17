"""
ETF API 路由
提供 ETF 相關的 RESTful API
"""

from flask import Blueprint, jsonify, request, current_app
from flask_restx import Namespace, Resource, fields
import logging

from backend.services.finmind import FinMindClient
from backend.services.cache import cache, CacheKeys, CacheTTL, cached

logger = logging.getLogger(__name__)

# 創建 Blueprint
etf_bp = Blueprint('etf', __name__)

# 創建 Namespace (for Swagger documentation)
api = Namespace('etf', description='ETF 相關操作')

# ============================================================
# API Models (Swagger 文件)
# ============================================================

etf_model = api.model('ETF', {
    'code': fields.String(required=True, description='ETF 代碼'),
    'name': fields.String(required=True, description='ETF 名稱'),
    'issuer': fields.String(description='發行商'),
    'type': fields.String(description='ETF 類型'),
})

holding_model = api.model('Holding', {
    'stock_code': fields.String(description='股票代碼'),
    'stock_name': fields.String(description='股票名稱'),
    'shares': fields.Integer(description='持股數'),
    'weight': fields.Float(description='權重(%)'),
    'market_value': fields.Float(description='市值'),
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='目前頁碼'),
    'limit': fields.Integer(description='每頁筆數'),
    'total': fields.Integer(description='總筆數'),
    'total_pages': fields.Integer(description='總頁數'),
})

# ============================================================
# Helper Functions
# ============================================================

def success_response(data, message="Success", cached_at=None):
    """統一成功回應格式"""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    if cached_at:
        response["cached_at"] = cached_at
    return jsonify(response)


def error_response(message, status_code=400):
    """統一錯誤回應格式"""
    return jsonify({
        "success": False,
        "message": message,
        "data": None
    }), status_code


def paginate(items, page, limit):
    """分頁處理"""
    total = len(items)
    total_pages = (total + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit

    return {
        "items": items[start:end],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
    }


# ============================================================
# API Routes
# ============================================================

@api.route('/etfs')
class ETFList(Resource):
    """ETF 清單"""

    @api.doc('list_etfs')
    @api.param('page', '頁碼', type=int, default=1)
    @api.param('limit', '每頁筆數', type=int, default=50)
    @api.param('issuer', '發行商篩選', type=str, required=False)
    @api.param('type', 'ETF 類型篩選', type=str, required=False)
    def get(self):
        """取得所有 ETF 清單"""
        try:
            # 取得查詢參數
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            issuer = request.args.get('issuer')
            etf_type = request.args.get('type')

            # 從快取或 API 取得資料
            etfs = cache.get(CacheKeys.ETF_LIST)

            if not etfs:
                logger.info("快取未命中，從 FinMind 取得 ETF 清單")
                client = FinMindClient(current_app.config.get('FINMIND_TOKEN'))
                etfs = client.get_all_etfs()
                cache.set(CacheKeys.ETF_LIST, etfs, CacheTTL.DAY_1)

            # 篩選
            if issuer:
                etfs = [e for e in etfs if issuer in e.get('industry', '')]
            if etf_type:
                etf_type = [e for e in etfs if etf_type in e.get('type', '')]

            # 分頁
            result = paginate(etfs, page, limit)

            return success_response(result)

        except Exception as e:
            logger.error(f"取得 ETF 清單失敗: {e}")
            return error_response(str(e), 500)


@api.route('/etf/<string:code>')
@api.param('code', 'ETF 代碼')
class ETFDetail(Resource):
    """ETF 詳情"""

    @api.doc('get_etf')
    def get(self, code):
        """取得單一 ETF 基本資訊"""
        try:
            # 從 ETF 清單中找到該 ETF
            etfs = cache.get(CacheKeys.ETF_LIST)

            if not etfs:
                client = FinMindClient(current_app.config.get('FINMIND_TOKEN'))
                etfs = client.get_all_etfs()
                cache.set(CacheKeys.ETF_LIST, etfs, CacheTTL.DAY_1)

            etf = next((e for e in etfs if e.get('stock_id') == code), None)

            if not etf:
                return error_response(f"找不到 ETF: {code}", 404)

            return success_response(etf)

        except Exception as e:
            logger.error(f"取得 ETF {code} 失敗: {e}")
            return error_response(str(e), 500)


@api.route('/etf/<string:code>/holdings')
@api.param('code', 'ETF 代碼')
class ETFHoldings(Resource):
    """ETF 持股明細"""

    @api.doc('get_etf_holdings')
    @api.param('date', '指定日期 (YYYY-MM-DD)', type=str, required=False)
    @api.param('enrich_prices', '是否附加即時價格', type=bool, default=False)
    def get(self, code):
        """取得 ETF 持股明細"""
        try:
            date = request.args.get('date')
            enrich_prices = request.args.get('enrich_prices', 'false').lower() == 'true'

            # 從快取取得
            cache_key = CacheKeys.ETF_HOLDINGS.format(code=code)
            holdings = cache.get(cache_key)

            if not holdings:
                logger.info(f"快取未命中，從 FinMind 取得 {code} 持股")
                client = FinMindClient(current_app.config.get('FINMIND_TOKEN'))
                holdings = client.get_etf_holdings(code, date=date)

                if not holdings:
                    return error_response(f"找不到 {code} 的持股資料", 404)

                cache.set(cache_key, holdings, CacheTTL.DAY_1)

            # 如果需要附加價格
            if enrich_prices and holdings:
                client = FinMindClient(current_app.config.get('FINMIND_TOKEN'))
                stock_codes = list(set([h.get('stock_id') for h in holdings]))
                prices = client.get_batch_prices(stock_codes[:50])  # 限制 50 檔

                for holding in holdings:
                    stock_code = holding.get('stock_id')
                    if stock_code in prices:
                        price_data = prices[stock_code]
                        holding['current_price'] = price_data.get('close')
                        holding['market_value'] = (
                            holding.get('HoldingShares', 0) * price_data.get('close', 0)
                        )

            # 整理回應資料
            response_data = {
                "etf_code": code,
                "record_date": holdings[0].get('date') if holdings else None,
                "holdings": holdings,
                "total_stocks": len(holdings)
            }

            return success_response(response_data)

        except Exception as e:
            logger.error(f"取得 {code} 持股失敗: {e}")
            return error_response(str(e), 500)


@api.route('/etf/<string:code>/holdings/changes')
@api.param('code', 'ETF 代碼')
class ETFHoldingsChanges(Resource):
    """ETF 持股變化"""

    @api.doc('get_etf_holdings_changes')
    @api.param('days', '比較天數', type=int, default=7)
    def get(self, code):
        """取得 ETF 持股變化"""
        try:
            days = int(request.args.get('days', 7))

            # 這裡需要從資料庫查詢歷史資料
            # 暫時返回空資料
            return success_response({
                "etf_code": code,
                "comparison_days": days,
                "changes": [],
                "note": "需要資料庫支援歷史資料查詢"
            })

        except Exception as e:
            logger.error(f"取得 {code} 持股變化失敗: {e}")
            return error_response(str(e), 500)


@api.route('/etf/<string:code>/similar')
@api.param('code', 'ETF 代碼')
class SimilarETFs(Resource):
    """相似 ETF 推薦"""

    @api.doc('get_similar_etfs')
    @api.param('limit', '推薦數量', type=int, default=5)
    def get(self, code):
        """根據持股相似度推薦 ETF"""
        try:
            limit = int(request.args.get('limit', 5))

            # 這裡需要實作持股重疊分析演算法
            # 暫時返回空資料
            return success_response({
                "etf_code": code,
                "similar_etfs": [],
                "note": "需要實作持股重疊分析"
            })

        except Exception as e:
            logger.error(f"取得 {code} 相似 ETF 失敗: {e}")
            return error_response(str(e), 500)


# ============================================================
# 註冊路由
# ============================================================

def init_app(app, api_instance):
    """初始化 ETF API"""
    api_instance.add_namespace(api, path='/etf')
    app.register_blueprint(etf_bp)
