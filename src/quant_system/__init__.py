"""
量化投资系统核心模块

这个包包含了量化投资交易系统的所有核心功能：
- 数据获取和处理
- 策略引擎和回测
- 特征提取和分析
- 交易策略制定
"""

__version__ = "0.1.0"

# 采用延迟导入机制，避免循环依赖
# 使用工厂模式提供模块访问


class ModuleFactory:
    """模块工厂类，提供统一的模块访问接口"""

    def __init__(self):
        self._modules = {}
        self._import_lock = {}

    def get_module(self, module_name: str):
        """获取指定模块，支持延迟加载"""
        if module_name not in self._modules:
            if module_name not in self._import_lock:
                self._import_lock[module_name] = True
                try:
                    self._modules[module_name] = self._import_module(
                        module_name)
                except ImportError as e:
                    print(f"Warning: Failed to import {module_name}: {e}")
                    self._modules[module_name] = None
                finally:
                    del self._import_lock[module_name]

        return self._modules[module_name]

    def _import_module(self, module_name: str):
        """导入指定模块"""
        import importlib

        module_mapping = {
            # 核心模块
            'data_provider': 'quant_system.core.data_provider',
            'strategy_engine': 'quant_system.core.strategy_engine',
            'backtest_engine': 'quant_system.core.backtest_engine',
            'trading_strategy': 'quant_system.core.trading_strategy',
            'feature_extraction': 'quant_system.core.feature_extraction',
            'analysis_module': 'quant_system.core.analysis_module',
            'ml_enhanced_strategy': 'quant_system.core.ml_enhanced_strategy',

            # 数据模型
            'stock_data': 'quant_system.models.stock_data',
            'strategy_models': 'quant_system.models.strategy_models',
            'backtest_models': 'quant_system.models.backtest_models',

            # 工具模块
            'config_loader': 'quant_system.utils.config_loader',
            'logger': 'quant_system.utils.logger',
            'validators': 'quant_system.utils.validators',
            'helpers': 'quant_system.utils.helpers',
            'performance': 'quant_system.utils.performance',
            'cache': 'quant_system.utils.cache',
            'concurrent': 'quant_system.utils.concurrent',
            'config_validator': 'quant_system.utils.config_validator',
        }

        if module_name in module_mapping:
            return importlib.import_module(module_mapping[module_name])
        else:
            raise ImportError(f"Unknown module: {module_name}")


# 创建全局模块工厂实例
_module_factory = ModuleFactory()


def get_module(module_name: str):
    """获取指定模块的便捷函数"""
    return _module_factory.get_module(module_name)


# 定义可用模块列表
__all__ = [
    # 核心模块
    "data_provider",
    "strategy_engine",
    "backtest_engine",
    "trading_strategy",
    "feature_extraction",
    "analysis_module",
    "ml_enhanced_strategy",

    # 数据模型
    "stock_data",
    "strategy_models",
    "backtest_models",

    # 工具模块
    "config_loader",
    "logger",
    "validators",
    "helpers",
    "performance",
    "cache",
    "concurrent",
    "config_validator",

    # 工具函数
    "get_module",
    "ModuleFactory",
]
