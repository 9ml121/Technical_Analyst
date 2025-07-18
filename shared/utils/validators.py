"""
数据验证器工具 - 微服务架构共享工具
提供数据验证和校验功能
"""
import re
from typing import List, Dict, Any, Optional, Union, Callable, Tuple
from datetime import date, datetime
from pathlib import Path

from .exceptions import ValidationError


class DataValidator:
    """数据验证器"""

    def __init__(self):
        """初始化数据验证器"""
        self.errors = []
        self.warnings = []

    def validate_stock_data(self, data: Dict[str, Any]) -> bool:
        """
        验证股票数据

        Args:
            data: 股票数据字典

        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()

        # 必需字段验证
        required_fields = ['code', 'date', 'open_price',
                           'close_price', 'high_price', 'low_price', 'volume']
        for field in required_fields:
            if field not in data:
                self.errors.append(f"缺少必需字段: {field}")

        # 股票代码验证
        if 'code' in data:
            if not self._validate_stock_code(data['code']):
                self.errors.append(f"无效的股票代码: {data['code']}")

        # 日期验证
        if 'date' in data:
            if not self._validate_date(data['date']):
                self.errors.append(f"无效的日期格式: {data['date']}")

        # 价格验证
        price_fields = ['open_price', 'close_price', 'high_price', 'low_price']
        for field in price_fields:
            if field in data:
                if not self._validate_price(data[field]):
                    self.errors.append(f"无效的价格值: {field} = {data[field]}")

        # 成交量验证
        if 'volume' in data:
            if not self._validate_volume(data['volume']):
                self.errors.append(f"无效的成交量: {data['volume']}")

        # 价格逻辑验证
        if all(field in data for field in price_fields):
            if not self._validate_price_logic(data):
                self.warnings.append("价格逻辑异常: 最高价应大于等于最低价")

        return len(self.errors) == 0

    def validate_trading_signal(self, signal: Dict[str, Any]) -> bool:
        """
        验证交易信号

        Args:
            signal: 交易信号字典

        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()

        # 必需字段验证
        required_fields = ['stock_code', 'signal_type', 'signal_time', 'price']
        for field in required_fields:
            if field not in signal:
                self.errors.append(f"缺少必需字段: {field}")

        # 股票代码验证
        if 'stock_code' in signal:
            if not self._validate_stock_code(signal['stock_code']):
                self.errors.append(f"无效的股票代码: {signal['stock_code']}")

        # 信号类型验证
        if 'signal_type' in signal:
            valid_types = ['buy', 'sell', 'hold']
            if signal['signal_type'] not in valid_types:
                self.errors.append(f"无效的信号类型: {signal['signal_type']}")

        # 价格验证
        if 'price' in signal:
            if not self._validate_price(signal['price']):
                self.errors.append(f"无效的价格: {signal['price']}")

        # 置信度验证
        if 'confidence' in signal:
            if not self._validate_confidence(signal['confidence']):
                self.errors.append(f"无效的置信度: {signal['confidence']}")

        return len(self.errors) == 0

    def validate_strategy_config(self, config: Dict[str, Any]) -> bool:
        """
        验证策略配置

        Args:
            config: 策略配置字典

        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()

        # 必需字段验证
        required_fields = ['name', 'strategy_type']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必需字段: {field}")

        # 策略类型验证
        if 'strategy_type' in config:
            valid_types = ['momentum', 'mean_reversion', 'breakout', 'custom']
            if config['strategy_type'] not in valid_types:
                self.errors.append(f"无效的策略类型: {config['strategy_type']}")

        # 参数验证
        if 'parameters' in config:
            if not isinstance(config['parameters'], dict):
                self.errors.append("参数必须是字典格式")

        # 风控参数验证
        if 'risk_management' in config:
            self._validate_risk_management(config['risk_management'])

        return len(self.errors) == 0

    def validate_backtest_config(self, config: Dict[str, Any]) -> bool:
        """
        验证回测配置

        Args:
            config: 回测配置字典

        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()

        # 必需字段验证
        required_fields = ['start_date', 'end_date', 'initial_capital']
        for field in required_fields:
            if field not in config:
                self.errors.append(f"缺少必需字段: {field}")

        # 日期验证
        if 'start_date' in config and 'end_date' in config:
            if not self._validate_date_range(config['start_date'], config['end_date']):
                self.errors.append("开始日期不能晚于结束日期")

        # 资金验证
        if 'initial_capital' in config:
            if not self._validate_capital(config['initial_capital']):
                self.errors.append(f"无效的初始资金: {config['initial_capital']}")

        # 手续费验证
        if 'commission_rate' in config:
            if not self._validate_rate(config['commission_rate']):
                self.errors.append(f"无效的手续费率: {config['commission_rate']}")

        return len(self.errors) == 0

    def _validate_stock_code(self, code: str) -> bool:
        """验证股票代码"""
        if not code or not isinstance(code, str):
            return False

        # 股票代码格式验证
        valid_patterns = [
            r'^600\d{3}$',  # 沪市主板
            r'^601\d{3}$',  # 沪市主板
            r'^603\d{3}$',  # 沪市主板
            r'^688\d{3}$',  # 科创板
            r'^000\d{3}$',  # 深市主板
            r'^002\d{3}$',  # 中小板
            r'^300\d{3}$',  # 创业板
            r'^8\d{5}$',    # 北交所
        ]

        return any(re.match(pattern, code) for pattern in valid_patterns)

    def _validate_date(self, date_value: Any) -> bool:
        """验证日期"""
        if isinstance(date_value, (date, datetime)):
            return True

        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, '%Y-%m-%d')
                return True
            except ValueError:
                return False

        return False

    def _validate_price(self, price: Any) -> bool:
        """验证价格"""
        if not isinstance(price, (int, float)):
            return False

        return price > 0 and not float('inf') == price and not float('-inf') == price

    def _validate_volume(self, volume: Any) -> bool:
        """验证成交量"""
        if not isinstance(volume, (int, float)):
            return False

        return volume >= 0 and not float('inf') == volume

    def _validate_price_logic(self, data: Dict[str, Any]) -> bool:
        """验证价格逻辑"""
        high = data.get('high_price', 0)
        low = data.get('low_price', 0)
        open_price = data.get('open_price', 0)
        close_price = data.get('close_price', 0)

        return high >= low and high >= open_price and high >= close_price and low <= open_price and low <= close_price

    def _validate_confidence(self, confidence: Any) -> bool:
        """验证置信度"""
        if not isinstance(confidence, (int, float)):
            return False

        return 0 <= confidence <= 1

    def _validate_date_range(self, start_date: Any, end_date: Any) -> bool:
        """验证日期范围"""
        try:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            return start_date <= end_date
        except (ValueError, TypeError):
            return False

    def _validate_capital(self, capital: Any) -> bool:
        """验证资金"""
        if not isinstance(capital, (int, float)):
            return False

        return capital > 0 and not float('inf') == capital

    def _validate_rate(self, rate: Any) -> bool:
        """验证费率"""
        if not isinstance(rate, (int, float)):
            return False

        return 0 <= rate <= 1

    def _validate_risk_management(self, risk_config: Dict[str, Any]):
        """验证风控配置"""
        if not isinstance(risk_config, dict):
            self.errors.append("风控配置必须是字典格式")
            return

        # 验证止损比例
        if 'stop_loss_pct' in risk_config:
            if not self._validate_rate(risk_config['stop_loss_pct']):
                self.errors.append(f"无效的止损比例: {risk_config['stop_loss_pct']}")

        # 验证最大回撤
        if 'max_drawdown_pct' in risk_config:
            if not self._validate_rate(risk_config['max_drawdown_pct']):
                self.errors.append(
                    f"无效的最大回撤: {risk_config['max_drawdown_pct']}")

    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors.copy()

    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings.copy()


