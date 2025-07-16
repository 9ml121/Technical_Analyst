#!/usr/bin/env python3
"""
搜索最近A股市场短期爆发能力强的股票
- 搜索最近3个月内有过2-5日大涨的股票
- 按爆发力排序，获取最活跃的股票
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import akshare as ak
import warnings
warnings.filterwarnings('ignore')

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


def get_recent_explosive_stocks():
    """获取最近爆发力强的股票"""

    print("🔍 搜索最近A股市场短期爆发能力强的股票...")

    # 获取A股所有股票列表
    try:
        stock_list = ak.stock_zh_a_spot_em()
        print(f"✅ 获取到 {len(stock_list)} 只A股股票")
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return []

    # 筛选有效股票代码
    valid_stocks = []
    for _, row in stock_list.iterrows():
        code = row['代码']
        if code.startswith(('300', '688', '000', '002', '600', '601', '603')):
            valid_stocks.append(code)

    print(f"📊 筛选出 {len(valid_stocks)} 只有效股票")

    # 分析最近3个月的爆发力
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    explosive_stocks = []

    # 分批处理，避免请求过多
    batch_size = 50
    for i in range(0, len(valid_stocks), batch_size):
        batch = valid_stocks[i:i+batch_size]
        print(f"📈 分析第 {i//batch_size + 1} 批股票 ({len(batch)} 只)...")

        for code in batch:
            try:
                # 获取历史数据
                stock_data = ak.stock_zh_a_hist(symbol=code, period="daily",
                                                start_date=start_date.strftime(
                                                    '%Y%m%d'),
                                                end_date=end_date.strftime(
                                                    '%Y%m%d'),
                                                adjust="qfq")

                if len(stock_data) < 20:  # 数据不足
                    continue

                # 计算爆发力指标
                stock_data['涨跌幅'] = stock_data['涨跌幅'] / 100  # 转换为小数

                # 计算2-5日累计涨幅
                explosive_score = 0
                max_5d_return = 0
                explosive_days = 0

                for j in range(4, len(stock_data)):
                    # 计算5日累计涨幅
                    returns_5d = []
                    for k in range(j-4, j+1):
                        if k < len(stock_data):
                            returns_5d.append(stock_data.iloc[k]['涨跌幅'])

                    cumulative_return = sum(returns_5d)
                    max_5d_return = max(max_5d_return, cumulative_return)

                    # 判断是否为爆发日
                    if cumulative_return > 0.15:  # 5日涨幅超过15%
                        explosive_score += cumulative_return
                        explosive_days += 1

                # 计算平均爆发力
                avg_explosive = explosive_score / max(explosive_days, 1)

                # 计算换手率（如果有数据）
                turnover = 0
                if '换手率' in stock_data.columns:
                    turnover = stock_data['换手率'].mean()

                # 记录爆发力强的股票
                if explosive_days > 0 or max_5d_return > 0.20:
                    explosive_stocks.append({
                        'code': code,
                        'name': row.get('名称', ''),
                        'max_5d_return': max_5d_return,
                        'explosive_days': explosive_days,
                        'avg_explosive': avg_explosive,
                        'turnover': turnover,
                        'market': get_market_type(code)
                    })

            except Exception as e:
                continue

    # 按爆发力排序
    explosive_stocks.sort(key=lambda x: x['max_5d_return'], reverse=True)

    print(f"🎯 找到 {len(explosive_stocks)} 只爆发力强的股票")

    return explosive_stocks


def get_market_type(code):
    """获取股票所属市场"""
    if code.startswith('300'):
        return '创业板'
    elif code.startswith('688'):
        return '科创板'
    elif code.startswith('000') or code.startswith('002'):
        return '深市主板'
    elif code.startswith('600') or code.startswith('601') or code.startswith('603'):
        return '沪市主板'
    else:
        return '其他'


def analyze_explosive_stocks(explosive_stocks):
    """分析爆发股特征"""
    if not explosive_stocks:
        print("❌ 没有找到爆发力强的股票")
        return

    print("\n📊 爆发股分析结果:")
    print("=" * 80)

    # 按市场分类统计
    market_stats = {}
    for stock in explosive_stocks:
        market = stock['market']
        if market not in market_stats:
            market_stats[market] = []
        market_stats[market].append(stock)

    print("📈 各市场爆发股分布:")
    for market, stocks in market_stats.items():
        print(f"  {market}: {len(stocks)} 只")

    print("\n🏆 爆发力最强的前20只股票:")
    print("-" * 80)
    print(f"{'代码':<10} {'市场':<8} {'最大5日涨幅':<12} {'爆发天数':<8} {'平均爆发力':<12}")
    print("-" * 80)

    for i, stock in enumerate(explosive_stocks[:20]):
        print(f"{stock['code']:<10} {stock['market']:<8} "
              f"{stock['max_5d_return']*100:>8.1f}% {stock['explosive_days']:>6} "
              f"{stock['avg_explosive']*100:>8.1f}%")

    # 生成优化后的股票池
    print("\n🎯 推荐股票池（按爆发力排序）:")
    print("-" * 80)

    recommended_stocks = []

    # 创业板爆发股（前15只）
    cyb_stocks = [s for s in explosive_stocks if s['market'] == '创业板'][:15]
    recommended_stocks.extend([s['code'] for s in cyb_stocks])

    # 科创板爆发股（前15只）
    kcb_stocks = [s for s in explosive_stocks if s['market'] == '科创板'][:15]
    recommended_stocks.extend([s['code'] for s in kcb_stocks])

    # 主板爆发股（前20只）
    zb_stocks = [s for s in explosive_stocks if s['market']
                 in ['深市主板', '沪市主板']][:20]
    recommended_stocks.extend([s['code'] for s in zb_stocks])

    print("创业板爆发股（15只）:")
    for stock in cyb_stocks:
        print(f"  {stock['code']} - 最大5日涨幅: {stock['max_5d_return']*100:.1f}%")

    print("\n科创板爆发股（15只）:")
    for stock in kcb_stocks:
        print(f"  {stock['code']} - 最大5日涨幅: {stock['max_5d_return']*100:.1f}%")

    print("\n主板爆发股（20只）:")
    for stock in zb_stocks:
        print(f"  {stock['code']} - 最大5日涨幅: {stock['max_5d_return']*100:.1f}%")

    return recommended_stocks


def main():
    """主函数"""
    print("🚀 开始搜索A股市场短期爆发能力强的股票")
    print("=" * 80)

    # 获取爆发股
    explosive_stocks = get_recent_explosive_stocks()

    if not explosive_stocks:
        print("❌ 未找到爆发力强的股票，可能原因:")
        print("  1. 网络连接问题")
        print("  2. 数据源限制")
        print("  3. 最近市场较为平稳")
        return

    # 分析爆发股
    recommended_stocks = analyze_explosive_stocks(explosive_stocks)

    print(f"\n✅ 分析完成，推荐 {len(recommended_stocks)} 只爆发力强的股票")
    print("💡 建议将这些股票加入训练样本，提升模型对爆发股的识别能力")


if __name__ == "__main__":
    main()
