#!/usr/bin/env python3
"""
性能测试脚本

测试系统各个组件的性能表现
"""

import sys
import time
import random
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from quant_system.utils.performance import (
    performance_monitor, start_performance_monitoring, stop_performance_monitoring,
    print_performance_report, performance_timer, performance_context
)
from quant_system.utils.cache import cache_manager, cache_result
from quant_system.utils.concurrent import parallel_map, parallel_process
from market_data.processors.data_processor import MarketDataProcessor

def generate_mock_stock_data(count: int = 1000):
    """生成模拟股票数据"""
    stocks = []
    
    for i in range(count):
        stock = {
            'code': f"{random.randint(0, 999):03d}{random.randint(0, 999):03d}",
            'name': f"股票{i+1}",
            'price': round(random.uniform(5, 100), 2),
            'open': round(random.uniform(5, 100), 2),
            'high': round(random.uniform(5, 100), 2),
            'low': round(random.uniform(5, 100), 2),
            'close': round(random.uniform(5, 100), 2),
            'volume': random.randint(100000, 10000000),
            'amount': random.randint(1000000, 100000000),
            'pct_change': round(random.uniform(-0.1, 0.1), 4),
            'change': round(random.uniform(-5, 5), 2),
            'turnover_rate': round(random.uniform(0.01, 0.2), 4),
            'market_cap': random.randint(1000000000, 100000000000)
        }
        stocks.append(stock)
    
    return stocks

@performance_timer
def test_data_processing_performance():
    """测试数据处理性能"""
    print("\n🔧 测试数据处理性能...")
    
    # 生成测试数据
    test_sizes = [100, 500, 1000, 5000]
    processor = MarketDataProcessor(enable_parallel=True)
    
    results = {}
    
    for size in test_sizes:
        print(f"\n  测试数据量: {size}")
        
        # 生成数据
        with performance_context(f"generate_data_{size}"):
            mock_data = generate_mock_stock_data(size)
        
        # 测试数据清洗
        with performance_context(f"clean_data_{size}"):
            cleaned_data = processor.clean_stock_data(mock_data)
        
        # 测试数据筛选
        filters = {
            'min_price': 10.0,
            'min_volume': 1000000,
            'min_pct_change': 0.0
        }
        
        with performance_context(f"filter_data_{size}"):
            filtered_data = processor.filter_stocks(cleaned_data, filters)
        
        # 测试数据排序
        with performance_context(f"sort_data_{size}"):
            sorted_data = processor.sort_stocks(filtered_data, 'pct_change')
        
        results[size] = {
            'original': len(mock_data),
            'cleaned': len(cleaned_data),
            'filtered': len(filtered_data),
            'sorted': len(sorted_data)
        }
        
        print(f"    原始数据: {results[size]['original']}")
        print(f"    清洗后: {results[size]['cleaned']}")
        print(f"    筛选后: {results[size]['filtered']}")
        print(f"    排序后: {results[size]['sorted']}")
    
    return results

@performance_timer
def test_parallel_processing_performance():
    """测试并行处理性能"""
    print("\n⚡ 测试并行处理性能...")
    
    def cpu_intensive_task(n):
        """CPU密集型任务"""
        result = 0
        for i in range(n * 1000):
            result += i ** 2
        return result
    
    def io_intensive_task(delay):
        """IO密集型任务"""
        time.sleep(delay)
        return f"Task completed after {delay}s"
    
    # 测试CPU密集型任务
    print("\n  CPU密集型任务测试:")
    cpu_tasks = [100, 200, 300, 400, 500]
    
    # 串行执行
    start_time = time.time()
    serial_results = [cpu_intensive_task(n) for n in cpu_tasks]
    serial_time = time.time() - start_time
    print(f"    串行执行时间: {serial_time:.2f}s")
    
    # 并行执行（线程）
    start_time = time.time()
    parallel_results_thread = parallel_map(cpu_intensive_task, cpu_tasks, use_processes=False)
    parallel_time_thread = time.time() - start_time
    print(f"    并行执行时间（线程）: {parallel_time_thread:.2f}s")
    
    # 并行执行（进程）
    start_time = time.time()
    parallel_results_process = parallel_map(cpu_intensive_task, cpu_tasks, use_processes=True)
    parallel_time_process = time.time() - start_time
    print(f"    并行执行时间（进程）: {parallel_time_process:.2f}s")
    
    print(f"    线程加速比: {serial_time / parallel_time_thread:.2f}x")
    print(f"    进程加速比: {serial_time / parallel_time_process:.2f}x")
    
    # 测试IO密集型任务
    print("\n  IO密集型任务测试:")
    io_tasks = [0.1, 0.1, 0.1, 0.1, 0.1]  # 5个0.1秒的任务
    
    # 串行执行
    start_time = time.time()
    serial_io_results = [io_intensive_task(delay) for delay in io_tasks]
    serial_io_time = time.time() - start_time
    print(f"    串行执行时间: {serial_io_time:.2f}s")
    
    # 并行执行
    start_time = time.time()
    parallel_io_results = parallel_map(io_intensive_task, io_tasks, use_processes=False)
    parallel_io_time = time.time() - start_time
    print(f"    并行执行时间: {parallel_io_time:.2f}s")
    print(f"    IO加速比: {serial_io_time / parallel_io_time:.2f}x")

@cache_result(ttl=60)
def expensive_calculation(n):
    """模拟耗时计算"""
    time.sleep(0.1)  # 模拟计算时间
    return sum(i ** 2 for i in range(n))

