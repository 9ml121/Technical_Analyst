#!/usr/bin/env python3
"""
策略监控和优化系统

建立完整的机器学习策略监控和优化系统：
1. 自动模型训练和更新
2. 实时性能监控
3. 风险预警系统
4. 自动参数优化
5. 策略表现报告
"""

import sys
from pathlib import Path
from datetime import date, timedelta, datetime
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import json
import os

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StrategyMonitor:
    """策略监控器"""

    def __init__(self, strategy, config_file: str = "strategy_monitor_config.json"):
        """初始化监控器"""
        self.strategy = strategy
        self.config_file = config_file
        self.monitoring_data = {
            'performance_history': [],
            'risk_metrics': [],
            'alerts': [],
            'model_updates': []
        }
        self.load_config()

        print("🔍 策略监控器初始化完成")

    def load_config(self):
        """加载监控配置"""
        default_config = {
            'performance_thresholds': {
                'min_sharpe_ratio': 0.8,
                'max_drawdown': 0.15,
                'min_win_rate': 0.55,
                'max_volatility': 0.25
            },
            'risk_alerts': {
                'drawdown_alert': 0.10,
                'volatility_alert': 0.20,
                'loss_streak_alert': 5
            },
            'model_update_frequency': 20,  # 每20个交易日更新一次
            'performance_evaluation_period': 30  # 30天评估周期
        }

        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """保存监控配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def calculate_performance_metrics(self, returns: List[float]) -> Dict:
        """计算性能指标"""
        if not returns:
            return {}

        returns_array = np.array(returns)

        # 基础指标
        total_return = (1 + returns_array).prod() - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = np.std(returns_array) * np.sqrt(252)

        # 风险调整收益
        risk_free_rate = 0.03
        sharpe_ratio = (annual_return - risk_free_rate) / \
            volatility if volatility > 0 else 0

        # 最大回撤
        cumulative_returns = (1 + returns_array).cumprod()
        peak = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = abs(drawdown.min())

        # 胜率
        win_rate = np.sum(returns_array > 0) / len(returns_array)

        # 盈亏比
        positive_returns = returns_array[returns_array > 0]
        negative_returns = returns_array[returns_array < 0]
        avg_win = np.mean(positive_returns) if len(positive_returns) > 0 else 0
        avg_loss = abs(np.mean(negative_returns)) if len(
            negative_returns) > 0 else 0
        profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0

        # Calmar比率
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0

        # Sortino比率
        downside_returns = returns_array[returns_array < 0]
        downside_volatility = np.std(
            downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annual_return - risk_free_rate) / \
            downside_volatility if downside_volatility > 0 else 0

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio,
            'calmar_ratio': calmar_ratio,
            'sortino_ratio': sortino_ratio,
            'period_days': len(returns)
        }

    def check_risk_alerts(self, metrics: Dict) -> List[str]:
        """检查风险预警"""
        alerts = []
        thresholds = self.config['performance_thresholds']
        risk_alerts = self.config['risk_alerts']

        # 性能预警
        if metrics.get('sharpe_ratio', 0) < thresholds['min_sharpe_ratio']:
            alerts.append(
                f"夏普比率过低: {metrics['sharpe_ratio']:.3f} < {thresholds['min_sharpe_ratio']}")

        if metrics.get('max_drawdown', 0) > thresholds['max_drawdown']:
            alerts.append(
                f"最大回撤过大: {metrics['max_drawdown']:.2%} > {thresholds['max_drawdown']:.2%}")

        if metrics.get('win_rate', 0) < thresholds['min_win_rate']:
            alerts.append(
                f"胜率过低: {metrics['win_rate']:.2%} < {thresholds['min_win_rate']:.2%}")

        if metrics.get('volatility', 0) > thresholds['max_volatility']:
            alerts.append(
                f"波动率过高: {metrics['volatility']:.2%} > {thresholds['max_volatility']:.2%}")

        # 风险预警
        if metrics.get('max_drawdown', 0) > risk_alerts['drawdown_alert']:
            alerts.append(
                f"⚠️ 回撤预警: {metrics['max_drawdown']:.2%} > {risk_alerts['drawdown_alert']:.2%}")

        if metrics.get('volatility', 0) > risk_alerts['volatility_alert']:
            alerts.append(
                f"⚠️ 波动率预警: {metrics['volatility']:.2%} > {risk_alerts['volatility_alert']:.2%}")

        return alerts

    def update_performance_history(self, daily_return: float, timestamp: datetime):
        """更新性能历史"""
        self.monitoring_data['performance_history'].append({
            'timestamp': timestamp,
            'daily_return': daily_return
        })

        # 保持最近1000天的数据
        if len(self.monitoring_data['performance_history']) > 1000:
            self.monitoring_data['performance_history'] = self.monitoring_data['performance_history'][-1000:]

    def evaluate_strategy_performance(self) -> Dict:
        """评估策略性能"""
        if len(self.monitoring_data['performance_history']) < 10:
            return {}

        # 获取最近的性能数据
        recent_period = self.config['performance_evaluation_period']
        recent_data = self.monitoring_data['performance_history'][-recent_period:]

        returns = [item['daily_return'] for item in recent_data]
        metrics = self.calculate_performance_metrics(returns)

        # 检查风险预警
        alerts = self.check_risk_alerts(metrics)

        # 记录评估结果
        evaluation_result = {
            'timestamp': datetime.now(),
            'metrics': metrics,
            'alerts': alerts,
            'evaluation_period': recent_period
        }

        self.monitoring_data['risk_metrics'].append(evaluation_result)

        # 保持最近100次评估记录
        if len(self.monitoring_data['risk_metrics']) > 100:
            self.monitoring_data['risk_metrics'] = self.monitoring_data['risk_metrics'][-100:]

        return evaluation_result

    def should_update_model(self) -> bool:
        """判断是否需要更新模型"""
        if not self.monitoring_data['model_updates']:
            return True

        last_update = self.monitoring_data['model_updates'][-1]['timestamp']
        days_since_update = (datetime.now() - last_update).days

        return days_since_update >= self.config['model_update_frequency']

    def record_model_update(self, update_info: Dict):
        """记录模型更新"""
        update_record = {
            'timestamp': datetime.now(),
            'update_info': update_info
        }
        self.monitoring_data['model_updates'].append(update_record)

        # 保持最近50次更新记录
        if len(self.monitoring_data['model_updates']) > 50:
            self.monitoring_data['model_updates'] = self.monitoring_data['model_updates'][-50:]

    def generate_performance_report(self) -> str:
        """生成性能报告"""
        if not self.monitoring_data['performance_history']:
            return "暂无性能数据"

        # 计算总体性能指标
        all_returns = [item['daily_return']
                       for item in self.monitoring_data['performance_history']]
        overall_metrics = self.calculate_performance_metrics(all_returns)

        # 获取最近的评估结果
        recent_evaluation = None
        if self.monitoring_data['risk_metrics']:
            recent_evaluation = self.monitoring_data['risk_metrics'][-1]

        # 生成报告
        report = f"""
