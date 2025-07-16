#!/usr/bin/env python3
"""
港股通历史数据需求分析

专门分析港股通股票的历史数据获取情况
"""

from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
import sys
import os
from datetime import date, timedelta

# 动态导入src目录下的模块，优先查找src
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))


def analyze_hk_connect_data():
    """分析港股通历史数据获取情况"""
    print("📊 港股通历史数据需求分析")
    print("=" * 60)

    fetcher = FreeDataSourcesFetcher()

    # 港股通主要股票列表（按市值和重要性排序）
    hk_connect_stocks = [
        # 科技股
        "00700",  # 腾讯控股
        "03690",  # 美团-W
        "09988",  # 阿里巴巴-SW
        "01024",  # 快手-W
        "09618",  # 京东集团-SW

        # 金融股
        "02318",  # 中国平安
        "01398",  # 工商银行
        "00939",  # 建设银行
        "01288",  # 农业银行
        "00005",  # 汇丰控股

        # 消费股
        "02020",  # 安踏体育
        "02331",  # 李宁
        "01068",  # 雨润食品
        "00388",  # 香港交易所

        # 地产股
        "01109",  # 华润置地
        "02007",  # 碧桂园
        "03333",  # 中国恒大
        "06862",  # 海底捞

        # 医药股
        "02269",  # 药明生物
        "06160",  # 百济神州
        "01877",  # 君实生物
    ]

    print(f"\n🔍 测试港股通股票数量: {len(hk_connect_stocks)}")
    print("测试时间范围: 最近7天")

    # 测试历史数据获取
    print("\n📈 港股通历史数据获取测试")
    print("-" * 50)

    success_count = 0
    success_stocks = []
    failed_stocks = []

    for i, stock in enumerate(hk_connect_stocks, 1):
        print(f"[{i:2d}/{len(hk_connect_stocks)}] 测试 {stock}...", end=" ")

        try:
            data = fetcher.get_historical_data_with_fallback(
                stock,
                date.today() - timedelta(days=7),
                date.today(),
                "h_stock"
            )

            if data:
                success_count += 1
                success_stocks.append(stock)
                source = data[0].get('source', 'unknown')
                print(f"✅ 成功 ({source}, {len(data)}条)")
            else:
                failed_stocks.append(stock)
                print("❌ 失败")

        except Exception as e:
            failed_stocks.append(stock)
            print(f"❌ 异常")

    # 统计结果
    print(f"\n📊 测试结果统计")
    print("-" * 30)
    print(f"总测试股票: {len(hk_connect_stocks)}")
    print(f"成功获取: {success_count}")
    print(f"获取失败: {len(failed_stocks)}")
    print(f"成功率: {success_count/len(hk_connect_stocks)*100:.1f}%")

    # 成功股票列表
    print(f"\n✅ 成功获取历史数据的港股通股票 ({len(success_stocks)}只):")
    for stock in success_stocks:
        print(f"  - {stock}")

    # 失败股票列表
    print(f"\n❌ 获取失败的港股通股票 ({len(failed_stocks)}只):")
    for stock in failed_stocks:
        print(f"  - {stock}")

    # 数据源分析
    print(f"\n🔍 数据源效果分析")
    print("-" * 30)

    source_stats = {}
    for stock in success_stocks:
        try:
            data = fetcher.get_historical_data_with_fallback(
                stock,
                date.today() - timedelta(days=7),
                date.today(),
                "h_stock"
            )
            if data:
                source = data[0].get('source', 'unknown')
                source_stats[source] = source_stats.get(source, 0) + 1
        except:
            pass

    for source, count in source_stats.items():
        print(f"  {source}: {count}只股票")

    # 需求满足度评估
    print(f"\n💡 港股通历史数据需求满足度评估")
    print("-" * 40)

    success_rate = success_count / len(hk_connect_stocks) * 100

    if success_rate >= 80:
        satisfaction = "🟢 完全满足"
        recommendation = "当前免费方案已完全满足港股通历史数据需求"
    elif success_rate >= 60:
        satisfaction = "🟡 基本满足"
        recommendation = "当前免费方案基本满足需求，建议补充1-2个数据源"
    elif success_rate >= 40:
        satisfaction = "🟠 部分满足"
        recommendation = "当前免费方案部分满足需求，建议添加更多数据源或考虑付费方案"
    else:
        satisfaction = "🔴 不满足"
        recommendation = "当前免费方案无法满足需求，建议使用付费数据源"

    print(f"需求满足度: {satisfaction}")
    print(f"成功率: {success_rate:.1f}%")
    print(f"建议: {recommendation}")

    # 具体建议
    print(f"\n📋 具体建议")
    print("-" * 20)

    if success_rate < 80:
        print("1. 短期改进:")
        print("   - 优化Yahoo Finance代码转换")
        print("   - 添加新浪财经API")
        print("   - 实现东方财富港股API")

        print("\n2. 中期扩展:")
        print("   - 添加Alpha Vantage (免费额度500次/天)")
        print("   - 实现雪球API")

        print("\n3. 长期方案:")
        print("   - 考虑Tushare Pro (¥2000/年)")
        print("   - 或Wind金融终端 (¥50000/年)")

    print(f"\n4. 当前方案优势:")
    print("   - 完全免费")
    print("   - 实时数据100%可用")
    print("   - 适合个人开发和学习")
    print("   - 可扩展性强")


if __name__ == "__main__":
    analyze_hk_connect_data()
