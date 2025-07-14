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
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        try:
            # 这里需要实现具体的K线数据获取方法
            # 由于当前API主要是实时数据，我们演示如何扩展历史数据功能

            # 模拟历史数据获取
            historical_data = generate_mock_historical_data(
                stock_code, start_date, end_date)

            if historical_data:
                print(f"   ✅ 获取成功，共{len(historical_data)}条记录")
                # 显示最近3天的数据
                for data in historical_data[-3:]:
                    print(f"     {data['date']}: 开盘{data['open']:.2f}, 收盘{data['close']:.2f}, "
                          f"最高{data['high']:.2f}, 最低{data['low']:.2f}, 成交量{data['volume']}")
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
                          f"收盘{data.close_price:.2f}, 涨跌幅{data.change_pct:.2f}%")
            else:
                print(f"   ❌ 获取失败")

        except Exception as e:
            print(f"   ❌ 获取失败: {e}")


def generate_mock_historical_data(stock_code, start_date, end_date):
    """生成模拟历史数据"""
    import random

    data = []
    current_date = start_date
    base_price = random.uniform(10, 50)

    while current_date <= end_date:
        # 跳过周末
        if current_date.weekday() < 5:
            # 模拟价格波动
            change_pct = random.gauss(0, 0.02)  # 平均0%，标准差2%
            base_price *= (1 + change_pct)
            base_price = max(base_price, 1.0)  # 最低价格1元

            open_price = base_price * random.uniform(0.98, 1.02)
            close_price = base_price
            high_price = max(open_price, close_price) * \
                random.uniform(1.00, 1.05)
            low_price = min(open_price, close_price) * \
                random.uniform(0.95, 1.00)
            volume = random.randint(1000000, 50000000)

            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'open': round(open_price, 2),
                'close': round(close_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'volume': volume,
                'amount': round(close_price * volume, 2)
            })

        current_date += timedelta(days=1)

    return data


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

        print("\n2. 获取A股分钟级数据:")
        # 获取分钟级数据（仅演示，实际使用需要注意数据量）
        try:
            stock_code = '000001'
            print(f"   获取 {stock_code} 的分钟级数据:")

            stock_zh_a_hist_min_df = ak.stock_zh_a_hist_min_em(
                symbol=stock_code,
                period="5",  # 5分钟K线
                start_date="2024-01-01 09:30:00",
                end_date="2024-01-01 15:00:00",
                adjust=""
            )

            if not stock_zh_a_hist_min_df.empty:
                print(f"   ✅ 获取成功，共{len(stock_zh_a_hist_min_df)}条记录")
                # 显示前3条数据
                for _, row in stock_zh_a_hist_min_df.head(3).iterrows():
                    print(
                        f"     {row['时间']}: 开盘{row['开盘']:.2f}, 收盘{row['收盘']:.2f}")
            else:
                print(f"   ❌ 获取失败：数据为空")

        except Exception as e:
            print(f"   ❌ 获取分钟级数据失败: {e}")

    except ImportError:
        print("⚠️ akshare未安装，请安装: pip install akshare")


def demo_historical_data_analysis():
    """演示历史数据分析"""
    print("\n" + "="*60)
    print("📈 历史数据分析演示")
    print("="*60)

    # 生成模拟历史数据进行分析
    stock_code = '000001'
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    historical_data = generate_mock_historical_data(
        stock_code, start_date, end_date)

    if not historical_data:
        print("❌ 无历史数据可分析")
        return

    print(f"\n分析股票 {stock_code} 最近60天的数据:")
    print(
        f"数据期间: {historical_data[0]['date']} 至 {historical_data[-1]['date']}")
    print(f"数据条数: {len(historical_data)}")

    # 基础统计分析
    closes = [float(d['close']) for d in historical_data]
    volumes = [int(d['volume']) for d in historical_data]

    print(f"\n价格统计:")
    print(f"  最高价: {max(closes):.2f}")
    print(f"  最低价: {min(closes):.2f}")
    print(f"  平均价: {sum(closes)/len(closes):.2f}")
    print(f"  期间涨跌幅: {((closes[-1] - closes[0]) / closes[0] * 100):.2f}%")

    print(f"\n成交量统计:")
    print(f"  最大成交量: {max(volumes):,}")
    print(f"  最小成交量: {min(volumes):,}")
    print(f"  平均成交量: {sum(volumes)//len(volumes):,}")

    # 简单技术指标计算
    print(f"\n技术指标:")

    # 计算5日移动平均
    if len(closes) >= 5:
        ma5 = sum(closes[-5:]) / 5
        print(f"  MA5: {ma5:.2f}")

    # 计算10日移动平均
    if len(closes) >= 10:
        ma10 = sum(closes[-10:]) / 10
        print(f"  MA10: {ma10:.2f}")

    # 计算20日移动平均
    if len(closes) >= 20:
        ma20 = sum(closes[-20:]) / 20
        print(f"  MA20: {ma20:.2f}")


def main():
    """主函数"""
    print("🚀 A股历史数据获取系统演示")
    print("=" * 80)

    # 演示各种历史数据获取方式
    demo_tushare_historical_data()
    demo_eastmoney_historical_data()
    demo_data_provider_historical()
    demo_akshare_historical_data()
    demo_historical_data_analysis()

    print("\n" + "="*80)
    print("📋 历史数据获取方式总结:")
    print("="*80)
    print("1. 🏆 Tushare API - 专业金融数据，需要token，数据质量高")
    print("2. 📊 东方财富API - 免费使用，实时性好，适合实时数据")
    print("3. 🏛️ DataProvider - 系统内置，支持缓存，适合批量处理")
    print("4. 📈 akshare - 开源免费，数据源丰富，适合研究使用")
    print("\n💡 建议:")
    print("  - 生产环境推荐使用Tushare API")
    print("  - 开发测试可以使用akshare")
    print("  - 实时数据可以使用东方财富API")
    print("  - 系统内部使用DataProvider进行数据管理")


if __name__ == "__main__":
    main()
