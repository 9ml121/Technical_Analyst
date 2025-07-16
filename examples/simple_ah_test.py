#!/usr/bin/env python3
"""
简化版AH股历史行情数据测试脚本

主要使用akshare测试以下市场的历史数据获取：
- 上交所：60开头（主板）、688开头（科创板）
- 深交所：00开头（主板）、300开头（创业板）
- 港股通：港股数据
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import time

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def test_akshare_ah_data():
    """使用akshare测试AH股历史数据获取"""
    print("🚀 AH股历史行情数据测试 - akshare版本")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        import akshare as ak
        import pandas as pd
    except ImportError:
        print("❌ akshare未安装，请先安装: pip install akshare")
        return

    # 测试股票代码
    test_stocks = {
        '上交所主板': ['600000', '600036', '600519'],  # 浦发银行、招商银行、贵州茅台
        '上交所科创板': ['688001', '688002', '688003'],  # 华兴源创、睿创微纳、天准科技
        '深交所主板': ['000001', '000002', '000858'],  # 平安银行、万科A、五粮液
        '深交所创业板': ['300001', '300002', '300059'],  # 特锐德、神州泰岳、东方财富
        '港股通': ['00700', '00941', '02318']  # 腾讯控股、中国移动、中国平安
    }

    # 测试时间范围
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    print(
        f"\n📅 测试时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print(f"📊 测试股票总数: {sum(len(codes) for codes in test_stocks.values())} 只")

    total_success = 0
    total_failed = 0

    for market_name, stock_codes in test_stocks.items():
        print(f"\n🏛️ 测试市场: {market_name}")
        print("-" * 60)

        market_success = 0
        market_failed = 0

        for stock_code in stock_codes:
            print(f"\n   测试股票: {stock_code}")

            try:
                # 获取历史数据
                start_date_str = start_date.strftime('%Y%m%d')
                end_date_str = end_date.strftime('%Y%m%d')

                if stock_code.startswith('6') or stock_code.startswith('0') or stock_code.startswith('3'):
                    # A股数据
                    df = ak.stock_zh_a_hist(
                        symbol=stock_code,
                        period="daily",
                        start_date=start_date_str,
                        end_date=end_date_str,
                        adjust=""
                    )
                else:
                    # 港股数据
                    df = ak.stock_hk_hist(
                        symbol=stock_code,
                        period="daily",
                        start_date=start_date_str,
                        end_date=end_date_str,
                        adjust=""
                    )

                if not df.empty:
                    print(f"   ✅ 成功获取 {len(df)} 条历史数据")

                    # 显示最近3天的数据
                    print("   最近3天数据:")
                    for _, row in df.tail(3).iterrows():
                        if '日期' in df.columns:
                            # A股数据格式
                            date_str = row['日期']
                            open_price = row['开盘']
                            close_price = row['收盘']
                            pct_change = row.get('涨跌幅', 0)
                            print(
                                f"     {date_str}: 开盘{open_price:.2f}, 收盘{close_price:.2f}, 涨跌幅{pct_change:.2f}%")
                        else:
                            # 港股数据格式
                            date_str = row['日期']
                            open_price = row['开盘']
                            close_price = row['收盘']
                            print(
                                f"     {date_str}: 开盘{open_price:.2f}, 收盘{close_price:.2f}")

                    market_success += 1
                    total_success += 1
                else:
                    print(f"   ❌ 获取失败: 数据为空")
                    market_failed += 1
                    total_failed += 1

            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
                market_failed += 1
                total_failed += 1

            # 添加延迟避免请求过于频繁
            time.sleep(0.5)

        print(
            f"\n   📈 {market_name} 测试结果: 成功 {market_success}, 失败 {market_failed}")

    print(f"\n🎯 总体测试结果:")
    print(f"   总成功: {total_success}, 总失败: {total_failed}")
    if total_success + total_failed > 0:
        success_rate = total_success / (total_success + total_failed) * 100
        print(f"   成功率: {success_rate:.1f}%")

    print("\n" + "="*80)
    print("🎉 测试完成!")
    print("="*80)


def test_eastmoney_simple():
    """简单测试东方财富API"""
    print("\n📊 简单测试东方财富API")
    print("="*50)

    try:
        from market_data.fetchers.eastmoney_api import EastMoneyAPI

        api = EastMoneyAPI()

        # 测试获取实时数据
        print("测试获取A股实时数据...")
        stocks = api.get_a_stock_realtime(limit=5)

        if stocks:
            print(f"✅ 成功获取 {len(stocks)} 只股票的实时数据")
            for stock in stocks[:3]:
                print(
                    f"   {stock.get('name', 'N/A')} ({stock.get('code', 'N/A')}): {stock.get('price', 0):.2f}")
        else:
            print("❌ 获取实时数据失败")

        # 测试获取单只股票详情
        print("\n测试获取单只股票详情...")
        test_code = '000001'
        detail = api.get_stock_detail(test_code)

        if detail:
            print(f"✅ 成功获取 {test_code} 详情")
            print(f"   名称: {detail.get('name', 'N/A')}")
            print(f"   价格: {detail.get('price', 0):.2f}")
            print(f"   涨跌幅: {detail.get('pct_change', 0):.2f}%")
        else:
            print(f"❌ 获取 {test_code} 详情失败")

    except Exception as e:
        print(f"❌ 东方财富API测试失败: {e}")


def test_tushare_simple():
    """简单测试Tushare API"""
    print("\n📈 简单测试Tushare API")
    print("="*50)

    try:
        from market_data.fetchers.tushare_api import TushareAPI

        api = TushareAPI()

        if not api.is_available():
            print("⚠️ Tushare API不可用，请配置token")
            return

        # 测试获取股票基本信息
        print("测试获取股票基本信息...")
        stock_info = api.get_stock_basic()

        if stock_info:
            print(f"✅ 成功获取 {len(stock_info)} 只股票的基本信息")
            for stock in stock_info[:3]:
                print(
                    f"   {stock.get('ts_code', 'N/A')}: {stock.get('name', 'N/A')}")
        else:
            print("❌ 获取股票基本信息失败")

    except Exception as e:
        print(f"❌ Tushare API测试失败: {e}")


def main():
    """主函数"""
    # 测试akshare
    test_akshare_ah_data()

    # 测试其他数据源
    test_eastmoney_simple()
    test_tushare_simple()

    print("\n💡 测试建议:")
    print("- akshare是最稳定的免费数据源，支持A股和港股")
    print("- 东方财富API适合获取实时数据")
    print("- Tushare API需要token，但数据质量较高")
    print("- 建议在生产环境中使用多个数据源互补")


if __name__ == "__main__":
    main()
