"""
缓存系统

提供多层次缓存机制，提升系统性能
"""

import time
import pickle
import hashlib
import threading
from typing import Any, Dict, Optional, Callable, Union, Tuple
from functools import wraps
from collections import OrderedDict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class LRUCache:
    """LRU (Least Recently Used) 缓存实现"""

    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        """
        初始化LRU缓存

        Args:
            max_size: 最大缓存条目数
            ttl: 生存时间(秒)，None表示永不过期
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def _is_expired(self, key: str) -> bool:
        """检查缓存项是否过期"""
        if self.ttl is None:
            return False

        timestamp = self.timestamps.get(key)
        if timestamp is None:
            return True

        return time.time() - timestamp > self.ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            if self._is_expired(key):
                self._remove(key)
                self.misses += 1
                return None

            # 移动到末尾（最近使用）
            value = self.cache.pop(key)
            self.cache[key] = value
            self.hits += 1
            return value

    def put(self, key: str, value: Any):
        """设置缓存值"""
        with self.lock:
            if key in self.cache:
                # 更新现有值
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # 移除最久未使用的项
                oldest_key = next(iter(self.cache))
                self._remove(oldest_key)

            self.cache[key] = value
            if self.ttl is not None:
                self.timestamps[key] = time.time()

    def _remove(self, key: str):
        """移除缓存项"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)

    def remove(self, key: str) -> bool:
        """手动移除缓存项"""
        with self.lock:
            if key in self.cache:
                self._remove(key)
                return True
            return False

    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.hits = 0
            self.misses = 0

    def size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.cache)

    def hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': self.hit_rate(),
                'ttl': self.ttl
            }


