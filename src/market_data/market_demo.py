"""
行情数据系统演示程序

展示如何使用行情数据系统获取和处理股票数据
"""

import sys
import os
import time
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# 导入行情数据系统模块
from market_data.fetchers.eastmoney_api import EastMoneyAPI
from market_data.processors.data_processor import MarketDataProcessor

def demo_eastmoney_api():
    """演示东方财富API使用"""
    print("=" * 60)
    print("东方财富API演示")
    print("=" * 60)
    
    # 创建API实例
    api = EastMoneyAPI()
    processor = MarketDataProcessor()
    
    # 1. 获取A股实时行情
    print("\n1. 获取A股实时行情 (前20只)")
    try:
        stocks = api.get_a_stock_realtime(limit=20)
        
        if stocks:
            # 数据清洗
            cleaned_stocks = processor.clean_stock_data(stocks)
            
            # 显示结果
            print(f"获取成功，共{len(cleaned_stocks)}只股票:")
            print(f"{'代码':<8} {'名称':<12} {'价格':<8} {'涨跌幅':<8} {'成交量':<12}")
            print("-" * 60)
            
            for stock in cleaned_stocks[:10]:  # 只显示前10只
                print(f"{stock['code']:<8} {stock['name']:<12} {stock['price']:<8.2f} "
                      f"{stock['pct_change']:<8.2%} {stock['volume']:<12}")
        else:
            print("获取数据失败")
    
    except Exception as e:
        print(f"获取A股实时行情失败: {e}")
    
    # 2. 获取单只股票详细信息
    print("\n2. 获取单只股票详细信息 (平安银行 000001)")
    try:
        stock_detail = api.get_stock_detail("000001")
        
        if stock_detail:
            print("股票详细信息:")
            for key, value in stock_detail.items():
                if key not in ['update_time']:
                    print(f"  {key}: {value}")
        else:
            print("获取股票详细信息失败")
    
    except Exception as e:
        print(f"获取股票详细信息失败: {e}")
    
    # 3. 获取历史数据
    print("\n3. 获取历史数据 (平安银行 最近10天)")
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=15)  # 多取几天，排除周末
        
        historical_data = api.get_historical_data("000001", start_date, end_date)
        
        if historical_data:
            # 计算技术指标
            processed_data = processor.calculate_technical_indicators(historical_data)
            
            print(f"获取历史数据成功，共{len(processed_data)}条:")
            print(f"{'日期':<12} {'开盘':<8} {'收盘':<8} {'最高':<8} {'最低':<8} {'MA5':<8}")
            print("-" * 60)
            
            for data in processed_data[-10:]:  # 显示最近10天
                print(f"{data['date']:<12} {data['open']:<8.2f} {data['close']:<8.2f} "
                      f"{data['high']:<8.2f} {data['low']:<8.2f} {data.get('ma5', 0):<8.2f}")
        else:
            print("获取历史数据失败")
    
    except Exception as e:
        print(f"获取历史数据失败: {e}")
    
    # 4. 市场状态
    print("\n4. 获取市场状态")
    try:
        market_status = api.get_market_status()
        print("市场状态:")
        for key, value in market_status.items():
            print(f"  {key}: {value}")
    
    except Exception as e:
        print(f"获取市场状态失败: {e}")

def demo_data_processor():
    """演示数据处理器使用"""
    print("\n" + "=" * 60)
    print("数据处理器演示")
    print("=" * 60)
    
    # 创建处理器
    processor = MarketDataProcessor()
    
    # 模拟数据
    sample_data = [
        {
            'code': '000001',
            'name': '平安银行',
            'price': 12.50,
            'pct_change': 0.02,
            'volume': 1000000,
            'market_cap': 50000000000
        },
        {
            'code': '000002',
            'name': '万科A',
            'price': 18.80,
            'pct_change': -0.015,
            'volume': 800000,
            'market_cap': 80000000000
        },
        {
            'code': '600000',
            'name': '浦发银行',
            'price': 8.90,
            'pct_change': 0.01,
            'volume': 1200000,
            'market_cap': 30000000000
        }
    ]
    
    print("\n1. 原始数据:")
    for stock in sample_data:
        print(f"  {stock['code']} {stock['name']} {stock['price']} {stock['pct_change']:.2%}")
    
    # 数据筛选
    print("\n2. 筛选涨幅大于1%的股票:")
    filters = {'min_pct_change': 0.01}
    filtered_data = processor.filter_stocks(sample_data, filters)
    
    for stock in filtered_data:
        print(f"  {stock['code']} {stock['name']} {stock['pct_change']:.2%}")
    
    # 数据排序
    print("\n3. 按涨跌幅降序排列:")
    sorted_data = processor.sort_stocks(sample_data, sort_by='pct_change', ascending=False)
    
    for stock in sorted_data:
        print(f"  {stock['code']} {stock['name']} {stock['pct_change']:.2%}")
    
    # 市场统计
    print("\n4. 市场统计:")
    market_stats = processor.aggregate_market_data(sample_data)
    
    for key, value in market_stats.items():
        if key != 'update_time':
            print(f"  {key}: {value}")

def demo_tushare_api():
    """演示Tushare API使用"""
    print("\n" + "=" * 60)
    print("Tushare API演示")
    print("=" * 60)
    
    try:
        from market_data.fetchers.tushare_api import TushareAPI
        
        # 创建API实例
        api = TushareAPI()
        
        if not api.is_available():
            print("Tushare API不可用 (可能未安装tushare或未设置token)")
            print("请安装: pip install tushare")
            print("并设置环境变量: export TUSHARE_TOKEN=your_token")
            return
        
        # 获取股票基本信息
        print("\n1. 获取股票基本信息 (前5只)")
        basic_info = api.get_stock_basic()
        
        if basic_info:
            print(f"获取成功，共{len(basic_info)}只股票:")
            print(f"{'代码':<12} {'名称':<12} {'行业':<15} {'市场':<8}")
            print("-" * 60)
            
            for stock in basic_info[:5]:
                print(f"{stock['ts_code']:<12} {stock['name']:<12} "
                      f"{stock['industry']:<15} {stock['market']:<8}")
        else:
            print("获取股票基本信息失败")
    
    except ImportError:
        print("Tushare未安装，跳过演示")
    except Exception as e:
        print(f"Tushare API演示失败: {e}")

def main():
    """主演示函数"""
    print("🚀 行情数据系统演示程序")
    print("=" * 60)
    print("本程序演示如何使用行情数据系统获取和处理股票数据")
    print("包含以下功能:")
    print("1. 东方财富API数据获取")
    print("2. 数据处理和分析")
    print("3. Tushare API数据获取 (可选)")
    
    # 演示东方财富API
    demo_eastmoney_api()
    
    # 演示数据处理器
    demo_data_processor()
    
    # 演示Tushare API
    demo_tushare_api()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n💡 使用建议:")
    print("1. 东方财富API无需token，可直接使用")
    print("2. Tushare API需要注册获取token")
    print("3. 数据处理器提供丰富的数据清洗和分析功能")
    print("4. 所有API都支持错误处理和日志记录")
    
    print("\n📚 更多功能:")
    print("- 实时行情监控")
    print("- 历史数据分析")
    print("- 技术指标计算")
    print("- 市场统计分析")

if __name__ == "__main__":
    main()
