#!/usr/bin/env python3
"""
实盘模拟测试

模拟真实的交易环境，测试机器学习策略在实盘条件下的表现：
1. 模拟真实交易延迟和滑点
2. 考虑交易成本和手续费
3. 实时信号生成和仓位管理
4. 风险控制和资金管理
"""

import sys
from pathlib import Path
from datetime import date, timedelta, datetime
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
import random

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PaperTradingSimulator:
    """实盘模拟交易器"""

    def __init__(self, initial_capital: float = 1000000):
        """初始化模拟交易器"""
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}  # 当前持仓
        self.trade_history = []  # 交易历史
        self.daily_pnl = []  # 每日盈亏
        self.portfolio_values = []  # 组合价值历史

        # 交易成本设置
        self.commission_rate = 0.0003  # 手续费率 0.03%
        self.slippage_rate = 0.0005    # 滑点率 0.05%
        self.min_trade_amount = 100    # 最小交易金额

        # 风险控制
        self.max_position_pct = 0.15   # 单只股票最大仓位
        self.max_positions = 10        # 最大持仓数量
        self.stop_loss_pct = 0.06      # 止损比例
        self.take_profit_pct = 0.15    # 止盈比例

        print(f"💰 初始化模拟交易器，初始资金: ¥{initial_capital:,.2f}")

    def calculate_trade_cost(self, trade_amount: float) -> float:
        """计算交易成本"""
        commission = trade_amount * self.commission_rate
        slippage = trade_amount * self.slippage_rate
        return commission + slippage

    def execute_buy_order(self, stock_code: str, price: float, quantity: int, timestamp: datetime) -> bool:
        """执行买入订单"""
        trade_amount = price * quantity
        trade_cost = self.calculate_trade_cost(trade_amount)
        total_cost = trade_amount + trade_cost

        if total_cost > self.current_capital:
            print(f"❌ 资金不足，无法买入 {stock_code}")
            return False

        # 更新资金
        self.current_capital -= total_cost

        # 更新持仓
        if stock_code in self.positions:
            # 已有持仓，计算新的平均成本
            old_quantity = self.positions[stock_code]['quantity']
            old_avg_cost = self.positions[stock_code]['avg_cost']
            new_quantity = old_quantity + quantity
            new_avg_cost = (old_quantity * old_avg_cost +
                            quantity * price) / new_quantity

            self.positions[stock_code].update({
                'quantity': new_quantity,
                'avg_cost': new_avg_cost,
                'last_update': timestamp
            })
        else:
            # 新建持仓
            self.positions[stock_code] = {
                'quantity': quantity,
                'avg_cost': price,
                'buy_date': timestamp,
                'last_update': timestamp
            }

        # 记录交易
        trade_record = {
            'timestamp': timestamp,
            'stock_code': stock_code,
            'action': 'BUY',
            'price': price,
            'quantity': quantity,
            'amount': trade_amount,
            'cost': trade_cost,
            'total_cost': total_cost
        }
        self.trade_history.append(trade_record)

        print(
            f"✅ 买入 {stock_code}: {quantity}股 @ ¥{price:.2f}, 成本: ¥{trade_cost:.2f}")
        return True

    def execute_sell_order(self, stock_code: str, price: float, quantity: int, timestamp: datetime) -> bool:
        """执行卖出订单"""
        if stock_code not in self.positions:
            print(f"❌ 无持仓，无法卖出 {stock_code}")
            return False

        position = self.positions[stock_code]
        if quantity > position['quantity']:
            print(f"❌ 持仓不足，无法卖出 {stock_code}")
            return False

        trade_amount = price * quantity
        trade_cost = self.calculate_trade_cost(trade_amount)
        net_amount = trade_amount - trade_cost

        # 更新资金
        self.current_capital += net_amount

        # 更新持仓
        remaining_quantity = position['quantity'] - quantity
        if remaining_quantity == 0:
            # 全部卖出，删除持仓
            del self.positions[stock_code]
        else:
            # 部分卖出，更新持仓
            position['quantity'] = remaining_quantity
            position['last_update'] = timestamp

        # 记录交易
        trade_record = {
            'timestamp': timestamp,
            'stock_code': stock_code,
            'action': 'SELL',
            'price': price,
            'quantity': quantity,
            'amount': trade_amount,
            'cost': trade_cost,
            'net_amount': net_amount
        }
        self.trade_history.append(trade_record)

        # 计算盈亏
        profit = (price - position['avg_cost']) * quantity - trade_cost
        profit_pct = (price - position['avg_cost']) / position['avg_cost']

        print(
            f"✅ 卖出 {stock_code}: {quantity}股 @ ¥{price:.2f}, 盈亏: ¥{profit:.2f} ({profit_pct:.2%})")
        return True

    def update_portfolio_value(self, current_prices: Dict[str, float], timestamp: datetime):
        """更新组合价值"""
        total_position_value = 0

        for stock_code, position in self.positions.items():
            if stock_code in current_prices:
                current_price = current_prices[stock_code]
                position_value = position['quantity'] * current_price
                total_position_value += position_value

                # 更新持仓信息
                position['current_price'] = current_price
                position['current_value'] = position_value
                position['unrealized_pnl'] = position_value - \
                    (position['quantity'] * position['avg_cost'])
                position['unrealized_pnl_pct'] = (
                    current_price - position['avg_cost']) / position['avg_cost']

        portfolio_value = self.current_capital + total_position_value
        self.portfolio_values.append({
            'timestamp': timestamp,
            'cash': self.current_capital,
            'positions_value': total_position_value,
            'total_value': portfolio_value,
            'positions_count': len(self.positions)
        })

        return portfolio_value

    def check_risk_control(self, current_prices: Dict[str, float]) -> List[Dict]:
        """检查风险控制，返回需要执行的交易"""
        trades_to_execute = []

        for stock_code, position in self.positions.items():
            if stock_code not in current_prices:
                continue

            current_price = current_prices[stock_code]
            profit_pct = (current_price -
                          position['avg_cost']) / position['avg_cost']

            # 检查止损
            if profit_pct <= -self.stop_loss_pct:
                trades_to_execute.append({
                    'stock_code': stock_code,
                    'action': 'SELL',
                    'quantity': position['quantity'],
                    'reason': f'止损: {profit_pct:.2%}'
                })

            # 检查止盈
            elif profit_pct >= self.take_profit_pct:
                trades_to_execute.append({
                    'stock_code': stock_code,
                    'action': 'SELL',
                    'quantity': position['quantity'],
                    'reason': f'止盈: {profit_pct:.2%}'
                })

        return trades_to_execute

    def get_portfolio_summary(self) -> Dict:
        """获取组合摘要"""
        if not self.portfolio_values:
            return {}

        latest = self.portfolio_values[-1]
        total_return = (latest['total_value'] -
                        self.initial_capital) / self.initial_capital

        return {
            'total_value': latest['total_value'],
            'cash': latest['cash'],
            'positions_value': latest['positions_value'],
            'positions_count': latest['positions_count'],
            'total_return': total_return,
            'total_trades': len(self.trade_history)
        }


