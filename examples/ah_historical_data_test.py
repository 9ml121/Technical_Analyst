#!/usr/bin/env python3
"""
AH股历史行情数据测试脚本

测试获取以下市场的历史数据：
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

try:
    from market_data.fetchers.eastmoney_api import EastMoneyAPI
    from market_data.fetchers.tushare_api import TushareAPI
    from quant_system.utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)


class AHHistoricalDataTester:
    """AH股历史数据测试器"""

    def __init__(self):
        """初始化测试器"""
        self.eastmoney_api = EastMoneyAPI()
        self.tushare_api = TushareAPI()

        # 测试股票代码
        self.test_stocks = {
            # 浦发银行、招商银行、贵州茅台、伊利股份
            '上交所主板': ['600000', '600036', '600519', '600887'],
            # 华兴源创、睿创微纳、天准科技、容百科技
            '上交所科创板': ['688001', '688002', '688003', '688005'],
            # 平安银行、万科A、五粮液、新希望
            '深交所主板': ['000001', '000002', '000858', '000876'],
            # 特锐德、神州泰岳、东方财富、智飞生物
            '深交所创业板': ['300001', '300002', '300059', '300122'],
            '港股通': ['00700', '00941', '02318', '03988']  # 腾讯控股、中国移动、中国平安、中国银行
        }

        # 测试时间范围
        self.end_date = date.today()
        self.start_date = self.end_date - timedelta(days=30)

    def test_eastmoney_historical_data(self):
        """测试东方财富API获取历史数据"""
        print("\n" + "="*80)
        print("📊 测试东方财富API - AH股历史数据获取")
        print("="*80)

        total_success = 0
        total_failed = 0

        for market_name, stock_codes in self.test_stocks.items():
            print(f"\n🏛️ 测试市场: {market_name}")
            print("-" * 60)

            market_success = 0
            market_failed = 0

            for stock_code in stock_codes:
                print(f"\n   测试股票: {stock_code}")

                try:
                    # 获取历史数据
                    historical_data = self.eastmoney_api.get_historical_data(
                        stock_code, self.start_date, self.end_date
                    )

                    if historical_data:
                        print(f"   ✅ 成功获取 {len(historical_data)} 条历史数据")

                        # 显示最近3天的数据
                        print("   最近3天数据:")
                        for data in historical_data[-3:]:
                            print(f"     {data['date']}: 开盘{data['open']:.2f}, "
                                  f"收盘{data['close']:.2f}, 涨跌幅{data['pct_change']:.2f}%")

                        market_success += 1
                        total_success += 1
                    else:
                        print(f"   ❌ 获取失败: 无数据返回")
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

        print(f"\n🎯 东方财富API总体测试结果:")
        print(f"   总成功: {total_success}, 总失败: {total_failed}")
        print(f"   成功率: {total_success/(total_success+total_failed)*100:.1f}%")

    def test_tushare_historical_data(self):
        """测试Tushare API获取历史数据"""
        print("\n" + "="*80)
        print("📈 测试Tushare API - AH股历史数据获取")
        print("="*80)

        if not self.tushare_api.is_available():
            print("⚠️ Tushare API不可用，跳过测试")
            print("   请配置TUSHARE_TOKEN环境变量或在config中设置token")
            return

        total_success = 0
        total_failed = 0

        for market_name, stock_codes in self.test_stocks.items():
            print(f"\n🏛️ 测试市场: {market_name}")
            print("-" * 60)

            market_success = 0
            market_failed = 0

            for stock_code in stock_codes:
                print(f"\n   测试股票: {stock_code}")

                try:
                    # 转换为Tushare格式的代码
                    if stock_code.startswith('6'):
                        ts_code = f"{stock_code}.SH"
                    elif stock_code.startswith('0') or stock_code.startswith('3'):
                        ts_code = f"{stock_code}.SZ"
                    else:
                        # 港股代码，Tushare可能不支持
                        print(f"   ⚠️ 跳过港股代码 {stock_code} (Tushare主要支持A股)")
                        continue

                    # 获取日线数据
                    daily_data = self.tushare_api.get_daily_data(
                        ts_code,
                        self.start_date.strftime('%Y%m%d'),
                        self.end_date.strftime('%Y%m%d')
                    )

                    if daily_data:
                        print(f"   ✅ 成功获取 {len(daily_data)} 条日线数据")

                        # 显示最近3天的数据
                        print("   最近3天数据:")
                        for data in daily_data[-3:]:
                            print(f"     {data['trade_date']}: 开盘{data['open']:.2f}, "
                                  f"收盘{data['close']:.2f}, 涨跌幅{data['pct_chg']:.2f}%")

                        market_success += 1
                        total_success += 1
                    else:
                        print(f"   ❌ 获取失败: 无数据返回")
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

        print(f"\n🎯 Tushare API总体测试结果:")
        print(f"   总成功: {total_success}, 总失败: {total_failed}")
        if total_success + total_failed > 0:
            print(
                f"   成功率: {total_success/(total_success+total_failed)*100:.1f}%")

    def test_akshare_historical_data(self):
        """测试akshare获取历史数据"""
        print("\n" + "="*80)
        print("📊 测试akshare - AH股历史数据获取")
        print("="*80)

        try:
            import akshare as ak
        except ImportError:
            print("⚠️ akshare未安装，跳过测试")
            print("   安装命令: pip install akshare")
            return

        total_success = 0
        total_failed = 0

        for market_name, stock_codes in self.test_stocks.items():
            print(f"\n🏛️ 测试市场: {market_name}")
            print("-" * 60)

            market_success = 0
            market_failed = 0

            for stock_code in stock_codes:
                print(f"\n   测试股票: {stock_code}")

                try:
                    # 获取历史数据
                    start_date = self.start_date.strftime('%Y%m%d')
                    end_date = self.end_date.strftime('%Y%m%d')

                    if stock_code.startswith('6') or stock_code.startswith('0') or stock_code.startswith('3'):
                        # A股数据
                        df = ak.stock_zh_a_hist(
                            symbol=stock_code,
                            period="daily",
                            start_date=start_date,
                            end_date=end_date,
                            adjust=""
                        )
                    else:
                        # 港股数据
                        df = ak.stock_hk_hist(
                            symbol=stock_code,
                            period="daily",
                            start_date=start_date,
                            end_date=end_date,
                            adjust=""
                        )

                    if not df.empty:
                        print(f"   ✅ 成功获取 {len(df)} 条历史数据")

                        # 显示最近3天的数据
                        print("   最近3天数据:")
                        for _, row in df.tail(3).iterrows():
                            if '日期' in df.columns:
                                # A股数据格式
                                print(f"     {row['日期']}: 开盘{row['开盘']:.2f}, "
                                      f"收盘{row['收盘']:.2f}, 涨跌幅{row.get('涨跌幅', 0):.2f}%")
                            else:
                                # 港股数据格式
                                print(f"     {row['日期']}: 开盘{row['开盘']:.2f}, "
                                      f"收盘{row['收盘']:.2f}")

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

        print(f"\n🎯 akshare总体测试结果:")
        print(f"   总成功: {total_success}, 总失败: {total_failed}")
        if total_success + total_failed > 0:
            print(
                f"   成功率: {total_success/(total_success+total_failed)*100:.1f}%")

    def test_market_coverage(self):
        """测试市场覆盖情况"""
        print("\n" + "="*80)
        print("🌍 市场覆盖情况分析")
        print("="*80)

        print("\n📋 测试股票列表:")
        for market_name, stock_codes in self.test_stocks.items():
            print(f"\n{market_name}:")
            for i, code in enumerate(stock_codes, 1):
                print(f"  {i}. {code}")

        print(f"\n📅 测试时间范围:")
        print(f"   开始日期: {self.start_date.strftime('%Y-%m-%d')}")
        print(f"   结束日期: {self.end_date.strftime('%Y-%m-%d')}")
        print(f"   测试天数: {(self.end_date - self.start_date).days + 1} 天")

        print(f"\n🎯 测试目标:")
        print(f"   - 上交所主板 (60开头): {len(self.test_stocks['上交所主板'])} 只")
        print(f"   - 上交所科创板 (688开头): {len(self.test_stocks['上交所科创板'])} 只")
        print(f"   - 深交所主板 (00开头): {len(self.test_stocks['深交所主板'])} 只")
        print(f"   - 深交所创业板 (300开头): {len(self.test_stocks['深交所创业板'])} 只")
        print(f"   - 港股通: {len(self.test_stocks['港股通'])} 只")
        print(
            f"   总计: {sum(len(codes) for codes in self.test_stocks.values())} 只股票")

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 AH股历史行情数据测试开始")
        print("=" * 80)
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 显示测试概览
        self.test_market_coverage()

        # 运行各种数据源的测试
        self.test_eastmoney_historical_data()
        self.test_tushare_historical_data()
        self.test_akshare_historical_data()

        print("\n" + "="*80)
        print("🎉 测试完成!")
        print("="*80)
        print("\n📊 测试总结:")
        print("1. 东方财富API - 免费，支持A股和港股，实时性好")
        print("2. Tushare API - 专业数据，主要支持A股，需要token")
        print("3. akshare - 开源免费，支持A股和港股，数据源丰富")
        print("\n💡 建议:")
        print("- 生产环境推荐使用Tushare API (A股) + 东方财富API (港股)")
        print("- 开发测试可以使用akshare")
        print("- 实时数据优先使用东方财富API")


def main():
    """主函数"""
    tester = AHHistoricalDataTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
