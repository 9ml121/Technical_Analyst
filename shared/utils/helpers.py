"""
辅助函数工具 - 微服务架构共享工具
提供常用的辅助函数和工具方法
"""
import os
import math
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, date, timedelta
import json
import yaml


def ensure_dir(directory: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建

    Args:
        directory: 目录路径

    Returns:
        目录路径对象
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误

    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值

    Returns:
        除法结果
    """
    if denominator == 0 or math.isnan(denominator):
        return default
    return numerator / denominator


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    格式化百分比

    Args:
        value: 数值
        decimal_places: 小数位数

    Returns:
        格式化后的百分比字符串
    """
    return f"{value * 100:.{decimal_places}f}%"


def calculate_returns(prices: List[float]) -> List[float]:
    """
    计算收益率序列

    Args:
        prices: 价格序列

    Returns:
        收益率序列
    """
    if len(prices) < 2:
        return []

    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            returns.append((prices[i] - prices[i-1]) / prices[i-1])
        else:
            returns.append(0.0)

    return returns


def calculate_cumulative_returns(returns: List[float]) -> List[float]:
    """
    计算累积收益率

    Args:
        returns: 收益率序列

    Returns:
        累积收益率序列
    """
    if not returns:
        return []

    cumulative = [1.0]
    for ret in returns:
        cumulative.append(cumulative[-1] * (1 + ret))

    return cumulative[1:]  # 去掉初始值1.0


def calculate_drawdown(returns: List[float]) -> Tuple[List[float], float]:
    """
    计算回撤序列和最大回撤

    Args:
        returns: 收益率序列

    Returns:
        回撤序列和最大回撤
    """
    if not returns:
        return [], 0.0

    cumulative = calculate_cumulative_returns(returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdowns = [(cumulative[i] - running_max[i]) / running_max[i]
                 for i in range(len(cumulative))]

    max_drawdown = min(drawdowns)
    return drawdowns, abs(max_drawdown)


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.03) -> float:
    """
    计算夏普比率

    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率

    Returns:
        夏普比率
    """
    if not returns:
        return 0.0

    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate / 252  # 日化无风险利率

    if np.std(excess_returns) == 0:
        return 0.0

    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)


def calculate_volatility(returns: List[float]) -> float:
    """
    计算波动率

    Args:
        returns: 收益率序列

    Returns:
        年化波动率
    """
    if not returns:
        return 0.0

    return np.std(returns) * np.sqrt(252)


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    """
    计算胜率

    Args:
        trades: 交易记录列表

    Returns:
        胜率
    """
    if not trades:
        return 0.0

    winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
    return winning_trades / len(trades)


def calculate_profit_loss_ratio(trades: List[Dict[str, Any]]) -> float:
    """
    计算盈亏比

    Args:
        trades: 交易记录列表

    Returns:
        盈亏比
    """
    if not trades:
        return 0.0

    profits = [trade['pnl'] for trade in trades if trade.get('pnl', 0) > 0]
    losses = [abs(trade['pnl']) for trade in trades if trade.get('pnl', 0) < 0]

    if not profits or not losses:
        return 0.0

    avg_profit = np.mean(profits)
    avg_loss = np.mean(losses)

    return safe_divide(avg_profit, avg_loss)


def normalize_data(data: List[float]) -> List[float]:
    """
    数据标准化 (Z-score)

    Args:
        data: 原始数据

    Returns:
        标准化后的数据
    """
    if not data:
        return []

    data_array = np.array(data)
    mean = np.mean(data_array)
    std = np.std(data_array)

    if std == 0:
        return [0.0] * len(data)

    return [(x - mean) / std for x in data]


def min_max_normalize(data: List[float]) -> List[float]:
    """
    最小-最大标准化

    Args:
        data: 原始数据

    Returns:
        标准化后的数据
    """
    if not data:
        return []

    data_array = np.array(data)
    min_val = np.min(data_array)
    max_val = np.max(data_array)

    if max_val == min_val:
        return [0.5] * len(data)

    return [(x - min_val) / (max_val - min_val) for x in data]


def rolling_window(data: List[float], window_size: int) -> List[List[float]]:
    """
    创建滚动窗口

    Args:
        data: 数据序列
        window_size: 窗口大小

    Returns:
        滚动窗口列表
    """
    if len(data) < window_size:
        return []

    windows = []
    for i in range(len(data) - window_size + 1):
        windows.append(data[i:i + window_size])

    return windows


def exponential_moving_average(data: List[float], alpha: float) -> List[float]:
    """
    计算指数移动平均

    Args:
        data: 数据序列
        alpha: 平滑因子

    Returns:
        指数移动平均序列
    """
    if not data:
        return []

    ema = [data[0]]
    for i in range(1, len(data)):
        ema.append(alpha * data[i] + (1 - alpha) * ema[i-1])

    return ema


