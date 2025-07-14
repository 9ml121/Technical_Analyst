"""
并发处理工具

提供线程池、进程池和异步处理功能
"""

import asyncio
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Callable, Any, Optional, Dict, Union, Iterable
import time
import logging
from functools import wraps, partial
from dataclasses import dataclass
import queue

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    result: Any
    success: bool
    error: Optional[Exception] = None
    execution_time: float = 0.0

class ThreadSafeCounter:
    """线程安全计数器"""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1) -> int:
        """增加计数"""
        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """减少计数"""
        with self._lock:
            self._value -= amount
            return self._value
    
    @property
    def value(self) -> int:
        """获取当前值"""
        with self._lock:
            return self._value
    
    def reset(self, value: int = 0):
        """重置计数"""
        with self._lock:
            self._value = value

class TaskQueue:
    """任务队列"""
    
    def __init__(self, max_size: int = 0):
        """
        初始化任务队列
        
        Args:
            max_size: 队列最大大小，0表示无限制
        """
        self.queue = queue.Queue(maxsize=max_size)
        self.completed_tasks = []
        self.failed_tasks = []
        self._lock = threading.Lock()
    
    def put_task(self, task_id: str, func: Callable, *args, **kwargs):
        """添加任务"""
        task = {
            'id': task_id,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'created_time': time.time()
        }
        self.queue.put(task)
    
    def get_task(self, timeout: Optional[float] = None):
        """获取任务"""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def task_done(self):
        """标记任务完成"""
        self.queue.task_done()
    
    def add_result(self, result: TaskResult):
        """添加任务结果"""
        with self._lock:
            if result.success:
                self.completed_tasks.append(result)
            else:
                self.failed_tasks.append(result)
    
    def get_results(self) -> Dict[str, List[TaskResult]]:
        """获取所有结果"""
        with self._lock:
            return {
                'completed': self.completed_tasks.copy(),
                'failed': self.failed_tasks.copy()
            }
    
    def clear_results(self):
        """清空结果"""
        with self._lock:
            self.completed_tasks.clear()
            self.failed_tasks.clear()
    
    @property
    def size(self) -> int:
        """队列大小"""
        return self.queue.qsize()
    
    @property
    def empty(self) -> bool:
        """队列是否为空"""
        return self.queue.empty()

def parallel_map(func: Callable, iterable: Iterable, max_workers: Optional[int] = None,
                use_processes: bool = False, timeout: Optional[float] = None) -> List[Any]:
    """
    并行映射函数
    
    Args:
        func: 要执行的函数
        iterable: 可迭代对象
        max_workers: 最大工作线程/进程数
        use_processes: 是否使用进程池
        timeout: 超时时间
    
    Returns:
        结果列表
    """
    if max_workers is None:
        max_workers = min(32, (mp.cpu_count() or 1) + 4)
    
    executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    
    try:
        with executor_class(max_workers=max_workers) as executor:
            if timeout:
                futures = [executor.submit(func, item) for item in iterable]
                results = []
                
                for future in as_completed(futures, timeout=timeout):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        logger.error(f"任务执行失败: {e}")
                        results.append(None)
                
                return results
            else:
                return list(executor.map(func, iterable))
                
    except Exception as e:
        logger.error(f"并行执行失败: {e}")
        # 回退到串行执行
        return [func(item) for item in iterable]

