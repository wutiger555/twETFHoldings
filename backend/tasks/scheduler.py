"""
定時任務排程器
使用 APScheduler 實作自動化資料更新
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TaskScheduler:
    """定時任務排程器"""

    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone='Asia/Taipei',
            job_defaults={
                'coalesce': True,  # 合併累積的任務
                'max_instances': 1  # 同時只執行一個實例
            }
        )
        self.is_running = False

    def start(self):
        """啟動排程器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("定時任務排程器已啟動")

    def shutdown(self):
        """關閉排程器"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("定時任務排程器已關閉")

    def add_daily_job(
        self,
        func,
        hour: int,
        minute: int = 0,
        job_id: str = None,
        **kwargs
    ):
        """
        新增每日任務

        Args:
            func: 要執行的函數
            hour: 小時 (0-23)
            minute: 分鐘 (0-59)
            job_id: 任務 ID
            **kwargs: 傳遞給函數的參數
        """
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone='Asia/Taipei'
        )

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id or f"{func.__name__}_{hour}_{minute}",
            kwargs=kwargs,
            replace_existing=True
        )

        logger.info(f"已新增每日任務: {func.__name__} at {hour:02d}:{minute:02d}")

    def add_interval_job(
        self,
        func,
        minutes: int,
        job_id: str = None,
        **kwargs
    ):
        """
        新增間隔任務

        Args:
            func: 要執行的函數
            minutes: 間隔分鐘數
            job_id: 任務 ID
            **kwargs: 傳遞給函數的參數
        """
        trigger = IntervalTrigger(
            minutes=minutes,
            timezone='Asia/Taipei'
        )

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id or f"{func.__name__}_every_{minutes}m",
            kwargs=kwargs,
            replace_existing=True
        )

        logger.info(f"已新增間隔任務: {func.__name__} every {minutes} minutes")

    def add_cron_job(
        self,
        func,
        cron_expression: str,
        job_id: str = None,
        **kwargs
    ):
        """
        新增 Cron 任務

        Args:
            func: 要執行的函數
            cron_expression: Cron 表達式
            job_id: 任務 ID
            **kwargs: 傳遞給函數的參數
        """
        # 解析 Cron 表達式
        # 格式: "分 時 日 月 週"
        parts = cron_expression.split()
        trigger = CronTrigger(
            minute=parts[0] if len(parts) > 0 else '0',
            hour=parts[1] if len(parts) > 1 else '*',
            day=parts[2] if len(parts) > 2 else '*',
            month=parts[3] if len(parts) > 3 else '*',
            day_of_week=parts[4] if len(parts) > 4 else '*',
            timezone='Asia/Taipei'
        )

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id or f"{func.__name__}_cron",
            kwargs=kwargs,
            replace_existing=True
        )

        logger.info(f"已新增 Cron 任務: {func.__name__} ({cron_expression})")

    def remove_job(self, job_id: str):
        """移除任務"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"已移除任務: {job_id}")
        except Exception as e:
            logger.error(f"移除任務失敗 {job_id}: {e}")

    def get_jobs(self):
        """取得所有任務"""
        return self.scheduler.get_jobs()

    def print_jobs(self):
        """列印所有任務"""
        jobs = self.get_jobs()
        if not jobs:
            print("目前沒有排程任務")
            return

        print(f"\n目前排程任務 ({len(jobs)} 個):")
        print("-" * 80)
        for job in jobs:
            print(f"ID: {job.id}")
            print(f"Function: {job.func.__name__}")
            print(f"Trigger: {job.trigger}")
            print(f"Next run: {job.next_run_time}")
            print("-" * 80)


# ============================================================
# 定時任務函數
# ============================================================

def update_etf_list():
    """更新 ETF 清單 - 每日 14:00"""
    from backend.services.finmind import FinMindClient
    from backend.services.cache import cache, CacheKeys, CacheTTL

    logger.info("[定時任務] 開始更新 ETF 清單")

    try:
        client = FinMindClient()
        etfs = client.get_all_etfs()

        # 儲存到快取
        cache.set(CacheKeys.ETF_LIST, etfs, CacheTTL.DAY_1)

        logger.info(f"[定時任務] ETF 清單更新完成: {len(etfs)} 個")

    except Exception as e:
        logger.error(f"[定時任務] 更新 ETF 清單失敗: {e}")


def update_all_etf_holdings():
    """更新所有 ETF 持股 - 每日 14:30"""
    from backend.services.finmind import FinMindClient
    from backend.services.cache import cache, CacheKeys, CacheTTL
    import time

    logger.info("[定時任務] 開始更新所有 ETF 持股")

    try:
        client = FinMindClient()

        # 取得 ETF 清單
        etfs = cache.get(CacheKeys.ETF_LIST)
        if not etfs:
            etfs = client.get_all_etfs()

        success_count = 0
        fail_count = 0

        # 分批更新，避免超過限制
        for i, etf in enumerate(etfs):
            etf_code = etf['stock_id']

            try:
                holdings = client.get_etf_holdings(etf_code)

                if holdings:
                    # 儲存到快取
                    cache_key = CacheKeys.ETF_HOLDINGS.format(code=etf_code)
                    cache.set(cache_key, holdings, CacheTTL.DAY_1)
                    success_count += 1

                    logger.info(f"[定時任務] 已更新 {etf_code} ({i+1}/{len(etfs)})")

                # 每 10 個 ETF 暫停一下，避免過快
                if (i + 1) % 10 == 0:
                    time.sleep(2)

            except Exception as e:
                logger.error(f"[定時任務] 更新 {etf_code} 失敗: {e}")
                fail_count += 1
                continue

        logger.info(f"[定時任務] ETF 持股更新完成: 成功 {success_count}, 失敗 {fail_count}")

    except Exception as e:
        logger.error(f"[定時任務] 更新 ETF 持股失敗: {e}")