def simple_moving_average(data: List[float], window_size: int) -> List[float]:
    """
    计算简单移动平均

    Args:
        data: 数据序列
        window_size: 窗口大小

    Returns:
        简单移动平均序列
    """
    if len(data) < window_size:
        return []

    sma = []
    for i in range(window_size - 1, len(data)):
        window = data[i - window_size + 1:i + 1]
        sma.append(np.mean(window))

    return sma


def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    加载JSON文件

    Args:
        file_path: 文件路径

    Returns:
        JSON数据字典
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2):
    """
    保存JSON文件

    Args:
        data: 要保存的数据
        file_path: 文件路径
        indent: 缩进空格数
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    加载YAML文件

    Args:
        file_path: 文件路径

    Returns:
        YAML数据字典
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def save_yaml_file(data: Dict[str, Any], file_path: Union[str, Path]):
    """
    保存YAML文件

    Args:
        data: 要保存的数据
        file_path: 文件路径
    """
    file_path = Path(file_path)
    ensure_dir(file_path.parent)

    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    获取文件大小（MB）

    Args:
        file_path: 文件路径

    Returns:
        文件大小（MB）
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return 0.0

    return file_path.stat().st_size / (1024 * 1024)


def get_directory_size_mb(directory: Union[str, Path]) -> float:
    """
    获取目录大小（MB）

    Args:
        directory: 目录路径

    Returns:
        目录大小（MB）
    """
    directory = Path(directory)
    if not directory.exists():
        return 0.0

    total_size = 0
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size

    return total_size / (1024 * 1024)


def clean_old_files(directory: Union[str, Path], days: int = 30):
    """
    清理旧文件

    Args:
        directory: 目录路径
        days: 保留天数
    """
    directory = Path(directory)
    if not directory.exists():
        return

    cutoff_date = datetime.now() - timedelta(days=days)

    for file_path in directory.rglob('*'):
        if file_path.is_file():
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff_date:
                try:
                    file_path.unlink()
                    print(f"已删除旧文件: {file_path}")
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")


def generate_unique_id(prefix: str = "") -> str:
    """
    生成唯一ID

    Args:
        prefix: ID前缀

    Returns:
        唯一ID字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    import uuid
    unique_part = str(uuid.uuid4())[:8]

    if prefix:
        return f"{prefix}_{timestamp}_{unique_part}"
    else:
        return f"{timestamp}_{unique_part}"


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    验证日期范围

    Args:
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        是否有效
    """
    return start_date <= end_date


def get_trading_days(start_date: date, end_date: date, exclude_weekends: bool = True) -> List[date]:
    """
    获取交易日列表

    Args:
        start_date: 开始日期
        end_date: 结束日期
        exclude_weekends: 是否排除周末

    Returns:
        交易日列表
    """
    if not validate_date_range(start_date, end_date):
        return []

    trading_days = []
    current_date = start_date

    while current_date <= end_date:
        if not exclude_weekends or current_date.weekday() < 5:  # 0-4 是周一到周五
            trading_days.append(current_date)
        current_date += timedelta(days=1)

    return trading_days


def format_number(number: float, decimal_places: int = 2) -> str:
    """
    格式化数字

    Args:
        number: 数字
        decimal_places: 小数位数

    Returns:
        格式化后的字符串
    """
    if abs(number) >= 1e6:
        return f"{number/1e6:.{decimal_places}f}M"
    elif abs(number) >= 1e3:
        return f"{number/1e3:.{decimal_places}f}K"
    else:
        return f"{number:.{decimal_places}f}"


def is_valid_stock_code(code: str) -> bool:
    """
    验证股票代码格式

    Args:
        code: 股票代码

    Returns:
        是否有效
    """
    if not code or not isinstance(code, str):
        return False

    # 简单的股票代码验证规则
    # 沪市: 600xxx, 601xxx, 603xxx, 688xxx
    # 深市: 000xxx, 002xxx, 300xxx
    # 北交所: 8xxxxx
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

    import re
    return any(re.match(pattern, code) for pattern in valid_patterns)


def extract_stock_info_from_code(code: str) -> Dict[str, str]:
    """
    从股票代码提取信息

    Args:
        code: 股票代码

    Returns:
        股票信息字典
    """
    if not is_valid_stock_code(code):
        return {}

    if code.startswith('600') or code.startswith('601') or code.startswith('603'):
        return {
            'exchange': 'SSE',
            'market': '主板',
            'code': code
        }
    elif code.startswith('688'):
        return {
            'exchange': 'SSE',
            'market': '科创板',
            'code': code
        }
    elif code.startswith('000'):
        return {
            'exchange': 'SZSE',
            'market': '主板',
            'code': code
        }
    elif code.startswith('002'):
        return {
            'exchange': 'SZSE',
            'market': '中小板',
            'code': code
        }
    elif code.startswith('300'):
        return {
            'exchange': 'SZSE',
            'market': '创业板',
            'code': code
        }
    elif code.startswith('8'):
        return {
            'exchange': 'BSE',
            'market': '北交所',
            'code': code
        }
    else:
        return {
            'exchange': 'UNKNOWN',
            'market': 'UNKNOWN',
            'code': code
        }
