#!/usr/bin/env python3
"""
測試新方案：統一資料來源
目的：驗證是否可行，再決定是否重構
"""

import requests
import json
from datetime import datetime

def test_sitca_etf_holdings():
    """測試：從投信投顧公會取得 ETF 持股"""
    print("=" * 60)
    print("測試 1: 投信投顧公會 - ETF 持股資料")
    print("=" * 60)

    # 這個需要實際測試網站結構
    # 可能的端點（需要驗證）
    etf_code = "0050"
    url = f"https://www.sitca.org.tw/Products/ETF/Stock.aspx?txtStockCode={etf_code}"

    try:
        response = requests.get(url, timeout=10)
        print(f"✅ 狀態碼：{response.status_code}")
        print(f"✅ 回應大小：{len(response.text)} bytes")
        print(f"📝 需要進一步解析 HTML 來提取持股資料")
        return True
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

def test_twstock_price():
    """測試：使用 twstock 取得即時股價"""
    print("\n" + "=" * 60)
    print("測試 2: twstock - 即時股價")
    print("=" * 60)

    try:
        import twstock

        # 測試台積電
        stock_code = "2330"
        print(f"📊 查詢股票：{stock_code} (台積電)")

        stock = twstock.realtime.get(stock_code)

        if stock['success']:
            price = stock['realtime']['latest_trade_price']
            change = stock['realtime']['change']
            print(f"✅ 即時價格：{price}")
            print(f"✅ 漲跌：{change}")
            print(f"✅ 成交量：{stock['realtime']['accumulate_trade_volume']}")
            return True
        else:
            print(f"❌ 無法取得資料")
            return False

    except ImportError:
        print("⚠️  twstock 未安裝")
        print("請執行：pip install twstock")
        return False
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

def test_yfinance_price():
    """測試：使用 yfinance 取得股價"""
    print("\n" + "=" * 60)
    print("測試 3: yfinance - 歷史股價")
    print("=" * 60)

    try:
        import yfinance as yf

        stock_code = "2330.TW"
        print(f"📊 查詢股票：{stock_code}")

        ticker = yf.Ticker(stock_code)
        hist = ticker.history(period="5d")

        if not hist.empty:
            latest = hist.iloc[-1]
            print(f"✅ 最新收盤價：{latest['Close']:.2f}")
            print(f"✅ 成交量：{int(latest['Volume']):,}")
            print(f"✅ 資料筆數：{len(hist)}")
            return True
        else:
            print(f"❌ 無資料")
            return False

    except ImportError:
        print("⚠️  yfinance 未安裝")
        print("請執行：pip install yfinance")
        return False
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

def test_twse_opendata():
    """測試：證交所開放資料（你現在已經在用的）"""
    print("\n" + "=" * 60)
    print("測試 4: 證交所開放資料 - 基金資料")
    print("=" * 60)

    # 你已經在用的 API
    url = "https://mopsfin.twse.com.tw/opendata/t187ap47_L.csv"

    try:
        response = requests.get(url, timeout=30, verify=False)
        if response.status_code == 200:
            lines = response.text.split('\n')
            print(f"✅ 資料筆數：{len(lines) - 1}")
            print(f"✅ 這個 API 已經在你的專案中使用")
            print(f"📝 可能還有其他端點包含持股明細")
            return True
        else:
            print(f"❌ 狀態碼：{response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

def test_twse_etf_list():
    """測試：從證交所取得所有 ETF 清單"""
    print("\n" + "=" * 60)
    print("測試 5: 證交所 - ETF 清單（你已經在用）")
    print("=" * 60)

    import urllib3
    urllib3.disable_warnings()

    url = "https://www.twse.com.tw/rwd/zh/ETF/domestic?response=json"

    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0'},
            verify=False,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('stat') == 'OK':
                etf_count = len(data['data'])
                print(f"✅ 找到 {etf_count} 個 ETF")
                print(f"✅ 前 5 個：")
                for item in data['data'][:5]:
                    print(f"   - {item[0]}: {item[1]}")
                return True
        print(f"❌ 無法取得資料")
        return False
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return False

def main():
    print("\n🚀 開始測試新的資料來源方案\n")

    results = {
        "投信投顧公會": test_sitca_etf_holdings(),
        "twstock 即時價格": test_twstock_price(),
        "yfinance 歷史價格": test_yfinance_price(),
        "證交所開放資料": test_twse_opendata(),
        "證交所 ETF 清單": test_twse_etf_list(),
    }

    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)

    for name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} - {name}")

    success_rate = sum(results.values()) / len(results) * 100
    print(f"\n成功率：{success_rate:.0f}%")

    print("\n" + "=" * 60)
    print("💡 建議")
    print("=" * 60)

    if success_rate >= 60:
        print("✅ 新方案可行！建議開始重構")
        print("\n下一步：")
        print("1. 安裝缺少的套件：pip install twstock yfinance")
        print("2. 研究投信投顧公會的網站結構")
        print("3. 開始建立 scraper_v2.py")
    else:
        print("⚠️  部分測試失敗，需要進一步研究")
        print("建議先解決測試中的問題")

if __name__ == "__main__":
    main()
