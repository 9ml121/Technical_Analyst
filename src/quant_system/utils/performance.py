"""
性能分析和优化工具

提供性能监控、分析和优化功能
"""

import time
import psutil
import threading
import functools
import cProfile
import pstats
import io
from typing import Dict, List, Any, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    function_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    call_count: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'function_name': self.function_name,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'call_count': self.call_count,
            'timestamp': self.timestamp.isoformat()
        }

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.function_stats: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._monitoring = False
        self._monitor_thread = None
    
    def start_monitoring(self, interval: float = 1.0):
        """开始性能监控"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_system,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("性能监控已启动")
    
    def stop_monitoring(self):
        """停止性能监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("性能监控已停止")
    
    def _monitor_system(self, interval: float):
        """系统监控循环"""
        while self._monitoring:
            try:
                # 获取系统指标
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                # 记录系统指标
                with self._lock:
                    metric = PerformanceMetrics(
                        function_name="system",
                        execution_time=0.0,
                        memory_usage=memory_info.percent,
                        cpu_usage=cpu_percent,
                        call_count=0,
                        timestamp=datetime.now()
                    )
                    self.metrics.append(metric)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"系统监控出错: {e}")
                time.sleep(interval)
    
    def record_function_performance(self, func_name: str, execution_time: float, 
                                  memory_usage: float = 0.0, cpu_usage: float = 0.0):
        """记录函数性能"""
        with self._lock:
            # 更新函数统计
            if func_name not in self.function_stats:
                self.function_stats[func_name] = {
                    'total_time': 0.0,
                    'call_count': 0,
                    'avg_time': 0.0,
                    'min_time': float('inf'),
                    'max_time': 0.0
                }
            
            stats = self.function_stats[func_name]
            stats['total_time'] += execution_time
            stats['call_count'] += 1
            stats['avg_time'] = stats['total_time'] / stats['call_count']
            stats['min_time'] = min(stats['min_time'], execution_time)
            stats['max_time'] = max(stats['max_time'], execution_time)
            
            # 记录性能指标
            metric = PerformanceMetrics(
                function_name=func_name,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                call_count=stats['call_count'],
                timestamp=datetime.now()
            )
            self.metrics.append(metric)
    
    def get_function_stats(self, func_name: Optional[str] = None) -> Dict[str, Any]:
        """获取函数统计信息"""
        with self._lock:
            if func_name:
                return self.function_stats.get(func_name, {})
            return self.function_stats.copy()
    
    def get_recent_metrics(self, minutes: int = 5) -> List[PerformanceMetrics]:
        """获取最近的性能指标"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self._lock:
            return [m for m in self.metrics if m.timestamp >= cutoff_time]
    
    def get_top_functions(self, limit: int = 10, sort_by: str = 'total_time') -> List[Dict[str, Any]]:
        """获取性能最差的函数"""
        with self._lock:
            sorted_functions = sorted(
                self.function_stats.items(),
                key=lambda x: x[1].get(sort_by, 0),
                reverse=True
            )
            
            return [
                {'name': name, **stats}
                for name, stats in sorted_functions[:limit]
            ]
    
    def clear_metrics(self):
        """清空性能指标"""
        with self._lock:
            self.metrics.clear()
            self.function_stats.clear()
        logger.info("性能指标已清空")

# 全局性能监控器实例
performance_monitor = PerformanceMonitor()

def performance_timer(func: Callable) -> Callable:
    """性能计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            execution_time = end_time - start_time
            memory_usage = end_memory - start_memory
            
            # 记录性能数据
            performance_monitor.record_function_performance(
                func.__name__,
                execution_time,
                memory_usage
            )
            
            # 如果执行时间过长，记录警告
            if execution_time > 1.0:
                logger.warning(f"函数 {func.__name__} 执行时间过长: {execution_time:.2f}s")
    
    return wrapper

