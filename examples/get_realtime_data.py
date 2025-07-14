#!/usr/bin/env python3
"""
获取实时行情数据示例

演示如何使用量化投资系统获取A股实时行情数据
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from market_data import get_eastmoney_api
from market_data.processors import MarketDataProcessor
from quant_system.utils.logger import get_logger

# 初始化日志
logger = get_logger(__name__)

def main():
    """主函数"""
    print("🚀 量化投资系统 - 实时行情数据获取示例")
    print("=" * 50)
    
    try:
        # 1. 初始化API和处理器
        print("\n📡 初始化数据源...")
        api = get_eastmoney_api()
        processor = MarketDataProcessor()
        
        # 2. 获取A股实时数据
        print("\n📊 获取A股实时数据...")
        stocks = api.get_a_stock_realtime(limit=10)
        
        if not stocks:
            print("❌ 无法获取实时数据，请检查网络连接")
            return
        
        print(f"✅ 成功获取 {len(stocks)} 只股票的实时数据")
        
        # 3. 显示原始数据
        print("\n📋 原始数据示例:")
        for i, stock in enumerate(stocks[:3]):
            print(f"  {i+1}. {stock.get('name', 'N/A')} ({stock.get('code', 'N/A')})")
            print(f"     价格: {stock.get('price', 0):.2f}")
            print(f"     涨跌幅: {stock.get('pct_change', 0):.2%}")
            print(f"     成交量: {stock.get('volume', 0):,}")
        
        # 4. 数据处理
        print("\n🔧 数据处理...")
        cleaned_stocks = processor.clean_stock_data(stocks)
        print(f"✅ 数据清洗完成，保留 {len(cleaned_stocks)} 只有效股票")
        
        # 5. 数据筛选
        print("\n🎯 数据筛选...")
        filters = {
            'min_price': 5.0,           # 最低价格5元
            'min_volume': 10000000,     # 最小成交量1000万
            'min_pct_change': 0.0       # 只看上涨的股票
        }
        
        filtered_stocks = processor.filter_stocks(cleaned_stocks, filters)
        print(f"✅ 筛选完成，符合条件的股票: {len(filtered_stocks)} 只")
        
        # 6. 数据排序
        print("\n📈 按涨跌幅排序...")
        sorted_stocks = processor.sort_stocks(
            filtered_stocks, 
            sort_by='pct_change', 
            ascending=False
        )
        
        # 7. 显示处理后的数据
        print("\n🏆 今日涨幅榜 (前5名):")
        print("-" * 60)
        print(f"{'排名':<4} {'股票代码':<8} {'股票名称':<12} {'当前价格':<8} {'涨跌幅':<8} {'成交量(万)':<10}")
        print("-" * 60)
        
        for i, stock in enumerate(sorted_stocks[:5]):
            rank = i + 1
            code = stock.get('code', 'N/A')
            name = stock.get('name', 'N/A')[:10]  # 限制名称长度
            price = stock.get('price', 0)
            pct_change = stock.get('pct_change', 0)
            volume = stock.get('volume', 0) / 10000  # 转换为万
            
            print(f"{rank:<4} {code:<8} {name:<12} {price:<8.2f} {pct_change:<8.2%} {volume:<10.0f}")
        
        # 8. 市场统计
        print("\n📊 市场统计:")
        market_stats = processor.aggregate_market_data(cleaned_stocks)
        
        print(f"  总股票数: {market_stats.get('total_stocks', 0)}")
        print(f"  上涨股票: {market_stats.get('rising_stocks', 0)}")
        print(f"  下跌股票: {market_stats.get('falling_stocks', 0)}")
        print(f"  平盘股票: {market_stats.get('flat_stocks', 0)}")
        print(f"  上涨比例: {market_stats.get('rising_ratio', 0):.2%}")
        print(f"  平均涨跌幅: {market_stats.get('avg_pct_change', 0):.2%}")
        
        # 9. 获取特定股票详情
        print("\n🔍 获取特定股票详情...")
        test_codes = ['000001', '600000', '000002']  # 平安银行、浦发银行、万科A
        
        for code in test_codes:
            detail = api.get_stock_detail(code)
            if detail:
                print(f"  {detail.get('name', 'N/A')} ({code}):")
                print(f"    当前价格: {detail.get('price', 0):.2f}")
                print(f"    开盘价格: {detail.get('open', 0):.2f}")
                print(f"    最高价格: {detail.get('high', 0):.2f}")
                print(f"    最低价格: {detail.get('low', 0):.2f}")
                print(f"    涨跌幅度: {detail.get('pct_change', 0):.2%}")
                print(f"    成交金额: {detail.get('amount', 0):,.0f}")
                print(f"    更新时间: {detail.get('update_time', 'N/A')}")
            else:
                print(f"  ❌ 无法获取股票 {code} 的详情")
        
        # 10. 市场状态检查
        print("\n🏪 市场状态检查...")
        market_status = api.get_market_status()
        
        if market_status:
            print(f"  市场: {market_status.get('market', 'N/A')}")
            print(f"  状态: {market_status.get('status', 'N/A')}")
            print(f"  数据可用: {'是' if market_status.get('data_available') else '否'}")
            print(f"  更新时间: {market_status.get('update_time', 'N/A')}")
        
        print("\n✅ 实时数据获取示例完成！")
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
        print(f"\n❌ 程序执行出错: {e}")
        print("请检查网络连接和配置设置")

def demo_data_processing():
    """演示数据处理功能"""
    print("\n" + "="*50)
    print("🔧 数据处理功能演示")
    print("="*50)
    
    # 模拟数据
    mock_data = [
        {
            'code': '000001',
            'name': '平安银行',
            'price': 12.50,
            'pct_change': 0.024,
            'volume': 15000000,
            'amount': 187500000
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'price': 8.90,
            'pct_change': -0.011,
            'volume': 12000000,
            'amount': 106800000
        },
        {
            'code': '000002',
            'name': '万科A',
            'price': 18.80,
            'pct_change': 0.032,
            'volume': 25000000,
            'amount': 470000000
        }
    ]
    
    processor = MarketDataProcessor()
    
    # 数据清洗
    print("\n1. 数据清洗:")
    cleaned_data = processor.clean_stock_data(mock_data)
    print(f"   原始数据: {len(mock_data)} 条")
    print(f"   清洗后: {len(cleaned_data)} 条")
    
    # 数据筛选
    print("\n2. 数据筛选 (价格>10元, 涨幅>0):")
    filtered_data = processor.filter_stocks(cleaned_data, {
        'min_price': 10.0,
        'min_pct_change': 0.0
    })
    
    for stock in filtered_data:
        print(f"   {stock['name']}: {stock['price']:.2f} (+{stock['pct_change']:.2%})")
    
    # 数据排序
    print("\n3. 按涨跌幅排序:")
    sorted_data = processor.sort_stocks(cleaned_data, 'pct_change', ascending=False)
    
    for i, stock in enumerate(sorted_data):
        print(f"   {i+1}. {stock['name']}: {stock['pct_change']:+.2%}")
    
    # 市场统计
    print("\n4. 市场统计:")
    stats = processor.aggregate_market_data(cleaned_data)
    
    for key, value in stats.items():
        if isinstance(value, float):
            if 'ratio' in key or 'pct' in key:
                print(f"   {key}: {value:.2%}")
            else:
                print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")

def demo_error_handling():
    """演示错误处理"""
    print("\n" + "="*50)
    print("⚠️ 错误处理演示")
    print("="*50)
    
    api = get_eastmoney_api()
    
    # 测试无效股票代码
    print("\n1. 测试无效股票代码:")
    invalid_detail = api.get_stock_detail("INVALID")
    if invalid_detail is None:
        print("   ✅ 正确处理了无效股票代码")
    
    # 测试空数据处理
    print("\n2. 测试空数据处理:")
    processor = MarketDataProcessor()
    empty_result = processor.clean_stock_data([])
    print(f"   ✅ 空数据处理结果: {len(empty_result)} 条记录")
    
    # 测试异常数据处理
    print("\n3. 测试异常数据处理:")
    bad_data = [
        {'code': '', 'name': '', 'price': -1},  # 无效数据
        {'code': '000001', 'name': '平安银行', 'price': 12.50}  # 有效数据
    ]
    
    cleaned_result = processor.clean_stock_data(bad_data)
    print(f"   原始数据: {len(bad_data)} 条")
    print(f"   清洗后: {len(cleaned_result)} 条")
    print("   ✅ 正确过滤了异常数据")

if __name__ == "__main__":
    # 运行主要示例
    main()
    
    # 运行数据处理演示
    demo_data_processing()
    
    # 运行错误处理演示
    demo_error_handling()
    
    print("\n🎉 所有示例运行完成！")
    print("\n💡 提示:")
    print("  - 实时数据需要网络连接")
    print("  - 数据可能有1-5分钟延迟")
    print("  - 请在交易时间内运行以获得最新数据")
    print("  - 可以修改筛选条件来获得不同的结果")
