"""
Redis 快取管理器
提供統一的快取介面，支援自動序列化、TTL 管理
"""

import json
import logging
from typing import Any, Optional, Callable
from functools import wraps
from datetime import timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available, using memory cache")

logger = logging.getLogger(__name__)


class CacheManager:
    """快取管理器"""

    def __init__(self, redis_url: Optional[str] = None):
        """
        初始化快取管理器

        Args:
            redis_url: Redis 連接字串 (如 redis://localhost:6379/0)
        """
        self.redis_client = None
        self.memory_cache = {}  # 備援記憶體快取

        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(
                    redis_url,
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("Redis 快取已連接")
            except Exception as e:
                logger.error(f"Redis 連接失敗，使用記憶體快取: {e}")
                self.redis_client = None
        else:
            logger.warning("使用記憶體快取（不建議用於生產環境）")

    def get(self, key: str) -> Optional[Any]:
        """
        取得快取值

        Args:
            key: 快取鍵

        Returns:
            快取值，若不存在則回傳 None
        """
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"快取命中: {key}")
                    return json.loads(value)
            else:
                # 使用記憶體快取
                if key in self.memory_cache:
                    logger.debug(f"記憶體快取命中: {key}")
                    return self.memory_cache[key]

            logger.debug(f"快取未命中: {key}")
            return None

        except Exception as e:
            logger.error(f"取得快取失敗 {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        設定快取值

        Args:
            key: 快取鍵
            value: 快取值
            ttl: 過期時間（秒），None 表示永不過期

        Returns:
            是否成功
        """
        try:
            serialized = json.dumps(value, ensure_ascii=False)

            if self.redis_client:
                if ttl:
                    self.redis_client.setex(key, ttl, serialized)
                else:
                    self.redis_client.set(key, serialized)
                logger.debug(f"已快取: {key} (TTL: {ttl}s)")
                return True
            else:
                # 記憶體快取（不支援 TTL）
                self.memory_cache[key] = value
                logger.debug(f"已快取到記憶體: {key}")
                return True

        except Exception as e:
            logger.error(f"設定快取失敗 {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        刪除快取

        Args:
            key: 快取鍵

        Returns:
            是否成功
        """
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                self.memory_cache.pop(key, None)
            logger.debug(f"已刪除快取: {key}")
            return True
        except Exception as e:
            logger.error(f"刪除快取失敗 {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        刪除符合模式的所有快取

        Args:
            pattern: 鍵值模式 (如 "etf:*")

        Returns:
            刪除的數量
        """
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
                    logger.info(f"已刪除 {count} 個快取: {pattern}")
                    return count
            else:
                # 記憶體快取
                keys_to_delete = [
                    k for k in self.memory_cache.keys()
                    if k.startswith(pattern.replace('*', ''))
                ]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                logger.info(f"已從記憶體刪除 {len(keys_to_delete)} 個快取")
                return len(keys_to_delete)

            return 0

        except Exception as e:
            logger.error(f"清除快取失敗 {pattern}: {e}")
            return 0

    def get_ttl(self, key: str) -> Optional[int]:
        """
        取得快取剩餘時間

        Args:
            key: 快取鍵

        Returns:
            剩餘秒數，-1 表示永不過期，None 表示不存在
        """
        try:
            if self.redis_client:
                ttl = self.redis_client.ttl(key)
                return ttl if ttl >= -1 else None
            return None
        except Exception as e:
            logger.error(f"取得 TTL 失敗 {key}: {e}")
            return None


# ============================================================
# 快取裝飾器
# ============================================================

def cached(
    key_pattern: str,
    ttl: int = 3600,
    cache_manager: Optional[CacheManager] = None
):
    """
    快取裝飾器

    Args:
        key_pattern: 快取鍵模式，支援 {arg_name} 格式
        ttl: 過期時間（秒）
        cache_manager: 快取管理器實例

    Example:
        @cached("etf:holdings:{etf_code}", ttl=86400)
        def get_etf_holdings(etf_code):
            # 實際邏輯
            pass
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 如果沒有提供 cache_manager，則不使用快取
            if not cache_manager:
                return func(*args, **kwargs)

            # 生成快取鍵
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            cache_key = key_pattern.format(**bound_args.arguments)

            # 嘗試從快取取得
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.info(f"從快取返回: {cache_key}")
                return cached_value

            # 執行函數
            result = func(*args, **kwargs)

            # 儲存到快取
            if result is not None:
                cache_manager.set(cache_key, result, ttl)
                logger.info(f"已快取結果: {cache_key}")

            return result

        return wrapper
    return decorator


# ============================================================
# 預定義快取鍵與 TTL
# ============================================================

class CacheKeys:
    """快取鍵常數"""

    # ETF 相關
    ETF_LIST = "etf:list"
    ETF_INFO = "etf:info:{code}"
    ETF_HOLDINGS = "etf:holdings:{code}"
    ETF_HOLDINGS_DATE = "etf:holdings:{code}:{date}"

    # 股票相關
    STOCK_INFO = "stock:info:{code}"
    STOCK_PRICE_DAILY = "stock:price:{code}:daily"
    STOCK_PRICE_HISTORY = "stock:history:{code}:{days}d"

    # 統計相關
    STATS_POPULAR = "stats:popular_stocks"
    STATS_MARKET = "stats:market"

    # 搜尋相關
    SEARCH_INDEX = "search:index"


class CacheTTL:
    """快取過期時間常數（秒）"""

    MINUTE_1 = 60
    MINUTE_5 = 300
    MINUTE_15 = 900
    HOUR_1 = 3600
    HOUR_6 = 21600
    DAY_1 = 86400
    WEEK_1 = 604800


# ============================================================
# 全域快取管理器
# ============================================================

# 初始化全域快取管理器（需要在 app 初始化時設定 redis_url）
cache = CacheManager()


def init_cache(redis_url: str):
    """初始化全域快取管理器"""
    global cache
    cache = CacheManager(redis_url)
    return cache


# ============================================================
# 使用範例
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 初始化快取（使用記憶體快取示範）
    cache = CacheManager()

    # 1. 基本使用
    print("\n=== 基本快取操作 ===")
    cache.set("test:key", {"data": "value"}, ttl=60)
    value = cache.get("test:key")
    print(f"取得快取: {value}")

    # 2. 使用裝飾器
    print("\n=== 使用快取裝飾器 ===")

    @cached("etf:holdings:{etf_code}", ttl=CacheTTL.DAY_1, cache_manager=cache)
    def get_etf_holdings(etf_code: str):
        print(f"實際查詢 {etf_code}...")
        return {
            "etf_code": etf_code,
            "holdings": [
                {"code": "2330", "weight": 45.5},
                {"code": "2317", "weight": 8.2}
            ]
        }

    # 第一次呼叫：實際查詢
    result1 = get_etf_holdings("0050")
    print(f"結果 1: {result1}")

    # 第二次呼叫：從快取取得
    result2 = get_etf_holdings("0050")
    print(f"結果 2: {result2}")

    # 3. 清除快取
    print("\n=== 清除快取 ===")
    count = cache.clear_pattern("etf:*")
    print(f"已清除 {count} 個快取")
