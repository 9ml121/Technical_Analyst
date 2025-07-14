"""
量化投资系统核心功能模块

包含系统的核心业务逻辑：
- data_provider: 数据获取和管理
- strategy_engine: 选股策略引擎
- backtest_engine: 回测引擎
- trading_strategy: 交易策略
- feature_extraction: 特征提取
- analysis_module: 数据分析
"""

# 不在包初始化时导入，避免依赖问题
# 使用时再导入具体模块

__all__ = [
    "data_provider",
    "strategy_engine",
    "backtest_engine",
    "trading_strategy",
    "feature_extraction",
    "analysis_module",
]
