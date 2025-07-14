"""
数据验证工具模块

提供各种数据验证功能
"""
import re
from datetime import date, datetime
from typing import Any, List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class StockCodeValidator:
    """股票代码验证器"""
    
    @staticmethod
    def is_valid_a_share(code: str) -> bool:
        """验证A股代码"""
        if not code or len(code) != 6:
            return False
        
        # A股代码规则
        patterns = [
            r'^00\d{4}$',  # 深市主板
            r'^30\d{4}$',  # 创业板
            r'^60\d{4}$',  # 沪市主板
            r'^68\d{4}$',  # 科创板
        ]
        
        return any(re.match(pattern, code) for pattern in patterns)
    
    @staticmethod
    def is_valid_hk_share(code: str) -> bool:
        """验证港股代码"""
        if not code:
            return False
        
        # 港股代码通常是5位数字
        return re.match(r'^\d{5}$', code) is not None
    
    @staticmethod
    def validate_code(code: str, market: str = "A") -> bool:
        """验证股票代码"""
        if market.upper() == "A":
            return StockCodeValidator.is_valid_a_share(code)
        elif market.upper() == "HK":
            return StockCodeValidator.is_valid_hk_share(code)
        else:
            return False

class DataValidator:
    """通用数据验证器"""
    
    @staticmethod
    def validate_price(price: float, min_price: float = 0.01, max_price: float = 10000) -> bool:
        """验证价格数据"""
        try:
            price = float(price)
            return min_price <= price <= max_price
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_volume(volume: int) -> bool:
        """验证成交量"""
        try:
            volume = int(volume)
            return volume >= 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_percentage(value: float, min_val: float = -1.0, max_val: float = 1.0) -> bool:
        """验证百分比数据"""
        try:
            value = float(value)
            return min_val <= value <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """验证日期范围"""
        try:
            return start_date <= end_date
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_config_dict(config: Dict[str, Any], required_keys: List[str]) -> List[str]:
        """验证配置字典"""
        errors = []
        
        for key in required_keys:
            if key not in config:
                errors.append(f"缺少必需的配置项: {key}")
        
        return errors

class StrategyValidator:
    """策略验证器"""
    
    @staticmethod
    def validate_selection_criteria(criteria: Dict[str, Any]) -> List[str]:
        """验证选股条件"""
        errors = []
        
        # 检查基础条件
        basic_criteria = criteria.get('basic_criteria', {})
        
        consecutive_days = basic_criteria.get('consecutive_days')
        if consecutive_days is not None:
            if not isinstance(consecutive_days, int) or consecutive_days < 1:
                errors.append("连续交易日数必须是正整数")
        
        min_return = basic_criteria.get('min_total_return')
        if min_return is not None:
            if not isinstance(min_return, (int, float)) or min_return < 0:
                errors.append("最小收益率必须是非负数")
        
        max_drawdown = basic_criteria.get('max_drawdown')
        if max_drawdown is not None:
            if not isinstance(max_drawdown, (int, float)) or max_drawdown < 0:
                errors.append("最大回撤必须是非负数")
        
        # 检查价格筛选
        price_filters = criteria.get('price_filters', {})
        
        min_price = price_filters.get('min_stock_price')
        max_price = price_filters.get('max_stock_price')
        
        if min_price is not None and max_price is not None:
            if min_price >= max_price:
                errors.append("最小股价必须小于最大股价")
        
        return errors
    
    @staticmethod
    def validate_backtest_config(config: Dict[str, Any]) -> List[str]:
        """验证回测配置"""
        errors = []
        
        # 检查必需字段
        required_fields = ['start_date', 'end_date', 'initial_capital']
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需的回测配置: {field}")
        
        # 检查日期
        if 'start_date' in config and 'end_date' in config:
            try:
                start_date = config['start_date']
                end_date = config['end_date']
                
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                if start_date >= end_date:
                    errors.append("开始日期必须早于结束日期")
            except ValueError as e:
                errors.append(f"日期格式错误: {e}")
        
        # 检查初始资金
        initial_capital = config.get('initial_capital')
        if initial_capital is not None:
            if not isinstance(initial_capital, (int, float)) or initial_capital <= 0:
                errors.append("初始资金必须是正数")
        
        return errors

def validate_stock_data(data: Dict[str, Any]) -> List[str]:
    """验证股票数据"""
    errors = []
    
    # 验证股票代码
    code = data.get('code')
    if not code:
        errors.append("股票代码不能为空")
    elif not StockCodeValidator.validate_code(code):
        errors.append(f"无效的股票代码: {code}")
    
    # 验证价格数据
    price_fields = ['open_price', 'close_price', 'high_price', 'low_price']
    for field in price_fields:
        price = data.get(field)
        if price is not None and not DataValidator.validate_price(price):
            errors.append(f"无效的价格数据: {field} = {price}")
    
    # 验证成交量
    volume = data.get('volume')
    if volume is not None and not DataValidator.validate_volume(volume):
        errors.append(f"无效的成交量: {volume}")
    
    # 验证价格关系
    high = data.get('high_price')
    low = data.get('low_price')
    open_price = data.get('open_price')
    close = data.get('close_price')
    
    if all(x is not None for x in [high, low, open_price, close]):
        if high < max(open_price, close, low):
            errors.append("最高价不能小于开盘价、收盘价或最低价")
        if low > min(open_price, close, high):
            errors.append("最低价不能大于开盘价、收盘价或最高价")
    
    return errors

def validate_config_file(config_path: str) -> bool:
    """验证配置文件是否存在且可读"""
    try:
        import os
        return os.path.exists(config_path) and os.access(config_path, os.R_OK)
    except Exception:
        return False

def sanitize_input(value: Any, data_type: type, default: Any = None) -> Any:
    """清理和转换输入数据"""
    try:
        if value is None:
            return default
        
        if data_type == str:
            return str(value).strip()
        elif data_type == int:
            return int(float(value))  # 先转float再转int，处理"1.0"这种情况
        elif data_type == float:
            return float(value)
        elif data_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        else:
            return data_type(value)
    
    except (ValueError, TypeError):
        logger.warning(f"无法转换数据 {value} 为类型 {data_type}, 使用默认值 {default}")
        return default
