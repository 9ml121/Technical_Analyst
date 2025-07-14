#!/usr/bin/env python3
"""
压力测试脚本

测试系统在高负载和极端条件下的表现
"""

import sys
import time
import random
import threading
import multiprocessing as mp
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from quant_system.utils.performance import (
    performance_monitor, start_performance_monitoring, 
    stop_performance_monitoring, performance_context
)
from quant_system.utils.cache import cache_manager, LRUCache
from quant_system.utils.concurrent import parallel_map, WorkerPool

class StressTestRunner:
    """压力测试运行器"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        
    def run_all_tests(self):
        """运行所有压力测试"""
        print("🔥 量化投资系统压力测试")
        print("=" * 50)
        
        # 启动性能监控
        start_performance_monitoring(interval=0.5)
        
        try:
            test_methods = [
                ("大数据量处理", self.test_large_dataset_processing),
                ("高并发访问", self.test_high_concurrency),
                ("内存压力", self.test_memory_stress),
                ("缓存压力", self.test_cache_stress),
                ("CPU密集型任务", self.test_cpu_intensive),
                ("I/O密集型任务", self.test_io_intensive),
                ("长时间运行", self.test_long_running),
                ("异常恢复", self.test_exception_recovery)
            ]
            
            for test_name, test_method in test_methods:
                print(f"\n🧪 {test_name}测试...")
                try:
                    result = test_method()
                    self.results[test_name] = result
                    print(f"  ✅ {test_name}测试通过")
                except Exception as e:
                    self.errors.append((test_name, str(e)))
                    print(f"  ❌ {test_name}测试失败: {e}")
            
            # 生成测试报告
            self.generate_report()
            
        finally:
            stop_performance_monitoring()
    
    def generate_mock_stock_data(self, count: int):
        """生成模拟股票数据"""
        stocks = []
        for i in range(count):
            stock = {
                'code': f"{random.randint(0, 999):03d}{random.randint(0, 999):03d}",
                'name': f"股票{i+1}",
                'price': round(random.uniform(5, 100), 2),
                'volume': random.randint(100000, 10000000),
                'pct_change': round(random.uniform(-0.1, 0.1), 4),
                'market_cap': random.randint(1000000000, 100000000000),
                'pe_ratio': round(random.uniform(5, 50), 2),
                'pb_ratio': round(random.uniform(0.5, 5), 2)
            }
            stocks.append(stock)
        return stocks
    
    def test_large_dataset_processing(self):
        """测试大数据量处理"""
        test_sizes = [10000, 50000, 100000]
        results = {}
        
        for size in test_sizes:
            print(f"    测试数据量: {size}")
            
            # 生成数据
            start_time = time.time()
            data = self.generate_mock_stock_data(size)
            generation_time = time.time() - start_time
            
            # 数据处理
            start_time = time.time()
            processed_data = []
            for stock in data:
                if (stock['price'] > 10 and 
                    stock['volume'] > 1000000 and 
                    stock['pct_change'] > 0):
                    processed_data.append(stock)
            processing_time = time.time() - start_time
            
            # 排序
            start_time = time.time()
            sorted_data = sorted(processed_data, key=lambda x: x['pct_change'], reverse=True)
            sorting_time = time.time() - start_time
            
            results[size] = {
                'generation_time': generation_time,
                'processing_time': processing_time,
                'sorting_time': sorting_time,
                'processed_count': len(processed_data),
                'total_time': generation_time + processing_time + sorting_time
            }
            
            print(f"      生成: {generation_time:.3f}s, 处理: {processing_time:.3f}s, 排序: {sorting_time:.3f}s")
            print(f"      结果: {len(data)} -> {len(processed_data)} -> {len(sorted_data)}")
        
        return results
    
    def test_high_concurrency(self):
        """测试高并发访问"""
        def worker_task(worker_id):
            """工作线程任务"""
            results = []
            errors = []
            
            try:
                # 模拟数据处理
                data = self.generate_mock_stock_data(100)
                
                # 模拟计算
                for stock in data:
                    score = stock['price'] * stock['volume'] / 1000000
                    results.append((stock['code'], score))
                
                # 排序
                results.sort(key=lambda x: x[1], reverse=True)
                
                return {
                    'worker_id': worker_id,
                    'processed_count': len(results),
                    'top_stock': results[0] if results else None,
                    'success': True
                }
                
            except Exception as e:
                errors.append(str(e))
                return {
                    'worker_id': worker_id,
                    'error': str(e),
                    'success': False
                }
        
        # 测试不同并发级别
        concurrency_levels = [10, 50, 100]
        results = {}
        
        for level in concurrency_levels:
            print(f"    并发级别: {level}")
            
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=level) as executor:
                futures = [executor.submit(worker_task, i) for i in range(level)]
                worker_results = [future.result() for future in futures]
            
            execution_time = time.time() - start_time
            
            successful_workers = [r for r in worker_results if r['success']]
            failed_workers = [r for r in worker_results if not r['success']]
            
            results[level] = {
                'execution_time': execution_time,
                'successful_workers': len(successful_workers),
                'failed_workers': len(failed_workers),
                'success_rate': len(successful_workers) / level,
                'throughput': level / execution_time
            }
            
            print(f"      执行时间: {execution_time:.3f}s")
            print(f"      成功率: {len(successful_workers)}/{level} ({results[level]['success_rate']:.2%})")
            print(f"      吞吐量: {results[level]['throughput']:.1f} 任务/秒")
        
        return results
    
    def test_memory_stress(self):
        """测试内存压力"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"    初始内存: {initial_memory:.1f}MB")
        
        # 逐步增加内存使用
        memory_data = []
        batch_sizes = [1000, 5000, 10000, 20000]
        
        results = {
            'initial_memory': initial_memory,
            'batches': []
        }
        
        for batch_size in batch_sizes:
            print(f"    创建批次: {batch_size} 个对象")
            
            # 创建大量对象
            batch_data = []
            for i in range(batch_size):
                obj = {
                    'id': i,
                    'data': f"test_data_{i}" * 100,  # 每个对象约1KB
                    'numbers': list(range(100)),
                    'timestamp': time.time()
                }
                batch_data.append(obj)
            
            memory_data.append(batch_data)
            
            # 检查内存使用
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = current_memory - initial_memory
            
            batch_result = {
                'batch_size': batch_size,
                'current_memory': current_memory,
                'memory_growth': memory_growth,
                'objects_count': sum(len(batch) for batch in memory_data)
            }
            
            results['batches'].append(batch_result)
            
            print(f"      当前内存: {current_memory:.1f}MB (+{memory_growth:.1f}MB)")
            print(f"      对象总数: {batch_result['objects_count']}")
        
        # 清理内存
        del memory_data
        import gc
        gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        results['final_memory'] = final_memory
        results['memory_released'] = results['batches'][-1]['current_memory'] - final_memory
        
        print(f"    清理后内存: {final_memory:.1f}MB")
        print(f"    释放内存: {results['memory_released']:.1f}MB")
        
        return results
    
    def test_cache_stress(self):
        """测试缓存压力"""
        cache_sizes = [100, 1000, 10000]
        results = {}
        
        for cache_size in cache_sizes:
            print(f"    缓存大小: {cache_size}")
            
            cache = LRUCache(max_size=cache_size, ttl=60)
            
            # 写入测试
            start_time = time.time()
            for i in range(cache_size * 2):  # 写入2倍容量的数据
                key = f"key_{i}"
                value = f"value_{i}" * 100  # 每个值约600字节
                cache.put(key, value)
            write_time = time.time() - start_time
            
            # 读取测试
            start_time = time.time()
            hit_count = 0
            miss_count = 0
            
            for i in range(cache_size * 2):
                key = f"key_{i}"
                value = cache.get(key)
                if value is not None:
                    hit_count += 1
                else:
                    miss_count += 1
            
            read_time = time.time() - start_time
            
            cache_stats = cache.stats()
            
            results[cache_size] = {
                'write_time': write_time,
                'read_time': read_time,
                'hit_count': hit_count,
                'miss_count': miss_count,
                'hit_rate': hit_count / (hit_count + miss_count),
                'cache_stats': cache_stats
            }
            
            print(f"      写入时间: {write_time:.3f}s")
            print(f"      读取时间: {read_time:.3f}s")
            print(f"      命中率: {results[cache_size]['hit_rate']:.2%}")
        
        return results
    
    def test_cpu_intensive(self):
        """测试CPU密集型任务"""
        def cpu_task(n):
            """CPU密集型任务"""
            result = 0
            for i in range(n * 10000):
                result += i ** 2
            return result
        
        task_sizes = [100, 500, 1000]
        results = {}
        
        for size in task_sizes:
            print(f"    任务规模: {size}")
            
            tasks = [size] * 10  # 10个相同规模的任务
            
            # 串行执行
            start_time = time.time()
            serial_results = [cpu_task(task) for task in tasks]
            serial_time = time.time() - start_time
            
            # 并行执行（线程）
            start_time = time.time()
            thread_results = parallel_map(cpu_task, tasks, use_processes=False, max_workers=4)
            thread_time = time.time() - start_time
            
            # 并行执行（进程）
            start_time = time.time()
            process_results = parallel_map(cpu_task, tasks, use_processes=True, max_workers=4)
            process_time = time.time() - start_time
            
            # 验证结果一致性
            assert serial_results == thread_results == process_results
            
            results[size] = {
                'serial_time': serial_time,
                'thread_time': thread_time,
                'process_time': process_time,
                'thread_speedup': serial_time / thread_time,
                'process_speedup': serial_time / process_time
            }
            
            print(f"      串行: {serial_time:.3f}s")
            print(f"      线程: {thread_time:.3f}s (加速 {results[size]['thread_speedup']:.2f}x)")
            print(f"      进程: {process_time:.3f}s (加速 {results[size]['process_speedup']:.2f}x)")
        
        return results
    
    def test_io_intensive(self):
        """测试I/O密集型任务"""
        def io_task(delay):
            """I/O密集型任务（模拟）"""
            time.sleep(delay)
            return f"Task completed after {delay}s"
        
        delays = [0.1] * 20  # 20个0.1秒的任务
        
        # 串行执行
        start_time = time.time()
        serial_results = [io_task(delay) for delay in delays]
        serial_time = time.time() - start_time
        
        # 并行执行
        start_time = time.time()
        parallel_results = parallel_map(io_task, delays, use_processes=False, max_workers=10)
        parallel_time = time.time() - start_time
        
        results = {
            'task_count': len(delays),
            'serial_time': serial_time,
            'parallel_time': parallel_time,
            'speedup': serial_time / parallel_time,
            'efficiency': (serial_time / parallel_time) / 10  # 10个工作线程
        }
        
        print(f"    任务数量: {results['task_count']}")
        print(f"    串行时间: {serial_time:.3f}s")
        print(f"    并行时间: {parallel_time:.3f}s")
        print(f"    加速比: {results['speedup']:.2f}x")
        print(f"    效率: {results['efficiency']:.2%}")
        
        return results
    
    def test_long_running(self):
        """测试长时间运行"""
        print("    运行30秒长时间测试...")
        
        start_time = time.time()
        end_time = start_time + 30  # 运行30秒
        
        iteration_count = 0
        memory_samples = []
        
        process = psutil.Process()
        
        while time.time() < end_time:
            # 模拟工作负载
            data = self.generate_mock_stock_data(100)
            processed = [s for s in data if s['price'] > 20]
            sorted_data = sorted(processed, key=lambda x: x['pct_change'])
            
            iteration_count += 1
            
            # 每5秒采样一次内存
            if iteration_count % 100 == 0:
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
                elapsed = time.time() - start_time
                print(f"      {elapsed:.1f}s: 迭代 {iteration_count}, 内存 {memory_mb:.1f}MB")
        
        total_time = time.time() - start_time
        
        results = {
            'total_time': total_time,
            'iteration_count': iteration_count,
            'iterations_per_second': iteration_count / total_time,
            'memory_samples': memory_samples,
            'memory_stable': max(memory_samples) - min(memory_samples) < 50 if memory_samples else True
        }
        
        print(f"    总时间: {total_time:.1f}s")
        print(f"    总迭代: {iteration_count}")
        print(f"    迭代速率: {results['iterations_per_second']:.1f} 次/秒")
        print(f"    内存稳定: {'是' if results['memory_stable'] else '否'}")
        
        return results
    
    def test_exception_recovery(self):
        """测试异常恢复"""
        def failing_task(should_fail):
            """可能失败的任务"""
            if should_fail:
                raise ValueError("模拟任务失败")
            return "任务成功"
        
        # 测试异常处理
        tasks = [False] * 5 + [True] * 3 + [False] * 2  # 混合成功和失败的任务
        
        success_count = 0
        error_count = 0
        results = []
        
        for i, should_fail in enumerate(tasks):
            try:
                result = failing_task(should_fail)
                results.append(('success', result))
                success_count += 1
            except Exception as e:
                results.append(('error', str(e)))
                error_count += 1
        
        # 测试系统在异常后的恢复能力
        recovery_test_passed = True
        try:
            # 在异常后继续正常工作
            normal_data = self.generate_mock_stock_data(10)
            assert len(normal_data) == 10
        except Exception:
            recovery_test_passed = False
        
        test_results = {
            'total_tasks': len(tasks),
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / len(tasks),
            'recovery_test_passed': recovery_test_passed
        }
        
        print(f"    总任务: {test_results['total_tasks']}")
        print(f"    成功: {success_count}, 失败: {error_count}")
        print(f"    成功率: {test_results['success_rate']:.2%}")
        print(f"    恢复测试: {'通过' if recovery_test_passed else '失败'}")
        
        return test_results
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 50)
        print("📊 压力测试报告")
        print("=" * 50)
        
        if self.errors:
            print(f"\n❌ 失败的测试 ({len(self.errors)}):")
            for test_name, error in self.errors:
                print(f"  - {test_name}: {error}")
        
        if self.results:
            print(f"\n✅ 成功的测试 ({len(self.results)}):")
            for test_name in self.results:
                print(f"  - {test_name}")
        
        # 系统资源使用情况
        print(f"\n💻 系统资源:")
        print(f"  CPU核心数: {mp.cpu_count()}")
        print(f"  内存总量: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB")
        print(f"  当前内存使用: {psutil.virtual_memory().percent:.1f}%")
        
        # 性能建议
        print(f"\n💡 性能建议:")
        if len(self.errors) == 0:
            print("  ✅ 系统在压力测试中表现良好")
            print("  ✅ 所有测试都通过了压力测试")
        else:
            print("  ⚠️ 部分测试失败，建议检查相关组件")
        
        print("  📈 建议定期进行压力测试以确保系统稳定性")
        print("  🔧 根据实际负载调整系统配置参数")

def main():
    """主函数"""
    runner = StressTestRunner()
    runner.run_all_tests()

if __name__ == "__main__":
    main()
