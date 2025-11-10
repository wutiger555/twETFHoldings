"""
FinMind API 客戶端
封裝所有 FinMind API 呼叫，包含限流、錯誤處理、重試機制
"""

import requests
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class FinMindRateLimiter:
    """FinMind API 限流器 - 600 requests/hour"""

    def __init__(self, max_requests=600, time_window=3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def acquire(self):
        """取得請求許可"""
        now = time.time()

        # 清理過期請求
        self.requests = [t for t in self.requests if t > now - self.time_window]

        # 檢查限制
        if len(self.requests) >= self.max_requests:
            oldest = self.requests[0]
            wait_time = self.time_window - (now - oldest) + 1
            logger.warning(f"達到 FinMind API 限制，等待 {wait_time:.1f} 秒")
            time.sleep(wait_time)
            return self.acquire()

        self.requests.append(now)
        return True

    def get_remaining(self):
        """取得剩餘請求數"""
        now = time.time()
        self.requests = [t for t in self.requests if t > now - self.time_window]
        return self.max_requests - len(self.requests)


# 全域限流器
rate_limiter = FinMindRateLimiter()


def with_rate_limit(func):
    """裝飾器：自動限流"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        rate_limiter.acquire()
        return func(*args, **kwargs)
    return wrapper


def retry_on_error(max_retries=3, delay=1):
    """裝飾器：自動重試"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"{func.__name__} 失敗，重試 {attempt + 1}/{max_retries}: {e}")
                    time.sleep(delay * (attempt + 1))
        return wrapper
    return decorator


class FinMindClient:
    """FinMind API 客戶端"""

    BASE_URL = "https://api.finmindtrade.com/api/v4/data"

    def __init__(self, token: Optional[str] = None):
        """
        初始化 FinMind 客戶端

        Args:
            token: API token (可選，註冊後可提升限制)
        """
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TW-ETF-App/1.0'
        })

    @with_rate_limit
    @retry_on_error(max_retries=3)
    def _request(
        self,
        dataset: str,
        data_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        通用 API 請求方法

        Args:
            dataset: 資料集名稱
            data_id: 資料 ID (股票代碼、ETF 代碼等)
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)

        Returns:
            API 回應 dict
        """
        params = {
            'dataset': dataset,
        }

        if data_id:
            params['data_id'] = data_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        if self.token:
            params['token'] = self.token

        # 合併額外參數
        params.update(kwargs)

        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 200:
                raise Exception(f"FinMind API 錯誤: {data.get('msg', 'Unknown error')}")

            logger.info(f"FinMind API 成功: {dataset} - {data_id or 'all'}")
            return data

        except requests.RequestException as e:
            logger.error(f"FinMind API 請求失敗: {e}")
            raise

    # ============================================================
    # ETF 相關 API
    # ============================================================

    def get_all_taiwan_stocks(self) -> List[Dict]:
        """
        取得所有台灣股票/ETF 清單

        Returns:
            股票清單
        """
        response = self._request(dataset='TaiwanStockInfo')
        return response.get('data', [])

    def get_all_etfs(self) -> List[Dict]:
        """
        取得所有台灣 ETF 清單

        Returns:
            ETF 清單
        """
        all_stocks = self.get_all_taiwan_stocks()
        etfs = [
            stock for stock in all_stocks
            if stock.get('type') == 'ETF'
        ]
        logger.info(f"找到 {len(etfs)} 個 ETF")
        return etfs

    def get_etf_holdings(
        self,
        etf_code: str,
        date: Optional[str] = None
    ) -> List[Dict]:
        """
        取得 ETF 持股明細

        Args:
            etf_code: ETF 代碼 (如 "0050")
            date: 查詢日期 (可選，預設最近 7 天)

        Returns:
            持股明細列表
        """
        if not date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            start_date = date
            end_date = date

        response = self._request(
            dataset='TaiwanStockHoldingsPer',
            data_id=etf_code,
            start_date=start_date,
            end_date=end_date
        )

        holdings = response.get('data', [])
        logger.info(f"取得 {etf_code} 持股: {len(holdings)} 筆")
        return holdings

    # ============================================================
    # 股價相關 API
    # ============================================================

    def get_stock_price(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        days: int = 30
    ) -> List[Dict]:
        """
        取得股價資料

        Args:
            stock_code: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            days: 天數 (當未指定日期時)

        Returns:
            股價資料列表
        """
        if not start_date or not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        response = self._request(
            dataset='TaiwanStockPrice',
            data_id=stock_code,
            start_date=start_date,
            end_date=end_date
        )

        prices = response.get('data', [])
        logger.info(f"取得 {stock_code} 股價: {len(prices)} 天")
        return prices

    def get_latest_price(self, stock_code: str) -> Optional[Dict]:
        """
        取得最新股價

        Args:
            stock_code: 股票代碼

        Returns:
            最新股價資料
        """
        prices = self.get_stock_price(stock_code, days=5)
        if prices:
            return prices[-1]
        return None

    def get_batch_prices(
        self,
        stock_codes: List[str],
        days: int = 1
    ) -> Dict[str, Dict]:
        """
        批次取得多個股票的價格

        Args:
            stock_codes: 股票代碼列表
            days: 天數

        Returns:
            {股票代碼: 股價資料} 的字典
        """
        result = {}
        for code in stock_codes:
            try:
                price = self.get_latest_price(code)
                if price:
                    result[code] = price
            except Exception as e:
                logger.error(f"取得 {code} 價格失敗: {e}")
                continue

        logger.info(f"批次取得 {len(result)}/{len(stock_codes)} 檔股價")
        return result

    # ============================================================
    # 財務資料 API（進階功能）
    # ============================================================

    def get_stock_financial_statements(
        self,
        stock_code: str,
        year: Optional[int] = None,
        season: Optional[int] = None
    ) -> List[Dict]:
        """
        取得財務報表

        Args:
            stock_code: 股票代碼
            year: 年份
            season: 季度 (1-4)

        Returns:
            財務報表資料
        """
        if not year:
            year = datetime.now().year

        response = self._request(
            dataset='TaiwanStockFinancialStatements',
            data_id=stock_code,
            start_date=f"{year}-01-01"
        )

        return response.get('data', [])

    def get_stock_dividend(
        self,
        stock_code: str,
        years: int = 5
    ) -> List[Dict]:
        """
        取得股利資料

        Args:
            stock_code: 股票代碼
            years: 查詢年數

        Returns:
            股利資料
        """
        end_year = datetime.now().year
        start_year = end_year - years

        response = self._request(
            dataset='TaiwanStockDividend',
            data_id=stock_code,
            start_date=f"{start_year}-01-01"
        )

        return response.get('data', [])

    # ============================================================
    # 統計與分析
    # ============================================================

    def get_market_stats(self) -> Dict[str, Any]:
        """
        取得市場統計資料

        Returns:
            市場統計
        """
        # 這裡可以從其他 API 整合市場資訊
        # 例如大盤指數、成交量等
        return {
            "timestamp": datetime.now().isoformat(),
            "rate_limit_remaining": rate_limiter.get_remaining()
        }

    def health_check(self) -> bool:
        """
        健康檢查

        Returns:
            API 是否正常
        """
        try:
            self.get_all_taiwan_stocks()
            return True
        except Exception as e:
            logger.error(f"FinMind API 健康檢查失敗: {e}")
            return False


# ============================================================
# 使用範例
# ============================================================

if __name__ == "__main__":
    # 設定日誌
    logging.basicConfig(level=logging.INFO)

    # 初始化客戶端
    client = FinMindClient(token=None)  # 替換成你的 token

    # 1. 取得所有 ETF
    print("\n=== 取得所有 ETF ===")
    etfs = client.get_all_etfs()
    print(f"找到 {len(etfs)} 個 ETF")
    print(f"前 5 個: {[e['stock_id'] for e in etfs[:5]]}")

    # 2. 取得 0050 持股
    print("\n=== 取得 0050 持股 ===")
    holdings = client.get_etf_holdings("0050")
    if holdings:
        print(f"持股數量: {len(holdings)}")
        print(f"最新日期: {holdings[-1].get('date')}")

    # 3. 取得台積電股價
    print("\n=== 取得台積電股價 ===")
    price = client.get_latest_price("2330")
    if price:
        print(f"日期: {price.get('date')}")
        print(f"收盤價: {price.get('close')}")

    # 4. 批次取得股價
    print("\n=== 批次取得股價 ===")
    prices = client.get_batch_prices(["2330", "2317", "2454"])
    for code, data in prices.items():
        print(f"{code}: {data.get('close')}")

    # 5. 剩餘請求數
    print(f"\n剩餘請求數: {rate_limiter.get_remaining()}/600")