@performance_timer
def test_cache_performance():
    """测试缓存性能"""
    print("\n💾 测试缓存性能...")
    
    test_values = [100, 200, 300, 100, 200, 400, 100]  # 包含重复值
    
    # 第一次执行（无缓存）
    print("\n  第一次执行（无缓存）:")
    start_time = time.time()
    results1 = []
    for value in test_values:
        result = expensive_calculation(value)
        results1.append(result)
    first_time = time.time() - start_time
    print(f"    执行时间: {first_time:.2f}s")
    
    # 第二次执行（有缓存）
    print("\n  第二次执行（有缓存）:")
    start_time = time.time()
    results2 = []
    for value in test_values:
        result = expensive_calculation(value)
        results2.append(result)
    second_time = time.time() - start_time
    print(f"    执行时间: {second_time:.2f}s")
    
    print(f"    缓存加速比: {first_time / second_time:.2f}x")
    
    # 验证结果一致性
    assert results1 == results2, "缓存结果不一致"
    print("    ✅ 缓存结果验证通过")
    
    # 显示缓存统计
    print("\n  缓存统计:")
    cache_manager.print_stats()

@performance_timer
def test_memory_usage():
    """测试内存使用"""
    print("\n💾 测试内存使用...")
    
    import psutil
    process = psutil.Process()
    
    # 初始内存
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"  初始内存使用: {initial_memory:.1f}MB")
    
    # 创建大量数据
    large_data = []
    for i in range(10):
        batch_data = generate_mock_stock_data(1000)
        large_data.extend(batch_data)
        
        current_memory = process.memory_info().rss / 1024 / 1024
        print(f"    批次 {i+1}: {current_memory:.1f}MB (+{current_memory - initial_memory:.1f}MB)")
    
    # 处理数据
    processor = MarketDataProcessor()
    
    print("\n  处理大量数据...")
    processed_memory_start = process.memory_info().rss / 1024 / 1024
    
    cleaned_data = processor.clean_stock_data(large_data)
    
    processed_memory_end = process.memory_info().rss / 1024 / 1024
    print(f"    处理后内存: {processed_memory_end:.1f}MB")
    print(f"    处理增量: {processed_memory_end - processed_memory_start:.1f}MB")
    
    # 清理数据
    del large_data
    del cleaned_data
    
    import gc
    gc.collect()
    
    final_memory = process.memory_info().rss / 1024 / 1024
    print(f"    清理后内存: {final_memory:.1f}MB")

def test_system_performance():
    """系统性能综合测试"""
    print("🚀 量化投资系统性能测试")
    print("=" * 60)
    
    # 启动性能监控
    start_performance_monitoring(interval=0.5)
    
    try:
        # 运行各项性能测试
        test_data_processing_performance()
        test_parallel_processing_performance()
        test_cache_performance()
        test_memory_usage()
        
        # 显示性能报告
        print("\n📊 性能监控报告:")
        print_performance_report()
        
    finally:
        # 停止性能监控
        stop_performance_monitoring()

def benchmark_comparison():
    """基准测试对比"""
    print("\n📈 基准测试对比")
    print("=" * 40)
    
    # 数据处理基准测试
    data_sizes = [100, 500, 1000, 2000]
    
    print("\n数据处理性能对比:")
    print(f"{'数据量':<8} {'串行(ms)':<10} {'并行(ms)':<10} {'加速比':<8}")
    print("-" * 40)
    
    for size in data_sizes:
        mock_data = generate_mock_stock_data(size)
        
        # 串行处理
        processor_serial = MarketDataProcessor(enable_parallel=False)
        start_time = time.time()
        processor_serial.clean_stock_data(mock_data)
        serial_time = (time.time() - start_time) * 1000
        
        # 并行处理
        processor_parallel = MarketDataProcessor(enable_parallel=True)
        start_time = time.time()
        processor_parallel.clean_stock_data(mock_data)
        parallel_time = (time.time() - start_time) * 1000
        
        speedup = serial_time / parallel_time if parallel_time > 0 else 1.0
        
        print(f"{size:<8} {serial_time:<10.1f} {parallel_time:<10.1f} {speedup:<8.2f}x")

def stress_test():
    """压力测试"""
    print("\n🔥 压力测试")
    print("=" * 30)
    
    # 大数据量测试
    large_sizes = [5000, 10000, 20000]
    
    for size in large_sizes:
        print(f"\n测试数据量: {size}")
        
        try:
            with performance_context(f"stress_test_{size}"):
                # 生成大量数据
                mock_data = generate_mock_stock_data(size)
                
                # 数据处理
                processor = MarketDataProcessor(enable_parallel=True)
                cleaned_data = processor.clean_stock_data(mock_data)
                
                # 复杂筛选
                filters = {
                    'min_price': 10.0,
                    'max_price': 80.0,
                    'min_volume': 1000000,
                    'min_pct_change': -0.05,
                    'max_pct_change': 0.05
                }
                filtered_data = processor.filter_stocks(cleaned_data, filters)
                
                # 排序
                sorted_data = processor.sort_stocks(filtered_data, 'market_cap')
                
                print(f"  ✅ 成功处理 {len(sorted_data)} 只股票")
                
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")

def main():
    """主函数"""
    print("🎯 开始性能测试...")
    
    # 系统性能测试
    test_system_performance()
    
    # 基准测试对比
    benchmark_comparison()
    
    # 压力测试
    stress_test()
    
    print("\n🎉 性能测试完成！")
    print("\n💡 优化建议:")
    print("  1. 对于大数据集，启用并行处理可显著提升性能")
    print("  2. 合理使用缓存可以避免重复计算")
    print("  3. 监控内存使用，及时清理不需要的数据")
    print("  4. CPU密集型任务适合使用进程池")
    print("  5. IO密集型任务适合使用线程池")

if __name__ == "__main__":
    main()
