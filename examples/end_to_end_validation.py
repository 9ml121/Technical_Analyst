#!/usr/bin/env python3
"""
端到端验证脚本 - 正式量化交易策略

验证正式量化交易策略的完整流程：
1. 系统初始化
2. 数据获取和处理
3. 策略执行
4. 回测验证
5. 性能分析
6. 结果报告
"""

import sys
from pathlib import Path
from datetime import date, timedelta, datetime
import time
import logging
import json
import warnings
warnings.filterwarnings('ignore')

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EndToEndValidator:
    """端到端验证器"""

    def __init__(self):
        """初始化验证器"""
        self.validation_results = {}
        self.start_time = time.time()

        logger.info("端到端验证器初始化完成")

    def run_full_validation(self):
        """运行完整验证流程"""
        print("🚀 开始端到端验证 - 正式量化交易策略")
        print("=" * 60)

        try:
            # 1. 系统初始化验证
            print("\n📋 步骤1: 系统初始化验证")
            init_success = self._validate_system_initialization()
            self.validation_results['system_initialization'] = init_success

            if not init_success:
                print("❌ 系统初始化失败，终止验证")
                return False

            # 2. 数据获取验证
            print("\n📊 步骤2: 数据获取验证")
            data_success = self._validate_data_acquisition()
            self.validation_results['data_acquisition'] = data_success

            if not data_success:
                print("❌ 数据获取失败，终止验证")
                return False

            # 3. 策略执行验证
            print("\n🎯 步骤3: 策略执行验证")
            strategy_success = self._validate_strategy_execution()
            self.validation_results['strategy_execution'] = strategy_success

            if not strategy_success:
                print("❌ 策略执行失败，终止验证")
                return False

            # 4. 回测验证
            print("\n📈 步骤4: 回测验证")
            backtest_success = self._validate_backtest()
            self.validation_results['backtest'] = backtest_success

            if not backtest_success:
                print("❌ 回测验证失败，终止验证")
                return False

            # 5. 性能分析验证
            print("\n📊 步骤5: 性能分析验证")
            performance_success = self._validate_performance_analysis()
            self.validation_results['performance_analysis'] = performance_success

            # 6. 结果保存验证
            print("\n💾 步骤6: 结果保存验证")
            save_success = self._validate_result_saving()
            self.validation_results['result_saving'] = save_success

            # 7. 生成验证报告
            print("\n📋 步骤7: 生成验证报告")
            self._generate_validation_report()

            # 计算总耗时
            total_time = time.time() - self.start_time
            print(f"\n⏱️ 总验证耗时: {total_time:.2f} 秒")

            # 总结验证结果
            success_count = sum(self.validation_results.values())
            total_count = len(self.validation_results)

            print(f"\n📊 验证结果总结:")
            print(f"   成功步骤: {success_count}/{total_count}")
            print(f"   成功率: {success_count/total_count*100:.1f}%")

            if success_count == total_count:
                print("🎉 端到端验证完全成功！")
                return True
            else:
                print("⚠️ 端到端验证部分成功，请检查失败的步骤")
                return False

        except Exception as e:
            logger.error(f"端到端验证过程中发生错误: {e}")
            print(f"❌ 验证过程中发生错误: {e}")
            return False

    def _validate_system_initialization(self) -> bool:
        """验证系统初始化"""
        try:
            print("   正在初始化正式量化交易策略...")

            # 导入策略类
            from formal_quantitative_strategy import FormalQuantitativeStrategy

            # 创建策略实例
            strategy = FormalQuantitativeStrategy()

            # 初始化组件
            init_success = strategy.initialize_components()

            if init_success:
                print("   ✅ 系统初始化成功")
                self.strategy = strategy
                return True
            else:
                print("   ❌ 系统初始化失败")
                return False

        except Exception as e:
            print(f"   ❌ 系统初始化异常: {e}")
            return False

    def _validate_data_acquisition(self) -> bool:
        """验证数据获取"""
        try:
            print("   正在验证数据获取功能...")

            # 获取股票池
            stock_pool = self.strategy.get_stock_pool()
            if not stock_pool:
                print("   ❌ 无法获取股票池")
                return False

            print(f"   ✅ 成功获取股票池，共 {len(stock_pool)} 只股票")

            # 获取历史数据（使用较短时间进行测试）
            end_date = date.today()
            start_date = end_date - timedelta(days=30)  # 30天数据

            print(f"   正在获取 {len(stock_pool[:5])} 只股票的历史数据...")
            historical_data = self.strategy.get_historical_data(
                stock_pool[:5], start_date, end_date)

            if not historical_data:
                print("   ❌ 无法获取历史数据")
                return False

            print(f"   ✅ 成功获取历史数据，共 {len(historical_data)} 只股票")

            # 验证数据质量
            data_quality_ok = self._validate_data_quality(historical_data)
            if not data_quality_ok:
                print("   ❌ 数据质量验证失败")
                return False

            print("   ✅ 数据质量验证通过")
            self.test_data = historical_data

            return True

        except Exception as e:
            print(f"   ❌ 数据获取验证异常: {e}")
            return False

    def _validate_data_quality(self, historical_data: dict) -> bool:
        """验证数据质量"""
        try:
            for code, data in historical_data.items():
                if len(data) < 20:  # 至少需要20天数据
                    return False

                # 检查数据完整性
                for item in data:
                    if not all(hasattr(item, attr) for attr in ['date', 'open_price', 'close_price', 'volume']):
                        return False

                    # 检查价格合理性
                    if item.close_price <= 0 or item.volume <= 0:
                        return False

            return True

        except Exception as e:
            logger.error(f"数据质量验证失败: {e}")
            return False

    def _validate_strategy_execution(self) -> bool:
        """验证策略执行"""
        try:
            print("   正在验证策略执行功能...")

            if not hasattr(self, 'test_data') or not self.test_data:
                print("   ❌ 没有测试数据")
                return False

            # 生成交易信号
            signals = self.strategy.generate_trading_signals(self.test_data)

            print(f"   ✅ 成功生成 {len(signals)} 个交易信号")

            # 验证信号质量
            if signals:
                signal_quality_ok = self._validate_signal_quality(signals)
                if not signal_quality_ok:
                    print("   ❌ 信号质量验证失败")
                    return False

                print("   ✅ 信号质量验证通过")

            self.test_signals = signals
            return True

        except Exception as e:
            print(f"   ❌ 策略执行验证异常: {e}")
            return False

    def _validate_signal_quality(self, signals: list) -> bool:
        """验证信号质量"""
        try:
            for signal in signals:
                # 检查必要字段
                required_fields = ['code', 'action', 'price', 'date', 'reason']
                if not all(field in signal for field in required_fields):
                    return False

                # 检查价格合理性
                if signal['price'] <= 0:
                    return False

                # 检查动作类型
                if signal['action'] not in ['BUY', 'SELL']:
                    return False

            return True

        except Exception as e:
            logger.error(f"信号质量验证失败: {e}")
            return False

    def _validate_backtest(self) -> bool:
        """验证回测功能"""
        try:
            print("   正在验证回测功能...")

            # 设置回测参数（使用较短时间进行测试）
            end_date = date.today()
            start_date = end_date - timedelta(days=60)  # 60天回测

            print(f"   回测期间: {start_date} 到 {end_date}")

            # 运行回测
            results = self.strategy.run_backtest(start_date, end_date)

            if not results:
                print("   ❌ 回测执行失败")
                return False

            # 验证回测结果
            if 'performance' not in results:
                print("   ❌ 回测结果缺少性能指标")
                return False

            performance = results['performance']
            required_metrics = ['total_return',
                                'annual_return', 'max_drawdown', 'sharpe_ratio']

            if not all(metric in performance for metric in required_metrics):
                print("   ❌ 回测结果缺少必要指标")
                return False

            print("   ✅ 回测执行成功")
            print(f"      总收益率: {performance.get('total_return', 0):.2%}")
            print(f"      年化收益率: {performance.get('annual_return', 0):.2%}")
            print(f"      最大回撤: {performance.get('max_drawdown', 0):.2%}")
            print(f"      夏普比率: {performance.get('sharpe_ratio', 0):.2f}")

            self.backtest_results = results
            return True

        except Exception as e:
            print(f"   ❌ 回测验证异常: {e}")
            return False

    def _validate_performance_analysis(self) -> bool:
        """验证性能分析"""
        try:
            print("   正在验证性能分析功能...")

            if not hasattr(self, 'backtest_results'):
                print("   ❌ 没有回测结果")
                return False

            # 生成性能报告
            report = self.strategy.generate_report()

            if not report or len(report.strip()) == 0:
                print("   ❌ 性能报告生成失败")
                return False

            print("   ✅ 性能报告生成成功")
            print(f"      报告长度: {len(report)} 字符")

            # 验证报告内容
            required_sections = ['策略信息', '回测结果', '交易统计', '策略配置']
            for section in required_sections:
                if section not in report:
                    print(f"   ❌ 报告缺少 {section} 部分")
                    return False

            print("   ✅ 性能报告内容验证通过")
            self.performance_report = report

            return True

        except Exception as e:
            print(f"   ❌ 性能分析验证异常: {e}")
            return False

    def _validate_result_saving(self) -> bool:
        """验证结果保存"""
        try:
            print("   正在验证结果保存功能...")

            # 保存结果
            output_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.strategy.save_results(output_file)

            # 检查文件是否创建
            if not Path(output_file).exists():
                print("   ❌ 结果文件未创建")
                return False

            # 验证文件内容
            with open(output_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)

            required_keys = ['strategy_info', 'config',
                             'results', 'performance_metrics']
            if not all(key in saved_data for key in required_keys):
                print("   ❌ 保存的数据缺少必要字段")
                return False

            print("   ✅ 结果保存成功")
            print(f"      保存文件: {output_file}")
            print(f"      文件大小: {Path(output_file).stat().st_size} 字节")

            self.saved_file = output_file
            return True

        except Exception as e:
            print(f"   ❌ 结果保存验证异常: {e}")
            return False

    def _generate_validation_report(self):
        """生成验证报告"""
        try:
            report = f"""
# 端到端验证报告

## 验证概述
- 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 验证策略: 正式量化交易策略V1.0
- 总耗时: {time.time() - self.start_time:.2f} 秒

## 验证结果

### 1. 系统初始化
- 状态: {'✅ 成功' if self.validation_results.get('system_initialization', False) else '❌ 失败'}
- 说明: 验证策略系统组件初始化

### 2. 数据获取
- 状态: {'✅ 成功' if self.validation_results.get('data_acquisition', False) else '❌ 失败'}
- 说明: 验证股票池获取和历史数据获取

### 3. 策略执行
- 状态: {'✅ 成功' if self.validation_results.get('strategy_execution', False) else '❌ 失败'}
- 说明: 验证交易信号生成

### 4. 回测验证
- 状态: {'✅ 成功' if self.validation_results.get('backtest', False) else '❌ 失败'}
- 说明: 验证回测执行和结果

### 5. 性能分析
- 状态: {'✅ 成功' if self.validation_results.get('performance_analysis', False) else '❌ 失败'}
- 说明: 验证性能指标计算和报告生成

### 6. 结果保存
- 状态: {'✅ 成功' if self.validation_results.get('result_saving', False) else '❌ 失败'}
- 说明: 验证结果文件保存

## 验证统计
- 成功步骤: {sum(self.validation_results.values())}/{len(self.validation_results)}
- 成功率: {sum(self.validation_results.values())/len(self.validation_results)*100:.1f}%

## 详细结果
"""

            # 添加详细结果
            if hasattr(self, 'backtest_results') and self.backtest_results:
                performance = self.backtest_results.get('performance', {})
                report += f"""
### 回测性能指标
- 总收益率: {performance.get('total_return', 0):.2%}
- 年化收益率: {performance.get('annual_return', 0):.2%}
- 最大回撤: {performance.get('max_drawdown', 0):.2%}
- 夏普比率: {performance.get('sharpe_ratio', 0):.2f}
- 胜率: {performance.get('win_rate', 0):.2%}
- 总交易次数: {performance.get('total_trades', 0)}
"""

            if hasattr(self, 'saved_file'):
                report += f"""
### 保存文件
- 文件名: {self.saved_file}
- 文件大小: {Path(self.saved_file).stat().st_size} 字节
"""

            # 保存验证报告
            report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"   📋 验证报告已保存: {report_file}")

        except Exception as e:
            print(f"   ❌ 生成验证报告失败: {e}")


def main():
    """主函数"""
    print("🚀 正式量化交易策略 - 端到端验证")
    print("=" * 60)

    # 创建验证器
    validator = EndToEndValidator()

    # 运行完整验证
    success = validator.run_full_validation()

    if success:
        print("\n🎉 端到端验证完全成功！")
        print("   正式量化交易策略已通过所有验证步骤")
        print("   可以投入生产环境使用")
    else:
        print("\n⚠️ 端到端验证部分成功")
        print("   请检查失败的验证步骤")
        print("   建议在投入生产环境前解决所有问题")

    return success


if __name__ == "__main__":
    main()
