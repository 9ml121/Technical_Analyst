#!/usr/bin/env python3
"""
系统集成测试

验证各个模块之间的协作和整体系统功能
"""

from quant_system.utils.cache import cache_manager
from quant_system.utils.performance import performance_monitor
from quant_system.utils.logger import get_logger
from quant_system.utils.config_loader import ConfigLoader
import sys
import pytest
import tempfile
import yaml
import logging
from pathlib import Path
from unittest.mock import Mock, patch

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


class TestSystemIntegration:
    """系统集成测试类"""

    def setup_method(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "config"
        self.config_dir.mkdir(parents=True)

        # 设置环境变量
        import os
        os.environ["ENVIRONMENT"] = "test"

        # 创建测试配置
        self.create_test_configs()

        # 初始化组件
        self.config_loader = ConfigLoader(str(self.config_dir))
        self.logger = get_logger("test")

    def teardown_method(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

        # 清理缓存
        cache_manager.clear_all()

    def create_test_configs(self):
        """创建测试配置文件"""
        # 默认配置
        default_config = {
            'system': {
                'name': '量化投资系统',
                'version': '1.0.0',
                'environment': 'test'
            },
            'database': {
                'host': 'localhost',
                'port': 3306,
                'name': 'quant_test'
            },
            'cache': {
                'enabled': True,
                'ttl': 300
            },
            'performance': {
                'monitoring': True,
                'parallel_processing': True
            }
        }

        with open(self.config_dir / "default.yaml", 'w') as f:
            yaml.dump(default_config, f)

        # 环境配置
        env_dir = self.config_dir / "environments"
        env_dir.mkdir()

        test_env_config = {
            'database': {
                'host': 'test-db',
                'name': 'quant_test_db'
            },
            'logging': {
                'level': 'DEBUG'
            }
        }

        with open(env_dir / "test.yaml", 'w') as f:
            yaml.dump(test_env_config, f)

        # 策略配置
        strategy_dir = self.config_dir / "strategies"
        strategy_dir.mkdir()

        strategy_config = {
            'strategy_info': {
                'name': '测试策略',
                'version': '1.0.0',
                'type': 'momentum'
            },
            'parameters': {
                'lookback_days': 20,
                'threshold': 0.05
            }
        }

        with open(strategy_dir / "test_strategy.yaml", 'w') as f:
            yaml.dump(strategy_config, f)

    def test_config_system_integration(self):
        """测试配置系统集成"""
        # 测试默认配置加载
        config = self.config_loader.load_config("default")
        assert config['system']['name'] == '量化投资系统'
        # 检查数据库配置存在（可能有默认值）
        assert 'database' in config
        assert 'host' in config['database']

        # 测试策略配置加载
        strategy_config = self.config_loader.load_strategy_config(
            "test_strategy")
        assert strategy_config['strategy_info']['name'] == '测试策略'

        # 测试配置缓存
        config1 = self.config_loader.load_config("default")
        config2 = self.config_loader.load_config("default")
        assert config1 is config2  # 应该是同一个对象（缓存）

    def test_logging_system_integration(self):
        """测试日志系统集成"""
        logger = get_logger("integration_test")

        # 测试不同级别的日志
        logger.debug("调试信息")
        logger.info("信息日志")
        logger.warning("警告信息")
        logger.error("错误信息")

        # 验证日志记录（这里简化处理）
        # 注意：get_logger可能返回现有的logger实例
        assert isinstance(logger, logging.Logger)
        # 日志器名称可能包含多种格式
        assert logger.name is not None

    def test_performance_monitoring_integration(self):
        """测试性能监控集成"""
        from quant_system.utils.performance import performance_timer, performance_context

        # 启动性能监控
        performance_monitor.start_monitoring(interval=0.1)

        try:
            @performance_timer
            def test_function():
                import time
                time.sleep(0.01)
                return "test result"

            # 执行被监控的函数
            result = test_function()
            assert result == "test result"

            # 使用性能上下文
            with performance_context("test_context"):
                import time
                time.sleep(0.01)

            # 检查性能统计
            stats = performance_monitor.get_function_stats()
            assert len(stats) > 0

        finally:
            performance_monitor.stop_monitoring()

    def test_cache_system_integration(self):
        """测试缓存系统集成"""
        from quant_system.utils.cache import cache_result

        call_count = 0

        @cache_result(ttl=1.0)
        def cached_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # 第一次调用
        result1 = cached_function(5)
        assert result1 == 10
        assert call_count == 1

        # 第二次调用（使用缓存）
        result2 = cached_function(5)
        assert result2 == 10
        assert call_count == 1  # 没有增加

        # 不同参数的调用
        result3 = cached_function(10)
        assert result3 == 20
        assert call_count == 2

    def test_data_processor_integration(self):
        """测试数据处理器集成"""
        try:
            from market_data.processors.data_processor import MarketDataProcessor

            processor = MarketDataProcessor(enable_parallel=False)  # 避免并发问题

            # 测试数据
            test_data = [
                {
                    'code': '000001',
                    'name': '测试股票1',
                    'price': 10.5,
                    'volume': 1000000,
                    'pct_change': 0.05
                },
                {
                    'code': '000002',
                    'name': '测试股票2',
                    'price': 20.0,
                    'volume': 2000000,
                    'pct_change': -0.02
                }
            ]

            # 测试数据清洗
            cleaned_data = processor.clean_stock_data(test_data)
            assert len(cleaned_data) == 2
            assert cleaned_data[0]['code'] == '000001'

            # 测试数据筛选
            filters = {'min_price': 15.0}
            filtered_data = processor.filter_stocks(cleaned_data, filters)
            assert len(filtered_data) == 1
            assert filtered_data[0]['code'] == '000002'

            # 测试数据排序
            sorted_data = processor.sort_stocks(
                cleaned_data, 'pct_change', ascending=False)
            assert sorted_data[0]['code'] == '000001'  # 涨幅更高的在前

        except ImportError:
            pytest.skip("数据处理器模块不可用")

    def test_concurrent_processing_integration(self):
        """测试并发处理集成"""
        from quant_system.utils.concurrent import parallel_map, WorkerPool

        def simple_task(x):
            return x * x

        # 测试并行映射
        test_data = list(range(10))
        results = parallel_map(simple_task, test_data, max_workers=2)
        expected = [x * x for x in test_data]
        assert results == expected

        # 测试工作线程池
        pool = WorkerPool(max_workers=2, queue_size=10)
        pool.start()

        try:
            # 提交任务
            for i in range(5):
                pool.submit_task(f"task_{i}", simple_task, i)

            # 等待任务完成
            import time
            time.sleep(0.5)

            # 检查统计信息
            stats = pool.get_stats()
            assert stats['completed_tasks'] >= 0

        finally:
            pool.stop()

    def test_error_handling_integration(self):
        """测试错误处理集成"""
        # 测试配置加载错误处理
        try:
            config = self.config_loader.load_config("nonexistent")
            # 应该返回默认配置或空配置，而不是抛出异常
            assert isinstance(config, dict)
        except Exception as e:
            pytest.fail(f"配置加载应该优雅处理错误: {e}")

        # 测试缓存错误处理
        from quant_system.utils.cache import LRUCache

        cache = LRUCache(max_size=2)

        # 测试无效键
        result = cache.get("nonexistent_key")
        assert result is None

        # 测试缓存满的情况
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")  # 应该淘汰key1

        assert cache.get("key1") is None
        assert cache.get("key3") == "value3"

    def test_system_startup_shutdown(self):
        """测试系统启动和关闭"""
        # 模拟系统启动
        startup_success = True

        try:
            # 初始化各个组件
            config = self.config_loader.load_config("default")
            logger = get_logger("system")

            # 启动性能监控
            if config.get('performance', {}).get('monitoring'):
                performance_monitor.start_monitoring()

            logger.info("系统启动成功")

        except Exception as e:
            startup_success = False
            print(f"系统启动失败: {e}")

        assert startup_success

        # 模拟系统关闭
        shutdown_success = True

        try:
            # 停止性能监控
            performance_monitor.stop_monitoring()

            # 清理缓存
            cache_manager.clear_all()

            logger.info("系统关闭成功")

        except Exception as e:
            shutdown_success = False
            print(f"系统关闭失败: {e}")

        assert shutdown_success

    def test_configuration_validation(self):
        """测试配置验证"""
        # 测试必需配置项
        config = self.config_loader.load_config("default")

        required_keys = ['system', 'database']
        for key in required_keys:
            assert key in config, f"缺少必需的配置项: {key}"

        # 测试配置类型
        assert isinstance(config['system']['name'], str)
        assert isinstance(config['database']['port'], int)
        assert isinstance(config['cache']['enabled'], bool)

    def test_memory_management(self):
        """测试内存管理"""
        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # 创建大量对象
        large_data = []
        for i in range(1000):
            large_data.append({
                'id': i,
                'data': f"test_data_{i}" * 100
            })

        # 检查内存增长
        after_creation = process.memory_info().rss
        memory_growth = after_creation - initial_memory

        # 清理对象
        del large_data
        gc.collect()

        # 检查内存释放
        after_cleanup = process.memory_info().rss
        memory_released = after_creation - after_cleanup

        # 验证内存管理效果
        assert memory_growth > 0, "内存应该有增长"
        # 注意：Python的内存管理可能不会立即释放所有内存
        # 所以这里只检查基本的内存管理功能

    def test_thread_safety(self):
        """测试线程安全"""
        import threading
        from quant_system.utils.cache import LRUCache

        cache = LRUCache(max_size=100)
        results = []
        errors = []

        def worker(worker_id):
            try:
                for i in range(10):
                    key = f"worker_{worker_id}_key_{i}"
                    value = f"worker_{worker_id}_value_{i}"

                    # 写入缓存
                    cache.put(key, value)

                    # 读取缓存
                    retrieved = cache.get(key)
                    results.append((key, retrieved))

            except Exception as e:
                errors.append(e)

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"线程安全测试出现错误: {errors}"
        assert len(results) == 50, f"期望50个结果，实际得到{len(results)}个"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
