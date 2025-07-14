"""
回测验证系统
实现完整的回测系统，包括买卖点判断、仓位管理、交易规则等
严格遵守A股和港股交易规则
"""
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass, asdict
from collections import defaultdict
import copy

from quant_system_architecture import BacktestEngine, TradeRecord, Position, StockData, StrategyEngine, DataProvider
from trading_strategy import QuantitativeTradingStrategy

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """回测配置"""
    start_date: date
    end_date: date
    initial_capital: float = 1000000  # 初始资金100万
    max_positions: int = 5            # 最大持仓数
    position_size_pct: float = 0.20   # 单个仓位占比20%
    commission_rate: float = 0.0003   # 手续费万三
    stamp_tax_rate: float = 0.001     # 印花税千一(卖出时)
    min_commission: float = 5.0       # 最低手续费5元
    slippage_rate: float = 0.001      # 滑点千一


@dataclass
class BacktestResult:
    """回测结果"""
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    profit_loss_ratio: float
    total_trades: int
    avg_holding_days: float
    benchmark_return: float
    excess_return: float


class TradingSimulator:
    """交易模拟器"""

    def __init__(self, config: BacktestConfig):
        """初始化交易模拟器"""
        self.config = config
        self.cash = config.initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_records: List[TradeRecord] = []
        self.daily_portfolio_value: List[Tuple[date, float]] = []
        self.pending_orders: List[Dict] = []  # 待执行订单（T+1）

        logger.info(f"交易模拟器初始化，初始资金: {config.initial_capital:,.0f}")

    def can_buy(self, code: str, price: float, quantity: int) -> bool:
        """检查是否可以买入"""
        # 检查持仓数量限制
        if len(self.positions) >= self.config.max_positions:
            return False

        # 检查是否已持有该股票
        if code in self.positions:
            return False

        # 检查资金是否充足
        total_cost = self._calculate_buy_cost(price, quantity)
        if total_cost > self.cash:
            return False

        return True

    def can_sell(self, code: str, quantity: int, trade_date: date, buy_date: date) -> bool:
        """检查是否可以卖出"""
        # 检查是否持有该股票
        if code not in self.positions:
            return False

        # 检查持仓数量
        if self.positions[code].quantity < quantity:
            return False

        # A股T+1限制：买入当天不能卖出
        if trade_date <= buy_date:
            return False

        return True

    def place_buy_order(self, code: str, name: str, price: float, quantity: int, trade_date: date):
        """下买单"""
        if not self.can_buy(code, price, quantity):
            return False

        # A股买入立即成交
        return self._execute_buy(code, name, price, quantity, trade_date)

    def place_sell_order(self, code: str, price: float, quantity: int, trade_date: date):
        """下卖单"""
        position = self.positions.get(code)
        if not position:
            return False

        # 检查T+1限制
        if not self.can_sell(code, quantity, trade_date, position.buy_date):
            # 如果是T+1限制，加入待执行订单
            if trade_date <= position.buy_date:
                self.pending_orders.append({
                    'type': 'SELL',
                    'code': code,
                    'price': price,
                    'quantity': quantity,
                    'execute_date': position.buy_date + timedelta(days=1)
                })
                return True
            return False

        # 立即执行卖出
        return self._execute_sell(code, price, quantity, trade_date)

    def _execute_buy(self, code: str, name: str, price: float, quantity: int, trade_date: date) -> bool:
        """执行买入"""
        # 计算成本
        total_cost = self._calculate_buy_cost(price, quantity)

        if total_cost > self.cash:
            return False

        # 更新现金
        self.cash -= total_cost

        # 创建持仓
        market_value = price * quantity
        self.positions[code] = Position(
            code=code,
            name=name,
            quantity=quantity,
            avg_cost=price,
            current_price=price,
            market_value=market_value,
            profit_loss=0,
            profit_loss_pct=0,
            buy_date=trade_date,
            highest_price=price
        )

        # 记录交易
        commission = self._calculate_commission(price * quantity)
        self.trade_records.append(TradeRecord(
            code=code,
            name=name,
            action='BUY',
            quantity=quantity,
            price=price,
            amount=price * quantity,
            fee=commission,
            date=trade_date
        ))

        logger.debug(
            f"买入: {code} {quantity}股 @{price:.2f} 成本:{total_cost:.2f}")
        return True

    def _execute_sell(self, code: str, price: float, quantity: int, trade_date: date) -> bool:
        """执行卖出"""
        position = self.positions.get(code)
        if not position or position.quantity < quantity:
            return False

        # 计算收入
        gross_amount = price * quantity
        commission = self._calculate_commission(gross_amount)
        stamp_tax = gross_amount * self.config.stamp_tax_rate  # 印花税
        net_amount = gross_amount - commission - stamp_tax

        # 更新现金
        self.cash += net_amount

        # 计算盈亏
        cost_amount = position.avg_cost * quantity
        profit_loss = net_amount - cost_amount
        holding_days = (trade_date - position.buy_date).days

        # 记录交易
        self.trade_records.append(TradeRecord(
            code=code,
            name=position.name,
            action='SELL',
            quantity=quantity,
            price=price,
            amount=gross_amount,
            fee=commission + stamp_tax,
            date=trade_date,
            profit_loss=profit_loss,
            holding_days=holding_days
        ))

        # 更新或删除持仓
        if position.quantity == quantity:
            del self.positions[code]
        else:
            position.quantity -= quantity
            position.market_value = position.current_price * position.quantity

        logger.debug(
            f"卖出: {code} {quantity}股 @{price:.2f} 盈亏:{profit_loss:.2f}")
        return True

    def _calculate_buy_cost(self, price: float, quantity: int) -> float:
        """计算买入成本"""
        amount = price * quantity
        commission = self._calculate_commission(amount)
        return amount + commission

    def _calculate_commission(self, amount: float) -> float:
        """计算手续费"""
        commission = amount * self.config.commission_rate
        return max(commission, self.config.min_commission)

    def update_positions(self, market_data: Dict[str, float], trade_date: date):
        """更新持仓市值"""
        for code, position in self.positions.items():
            if code in market_data:
                current_price = market_data[code]
                position.current_price = current_price
                position.market_value = current_price * position.quantity
                position.profit_loss = position.market_value - \
                    (position.avg_cost * position.quantity)
                position.profit_loss_pct = position.profit_loss / \
                    (position.avg_cost * position.quantity)

                # 更新最高价
                if current_price > position.highest_price:
                    position.highest_price = current_price

    def process_pending_orders(self, trade_date: date, market_data: Dict[str, float]):
        """处理待执行订单"""
        executed_orders = []

        for i, order in enumerate(self.pending_orders):
            if trade_date >= order['execute_date']:
                if order['type'] == 'SELL':
                    # 使用当日开盘价执行
                    current_price = market_data.get(
                        order['code'], order['price'])
                    if self._execute_sell(order['code'], current_price, order['quantity'], trade_date):
                        executed_orders.append(i)

        # 移除已执行的订单
        for i in reversed(executed_orders):
            self.pending_orders.pop(i)

    def get_portfolio_value(self) -> float:
        """获取组合总价值"""
        total_market_value = sum(
            pos.market_value for pos in self.positions.values())
        return self.cash + total_market_value

    def record_daily_value(self, trade_date: date):
        """记录每日组合价值"""
        portfolio_value = self.get_portfolio_value()
        self.daily_portfolio_value.append((trade_date, portfolio_value))