def parallel_process(func: Callable, items: List[Any], max_workers: Optional[int] = None,
                    use_processes: bool = False, return_exceptions: bool = False) -> List[TaskResult]:
    """
    并行处理任务列表
    
    Args:
        func: 处理函数
        items: 要处理的项目列表
        max_workers: 最大工作线程/进程数
        use_processes: 是否使用进程池
        return_exceptions: 是否返回异常信息
    
    Returns:
        任务结果列表
    """
    if not items:
        return []
    
    if max_workers is None:
        max_workers = min(32, (mp.cpu_count() or 1) + 4)
    
    executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    results = []
    
    try:
        with executor_class(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_item = {
                executor.submit(func, item): (i, item) 
                for i, item in enumerate(items)
            }
            
            # 收集结果
            for future in as_completed(future_to_item):
                task_id, item = future_to_item[future]
                start_time = time.time()
                
                try:
                    result = future.result()
                    execution_time = time.time() - start_time
                    
                    task_result = TaskResult(
                        task_id=str(task_id),
                        result=result,
                        success=True,
                        execution_time=execution_time
                    )
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    
                    task_result = TaskResult(
                        task_id=str(task_id),
                        result=None,
                        success=False,
                        error=e,
                        execution_time=execution_time
                    )
                    
                    if not return_exceptions:
                        logger.error(f"任务 {task_id} 执行失败: {e}")
                
                results.append(task_result)
        
        # 按原始顺序排序
        results.sort(key=lambda x: int(x.task_id))
        return results
        
    except Exception as e:
        logger.error(f"并行处理失败: {e}")
        return []

class WorkerPool:
    """工作线程池"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 100):
        """
        初始化工作线程池
        
        Args:
            max_workers: 最大工作线程数
            queue_size: 任务队列大小
        """
        self.max_workers = max_workers
        self.task_queue = TaskQueue(queue_size)
        self.workers = []
        self.running = False
        self.completed_counter = ThreadSafeCounter()
        self.failed_counter = ThreadSafeCounter()
    
    def start(self):
        """启动工作线程池"""
        if self.running:
            return
        
        self.running = True
        
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"Worker-{i}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"工作线程池已启动，{self.max_workers}个工作线程")
    
    def stop(self, timeout: float = 5.0):
        """停止工作线程池"""
        if not self.running:
            return
        
        self.running = False
        
        # 等待所有任务完成
        self.task_queue.queue.join()
        
        # 等待工作线程结束
        for worker in self.workers:
            worker.join(timeout=timeout)
        
        logger.info("工作线程池已停止")
    
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs):
        """提交任务"""
        if not self.running:
            raise RuntimeError("工作线程池未启动")
        
        self.task_queue.put_task(task_id, func, *args, **kwargs)
    
    def _worker_loop(self):
        """工作线程循环"""
        while self.running:
            task = self.task_queue.get_task(timeout=1.0)
            
            if task is None:
                continue
            
            start_time = time.time()
            
            try:
                result = task['func'](*task['args'], **task['kwargs'])
                execution_time = time.time() - start_time
                
                task_result = TaskResult(
                    task_id=task['id'],
                    result=result,
                    success=True,
                    execution_time=execution_time
                )
                
                self.completed_counter.increment()
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                task_result = TaskResult(
                    task_id=task['id'],
                    result=None,
                    success=False,
                    error=e,
                    execution_time=execution_time
                )
                
                self.failed_counter.increment()
                logger.error(f"任务 {task['id']} 执行失败: {e}")
            
            self.task_queue.add_result(task_result)
            self.task_queue.task_done()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'max_workers': self.max_workers,
            'running': self.running,
            'queue_size': self.task_queue.size,
            'completed_tasks': self.completed_counter.value,
            'failed_tasks': self.failed_counter.value,
            'total_tasks': self.completed_counter.value + self.failed_counter.value
        }

def async_timeout(timeout: float):
    """异步超时装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                logger.warning(f"函数 {func.__name__} 执行超时 ({timeout}s)")
                raise
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """失败重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"函数 {func.__name__} 第{attempt + 1}次尝试失败: {e}, "
                            f"{current_delay}秒后重试"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"函数 {func.__name__} 重试{max_retries}次后仍然失败")
            
            raise last_exception
        return wrapper
    return decorator

def rate_limit(calls_per_second: float):
    """速率限制装饰器"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    lock = threading.Lock()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                elapsed = time.time() - last_called[0]
                left_to_wait = min_interval - elapsed
                
                if left_to_wait > 0:
                    time.sleep(left_to_wait)
                
                last_called[0] = time.time()
                return func(*args, **kwargs)
        return wrapper
    return decorator

# 便捷函数
def run_in_thread(func: Callable, *args, **kwargs) -> threading.Thread:
    """在新线程中运行函数"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread

def run_in_process(func: Callable, *args, **kwargs) -> mp.Process:
    """在新进程中运行函数"""
    process = mp.Process(target=func, args=args, kwargs=kwargs, daemon=True)
    process.start()
    return process

async def run_in_executor(func: Callable, *args, executor=None, **kwargs) -> Any:
    """在执行器中运行同步函数"""
    loop = asyncio.get_event_loop()
    if kwargs:
        func = partial(func, **kwargs)
    return await loop.run_in_executor(executor, func, *args)

# 全局工作线程池实例
default_worker_pool = WorkerPool(max_workers=4)

def start_default_worker_pool():
    """启动默认工作线程池"""
    default_worker_pool.start()

def stop_default_worker_pool():
    """停止默认工作线程池"""
    default_worker_pool.stop()

def submit_to_default_pool(task_id: str, func: Callable, *args, **kwargs):
    """提交任务到默认工作线程池"""
    default_worker_pool.submit_task(task_id, func, *args, **kwargs)
