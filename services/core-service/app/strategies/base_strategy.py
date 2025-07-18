"""
量化交易策略制定模块 - 微服务版本
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

# 导入微服务架构的共享模型
from shared.models.market_data import StockData
from shared.models.base import TradingSignal

# 导入特征提取器
from app.processors.feature_calculator import QuantitativeFeatureExtractor

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
                TradingRule("RSI超卖反弹", "rsi_14 > 30 and rsi_14 < 70",
                            0.10, "RSI在合理区间")
            ],
            sell_rules=[
                TradingRule("止盈", "profit_pct >= 0.05", 1.0, "盈利达到5%止盈"),
                TradingRule("止损", "profit_pct <= -0.03", 1.0, "亏损达到3%止损"),
                TradingRule("技术破位", "ma5_ratio < -0.02", 0.8, "跌破5日线"),
                TradingRule("成交量萎缩", "volume_ratio_5d < 0.5", 0.6, "成交量严重萎缩"),
                TradingRule("RSI超买", "rsi_14 > 80", 0.7, "RSI超买")
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
                TradingRule("RSI超卖", "rsi_14 < 30", 0.20, "RSI超卖"),
                TradingRule("成交量放大", "volume_ratio_5d > 1.2", 0.15, "成交量放大确认"),
                TradingRule("支撑位确认", "price_position < 0.3", 0.10, "价格在低位区间")
            ],
            sell_rules=[
                TradingRule("均值回归", "bb_position > 0.8", 0.8, "价格回归至布林带上轨"),
                TradingRule("RSI超买", "rsi_14 > 70", 0.7, "RSI超买"),
                TradingRule("止损", "profit_pct <= -0.05", 1.0, "亏损达到5%止损"),
                TradingRule(
                    "反弹乏力", "momentum_3d < 0.02 and rsi_14 > 50", 0.6, "反弹乏力")
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
                TradingRule("ATR扩张", "atr_20d > 0.03", 0.05, "真实波动率扩张")
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
        if not self.current_strategy:
            return None

        total_score = 0
        total_weight = 0
        triggered_rules = []

        for rule in self.current_strategy.buy_rules:
            if self._evaluate_condition(rule.condition, features):
                total_score += rule.weight
                triggered_rules.append(rule.name)
            total_weight += rule.weight

        if total_weight > 0 and total_score / total_weight >= 0.6:  # 至少60%的规则满足
            signal = TradingSignal(
                code=code,
                signal_type="BUY",
                price=price,
                confidence=total_score / total_weight,
                timestamp=datetime.now(),
                strategy_name=self.current_strategy.name,
                triggered_rules=triggered_rules
            )
            return signal

        return None

    def _evaluate_sell_rules(self, features: Dict[str, float], position: Dict,
                             code: str, current_price: float) -> Optional[TradingSignal]:
        """评估卖出规则"""
        if not self.current_strategy:
            return None

        # 计算当前盈亏
        entry_price = position.get('entry_price', current_price)
        profit_pct = (current_price - entry_price) / entry_price
        features['profit_pct'] = profit_pct

        total_score = 0
        total_weight = 0
        triggered_rules = []

        for rule in self.current_strategy.sell_rules:
            if self._evaluate_condition(rule.condition, features):
                total_score += rule.weight
                triggered_rules.append(rule.name)
            total_weight += rule.weight

        if total_weight > 0 and total_score / total_weight >= 0.5:  # 至少50%的规则满足
            signal = TradingSignal(
                code=code,
                signal_type="SELL",
                price=current_price,
                confidence=total_score / total_weight,
                timestamp=datetime.now(),
                strategy_name=self.current_strategy.name,
                triggered_rules=triggered_rules,
                profit_pct=profit_pct
            )
            return signal

        return None

    def _evaluate_condition(self, condition: str, features: Dict[str, float]) -> bool:
        """评估条件表达式"""
        try:
            # 创建安全的评估环境
            safe_dict = {k: v for k, v in features.items()
                         if isinstance(v, (int, float))}

            # 添加一些常用的数学函数
            safe_dict.update({
                'abs': abs,
                'min': min,
                'max': max,
                'sum': sum,
                'len': len
            })

            # 评估条件
            result = eval(condition, {"__builtins__": {}}, safe_dict)
            return bool(result)
        except Exception as e:
            logger.debug(f"条件评估失败: {condition}, 错误: {e}")
            return False

    def calculate_position_size(self, signal: TradingSignal, available_capital: float,
                                current_positions: Dict) -> int:
        """计算仓位大小"""
        if not self.current_strategy:
            return 0

        risk_config = self.current_strategy.risk_management
        max_position_pct = risk_config.get("max_position_pct", 0.20)
        max_positions = risk_config.get("max_positions", 5)
        sizing_method = self.current_strategy.position_sizing

        # 检查持仓数量限制
        if len(current_positions) >= max_positions:
            return 0

        # 根据策略计算仓位
        if sizing_method == "equal_weight":
            position_value = available_capital * max_position_pct
        elif sizing_method == "momentum_weighted":
            # 根据动量强度调整仓位
            momentum_adjustment = min(signal.confidence * 2, 1.5)
            position_value = available_capital * max_position_pct * momentum_adjustment
        elif sizing_method == "volatility_adjusted":
            # 根据波动率调整仓位
            volatility = signal.confidence  # 简化处理
            volatility_adjustment = max(0.5, 1 - volatility)
            position_value = available_capital * max_position_pct * volatility_adjustment
        else:
            position_value = available_capital * max_position_pct

        # 计算股票数量（向下取整到100股的倍数）
        shares = int(position_value / signal.price / 100) * 100
        return max(shares, 0)

    def get_strategy_summary(self) -> Dict:
        """获取策略摘要"""
        if not self.current_strategy:
            return {}

        return {
            "name": self.current_strategy.name,
            "description": self.current_strategy.description,
            "position_sizing": self.current_strategy.position_sizing,
            "risk_management": self.current_strategy.risk_management,
            "buy_rules_count": len(self.current_strategy.buy_rules),
            "sell_rules_count": len(self.current_strategy.sell_rules),
            "available_strategies": list(self.strategies.keys())
        }

    def save_strategy(self, strategy_name: str, file_path: str):
        """保存策略配置"""
        if strategy_name not in self.strategies:
            logger.error(f"策略不存在: {strategy_name}")
            return

        strategy = self.strategies[strategy_name]

        # 转换为可序列化的格式
        strategy_data = {
            "name": strategy.name,
            "description": strategy.description,
            "position_sizing": strategy.position_sizing,
            "risk_management": strategy.risk_management,
            "buy_rules": [
                {
                    "name": rule.name,
                    "condition": rule.condition,
                    "weight": rule.weight,
                    "description": rule.description
                }
                for rule in strategy.buy_rules
            ],
            "sell_rules": [
                {
                    "name": rule.name,
                    "condition": rule.condition,
                    "weight": rule.weight,
                    "description": rule.description
                }
                for rule in strategy.sell_rules
            ]
        }

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(strategy_data, f, ensure_ascii=False, indent=2)
            logger.info(f"策略已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存策略失败: {e}")

    def load_strategy(self, file_path: str) -> bool:
        """加载策略配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                strategy_data = json.load(f)

            # 重建策略对象
            buy_rules = [
                TradingRule(
                    name=rule["name"],
                    condition=rule["condition"],
                    weight=rule["weight"],
                    description=rule["description"]
                )
                for rule in strategy_data["buy_rules"]
            ]

            sell_rules = [
                TradingRule(
                    name=rule["name"],
                    condition=rule["condition"],
                    weight=rule["weight"],
                    description=rule["description"]
                )
                for rule in strategy_data["sell_rules"]
            ]

            strategy = StrategyConfig(
                name=strategy_data["name"],
                description=strategy_data["description"],
                position_sizing=strategy_data["position_sizing"],
                risk_management=strategy_data["risk_management"],
                buy_rules=buy_rules,
                sell_rules=sell_rules
            )

            # 注册策略
            self.strategies[strategy.name] = strategy
            logger.info(f"策略已从 {file_path} 加载")
            return True

        except Exception as e:
            logger.error(f"加载策略失败: {e}")
            return False

    def list_strategies(self) -> List[str]:
        """列出所有可用策略"""
        return list(self.strategies.keys())

    def get_strategy_config(self, strategy_name: str) -> Optional[Dict]:
        """获取策略配置"""
        if strategy_name not in self.strategies:
            return None

        strategy = self.strategies[strategy_name]
        return {
            "name": strategy.name,
            "description": strategy.description,
            "position_sizing": strategy.position_sizing,
            "risk_management": strategy.risk_management,
            "buy_rules": [
                {
                    "name": rule.name,
                    "condition": rule.condition,
                    "weight": rule.weight,
                    "description": rule.description
                }
                for rule in strategy.buy_rules
            ],
            "sell_rules": [
                {
                    "name": rule.name,
                    "condition": rule.condition,
                    "weight": rule.weight,
                    "description": rule.description
                }
                for rule in strategy.sell_rules
            ]
        }