def simulate_real_time_trading(strategy, stock_data_dict, simulation_days: int = 30):
    """模拟实时交易"""
    print(f"\n🔄 开始实时交易模拟 ({simulation_days} 天)...")

    # 初始化模拟交易器
    simulator = PaperTradingSimulator(initial_capital=1000000)

    # 获取所有交易日期
    all_dates = set()
    for stock_data in stock_data_dict.values():
        for data in stock_data:
            all_dates.add(data.date)

    sorted_dates = sorted(all_dates)

    # 选择最近的simulation_days天进行模拟
    simulation_dates = sorted_dates[-simulation_days:]

    print(f"  模拟期间: {simulation_dates[0]} 到 {simulation_dates[-1]}")

    for i, current_date in enumerate(simulation_dates, 1):
        print(f"\n📅 第 {i} 天: {current_date}")

        # 获取当日价格
        current_prices = {}
        for stock_code, stock_data in stock_data_dict.items():
            for data in stock_data:
                if data.date == current_date:
                    current_prices[stock_code] = data.close_price
                    break

        if not current_prices:
            continue

        # 更新组合价值
        portfolio_value = simulator.update_portfolio_value(
            current_prices, current_date)
        print(f"  组合价值: ¥{portfolio_value:,.2f}")

        # 检查风险控制
        risk_trades = simulator.check_risk_control(current_prices)
        for trade in risk_trades:
            stock_code = trade['stock_code']
            price = current_prices[stock_code]
            quantity = trade['quantity']
            reason = trade['reason']

            print(f"  🚨 {reason}")
            simulator.execute_sell_order(
                stock_code, price, quantity, current_date)

        # 生成交易信号
        signals_generated = 0
        for stock_code, stock_data in stock_data_dict.items():
            if stock_code not in current_prices:
                continue

            # 获取到当前日期的历史数据
            historical_data = []
            for data in stock_data:
                if data.date <= current_date:
                    historical_data.append(data)

            if len(historical_data) < 60:  # 需要足够的历史数据
                continue

            # 生成信号
            signals = strategy.generate_trading_signals(historical_data)

            for signal in signals:
                if signal.signal_type == 'BUY':
                    # 检查是否已有持仓
                    if stock_code in simulator.positions:
                        continue

                    # 检查持仓数量限制
                    if len(simulator.positions) >= simulator.max_positions:
                        continue

                    # 计算买入数量
                    available_capital = simulator.current_capital * 0.9  # 保留10%现金
                    max_position_value = available_capital * simulator.max_position_pct
                    price = current_prices[stock_code]
                    quantity = int(max_position_value /
                                   price / 100) * 100  # 按100股整数倍

                    if quantity >= 100:  # 至少买入100股
                        simulator.execute_buy_order(
                            stock_code, price, quantity, current_date)
                        signals_generated += 1

                elif signal.signal_type == 'SELL':
                    if stock_code in simulator.positions:
                        position = simulator.positions[stock_code]
                        price = current_prices[stock_code]
                        quantity = position['quantity']
                        simulator.execute_sell_order(
                            stock_code, price, quantity, current_date)
                        signals_generated += 1

        if signals_generated > 0:
            print(f"  生成 {signals_generated} 个交易信号")

        # 显示持仓摘要
        if simulator.positions:
            print("  当前持仓:")
            for stock_code, position in simulator.positions.items():
                if stock_code in current_prices:
                    current_price = current_prices[stock_code]
                    unrealized_pnl = position['quantity'] * \
                        (current_price - position['avg_cost'])
                    unrealized_pnl_pct = (
                        current_price - position['avg_cost']) / position['avg_cost']
                    print(f"    {stock_code}: {position['quantity']}股 @ ¥{position['avg_cost']:.2f} "
                          f"当前: ¥{current_price:.2f} 盈亏: ¥{unrealized_pnl:.2f} ({unrealized_pnl_pct:.2%})")

    return simulator


