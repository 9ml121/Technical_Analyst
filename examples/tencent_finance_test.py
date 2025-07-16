#!/usr/bin/env python3
"""
腾讯财经API测试脚本

测试腾讯财经API的港股数据获取效果
"""

from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
from market_data.fetchers.tencent_finance_api import TencentFinanceAPI
import sys
import os
from datetime import date, timedelta

# 动态导入src目录下的模块，优先查找src
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


def test_tencent_api_direct():
    """直接测试腾讯财经API"""
    print("🔍 直接测试腾讯财经API")
    print("=" * 50)

    api = TencentFinanceAPI()

    # 测试连接
    print("1. 测试连接:")
    if api.test_connection():
        print("   ✅ 连接成功")
    else:
        print("   ❌ 连接失败")

    # 测试港股列表
    hk_stocks = [
        "00700",  # 腾讯控股
        "00941",  # 中国移动
        "02318",  # 中国平安
        "00005",  # 汇丰控股
        "00388",  # 香港交易所
    ]

    print("\n2. 测试实时数据:")
    for stock in hk_stocks:
        try:
            data = api.get_stock_detail(stock)
            if data:
                print(
                    f"   ✅ {stock}: {data.get('name', 'N/A')} - ¥{data.get('current_price', 0):.2f}")
            else:
                print(f"   ❌ {stock}: 获取失败")
        except Exception as e:
            print(f"   ❌ {stock}: 异常 - {e}")

    # 测试历史数据
    print("\n3. 测试历史数据:")
    end = date.today()
    start = end - timedelta(days=7)

    for stock in hk_stocks[:2]:  # 只测试前2个
        try:
            data = api.get_historical_data(stock, start, end)
            if data:
                print(f"   ✅ {stock}: 获取 {len(data)} 条历史数据")
                print(f"      最新: {data[0]}")
            else:
                print(f"   ❌ {stock}: 历史数据获取失败")
        except Exception as e:
            print(f"   ❌ {stock}: 异常 - {e}")


def test_integrated_fetcher():
    """测试集成后的数据获取器"""
    print("\n🔍 测试集成后的免费数据源整合器")
    print("=" * 50)

    fetcher = FreeDataSourcesFetcher()

    # 测试港股数据获取
    hk_stocks = ["00700", "00941", "00005"]
    end = date.today()
    start = end - timedelta(days=7)

    print("测试港股数据获取:")
    for stock in hk_stocks:
        print(f"\n📈 {stock}:")
        try:
            data = fetcher.get_historical_data_with_fallback(
                stock, start, end, "h_stock")
            if data:
                print(f"   ✅ 成功获取 {len(data)} 条数据")
                print(f"   数据源: {data[0].get('source', 'unknown')}")
                print(f"   最新数据: {data[0]}")
            else:
                print("   ❌ 获取失败")
        except Exception as e:
            print(f"   ❌ 异常: {e}")


def compare_data_sources():
    """比较不同数据源的效果"""
    print("\n🔍 数据源效果对比")
    print("=" * 50)

    fetcher = FreeDataSourcesFetcher()

    # 获取可用数据源
    hk_sources = fetcher.get_available_sources("h_stock")
    print(f"港股可用数据源: {hk_sources}")

    # 测试单个股票在不同数据源的效果
    test_stock = "00700"
    end = date.today()
    start = end - timedelta(days=3)

    print(f"\n测试股票 {test_stock} 在不同数据源的效果:")

    for source in hk_sources:
        print(f"\n{source}:")
        try:
            if source == "akshare":
                data = fetcher._fetch_from_akshare(test_stock, start, end)
            elif source == "yahoo_finance":
                data = fetcher._fetch_from_yahoo(test_stock, start, end)
            elif source == "tencent_finance":
                data = fetcher._fetch_from_tencent(test_stock, start, end)
            else:
                continue

            if data:
                print(f"   ✅ 成功，{len(data)} 条数据")
            else:
                print("   ❌ 失败")
        except Exception as e:
            print(f"   ❌ 异常: {e}")


if __name__ == "__main__":
    test_tencent_api_direct()
    test_integrated_fetcher()
    compare_data_sources()