class FileCache:
    """文件缓存实现"""

    def __init__(self, cache_dir: str = "cache", max_size_mb: int = 100):
        """
        初始化文件缓存

        Args:
            cache_dir: 缓存目录
            max_size_mb: 最大缓存大小(MB)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.lock = threading.Lock()

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用MD5哈希避免文件名过长或包含特殊字符
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"

    def _get_meta_path(self, key: str) -> Path:
        """获取元数据文件路径"""
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.meta"

    def get(self, key: str, ttl: Optional[float] = None) -> Optional[Any]:
        """获取缓存值"""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)

        if not cache_path.exists() or not meta_path.exists():
            return None

        try:
            # 检查TTL
            if ttl is not None:
                meta_stat = meta_path.stat()
                if time.time() - meta_stat.st_mtime > ttl:
                    self.remove(key)
                    return None

            # 读取缓存数据
            with open(cache_path, 'rb') as f:
                return pickle.load(f)

        except Exception as e:
            logger.warning(f"读取文件缓存失败: {e}")
            self.remove(key)
            return None

    def put(self, key: str, value: Any):
        """设置缓存值"""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)

        try:
            with self.lock:
                # 检查缓存大小
                self._cleanup_if_needed()

                # 写入缓存数据
                with open(cache_path, 'wb') as f:
                    pickle.dump(value, f)

                # 写入元数据
                with open(meta_path, 'w') as f:
                    f.write(f"key: {key}\n")
                    f.write(f"timestamp: {time.time()}\n")

        except Exception as e:
            logger.error(f"写入文件缓存失败: {e}")

    def remove(self, key: str) -> bool:
        """移除缓存项"""
        cache_path = self._get_cache_path(key)
        meta_path = self._get_meta_path(key)

        removed = False
        for path in [cache_path, meta_path]:
            if path.exists():
                try:
                    path.unlink()
                    removed = True
                except Exception as e:
                    logger.warning(f"删除缓存文件失败: {e}")

        return removed

    def clear(self):
        """清空缓存"""
        try:
            for file_path in self.cache_dir.glob("*.cache"):
                file_path.unlink()
            for file_path in self.cache_dir.glob("*.meta"):
                file_path.unlink()
        except Exception as e:
            logger.error(f"清空文件缓存失败: {e}")

    def _cleanup_if_needed(self):
        """如果需要则清理缓存"""
        total_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.cache")
            if f.is_file()
        )

        if total_size > self.max_size_bytes:
            # 按修改时间排序，删除最旧的文件
            cache_files = list(self.cache_dir.glob("*.cache"))
            cache_files.sort(key=lambda x: x.stat().st_mtime)

            for cache_file in cache_files:
                if total_size <= self.max_size_bytes * 0.8:  # 清理到80%
                    break

                try:
                    file_size = cache_file.stat().st_size
                    cache_file.unlink()

                    # 删除对应的元数据文件
                    meta_file = cache_file.with_suffix('.meta')
                    if meta_file.exists():
                        meta_file.unlink()

                    total_size -= file_size

                except Exception as e:
                    logger.warning(f"清理缓存文件失败: {e}")

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())

        return {
            'file_count': len(cache_files),
            'total_size_mb': total_size / 1024 / 1024,
            'max_size_mb': self.max_size_bytes / 1024 / 1024,
            'cache_dir': str(self.cache_dir)
        }


class MultiLevelCache:
    """多级缓存系统"""

    def __init__(self,
                 l1_size: int = 1000,
                 l1_ttl: Optional[float] = 300,  # 5分钟
                 l2_size_mb: int = 100,
                 l2_ttl: Optional[float] = 3600):  # 1小时
        """
        初始化多级缓存

        Args:
            l1_size: L1缓存大小（内存）
            l1_ttl: L1缓存TTL
            l2_size_mb: L2缓存大小（文件）
            l2_ttl: L2缓存TTL
        """
        self.l1_cache = LRUCache(max_size=l1_size, ttl=l1_ttl)
        self.l2_cache = FileCache(max_size_mb=l2_size_mb)
        self.l2_ttl = l2_ttl

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        # 先查L1缓存
        value = self.l1_cache.get(key)
        if value is not None:
            return value

        # 再查L2缓存
        value = self.l2_cache.get(key, self.l2_ttl)
        if value is not None:
            # 提升到L1缓存
            self.l1_cache.put(key, value)
            return value

        return None

    def put(self, key: str, value: Any):
        """设置缓存值"""
        # 同时写入L1和L2缓存
        self.l1_cache.put(key, value)
        self.l2_cache.put(key, value)

    def remove(self, key: str) -> bool:
        """移除缓存项"""
        l1_removed = self.l1_cache.remove(key)
        l2_removed = self.l2_cache.remove(key)
        return l1_removed or l2_removed

    def clear(self):
        """清空所有缓存"""
        self.l1_cache.clear()
        self.l2_cache.clear()

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'l1_cache': self.l1_cache.stats(),
            'l2_cache': self.l2_cache.stats()
        }


# 全局缓存实例
default_cache = MultiLevelCache()


def cache_result(ttl: Optional[float] = None,
                 cache_instance: Optional[MultiLevelCache] = None,
                 key_func: Optional[Callable] = None):
    """
    缓存函数结果的装饰器

    Args:
        ttl: 缓存生存时间
        cache_instance: 缓存实例
        key_func: 自定义键生成函数
    """
    def decorator(func: Callable) -> Callable:
        cache = cache_instance or default_cache

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                try:
                    # 尝试生成哈希键
                    args_str = str(args)
                    kwargs_str = str(sorted(kwargs.items()))
                    cache_key = f"{func.__module__}.{func.__name__}:{hash((args_str, kwargs_str))}"
                except (TypeError, ValueError):
                    # 如果无法哈希，使用字符串表示
                    cache_key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"

            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.put(cache_key, result)

            return result

        # 添加缓存管理方法
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_stats = lambda: cache.stats()

        return wrapper

    return decorator


def memoize(func: Callable) -> Callable:
    """简单的记忆化装饰器"""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    wrapper.cache_clear = lambda: cache.clear()
    wrapper.cache_info = lambda: {'size': len(cache)}

    return wrapper


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.caches: Dict[str, Union[LRUCache,
                                     FileCache, MultiLevelCache]] = {}

    def create_cache(self, name: str, cache_type: str = 'lru', **kwargs) -> Union[LRUCache, FileCache, MultiLevelCache]:
        """创建缓存实例"""
        if cache_type == 'lru':
            cache = LRUCache(**kwargs)
        elif cache_type == 'file':
            cache = FileCache(**kwargs)
        elif cache_type == 'multi':
            cache = MultiLevelCache(**kwargs)
        else:
            raise ValueError(f"不支持的缓存类型: {cache_type}")

        self.caches[name] = cache
        return cache

    def get_cache(self, name: str) -> Optional[Union[LRUCache, FileCache, MultiLevelCache]]:
        """获取缓存实例"""
        return self.caches.get(name)

    def clear_all(self):
        """清空所有缓存"""
        for cache in self.caches.values():
            cache.clear()

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有缓存的统计信息"""
        return {name: cache.stats() for name, cache in self.caches.items()}

    def print_stats(self):
        """打印缓存统计信息"""
        print("📦 缓存系统统计")
        print("=" * 50)

        for name, cache in self.caches.items():
            print(f"\n🗂️ 缓存: {name}")
            stats = cache.stats()

            if isinstance(cache, LRUCache):
                print(f"  类型: 内存LRU缓存")
                print(f"  大小: {stats['size']}/{stats['max_size']}")
                print(f"  命中率: {stats['hit_rate']:.2%}")
                print(f"  命中次数: {stats['hits']}")
                print(f"  未命中次数: {stats['misses']}")

            elif isinstance(cache, FileCache):
                print(f"  类型: 文件缓存")
                print(f"  文件数: {stats['file_count']}")
                print(
                    f"  大小: {stats['total_size_mb']:.1f}/{stats['max_size_mb']:.1f}MB")
                print(f"  目录: {stats['cache_dir']}")

            elif isinstance(cache, MultiLevelCache):
                print(f"  类型: 多级缓存")
                l1_stats = stats['l1_cache']
                l2_stats = stats['l2_cache']
                print(
                    f"  L1缓存: {l1_stats['size']}/{l1_stats['max_size']} (命中率: {l1_stats['hit_rate']:.2%})")
                print(
                    f"  L2缓存: {l2_stats['file_count']}个文件, {l2_stats['total_size_mb']:.1f}MB")


# 全局缓存管理器
cache_manager = CacheManager()

# 创建默认缓存实例
cache_manager.create_cache('default', 'multi')
cache_manager.create_cache('stock_data', 'multi', l1_size=500, l2_size_mb=50)
cache_manager.create_cache('strategy_results', 'lru',
                           max_size=100, ttl=1800)  # 30分钟
