#!/usr/bin/env python3
"""
多数据源整合演示脚本

展示长期改进方案的效果，包括：
1. 多数据源自动切换
2. 数据质量对比验证
3. 智能缓存机制
4. 性能监控
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
import time

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from market_data.fetchers.multi_source_fetcher import MultiSourceFetcher, DataSourceConfig, CacheStrategy
    from market_data.utils.cache_manager import CacheManager, CacheConfig
    from quant_system.utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保在项目根目录下运行此脚本")
    sys.exit(1)


class MultiSourceDemo:
    """多数据源整合演示"""

    def __init__(self):
        """初始化演示器"""
        # 初始化多数据源整合器
        self.multi_fetcher = MultiSourceFetcher()

        # 初始化缓存管理器
        cache_config = CacheConfig(
            strategy=CacheStrategy.MEDIUM,
            ttl_seconds=3600,
            max_size_mb=50,
            compress=True,
            enable_monitoring=True
        )
        self.cache_manager = CacheManager("cache", cache_config)

        # 测试股票代码
        self.test_stocks = {
            'A股': ['000001', '600000', '300001'],  # 平安银行、浦发银行、特锐德
            '港股': ['00700', '00941', '02318']     # 腾讯控股、中国移动、中国平安
        }

        # 测试时间范围
        self.end_date = date.today()
        self.start_date = self.end_date - timedelta(days=30)

    def demo_data_source_health_check(self):
        """演示数据源健康检查"""
        print("\n" + "="*80)
        print("🏥 数据源健康检查演示")
        print("="*80)

        print("\n📊 可用数据源:")
        for market_type in ['a_stock', 'h_stock']:
            available_sources = self.multi_fetcher.get_available_sources(
                market_type)
            print(f"\n{market_type.upper()} 市场:")
            for source_name in available_sources:
                config = self.multi_fetcher.data_sources[source_name]
                health_status = self.multi_fetcher.check_source_health(
                    source_name)
                status_icon = "✅" if health_status else "❌"
                free_icon = "🆓" if config.is_free else "💰"
                cost_info = f"¥{config.cost_per_month}/月" if config.cost_per_month else "免费"

                print(f"  {status_icon} {free_icon} {source_name}: {cost_info}")
                print(f"     优先级: {config.priority}, 支持: A股={config.supports_a_stock}, "
                      f"港股={config.supports_h_stock}, 美股={config.supports_us_stock}")

        # 获取性能报告
        report = self.multi_fetcher.get_performance_report()
        print(f"\n📈 性能报告:")
        print(f"   总数据源: {report['total_sources']}")
        print(f"   可用数据源: {report['available_sources']}")
        print(f"   推荐: {', '.join(report['recommendations'])}")

    def demo_fallback_mechanism(self):
        """演示故障转移机制"""
        print("\n" + "="*80)
        print("🔄 故障转移机制演示")
        print("="*80)

        for market_name, stock_codes in self.test_stocks.items():
            print(f"\n🏛️ 测试市场: {market_name}")
            print("-" * 60)

            for stock_code in stock_codes:
                print(f"\n   测试股票: {stock_code}")

                # 使用故障转移机制获取数据
                data = self.multi_fetcher.get_historical_data_with_fallback(
                    stock_code, self.start_date, self.end_date
                )

                if data:
                    print(f"   ✅ 成功获取 {len(data)} 条数据")
                    print(f"   数据源: {data[0].get('source', 'unknown')}")

                    # 显示最近3天的数据
                    print("   最近3天数据:")
                    for item in data[-3:]:
                        print(f"     {item['date']}: 开盘{item['open']:.2f}, "
                              f"收盘{item['close']:.2f}, 涨跌幅{item['pct_change']:.2f}%")
                else:
                    print(f"   ❌ 所有数据源都无法获取数据")

    def demo_data_quality_comparison(self):
        """演示数据质量对比"""
        print("\n" + "="*80)
        print("📊 数据质量对比演示")
        print("="*80)

        test_stock = '000001'  # 平安银行
        print(f"\n🔍 对比股票: {test_stock}")

        # 比较不同数据源的数据质量
        quality_metrics = self.multi_fetcher.compare_data_quality(
            test_stock, self.start_date, self.end_date
        )

        if quality_metrics:
            print("\n📈 数据质量评分:")
            print("-" * 80)
            print(
                f"{'数据源':<12} {'完整性':<8} {'准确性':<8} {'及时性':<8} {'一致性':<8} {'综合评分':<8}")
            print("-" * 80)

            for source_name, metrics in quality_metrics.items():
                print(f"{source_name:<12} {metrics.completeness:<8.2f} {metrics.accuracy:<8.2f} "
                      f"{metrics.timeliness:<8.2f} {metrics.consistency:<8.2f} {metrics.overall_score:<8.2f}")

            # 找出最佳数据源
            best_source = max(quality_metrics.items(),
                              key=lambda x: x[1].overall_score)
            print(
                f"\n🏆 最佳数据源: {best_source[0]} (评分: {best_source[1].overall_score:.2f})")
        else:
            print("❌ 无法获取数据质量对比信息")

    def demo_cache_mechanism(self):
        """演示缓存机制"""
        print("\n" + "="*80)
        print("💾 智能缓存机制演示")
        print("="*80)

        test_stock = '600000'  # 浦发银行

        print(f"\n📊 测试股票: {test_stock}")

        # 第一次获取数据（无缓存）
        print("\n1️⃣ 第一次获取数据 (无缓存):")
        start_time = time.time()
        data1 = self.multi_fetcher.get_historical_data_with_fallback(
            test_stock, self.start_date, self.end_date
        )
        time1 = time.time() - start_time

        if data1:
            print(f"   ✅ 获取成功，耗时: {time1:.2f}秒")

            # 缓存数据
            cache_strategy = CacheStrategy.MEDIUM
            cache_success = self.cache_manager.set(
                'historical_data', test_stock, data1, cache_strategy,
                start_date=self.start_date.isoformat(),
                end_date=self.end_date.isoformat()
            )

            if cache_success:
                print(f"   💾 数据已缓存 (策略: {cache_strategy.value})")
            else:
                print("   ❌ 缓存失败")

        # 第二次获取数据（有缓存）
        print("\n2️⃣ 第二次获取数据 (有缓存):")
        start_time = time.time()

        # 先尝试从缓存获取
        cached_data = self.cache_manager.get(
            'historical_data', test_stock,
            start_date=self.start_date.isoformat(),
            end_date=self.end_date.isoformat()
        )

        if cached_data:
            print(f"   ✅ 从缓存获取成功，耗时: {time.time() - start_time:.2f}秒")
            data2 = cached_data
        else:
            print("   ⚠️ 缓存未命中，重新获取数据")
            data2 = self.multi_fetcher.get_historical_data_with_fallback(
                test_stock, self.start_date, self.end_date
            )
            print(f"   ✅ 重新获取成功，耗时: {time.time() - start_time:.2f}秒")

        # 显示缓存统计
        cache_stats = self.cache_manager.get_stats()
        print(f"\n📈 缓存统计:")
        print(f"   总请求数: {cache_stats['stats']['total_requests']}")
        print(f"   缓存命中: {cache_stats['stats']['cache_hits']}")
        print(f"   缓存未命中: {cache_stats['stats']['cache_misses']}")
        print(f"   命中率: {cache_stats['stats']['hit_rate']:.2%}")
        print(f"   缓存大小: {cache_stats['stats']['total_size_mb']:.2f}MB")
        print(f"   缓存项数: {cache_stats['cache_count']}")

    def demo_performance_optimization(self):
        """演示性能优化"""
        print("\n" + "="*80)
        print("⚡ 性能优化演示")
        print("="*80)

        # 批量获取数据
        print("\n📦 批量数据获取测试:")
        all_stocks = []
        for stocks in self.test_stocks.values():
            all_stocks.extend(stocks)

        print(f"   测试股票数量: {len(all_stocks)}")

        # 不使用缓存
        print("\n🔄 不使用缓存:")
        start_time = time.time()
        success_count = 0

        for stock_code in all_stocks:
            data = self.multi_fetcher.get_historical_data_with_fallback(
                stock_code, self.start_date, self.end_date
            )
            if data:
                success_count += 1

        time_without_cache = time.time() - start_time
        print(f"   成功获取: {success_count}/{len(all_stocks)}")
        print(f"   总耗时: {time_without_cache:.2f}秒")
        print(f"   平均耗时: {time_without_cache/len(all_stocks):.2f}秒/只")

        # 使用缓存
        print("\n💾 使用缓存:")
        start_time = time.time()
        success_count = 0

        for stock_code in all_stocks:
            # 先尝试从缓存获取
            cached_data = self.cache_manager.get(
                'historical_data', stock_code,
                start_date=self.start_date.isoformat(),
                end_date=self.end_date.isoformat()
            )

            if cached_data:
                success_count += 1
            else:
                # 缓存未命中，从数据源获取
                data = self.multi_fetcher.get_historical_data_with_fallback(
                    stock_code, self.start_date, self.end_date
                )
                if data:
                    success_count += 1
                    # 缓存数据
                    self.cache_manager.set(
                        'historical_data', stock_code, data, CacheStrategy.MEDIUM,
                        start_date=self.start_date.isoformat(),
                        end_date=self.end_date.isoformat()
                    )

        time_with_cache = time.time() - start_time
        print(f"   成功获取: {success_count}/{len(all_stocks)}")
        print(f"   总耗时: {time_with_cache:.2f}秒")
        print(f"   平均耗时: {time_with_cache/len(all_stocks):.2f}秒/只")

        # 性能提升
        if time_without_cache > 0:
            improvement = (time_without_cache - time_with_cache) / \
                time_without_cache * 100
            print(f"   性能提升: {improvement:.1f}%")

    def demo_cost_analysis(self):
        """演示成本分析"""
        print("\n" + "="*80)
        print("💰 成本分析演示")
        print("="*80)

        print("\n📊 数据源成本对比:")
        print("-" * 80)
        print(f"{'数据源':<15} {'费用':<12} {'A股':<6} {'港股':<6} {'美股':<6} {'推荐指数':<8}")
        print("-" * 80)

        cost_data = [
            ('akshare', '免费', '✅', '⚠️', '❌', '⭐⭐⭐⭐⭐'),
            ('东方财富', '免费', '✅', '❌', '❌', '⭐⭐⭐⭐'),
            ('Yahoo Finance', '免费', '⚠️', '✅', '✅', '⭐⭐⭐⭐'),
            ('Tushare基础版', '¥199/月', '✅', '⚠️', '❌', '⭐⭐⭐⭐⭐'),
            ('聚宽基础版', '¥99/月', '✅', '✅', '✅', '⭐⭐⭐⭐'),
            ('万得个人版', '¥299/月', '✅', '✅', '✅', '⭐⭐⭐⭐'),
        ]

        for source, cost, a_stock, h_stock, us_stock, rating in cost_data:
            print(
                f"{source:<15} {cost:<12} {a_stock:<6} {h_stock:<6} {us_stock:<6} {rating:<8}")

        print("\n💡 推荐方案:")
        print("1. 🆓 纯免费方案: akshare + Yahoo Finance (月费用: ¥0)")
        print("2. 💰 混合方案: akshare + Tushare基础版 + Yahoo Finance (月费用: ¥199)")
        print("3. 💎 专业方案: Tushare专业版 + 聚宽专业版 + 万得数据 (月费用: ¥697)")

    def run_all_demos(self):
        """运行所有演示"""
        print("🚀 多数据源整合系统演示")
        print("=" * 80)
        print(f"演示时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 运行各个演示
        self.demo_data_source_health_check()
        self.demo_fallback_mechanism()
        self.demo_data_quality_comparison()
        self.demo_cache_mechanism()
        self.demo_performance_optimization()
        self.demo_cost_analysis()

        print("\n" + "="*80)
        print("🎉 演示完成!")
        print("="*80)
        print("\n📋 长期改进方案总结:")
        print("✅ 多数据源自动切换 - 提高数据可用性")
        print("✅ 数据质量对比验证 - 确保数据准确性")
        print("✅ 智能缓存机制 - 提升性能")
        print("✅ 成本效益分析 - 优化资源配置")
        print("\n💡 下一步建议:")
        print("1. 根据实际需求选择合适的付费数据源")
        print("2. 持续监控数据源健康状态")
        print("3. 定期优化缓存策略")
        print("4. 建立数据质量监控体系")


def main():
    """主函数"""
    demo = MultiSourceDemo()
    demo.run_all_demos()


if __name__ == "__main__":
    main()
