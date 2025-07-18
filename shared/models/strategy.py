"""
策略相关模型 - 微服务架构共享模型
定义选股策略、交易策略等相关的数据结构
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Optional, Any
from enum import Enum

from .base import SignalType, StrategyType


@dataclass
class SelectionCriteria:
    """选股条件模型"""
    consecutive_days: int = 3                    # 连续交易日数
    min_total_return: float = 0.15              # 最小总收益率
    max_drawdown: float = 0.05                  # 最大回撤
    exclude_limit_up_first_day: bool = True     # 排除首日涨停

    # 价格筛选
    min_stock_price: Optional[float] = None     # 最小股价
    max_stock_price: Optional[float] = None     # 最大股价
    min_market_cap: Optional[float] = None      # 最小市值
    max_market_cap: Optional[float] = None      # 最大市值

    # 成交量筛选
    min_avg_volume: Optional[float] = None      # 最小平均成交额
    min_turnover_rate: Optional[float] = None   # 最小换手率
    max_turnover_rate: Optional[float] = None   # 最大换手率

    # 技术指标
    enable_technical: bool = False              # 启用技术指标
    rsi_min: Optional[float] = None            # RSI下限
    rsi_max: Optional[float] = None            # RSI上限
    require_macd_golden_cross: bool = False     # 要求MACD金叉
    require_ma_bullish: bool = False            # 要求均线多头

    # 基本面筛选
    enable_fundamental: bool = False            # 启用基本面筛选
    min_roe: Optional[float] = None            # 最小ROE
    max_pe_ratio: Optional[float] = None       # 最大PE
    min_revenue_growth: Optional[float] = None  # 最小营收增长率
    max_debt_ratio: Optional[float] = None     # 最大负债率

    # 行业筛选
    excluded_industries: List[str] = field(default_factory=list)  # 排除行业
    included_sectors: List[str] = field(default_factory=list)     # 包含板块
    exclude_new_stocks: bool = True             # 排除新股
    new_stock_days_limit: int = 60             # 新股天数限制


@dataclass
class TradingRule:
    """交易规则模型"""
    name: str                      # 规则名称
    description: str               # 规则描述
    condition: str                 # 条件表达式
    action: SignalType            # 执行动作
    priority: int = 1             # 优先级
    enabled: bool = True          # 是否启用
    weight: float = 1.0           # 规则权重
    parameters: Dict[str, Any] = field(default_factory=dict)  # 规则参数


@dataclass
class StrategyConfig:
    """策略配置模型"""
    name: str                      # 策略名称
    strategy_type: StrategyType    # 策略类型
    description: str               # 策略描述
    version: str = "1.0.0"         # 策略版本
    author: str = ""               # 策略作者
    created_date: str = ""         # 创建日期

    # 规则配置
    buy_rules: List[TradingRule] = field(default_factory=list)   # 买入规则
    sell_rules: List[TradingRule] = field(default_factory=list)  # 卖出规则
    risk_rules: List[TradingRule] = field(default_factory=list)  # 风控规则

    # 策略参数
    parameters: Dict[str, Any] = field(default_factory=dict)     # 策略参数
    position_sizing: str = "equal_weight"                        # 仓位分配方法
    max_positions: int = 5                                        # 最大持仓数量
    position_size_pct: float = 0.20                              # 单只股票仓位比例

    # 风控参数
    stop_loss_pct: float = 0.05                                  # 止损比例
    take_profit_pct: float = 0.10                                # 止盈比例
    max_drawdown_pct: float = 0.15                               # 最大回撤限制

    # 选股条件
    selection_criteria: Optional[SelectionCriteria] = None       # 选股条件

    def add_buy_rule(self, rule: TradingRule):
        """添加买入规则"""
        self.buy_rules.append(rule)

    def add_sell_rule(self, rule: TradingRule):
        """添加卖出规则"""
        self.sell_rules.append(rule)

    def add_risk_rule(self, rule: TradingRule):
        """添加风控规则"""
        self.risk_rules.append(rule)


@dataclass
class StrategyExecution:
    """策略执行记录"""
    strategy_name: str            # 策略名称
    execution_time: str           # 执行时间
    execution_date: date          # 执行日期
    signals_generated: int        # 生成信号数量
    positions_updated: int        # 更新持仓数量
    execution_status: str         # 执行状态
    execution_time_ms: int        # 执行耗时(毫秒)
    error_message: Optional[str] = None  # 错误信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 执行元数据


@dataclass
class StrategyBacktest:
    """策略回测配置"""
    strategy_config: StrategyConfig
    start_date: date
    end_date: date
    initial_capital: float = 1000000
    benchmark: str = "000300.SH"
    commission_rate: float = 0.0003
    stamp_tax_rate: float = 0.001
    slippage_rate: float = 0.001
    rebalance_frequency: str = "daily"
    enable_short_selling: bool = False
    risk_free_rate: float = 0.03


@dataclass
class StrategyOptimization:
    """策略优化配置"""
    strategy_config: StrategyConfig
    parameter_ranges: Dict[str, List[Any]] = field(default_factory=dict)
    optimization_method: str = "grid_search"  # grid_search, bayesian, genetic
    # sharpe_ratio, total_return, max_drawdown
    optimization_metric: str = "sharpe_ratio"
    cv_folds: int = 5
    max_iterations: int = 100
    parallel_jobs: int = -1
    random_state: int = 42


@dataclass
class StrategyValidation:
    """策略验证配置"""
    strategy_config: StrategyConfig
    validation_periods: List[Dict[str, date]] = field(default_factory=list)
    out_of_sample_test: bool = True
    walk_forward_analysis: bool = False
    monte_carlo_simulation: bool = False
    stress_test_scenarios: List[Dict[str, Any]] = field(default_factory=list)
    validation_metrics: List[str] = field(default_factory=lambda: [
        "total_return", "sharpe_ratio", "max_drawdown", "win_rate", "profit_loss_ratio"
    ])
