#!/usr/bin/env python3
"""
FinMind API 使用範例
官網：https://finmind.github.io/
註冊：https://finmindtrade.com/ (免費，600 req/hr)
"""

import requests
import json
from datetime import datetime, timedelta

# FinMind API 基礎 URL
FINMIND_API = "https://api.finmindtrade.com/api/v4/data"

def get_etf_holdings(etf_code: str, token: str = None) -> dict:
    """
    取得 ETF 持股明細

    Args:
        etf_code: ETF 代碼，如 "0050"
        token: API token（註冊後取得，可提升請求限制）

    Returns:
        持股資料 dict
    """
    params = {
        "dataset": "TaiwanStockHoldingsPer",  # ETF 持股比例
        "data_id": etf_code,
        "start_date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
    }

    if token:
        params["token"] = token

    try:
        response = requests.get(FINMIND_API, params=params, timeout=10)
        data = response.json()

        if data['status'] == 200:
            return {
                "success": True,
                "data": data['data'],
                "msg": data.get('msg', '')
            }
        else:
            return {
                "success": False,
                "msg": data.get('msg', 'Unknown error')
            }
    except Exception as e:
        return {
            "success": False,
            "msg": str(e)
        }

def get_stock_price(stock_code: str, days: int = 5, token: str = None) -> dict:
    """
    取得個股價格資料

    Args:
        stock_code: 股票代碼，如 "2330"
        days: 取得最近幾天的資料
        token: API token

    Returns:
        價格資料 dict
    """
    params = {
        "dataset": "TaiwanStockPrice",  # 股價資料
        "data_id": stock_code,
        "start_date": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
    }

    if token:
        params["token"] = token

    try:
        response = requests.get(FINMIND_API, params=params, timeout=10)
        data = response.json()

        if data['status'] == 200:
            return {
                "success": True,
                "data": data['data'],
                "msg": data.get('msg', '')
            }
        else:
            return {
                "success": False,
                "msg": data.get('msg', 'Unknown error')
            }
    except Exception as e:
        return {
            "success": False,
            "msg": str(e)
        }

def get_all_taiwan_etf(token: str = None) -> dict:
    """
    取得所有台灣 ETF 清單

    Args:
        token: API token

    Returns:
        ETF 清單 dict
    """
    params = {
        "dataset": "TaiwanStockInfo",  # 股票資訊
    }

    if token:
        params["token"] = token

    try:
        response = requests.get(FINMIND_API, params=params, timeout=10)
        data = response.json()

        if data['status'] == 200:
            # 過濾出 ETF（type 為 ETF）
            etfs = [item for item in data['data'] if item.get('type') == 'ETF']
            return {
                "success": True,
                "data": etfs,
                "count": len(etfs)
            }
        else:
            return {
                "success": False,
                "msg": data.get('msg', 'Unknown error')
            }
    except Exception as e:
        return {
            "success": False,
            "msg": str(e)
        }

# ============================================================
# 使用範例
# ============================================================

if __name__ == "__main__":
    # 註冊後可取得 token，提升請求限制
    # 免費用戶：300 req/hr
    # 註冊用戶：600 req/hr
    TOKEN = None  # 替換成你的 token

    print("=" * 60)
    print("FinMind API 測試")
    print("=" * 60)

    # 1. 取得所有 ETF 清單
    print("\n[1] 取得所有 ETF 清單")
    result = get_all_taiwan_etf(TOKEN)
    if result['success']:
        print(f"✅ 找到 {result['count']} 個 ETF")
        print(f"前 5 個：")
        for etf in result['data'][:5]:
            print(f"   {etf['stock_id']}: {etf['stock_name']}")
    else:
        print(f"❌ {result['msg']}")

    # 2. 取得 0050 持股明細
    print("\n[2] 取得 0050 持股明細")
    result = get_etf_holdings("0050", TOKEN)
    if result['success']:
        print(f"✅ 成功取得 {len(result['data'])} 筆持股資料")
        if result['data']:
            latest = result['data'][-1]
            print(f"最新日期：{latest.get('date')}")
            print(f"範例資料：{json.dumps(latest, ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ {result['msg']}")

    # 3. 取得台積電股價
    print("\n[3] 取得台積電股價")
    result = get_stock_price("2330", days=5, token=TOKEN)
    if result['success']:
        print(f"✅ 成功取得 {len(result['data'])} 天股價")
        if result['data']:
            latest = result['data'][-1]
            print(f"最新日期：{latest.get('date')}")
            print(f"收盤價：{latest.get('close')}")
            print(f"成交量：{latest.get('Trading_Volume')}")
    else:
        print(f"❌ {result['msg']}")

    print("\n" + "=" * 60)
    print("💡 下一步")
    print("=" * 60)
    print("1. 註冊 FinMind：https://finmindtrade.com/")
    print("2. 取得 API Token")
    print("3. 將此範例整合到你的 scraper 中")
    print("4. 享受零維護的資料來源！")