def analyze_simulation_results(simulator: PaperTradingSimulator):
    """分析模拟结果"""
    print("\n📊 模拟结果分析...")

    summary = simulator.get_portfolio_summary()
    if not summary:
        print("❌ 无模拟数据")
        return

    print(f"  初始资金: ¥{simulator.initial_capital:,.2f}")
    print(f"  最终资金: ¥{summary['total_value']:,.2f}")
    print(f"  总收益率: {summary['total_return']:.2%}")
    print(f"  现金余额: ¥{summary['cash']:,.2f}")
    print(f"  持仓价值: ¥{summary['positions_value']:,.2f}")
    print(f"  持仓数量: {summary['positions_count']} 只")
    print(f"  总交易次数: {summary['total_trades']} 次")

    # 计算交易统计
    if simulator.trade_history:
        buy_trades = [
            t for t in simulator.trade_history if t['action'] == 'BUY']
        sell_trades = [
            t for t in simulator.trade_history if t['action'] == 'SELL']

        print(f"  买入交易: {len(buy_trades)} 次")
        print(f"  卖出交易: {len(sell_trades)} 次")

        # 计算交易成本
        total_commission = sum(t['cost'] for t in simulator.trade_history)
        print(f"  总交易成本: ¥{total_commission:,.2f}")

        # 计算胜率
        if sell_trades:
            profitable_trades = [
                t for t in sell_trades if t.get('net_amount', 0) > 0]
            win_rate = len(profitable_trades) / len(sell_trades)
            print(f"  交易胜率: {win_rate:.2%}")

    # 计算风险指标
    if len(simulator.portfolio_values) > 1:
        returns = []
        for i in range(1, len(simulator.portfolio_values)):
            prev_value = simulator.portfolio_values[i-1]['total_value']
            curr_value = simulator.portfolio_values[i]['total_value']
            daily_return = (curr_value - prev_value) / prev_value
            returns.append(daily_return)

        if returns:
            volatility = np.std(returns) * np.sqrt(252)
            sharpe_ratio = (summary['total_return'] * 252 /
                            len(returns) - 0.03) / volatility if volatility > 0 else 0

            print(f"  年化波动率: {volatility:.2%}")
            print(f"  夏普比率: {sharpe_ratio:.3f}")

            # 计算最大回撤
            values = [pv['total_value'] for pv in simulator.portfolio_values]
            peak = np.maximum.accumulate(values)
            drawdown = (values - peak) / peak
            max_drawdown = abs(drawdown.min())
            print(f"  最大回撤: {max_drawdown:.2%}")