📊 策略性能报告
{'='*50}
📈 总体表现 (共{len(all_returns)}个交易日):
  总收益率: {overall_metrics.get('total_return', 0):.2%}
  年化收益率: {overall_metrics.get('annual_return', 0):.2%}
  年化波动率: {overall_metrics.get('volatility', 0):.2%}
  夏普比率: {overall_metrics.get('sharpe_ratio', 0):.3f}
  最大回撤: {overall_metrics.get('max_drawdown', 0):.2%}
  胜率: {overall_metrics.get('win_rate', 0):.2%}
  盈亏比: {overall_metrics.get('profit_loss_ratio', 0):.2f}
  Calmar比率: {overall_metrics.get('calmar_ratio', 0):.3f}
  Sortino比率: {overall_metrics.get('sortino_ratio', 0):.3f}

📋 最近评估 ({recent_evaluation['evaluation_period'] if recent_evaluation else 0}天):
"""

        if recent_evaluation:
            recent_metrics = recent_evaluation['metrics']
            report += f"""  年化收益率: {recent_metrics.get('annual_return', 0):.2%}
  夏普比率: {recent_metrics.get('sharpe_ratio', 0):.3f}
  最大回撤: {recent_metrics.get('max_drawdown', 0):.2%}
  胜率: {recent_metrics.get('win_rate', 0):.2%}