class ConfigValidator:
    """配置验证器"""

    def __init__(self):
        """初始化配置验证器"""
        self.errors = []
        self.warnings = []

    def validate_system_config(self, config: Dict[str, Any]) -> bool:
        """
        验证系统配置

        Args:
            config: 系统配置字典

        Returns:
            验证是否通过
        """
        self.errors.clear()
        self.warnings.clear()

        # 验证必需的顶级配置项
        required_sections = ['system', 'logging', 'database', 'data_sources']
        for section in required_sections:
            if section not in config:
                self.errors.append(f"缺少必需的配置节: {section}")

        # 验证系统配置
        if 'system' in config:
            self._validate_system_section(config['system'])

        # 验证日志配置
        if 'logging' in config:
            self._validate_logging_section(config['logging'])

        # 验证数据库配置
        if 'database' in config:
            self._validate_database_section(config['database'])

        # 验证数据源配置
        if 'data_sources' in config:
            self._validate_data_sources_section(config['data_sources'])

        # 验证回测配置
        if 'backtest' in config:
            self._validate_backtest_section(config['backtest'])

        # 验证策略配置
        if 'strategy' in config:
            self._validate_strategy_section(config['strategy'])

        return len(self.errors) == 0

    def _validate_system_section(self, system_config: Dict[str, Any]):
        """验证系统配置节"""
        required_fields = ['name', 'version']
        for field in required_fields:
            if field not in system_config:
                self.errors.append(f"系统配置缺少必需字段: {field}")

    def _validate_logging_section(self, logging_config: Dict[str, Any]):
        """验证日志配置节"""
        required_fields = ['level', 'format']
        for field in required_fields:
            if field not in logging_config:
                self.errors.append(f"日志配置缺少必需字段: {field}")

        # 验证日志级别
        if 'level' in logging_config:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if logging_config['level'].upper() not in valid_levels:
                self.errors.append(f"无效的日志级别: {logging_config['level']}")

    def _validate_database_section(self, database_config: Dict[str, Any]):
        """验证数据库配置节"""
        required_fields = ['host', 'port', 'database']
        for field in required_fields:
            if field not in database_config:
                self.errors.append(f"数据库配置缺少必需字段: {field}")

        # 验证端口号
        if 'port' in database_config:
            try:
                port = int(database_config['port'])
                if not (1 <= port <= 65535):
                    self.errors.append(f"无效的端口号: {port}")
            except (ValueError, TypeError):
                self.errors.append(f"端口号必须是整数: {database_config['port']}")

    def _validate_data_sources_section(self, data_sources_config: Dict[str, Any]):
        """验证数据源配置节"""
        if not isinstance(data_sources_config, dict):
            self.errors.append("数据源配置必须是字典格式")
            return

        for source_name, source_config in data_sources_config.items():
            if not isinstance(source_config, dict):
                self.errors.append(f"数据源 {source_name} 配置必须是字典格式")
                continue

            if 'type' not in source_config:
                self.errors.append(f"数据源 {source_name} 缺少类型配置")

            # 验证数据源类型
            if 'type' in source_config:
                valid_types = ['tushare', 'akshare', 'yfinance', 'custom']
                if source_config['type'] not in valid_types:
                    self.errors.append(f"无效的数据源类型: {source_config['type']}")

    def _validate_backtest_section(self, backtest_config: Dict[str, Any]):
        """验证回测配置节"""
        if 'max_positions' in backtest_config:
            if not isinstance(backtest_config['max_positions'], int) or backtest_config['max_positions'] <= 0:
                self.errors.append("最大持仓数量必须是正整数")

        if 'position_size_pct' in backtest_config:
            pct = backtest_config['position_size_pct']
            if not isinstance(pct, (int, float)) or pct <= 0 or pct > 1:
                self.errors.append("仓位比例必须在0-1之间")

    def _validate_strategy_section(self, strategy_config: Dict[str, Any]):
        """验证策略配置节"""
        if 'position_management' in strategy_config:
            self._validate_position_management(
                strategy_config['position_management'])

    def _validate_position_management(self, position_mgmt: Dict[str, Any]):
        """验证仓位管理配置"""
        valid_methods = ['equal', 'kelly',
                         'volatility_adjusted', 'risk_parity']

        if 'allocation_method' in position_mgmt:
            if position_mgmt['allocation_method'] not in valid_methods:
                self.errors.append(
                    f"无效的仓位分配方法: {position_mgmt['allocation_method']}")

        size_fields = ['base_position_size',
                       'max_position_size', 'min_position_size']
        for field in size_fields:
            if field in position_mgmt:
                size = position_mgmt[field]
                if not isinstance(size, (int, float)) or size <= 0:
                    self.errors.append(f"{field} 必须是正数")

    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors.copy()

    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings.copy()


