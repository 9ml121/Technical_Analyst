#!/usr/bin/env python3
"""
小资金实盘测试系统

进行小资金实盘测试验证，包含：
1. 资金管理和风险控制
2. 实时信号生成和交易执行
3. 持仓监控和绩效跟踪
4. 风险预警和止损机制
5. 详细的交易记录和报告
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
import threading
from dataclasses import dataclass, asdict

# 添加src目录到Python路径
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class TradeRecord:
    """交易记录"""
    timestamp: datetime
    stock_code: str
    action: str  # BUY, SELL
    price: float
    quantity: int
    amount: float
    commission: float
    reason: str
    strategy_name: str


@dataclass
class Position:
    """持仓信息"""
    stock_code: str
    quantity: int
    avg_cost: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    buy_date: datetime
    last_update: datetime


class LiveTradingAccount:
    """实盘交易账户"""

    def __init__(self, initial_capital: float = 10000):
        """初始化交易账户"""
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeRecord] = []
        self.daily_pnl: List[Dict] = []

        # 交易成本设置
        self.commission_rate = 0.0003  # 手续费率 0.03%
        self.min_commission = 5.0      # 最低手续费5元
        self.slippage_rate = 0.0005    # 滑点率 0.05%

        # 风险控制参数
        self.max_position_pct = 0.20   # 单只股票最大仓位20%
        self.max_positions = 5         # 最大持仓5只股票
        self.stop_loss_pct = 0.08      # 止损8%
        self.take_profit_pct = 0.20    # 止盈20%
        self.max_daily_loss_pct = 0.05  # 单日最大亏损5%

        # 交易记录
        self.trading_log = []

        print(f"💰 实盘交易账户初始化完成")
        print(f"   初始资金: ¥{initial_capital:,.2f}")
        print(f"   最大持仓: {self.max_positions} 只股票")
        print(f"   单股最大仓位: {self.max_position_pct:.1%}")

    def calculate_commission(self, trade_amount: float) -> float:
        """计算手续费"""
        commission = max(trade_amount * self.commission_rate,
                         self.min_commission)
        return commission

    def calculate_slippage(self, trade_amount: float) -> float:
        """计算滑点成本"""
        return trade_amount * self.slippage_rate

    def get_available_capital(self) -> float:
        """获取可用资金"""
        return self.current_capital * 0.95  # 保留5%现金

    def can_buy(self, stock_code: str, price: float, quantity: int) -> Tuple[bool, str]:
        """检查是否可以买入"""
        # 检查是否已有持仓
        if stock_code in self.positions:
            return False, f"已有 {stock_code} 持仓"

        # 检查持仓数量限制
        if len(self.positions) >= self.max_positions:
            return False, f"已达到最大持仓数量 {self.max_positions}"

        # 计算交易金额
        trade_amount = price * quantity
        total_cost = trade_amount + \
            self.calculate_commission(trade_amount) + \
            self.calculate_slippage(trade_amount)

        # 检查资金是否足够
        if total_cost > self.get_available_capital():
            return False, f"资金不足，需要 ¥{total_cost:,.2f}，可用 ¥{self.get_available_capital():,.2f}"

        # 检查仓位限制
        position_value = trade_amount
        account_value = self.get_account_value()
        if account_value > 0 and position_value / account_value > self.max_position_pct:
            return False, f"超过单股最大仓位限制 {self.max_position_pct:.1%}"

        return True, "可以买入"

    def execute_buy(self, stock_code: str, price: float, quantity: int, reason: str = "策略信号") -> bool:
        """执行买入"""
        can_buy, message = self.can_buy(stock_code, price, quantity)
        if not can_buy:
            self.log_trading(f"买入失败: {stock_code} - {message}")
            return False

        trade_amount = price * quantity
        commission = self.calculate_commission(trade_amount)
        slippage = self.calculate_slippage(trade_amount)
        total_cost = trade_amount + commission + slippage

        # 更新资金
        self.current_capital -= total_cost

        # 创建持仓
        position = Position(
            stock_code=stock_code,
            quantity=quantity,
            avg_cost=price,
            current_price=price,
            unrealized_pnl=0.0,
            unrealized_pnl_pct=0.0,
            buy_date=datetime.now(),
            last_update=datetime.now()
        )
        self.positions[stock_code] = position

        # 记录交易
        trade_record = TradeRecord(
            timestamp=datetime.now(),
            stock_code=stock_code,
            action="BUY",
            price=price,
            quantity=quantity,
            amount=trade_amount,
            commission=commission,
            reason=reason,
            strategy_name="ML增强策略"
        )
        self.trade_history.append(trade_record)

        self.log_trading(
            f"买入成功: {stock_code} {quantity}股 @ ¥{price:.2f}, 成本: ¥{commission:.2f}")
        return True

    def execute_sell(self, stock_code: str, price: float, quantity: int, reason: str = "策略信号") -> bool:
        """执行卖出"""
        if stock_code not in self.positions:
            self.log_trading(f"卖出失败: {stock_code} - 无持仓")
            return False

        position = self.positions[stock_code]
        if quantity > position.quantity:
            self.log_trading(f"卖出失败: {stock_code} - 持仓不足")
            return False

        trade_amount = price * quantity
        commission = self.calculate_commission(trade_amount)
        slippage = self.calculate_slippage(trade_amount)
        net_amount = trade_amount - commission - slippage

        # 更新资金
        self.current_capital += net_amount

        # 计算盈亏
        profit = (price - position.avg_cost) * quantity - commission - slippage
        profit_pct = (price - position.avg_cost) / position.avg_cost

        # 更新持仓
        remaining_quantity = position.quantity - quantity
        if remaining_quantity == 0:
            # 全部卖出，删除持仓
            del self.positions[stock_code]
        else:
            # 部分卖出，更新持仓
            position.quantity = remaining_quantity
            position.last_update = datetime.now()

        # 记录交易
        trade_record = TradeRecord(
            timestamp=datetime.now(),
            stock_code=stock_code,
            action="SELL",
            price=price,
            quantity=quantity,
            amount=trade_amount,
            commission=commission,
            reason=reason,
            strategy_name="ML增强策略"
        )
        self.trade_history.append(trade_record)

        self.log_trading(
            f"卖出成功: {stock_code} {quantity}股 @ ¥{price:.2f}, 盈亏: ¥{profit:.2f} ({profit_pct:.2%})")
        return True

    def update_positions(self, current_prices: Dict[str, float]):
        """更新持仓信息"""
        for stock_code, position in self.positions.items():
            if stock_code in current_prices:
                current_price = current_prices[stock_code]
                position.current_price = current_price
                position.unrealized_pnl = (
                    current_price - position.avg_cost) * position.quantity
                position.unrealized_pnl_pct = (
                    current_price - position.avg_cost) / position.avg_cost
                position.last_update = datetime.now()

    def check_risk_control(self, current_prices: Dict[str, float]) -> List[Dict]:
        """检查风险控制"""
        risk_trades = []

        for stock_code, position in self.positions.items():
            if stock_code not in current_prices:
                continue

            current_price = current_prices[stock_code]
            profit_pct = (current_price - position.avg_cost) / \
                position.avg_cost

            # 检查止损
            if profit_pct <= -self.stop_loss_pct:
                risk_trades.append({
                    'stock_code': stock_code,
                    'action': 'SELL',
                    'quantity': position.quantity,
                    'reason': f'止损: {profit_pct:.2%}'
                })

            # 检查止盈
            elif profit_pct >= self.take_profit_pct:
                risk_trades.append({
                    'stock_code': stock_code,
                    'action': 'SELL',
                    'quantity': position.quantity,
                    'reason': f'止盈: {profit_pct:.2%}'
                })

        return risk_trades

    def get_account_value(self) -> float:
        """获取账户总价值"""
        total_position_value = sum(
            pos.quantity * pos.current_price
            for pos in self.positions.values()
        )
        return self.current_capital + total_position_value

    def get_account_summary(self) -> Dict:
        """获取账户摘要"""
        account_value = self.get_account_value()
        total_return = (account_value - self.initial_capital) / \
            self.initial_capital

        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'account_value': account_value,
            'total_return': total_return,
            'positions_count': len(self.positions),
            'total_trades': len(self.trade_history)
        }

    def log_trading(self, message: str):
        """记录交易日志"""
        log_entry = {
            'timestamp': datetime.now(),
            'message': message
        }
        self.trading_log.append(log_entry)
        print(f"[{log_entry['timestamp'].strftime('%H:%M:%S')}] {message}")


class LiveTradingTest:
    """实盘测试系统"""

    def __init__(self, test_capital: float = 10000):
        """初始化实盘测试系统"""
        self.account = LiveTradingAccount(test_capital)
        self.strategy = None
        self.test_stocks = []
        self.is_running = False
        self.test_results = {}

        print(f"🚀 实盘测试系统初始化完成")
        print(f"   测试资金: ¥{test_capital:,.2f}")

    def setup_strategy(self):
        """设置策略"""
        from quant_system.core.ml_enhanced_strategy import MLStrategyConfig, ModelConfig, MLEnhancedStrategy

        # 创建保守的策略配置
        model_config = ModelConfig(
            model_type='random_forest',
            n_estimators=100,
            max_depth=8,
            feature_selection='kbest',
            n_features=15,
            target_horizon=3
        )

        strategy_config = MLStrategyConfig(
            name="实盘测试策略",
            model_config=model_config,
            signal_threshold=0.03,   # 提高信号阈值，更保守
            confidence_threshold=0.75,  # 提高置信度要求
            position_sizing='equal',
            risk_management={
                "max_position_pct": 0.20,
                "max_positions": 5,
                "stop_loss_pct": 0.08,
                "take_profit_pct": 0.20,
                "max_drawdown_pct": 0.10,
                "min_confidence": 0.75
            }
        )

        self.strategy = MLEnhancedStrategy(strategy_config)
        print("✅ 策略配置完成")

    def setup_test_stocks(self):
        """设置测试股票"""
        # 选择流动性好、波动适中的股票
        self.test_stocks = [
            "000001",  # 平安银行
            "000002",  # 万科A
            "600000",  # 浦发银行
            "600036",  # 招商银行
            "000858",  # 五粮液
            "002415",  # 海康威视
            "600519",  # 贵州茅台
            "000725",  # 京东方A
        ]
        print(f"✅ 测试股票设置完成: {len(self.test_stocks)} 只")

    def get_current_prices(self) -> Dict[str, float]:
        """获取当前价格"""
        from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher

        fetcher = FreeDataSourcesFetcher()
        current_prices = {}

        for stock_code in self.test_stocks:
            try:
                # 获取最新数据
                end_date = date.today()
                start_date = end_date - timedelta(days=5)

                data = fetcher.get_historical_data_with_fallback(
                    stock_code, start_date, end_date, "a_stock"
                )

                if data and len(data) > 0:
                    latest_data = data[-1]
                    current_prices[stock_code] = float(latest_data['close'])

            except Exception as e:
                print(f"⚠️  获取 {stock_code} 价格失败: {e}")
                continue

        return current_prices

    def run_daily_trading(self):
        """执行每日交易"""
        print(f"\n📅 开始每日交易 - {date.today()}")

        # 获取当前价格
        current_prices = self.get_current_prices()
        if not current_prices:
            print("❌ 无法获取价格数据")
            return

        # 更新持仓
        self.account.update_positions(current_prices)

        # 检查风险控制
        risk_trades = self.account.check_risk_control(current_prices)
        for trade in risk_trades:
            stock_code = trade['stock_code']
            price = current_prices[stock_code]
            quantity = trade['quantity']
            reason = trade['reason']

            print(f"🚨 {reason}")
            self.account.execute_sell(stock_code, price, quantity, reason)

        # 生成交易信号
        signals_generated = 0
        for stock_code in self.test_stocks:
            if stock_code not in current_prices:
                continue

            # 获取历史数据
            from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
            from quant_system.models.stock_data import StockData

            fetcher = FreeDataSourcesFetcher()
            end_date = date.today()
            start_date = end_date - timedelta(days=100)

            try:
                data = fetcher.get_historical_data_with_fallback(
                    stock_code, start_date, end_date, "a_stock"
                )

                if data and len(data) > 60:
                    # 转换为StockData对象
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

                    # 生成信号
                    signals = self.strategy.generate_trading_signals(
                        stock_data)

                    for signal in signals:
                        if signal.signal_type == 'BUY':
                            price = current_prices[stock_code]
                            # 计算买入数量
                            available_capital = self.account.get_available_capital()
                            max_position_value = available_capital * self.account.max_position_pct
                            quantity = int(
                                max_position_value / price / 100) * 100

                            if quantity >= 100:
                                if self.account.execute_buy(stock_code, price, quantity, "策略买入信号"):
                                    signals_generated += 1

                        elif signal.signal_type == 'SELL':
                            if stock_code in self.account.positions:
                                position = self.account.positions[stock_code]
                                price = current_prices[stock_code]
                                if self.account.execute_sell(stock_code, price, position.quantity, "策略卖出信号"):
                                    signals_generated += 1

            except Exception as e:
                print(f"⚠️  处理 {stock_code} 信号失败: {e}")
                continue

        if signals_generated > 0:
            print(f"✅ 生成 {signals_generated} 个交易信号")

        # 显示持仓摘要
        self.show_positions_summary(current_prices)

        # 记录每日盈亏
        self.record_daily_pnl()

    def show_positions_summary(self, current_prices: Dict[str, float]):
        """显示持仓摘要"""
        if not self.account.positions:
            print("  当前无持仓")
            return

        print("  当前持仓:")
        total_position_value = 0

        for stock_code, position in self.account.positions.items():
            if stock_code in current_prices:
                current_price = current_prices[stock_code]
                position_value = position.quantity * current_price
                total_position_value += position_value

                print(f"    {stock_code}: {position.quantity}股 @ ¥{position.avg_cost:.2f} "
                      f"当前: ¥{current_price:.2f} 盈亏: ¥{position.unrealized_pnl:.2f} ({position.unrealized_pnl_pct:.2%})")

        account_summary = self.account.get_account_summary()
        print(f"  持仓价值: ¥{total_position_value:,.2f}")
        print(f"  账户总价值: ¥{account_summary['account_value']:,.2f}")
        print(f"  总收益率: {account_summary['total_return']:.2%}")

    def record_daily_pnl(self):
        """记录每日盈亏"""
        account_summary = self.account.get_account_summary()

        daily_pnl = {
            'date': date.today(),
            'account_value': account_summary['account_value'],
            'total_return': account_summary['total_return'],
            'positions_count': account_summary['positions_count'],
            'cash': self.account.current_capital
        }

        self.account.daily_pnl.append(daily_pnl)

    def run_test(self, test_days: int = 10):
        """运行测试"""
        print(f"🚀 开始实盘测试 ({test_days} 天)")
        print("=" * 60)

        # 设置策略和股票
        self.setup_strategy()
        self.setup_test_stocks()

        self.is_running = True

        for day in range(test_days):
            if not self.is_running:
                break

            try:
                self.run_daily_trading()

                # 显示账户摘要
                summary = self.account.get_account_summary()
                print(f"\n📊 第 {day + 1} 天账户摘要:")
                print(f"  账户价值: ¥{summary['account_value']:,.2f}")
                print(f"  总收益率: {summary['total_return']:.2%}")
                print(f"  持仓数量: {summary['positions_count']} 只")
                print(f"  总交易次数: {summary['total_trades']} 次")

                # 检查风险
                if summary['total_return'] < -0.10:  # 亏损超过10%
                    print("🚨 风险警告: 亏损超过10%，停止测试")
                    break

                if day < test_days - 1:
                    print(f"\n⏳ 等待下一天...")
                    time.sleep(2)  # 模拟等待

            except Exception as e:
                print(f"❌ 第 {day + 1} 天测试失败: {e}")
                continue

        self.is_running = False
        self.generate_test_report()

    def generate_test_report(self):
        """生成测试报告"""
        print(f"\n📋 实盘测试报告")
        print("=" * 60)

        summary = self.account.get_account_summary()

        print(f"测试期间: {len(self.account.daily_pnl)} 天")
        print(f"初始资金: ¥{summary['initial_capital']:,.2f}")
        print(f"最终资金: ¥{summary['account_value']:,.2f}")
        print(f"总收益率: {summary['total_return']:.2%}")
        print(f"总交易次数: {summary['total_trades']} 次")
        print(f"最终持仓: {summary['positions_count']} 只")

        # 计算风险指标
        if len(self.account.daily_pnl) > 1:
            returns = []
            for i in range(1, len(self.account.daily_pnl)):
                prev_value = self.account.daily_pnl[i-1]['account_value']
                curr_value = self.account.daily_pnl[i]['account_value']
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)

            if returns:
                volatility = np.std(returns) * np.sqrt(252)
                sharpe_ratio = (
                    summary['total_return'] * 252 / len(returns) - 0.03) / volatility if volatility > 0 else 0

                print(f"年化波动率: {volatility:.2%}")
                print(f"夏普比率: {sharpe_ratio:.3f}")

                # 计算最大回撤
                values = [pnl['account_value']
                          for pnl in self.account.daily_pnl]
                peak = np.maximum.accumulate(values)
                drawdown = (values - peak) / peak
                max_drawdown = abs(drawdown.min())
                print(f"最大回撤: {max_drawdown:.2%}")

        # 交易统计
        if self.account.trade_history:
            buy_trades = [
                t for t in self.account.trade_history if t.action == 'BUY']
            sell_trades = [
                t for t in self.account.trade_history if t.action == 'SELL']

            print(f"\n交易统计:")
            print(f"  买入交易: {len(buy_trades)} 次")
            print(f"  卖出交易: {len(sell_trades)} 次")

            # 计算总手续费
            total_commission = sum(
                t.commission for t in self.account.trade_history)
            print(f"  总手续费: ¥{total_commission:,.2f}")

        # 保存测试结果
        test_results = {
            'test_summary': summary,
            'daily_pnl': self.account.daily_pnl,  # 已经是字典格式
            'trade_history': [asdict(trade) for trade in self.account.trade_history],
            'trading_log': self.account.trading_log,
            'test_date': datetime.now().isoformat()
        }

        with open("live_trading_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2,
                      ensure_ascii=False, default=str)

        print(f"\n✅ 测试结果已保存到 live_trading_test_results.json")

        # 评估结果
        if summary['total_return'] > 0.05:
            print("🎉 测试成功！策略表现良好")
        elif summary['total_return'] > -0.05:
            print("✅ 测试通过！策略表现稳定")
        else:
            print("⚠️  测试需要改进！策略表现不佳")


def run_live_trading_test():
    """运行实盘测试"""
    print("🚀 小资金实盘测试系统")
    print("=" * 60)

    try:
        # 创建测试系统
        test_system = LiveTradingTest(test_capital=10000)

        # 运行测试
        test_system.run_test(test_days=5)  # 测试5天

        print("\n🎉 实盘测试完成！")
        return True

    except Exception as e:
        print(f"❌ 实盘测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_live_trading_test()

    if success:
        print("\n💡 下一步建议:")
        print("1. 分析测试结果，评估策略表现")
        print("2. 根据测试结果调整策略参数")
        print("3. 增加测试天数，验证策略稳定性")
        print("4. 考虑增加更多股票进行测试")
        print("5. 准备进行更大资金的实盘测试")
    else:
        print("\n🔧 请检查:")
        print("1. 网络连接是否正常")
        print("2. 数据源是否可用")
        print("3. 策略配置是否正确")
        print("4. 测试参数是否合理")
