import os
import json
import time
import requests
import logging
from typing import List, Dict, Any, Optional
from flask import Flask, redirect
from flask_restx import Api, Resource, fields

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

# --- App and API Initialization ---
app = Flask(__name__)
api = Api(app, version='6.0', title='台股 ETF 資訊 API (本地測試)',
          description='一個整合了「即時查詢」與「本地快取讀取」的複合式 API',
          doc='/apidocs/'
)

# --- Constants & Data Directory ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

# --- Issuer Mapping ---
ISSUER_MAPPING: Dict[str, Dict[str, str]] = {
    "元大": {"id": "yuanta", "name": "元大投信"},
    "富邦": {"id": "fubon", "name": "富邦投信"},
    "國泰": {"id": "cathay", "name": "國泰投信"},
    # ... (add other issuers as needed)
}

# --- In-Memory Cache for Live Data ---
_cache: Dict[str, Any] = {'data': None, 'timestamp': 0}
CACHE_DURATION: int = 3600  # 1 hour

def get_categorized_etfs() -> Dict[str, Any]:
    """
    Fetches a categorized list of all domestic ETFs from the Taiwan Stock Exchange (TWSE).
    
    The data is fetched live from the TWSE website and is cached in memory for
    one hour to reduce redundant requests.
    
    Returns:
        A dictionary containing categorized ETF data.
        
    Raises:
        Exception: If fetching data from TWSE fails and no cached data is available.
    """
    current_time = time.time()
    if _cache['data'] and (current_time - _cache['timestamp']) < CACHE_DURATION:
        return _cache['data']

    logging.info("Cache expired or empty. Fetching live data from TWSE...")
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        timestamp = int(time.time() * 1000)
        twse_url = f"https://www.twse.com.tw/rwd/zh/ETF/domestic?response=json&_={timestamp}"
        response = requests.get(twse_url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('stat') != 'OK':
            raise Exception(f"TWSE API returned a non-OK status: {data.get('stat')}")

        etfs_by_issuer: Dict[str, List[Dict[str, str]]] = {info['id']: [] for info in ISSUER_MAPPING.values()}
        etfs_by_issuer['other'] = []
        raw_etfs = [{"code": item[0], "name": item[1]} for item in data.get('data', [])]

        for etf in raw_etfs:
            found = False
            for keyword, issuer_info in ISSUER_MAPPING.items():
                if keyword in etf['name']:
                    etfs_by_issuer[issuer_info['id']].append(etf)
                    found = True
                    break
            if not found:
                etfs_by_issuer['other'].append(etf)
        
        issuers = list(ISSUER_MAPPING.values()) + [{"id": "other", "name": "其他"}]
        categorized_data = {"issuers": issuers, "etfs_by_issuer": etfs_by_issuer}
        
        _cache['data'] = categorized_data
        _cache['timestamp'] = current_time
        logging.info(f"Successfully fetched and cached data for {len(raw_etfs)} ETFs.")
        return categorized_data

    except Exception as e:
        logging.error(f"Failed to fetch data from TWSE: {e}")
        if _cache['data']:
            logging.warning("Serving stale data from cache due to fetch failure.")
            return _cache['data']
        api.abort(500, f"Failed to fetch data from TWSE and no cache is available: {e}")

# --- API Namespaces and Models ---
live_ns = api.namespace('live', description='從公開來源即時抓取資料')
cached_ns = api.namespace('cached', description='讀取由爬蟲預先抓取的本地快取資料')

etf_model = api.model('ETF', {
    'code': fields.String(required=True, description='ETF 代碼'),
    'name': fields.String(required=True, description='ETF 名稱')
})

issuer_model = api.model('Issuer', {
    'id': fields.String(required=True, description='發行商的唯一識別ID'),
    'name': fields.String(required=True, description='發行商的中文名稱')
})

holding_model = api.model('Holding', {
    'asset_type': fields.String(required=True, description='資產類別 (stock, future, bond)'),
    'code': fields.String(required=True, description='商品代碼'),
    'name': fields.String(required=True, description='商品名稱'),
    'shares': fields.Integer(description='持有股數/口數 (債券則為 null)'),
    'weight': fields.Float(description='佔比權重 (%) (債券可能為 null)')
})

holding_file_model = api.model('HoldingFile', {
    'last_updated_utc': fields.String(required=True, description='資料最後更新時間 (UTC)'),
    'holdings': fields.List(fields.Nested(holding_model))
})

# --- API Routes ---
@app.route('/')
def index() -> Any:
    """Redirects the root URL to the API documentation page."""
    return redirect('/apidocs')

# --- Live Data Endpoints ---
@live_ns.route('/issuers')
class IssuerList(Resource):
    @live_ns.doc('live_list_issuers')
    @live_ns.marshal_list_with(issuer_model)
    def get(self) -> List[Dict[str, str]]:
        """(即時) 列出所有偵測到的 ETF 發行商"""
        data = get_categorized_etfs()
        return data['issuers']

@live_ns.route('/issuers/<string:issuer_id>/etfs')
@live_ns.param('issuer_id', '發行商的ID (例如: yuanta, fubon, cathay...)')
class ETFsByIssuer(Resource):
    @live_ns.doc('live_list_etfs_by_issuer')
    @live_ns.marshal_list_with(etf_model)
    @api.response(404, '找不到指定的發行商')
    def get(self, issuer_id: str) -> List[Dict[str, str]]:
        """(即時) 根據發行商ID，列出該發行商旗下的所有ETF"""
        data = get_categorized_etfs()
        etf_list = data['etfs_by_issuer'].get(issuer_id)
        if etf_list is None:
            api.abort(404, f"Issuer with id '{issuer_id}' not found.")
        return etf_list

# --- Cached Data Endpoints ---
@cached_ns.route('/etfs')
class CachedETFList(Resource):
    """Lists all ETFs that have been successfully scraped and cached."""
    etf_manifest_item_model = api.model('ETFManifestItem', {
        'code': fields.String(required=True, description='ETF 代碼'),
        'name': fields.String(required=True, description='ETF 名稱'),
        'firm_id': fields.String(required=True, description='發行商 ID'),
        'firm_name': fields.String(required=True, description='發行商名稱'),
        'last_updated_utc': fields.String(required=True, description='資料最後更新時間 (UTC)')
    })

    @cached_ns.doc('list_cached_etfs')
    @cached_ns.marshal_list_with(etf_manifest_item_model)
    @api.response(404, '找不到 etf_list.json 檔案 (請先執行爬蟲)')
    def get(self) -> List[Dict[str, Any]]:
        """(讀取快取) 列出由爬蟲成功抓取的 ETF 清單 (含時間戳)"""
        manifest_path = os.path.join(DATA_DIR, "etf_list.json")
        if not os.path.exists(manifest_path):
            api.abort(404, "etf_list.json not found. Please run the scraper script first.")
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to read or parse manifest file {manifest_path}: {e}")
            api.abort(500, "Could not process the ETF manifest file.")

@cached_ns.route('/holdings/<string:etf_code>')
@cached_ns.param('etf_code', '要查詢的 ETF 代碼 (例如: 0050)')
class CachedHoldingResource(Resource):
    """Retrieves the detailed holdings for a specific cached ETF."""
    @cached_ns.doc('get_cached_holdings')
    @cached_ns.marshal_with(holding_file_model)
    @api.response(400, '無效的 ETF 代碼格式')
    @api.response(404, '找不到指定的 ETF 持股資料')
    def get(self, etf_code: str) -> Dict[str, Any]:
        """(讀取快取) 查詢指定 ETF 的詳細持股資料 (含時間戳)"""
        if not etf_code.isalnum() or '..' in etf_code or '/' in etf_code:
            api.abort(400, "Invalid ETF code format.")
        
        file_path = os.path.join(DATA_DIR, f"{etf_code}.json")
        if not os.path.exists(file_path):
            api.abort(404, f"Holdings for ETF {etf_code} not found. Please run the scraper script.")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to read or parse holding file {file_path}: {e}")
            api.abort(500, f"Could not process holding file for ETF {etf_code}.")

if __name__ == '__main__':
    app.run(debug=True)
