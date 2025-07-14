"""
量化投资交易系统源码包
"""

__version__ = "0.1.0"
__author__ = "QuantTeam"
__email__ = "contact@quantsystem.com"
__description__ = "A comprehensive quantitative investment and trading system"

# 导出主要模块
from . import quant_system
from . import market_data

__all__ = [
    "quant_system",
    "market_data",
]