class SchemaValidator:
    """模式验证器"""

    def __init__(self):
        """初始化模式验证器"""
        self.errors = []

    def validate_against_schema(self, data: Any, schema: Dict[str, Any]) -> bool:
        """
        根据模式验证数据

        Args:
            data: 要验证的数据
            schema: 验证模式

        Returns:
            验证是否通过
        """
        self.errors.clear()
        self._validate_value(data, schema)
        return len(self.errors) == 0

    def _validate_value(self, value: Any, schema: Dict[str, Any]):
        """验证单个值"""
        # 类型验证
        if 'type' in schema:
            if not self._validate_type(value, schema['type']):
                self.errors.append(
                    f"类型不匹配: 期望 {schema['type']}, 实际 {type(value).__name__}")
                return

        # 必需字段验证
        if schema.get('required', False) and value is None:
            self.errors.append("字段是必需的")
            return

        # 枚举值验证
        if 'enum' in schema:
            if value not in schema['enum']:
                self.errors.append(f"值不在允许的枚举中: {value}")

        # 范围验证
        if 'minimum' in schema and isinstance(value, (int, float)):
            if value < schema['minimum']:
                self.errors.append(f"值小于最小值: {value} < {schema['minimum']}")

        if 'maximum' in schema and isinstance(value, (int, float)):
            if value > schema['maximum']:
                self.errors.append(f"值大于最大值: {value} > {schema['maximum']}")

        # 字符串长度验证
        if 'min_length' in schema and isinstance(value, str):
            if len(value) < schema['min_length']:
                self.errors.append(
                    f"字符串长度小于最小值: {len(value)} < {schema['min_length']}")

        if 'max_length' in schema and isinstance(value, str):
            if len(value) > schema['max_length']:
                self.errors.append(
                    f"字符串长度大于最大值: {len(value)} > {schema['max_length']}")

        # 正则表达式验证
        if 'pattern' in schema and isinstance(value, str):
            if not re.match(schema['pattern'], value):
                self.errors.append(f"字符串不匹配模式: {value}")

        # 数组验证
        if 'items' in schema and isinstance(value, list):
            for i, item in enumerate(value):
                self._validate_value(item, schema['items'])

        # 对象验证
        if 'properties' in schema and isinstance(value, dict):
            for prop_name, prop_schema in schema['properties'].items():
                if prop_name in value:
                    self._validate_value(value[prop_name], prop_schema)

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """验证类型"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }

        if expected_type not in type_mapping:
            return True  # 未知类型，跳过验证

        expected = type_mapping[expected_type]
        return isinstance(value, expected)

    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors.copy()


# 便捷验证函数
def validate_stock_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证股票数据

    Args:
        data: 股票数据字典

    Returns:
        (是否通过, 错误列表)
    """
    validator = DataValidator()
    is_valid = validator.validate_stock_data(data)
    return is_valid, validator.get_errors()


def validate_trading_signal(signal: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证交易信号

    Args:
        signal: 交易信号字典

    Returns:
        (是否通过, 错误列表)
    """
    validator = DataValidator()
    is_valid = validator.validate_trading_signal(signal)
    return is_valid, validator.get_errors()


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    验证配置

    Args:
        config: 配置字典

    Returns:
        (是否通过, 错误列表)
    """
    validator = ConfigValidator()
    is_valid = validator.validate_system_config(config)
    return is_valid, validator.get_errors()