def update_popular_stock_prices():
    """更新熱門股票價格 - 每日 14:30"""
    from backend.services.finmind import FinMindClient
    from backend.services.cache import cache, CacheKeys, CacheTTL

    logger.info("[定時任務] 開始更新熱門股票價格")

    try:
        client = FinMindClient()

        # 取得熱門股票清單（從快取統計）
        popular_stocks = cache.get(CacheKeys.STATS_POPULAR)
        if not popular_stocks:
            # 如果沒有快取，使用預設清單
            popular_stocks = [
                "2330", "2317", "2454", "2308", "2303",  # 半導體
                "2882", "2881", "2886", "2891", "2892",  # 金融
                "1301", "1303", "1326", "2002", "2912"   # 傳產
            ]

        success_count = 0

        for stock_code in popular_stocks[:100]:  # 限制 100 檔
            try:
                price = client.get_latest_price(stock_code)

                if price:
                    cache_key = CacheKeys.STOCK_PRICE_DAILY.format(code=stock_code)
                    cache.set(cache_key, price, CacheTTL.DAY_1)
                    success_count += 1

            except Exception as e:
                logger.error(f"[定時任務] 更新 {stock_code} 價格失敗: {e}")
                continue

        logger.info(f"[定時任務] 熱門股票價格更新完成: {success_count} 檔")

    except Exception as e:
        logger.error(f"[定時任務] 更新股票價格失敗: {e}")


def cleanup_expired_cache():
    """清理過期快取 - 每週日 02:00"""
    from backend.services.cache import cache

    logger.info("[定時任務] 開始清理過期快取")

    try:
        # Redis 會自動清理過期快取，這裡只是記錄
        logger.info("[定時任務] 快取清理完成（Redis 自動管理）")

    except Exception as e:
        logger.error(f"[定時任務] 清理快取失敗: {e}")


def backup_database():
    """備份資料庫 - 每日 03:00"""
    import os
    import subprocess
    from datetime import datetime

    logger.info("[定時任務] 開始備份資料庫")

    try:
        # 這裡是備份 PostgreSQL 的範例
        backup_dir = os.getenv('BACKUP_DIR', '/backups')
        db_name = os.getenv('DB_NAME', 'etf_app')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/backup_{db_name}_{timestamp}.sql"

        # 執行 pg_dump
        # 注意：需要設定環境變數 PGPASSWORD
        command = f"pg_dump {db_name} > {backup_file}"
        subprocess.run(command, shell=True, check=True)

        # 刪除 7 天前的備份
        command = f"find {backup_dir} -name 'backup_*.sql' -mtime +7 -delete"
        subprocess.run(command, shell=True, check=True)

        logger.info(f"[定時任務] 資料庫備份完成: {backup_file}")

    except Exception as e:
        logger.error(f"[定時任務] 資料庫備份失敗: {e}")


# ============================================================
# 排程器初始化
# ============================================================

# 全域排程器實例
scheduler = TaskScheduler()


def init_scheduler():
    """初始化所有定時任務"""

    logger.info("初始化定時任務排程器...")

    # 1. 每日更新 ETF 清單 (14:00)
    scheduler.add_daily_job(
        update_etf_list,
        hour=14,
        minute=0,
        job_id='update_etf_list'
    )

    # 2. 每日更新 ETF 持股 (14:30)
    scheduler.add_daily_job(
        update_all_etf_holdings,
        hour=14,
        minute=30,
        job_id='update_etf_holdings'
    )

    # 3. 每日更新熱門股價 (14:30)
    scheduler.add_daily_job(
        update_popular_stock_prices,
        hour=14,
        minute=30,
        job_id='update_stock_prices'
    )

    # 4. 每週日清理快取 (02:00)
    scheduler.add_cron_job(
        cleanup_expired_cache,
        cron_expression='0 2 * * 0',  # 週日 2:00
        job_id='cleanup_cache'
    )

    # 5. 每日備份資料庫 (03:00)
    scheduler.add_daily_job(
        backup_database,
        hour=3,
        minute=0,
        job_id='backup_database'
    )

    # 啟動排程器
    scheduler.start()

    # 列印所有任務
    scheduler.print_jobs()

    logger.info("定時任務排程器初始化完成")


# ============================================================
# 使用範例
# ============================================================

if __name__ == "__main__":
    import logging
    import time

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(message)s'
    )

    # 初始化排程器
    init_scheduler()

    # 手動觸發測試（開發時使用）
    print("\n立即執行測試任務...")
    # update_etf_list()

    # 保持運行
    try:
        print("\n排程器運行中... (Ctrl+C 退出)")
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n正在關閉排程器...")
        scheduler.shutdown()
        print("排程器已關閉")