@contextmanager
def performance_context(name: str):
    """性能监控上下文管理器"""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss / 1024 / 1024
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        performance_monitor.record_function_performance(
            name,
            execution_time,
            memory_usage
        )

class ProfilerManager:
    """性能分析器管理器"""
    
    def __init__(self):
        self.profiler = None
        self.profiling = False
    
    def start_profiling(self):
        """开始性能分析"""
        if self.profiling:
            return
        
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.profiling = True
        logger.info("性能分析已启动")
    
    def stop_profiling(self) -> str:
        """停止性能分析并返回报告"""
        if not self.profiling or not self.profiler:
            return "性能分析未启动"
        
        self.profiler.disable()
        self.profiling = False
        
        # 生成报告
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(20)  # 显示前20个函数
        
        logger.info("性能分析已停止")
        return s.getvalue()
    
    @contextmanager
    def profile_context(self):
        """性能分析上下文管理器"""
        self.start_profiling()
        try:
            yield
        finally:
            report = self.stop_profiling()
            print("性能分析报告:")
            print(report)

class MemoryProfiler:
    """内存分析器"""
    
    def __init__(self):
        self.snapshots = []
    
    def take_snapshot(self, name: str = ""):
        """获取内存快照"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        snapshot = {
            'name': name,
            'timestamp': datetime.now(),
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available / 1024 / 1024  # MB
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def get_memory_usage(self) -> Dict[str, float]:
        """获取当前内存使用情况"""
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        
        return {
            'process_rss_mb': memory_info.rss / 1024 / 1024,
            'process_vms_mb': memory_info.vms / 1024 / 1024,
            'process_percent': process.memory_percent(),
            'system_total_mb': system_memory.total / 1024 / 1024,
            'system_available_mb': system_memory.available / 1024 / 1024,
            'system_used_percent': system_memory.percent
        }
    
    def analyze_memory_growth(self) -> Dict[str, Any]:
        """分析内存增长趋势"""
        if len(self.snapshots) < 2:
            return {'error': '需要至少2个快照来分析趋势'}
        
        first = self.snapshots[0]
        last = self.snapshots[-1]
        
        time_diff = (last['timestamp'] - first['timestamp']).total_seconds()
        rss_growth = last['rss'] - first['rss']
        
        return {
            'time_span_seconds': time_diff,
            'rss_growth_mb': rss_growth,
            'growth_rate_mb_per_second': rss_growth / time_diff if time_diff > 0 else 0,
            'snapshots_count': len(self.snapshots),
            'first_snapshot': first,
            'last_snapshot': last
        }
    
    def clear_snapshots(self):
        """清空内存快照"""
        self.snapshots.clear()

def memory_usage_decorator(func: Callable) -> Callable:
    """内存使用监控装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = MemoryProfiler()
        
        # 执行前快照
        profiler.take_snapshot(f"{func.__name__}_before")
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # 执行后快照
            profiler.take_snapshot(f"{func.__name__}_after")
            
            # 分析内存使用
            analysis = profiler.analyze_memory_growth()
            if analysis.get('rss_growth_mb', 0) > 10:  # 超过10MB增长
                logger.warning(
                    f"函数 {func.__name__} 内存使用增长: "
                    f"{analysis['rss_growth_mb']:.2f}MB"
                )
    
    return wrapper

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.optimization_suggestions = []
    
    def analyze_performance(self, metrics: List[PerformanceMetrics]) -> List[str]:
        """分析性能并提供优化建议"""
        suggestions = []
        
        # 分析执行时间
        slow_functions = [m for m in metrics if m.execution_time > 1.0]
        if slow_functions:
            suggestions.append(
                f"发现 {len(slow_functions)} 个慢函数，建议优化算法或使用缓存"
            )
        
        # 分析内存使用
        high_memory_functions = [m for m in metrics if m.memory_usage > 100]  # 100MB
        if high_memory_functions:
            suggestions.append(
                f"发现 {len(high_memory_functions)} 个高内存使用函数，建议优化数据结构"
            )
        
        # 分析调用频率
        function_calls = {}
        for metric in metrics:
            function_calls[metric.function_name] = function_calls.get(metric.function_name, 0) + 1
        
        frequent_functions = [name for name, count in function_calls.items() if count > 100]
        if frequent_functions:
            suggestions.append(
                f"发现 {len(frequent_functions)} 个高频调用函数，建议使用缓存或优化算法"
            )
        
        self.optimization_suggestions.extend(suggestions)
        return suggestions
    
    def suggest_optimizations(self, function_stats: Dict[str, Dict[str, Any]]) -> List[str]:
        """基于函数统计提供优化建议"""
        suggestions = []
        
        for func_name, stats in function_stats.items():
            avg_time = stats.get('avg_time', 0)
            call_count = stats.get('call_count', 0)
            total_time = stats.get('total_time', 0)
            
            # 平均执行时间过长
            if avg_time > 0.5:
                suggestions.append(
                    f"函数 {func_name} 平均执行时间过长 ({avg_time:.2f}s)，建议优化算法"
                )
            
            # 总执行时间占比过高
            if total_time > 10.0:
                suggestions.append(
                    f"函数 {func_name} 总执行时间过长 ({total_time:.2f}s)，建议重点优化"
                )
            
            # 调用次数过多
            if call_count > 1000:
                suggestions.append(
                    f"函数 {func_name} 调用次数过多 ({call_count}次)，建议使用缓存"
                )
        
        return suggestions

