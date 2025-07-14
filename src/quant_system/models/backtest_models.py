"""
回测相关数据模型

定义回测配置、交易记录、绩效分析等相关的数据结构
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum


class OrderType(Enum):
    """订单类型枚举"""
    MARKET = "market"              # 市价单
    LIMIT = "limit"                # 限价单
    STOP = "stop"                  # 止损单
    STOP_LIMIT = "stop_limit"      # 止损限价单


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"            # 待成交
    FILLED = "filled"              # 已成交
    CANCELLED = "cancelled"        # 已取消
    REJECTED = "rejected"          # 已拒绝


class TradeAction(Enum):
    """交易动作枚举"""
    BUY = "buy"                    # 买入
    SELL = "sell"                  # 卖出


@dataclass
class BacktestConfig:
    """回测配置模型"""
    start_date: date               # 回测开始日期
    end_date: date                 # 回测结束日期
    initial_capital: float         # 初始资金
    max_positions: int = 5         # 最大持仓数量
    position_size_pct: float = 0.20  # 单只股票仓位比例
    commission_rate: float = 0.0003  # 手续费率
    stamp_tax_rate: float = 0.001    # 印花税率(卖出时)
    slippage_rate: float = 0.001     # 滑点率
    stop_loss_pct: float = 0.05      # 止损比例
    benchmark: str = "000300.SH"     # 基准指数

    def __post_init__(self):
        """验证配置参数"""
        if self.start_date >= self.end_date:
            raise ValueError("开始日期必须早于结束日期")
        if self.initial_capital <= 0:
            raise ValueError("初始资金必须大于0")
        if not (0 < self.position_size_pct <= 1):
            raise ValueError("仓位比例必须在0-1之间")


@dataclass
class Order:
    """订单模型"""
    order_id: str                  # 订单ID
    stock_code: str                # 股票代码
    action: TradeAction            # 交易动作
    order_type: OrderType          # 订单类型
    quantity: int                  # 数量
    price: float                   # 价格
    order_time: datetime           # 下单时间
    status: OrderStatus = OrderStatus.PENDING  # 订单状态
    filled_quantity: int = 0       # 已成交数量
    filled_price: float = 0.0      # 成交价格
    fill_time: Optional[datetime] = None  # 成交时间
    commission: float = 0.0        # 手续费
    reason: str = ""               # 下单原因


@dataclass
class TradeRecord:
    """交易记录模型"""
    trade_id: str                  # 交易ID
    stock_code: str                # 股票代码
    stock_name: str                # 股票名称
    action: TradeAction            # 交易动作
    quantity: int                  # 交易数量
    price: float                   # 交易价格
    amount: float                  # 交易金额
    commission: float              # 手续费
    date: date                     # 交易日期
    time: datetime                 # 交易时间
    stamp_tax: float = 0.0         # 印花税
    profit_loss: Optional[float] = None     # 盈亏金额
    profit_loss_pct: Optional[float] = None  # 盈亏比例
    holding_days: Optional[int] = None      # 持仓天数
    reason: str = ""               # 交易原因
    strategy_name: str = ""        # 策略名称


@dataclass
class DailyPerformance:
    """日度绩效模型"""
    date: date                     # 日期
    portfolio_value: float         # 组合价值
    cash: float                    # 现金
    market_value: float            # 持仓市值
    daily_return: float            # 日收益率
    cumulative_return: float       # 累计收益率
    drawdown: float                # 回撤
    benchmark_return: float = 0.0  # 基准日收益率
    positions_count: int = 0       # 持仓数量
    turnover: float = 0.0          # 换手率


@dataclass
class BacktestResult:
    """回测结果模型"""
    config: BacktestConfig         # 回测配置
    start_date: date              # 实际开始日期
    end_date: date                # 实际结束日期
    initial_capital: float        # 初始资金
    final_capital: float          # 最终资金
    total_return: float           # 总收益率
    annual_return: float          # 年化收益率
    max_drawdown: float           # 最大回撤
    sharpe_ratio: float           # 夏普比率
    sortino_ratio: float          # 索提诺比率
    calmar_ratio: float           # 卡玛比率
    win_rate: float               # 胜率
    profit_loss_ratio: float      # 盈亏比
    total_trades: int             # 总交易次数
    avg_holding_days: float       # 平均持仓天数
    turnover_rate: float          # 换手率
    benchmark_return: float       # 基准收益率
    excess_return: float          # 超额收益
    tracking_error: float         # 跟踪误差
    information_ratio: float      # 信息比率
    volatility: float             # 波动率
    downside_volatility: float    # 下行波动率

    # 详细记录
    trade_records: List[TradeRecord] = field(default_factory=list)
    daily_performance: List[DailyPerformance] = field(default_factory=list)
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    yearly_returns: Dict[str, float] = field(default_factory=dict)

    def calculate_metrics(self):
        """计算绩效指标"""
        if not self.daily_performance:
            return

        import numpy as np

        # 提取日收益率
        daily_returns = [dp.daily_return for dp in self.daily_performance]
        benchmark_returns = [
            dp.benchmark_return for dp in self.daily_performance]

        # 基础指标
        self.total_return = (self.final_capital -
                             self.initial_capital) / self.initial_capital
        trading_days = len(daily_returns)
        self.annual_return = (
            1 + self.total_return) ** (252 / trading_days) - 1 if trading_days > 0 else 0

        # 波动率
        self.volatility = np.std(daily_returns) * \
            np.sqrt(252) if daily_returns else 0

        # 下行波动率
        negative_returns = [r for r in daily_returns if r < 0]
        self.downside_volatility = np.std(
            negative_returns) * np.sqrt(252) if negative_returns else 0

        # 夏普比率 (假设无风险利率3%)
        risk_free_rate = 0.03
        excess_daily_return = np.mean(daily_returns) - risk_free_rate / 252
        self.sharpe_ratio = excess_daily_return / \
            (self.volatility / np.sqrt(252)) if self.volatility > 0 else 0

        # 索提诺比率
        self.sortino_ratio = excess_daily_return / \
            (self.downside_volatility / np.sqrt(252)
             ) if self.downside_volatility > 0 else 0

        # 最大回撤
        portfolio_values = [
            dp.portfolio_value for dp in self.daily_performance]
        running_max = np.maximum.accumulate(portfolio_values)
        drawdowns = (np.array(portfolio_values) - running_max) / running_max
        self.max_drawdown = abs(drawdowns.min()) if len(drawdowns) > 0 else 0

        # 卡玛比率
        self.calmar_ratio = self.annual_return / \
            self.max_drawdown if self.max_drawdown > 0 else 0

        # 基准对比
        if benchmark_returns:
            self.benchmark_return = (
                1 + np.array(benchmark_returns)).prod() - 1
            self.excess_return = self.total_return - self.benchmark_return

            # 跟踪误差
            excess_returns = np.array(
                daily_returns) - np.array(benchmark_returns)
            self.tracking_error = np.std(excess_returns) * np.sqrt(252)

            # 信息比率
            self.information_ratio = np.mean(excess_returns) / np.std(
                excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0

        # 交易统计
        if self.trade_records:
            sell_trades = [t for t in self.trade_records if t.action ==
                           TradeAction.SELL and t.profit_loss is not None]

            if sell_trades:
                win_trades = [t for t in sell_trades if t.profit_loss > 0]
                self.win_rate = len(win_trades) / len(sell_trades)

                avg_win = np.mean(
                    [t.profit_loss for t in win_trades]) if win_trades else 0
                loss_trades = [t for t in sell_trades if t.profit_loss <= 0]
                avg_loss = abs(
                    np.mean([t.profit_loss for t in loss_trades])) if loss_trades else 1
                self.profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0

                self.avg_holding_days = np.mean(
                    [t.holding_days for t in sell_trades if t.holding_days])

            self.total_trades = len(self.trade_records)


@dataclass
class RiskMetrics:
    """风险指标模型"""
    var_95: float                  # 95% VaR
    var_99: float                  # 99% VaR
    cvar_95: float                 # 95% CVaR
    cvar_99: float                 # 99% CVaR
    max_consecutive_losses: int    # 最大连续亏损次数
    max_consecutive_loss_days: int  # 最大连续亏损天数
    max_single_loss: float         # 最大单次亏损
    max_single_loss_pct: float     # 最大单次亏损比例

    @classmethod
    def calculate_from_returns(cls, returns: List[float]) -> 'RiskMetrics':
        """从收益率序列计算风险指标"""
        import numpy as np

        if not returns:
            return cls(0, 0, 0, 0, 0, 0, 0, 0)

        returns_array = np.array(returns)

        # VaR计算
        var_95 = np.percentile(returns_array, 5)
        var_99 = np.percentile(returns_array, 1)

        # CVaR计算
        cvar_95 = np.mean(returns_array[returns_array <= var_95])
        cvar_99 = np.mean(returns_array[returns_array <= var_99])

        # 连续亏损统计
        consecutive_losses = 0
        max_consecutive_losses = 0
        consecutive_loss_days = 0
        max_consecutive_loss_days = 0

        for ret in returns:
            if ret < 0:
                consecutive_losses += 1
                consecutive_loss_days += 1
                max_consecutive_losses = max(
                    max_consecutive_losses, consecutive_losses)
                max_consecutive_loss_days = max(
                    max_consecutive_loss_days, consecutive_loss_days)
            else:
                consecutive_losses = 0
                consecutive_loss_days = 0

        # 最大单次亏损
        negative_returns = [r for r in returns if r < 0]
        max_single_loss = min(negative_returns) if negative_returns else 0
        max_single_loss_pct = abs(max_single_loss)

        return cls(
            var_95=abs(var_95),
            var_99=abs(var_99),
            cvar_95=abs(cvar_95),
            cvar_99=abs(cvar_99),
            max_consecutive_losses=max_consecutive_losses,
            max_consecutive_loss_days=max_consecutive_loss_days,
            max_single_loss=abs(max_single_loss),
            max_single_loss_pct=max_single_loss_pct
        )