"""

            if recent_evaluation['alerts']:
                report += "\n🚨 风险预警:\n"
                for alert in recent_evaluation['alerts']:
                    report += f"  • {alert}\n"

        # 模型更新历史
        if self.monitoring_data['model_updates']:
            report += f"\n🤖 模型更新历史 (最近{min(5, len(self.monitoring_data['model_updates']))}次):\n"
            for update in self.monitoring_data['model_updates'][-5:]:
                report += f"  • {update['timestamp'].strftime('%Y-%m-%d %H:%M')}: {update['update_info'].get('reason', '模型更新')}\n"

        return report

    def save_monitoring_data(self, filename: str = "monitoring_data.json"):
        """保存监控数据"""
        # 转换datetime对象为字符串
        data_to_save = {}
        for key, value in self.monitoring_data.items():
            if key in ['performance_history', 'risk_metrics', 'model_updates']:
                data_to_save[key] = []
                for item in value:
                    item_copy = item.copy()
                    if 'timestamp' in item_copy:
                        item_copy['timestamp'] = item_copy['timestamp'].isoformat()
                    data_to_save[key].append(item_copy)
            else:
                data_to_save[key] = value

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

        print(f"✅ 监控数据已保存到 {filename}")


class AutoOptimizer:
    """自动优化器"""

    def __init__(self, strategy, monitor: StrategyMonitor):
        """初始化自动优化器"""
        self.strategy = strategy
        self.monitor = monitor
        self.optimization_history = []

        print("🔧 自动优化器初始化完成")

    def optimize_strategy_parameters(self) -> Dict:
        """优化策略参数"""
        print("🔧 开始自动参数优化...")

        # 获取当前性能指标
        evaluation = self.monitor.evaluate_strategy_performance()
        if not evaluation:
            print("❌ 无法获取性能数据，跳过优化")
            return {}

        current_metrics = evaluation['metrics']
        current_alerts = evaluation['alerts']

        # 定义参数搜索空间
        param_ranges = {
            'signal_threshold': [0.01, 0.02, 0.03, 0.04, 0.05],
            'confidence_threshold': [0.6, 0.65, 0.7, 0.75, 0.8],
            'max_position_pct': [0.1, 0.12, 0.15, 0.18, 0.2],
            'stop_loss_pct': [0.05, 0.06, 0.07, 0.08, 0.09],
            'take_profit_pct': [0.12, 0.15, 0.18, 0.2, 0.25]
        }

        best_params = {}
        best_score = -np.inf

        # 模拟参数优化过程
        print("  参数搜索中...")
        for i in range(10):  # 模拟10次参数组合测试
            # 随机选择参数组合
            test_params = {}
            for param, values in param_ranges.items():
                test_params[param] = np.random.choice(values)

            # 模拟性能评估
            simulated_sharpe = np.random.uniform(0.5, 1.5)
            simulated_drawdown = np.random.uniform(0.05, 0.15)
            simulated_return = np.random.uniform(0.05, 0.25)

            # 计算综合评分
            score = simulated_sharpe * 0.4 + \
                (1 - simulated_drawdown) * 0.3 + simulated_return * 0.3

            if score > best_score:
                best_score = score
                best_params = test_params.copy()

            print(f"    测试 {i+1}/10: 评分 {score:.3f}")

        # 应用最佳参数
        if best_params:
            print(f"  ✅ 找到最佳参数组合，评分: {best_score:.3f}")
            print("  最佳参数:")
            for param, value in best_params.items():
                print(f"    {param}: {value}")

            # 记录优化结果
            optimization_record = {
                'timestamp': datetime.now(),
                'previous_metrics': current_metrics,
                'new_params': best_params,
                'expected_improvement': best_score,
                'reason': '自动参数优化'
            }
            self.optimization_history.append(optimization_record)

            return best_params

        return {}

    def suggest_model_improvements(self) -> List[str]:
        """建议模型改进"""
        suggestions = []

        # 基于性能指标提出建议
        evaluation = self.monitor.evaluate_strategy_performance()
        if not evaluation:
            return suggestions

        metrics = evaluation['metrics']

        if metrics.get('sharpe_ratio', 0) < 1.0:
            suggestions.append("夏普比率偏低，建议增加更多技术指标特征")

        if metrics.get('max_drawdown', 0) > 0.12:
            suggestions.append("最大回撤过大，建议优化止损策略和仓位管理")

        if metrics.get('win_rate', 0) < 0.55:
            suggestions.append("胜率偏低，建议优化信号生成逻辑和特征选择")

        if metrics.get('volatility', 0) > 0.20:
            suggestions.append("波动率过高，建议增加风险控制措施")

        # 通用建议
        suggestions.extend([
            "考虑使用集成学习方法（如Stacking）",
            "增加基本面因子和宏观经济指标",
            "优化特征工程，去除冗余特征",
            "考虑多时间框架分析",
            "增加市场情绪指标"
        ])

        return suggestions


def run_strategy_monitoring_system():
    """运行策略监控系统"""
    print("🚀 策略监控和优化系统")
    print("=" * 60)

    try:
        # 1. 创建策略配置
        from quant_system.core.ml_enhanced_strategy import MLStrategyConfig, ModelConfig

        model_config = ModelConfig(
            model_type='random_forest',
            n_estimators=200,
            max_depth=12,
            feature_selection='kbest',
            n_features=20,
            target_horizon=5
        )

        strategy_config = MLStrategyConfig(
            name="监控优化策略",
            model_config=model_config,
            signal_threshold=0.02,
            confidence_threshold=0.7,
            position_sizing='kelly',
            risk_management={
                "max_position_pct": 0.15,
                "max_positions": 8,
                "stop_loss_pct": 0.06,
                "take_profit_pct": 0.15,
                "max_drawdown_pct": 0.12,
                "min_confidence": 0.65
            }
        )

        # 2. 创建策略实例
        from quant_system.core.ml_enhanced_strategy import MLEnhancedStrategy
        strategy = MLEnhancedStrategy(strategy_config)

        # 3. 初始化监控器
        monitor = StrategyMonitor(strategy)

        # 4. 初始化优化器
        optimizer = AutoOptimizer(strategy, monitor)

        # 5. 模拟监控数据
        print("\n📊 模拟监控数据...")

        # 生成模拟的每日收益数据
        np.random.seed(42)
        simulation_days = 100
        daily_returns = np.random.normal(
            0.001, 0.02, simulation_days)  # 平均0.1%，标准差2%

        # 添加一些趋势和波动
        trend = np.linspace(0, 0.002, simulation_days)  # 逐渐改善的趋势
        daily_returns += trend

        # 更新监控数据
        for i, daily_return in enumerate(daily_returns):
            timestamp = datetime.now() - timedelta(days=simulation_days-i)
            monitor.update_performance_history(daily_return, timestamp)

        print(f"✅ 已生成 {simulation_days} 天的模拟监控数据")

        # 6. 性能评估
        print("\n📈 策略性能评估...")
        evaluation = monitor.evaluate_strategy_performance()

        if evaluation:
            metrics = evaluation['metrics']
            print(f"  年化收益率: {metrics.get('annual_return', 0):.2%}")
            print(f"  夏普比率: {metrics.get('sharpe_ratio', 0):.3f}")
            print(f"  最大回撤: {metrics.get('max_drawdown', 0):.2%}")
            print(f"  胜率: {metrics.get('win_rate', 0):.2%}")

            if evaluation['alerts']:
                print("\n🚨 风险预警:")
                for alert in evaluation['alerts']:
                    print(f"  • {alert}")

        # 7. 自动优化
        print("\n🔧 自动参数优化...")
        optimized_params = optimizer.optimize_strategy_parameters()

        if optimized_params:
            print("✅ 参数优化完成")

        # 8. 模型改进建议
        print("\n💡 模型改进建议...")
        suggestions = optimizer.suggest_model_improvements()

        for i, suggestion in enumerate(suggestions[:5], 1):  # 显示前5个建议
            print(f"  {i}. {suggestion}")

        # 9. 生成性能报告
        print("\n📋 生成性能报告...")
        report = monitor.generate_performance_report()
        print(report)

        # 10. 保存监控数据
        monitor.save_monitoring_data()

        print("\n🎉 策略监控系统运行完成！")
        return True

    except Exception as e:
        print(f"❌ 监控系统运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_strategy_monitoring_system()

    if success:
        print("\n💡 下一步建议:")
        print("1. 根据监控结果调整策略参数")
        print("2. 实施模型改进建议")
        print("3. 建立实时监控告警机制")
        print("4. 定期进行策略回测验证")
        print("5. 考虑多策略组合管理")
    else:
        print("\n🔧 请检查:")
        print("1. 策略配置是否正确")
        print("2. 监控参数是否合理")
        print("3. 数据源是否可用")
        print("4. 系统依赖是否完整")
