"""
配置文件加载器

支持YAML、JSON等多种格式的配置文件加载和验证，包含性能优化
"""
import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging
import threading
import time
from functools import lru_cache

# 使用模块工厂模式导入依赖


def _get_dependencies():
    """获取依赖模块"""
    try:
        from quant_system.utils.cache import LRUCache
        from quant_system.utils.performance import performance_timer
        return LRUCache, performance_timer
    except ImportError:
        return None, None


# 获取依赖
LRUCache, performance_timer = _get_dependencies()

# 如果性能工具不可用，提供空的装饰器
if not performance_timer:
    def performance_timer(func):
        return func

# 如果缓存工具不可用，提供简单的LRU缓存实现
if not LRUCache:
    class LRUCache:
        def __init__(self, max_size=100, ttl=None):
            self.cache = {}
            self.max_size = max_size

        def get(self, key):
            return self.cache.get(key)

        def put(self, key, value):
            if len(self.cache) >= self.max_size:
                # 简单清理策略
                self.cache.clear()
            self.cache[key] = value

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置文件加载器"""

    def __init__(self, config_dir: str = "config", enable_cache: bool = True, cache_ttl: int = 3600):
        """
        初始化配置加载器

        Args:
            config_dir: 配置文件目录
            enable_cache: 是否启用缓存
            cache_ttl: 缓存生存时间(秒)
        """
        self.config_dir = Path(config_dir)
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl

        # 初始化缓存
        if self.enable_cache:
            if LRUCache:
                self._cache = LRUCache(max_size=100, ttl=cache_ttl)
                self._schema_cache = LRUCache(max_size=50, ttl=cache_ttl)
            else:
                self._cache = LRUCache(max_size=100)
                self._schema_cache = LRUCache(max_size=50)
        else:
            self._cache = None
            self._schema_cache = None

        # 文件监控
        self._file_timestamps = {}
        self._lock = threading.RLock()

        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / "environments").mkdir(exist_ok=True)
        (self.config_dir / "strategies").mkdir(exist_ok=True)

    @performance_timer
    def load_config(self, config_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        加载配置文件

        Args:
            config_name: 配置文件名 (不含扩展名)
            use_cache: 是否使用缓存

        Returns:
            配置字典
        """
        with self._lock:
            # 检查缓存
            if use_cache and self.enable_cache and self._cache:
                cached_config = self._cache.get(config_name)
                if cached_config is not None:
                    # 检查文件是否有更新
                    if not self._is_config_outdated(config_name):
                        return cached_config

            config = {}

            # 1. 加载默认配置
            default_config = self._load_file_with_cache(
                self.config_dir / "default.yaml")
            if default_config:
                config.update(default_config)

            # 2. 加载环境特定配置
            env_config = self._load_file_with_cache(
                self.config_dir / "environments" / f"{self.environment}.yaml")
            if env_config:
                config = self._deep_merge(config, env_config)

            # 3. 加载具体配置文件
            specific_config = self._load_config_file(config_name)
            if specific_config:
                config = self._deep_merge(config, specific_config)

            # 4. 环境变量覆盖
            config = self._apply_env_overrides(config)

            # 更新缓存
            if use_cache and self.enable_cache and self._cache:
                self._cache.put(config_name, config)
                self._update_file_timestamps(config_name)

        logger.info(f"配置加载完成: {config_name}")
        return config

    def _load_file_with_cache(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """带缓存的文件加载"""
        cache_key = str(file_path)

        if self.enable_cache and self._cache:
            cached_content = self._cache.get(cache_key)
            if cached_content is not None:
                # 检查文件时间戳
                if file_path.exists():
                    current_mtime = file_path.stat().st_mtime
                    cached_mtime = self._file_timestamps.get(cache_key, 0)
                    if current_mtime <= cached_mtime:
                        return cached_content

        # 加载文件
        content = self._load_file(file_path)

        # 更新缓存
        if content and self.enable_cache and self._cache:
            self._cache.put(cache_key, content)
            if file_path.exists():
                self._file_timestamps[cache_key] = file_path.stat().st_mtime

        return content

    def _is_config_outdated(self, config_name: str) -> bool:
        """检查配置是否过期"""
        config_files = [
            self.config_dir / "default.yaml",
            self.config_dir / "environments" / f"{self.environment}.yaml",
            self.config_dir / f"{config_name}.yaml",
            self.config_dir / "strategies" / f"{config_name}.yaml"
        ]

        for file_path in config_files:
            if file_path.exists():
                cache_key = str(file_path)
                current_mtime = file_path.stat().st_mtime
                cached_mtime = self._file_timestamps.get(cache_key, 0)
                if current_mtime > cached_mtime:
                    return True

        return False

    def _update_file_timestamps(self, config_name: str):
        """更新文件时间戳"""
        config_files = [
            self.config_dir / "default.yaml",
            self.config_dir / "environments" / f"{self.environment}.yaml",
            self.config_dir / f"{config_name}.yaml",
            self.config_dir / "strategies" / f"{config_name}.yaml"
        ]

        for file_path in config_files:
            if file_path.exists():
                cache_key = str(file_path)
                self._file_timestamps[cache_key] = file_path.stat().st_mtime

    def clear_cache(self):
        """清空缓存"""
        with self._lock:
            if self._cache:
                if hasattr(self._cache, 'clear'):
                    self._cache.clear()
                else:
                    self._cache = LRUCache(max_size=100)

            if self._schema_cache:
                if hasattr(self._schema_cache, 'clear'):
                    self._schema_cache.clear()
                else:
                    self._schema_cache = LRUCache(max_size=50)

            self._file_timestamps.clear()

        logger.info("配置缓存已清空")

    def load_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """
        加载策略配置

        Args:
            strategy_name: 策略名称

        Returns:
            策略配置字典
        """
        strategy_file = self.config_dir / \
            "strategies" / f"{strategy_name}.yaml"

        if not strategy_file.exists():
            # 尝试加载默认策略配置
            strategy_file = self.config_dir / "strategies" / "default.yaml"

        if strategy_file.exists():
            return self._load_file(strategy_file)
        else:
            logger.warning(f"策略配置文件不存在: {strategy_name}")
            return {}

    def load_data_sources_config(self) -> Dict[str, Any]:
        """
        加载数据源配置

        Returns:
            数据源配置字典
        """
        data_sources_file = self.config_dir / "data_sources.yaml"

        if data_sources_file.exists():
            return self._load_file(data_sources_file)
        else:
            logger.warning("数据源配置文件不存在")
            return {}

    def get_environment_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        获取环境特定配置

        Args:
            environment: 环境名称，默认使用当前环境

        Returns:
            环境配置字典
        """
        env = environment or self.environment
        env_file = self.config_dir / "environments" / f"{env}.yaml"

        if env_file.exists():
            return self._load_file(env_file)
        else:
            logger.warning(f"环境配置文件不存在: {env}")
            return {}

    def list_available_strategies(self) -> List[str]:
        """
        列出可用的策略配置

        Returns:
            策略名称列表
        """
        strategies_dir = self.config_dir / "strategies"
        if not strategies_dir.exists():
            return []

        strategies = []
        for file_path in strategies_dir.glob("*.yaml"):
            if file_path.name != "default.yaml":
                strategies.append(file_path.stem)

        return sorted(strategies)

    def list_available_environments(self) -> List[str]:
        """
        列出可用的环境配置

        Returns:
            环境名称列表
        """
        env_dir = self.config_dir / "environments"
        if not env_dir.exists():
            return []

        environments = []
        for file_path in env_dir.glob("*.yaml"):
            environments.append(file_path.stem)

        return sorted(environments)

    def _load_config_file(self, config_name: str) -> Optional[Dict[str, Any]]:
        """加载指定的配置文件"""
        # 尝试不同的文件路径和格式
        possible_paths = [
            self.config_dir / f"{config_name}.yaml",
            self.config_dir / f"{config_name}.yml",
            self.config_dir / f"{config_name}.json",
            self.config_dir / "strategies" / f"{config_name}.yaml",
            Path(config_name),  # 直接路径
        ]

        for path in possible_paths:
            if path.exists():
                return self._load_file(path)

        logger.warning(f"配置文件未找到: {config_name}")
        return None

    def _load_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载单个配置文件"""
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif file_path.suffix.lower() == '.json':
                    return json.load(f) or {}
                else:
                    # 尝试YAML格式
                    return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载配置文件失败 {file_path}: {e}")
            return None

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并字典"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        # 定义环境变量映射
        env_mappings = {
            'DATABASE_PATH': ['database', 'path'],
            'LOG_LEVEL': ['logging', 'level'],
            'INITIAL_CAPITAL': ['backtest', 'initial_capital'],
            'MAX_POSITIONS': ['backtest', 'max_positions'],
            'COMMISSION_RATE': ['backtest', 'commission_rate'],
        }

        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # 类型转换
                try:
                    if env_value.lower() in ('true', 'false'):
                        env_value = env_value.lower() == 'true'
                    elif '.' in env_value:
                        env_value = float(env_value)
                    elif env_value.isdigit():
                        env_value = int(env_value)
                except ValueError:
                    pass  # 保持字符串类型

                # 设置配置值
                current = config
                for key in config_path[:-1]:
                    if key not in current:
                        current[key] = {}
                    current = current[key]
                current[config_path[-1]] = env_value

        return config

    def validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        验证配置格式

        Args:
            config: 配置字典
            schema: 验证模式

        Returns:
            是否验证通过
        """
        try:
            # 简单的配置验证
            for key, expected_type in schema.items():
                if key in config:
                    if not isinstance(config[key], expected_type):
                        logger.error(f"配置项 {key} 类型错误，期望 {expected_type}")
                        return False
            return True
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False

    def save_config(self, config: Dict[str, Any], file_path: Union[str, Path]):
        """
        保存配置到文件

        Args:
            config: 配置字典
            file_path: 文件路径
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config, f, default_flow_style=False,
                              allow_unicode=True)
                elif file_path.suffix.lower() == '.json':
                    json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    # 默认使用YAML格式
                    yaml.dump(config, f, default_flow_style=False,
                              allow_unicode=True)

            logger.info(f"配置已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def clear_cache(self):
        """清空配置缓存"""
        self._cache.clear()
        logger.info("配置缓存已清空")


# 全局配置加载器实例
config_loader = ConfigLoader()


def load_config(config_name: str) -> Dict[str, Any]:
    """便捷函数：加载配置"""
    return config_loader.load_config(config_name)


def load_strategy_config(strategy_name: str) -> Dict[str, Any]:
    """便捷函数：加载策略配置"""
    return config_loader.load_strategy_config(strategy_name)
