#!/usr/bin/env python3
"""
港股数据获取测试脚本

测试不同的港股代码格式和数据源
"""

from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
import sys
import os
from datetime import date, timedelta

# 动态导入src目录下的模块，优先查找src
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


def test_hk_stocks():
    """测试港股数据获取"""
    fetcher = FreeDataSourcesFetcher()

    # 测试不同的港股代码
    hk_stocks = [
        "00700",  # 腾讯控股
        "00941",  # 中国移动
        "02318",  # 中国平安
        "00005",  # 汇丰控股
        "00388",  # 香港交易所
    ]

    end = date.today()
    start = end - timedelta(days=7)  # 只测试最近7天

    print("🔍 港股数据获取测试")
    print("=" * 50)

    for stock_code in hk_stocks:
        print(f"\n📈 测试港股: {stock_code}")
        print("-" * 30)

        # 测试akshare
        print("1. 测试akshare数据源:")
        try:
            data = fetcher._fetch_from_akshare(stock_code, start, end)
            if data:
                print(f"   ✅ 成功获取 {len(data)} 条数据")
                print(f"   最新数据: {data[0]}")
            else:
                print("   ❌ 获取失败或数据为空")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

        # 测试Yahoo Finance
        print("2. 测试Yahoo Finance数据源:")
        try:
            data = fetcher._fetch_from_yahoo(stock_code, start, end)
            if data:
                print(f"   ✅ 成功获取 {len(data)} 条数据")
                print(f"   最新数据: {data[0]}")
            else:
                print("   ❌ 获取失败或数据为空")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

        # 测试整合获取
        print("3. 测试整合获取:")
        try:
            data = fetcher.get_historical_data_with_fallback(
                stock_code, start, end, market_type="h_stock")
            if data:
                print(f"   ✅ 整合获取成功 {len(data)} 条数据")
                print(f"   数据源: {data[0].get('source', 'unknown')}")
            else:
                print("   ❌ 整合获取失败")
        except Exception as e:
            print(f"   ❌ 异常: {e}")


def test_yahoo_codes():
    """测试Yahoo Finance代码格式"""
    print("\n🔧 Yahoo Finance代码格式测试")
    print("=" * 50)

    import yfinance as yf
    from datetime import date, timedelta

    test_codes = [
        "00700.HK",
        "0700.HK",
        "700.HK",
        "00941.HK",
        "0941.HK",
        "941.HK"
    ]

    end = date.today()
    start = end - timedelta(days=3)

    for code in test_codes:
        print(f"\n测试代码: {code}")
        try:
            ticker = yf.Ticker(code)
            df = ticker.history(start=start, end=end)
            if not df.empty:
                print(f"  ✅ 成功，数据条数: {len(df)}")
                print(f"  最新价格: {df['Close'].iloc[-1]:.2f}")
            else:
                print("  ❌ 数据为空")
        except Exception as e:
            print(f"  ❌ 失败: {e}")


if __name__ == "__main__":
    test_hk_stocks()
    test_yahoo_codes()
