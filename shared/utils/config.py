"""
配置文件加载器 - 微服务架构共享工具
支持YAML、JSON等多种格式的配置文件加载和验证
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

logger = logging.getLogger(__name__)


class SimpleCache:
    """简单的缓存实现"""

    def __init__(self, max_size=100, ttl=None):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.timestamps = {}

    def get(self, key):
        if key not in self.cache:
            return None

        # 检查TTL
        if self.ttl and time.time() - self.timestamps.get(key, 0) > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None

        return self.cache[key]

    def put(self, key, value):
        if len(self.cache) >= self.max_size:
            # 简单清理策略：清除最旧的条目
            oldest_key = min(self.timestamps.keys(),
                             key=lambda k: self.timestamps[k])
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]

        self.cache[key] = value
        self.timestamps[key] = time.time()

    def clear(self):
        self.cache.clear()
        self.timestamps.clear()


def performance_timer(func):
    """性能计时装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(
            f"{func.__name__} 执行时间: {(end_time - start_time) * 1000:.2f}ms")
        return result
    return wrapper


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
            self._cache = SimpleCache(max_size=100, ttl=cache_ttl)
            self._schema_cache = SimpleCache(max_size=50, ttl=cache_ttl)
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
        """清除缓存"""
        if self._cache:
            self._cache.clear()
        if self._schema_cache:
            self._schema_cache.clear()
        self._file_timestamps.clear()
        logger.info("配置缓存已清除")

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
        # 这里可以实现环境变量覆盖逻辑
        # 例如：QUANT_SYSTEM_DATABASE_HOST 覆盖 config['database']['host']
        return config

    def validate_config(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        验证配置

        Args:
            config: 配置字典
            schema: 配置模式

        Returns:
            验证是否通过
        """
        # 这里可以实现配置验证逻辑
        return True

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
                if file_path.suffix.lower() == '.json':
                    json.dump(config, f, indent=2, ensure_ascii=False)
                else:
                    yaml.dump(config, f, default_flow_style=False,
                              allow_unicode=True)
            logger.info(f"配置已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")


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

    def _validate_database_section(self, database_config: Dict[str, Any]):
        """验证数据库配置节"""
        required_fields = ['host', 'port', 'database']
        for field in required_fields:
            if field not in database_config:
                self.errors.append(f"数据库配置缺少必需字段: {field}")

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


# 便捷函数
def load_config(config_name: str) -> Dict[str, Any]:
    """便捷的配置加载函数"""
    loader = ConfigLoader()
    return loader.load_config(config_name)


def load_strategy_config(strategy_name: str) -> Dict[str, Any]:
    """便捷的策略配置加载函数"""
    loader = ConfigLoader()
    return loader.load_strategy_config(strategy_name)
