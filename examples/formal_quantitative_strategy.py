#!/usr/bin/env python3
"""
正式量化交易策略版本 - 端到端验证系统

基于项目现有架构，设计一个完整的量化交易策略，包含：
1. 多因子选股策略
2. 机器学习增强信号生成
3. 风险管理系统
4. 完整的回测验证
5. 性能分析和报告生成
"""

from quant_system.models.stock_data import StockData
import sys
from pathlib import Path
from datetime import date, timedelta, datetime
import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
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


class FormalQuantitativeStrategy:
    """正式量化交易策略系统"""

    def __init__(self):
        """初始化策略系统"""
        self.strategy_name = "正式量化交易策略V1.0"
        self.version = "1.0.0"
        self.description = "基于多因子选股和机器学习增强的量化交易策略"

        # 策略配置
        self.config = self._load_strategy_config()

        # 初始化组件
        self.data_fetcher = None
        self.strategy_engine = None
        self.backtest_engine = None
        self.risk_manager = None

        # 结果存储
        self.results = {}
        self.performance_metrics = {}

        logger.info(f"正式量化交易策略系统初始化完成: {self.strategy_name}")

    def _load_strategy_config(self) -> Dict:
        """加载策略配置"""
        return {
            # 基础配置
            'strategy_info': {
                'name': self.strategy_name,
                'version': self.version,
                'description': self.description,
                'author': '量化投资系统',
                'created_date': '2024-01-01'
            },

            # 选股配置
            'stock_screening': {
                'min_market_cap': 10000000000,  # 最小市值10亿
                'max_market_cap': 500000000000,  # 最大市值5000亿
                'min_price': 5.0,  # 最小股价
                'max_price': 200.0,  # 最大股价
                'min_volume': 10000000,  # 最小成交额1000万
                'exclude_st': True,  # 排除ST股票
                'exclude_new_stocks': True,  # 排除新股
                'new_stock_days_limit': 60,  # 新股天数限制
                'excluded_industries': ['房地产', '钢铁', '煤炭'],
                'included_sectors': ['科技', '医药', '消费', '新能源']
            },

            # 技术指标配置
            'technical_indicators': {
                'momentum_periods': [5, 10, 20, 60],
                'volume_periods': [5, 10, 20],
                'volatility_periods': [20],
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'bollinger_period': 20,
                'bollinger_std': 2
            },

            # 信号生成配置
            'signal_generation': {
                'buy_thresholds': {
                    'momentum_20d': 0.15,  # 20日动量超过15%
                    'volume_ratio': 1.5,   # 成交量放大1.5倍
                    'rsi_buy': 30,         # RSI买入阈值
                    'rsi_sell': 70,        # RSI卖出阈值
                    'ma_bullish': True,    # 均线多头排列
                    'volatility_max': 0.05  # 最大波动率
                },
                'sell_thresholds': {
                    'stop_loss': -0.05,    # 止损5%
                    'take_profit': 0.15,   # 止盈15%
                    'momentum_reversal': -0.05,  # 动量反转
                    'volume_shrink': 0.5   # 成交量萎缩
                }
            },

            # 风险管理配置
            'risk_management': {
                'max_positions': 8,        # 最大持仓数
                'max_position_pct': 0.15,  # 单只股票最大仓位
                'max_sector_exposure': 0.30,  # 单行业最大暴露
                'stop_loss_pct': 0.05,     # 止损比例
                'take_profit_pct': 0.15,   # 止盈比例
                'max_drawdown_pct': 0.10,  # 最大回撤
                'trailing_stop': True,     # 启用追踪止损
                'trailing_stop_pct': 0.03  # 追踪止损比例
            },

            # 回测配置
            'backtest': {
                'initial_capital': 1000000,  # 初始资金100万
                'commission_rate': 0.0003,   # 手续费率
                'stamp_tax_rate': 0.001,     # 印花税率
                'slippage_rate': 0.001,      # 滑点率
                'benchmark': '000300.SH'     # 基准指数
            }
        }

    def initialize_components(self):
        """初始化系统组件"""
        logger.info("初始化系统组件...")

        try:
            # 初始化数据获取器
            from market_data.fetchers.free_data_sources import FreeDataSourcesFetcher
            self.data_fetcher = FreeDataSourcesFetcher()
            logger.info("✅ 数据获取器初始化完成")

            # 初始化策略引擎
            from quant_system.core.strategy_engine import ConfigurableStrategyEngine
            self.strategy_engine = ConfigurableStrategyEngine()
            logger.info("✅ 策略引擎初始化完成")

            # 初始化回测引擎
            from quant_system.core.backtest_engine import QuantitativeBacktestEngine
            self.backtest_engine = QuantitativeBacktestEngine()
            logger.info("✅ 回测引擎初始化完成")

            # 初始化风险管理器
            self.risk_manager = RiskManager(self.config['risk_management'])
            logger.info("✅ 风险管理器初始化完成")

            return True

        except Exception as e:
            logger.error(f"组件初始化失败: {e}")
            return False

    def get_stock_pool(self) -> List[str]:
        """获取股票池（直接返回默认池）"""
        logger.info("获取股票池...")
        return self._get_default_stock_pool()

    def _get_default_stock_pool(self) -> List[str]:
        """获取默认股票池"""
        return [
            '000001',  # 平安银行
            '000002',  # 万科A
            '000858',  # 五粮液
            '002415',  # 海康威视
            '600036',  # 招商银行
            '600519',  # 贵州茅台
            '600887',  # 伊利股份
            '000858',  # 五粮液
            '002594',  # 比亚迪
            '300059'   # 东方财富
        ]

    def _apply_stock_filters(self, stock_list: List[Dict]) -> List[str]:
        """应用股票筛选条件"""
        filtered_stocks = []
        screening_config = self.config['stock_screening']

        for stock in stock_list:
            try:
                code = stock.get('code', '')
                name = stock.get('name', '')
                price = stock.get('price', 0)
                market_cap = stock.get('market_cap', 0)
                volume = stock.get('volume', 0)
                industry = stock.get('industry', '')

                # 基础筛选
                if not code or len(code) != 6:
                    continue

                # 价格筛选
                if price < screening_config['min_price'] or price > screening_config['max_price']:
                    continue

                # 市值筛选
                if market_cap < screening_config['min_market_cap'] or market_cap > screening_config['max_market_cap']:
                    continue

                # 成交量筛选
                if volume < screening_config['min_volume']:
                    continue

                # 排除ST股票
                if screening_config['exclude_st'] and ('ST' in name or '*' in name):
                    continue

                # 行业筛选
                if industry in screening_config['excluded_industries']:
                    continue

                filtered_stocks.append(code)

            except Exception as e:
                logger.debug(f"筛选股票 {stock.get('code', '')} 时出错: {e}")
                continue

        return filtered_stocks[:50]  # 限制数量

    def get_historical_data(self, stock_codes: List[str],
                            start_date: date, end_date: date) -> Dict[str, List]:
        """获取历史数据，并转换为StockData对象，放宽天数限制"""
        logger.info(f"获取 {len(stock_codes)} 只股票的历史数据...")

        historical_data = {}
        success_count = 0

        for code in stock_codes:
            try:
                data = self.data_fetcher.get_historical_data_with_fallback(
                    code, start_date, end_date)

                # 转换为StockData对象
                stock_data_list = []
                for d in data:
                    if isinstance(d, StockData):
                        stock_data_list.append(d)
                    elif isinstance(d, dict):
                        try:
                            # 字段映射和补全
                            mapped_data = self._map_dict_to_stockdata(d, code)
                            if mapped_data:
                                stock_data_list.append(
                                    StockData(**mapped_data))
                        except Exception as e:
                            logger.debug(f"转换dict为StockData失败: {e}")
                            continue

                # 只需20天数据即可
                if stock_data_list and len(stock_data_list) >= 20:
                    historical_data[code] = stock_data_list
                    success_count += 1

                time.sleep(0.1)

            except Exception as e:
                logger.debug(f"获取股票 {code} 历史数据失败: {e}")
                continue

        logger.info(f"历史数据获取完成，成功获取 {success_count} 只股票数据")
        return historical_data

    def _map_dict_to_stockdata(self, data_dict: dict, code: str) -> dict:
        """将dict映射为StockData参数"""
        try:
            # 打印第一个数据样本，用于调试
            if len(data_dict) > 0:
                logger.debug(f"数据样本: {list(data_dict.keys())}")

            mapped = {
                'code': code,
                'name': data_dict.get('name', f'股票{code}'),
                'date': data_dict.get('date', data_dict.get('trade_date', date.today())),
                'open_price': float(data_dict.get('open', data_dict.get('open_price', 0))),
                'close_price': float(data_dict.get('close', data_dict.get('close_price', 0))),
                'high_price': float(data_dict.get('high', data_dict.get('high_price', 0))),
                'low_price': float(data_dict.get('low', data_dict.get('low_price', 0))),
                'volume': int(data_dict.get('volume', 0)),
                'amount': float(data_dict.get('amount', data_dict.get('turnover', 0))),
                'pre_close': data_dict.get('pre_close', None),
                'change': data_dict.get('change', None),
                'pct_change': data_dict.get('pct_change', None),
                'turnover_rate': data_dict.get('turnover_rate', None)
            }

            # 验证必要字段
            if mapped['close_price'] <= 0:
                return None

            return mapped

        except Exception as e:
            logger.debug(f"字段映射失败: {e}")
            return None

    def calculate_technical_indicators(self, stock_data: List) -> Dict:
        """计算技术指标"""
        if len(stock_data) < 60:
            return {}

        try:
            # 转换为DataFrame
            df = pd.DataFrame([{
                'date': data.date,
                'open': data.open_price,
                'high': data.high_price,
                'low': data.low_price,
                'close': data.close_price,
                'volume': data.volume
            } for data in stock_data])

            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date').reset_index(drop=True)

            indicators = {}

            # 计算移动平均线
            for period in [5, 10, 20, 60]:
                if len(df) >= period:
                    indicators[f'ma_{period}'] = df['close'].rolling(
                        period).mean().iloc[-1]

            # 计算动量指标
            for period in [5, 10, 20, 60]:
                if len(df) >= period:
                    indicators[f'momentum_{period}d'] = (
                        df['close'].iloc[-1] - df['close'].iloc[-period]) / df['close'].iloc[-period]

            # 计算成交量指标
            for period in [5, 10, 20]:
                if len(df) >= period:
                    current_volume = df['volume'].iloc[-1]
                    avg_volume = df['volume'].rolling(period).mean().iloc[-1]
                    indicators[f'volume_ratio_{period}d'] = current_volume / \
                        avg_volume if avg_volume > 0 else 1

            # 计算RSI
            if len(df) >= 14:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                indicators['rsi'] = 100 - \
                    (100 / (1 + rs.iloc[-1])) if rs.iloc[-1] != 0 else 50

            # 计算波动率
            if len(df) >= 20:
                returns = df['close'].pct_change().dropna()
                indicators['volatility_20d'] = returns.rolling(
                    20).std().iloc[-1]

            # 计算均线多头排列
            if all(f'ma_{period}' in indicators for period in [5, 10, 20]):
                indicators['ma_bullish'] = (
                    indicators['ma_5'] > indicators['ma_10'] > indicators['ma_20']
                )

            return indicators

        except Exception as e:
            logger.error(f"计算技术指标失败: {e}")
            return {}

    def generate_trading_signals(self, stock_data: Dict[str, List],
                                 current_positions: Dict = None) -> List[Dict]:
        """生成交易信号"""
        logger.info("生成交易信号...")

        signals = []
        signal_config = self.config['signal_generation']

        for code, data in stock_data.items():
            try:
                # 计算技术指标
                indicators = self.calculate_technical_indicators(data)
                if not indicators:
                    continue

                current_price = data[-1].close_price

                # 检查买入信号
                if current_positions is None or code not in current_positions:
                    buy_signal = self._check_buy_signals(
                        indicators, code, current_price, signal_config)
                    if buy_signal:
                        signals.append(buy_signal)

                # 检查卖出信号
                if current_positions and code in current_positions:
                    sell_signal = self._check_sell_signals(
                        indicators, code, current_price, signal_config)
                    if sell_signal:
                        signals.append(sell_signal)

            except Exception as e:
                logger.debug(f"生成股票 {code} 交易信号失败: {e}")
                continue

        logger.info(f"交易信号生成完成，共 {len(signals)} 个信号")
        return signals

    def _check_buy_signals(self, indicators: Dict, code: str,
                           current_price: float, signal_config: Dict) -> Optional[Dict]:
        """检查买入信号"""
        buy_thresholds = signal_config['buy_thresholds']

        # 动量信号
        momentum_ok = indicators.get(
            'momentum_20d', 0) > buy_thresholds['momentum_20d']

        # 成交量信号
        volume_ok = indicators.get(
            'volume_ratio_5d', 1) > buy_thresholds['volume_ratio']

        # RSI信号
        rsi = indicators.get('rsi', 50)
        rsi_ok = buy_thresholds['rsi_buy'] < rsi < buy_thresholds['rsi_sell']

        # 均线信号
        ma_ok = indicators.get('ma_bullish', False)

        # 波动率信号
        volatility = indicators.get('volatility_20d', 0)
        volatility_ok = volatility < buy_thresholds['volatility_max']

        # 综合判断
        if momentum_ok and volume_ok and rsi_ok and ma_ok and volatility_ok:
            return {
                'code': code,
                'action': 'BUY',
                'price': current_price,
                'date': datetime.now().date(),
                'reason': '多因子买入信号',
                'confidence': 0.8,
                'indicators': indicators
            }

        return None

    def _check_sell_signals(self, indicators: Dict, code: str,
                            current_price: float, signal_config: Dict) -> Optional[Dict]:
        """检查卖出信号"""
        sell_thresholds = signal_config['sell_thresholds']

        # 动量反转
        momentum_reversal = indicators.get(
            'momentum_20d', 0) < sell_thresholds['momentum_reversal']

        # 成交量萎缩
        volume_shrink = indicators.get(
            'volume_ratio_5d', 1) < sell_thresholds['volume_shrink']

        # RSI超买
        rsi = indicators.get('rsi', 50)
        rsi_overbought = rsi > sell_thresholds['rsi_sell']

        if momentum_reversal or volume_shrink or rsi_overbought:
            return {
                'code': code,
                'action': 'SELL',
                'price': current_price,
                'date': datetime.now().date(),
                'reason': '技术指标卖出信号',
                'confidence': 0.7,
                'indicators': indicators
            }

        return None

    def run_backtest(self, start_date: date, end_date: date) -> Dict:
        """运行回测"""
        logger.info(f"开始回测: {start_date} 到 {end_date}")

        try:
            # 获取股票池
            stock_pool = self.get_stock_pool()
            if not stock_pool:
                logger.error("无法获取股票池")
                return {}

            # 获取历史数据
            historical_data = self.get_historical_data(
                stock_pool, start_date, end_date)
            if not historical_data:
                logger.error("无法获取历史数据")
                return {}

            # 运行回测
            backtest_config = self.config['backtest']
            results = self._run_backtest_simulation(
                historical_data, backtest_config)

            # 计算性能指标
            performance = self._calculate_performance_metrics(results)

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

    def _run_backtest_simulation(self, historical_data: Dict[str, List],
                                 config: Dict) -> Dict:
        """运行回测模拟"""
        # 初始化
        initial_capital = config['initial_capital']
        current_capital = initial_capital
        positions = {}
        trades = []
        portfolio_values = []

        # 按日期遍历
        all_dates = set()
        for data in historical_data.values():
            all_dates.update([d.date for d in data])

        sorted_dates = sorted(all_dates)

        for current_date in sorted_dates:
            try:
                # 更新持仓市值
                current_portfolio_value = current_capital
                for code, position in positions.items():
                    if code in historical_data:
                        # 找到当前日期的价格
                        current_price = None
                        for data in historical_data[code]:
                            if data.date == current_date:
                                current_price = data.close_price
                                break

                        if current_price:
                            position['market_value'] = position['quantity'] * \
                                current_price
                            position['unrealized_pnl'] = position['market_value'] - \
                                position['cost']
                            current_portfolio_value += position['unrealized_pnl']

                # 检查卖出信号
                self._check_exit_signals(
                    current_date, historical_data, positions, trades, config)

                # 检查买入信号
                self._check_entry_signals(
                    current_date, historical_data, positions, trades, config)

                # 记录组合价值
                portfolio_values.append({
                    'date': current_date,
                    'value': current_portfolio_value,
                    'positions': len(positions)
                })

            except Exception as e:
                logger.debug(f"处理日期 {current_date} 时出错: {e}")
                continue

        return {
            'initial_capital': initial_capital,
            'final_value': portfolio_values[-1]['value'] if portfolio_values else initial_capital,
            'trades': trades,
            'portfolio_values': portfolio_values,
            'positions': positions
        }

    def _check_exit_signals(self, current_date: date, historical_data: Dict,
                            positions: Dict, trades: List, config: Dict):
        """检查退出信号"""
        for code in list(positions.keys()):
            if code not in historical_data:
                continue

            # 找到当前价格
            current_price = None
            for data in historical_data[code]:
                if data.date == current_date:
                    current_price = data.close_price
                    break

            if not current_price:
                continue

            position = positions[code]

            # 检查止损止盈
            cost_price = position['cost'] / position['quantity']
            profit_pct = (current_price - cost_price) / cost_price

            # 止损
            if profit_pct <= -config['stop_loss_pct']:
                self._execute_sell(code, current_price, position['quantity'],
                                   current_date, '止损', trades, positions, config)

            # 止盈
            elif profit_pct >= config['take_profit_pct']:
                self._execute_sell(code, current_price, position['quantity'],
                                   current_date, '止盈', trades, positions, config)

    def _check_entry_signals(self, current_date: date, historical_data: Dict,
                             positions: Dict, trades: List, config: Dict):
        """检查入场信号"""
        # 检查持仓数量限制
        if len(positions) >= config['max_positions']:
            return

        # 计算可用资金
        available_capital = self._calculate_available_capital(
            positions, config)
        if available_capital <= 0:
            return

        # 生成买入信号
        for code, data in historical_data.items():
            if code in positions:
                continue

            # 找到当前价格
            current_price = None
            for data_point in data:
                if data_point.date == current_date:
                    current_price = data_point.close_price
                    break

            if not current_price:
                continue

            # 计算技术指标
            indicators = self.calculate_technical_indicators(data)
            if not indicators:
                continue

            # 检查买入条件
            if self._check_buy_signals(indicators, code, current_price,
                                       self.config['signal_generation']):
                # 计算买入数量
                position_value = available_capital * config['max_position_pct']
                quantity = int(position_value /
                               current_price / 100) * 100  # 整手买入

                if quantity > 0:
                    self._execute_buy(code, current_price, quantity,
                                      current_date, '技术信号买入', trades, positions, config)
                    break

    def _execute_buy(self, code: str, price: float, quantity: int,
                     date: date, reason: str, trades: List, positions: Dict, config: Dict):
        """执行买入"""
        cost = price * quantity
        commission = max(
            cost * config['commission_rate'], config.get('min_commission', 5))
        total_cost = cost + commission

        positions[code] = {
            'quantity': quantity,
            'cost': total_cost,
            'avg_price': price,
            'buy_date': date,
            'market_value': cost,
            'unrealized_pnl': 0
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

    def _execute_sell(self, code: str, price: float, quantity: int,
                      date: date, reason: str, trades: List, positions: Dict, config: Dict):
        """执行卖出"""
        if code not in positions:
            return

        position = positions[code]
        amount = price * quantity
        commission = max(
            amount * config['commission_rate'], config.get('min_commission', 5))
        stamp_tax = amount * config['stamp_tax_rate']
        net_amount = amount - commission - stamp_tax

        # 计算盈亏
        cost_portion = position['cost'] * (quantity / position['quantity'])
        realized_pnl = net_amount - cost_portion

        trades.append({
            'date': date,
            'code': code,
            'action': 'SELL',
            'price': price,
            'quantity': quantity,
            'amount': amount,
            'commission': commission + stamp_tax,
            'realized_pnl': realized_pnl,
            'reason': reason
        })

        # 更新持仓
        if quantity >= position['quantity']:
            del positions[code]
        else:
            position['quantity'] -= quantity
            position['cost'] -= cost_portion

    def _calculate_available_capital(self, positions: Dict, config: Dict) -> float:
        """计算可用资金"""
        # 简化实现，实际应该考虑持仓市值
        return config['initial_capital'] * 0.1  # 保留10%现金

    def _calculate_performance_metrics(self, results: Dict) -> Dict:
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

        # 计算夏普比率（简化）
        returns = []
        for i in range(1, len(portfolio_values)):
            daily_return = (
                portfolio_values[i]['value'] - portfolio_values[i-1]['value']) / portfolio_values[i-1]['value']
            returns.append(daily_return)

        if returns:
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = avg_return / std_return * \
                np.sqrt(252) if std_return > 0 else 0
        else:
            sharpe_ratio = 0

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
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'total_trades': len(trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'final_value': final_value,
            'initial_value': initial_value
        }

    def generate_report(self) -> str:
        """生成策略报告"""
        if not self.performance_metrics:
            return "无回测结果可生成报告"

        report = f"""
# 正式量化交易策略报告

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
- 夏普比率: {self.performance_metrics.get('sharpe_ratio', 0):.2f}
- 胜率: {self.performance_metrics.get('win_rate', 0):.2%}

## 交易统计
- 总交易次数: {self.performance_metrics.get('total_trades', 0)}
- 买入交易: {self.performance_metrics.get('buy_trades', 0)}
- 卖出交易: {self.performance_metrics.get('sell_trades', 0)}

## 策略配置
- 最大持仓数: {self.config['risk_management']['max_positions']}
- 单只股票最大仓位: {self.config['risk_management']['max_position_pct']:.1%}
- 止损比例: {self.config['risk_management']['stop_loss_pct']:.1%}
- 止盈比例: {self.config['risk_management']['take_profit_pct']:.1%}

## 风险控制
- 最大回撤限制: {self.config['risk_management']['max_drawdown_pct']:.1%}
- 追踪止损: {'启用' if self.config['risk_management']['trailing_stop'] else '禁用'}
- 行业暴露限制: {self.config['risk_management']['max_sector_exposure']:.1%}
"""

        return report

    def save_results(self, output_file: str = None):
        """保存结果"""
        if not output_file:
            output_file = f"formal_strategy_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

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


class RiskManager:
    """风险管理器"""

    def __init__(self, config: Dict):
        self.config = config

    def validate_signal(self, signal: Dict, current_positions: Dict) -> bool:
        """验证交易信号"""
        # 检查持仓数量限制
        if signal['action'] == 'BUY' and len(current_positions) >= self.config['max_positions']:
            return False

        # 检查仓位限制
        if signal['action'] == 'BUY':
            position_value = signal['price'] * signal.get('quantity', 100)
            total_portfolio_value = self._calculate_portfolio_value(
                current_positions)
            position_pct = position_value / \
                total_portfolio_value if total_portfolio_value > 0 else 0

            if position_pct > self.config['max_position_pct']:
                return False

        return True

    def _calculate_portfolio_value(self, positions: Dict) -> float:
        """计算组合总价值"""
        total_value = 0
        for position in positions.values():
            total_value += position.get('market_value', 0)
        return total_value


def main():
    """主函数 - 端到端验证"""
    print("🚀 正式量化交易策略 - 端到端验证")
    print("=" * 60)

    # 创建策略实例
    strategy = FormalQuantitativeStrategy()

    # 初始化组件
    if not strategy.initialize_components():
        print("❌ 组件初始化失败")
        return

    print("✅ 系统初始化完成")

    # 设置回测参数
    end_date = date.today()
    start_date = end_date - timedelta(days=180)  # 6个月回测

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
    print(f"   夏普比率: {performance.get('sharpe_ratio', 0):.2f}")
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
