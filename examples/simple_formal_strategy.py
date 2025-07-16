#!/usr/bin/env python3
"""
简化版正式量化交易策略 - 端到端验证

基于项目现有架构，设计一个简化的量化交易策略，避免复杂的依赖问题
包含完整的策略设计、回测验证和端到端测试
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


class SimpleFormalStrategy:
    """简化版正式量化交易策略"""

    def __init__(self):
        """初始化策略"""
        self.strategy_name = "简化版正式量化交易策略V1.0"
        self.version = "1.0.0"
        self.description = "基于多因子选股的简化量化交易策略"

        # 策略配置
        self.config = self._load_config()

        # 结果存储
        self.results = {}
        self.performance_metrics = {}

        logger.info(f"简化版正式量化交易策略初始化完成: {self.strategy_name}")

    def _load_config(self):
        """加载配置"""
        return {
            'strategy_info': {
                'name': self.strategy_name,
                'version': self.version,
                'description': self.description
            },
            'stock_screening': {
                'min_price': 5.0,
                'max_price': 200.0,
                'min_volume': 10000000
            },
            'signal_generation': {
                'momentum_threshold': 0.10,
                'volume_threshold': 1.2,
                'stop_loss': -0.05,
                'take_profit': 0.15
            },
            'risk_management': {
                'max_positions': 5,
                'max_position_pct': 0.20
            },
            'backtest': {
                'initial_capital': 100000,
                'commission_rate': 0.0003
            }
        }

    def get_stock_pool(self):
        """获取股票池"""
        logger.info("获取股票池...")

        # 使用固定的测试股票池
        test_stocks = [
            {'code': '000001', 'name': '平安银行', 'price': 12.5, 'volume': 50000000},
            {'code': '000002', 'name': '万科A', 'price': 18.2, 'volume': 30000000},
            {'code': '600036', 'name': '招商银行', 'price': 35.8, 'volume': 40000000},
            {'code': '600519', 'name': '贵州茅台', 'price': 1680.0, 'volume': 2000000},
            {'code': '000858', 'name': '五粮液', 'price': 156.5, 'volume': 8000000}
        ]

        # 应用筛选条件
        filtered_stocks = []
        for stock in test_stocks:
            if (self.config['stock_screening']['min_price'] <= stock['price'] <=
                self.config['stock_screening']['max_price'] and
                    stock['volume'] >= self.config['stock_screening']['min_volume']):
                filtered_stocks.append(stock['code'])

        logger.info(f"股票池筛选完成，共 {len(filtered_stocks)} 只股票")
        return filtered_stocks

    def generate_mock_data(self, stock_codes, start_date, end_date):
        """生成模拟历史数据"""
        logger.info("生成模拟历史数据...")

        historical_data = {}

        for code in stock_codes:
            data = []
            current_date = start_date

            # 生成基础价格
            base_price = 10.0 + hash(code) % 50  # 基于股票代码生成不同价格

            while current_date <= end_date:
                # 生成随机价格变动
                import random
                price_change = random.uniform(-0.05, 0.05)  # ±5%的随机变动
                current_price = base_price * (1 + price_change)

                # 生成成交量
                volume = random.randint(1000000, 10000000)

                data.append({
                    'date': current_date,
                    'open_price': current_price * 0.99,
                    'high_price': current_price * 1.02,
                    'low_price': current_price * 0.98,
                    'close_price': current_price,
                    'volume': volume
                })

                current_date += timedelta(days=1)
                base_price = current_price  # 更新基础价格

            historical_data[code] = data

        logger.info(f"模拟数据生成完成，共 {len(historical_data)} 只股票")
        return historical_data

    def calculate_indicators(self, stock_data):
        """计算技术指标"""
        if len(stock_data) < 20:
            return {}

        # 计算简单的技术指标
        prices = [d['close_price'] for d in stock_data]
        volumes = [d['volume'] for d in stock_data]

        # 计算动量（20日收益率）
        if len(prices) >= 20:
            momentum_20d = (prices[-1] - prices[-20]) / prices[-20]
        else:
            momentum_20d = 0

        # 计算成交量比率
        if len(volumes) >= 5:
            current_volume = volumes[-1]
            avg_volume = sum(volumes[-5:]) / 5
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        else:
            volume_ratio = 1

        return {
            'momentum_20d': momentum_20d,
            'volume_ratio': volume_ratio,
            'current_price': prices[-1]
        }

    def generate_signals(self, historical_data):
        """生成交易信号"""
        logger.info("生成交易信号...")

        signals = []
        signal_config = self.config['signal_generation']

        for code, data in historical_data.items():
            if len(data) < 20:
                continue

            # 计算技术指标
            indicators = self.calculate_indicators(data)

            # 生成买入信号
            if (indicators['momentum_20d'] > signal_config['momentum_threshold'] and
                    indicators['volume_ratio'] > signal_config['volume_threshold']):
                signals.append({
                    'code': code,
                    'action': 'BUY',
                    'price': indicators['current_price'],
                    'date': datetime.now().date(),
                    'reason': '动量+成交量信号',
                    'confidence': 0.8
                })

        logger.info(f"交易信号生成完成，共 {len(signals)} 个信号")
        return signals

    def run_backtest(self, start_date, end_date):
        """运行回测"""
        logger.info(f"开始回测: {start_date} 到 {end_date}")

        try:
            # 获取股票池
            stock_pool = self.get_stock_pool()
            if not stock_pool:
                logger.error("无法获取股票池")
                return {}

            # 生成模拟数据
            historical_data = self.generate_mock_data(
                stock_pool, start_date, end_date)

            # 运行回测模拟
            results = self._run_backtest_simulation(historical_data)

            # 计算性能指标
            performance = self._calculate_performance(results)

            self.results = results
            self.performance_metrics = performance

            logger.info("回测完成")
            return {
                'results': results,
                'performance': performance
            }

        except Exception as e:
            logger.error(f"回测失败: {e}")
            return {}

    def _run_backtest_simulation(self, historical_data):
        """运行回测模拟"""
        initial_capital = self.config['backtest']['initial_capital']
        current_capital = initial_capital
        positions = {}
        trades = []
        portfolio_values = []

        # 按日期遍历
        all_dates = set()
        for data in historical_data.values():
            all_dates.update([d['date'] for d in data])

        sorted_dates = sorted(all_dates)

        for current_date in sorted_dates:
            # 更新持仓市值
            portfolio_value = current_capital
            for code, position in positions.items():
                if code in historical_data:
                    # 找到当前价格
                    current_price = None
                    for data in historical_data[code]:
                        if data['date'] == current_date:
                            current_price = data['close_price']
                            break

                    if current_price:
                        position['market_value'] = position['quantity'] * \
                            current_price
                        portfolio_value += position['market_value'] - \
                            position['cost']

            # 检查卖出信号
            self._check_exit_signals(
                current_date, historical_data, positions, trades)

            # 检查买入信号
            self._check_entry_signals(
                current_date, historical_data, positions, trades)

            # 记录组合价值
            portfolio_values.append({
                'date': current_date,
                'value': portfolio_value
            })

        return {
            'initial_capital': initial_capital,
            'final_value': portfolio_values[-1]['value'] if portfolio_values else initial_capital,
            'trades': trades,
            'portfolio_values': portfolio_values
        }

    def _check_exit_signals(self, current_date, historical_data, positions, trades):
        """检查退出信号"""
        for code in list(positions.keys()):
            if code not in historical_data:
                continue

            # 找到当前价格
            current_price = None
            for data in historical_data[code]:
                if data['date'] == current_date:
                    current_price = data['close_price']
                    break

            if not current_price:
                continue

            position = positions[code]
            cost_price = position['cost'] / position['quantity']
            profit_pct = (current_price - cost_price) / cost_price

            # 止损止盈
            if (profit_pct <= self.config['signal_generation']['stop_loss'] or
                    profit_pct >= self.config['signal_generation']['take_profit']):
                self._execute_sell(code, current_price, position['quantity'],
                                   current_date, '止损止盈', trades, positions)

    def _check_entry_signals(self, current_date, historical_data, positions, trades):
        """检查入场信号"""
        if len(positions) >= self.config['risk_management']['max_positions']:
            return

        # 生成买入信号
        for code, data in historical_data.items():
            if code in positions:
                continue

            if len(data) < 20:
                continue

            # 找到当前价格
            current_price = None
            for data_point in data:
                if data_point['date'] == current_date:
                    current_price = data_point['close_price']
                    break

            if not current_price:
                continue

            # 计算技术指标
            indicators = self.calculate_indicators(data)

            # 检查买入条件
            if (indicators['momentum_20d'] > self.config['signal_generation']['momentum_threshold'] and
                    indicators['volume_ratio'] > self.config['signal_generation']['volume_threshold']):

                # 计算买入数量
                position_value = self.config['backtest']['initial_capital'] * \
                    self.config['risk_management']['max_position_pct']
                quantity = int(position_value / current_price / 100) * 100

                if quantity > 0:
                    self._execute_buy(code, current_price, quantity,
                                      current_date, '技术信号买入', trades, positions)
                    break

    def _execute_buy(self, code, price, quantity, date, reason, trades, positions):
        """执行买入"""
        cost = price * quantity
        commission = cost * self.config['backtest']['commission_rate']
        total_cost = cost + commission

        positions[code] = {
            'quantity': quantity,
            'cost': total_cost,
            'buy_date': date,
            'market_value': cost
        }

        trades.append({
            'date': date,
            'code': code,
            'action': 'BUY',
            'price': price,
            'quantity': quantity,
            'amount': cost,
            'commission': commission,
            'reason': reason
        })

    def _execute_sell(self, code, price, quantity, date, reason, trades, positions):
        """执行卖出"""
        if code not in positions:
            return

        position = positions[code]
        amount = price * quantity
        commission = amount * self.config['backtest']['commission_rate']
        net_amount = amount - commission

        cost_portion = position['cost'] * (quantity / position['quantity'])
        realized_pnl = net_amount - cost_portion

        trades.append({
            'date': date,
            'code': code,
            'action': 'SELL',
            'price': price,
            'quantity': quantity,
            'amount': amount,
            'commission': commission,
            'realized_pnl': realized_pnl,
            'reason': reason
        })

        if quantity >= position['quantity']:
            del positions[code]
        else:
            position['quantity'] -= quantity
            position['cost'] -= cost_portion

    def _calculate_performance(self, results):
        """计算性能指标"""
        if not results or 'portfolio_values' not in results:
            return {}

        portfolio_values = results['portfolio_values']
        if not portfolio_values:
            return {}

        # 计算基础指标
        initial_value = results['initial_capital']
        final_value = portfolio_values[-1]['value']
        total_return = (final_value - initial_value) / initial_value

        # 计算年化收益率
        if len(portfolio_values) > 1:
            days = (portfolio_values[-1]['date'] -
                    portfolio_values[0]['date']).days
            annual_return = (1 + total_return) ** (365 /
                                                   days) - 1 if days > 0 else 0
        else:
            annual_return = 0

        # 计算最大回撤
        max_drawdown = 0
        peak_value = initial_value

        for pv in portfolio_values:
            current_value = pv['value']
            if current_value > peak_value:
                peak_value = current_value

            drawdown = (peak_value - current_value) / peak_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # 交易统计
        trades = results.get('trades', [])
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']

        win_trades = [t for t in sell_trades if t.get('realized_pnl', 0) > 0]
        win_rate = len(win_trades) / len(sell_trades) if sell_trades else 0

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': len(trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'final_value': final_value,
            'initial_value': initial_value
        }

    def generate_report(self):
        """生成策略报告"""
        if not self.performance_metrics:
            return "无回测结果可生成报告"

        report = f"""
