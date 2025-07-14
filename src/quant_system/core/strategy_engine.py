"""
选股策略引擎
实现从配置文件读取选股规则，并根据规则筛选股票的功能
"""
import os
import re
import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import asdict

from quant_system_architecture import StrategyEngine, SelectionCriteria, TradingSignal, StockData, DataProvider

logger = logging.getLogger(__name__)


class ConfigurableStrategyEngine(StrategyEngine):
    """可配置的策略引擎"""

    def __init__(self):
        self.criteria: Optional[SelectionCriteria] = None
        self.config: Dict[str, Any] = {}

    def load_selection_criteria(self, config_file: str) -> SelectionCriteria:
        """
        从配置文件加载选股条件

        Args:
            config_file: 配置文件路径

        Returns:
            选股条件对象
        """
        logger.info(f"加载选股策略配置: {config_file}")

        if not os.path.exists(config_file):
            logger.warning(f"配置文件不存在: {config_file}，使用默认配置")
            return SelectionCriteria()

        try:
            # 尝试加载YAML格式
            config_data = self._load_yaml_config(config_file)

            # 扁平化配置数据，便于后续使用
            self.config = self._flatten_config(config_data)

            # 从基础条件创建SelectionCriteria对象
            basic_criteria = config_data.get('basic_criteria', {})
            criteria = SelectionCriteria(
                consecutive_days=basic_criteria.get('consecutive_days', 3),
                min_total_return=basic_criteria.get('min_total_return', 0.15),
                max_drawdown=basic_criteria.get('max_drawdown', 0.05),
                exclude_limit_up_first_day=basic_criteria.get(
                    'exclude_limit_up_first_day', True)
            )

            self.criteria = criteria
            logger.info(f"选股策略配置加载完成: {asdict(criteria)}")
            logger.info(f"扩展配置项数量: {len(self.config)}")

            return criteria

        except Exception as e:
            logger.error(f"YAML加载失败: {e}")
            # 如果YAML加载失败，尝试旧格式
            return self._load_legacy_config(config_file)

    def _load_yaml_config(self, config_file: str) -> Dict:
        """加载YAML配置文件"""
        try:
            import yaml

            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            logger.info("YAML配置加载成功")
            return config_data

        except ImportError:
            logger.warning("PyYAML未安装，尝试使用简化YAML解析器")
            return self._parse_simple_yaml(config_file)
        except Exception as e:
            logger.error(f"YAML加载失败: {e}")
            raise

    def _parse_simple_yaml(self, config_file: str) -> Dict:
        """简化的YAML解析器（不依赖PyYAML）"""
        config_data = {}
        current_section = None

        with open(config_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue

                # 检查是否是节标题
                if ':' in line and not line.startswith(' ') and not line.startswith('-'):
                    if line.endswith(':'):
                        # 这是一个节标题
                        current_section = line[:-1].strip()
                        config_data[current_section] = {}
                        continue
                    else:
                        # 这是一个键值对
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()

                        # 移除行尾注释
                        if '#' in value:
                            value = value.split('#')[0].strip()

                        # 类型转换
                        parsed_value = self._parse_yaml_value(value)

                        if current_section:
                            config_data[current_section][key] = parsed_value
                        else:
                            config_data[key] = parsed_value

                # 处理列表项
                elif line.startswith('- '):
                    if current_section:
                        list_item = line[2:].strip().strip('"\'')
                        if 'excluded_industries' not in config_data[current_section]:
                            config_data[current_section]['excluded_industries'] = []
                        config_data[current_section]['excluded_industries'].append(
                            list_item)

        logger.info("简化YAML解析完成")
        return config_data

    def _parse_yaml_value(self, value: str):
        """解析YAML值"""
        value = value.strip()

        # 布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # 空列表
        if value == '[]':
            return []

        # 数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # 字符串（移除引号）
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]

        return value

    def _flatten_config(self, config_data: Dict) -> Dict:
        """
        扁平化配置数据

        Args:
            config_data: 嵌套的配置数据

        Returns:
            扁平化的配置字典
        """
        flattened = {}

        for section_key, section_value in config_data.items():
            if isinstance(section_value, dict):
                for key, value in section_value.items():
                    flattened[key] = value
            else:
                flattened[section_key] = section_value

        return flattened

    def _load_legacy_config(self, config_file: str) -> SelectionCriteria:
        """加载旧格式配置文件"""
        logger.info("尝试加载旧格式配置文件")

        config = {}

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue

                    # 解析配置项
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()

                        # 类型转换
                        config[key] = self._parse_config_value(value)

            self.config = config

            # 创建SelectionCriteria对象
            criteria = SelectionCriteria(
                consecutive_days=config.get('consecutive_days', 3),
                min_total_return=config.get('min_total_return', 0.15),
                max_drawdown=config.get('max_drawdown', 0.05),
                exclude_limit_up_first_day=config.get(
                    'exclude_limit_up_first_day', True)
            )

            logger.info("旧格式配置加载成功")
            return criteria

        except Exception as e:
            logger.error(f"旧格式配置加载失败: {e}")
            return SelectionCriteria()

    def _parse_config_value(self, value: str) -> Any:
        """解析配置值"""
        value = value.strip()

        # 布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'

        # 数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # 字符串
        return value

    def screen_stocks(self, criteria: SelectionCriteria, data_provider: DataProvider) -> List[Dict]:
        """
        根据条件筛选股票

        Args:
            criteria: 选股条件
            data_provider: 数据提供者

        Returns:
            符合条件的股票列表
        """
        logger.info("开始筛选股票...")

        # 获取股票列表
        stock_list = data_provider.get_stock_list('A')  # 先处理A股
        logger.info(f"获取到{len(stock_list)}只A股")

        # 计算日期范围
        end_date = date.today()
        start_date = end_date - \
            timedelta(days=self.config.get('lookback_days', 252))

        qualified_stocks = []
        processed_count = 0

        for code, name in stock_list:
            processed_count += 1

            if processed_count % 100 == 0:
                logger.info(f"已处理 {processed_count}/{len(stock_list)} 只股票")

            try:
                # 获取历史数据
                historical_data = data_provider.get_historical_data(
                    code, start_date, end_date)

                if len(historical_data) < criteria.consecutive_days:
                    continue

                # 应用筛选条件
                result = self._apply_selection_criteria(
                    historical_data, criteria)

                if result:
                    qualified_stocks.append(result)

            except Exception as e:
                logger.debug(f"处理股票{code}时出错: {e}")
                continue

        logger.info(f"筛选完成，符合条件的股票: {len(qualified_stocks)}只")

        # 按配置排序
        if self.config.get('sort_by_return', True):
            qualified_stocks.sort(
                key=lambda x: x['total_return'], reverse=True)

        # 限制输出数量
        max_output = self.config.get('max_output_stocks', 100)
        return qualified_stocks[:max_output]

    def _apply_selection_criteria(self, data: List[StockData], criteria: SelectionCriteria) -> Optional[Dict]:
        """
        应用选股条件

        Args:
            data: 历史数据
            criteria: 选股条件

        Returns:
            如果符合条件返回股票信息，否则返回None
        """
        if len(data) < criteria.consecutive_days:
            return None

        # 按日期排序
        data.sort(key=lambda x: x.date)

        # 寻找符合条件的连续交易日
        for i in range(len(data) - criteria.consecutive_days + 1):
            segment = data[i:i + criteria.consecutive_days]

            # 检查基本条件
            if self._check_basic_conditions(segment, criteria):
                # 检查高级条件
                if self._check_advanced_conditions(segment, data):
                    return self._create_stock_result(segment, data)

        return None

    def _check_basic_conditions(self, segment: List[StockData], criteria: SelectionCriteria) -> bool:
        """检查基本选股条件"""
        if len(segment) != criteria.consecutive_days:
            return False

        # 计算累计涨幅
        start_price = segment[0].open_price
        end_price = segment[-1].close_price

        if start_price <= 0:
            return False

        total_return = (end_price - start_price) / start_price

        # 检查累计涨幅
        if total_return < criteria.min_total_return:
            return False

        # 计算最大回调
        max_price = max(item.high_price for item in segment)
        min_price_after_max = float('inf')

        max_price_found = False
        for item in segment:
            if item.high_price == max_price:
                max_price_found = True
            if max_price_found:
                min_price_after_max = min(min_price_after_max, item.low_price)

        if min_price_after_max != float('inf') and max_price > 0:
            max_drawdown = (max_price - min_price_after_max) / max_price
            if max_drawdown > criteria.max_drawdown:
                return False

        # 检查第一日涨停
        if criteria.exclude_limit_up_first_day:
            first_day = segment[0]
            if first_day.open_price > 0:
                limit_up_price = first_day.open_price * 1.10  # A股涨停10%
                if first_day.open_price >= limit_up_price * 0.99:  # 允许小误差
                    return False

        return True

    def _check_advanced_conditions(self, segment: List[StockData], full_data: List[StockData]) -> bool:
        """检查高级筛选条件"""
        # 股价范围检查
        min_price = self.config.get('min_stock_price', 0)
        max_price = self.config.get('max_stock_price', float('inf'))

        avg_price = np.mean([item.close_price for item in segment])
        if not (min_price <= avg_price <= max_price):
            return False

        # 成交量检查
        min_volume = self.config.get('min_avg_volume', 0)
        avg_volume = np.mean([item.amount for item in segment])
        if avg_volume < min_volume * 10000:  # 转换为元
            return False

        # 换手率检查（简化计算）
        if self.config.get('enable_technical_indicators', False):
            # 这里可以添加更复杂的技术指标计算
            pass

        # 排除新股
        if self.config.get('exclude_new_stocks', True):
            if len(full_data) < self.config.get('new_stock_days_limit', 60):
                return False

        # 排除ST股票
        excluded_industries = self.config.get(
            'excluded_industries', '').split(',')
        stock_name = segment[0].name
        for excluded in excluded_industries:
            if excluded.strip() and excluded.strip() in stock_name:
                return False

        return True

    def _create_stock_result(self, segment: List[StockData], full_data: List[StockData]) -> Dict:
        """创建股票筛选结果"""
        start_price = segment[0].open_price
        end_price = segment[-1].close_price
        total_return = (end_price - start_price) / start_price

        # 计算最大回调
        max_price = max(item.high_price for item in segment)
        min_price_after_max = float('inf')

        max_price_found = False
        for item in segment:
            if item.high_price == max_price:
                max_price_found = True
            if max_price_found:
                min_price_after_max = min(min_price_after_max, item.low_price)

        max_drawdown = 0
        if min_price_after_max != float('inf') and max_price > 0:
            max_drawdown = (max_price - min_price_after_max) / max_price

        return {
            'code': segment[0].code,
            'name': segment[0].name,
            'start_date': segment[0].date,
            'end_date': segment[-1].date,
            'start_price': start_price,
            'end_price': end_price,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'avg_volume': np.mean([item.volume for item in segment]),
            'avg_amount': np.mean([item.amount for item in segment]),
            'consecutive_days': len(segment)
        }

    def generate_trading_signals(self, stock_data: List[StockData]) -> List[TradingSignal]:
        """
        生成交易信号

        Args:
            stock_data: 股票数据

        Returns:
            交易信号列表
        """
        signals = []

        if not stock_data or not self.criteria:
            return signals

        # 按日期排序
        stock_data.sort(key=lambda x: x.date)

        # 寻找买入信号
        for i in range(len(stock_data) - self.criteria.consecutive_days + 1):
            segment = stock_data[i:i + self.criteria.consecutive_days]

            if self._check_basic_conditions(segment, self.criteria):
                # 生成买入信号
                signal = TradingSignal(
                    code=segment[0].code,
                    signal_type='BUY',
                    price=segment[-1].close_price,
                    timestamp=segment[-1].date,
                    confidence=0.8,  # 可以根据更复杂的逻辑计算
                    reason=f"连续{self.criteria.consecutive_days}日涨幅达到{self.criteria.min_total_return:.1%}"
                )
                signals.append(signal)

        return signals

    def get_strategy_summary(self) -> Dict:
        """获取策略摘要"""
        return {
            'criteria': asdict(self.criteria) if self.criteria else {},
            'config': self.config,
            'strategy_type': '连续上涨选股策略',
            'description': f"筛选连续{self.config.get('consecutive_days', 3)}个交易日累计涨幅超过{self.config.get('min_total_return', 0.15):.1%}的股票"
        }


if __name__ == "__main__":
    # 测试策略引擎
    from data_provider import HistoricalDataProvider

    print("测试选股策略引擎...")

    # 创建策略引擎和数据提供者
    strategy = ConfigurableStrategyEngine()
    data_provider = HistoricalDataProvider()

    # 加载选股条件
    criteria = strategy.load_selection_criteria('./选股策略.txt')
    print(f"选股条件: {asdict(criteria)}")

    # 获取策略摘要
    summary = strategy.get_strategy_summary()
    print(f"策略摘要: {summary['description']}")

    # 测试小规模筛选（只测试前10只股票）
    print("\n开始小规模测试筛选...")
    stock_list = data_provider.get_stock_list('A')[:10]

    if stock_list:
        # 模拟筛选过程
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        for code, name in stock_list[:3]:  # 只测试前3只
            try:
                historical_data = data_provider.get_historical_data(
                    code, start_date, end_date)
                if historical_data:
                    signals = strategy.generate_trading_signals(
                        historical_data)
                    print(f"{code} {name}: {len(signals)}个信号")
            except Exception as e:
                print(f"处理{code}时出错: {e}")

    print("测试完成！")
