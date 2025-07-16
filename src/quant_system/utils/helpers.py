"""
辅助函数模块

提供各种通用的辅助功能
"""
import os
import json
import pickle
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def ensure_dir(directory: Union[str, Path]) -> Path:
    """确保目录存在"""
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """安全除法，避免除零错误"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """计算百分比变化"""
    if old_value == 0:
        return 0.0
    return (new_value - old_value) / old_value


def format_currency(amount: float, currency: str = "¥") -> str:
    """格式化货币显示"""
    if amount >= 100000000:  # 亿
        return f"{currency}{amount/100000000:.2f}亿"
    elif amount >= 10000:    # 万
        return f"{currency}{amount/10000:.2f}万"
    else:
        return f"{currency}{amount:.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """格式化百分比显示"""
    return f"{value * 100:.{decimal_places}f}%"


def get_trading_dates(start_date: date, end_date: date, exclude_weekends: bool = True) -> List[date]:
    """获取交易日期列表"""
    dates = []
    current_date = start_date

    while current_date <= end_date:
        if not exclude_weekends or current_date.weekday() < 5:  # 0-4是周一到周五
            dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def is_trading_day(check_date: date) -> bool:
    """判断是否为交易日（简化版，仅排除周末）"""
    return check_date.weekday() < 5


def get_quarter(date_obj: date) -> str:
    """获取季度字符串"""
    quarter = (date_obj.month - 1) // 3 + 1
    return f"{date_obj.year}Q{quarter}"


def get_month_str(date_obj: date) -> str:
    """获取月份字符串"""
    return f"{date_obj.year}-{date_obj.month:02d}"


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化嵌套字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """反扁平化字典"""
    result = {}
    for key, value in d.items():
        keys = key.split(sep)
        current = result
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    return result


def save_to_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
    """保存数据到JSON文件"""
    try:
        file_path = Path(file_path)
        ensure_dir(file_path.parent)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

        logger.debug(f"数据已保存到JSON文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {e}")
        return False


def load_from_json(file_path: Union[str, Path]) -> Optional[Any]:
    """从JSON文件加载数据"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"JSON文件不存在: {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        logger.debug(f"从JSON文件加载数据: {file_path}")
        return data
    except Exception as e:
        logger.error(f"加载JSON文件失败: {e}")
        return None


def save_to_pickle(data: Any, file_path: Union[str, Path]) -> bool:
    """保存数据到pickle文件"""
    try:
        file_path = Path(file_path)
        ensure_dir(file_path.parent)

        with open(file_path, 'wb') as f:
            pickle.dump(data, f)

        logger.debug(f"数据已保存到pickle文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存pickle文件失败: {e}")
        return False


def load_from_pickle(file_path: Union[str, Path]) -> Optional[Any]:
    """从pickle文件加载数据"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            logger.warning(f"pickle文件不存在: {file_path}")
            return None

        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        logger.debug(f"从pickle文件加载数据: {file_path}")
        return data
    except Exception as e:
        logger.error(f"加载pickle文件失败: {e}")
        return None


def retry_on_exception(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"函数 {func.__name__} 第{attempt+1}次尝试失败: {e}, {delay}秒后重试")
                        import time
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"函数 {func.__name__} 重试{max_retries}次后仍然失败")

            raise last_exception

        return wrapper
    return decorator


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个字典"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def get_file_size(file_path: Union[str, Path]) -> int:
    """获取文件大小（字节）"""
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    if size_bytes >= 1024**3:  # GB
        return f"{size_bytes / 1024**3:.2f} GB"
    elif size_bytes >= 1024**2:  # MB
        return f"{size_bytes / 1024**2:.2f} MB"
    elif size_bytes >= 1024:  # KB
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"


def clean_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    import re
    # 移除或替换非法字符
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除多余的空格和点
    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' .')
    return cleaned


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    import platform
    import sys

    info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'hostname': platform.node(),
    }

    try:
        import psutil
        info.update({
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent
        })
    except ImportError:
        logger.debug("psutil未安装，无法获取详细系统信息")

    return info


def timing_context(operation_name: str):
    """计时上下文管理器"""
    class TimingContext:
        def __init__(self, name):
            self.name = name
            self.start_time = None

        def __enter__(self):
            self.start_time = datetime.now()
            logger.debug(f"开始执行: {self.name}")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = (datetime.now() - self.start_time).total_seconds()
            if exc_type is None:
                logger.info(f"操作完成: {self.name}, 耗时: {duration:.3f}秒")
            else:
                logger.error(
                    f"操作失败: {self.name}, 耗时: {duration:.3f}秒, 错误: {exc_val}")

    return TimingContext(operation_name)


def round_to_tick(price: float, tick_size: float = 0.01) -> float:
    """
    价格取整到最小变动单位

    Args:
        price: 价格
        tick_size: 最小变动单位

    Returns:
        取整后的价格
    """
    return round(price / tick_size) * tick_size


def format_number(value: float, decimal_places: int = 2) -> str:
    """
    格式化数字显示

    Args:
        value: 数值
        decimal_places: 小数位数

    Returns:
        格式化的数字字符串
    """
    return f"{value:,.{decimal_places}f}"


def validate_stock_code(code: str, market: str = "A") -> bool:
    """
    验证股票代码格式

    Args:
        code: 股票代码
        market: 市场类型 ("A", "HK")

    Returns:
        是否有效
    """
    import re
    if market == "A":
        return bool(re.match(r'^[0-9]{6}$', code))
    elif market == "HK":
        return bool(re.match(r'^[0-9]{5}$', code))
    return False


def normalize_stock_code(code: str, market: str = "A") -> str:
    """
    标准化股票代码

    Args:
        code: 股票代码
        market: 市场类型

    Returns:
        标准化的股票代码
    """
    code = code.strip().upper()
    if market == "A":
        return code.zfill(6)
    elif market == "HK":
        return code.zfill(5)
    return code


def get_next_trading_day(current_date: date) -> date:
    """
    获取下一个交易日

    Args:
        current_date: 当前日期

    Returns:
        下一个交易日
    """
    next_date = current_date + timedelta(days=1)
    while not is_trading_day(next_date):
        next_date += timedelta(days=1)
    return next_date


def get_previous_trading_day(current_date: date) -> date:
    """
    获取上一个交易日

    Args:
        current_date: 当前日期

    Returns:
        上一个交易日
    """
    prev_date = current_date - timedelta(days=1)
    while not is_trading_day(prev_date):
        prev_date -= timedelta(days=1)
    return prev_date


def clean_string(text: str) -> str:
    """
    清理字符串，去除多余空格和特殊字符

    Args:
        text: 输入文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    import re
    # 去除首尾空格
    text = text.strip()

    # 替换多个空格为单个空格
    text = re.sub(r'\s+', ' ', text)

    return text


def generate_hash(data: str) -> str:
    """
    生成数据的MD5哈希值

    Args:
        data: 输入数据

    Returns:
        MD5哈希值
    """
    import hashlib
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """
    格式化时间戳

    Args:
        timestamp: 时间戳，默认为当前时间

    Returns:
        格式化的时间字符串
    """
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


def load_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    加载YAML文件

    Args:
        file_path: 文件路径

    Returns:
        YAML数据
    """
    try:
        import yaml
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"加载YAML文件失败: {file_path}, 错误: {e}")
        return {}


def save_yaml_file(data: Dict[str, Any], file_path: Union[str, Path]):
    """
    保存YAML文件

    Args:
        data: 要保存的数据
        file_path: 文件路径
    """
    try:
        import yaml
        ensure_dir(Path(file_path).parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        logger.error(f"保存YAML文件失败: {file_path}, 错误: {e}")


def validate_config_value(value: Any, value_type: type,
                          min_value: Any = None, max_value: Any = None) -> bool:
    """
    验证配置值

    Args:
        value: 要验证的值
        value_type: 期望的类型
        min_value: 最小值
        max_value: 最大值

    Returns:
        是否有效
    """
    if not isinstance(value, value_type):
        return False

    if min_value is not None and value < min_value:
        return False

    if max_value is not None and value > max_value:
        return False

    return True
