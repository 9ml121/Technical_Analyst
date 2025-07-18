"""
共享模型包 - 微服务架构
导出所有共享的数据模型和类型
"""

# 从market_data模块导入
from .market_data import (
    StockData,
    StockInfo,
    MarketIndex,
    TradingSession,
    StockDataValidator,
    StockDataProcessor
)

# 从base模块导入核心模型
from .base import (
    # 枚举类型
    SignalType,
    TradeAction,
    OrderType,
    OrderStatus,
    StrategyType,

    # 核心数据模型
    TradingSignal,
    Position,
    TradeRecord,
    Order,
    Portfolio,

    # 策略相关模型
    TradingRule,
    TradingStrategy,

    # 回测相关模型
    BacktestConfig,
    DailyPerformance,
    BacktestResult,
    StrategyPerformance,
    RiskMetrics
)

# 从strategy模块导入策略配置模型
from .strategy import (
    SelectionCriteria,
    TradingRule as StrategyTradingRule,
    StrategyConfig,
    StrategyExecution,
    StrategyBacktest,
    StrategyOptimization,
    StrategyValidation
)

# 从ml_strategy模块导入ML策略模型
from .ml_strategy import (
    # 枚举类型
    ModelType,
    FeatureSelectionMethod,
    PositionSizingMethod,

    # 配置模型
    ModelConfig,
    RiskManagementConfig,
    MLStrategyConfig,

    # 性能和数据模型
    ModelPerformance,
    MLPrediction,
    MLSignal,
    TrainingDataConfig,
    ModelMetadata
)

__all__ = [
    # 市场数据模型
    'StockData',
    'StockInfo',
    'MarketIndex',
    'TradingSession',
    'StockDataValidator',
    'StockDataProcessor',

    # 枚举类型
    'SignalType',
    'TradeAction',
    'OrderType',
    'OrderStatus',
    'StrategyType',
    'ModelType',
    'FeatureSelectionMethod',
    'PositionSizingMethod',

    # 核心数据模型
    'TradingSignal',
    'Position',
    'TradeRecord',
    'Order',
    'Portfolio',

    # 策略相关模型
    'TradingRule',
    'TradingStrategy',
    'SelectionCriteria',
    'StrategyTradingRule',
    'StrategyConfig',
    'StrategyExecution',
    'StrategyBacktest',
    'StrategyOptimization',
    'StrategyValidation',

    # 回测相关模型
    'BacktestConfig',
    'DailyPerformance',
    'BacktestResult',
    'StrategyPerformance',
    'RiskMetrics',

    # ML策略相关模型
    'ModelConfig',
    'RiskManagementConfig',
    'MLStrategyConfig',
    'ModelPerformance',
    'MLPrediction',
    'MLSignal',
    'TrainingDataConfig',
    'ModelMetadata'
]
