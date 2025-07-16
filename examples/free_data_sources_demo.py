from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
import sys
import os
from datetime import date, timedelta

# 动态导入src目录下的模块，优先查找src
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../src')))

if __name__ == "__main__":
    fetcher = FreeDataSourcesFetcher()

    # 示例：获取贵州茅台（600519.SH）近30天A股历史数据
    stock_code_a = "600519"
    end = date.today()
    start = end - timedelta(days=30)
    print(f"\n获取A股 {stock_code_a} 近30天历史数据：")
    data_a = fetcher.get_historical_data_with_fallback(
        stock_code_a, start, end, market_type="a_stock")
    if data_a:
        for row in data_a[:5]:  # 只打印前5条
            print(row)
        print(f"... 共{len(data_a)}条\n")
    else:
        print("未获取到A股数据\n")

    # 示例：获取腾讯控股（00700.HK）近30天港股历史数据
    stock_code_h = "00700"
    print(f"获取港股 {stock_code_h} 近30天历史数据：")
    data_h = fetcher.get_historical_data_with_fallback(
        stock_code_h, start, end, market_type="h_stock")
    if data_h:
        for row in data_h[:5]:
            print(row)
        print(f"... 共{len(data_h)}条\n")
    else:
        print("未获取到港股数据\n")

    # 打印性能报告
    print("数据源性能报告：")
    report = fetcher.get_performance_report()
    for k, v in report.items():
        print(f"{k}: {v}")
