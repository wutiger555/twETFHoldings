"""
搜尋 API 路由
提供全域搜尋功能
"""

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
import logging

from backend.services.finmind import FinMindClient
from backend.services.cache import cache, CacheKeys, CacheTTL

logger = logging.getLogger(__name__)

# 創建 Namespace
api = Namespace('search', description='搜尋功能')

# ============================================================
# API Models
# ============================================================

search_result_model = api.model('SearchResult', {
    'code': fields.String(description='代碼'),
    'name': fields.String(description='名稱'),
    'type': fields.String(description='類型 (ETF/STOCK)'),
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


def build_search_index():
    """建立搜尋索引"""
    try:
        # 檢查快取
        index = cache.get(CacheKeys.SEARCH_INDEX)
        if index:
            return index

        logger.info("建立搜尋索引...")

        # 從 FinMind 取得所有股票/ETF
        from flask import current_app
        client = FinMindClient(current_app.config.get('FINMIND_TOKEN'))
        all_stocks = client.get_all_taiwan_stocks()

        # 建立索引
        index = []
        for stock in all_stocks:
            index.append({
                'code': stock.get('stock_id'),
                'name': stock.get('stock_name'),
                'type': stock.get('type'),
                'industry': stock.get('industry', ''),
                'market': stock.get('market', '')
            })

        # 快取索引
        cache.set(CacheKeys.SEARCH_INDEX, index, CacheTTL.DAY_1)

        logger.info(f"搜尋索引建立完成: {len(index)} 筆")
        return index

    except Exception as e:
        logger.error(f"建立搜尋索引失敗: {e}")
        return []


def search_items(query, item_type=None):
    """
    搜尋項目

    Args:
        query: 搜尋關鍵字
        item_type: 類型篩選 (ETF/STOCK/None)

    Returns:
        搜尋結果列表
    """
    index = build_search_index()

    if not index:
        return []

    query = query.lower()
    results = []

    for item in index:
        # 類型篩選
        if item_type and item.get('type') != item_type:
            continue

        # 搜尋代碼或名稱
        code = item.get('code', '').lower()
        name = item.get('name', '').lower()

        if query in code or query in name:
            results.append({
                'code': item.get('code'),
                'name': item.get('name'),
                'type': item.get('type'),
                'industry': item.get('industry'),
                'market': item.get('market')
            })

    return results


# ============================================================
# API Routes
# ============================================================

@api.route('')
class Search(Resource):
    """全域搜尋"""

    @api.doc('search')
    @api.param('q', '搜尋關鍵字', required=True, type=str)
    @api.param('type', '類型篩選 (ETF/STOCK)', type=str, required=False)
    @api.param('limit', '結果數量限制', type=int, default=20)
    @api.response(200, 'Success', fields.List(fields.Nested(search_result_model)))
    def get(self):
        """搜尋 ETF 或股票"""
        try:
            query = request.args.get('q')
            item_type = request.args.get('type')
            limit = int(request.args.get('limit', 20))

            if not query:
                error_response("請提供搜尋關鍵字", 400)

            if len(query) < 2:
                error_response("搜尋關鍵字至少 2 個字元", 400)

            # 執行搜尋
            results = search_items(query, item_type)

            # 限制結果數量
            results = results[:limit]

            # 依類型分組
            grouped = {
                'etfs': [r for r in results if r.get('type') == 'ETF'],
                'stocks': [r for r in results if r.get('type') != 'ETF']
            }

            return success_response({
                'query': query,
                'total': len(results),
                'etfs': grouped['etfs'],
                'stocks': grouped['stocks']
            })

        except Exception as e:
            logger.error(f"搜尋失敗: {e}")
            error_response(str(e), 500)


@api.route('/suggest')
class SearchSuggest(Resource):
    """搜尋建議"""

    @api.doc('search_suggest')
    @api.param('q', '搜尋關鍵字', required=True, type=str)
    @api.param('limit', '結果數量限制', type=int, default=5)
    @api.response(200, 'Success')
    def get(self):
        """取得搜尋建議（自動完成）"""
        try:
            query = request.args.get('q')
            limit = int(request.args.get('limit', 5))

            if not query:
                return success_response({'suggestions': []})

            # 執行搜尋
            results = search_items(query)

            # 只返回代碼和名稱
            suggestions = [
                {'code': r['code'], 'name': r['name'], 'type': r['type']}
                for r in results[:limit]
            ]

            return success_response({'suggestions': suggestions})

        except Exception as e:
            logger.error(f"搜尋建議失敗: {e}")
            error_response(str(e), 500)
