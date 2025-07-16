#!/usr/bin/env python3
"""
智能缓存管理器

实现数据缓存、过期策略、性能优化和缓存监控
"""

import os
import json
import pickle
import hashlib
import time
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """缓存策略"""
    NONE = "none"           # 不缓存
    SHORT = "short"         # 短期缓存 (5分钟)
    MEDIUM = "medium"       # 中期缓存 (1小时)
    LONG = "long"           # 长期缓存 (1天)
    PERMANENT = "permanent"  # 永久缓存


@dataclass
class CacheConfig:
    """缓存配置"""
    strategy: CacheStrategy
    ttl_seconds: int  # 生存时间(秒)
    max_size_mb: int  # 最大缓存大小(MB)
    compress: bool = True  # 是否压缩
    enable_monitoring: bool = True  # 是否启用监控


@dataclass
class CacheStats:
    """缓存统计"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_size_mb: float = 0.0
    hit_rate: float = 0.0
    last_cleanup: Optional[datetime] = None
    cleanup_count: int = 0


class CacheManager:
    """智能缓存管理器"""

    def __init__(self, cache_dir: str = "cache", config: Optional[CacheConfig] = None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录
            config: 缓存配置
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 默认配置
        self.default_config = CacheConfig(
            strategy=CacheStrategy.MEDIUM,
            ttl_seconds=3600,  # 1小时
            max_size_mb=100,   # 100MB
            compress=True,
            enable_monitoring=True
        )

        self.config = config or self.default_config
        self.stats = CacheStats()
        self.cache_index = {}  # 缓存索引
        self.metadata_file = self.cache_dir / "cache_metadata.json"

        # 加载缓存索引
        self._load_cache_index()

        # 启动监控
        if self.config.enable_monitoring:
            self._start_monitoring()

    def _load_cache_index(self):
        """加载缓存索引"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cache_index = data.get('index', {})
                    self.stats = CacheStats(**data.get('stats', {}))
                    logger.info(f"加载缓存索引，共 {len(self.cache_index)} 个缓存项")
        except Exception as e:
            logger.error(f"加载缓存索引失败: {e}")
            self.cache_index = {}

    def _save_cache_index(self):
        """保存缓存索引"""
        try:
            data = {
                'index': self.cache_index,
                'stats': asdict(self.stats),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存索引失败: {e}")

    def _generate_cache_key(self, data_type: str, identifier: str, **kwargs) -> str:
        """生成缓存键"""
        # 创建唯一标识符
        key_parts = [data_type, identifier]

        # 添加额外参数
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        key_string = "|".join(key_parts)

        # 生成MD5哈希
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.cache"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache_index:
            return False

        cache_info = self.cache_index[cache_key]
        created_time = datetime.fromisoformat(cache_info['created_time'])
        ttl_seconds = cache_info.get('ttl_seconds', self.config.ttl_seconds)

        # 检查是否过期
        if datetime.now() - created_time > timedelta(seconds=ttl_seconds):
            return False

        # 检查文件是否存在
        cache_file = self._get_cache_file_path(cache_key)
        if not cache_file.exists():
            return False

        return True

    def get(self, data_type: str, identifier: str, **kwargs) -> Optional[Any]:
        """
        获取缓存数据

        Args:
            data_type: 数据类型 (如: 'historical_data', 'realtime_data')
            identifier: 标识符 (如: 股票代码)
            **kwargs: 额外参数

        Returns:
            缓存的数据，如果不存在或过期则返回None
        """
        cache_key = self._generate_cache_key(data_type, identifier, **kwargs)

        self.stats.total_requests += 1

        if not self._is_cache_valid(cache_key):
            self.stats.cache_misses += 1
            return None

        try:
            cache_file = self._get_cache_file_path(cache_key)

            # 读取缓存数据
            with open(cache_file, 'rb') as f:
                if self.config.compress:
                    import gzip
                    with gzip.open(f, 'rb') as gz:
                        data = pickle.load(gz)
                else:
                    data = pickle.load(f)

            self.stats.cache_hits += 1
            logger.debug(f"缓存命中: {cache_key}")

            return data

        except Exception as e:
            logger.error(f"读取缓存失败 {cache_key}: {e}")
            self.stats.cache_misses += 1
            return None

    def set(self, data_type: str, identifier: str, data: Any,
            strategy: Optional[CacheStrategy] = None, **kwargs) -> bool:
        """
        设置缓存数据

        Args:
            data_type: 数据类型
            identifier: 标识符
            data: 要缓存的数据
            strategy: 缓存策略
            **kwargs: 额外参数

        Returns:
            是否成功设置缓存
        """
        cache_key = self._generate_cache_key(data_type, identifier, **kwargs)

        # 确定缓存策略
        cache_strategy = strategy or self.config.strategy

        if cache_strategy == CacheStrategy.NONE:
            return False

        # 计算TTL
        ttl_map = {
            CacheStrategy.SHORT: 300,      # 5分钟
            CacheStrategy.MEDIUM: 3600,    # 1小时
            CacheStrategy.LONG: 86400,     # 1天
            CacheStrategy.PERMANENT: 0     # 永久
        }
        ttl_seconds = ttl_map.get(cache_strategy, self.config.ttl_seconds)

        try:
            cache_file = self._get_cache_file_path(cache_key)

            # 写入缓存数据
            with open(cache_file, 'wb') as f:
                if self.config.compress:
                    import gzip
                    with gzip.open(f, 'wb') as gz:
                        pickle.dump(data, gz)
                else:
                    pickle.dump(data, f)

            # 更新缓存索引
            file_size = cache_file.stat().st_size / (1024 * 1024)  # MB

            self.cache_index[cache_key] = {
                'data_type': data_type,
                'identifier': identifier,
                'strategy': cache_strategy.value,
                'ttl_seconds': ttl_seconds,
                'created_time': datetime.now().isoformat(),
                'file_size_mb': file_size,
                'extra_params': kwargs
            }

            # 保存索引
            self._save_cache_index()

            logger.debug(f"缓存设置成功: {cache_key} (大小: {file_size:.2f}MB)")
            return True

        except Exception as e:
            logger.error(f"设置缓存失败 {cache_key}: {e}")
            return False

    def delete(self, data_type: str, identifier: str, **kwargs) -> bool:
        """删除缓存数据"""
        cache_key = self._generate_cache_key(data_type, identifier, **kwargs)

        try:
            cache_file = self._get_cache_file_path(cache_key)

            if cache_file.exists():
                cache_file.unlink()

            if cache_key in self.cache_index:
                del self.cache_index[cache_key]
                self._save_cache_index()

            logger.debug(f"缓存删除成功: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"删除缓存失败 {cache_key}: {e}")
            return False

    def clear(self, data_type: Optional[str] = None) -> int:
        """
        清理缓存

        Args:
            data_type: 指定数据类型，如果为None则清理所有

        Returns:
            清理的缓存项数量
        """
        cleared_count = 0

        try:
            keys_to_delete = []

            for cache_key, cache_info in self.cache_index.items():
                if data_type is None or cache_info['data_type'] == data_type:
                    keys_to_delete.append(cache_key)

            for cache_key in keys_to_delete:
                cache_file = self._get_cache_file_path(cache_key)

                if cache_file.exists():
                    cache_file.unlink()

                del self.cache_index[cache_key]
                cleared_count += 1

            if cleared_count > 0:
                self._save_cache_index()
                logger.info(f"清理了 {cleared_count} 个缓存项")

            return cleared_count

        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            return 0

    def cleanup_expired(self) -> int:
        """清理过期的缓存"""
        expired_count = 0

        try:
            keys_to_delete = []

            for cache_key, cache_info in self.cache_index.items():
                if not self._is_cache_valid(cache_key):
                    keys_to_delete.append(cache_key)

            for cache_key in keys_to_delete:
                cache_file = self._get_cache_file_path(cache_key)

                if cache_file.exists():
                    cache_file.unlink()

                del self.cache_index[cache_key]
                expired_count += 1

            if expired_count > 0:
                self._save_cache_index()
                self.stats.cleanup_count += 1
                self.stats.last_cleanup = datetime.now()
                logger.info(f"清理了 {expired_count} 个过期缓存项")

            return expired_count

        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            return 0

    def cleanup_by_size(self) -> int:
        """按大小清理缓存"""
        try:
            # 计算总大小
            total_size = sum(info['file_size_mb']
                             for info in self.cache_index.values())

            if total_size <= self.config.max_size_mb:
                return 0

            # 按创建时间排序，删除最旧的
            sorted_items = sorted(
                self.cache_index.items(),
                key=lambda x: x[1]['created_time']
            )

            cleared_count = 0
            current_size = total_size

            for cache_key, cache_info in sorted_items:
                if current_size <= self.config.max_size_mb * 0.8:  # 清理到80%
                    break

                cache_file = self._get_cache_file_path(cache_key)

                if cache_file.exists():
                    cache_file.unlink()

                del self.cache_index[cache_key]
                current_size -= cache_info['file_size_mb']
                cleared_count += 1

            if cleared_count > 0:
                self._save_cache_index()
                logger.info(f"按大小清理了 {cleared_count} 个缓存项")

            return cleared_count

        except Exception as e:
            logger.error(f"按大小清理缓存失败: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        # 计算命中率
        if self.stats.total_requests > 0:
            self.stats.hit_rate = self.stats.cache_hits / self.stats.total_requests

        # 计算总大小
        self.stats.total_size_mb = sum(
            info['file_size_mb'] for info in self.cache_index.values()
        )

        return {
            'stats': asdict(self.stats),
            'cache_count': len(self.cache_index),
            'cache_dir': str(self.cache_dir),
            'config': asdict(self.config),
            'cache_types': self._get_cache_types_stats()
        }

    def _get_cache_types_stats(self) -> Dict[str, int]:
        """获取各类型缓存的统计"""
        type_stats = {}
        for cache_info in self.cache_index.values():
            data_type = cache_info['data_type']
            type_stats[data_type] = type_stats.get(data_type, 0) + 1
        return type_stats

    def _start_monitoring(self):
        """启动监控"""
        # 定期清理过期缓存
        import threading

        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # 每5分钟检查一次
                    self.cleanup_expired()
                    self.cleanup_by_size()
                except Exception as e:
                    logger.error(f"缓存清理工作线程错误: {e}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("缓存监控已启动")

    def get_cache_info(self, data_type: str, identifier: str, **kwargs) -> Optional[Dict[str, Any]]:
        """获取缓存信息"""
        cache_key = self._generate_cache_key(data_type, identifier, **kwargs)

        if cache_key in self.cache_index:
            cache_info = self.cache_index[cache_key].copy()
            cache_info['is_valid'] = self._is_cache_valid(cache_key)
            return cache_info

        return None

    def preload_cache(self, data_list: List[Dict[str, Any]]) -> int:
        """
        预加载缓存

        Args:
            data_list: 数据列表，每个元素包含 data_type, identifier, data

        Returns:
            成功预加载的数量
        """
        success_count = 0

        for item in data_list:
            try:
                data_type = item['data_type']
                identifier = item['identifier']
                data = item['data']
                strategy = item.get('strategy', CacheStrategy.MEDIUM)

                if self.set(data_type, identifier, data, strategy):
                    success_count += 1

            except Exception as e:
                logger.error(f"预加载缓存失败: {e}")

        logger.info(f"预加载了 {success_count}/{len(data_list)} 个缓存项")
        return success_count
