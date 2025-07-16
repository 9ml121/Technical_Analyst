"""
量化交易策略制定模块
基于量化特征和行业最佳实践制定交易策略
整合多因子选股、动量策略、均值回归等主流量化策略
"""
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json

from quant_system_architecture import TradingSignal, StockData
from feature_extraction import QuantitativeFeatureExtractor

logger = logging.getLogger(__name__)


@dataclass
class TradingRule:
    """交易规则"""
    name: str
    condition: str
    weight: float
    description: str


@dataclass
class StrategyConfig:
    """策略配置"""
    name: str
    buy_rules: List[TradingRule]
    sell_rules: List[TradingRule]
    position_sizing: str
    risk_management: Dict[str, float]
    description: str


class QuantitativeTradingStrategy:
    """量化交易策略"""

    def __init__(self):
        """初始化交易策略"""
        self.strategies = {}
        self.feature_extractor = QuantitativeFeatureExtractor()
        self.current_strategy = None

        # 初始化内置策略
        self._initialize_builtin_strategies()

        logger.info("量化交易策略初始化完成")

    def _initialize_builtin_strategies(self):
        """初始化内置策略"""

        # 1. 多因子动量策略
        momentum_strategy = StrategyConfig(
            name="多因子动量策略",
            buy_rules=[
                TradingRule("价格动量", "momentum_20d > 0.15", 0.25, "20日动量超过15%"),
                TradingRule("成交量放大", "volume_ratio_5d > 1.5",
                            0.20, "5日成交量比20日均量放大1.5倍"),
                TradingRule(
                    "技术突破", "ma5_ratio > 0.02 and ma_bullish == 1", 0.20, "站上5日线且均线多头排列"),
                TradingRule("相对强度", "relative_strength > 0.05",
                            0.15, "相对强度指标良好"),
                TradingRule(
                    "波动率适中", "volatility_20d < 0.05 and volatility_20d > 0.01", 0.10, "波动率在合理区间"),
                TradingRule("RSI超卖反弹", "rsi > 30 and rsi < 70",
                            0.10, "RSI在合理区间")
            ],
            sell_rules=[
                TradingRule("止盈", "profit_pct >= 0.05", 1.0, "盈利达到5%止盈"),
                TradingRule("止损", "profit_pct <= -0.03", 1.0, "亏损达到3%止损"),
                TradingRule("技术破位", "ma5_ratio < -0.02", 0.8, "跌破5日线"),
                TradingRule("成交量萎缩", "volume_ratio_5d < 0.5", 0.6, "成交量严重萎缩"),
                TradingRule("RSI超买", "rsi > 80", 0.7, "RSI超买")
            ],
            position_sizing="equal_weight",
            risk_management={
                "max_position_pct": 0.20,
                "max_positions": 5,
                "stop_loss_pct": 0.03,
                "take_profit_pct": 0.05,
                "max_drawdown_pct": 0.10
            },
            description="基于多因子模型的动量策略，适合趋势性行情"
        )

        # 2. 均值回归策略
        mean_reversion_strategy = StrategyConfig(
            name="均值回归策略",
            buy_rules=[
                TradingRule(
                    "超跌反弹", "momentum_5d < -0.08 and momentum_20d > -0.15", 0.30, "短期超跌但中期趋势未破"),
                TradingRule("布林带下轨", "bb_position < 0.2", 0.25, "价格接近布林带下轨"),
                TradingRule("RSI超卖", "rsi < 30", 0.20, "RSI超卖"),
                TradingRule("成交量放大", "volume_ratio_5d > 1.2", 0.15, "成交量放大确认"),
                TradingRule("支撑位确认", "price_position < 0.3", 0.10, "价格在低位区间")
            ],
            sell_rules=[
                TradingRule("均值回归", "bb_position > 0.8", 0.8, "价格回归至布林带上轨"),
                TradingRule("RSI超买", "rsi > 70", 0.7, "RSI超买"),
                TradingRule("止损", "profit_pct <= -0.05", 1.0, "亏损达到5%止损"),
                TradingRule(
                    "反弹乏力", "momentum_3d < 0.02 and rsi > 50", 0.6, "反弹乏力")
            ],
            position_sizing="volatility_adjusted",
            risk_management={
                "max_position_pct": 0.15,
                "max_positions": 6,
                "stop_loss_pct": 0.05,
                "take_profit_pct": 0.08,
                "max_drawdown_pct": 0.08
            },
            description="基于均值回归理论的策略，适合震荡行情"
        )

        # 3. 突破策略
        breakout_strategy = StrategyConfig(
            name="技术突破策略",
            buy_rules=[
                TradingRule(
                    "价格突破", "price_position > 0.8 and momentum_5d > 0.05", 0.35, "价格突破近期高点"),
                TradingRule("成交量确认", "volume_ratio_5d > 2.0",
                            0.25, "成交量大幅放大确认突破"),
                TradingRule(
                    "均线支撑", "ma_bullish == 1 and ma20_ratio > 0.05", 0.20, "均线多头排列且站稳20日线"),
                TradingRule("MACD金叉", "macd_golden_cross == 1",
                            0.15, "MACD金叉确认"),
                TradingRule("ATR扩张", "atr > 0.03", 0.05, "真实波动率扩张")
            ],
            sell_rules=[
                TradingRule("快速止盈", "profit_pct >= 0.08", 1.0, "快速获利8%止盈"),
                TradingRule("跌破支撑", "ma10_ratio < -0.03", 0.9, "跌破10日线支撑"),
                TradingRule("成交量萎缩", "volume_ratio_5d < 0.8", 0.7, "成交量萎缩"),
                TradingRule("止损", "profit_pct <= -0.04", 1.0, "亏损4%止损")
            ],
            position_sizing="momentum_weighted",
            risk_management={
                "max_position_pct": 0.25,
                "max_positions": 4,
                "stop_loss_pct": 0.04,
                "take_profit_pct": 0.08,
                "max_drawdown_pct": 0.12
            },
            description="基于技术突破的策略，适合强势行情"
        )

        # 注册策略
        self.strategies = {
            "momentum": momentum_strategy,
            "mean_reversion": mean_reversion_strategy,
            "breakout": breakout_strategy
        }

        # 设置默认策略
        self.current_strategy = momentum_strategy

    def set_strategy(self, strategy_name: str) -> bool:
        """
        设置当前策略

        Args:
            strategy_name: 策略名称

        Returns:
            是否设置成功
        """
        if strategy_name in self.strategies:
            self.current_strategy = self.strategies[strategy_name]
            logger.info(f"切换到策略: {self.current_strategy.name}")
            return True
        else:
            logger.error(f"策略不存在: {strategy_name}")
            return False

    def generate_trading_signals(self, stock_data: List[StockData],
                                 current_positions: Dict = None) -> List[TradingSignal]:
        """
        生成交易信号

        Args:
            stock_data: 股票数据
            current_positions: 当前持仓

        Returns:
            交易信号列表
        """
        if not self.current_strategy or not stock_data:
            return []

        signals = []

        # 提取特征
        features = self.feature_extractor.extract_features(stock_data)
        if not features:
            return signals

        code = stock_data[0].code
        current_price = stock_data[-1].close_price

        # 检查买入信号
        if current_positions is None or code not in current_positions:
            buy_signal = self._evaluate_buy_rules(
                features, code, current_price)
            if buy_signal:
                signals.append(buy_signal)

        # 检查卖出信号
        if current_positions and code in current_positions:
            position = current_positions[code]
            sell_signal = self._evaluate_sell_rules(
                features, position, code, current_price)
            if sell_signal:
                signals.append(sell_signal)

        return signals

    def _evaluate_buy_rules(self, features: Dict[str, float], code: str, price: float) -> Optional[TradingSignal]:
        """评估买入规则"""
        total_score = 0
        total_weight = 0
        triggered_rules = []

        for rule in self.current_strategy.buy_rules:
            try:
                # 评估规则条件
                condition_result = self._evaluate_condition(
                    rule.condition, features)

                if condition_result:
                    total_score += rule.weight
                    triggered_rules.append(rule.name)

                total_weight += rule.weight

            except Exception as e:
                logger.debug(f"评估买入规则 {rule.name} 时出错: {e}")
                continue

        # 计算信号强度
        if total_weight > 0:
            signal_strength = total_score / total_weight
        else:
            signal_strength = 0

        # 买入阈值
        buy_threshold = 0.6  # 60%的规则满足才买入

        if signal_strength >= buy_threshold:
            return TradingSignal(
                code=code,
                signal_type='BUY',
                price=price,
                timestamp=datetime.now(),
                confidence=signal_strength,
                reason=f"触发规则: {', '.join(triggered_rules)}"
            )

        return None

    def _evaluate_sell_rules(self, features: Dict[str, float], position: Dict,
                             code: str, current_price: float) -> Optional[TradingSignal]:
        """评估卖出规则"""
        # 计算当前盈亏
        cost_price = position.get('avg_cost', current_price)
        profit_pct = (current_price - cost_price) / \
            cost_price if cost_price > 0 else 0

        # 添加盈亏特征
        features['profit_pct'] = profit_pct

        total_score = 0
        total_weight = 0
        triggered_rules = []

        for rule in self.current_strategy.sell_rules:
            try:
                condition_result = self._evaluate_condition(
                    rule.condition, features)

                if condition_result:
                    total_score += rule.weight
                    triggered_rules.append(rule.name)

                total_weight += rule.weight

            except Exception as e:
                logger.debug(f"评估卖出规则 {rule.name} 时出错: {e}")
                continue

        # 计算信号强度
        if total_weight > 0:
            signal_strength = total_score / total_weight
        else:
            signal_strength = 0

        # 卖出阈值
        sell_threshold = 0.5  # 50%的规则满足就卖出

        if signal_strength >= sell_threshold:
            return TradingSignal(
                code=code,
                signal_type='SELL',
                price=current_price,
                timestamp=datetime.now(),
                confidence=signal_strength,
                reason=f"触发规则: {', '.join(triggered_rules)} (盈亏: {profit_pct:.2%})"
            )

        return None

    def _evaluate_condition(self, condition: str, features: Dict[str, float]) -> bool:
        """
        评估条件表达式

        Args:
            condition: 条件字符串
            features: 特征字典

        Returns:
            条件是否满足
        """
        try:
            # 安全的条件评估
            # 替换特征名为实际值
            eval_condition = condition

            for feature_name, value in features.items():
                if feature_name in condition:
                    eval_condition = eval_condition.replace(
                        feature_name, str(value))

            # 只允许安全的操作符
            allowed_chars = set('0123456789.+-*/()><= and or')
            if not all(c in allowed_chars or c.isspace() for c in eval_condition):
                return False

            # 评估条件
            result = eval(eval_condition)
            return bool(result)

        except Exception as e:
            logger.debug(f"条件评估错误: {condition}, {e}")
            return False

    def calculate_position_size(self, signal: TradingSignal, available_capital: float,
                                current_positions: Dict) -> int:
        """
        计算仓位大小

        Args:
            signal: 交易信号
            available_capital: 可用资金
            current_positions: 当前持仓

        Returns:
            股票数量
        """
        if not self.current_strategy:
            return 0

        risk_config = self.current_strategy.risk_management
        max_position_pct = risk_config.get('max_position_pct', 0.20)
        max_positions = risk_config.get('max_positions', 5)

        # 检查持仓数量限制
        if len(current_positions) >= max_positions:
            return 0

        # 计算基础仓位
        base_position_value = available_capital * max_position_pct

        # 根据仓位调整方式计算
        sizing_method = self.current_strategy.position_sizing

        if sizing_method == "equal_weight":
            position_value = base_position_value
        elif sizing_method == "volatility_adjusted":
            # 根据波动率调整仓位
            volatility = signal.confidence  # 简化使用信号强度
            position_value = base_position_value * (1 - volatility * 0.5)
        elif sizing_method == "momentum_weighted":
            # 根据动量调整仓位
            momentum_weight = min(signal.confidence * 1.5, 1.0)
            position_value = base_position_value * momentum_weight
        else:
            position_value = base_position_value

        # 计算股票数量（向下取整到100股的倍数）
        shares = int(position_value / signal.price / 100) * 100

        return max(shares, 0)

    def get_strategy_summary(self) -> Dict:
        """获取策略摘要"""
        if not self.current_strategy:
            return {}

        return {
            'name': self.current_strategy.name,
            'description': self.current_strategy.description,
            'buy_rules_count': len(self.current_strategy.buy_rules),
            'sell_rules_count': len(self.current_strategy.sell_rules),
            'position_sizing': self.current_strategy.position_sizing,
            'risk_management': self.current_strategy.risk_management,
            'buy_rules': [
                {'name': rule.name, 'weight': rule.weight,
                    'description': rule.description}
                for rule in self.current_strategy.buy_rules
            ],
            'sell_rules': [
                {'name': rule.name, 'weight': rule.weight,
                    'description': rule.description}
                for rule in self.current_strategy.sell_rules
            ]
        }

    def save_strategy(self, strategy_name: str, file_path: str):
        """保存策略到文件"""
        if strategy_name not in self.strategies:
            logger.error(f"策略不存在: {strategy_name}")
            return

        strategy = self.strategies[strategy_name]
        strategy_dict = {
            'name': strategy.name,
            'description': strategy.description,
            'position_sizing': strategy.position_sizing,
            'risk_management': strategy.risk_management,
            'buy_rules': [
                {
                    'name': rule.name,
                    'condition': rule.condition,
                    'weight': rule.weight,
                    'description': rule.description
                }
                for rule in strategy.buy_rules
            ],
            'sell_rules': [
                {
                    'name': rule.name,
                    'condition': rule.condition,
                    'weight': rule.weight,
                    'description': rule.description
                }
                for rule in strategy.sell_rules
            ]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(strategy_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"策略已保存到: {file_path}")

    def load_strategy(self, file_path: str) -> bool:
        """从文件加载策略"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                strategy_dict = json.load(f)

            # 重建策略对象
            buy_rules = [
                TradingRule(
                    name=rule['name'],
                    condition=rule['condition'],
                    weight=rule['weight'],
                    description=rule['description']
                )
                for rule in strategy_dict['buy_rules']
            ]

            sell_rules = [
                TradingRule(
                    name=rule['name'],
                    condition=rule['condition'],
                    weight=rule['weight'],
                    description=rule['description']
                )
                for rule in strategy_dict['sell_rules']
            ]

            strategy = StrategyConfig(
                name=strategy_dict['name'],
                buy_rules=buy_rules,
                sell_rules=sell_rules,
                position_sizing=strategy_dict['position_sizing'],
                risk_management=strategy_dict['risk_management'],
                description=strategy_dict['description']
            )

            # 添加到策略库
            strategy_key = strategy_dict['name'].lower().replace(' ', '_')
            self.strategies[strategy_key] = strategy

            logger.info(f"策略已加载: {strategy.name}")
            return True

        except Exception as e:
            logger.error(f"加载策略失败: {e}")
            return False

    def list_strategies(self) -> List[str]:
        """列出所有可用策略"""
        return list(self.strategies.keys())


if __name__ == "__main__":
    # 测试交易策略
    print("测试量化交易策略模块...")

    strategy_engine = QuantitativeTradingStrategy()

    # 列出所有策略
    strategies = strategy_engine.list_strategies()
    print(f"可用策略: {strategies}")

    # 测试每个策略
    for strategy_name in strategies:
        strategy_engine.set_strategy(strategy_name)
        summary = strategy_engine.get_strategy_summary()

        print(f"\n策略: {summary['name']}")
        print(f"描述: {summary['description']}")
        print(f"买入规则数: {summary['buy_rules_count']}")
        print(f"卖出规则数: {summary['sell_rules_count']}")
        print(f"风险管理: {summary['risk_management']}")

    # 保存策略示例
    strategy_engine.save_strategy(
        'momentum', './config/momentum_strategy.json')

    print("\n测试完成！")