# 全局实例
profiler_manager = ProfilerManager()
memory_profiler = MemoryProfiler()
performance_optimizer = PerformanceOptimizer()

# 便捷函数
def start_performance_monitoring(interval: float = 1.0):
    """启动性能监控"""
    performance_monitor.start_monitoring(interval)

def stop_performance_monitoring():
    """停止性能监控"""
    performance_monitor.stop_monitoring()

def get_performance_report() -> Dict[str, Any]:
    """获取性能报告"""
    recent_metrics = performance_monitor.get_recent_metrics(5)
    function_stats = performance_monitor.get_function_stats()
    top_functions = performance_monitor.get_top_functions()
    memory_usage = memory_profiler.get_memory_usage()
    
    # 生成优化建议
    suggestions = performance_optimizer.analyze_performance(recent_metrics)
    function_suggestions = performance_optimizer.suggest_optimizations(function_stats)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'recent_metrics_count': len(recent_metrics),
        'function_stats': function_stats,
        'top_functions': top_functions,
        'memory_usage': memory_usage,
        'optimization_suggestions': suggestions + function_suggestions,
        'system_info': {
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / 1024 / 1024 / 1024
        }
    }

def print_performance_report():
    """打印性能报告"""
    report = get_performance_report()
    
    print("🚀 性能分析报告")
    print("=" * 50)
    
    print(f"\n📊 系统信息:")
    print(f"  CPU核心数: {report['system_info']['cpu_count']}")
    print(f"  总内存: {report['system_info']['memory_total_gb']:.1f}GB")
    
    print(f"\n💾 内存使用:")
    memory = report['memory_usage']
    print(f"  进程内存: {memory['process_rss_mb']:.1f}MB ({memory['process_percent']:.1f}%)")
    print(f"  系统内存: {memory['system_used_percent']:.1f}% 已使用")
    print(f"  可用内存: {memory['system_available_mb']:.1f}MB")
    
    print(f"\n⏱️ 性能最差的函数:")
    for i, func in enumerate(report['top_functions'][:5], 1):
        print(f"  {i}. {func['name']}: {func['total_time']:.2f}s "
              f"(调用{func['call_count']}次, 平均{func['avg_time']:.3f}s)")
    
    print(f"\n💡 优化建议:")
    for i, suggestion in enumerate(report['optimization_suggestions'][:5], 1):
        print(f"  {i}. {suggestion}")
    
    if not report['optimization_suggestions']:
        print("  ✅ 暂无优化建议，性能表现良好")