def run_paper_trading_simulation():
    """运行实盘模拟测试"""
    print("🚀 实盘模拟测试")
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
            name="实盘模拟策略",
            model_config=model_config,
            signal_threshold=0.02,
            confidence_threshold=0.65,
            position_sizing='equal',
            risk_management={
                "max_position_pct": 0.15,
                "max_positions": 8,
                "stop_loss_pct": 0.06,
                "take_profit_pct": 0.12,
                "max_drawdown_pct": 0.10,
                "min_confidence": 0.6
            }
        )

        # 2. 获取测试数据
        from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
        from quant_system.models.stock_data import StockData

        fetcher = FreeDataSourcesFetcher()

        # 选择测试股票
        test_stocks = ["000001", "000002", "600000",
                       "600036", "000858", "002415", "600519", "000725"]

        end_date = date.today()
        start_date = end_date - timedelta(days=200)

        stock_data_dict = {}
        for stock_code in test_stocks:
            print(f"  获取 {stock_code} 数据...")
            data = fetcher.get_historical_data_with_fallback(
                stock_code, start_date, end_date, "a_stock"
            )

            if data and len(data) > 100:
                stock_data = []
                for item in data:
                    date_str = str(item['date'])
                    stock_data.append(StockData(
                        code=stock_code,
                        name=item.get('name', ''),
                        date=date.fromisoformat(date_str),
                        open_price=float(item['open']),
                        close_price=float(item['close']),
                        high_price=float(item['high']),
                        low_price=float(item['low']),
                        volume=int(item['volume']),
                        amount=float(item['amount'])
                    ))

                stock_data_dict[stock_code] = stock_data
                print(f"    ✅ 成功获取 {len(stock_data)} 条数据")

        if not stock_data_dict:
            print("❌ 数据获取失败")
            return False

        # 3. 创建策略实例
        from quant_system.core.ml_enhanced_strategy import MLEnhancedStrategy
        strategy = MLEnhancedStrategy(strategy_config)

        # 4. 运行模拟交易
        simulator = simulate_real_time_trading(
            strategy, stock_data_dict, simulation_days=30)

        # 5. 分析结果
        analyze_simulation_results(simulator)

        print("\n🎉 实盘模拟测试完成！")
        return True

    except Exception as e:
        print(f"❌ 模拟测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_paper_trading_simulation()

    if success:
        print("\n💡 下一步建议:")
        print("1. 根据模拟结果调整策略参数")
        print("2. 增加更多股票进行测试")
        print("3. 优化风险控制机制")
        print("4. 考虑实盘部署")
        print("5. 建立监控和预警系统")
    else:
        print("\n🔧 请检查:")
        print("1. 数据源是否可用")
        print("2. 网络连接是否正常")
        print("3. 策略配置是否正确")
        print("4. 模拟参数是否合理")
