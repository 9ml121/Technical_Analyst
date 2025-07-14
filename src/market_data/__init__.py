"""
市场数据获取系统

独立的股票行情数据获取模块，支持：
- A股实时行情数据
- 港股和港股通数据
- 多数据源支持
- 数据处理和验证
"""

__version__ = "0.1.0"

# 延迟导入，避免启动时的依赖问题


def get_eastmoney_api():
    """获取东方财富API实例"""
    from .fetchers.eastmoney_api import EastMoneyAPI
    return EastMoneyAPI()


def get_tushare_api(token=None):
    """获取Tushare API实例"""
    from .fetchers.tushare_api import TushareAPI
    return TushareAPI(token)


def get_data_processor():
    """获取数据处理器实例"""
    from .processors.data_processor import MarketDataProcessor
    return MarketDataProcessor()


__all__ = [
    "fetchers",
    "processors",
    "get_eastmoney_api",
    "get_tushare_api",
    "get_data_processor",
]
