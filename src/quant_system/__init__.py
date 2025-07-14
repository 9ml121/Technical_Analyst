"""
量化投资系统核心模块

这个包包含了量化投资交易系统的所有核心功能：
- 数据获取和处理
- 策略引擎和回测
- 特征提取和分析
- 交易策略制定
"""

__version__ = "0.1.0"

# 延迟导入，避免循环依赖和启动时的依赖问题


def _lazy_import():
    """延迟导入模块"""
    import importlib

    # 核心模块
    core_modules = {}
    for module_name in ['data_provider', 'strategy_engine', 'backtest_engine',
                        'trading_strategy', 'feature_extraction', 'analysis_module']:
        try:
            core_modules[module_name] = importlib.import_module(
                f'.core.{module_name}', __name__)
        except ImportError as e:
            print(f"Warning: Failed to import {module_name}: {e}")

    # 数据模型
    model_modules = {}
    for module_name in ['stock_data', 'strategy_models', 'backtest_models']:
        try:
            model_modules[module_name] = importlib.import_module(
                f'.models.{module_name}', __name__)
        except ImportError as e:
            print(f"Warning: Failed to import {module_name}: {e}")

    # 工具模块
    util_modules = {}
    for module_name in ['config_loader', 'logger', 'validators', 'helpers']:
        try:
            util_modules[module_name] = importlib.import_module(
                f'.utils.{module_name}', __name__)
        except ImportError as e:
            print(f"Warning: Failed to import {module_name}: {e}")

    return {**core_modules, **model_modules, **util_modules}

# 提供便捷的导入函数


def get_module(module_name: str):
    """获取指定模块"""
    modules = _lazy_import()
    return modules.get(module_name)


# 定义可用模块列表
__all__ = [
    # 核心模块
    "data_provider",
    "strategy_engine",
    "backtest_engine",
    "trading_strategy",
    "feature_extraction",
    "analysis_module",

    # 数据模型
    "stock_data",
    "strategy_models",
    "backtest_models",

    # 工具模块
    "config_loader",
    "logger",
    "validators",
    "helpers",

    # 工具函数
    "get_module",
]