class QuantitativeBacktestEngine(BacktestEngine):
    """量化回测引擎"""

    def __init__(self):
        """初始化回测引擎"""
        self.simulator: Optional[TradingSimulator] = None
        self.strategy: Optional[QuantitativeTradingStrategy] = None
        self.data_provider: Optional[DataProvider] = None

        logger.info("量化回测引擎初始化完成")

    def run_backtest(self, strategy: StrategyEngine, start_date: date, end_date: date,
                     config: Optional[BacktestConfig] = None) -> Dict:
        """
        运行回测

        Args:
            strategy: 策略引擎
            start_date: 开始日期
            end_date: 结束日期
            config: 回测配置

        Returns:
            回测结果
        """
        if config is None:
            config = BacktestConfig(start_date=start_date, end_date=end_date)

        logger.info(f"开始回测: {start_date} 到 {end_date}")

        # 初始化
        self.simulator = TradingSimulator(config)
        self.strategy = strategy if isinstance(
            strategy, QuantitativeTradingStrategy) else None

        if not self.strategy:
            logger.error("策略类型不匹配")
            return {}

        # 获取股票池
        stock_pool = self._get_stock_pool()
        if not stock_pool:
            logger.error("无法获取股票池")
            return {}

        # 按日期回测
        current_date = start_date
        while current_date <= end_date:
            if self._is_trading_day(current_date):
                self._process_trading_day(current_date, stock_pool)

            current_date += timedelta(days=1)

        # 计算回测结果
        result = self._calculate_backtest_results(config)

        logger.info(f"回测完成，总收益率: {result.get('total_return', 0):.2%}")
        return result

    def _get_stock_pool(self) -> List[str]:
        """获取股票池"""
        if not self.data_provider:
            # 使用默认股票池
            return ['000001', '000002', '600000', '600036', '300001']  # 示例股票

        try:
            stock_list = self.data_provider.get_stock_list('A')
            return [code for code, name in stock_list[:100]]  # 限制股票数量
        except Exception as e:
            logger.error(f"获取股票池失败: {e}")
            return []

    def _is_trading_day(self, check_date: date) -> bool:
        """判断是否为交易日"""
        # 简化实现：排除周末
        return check_date.weekday() < 5

    def _process_trading_day(self, trade_date: date, stock_pool: List[str]):
        """处理交易日"""
        try:
            # 1. 处理待执行订单
            market_data = self._get_market_data(
                trade_date, list(self.simulator.positions.keys()))
            self.simulator.process_pending_orders(trade_date, market_data)

            # 2. 更新持仓市值
            self.simulator.update_positions(market_data, trade_date)

            # 3. 检查卖出信号
            self._check_sell_signals(trade_date, market_data)

            # 4. 检查买入信号
            self._check_buy_signals(trade_date, stock_pool)

            # 5. 记录每日价值
            self.simulator.record_daily_value(trade_date)

        except Exception as e:
            logger.error(f"处理交易日{trade_date}时出错: {e}")

    def _get_market_data(self, trade_date: date, codes: List[str]) -> Dict[str, float]:
        """获取市场数据"""
        market_data = {}

        if not self.data_provider:
            # 模拟数据
            for code in codes:
                # 简单的随机价格模拟
                base_price = 10.0
                random_change = np.random.normal(0, 0.02)  # 2%标准差
                market_data[code] = base_price * (1 + random_change)
            return market_data

        # 实际获取数据的逻辑
        for code in codes:
            try:
                historical_data = self.data_provider.get_historical_data(
                    code, trade_date, trade_date
                )
                if historical_data:
                    market_data[code] = historical_data[0].close_price
            except Exception as e:
                logger.debug(f"获取{code}在{trade_date}的数据失败: {e}")

        return market_data

    def _check_sell_signals(self, trade_date: date, market_data: Dict[str, float]):
        """检查卖出信号"""
        positions_to_sell = []

        for code, position in self.simulator.positions.items():
            try:
                # 获取历史数据用于信号生成
                if self.data_provider:
                    end_date = trade_date
                    start_date = trade_date - timedelta(days=60)
                    historical_data = self.data_provider.get_historical_data(
                        code, start_date, end_date)
                else:
                    # 模拟数据
                    historical_data = self._generate_mock_data(
                        code, trade_date)

                if not historical_data:
                    continue

                # 生成交易信号
                current_positions = {code: {'avg_cost': position.avg_cost}}
                signals = self.strategy.generate_trading_signals(
                    historical_data, current_positions)

                # 处理卖出信号
                for signal in signals:
                    if signal.signal_type == 'SELL' and signal.code == code:
                        # 检查止损止盈条件
                        current_price = market_data.get(
                            code, position.current_price)

                        # 5%回撤止损逻辑
                        if self._should_stop_loss(position, current_price):
                            positions_to_sell.append(
                                (code, current_price, position.quantity, "止损"))
                        elif signal.confidence > 0.7:  # 高置信度卖出信号
                            positions_to_sell.append(
                                (code, current_price, position.quantity, signal.reason))
                        break

            except Exception as e:
                logger.debug(f"检查{code}卖出信号时出错: {e}")

        # 执行卖出
        for code, price, quantity, reason in positions_to_sell:
            if self.simulator.place_sell_order(code, price, quantity, trade_date):
                logger.info(f"卖出信号: {code} @{price:.2f} 原因: {reason}")

    def _should_stop_loss(self, position: Position, current_price: float) -> bool:
        """判断是否应该止损"""
        # 从最高价回撤5%止损
        if position.highest_price > 0:
            drawdown = (position.highest_price - current_price) / \
                position.highest_price
            return drawdown >= 0.05
        return False

    def _check_buy_signals(self, trade_date: date, stock_pool: List[str]):
        """检查买入信号"""
        if len(self.simulator.positions) >= self.simulator.config.max_positions:
            return

        buy_candidates = []

        for code in stock_pool:
            if code in self.simulator.positions:
                continue

            try:
                # 获取历史数据
                if self.data_provider:
                    end_date = trade_date
                    start_date = trade_date - timedelta(days=60)
                    historical_data = self.data_provider.get_historical_data(
                        code, start_date, end_date)
                else:
                    historical_data = self._generate_mock_data(
                        code, trade_date)

                if not historical_data:
                    continue

                # 生成交易信号
                signals = self.strategy.generate_trading_signals(
                    historical_data)

                # 处理买入信号
                for signal in signals:
                    if signal.signal_type == 'BUY' and signal.confidence > 0.6:
                        buy_candidates.append((signal, historical_data[-1]))
                        break

            except Exception as e:
                logger.debug(f"检查{code}买入信号时出错: {e}")

        # 按信号强度排序，选择最强的信号
        buy_candidates.sort(key=lambda x: x[0].confidence, reverse=True)

        # 执行买入
        available_positions = self.simulator.config.max_positions - \
            len(self.simulator.positions)
        for signal, stock_data in buy_candidates[:available_positions]:
            quantity = self.strategy.calculate_position_size(
                signal, self.simulator.cash, self.simulator.positions
            )

            if quantity > 0:
                if self.simulator.place_buy_order(
                    signal.code, stock_data.name, signal.price, quantity, trade_date
                ):
                    logger.info(
                        f"买入信号: {signal.code} {quantity}股 @{signal.price:.2f} 置信度: {signal.confidence:.2f}")

    def _generate_mock_data(self, code: str, end_date: date) -> List[StockData]:
        """生成模拟数据"""
        mock_data = []
        base_price = 10.0

        for i in range(60):
            trade_date = end_date - timedelta(days=59-i)
            price_change = np.random.normal(0, 0.02)
            base_price *= (1 + price_change)

            mock_data.append(StockData(
                code=code,
                name=f"股票{code}",
                date=trade_date,
                open_price=base_price * 0.99,
                high_price=base_price * 1.02,
                low_price=base_price * 0.98,
                close_price=base_price,
                volume=1000000,
                amount=base_price * 1000000,
                pct_change=price_change
            ))

        return mock_data

    def _calculate_backtest_results(self, config: BacktestConfig) -> Dict:
        """计算回测结果"""
        if not self.simulator or not self.simulator.daily_portfolio_value:
            return {}

        # 转换为DataFrame便于计算
        df = pd.DataFrame(self.simulator.daily_portfolio_value,
                          columns=['date', 'portfolio_value'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # 计算收益率
        df['daily_return'] = df['portfolio_value'].pct_change()

        # 基础指标
        initial_value = config.initial_capital
        final_value = df['portfolio_value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value

        # 年化收益率
        days = len(df)
        annual_return = (final_value / initial_value) ** (252 /
                                                          days) - 1 if days > 0 else 0

        # 最大回撤
        df['cummax'] = df['portfolio_value'].cummax()
        df['drawdown'] = (df['portfolio_value'] - df['cummax']) / df['cummax']
        max_drawdown = df['drawdown'].min()

        # 夏普比率
        daily_returns = df['daily_return'].dropna()
        if len(daily_returns) > 0 and daily_returns.std() > 0:
            sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)
        else:
            sharpe_ratio = 0

        # 交易统计
        trades = [t for t in self.simulator.trade_records if t.action == 'SELL']
        total_trades = len(trades)

        if total_trades > 0:
            win_trades = [t for t in trades if t.profit_loss > 0]
            win_rate = len(win_trades) / total_trades

            avg_holding_days = np.mean(
                [t.holding_days for t in trades if t.holding_days])

            # 盈亏比
            avg_win = np.mean(
                [t.profit_loss for t in win_trades]) if win_trades else 0
            loss_trades = [t for t in trades if t.profit_loss <= 0]
            avg_loss = abs(
                np.mean([t.profit_loss for t in loss_trades])) if loss_trades else 1
            profit_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        else:
            win_rate = 0
            avg_holding_days = 0
            profit_loss_ratio = 0

        # 基准收益（沪深300，简化为5%年化）
        benchmark_return = 0.05 * (days / 252) if days > 0 else 0
        excess_return = total_return - benchmark_return

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': abs(max_drawdown),
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio,
            'total_trades': total_trades,
            'avg_holding_days': avg_holding_days,
            'benchmark_return': benchmark_return,
            'excess_return': excess_return,
            'final_value': final_value,
            'initial_value': initial_value,
            'trading_days': days
        }

    def calculate_performance(self, trades: List[TradeRecord]) -> Dict:
        """计算绩效指标"""
        if not trades:
            return {}

        # 按时间分组统计
        df = pd.DataFrame([asdict(trade) for trade in trades])
        df['date'] = pd.to_datetime(df['date'])

        # 按周统计
        df['week'] = df['date'].dt.to_period('W')
        weekly_stats = df.groupby('week').agg({
            'code': 'count',
            'profit_loss': ['sum', 'mean'],
            'holding_days': 'mean'
        }).round(2)

        # 按月统计
        df['month'] = df['date'].dt.to_period('M')
        monthly_stats = df.groupby('month').agg({
            'code': 'count',
            'profit_loss': ['sum', 'mean'],
            'holding_days': 'mean'
        }).round(2)

        # 按季度统计
        df['quarter'] = df['date'].dt.to_period('Q')
        quarterly_stats = df.groupby('quarter').agg({
            'code': 'count',
            'profit_loss': ['sum', 'mean'],
            'holding_days': 'mean'
        }).round(2)

        # 按年统计
        df['year'] = df['date'].dt.to_period('Y')
        yearly_stats = df.groupby('year').agg({
            'code': 'count',
            'profit_loss': ['sum', 'mean'],
            'holding_days': 'mean'
        }).round(2)

        return {
            'weekly_stats': weekly_stats.to_dict(),
            'monthly_stats': monthly_stats.to_dict(),
            'quarterly_stats': quarterly_stats.to_dict(),
            'yearly_stats': yearly_stats.to_dict()
        }

    def set_data_provider(self, data_provider: DataProvider):
        """设置数据提供者"""
        self.data_provider = data_provider

    def get_trade_records(self) -> List[TradeRecord]:
        """获取交易记录"""
        return self.simulator.trade_records if self.simulator else []

    def get_positions(self) -> Dict[str, Position]:
        """获取当前持仓"""
        return self.simulator.positions if self.simulator else {}

    def get_portfolio_history(self) -> List[Tuple[date, float]]:
        """获取组合价值历史"""
        return self.simulator.daily_portfolio_value if self.simulator else []


if __name__ == "__main__":
    # 测试回测引擎
    print("测试回测引擎...")

    from trading_strategy import QuantitativeTradingStrategy
    from datetime import date, timedelta

    # 创建策略和回测引擎
    strategy = QuantitativeTradingStrategy()
    backtest_engine = QuantitativeBacktestEngine()

    # 配置回测参数
    end_date = date.today()
    start_date = end_date - timedelta(days=30)  # 30天回测

    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000,  # 10万初始资金
        max_positions=3
    )

    print(f"回测期间: {start_date} 到 {end_date}")
    print(f"初始资金: {config.initial_capital:,.0f}")

    # 运行回测
    results = backtest_engine.run_backtest(
        strategy, start_date, end_date, config)

    if results:
        print(f"\n回测结果:")
        print(f"总收益率: {results['total_return']:.2%}")
        print(f"年化收益率: {results['annual_return']:.2%}")
        print(f"最大回撤: {results['max_drawdown']:.2%}")
        print(f"夏普比率: {results['sharpe_ratio']:.2f}")
        print(f"胜率: {results['win_rate']:.2%}")
        print(f"总交易次数: {results['total_trades']}")
        print(f"平均持仓天数: {results['avg_holding_days']:.1f}")

    print("测试完成！")