# 简化版正式量化交易策略报告

## 策略信息
- 策略名称: {self.strategy_name}
- 版本: {self.version}
- 描述: {self.description}

## 回测结果
- 初始资金: {self.performance_metrics.get('initial_value', 0):,.0f} 元
- 最终价值: {self.performance_metrics.get('final_value', 0):,.0f} 元
- 总收益率: {self.performance_metrics.get('total_return', 0):.2%}
- 年化收益率: {self.performance_metrics.get('annual_return', 0):.2%}
- 最大回撤: {self.performance_metrics.get('max_drawdown', 0):.2%}
- 胜率: {self.performance_metrics.get('win_rate', 0):.2%}

## 交易统计
- 总交易次数: {self.performance_metrics.get('total_trades', 0)}
- 买入交易: {self.performance_metrics.get('buy_trades', 0)}
- 卖出交易: {self.performance_metrics.get('sell_trades', 0)}

## 策略配置
- 最大持仓数: {self.config['risk_management']['max_positions']}
- 单只股票最大仓位: {self.config['risk_management']['max_position_pct']:.1%}
- 动量阈值: {self.config['signal_generation']['momentum_threshold']:.1%}
- 成交量阈值: {self.config['signal_generation']['volume_threshold']:.1f}
- 止损比例: {self.config['signal_generation']['stop_loss']:.1%}
- 止盈比例: {self.config['signal_generation']['take_profit']:.1%}
"""

        return report

    def save_results(self, output_file=None):
        """保存结果"""
        if not output_file:
            output_file = f"simple_strategy_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        results_data = {
            'strategy_info': {
                'name': self.strategy_name,
                'version': self.version,
                'description': self.description
            },
            'config': self.config,
            'results': self.results,
            'performance_metrics': self.performance_metrics,
            'timestamp': datetime.now().isoformat()
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, ensure_ascii=False,
                          indent=2, default=str)

            logger.info(f"结果已保存到: {output_file}")

            # 生成报告
            report = self.generate_report()
            report_file = output_file.replace('.json', '_report.md')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            logger.info(f"报告已保存到: {report_file}")

        except Exception as e:
            logger.error(f"保存结果失败: {e}")


def main():
    """主函数 - 端到端验证"""
    print("🚀 简化版正式量化交易策略 - 端到端验证")
    print("=" * 60)

    # 创建策略实例
    strategy = SimpleFormalStrategy()

    print("✅ 系统初始化完成")

    # 设置回测参数
    end_date = date.today()
    start_date = end_date - timedelta(days=30)  # 30天回测

    print(f"📅 回测期间: {start_date} 到 {end_date}")
    print(f"💰 初始资金: {strategy.config['backtest']['initial_capital']:,.0f} 元")

    # 运行回测
    print("\n🔄 开始回测...")
    results = strategy.run_backtest(start_date, end_date)

    if not results:
        print("❌ 回测失败")
        return

    # 显示结果
    performance = results['performance']
    print("\n📊 回测结果:")
    print(f"   总收益率: {performance.get('total_return', 0):.2%}")
    print(f"   年化收益率: {performance.get('annual_return', 0):.2%}")
    print(f"   最大回撤: {performance.get('max_drawdown', 0):.2%}")
    print(f"   胜率: {performance.get('win_rate', 0):.2%}")
    print(f"   总交易次数: {performance.get('total_trades', 0)}")

    # 保存结果
    print("\n💾 保存结果...")
    strategy.save_results()

    # 生成报告
    print("\n📋 生成策略报告...")
    report = strategy.generate_report()
    print(report)

    print("\n🎉 端到端验证完成！")


if __name__ == "__main__":
    main()
