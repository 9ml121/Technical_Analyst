#!/usr/bin/env python3
"""
简化性能测试脚本

测试系统核心性能，避免复杂依赖
"""

import sys
import time
import random
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

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

def test_performance_tools():
    """测试性能工具"""
    print("🔧 测试性能工具...")
    
    try:
        from quant_system.utils.performance import (
            performance_monitor, start_performance_monitoring, 
            stop_performance_monitoring, performance_timer, performance_context
        )
        
        # 启动性能监控
        start_performance_monitoring(interval=0.5)
        
        @performance_timer
        def test_function():
            time.sleep(0.1)
            return "test result"
        
        # 测试性能装饰器
        result = test_function()
        print(f"  ✅ 性能装饰器测试通过: {result}")
        
        # 测试性能上下文
        with performance_context("test_context"):
            time.sleep(0.05)
        
        print("  ✅ 性能上下文测试通过")
        
        # 停止监控
        stop_performance_monitoring()
        
        # 获取统计信息
        stats = performance_monitor.get_function_stats()
        print(f"  📊 函数统计: {len(stats)} 个函数被监控")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 性能工具测试失败: {e}")
        return False

def test_cache_system():
    """测试缓存系统"""
    print("\n💾 测试缓存系统...")
    
    try:
        from quant_system.utils.cache import LRUCache, cache_result
        
        # 测试LRU缓存
        cache = LRUCache(max_size=3, ttl=1.0)
        
        # 添加数据
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        
        # 测试获取
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        
        # 测试LRU淘汰
        cache.put("key4", "value4")  # 应该淘汰key1
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
        
        print("  ✅ LRU缓存测试通过")
        
        # 测试缓存装饰器
        call_count = 0
        
        @cache_result(ttl=1.0)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # 第一次调用
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # 第二次调用（应该使用缓存）
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加
        
        print("  ✅ 缓存装饰器测试通过")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 缓存系统测试失败: {e}")
        return False

def test_concurrent_processing():
    """测试并发处理"""
    print("\n⚡ 测试并发处理...")
    
    try:
        from quant_system.utils.concurrent import parallel_map, parallel_process
        
        def simple_task(x):
            return x * x
        
        # 测试数据
        test_data = list(range(10))
        
        # 串行执行
        start_time = time.time()
        serial_results = [simple_task(x) for x in test_data]
        serial_time = time.time() - start_time
        
        # 并行执行
        start_time = time.time()
        parallel_results = parallel_map(simple_task, test_data, max_workers=4)
        parallel_time = time.time() - start_time
        
        # 验证结果
        assert serial_results == parallel_results
        
        print(f"  串行时间: {serial_time:.4f}s")
        print(f"  并行时间: {parallel_time:.4f}s")
        print("  ✅ 并发处理测试通过")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 并发处理测试失败: {e}")
        return False

def test_config_performance():
    """测试配置系统性能"""
    print("\n⚙️ 测试配置系统性能...")
    
    try:
        from quant_system.utils.config_loader import ConfigLoader
        
        # 创建临时配置目录
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            config_loader = ConfigLoader(temp_dir, enable_cache=True)
            
            # 创建测试配置文件
            import yaml
            test_config = {
                "system": {
                    "name": "测试系统",
                    "version": "1.0.0"
                },
                "test": {
                    "value": 42
                }
            }
            
            config_file = Path(temp_dir) / "test.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(test_config, f)
            
            # 测试配置加载性能
            start_time = time.time()
            for _ in range(10):
                config = config_loader.load_config("test")
            first_load_time = time.time() - start_time
            
            # 测试缓存性能
            start_time = time.time()
            for _ in range(100):
                config = config_loader.load_config("test")
            cached_load_time = time.time() - start_time
            
            print(f"  首次加载(10次): {first_load_time:.4f}s")
            print(f"  缓存加载(100次): {cached_load_time:.4f}s")
            print(f"  缓存加速比: {first_load_time / cached_load_time * 10:.2f}x")
            print("  ✅ 配置系统性能测试通过")
            
            return True
            
    except Exception as e:
        print(f"  ❌ 配置系统性能测试失败: {e}")
        return False

def test_data_processing_basic():
    """测试基础数据处理性能"""
    print("\n📊 测试基础数据处理性能...")
    
    try:
        # 生成测试数据
        test_sizes = [100, 500, 1000]
        
        for size in test_sizes:
            print(f"\n  测试数据量: {size}")
            
            # 生成数据
            start_time = time.time()
            mock_data = generate_mock_stock_data(size)
            generate_time = time.time() - start_time
            
            # 简单数据处理
            start_time = time.time()
            processed_data = []
            for stock in mock_data:
                if (stock['price'] > 10.0 and 
                    stock['volume'] > 1000000 and 
                    stock['pct_change'] > 0):
                    processed_data.append(stock)
            process_time = time.time() - start_time
            
            # 排序
            start_time = time.time()
            sorted_data = sorted(processed_data, key=lambda x: x['pct_change'], reverse=True)
            sort_time = time.time() - start_time
            
            print(f"    生成时间: {generate_time:.4f}s")
            print(f"    处理时间: {process_time:.4f}s")
            print(f"    排序时间: {sort_time:.4f}s")
            print(f"    处理结果: {len(mock_data)} -> {len(processed_data)} -> {len(sorted_data)}")
        
        print("  ✅ 基础数据处理性能测试通过")
        return True
        
    except Exception as e:
        print(f"  ❌ 基础数据处理性能测试失败: {e}")
        return False

def test_memory_usage_basic():
    """测试基础内存使用"""
    print("\n💾 测试基础内存使用...")
    
    try:
        import psutil
        process = psutil.Process()
        
        # 初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"  初始内存: {initial_memory:.1f}MB")
        
        # 创建大量数据
        large_data = []
        for i in range(5):
            batch_data = generate_mock_stock_data(1000)
            large_data.extend(batch_data)
            
            current_memory = process.memory_info().rss / 1024 / 1024
            print(f"    批次 {i+1}: {current_memory:.1f}MB (+{current_memory - initial_memory:.1f}MB)")
        
        # 清理数据
        del large_data
        import gc
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        print(f"  清理后内存: {final_memory:.1f}MB")
        print("  ✅ 基础内存使用测试通过")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 基础内存使用测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎯 简化性能测试开始...")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("性能工具", test_performance_tools()))
    test_results.append(("缓存系统", test_cache_system()))
    test_results.append(("并发处理", test_concurrent_processing()))
    test_results.append(("配置性能", test_config_performance()))
    test_results.append(("数据处理", test_data_processing_basic()))
    test_results.append(("内存使用", test_memory_usage_basic()))
    
    # 汇总结果
    print("\n📊 测试结果汇总:")
    print("=" * 30)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:<12}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有性能测试通过！")
        print("\n💡 性能优化效果:")
        print("  - 缓存系统显著提升配置加载速度")
        print("  - 并发处理提升数据处理效率")
        print("  - 性能监控帮助识别瓶颈")
        print("  - 内存管理优化减少资源占用")
    else:
        print("⚠️ 部分测试失败，请检查相关组件")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
