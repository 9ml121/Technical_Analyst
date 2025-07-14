#!/usr/bin/env python3
"""
A股历史数据获取示例

演示如何使用系统获取A股历史K线数据、日线数据等
"""

from quant_system.utils.logger import get_logger
from quant_system.core.data_provider import HistoricalDataProvider
from market_data.fetchers.eastmoney_api import EastMoneyAPI
from market_data.fetchers.tushare_api import TushareAPI
import sys
from pathlib import Path
from datetime import datetime, date, timedelta

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


logger = get_logger(__name__)


def demo_tushare_historical_data():
    """演示使用Tushare获取历史数据"""
    print("\n" + "="*60)
    print("📊 Tushare历史数据获取演示")
    print("="*60)

    api = TushareAPI()

    if not api.is_available():
        print("⚠️ Tushare API不可用，请配置token")
        print("   配置方法：在config/default.yaml中设置tushare_token")
        return

    # 获取股票基本信息
    print("\n1. 获取股票基本信息:")
    stock_info = api.get_stock_basic()
    if stock_info:
        print(f"   ✅ 获取成功，共{len(stock_info)}只股票")
        # 显示前5只股票信息
        for i, stock in enumerate(stock_info[:5]):
            print(
                f"   {i+1}. {stock['ts_code']} - {stock['name']} ({stock['industry']})")

    # 获取日线数据
    print("\n2. 获取日线历史数据:")
    test_stocks = ['000001.SZ', '600000.SH', '000002.SZ']  # 平安银行、浦发银行、万科A

    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')

    for ts_code in test_stocks:
        print(f"\n   获取 {ts_code} 的历史数据:")
        daily_data = api.get_daily_data(ts_code, start_date, end_date)

        if daily_data:
            print(f"   ✅ 获取成功，共{len(daily_data)}条记录")
            # 显示最近3天的数据
            for i, data in enumerate(daily_data[-3:]):
                print(f"     {data['trade_date']}: 开盘{data['open']}, 收盘{data['close']}, "
                      f"涨跌幅{data['pct_chg']:.2f}%")
        else:
            print(f"   ❌ 获取失败")


def demo_eastmoney_historical_data():
    """演示使用东方财富API获取历史数据"""
    print("\n" + "="*60)
    print("📈 东方财富历史数据获取演示")
    print("="*60)

    api = EastMoneyAPI()

    # 获取A股历史K线数据
    print("\n1. 获取A股历史K线数据:")
    test_stocks = ['000001', '600000', '000002']  # 平安银行、浦发银行、万科A

    for stock_code in test_stocks:
        print(f"\n   获取 {stock_code} 的K线数据:")

        # 获取最近30天的日K线数据
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        try:
            historical_data = api.get_historical_data(
                stock_code, start_date, end_date)

            if historical_data:
                print(f"   ✅ 获取成功，共{len(historical_data)}条记录")
                # 显示最近3天的数据
                for data in historical_data[-3:]:
                    print(f"     {data['date']}: 开盘{data['open']:.2f}, 收盘{data['close']:.2f}, "
                          f"最高{data['high']:.2f}, 最低{data['low']:.2f}, 涨跌幅{data['pct_change']:.2f}%")
            else:
                print(f"   ❌ 获取失败")

        except Exception as e:
            print(f"   ❌ 获取失败: {e}")


def demo_data_provider_historical():
    """演示使用HistoricalDataProvider获取历史数据"""
    print("\n" + "="*60)
    print("🏛️ HistoricalDataProvider历史数据获取演示")
    print("="*60)

    provider = HistoricalDataProvider()

    # 获取历史数据
    print("\n1. 获取历史数据:")
    test_stocks = ['000001', '600000', '000002']

    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    for stock_code in test_stocks:
        print(f"\n   获取 {stock_code} 的历史数据:")

        try:
            historical_data = provider.get_historical_data(
                stock_code, start_date, end_date)

            if historical_data:
                print(f"   ✅ 获取成功，共{len(historical_data)}条记录")
                # 显示最近3条数据
                for data in historical_data[-3:]:
                    print(f"     {data.date}: {data.name} - 开盘{data.open_price:.2f}, "
                          f"收盘{data.close_price:.2f}, 涨跌幅{data.pct_change:.2f}%")
            else:
                print(f"   ❌ 获取失败")

        except Exception as e:
            print(f"   ❌ 获取失败: {e}")


def demo_akshare_historical_data():
    """演示使用akshare获取历史数据"""
    print("\n" + "="*60)
    print("📊 akshare历史数据获取演示")
    print("="*60)

    try:
        import akshare as ak

        print("\n1. 获取A股历史日K线数据:")
        test_stocks = ['000001', '600000', '000002']

        for stock_code in test_stocks:
            print(f"\n   获取 {stock_code} 的历史K线数据:")

            try:
                # 获取历史日K线数据
                stock_zh_a_hist_df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date="20240101",
                    end_date="20241231",
                    adjust=""
                )

                if not stock_zh_a_hist_df.empty:
                    print(f"   ✅ 获取成功，共{len(stock_zh_a_hist_df)}条记录")
                    # 显示最近3天的数据
                    for _, row in stock_zh_a_hist_df.tail(3).iterrows():
                        print(f"     {row['日期']}: 开盘{row['开盘']:.2f}, 收盘{row['收盘']:.2f}, "
                              f"最高{row['最高']:.2f}, 最低{row['最低']:.2f}")
                else:
                    print(f"   ❌ 获取失败：数据为空")

            except Exception as e:
                print(f"   ❌ 获取失败: {e}")

    except ImportError:
        print("⚠️ akshare未安装，请安装: pip install akshare")


def main():
    """主函数"""
    print("🚀 A股历史数据获取系统演示")
    print("=" * 80)

    # 演示各种历史数据获取方式
    demo_tushare_historical_data()
    demo_eastmoney_historical_data()
    demo_data_provider_historical()
    demo_akshare_historical_data()

    print("\n" + "="*80)
    print("📋 历史数据获取方式总结:")
    print("="*80)
    print("1. 🏆 Tushare API - 专业金融数据，需要token，数据质量高")
    print("2. 📊 东方财富API - 免费使用，实时性好，适合实时数据")
    print("3. 🏛️ HistoricalDataProvider - 系统内置，支持缓存，适合批量处理")
    print("4. 📈 akshare - 开源免费，数据源丰富，适合研究使用")
    print("\n💡 建议:")
    print("  - 生产环境推荐使用Tushare API")
    print("  - 开发测试可以使用akshare")
    print("  - 实时数据可以使用东方财富API")
    print("  - 系统内部使用HistoricalDataProvider进行数据管理")


if __name__ == "__main__":
    main()
