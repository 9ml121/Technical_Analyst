# 工具模块 API 文档

## 🛠️ 模块概述

工具模块提供系统运行所需的各种辅助功能，包括日志管理、性能监控、缓存系统、并发处理等。

## 🏗️ 模块架构

```
quant_system/utils/
├── logger.py              # 日志系统
├── performance.py         # 性能监控
├── cache.py              # 缓存系统
├── concurrent.py         # 并发处理
├── helpers.py            # 辅助函数
├── validators.py         # 数据验证
└── exceptions.py         # 异常定义
```

## 📝 日志系统 (Logger)

### 类定义

```python
class QuantLogger:
    """量化系统日志器"""
    
    def __init__(self, name: str, level: str = "INFO"):
        """初始化日志器"""
        
    def setup_file_handler(self, log_file: str, max_size: str = "10MB", backup_count: int = 5):
        """设置文件处理器"""
        
    def setup_console_handler(self, level: str = "INFO"):
        """设置控制台处理器"""
```

### 使用方法

```python
from quant_system.utils.logger import get_logger

# 获取日志器
logger = get_logger(__name__)

# 基本日志记录
logger.info("系统启动")
logger.warning("数据质量警告")
logger.error("处理失败", exc_info=True)

# 结构化日志
logger.info("交易执行", extra={
    'stock_code': '000001',
    'action': 'BUY',
    'price': 12.50,
    'quantity': 1000
})
```

### 日志配置

```python
def configure_logging(config: Dict[str, Any]):
    """配置日志系统"""
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/system.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'formatter': 'detailed'
            }
        },
        'loggers': {
            'quant_system': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
```

## 📊 性能监控 (Performance)

### 性能监控器

```python
class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        """初始化监控器"""
        
    def start_monitoring(self, interval: int = 60):
        """开始监控"""
        
    def stop_monitoring(self):
        """停止监控"""
        
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录指标"""
```

### 性能装饰器

```python
def performance_monitor(func_name: str = None):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            
            try:
                result = func(*args, **kwargs)
                success = True
            except Exception as e:
                success = False
                raise
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                
                metrics = {
                    'function': func_name or func.__name__,
                    'execution_time': end_time - start_time,
                    'memory_delta': end_memory - start_memory,
                    'success': success,
                    'timestamp': datetime.now()
                }
                
                monitor.record_metric('function_performance', metrics)
            
            return result
        return wrapper
    return decorator
```

### 使用示例

```python
from quant_system.utils.performance import performance_monitor, PerformanceMonitor

# 使用装饰器监控函数性能
@performance_monitor("数据处理")
def process_stock_data(data):
    # 数据处理逻辑
    return processed_data

# 手动监控
monitor = PerformanceMonitor()
monitor.start_monitoring()

# 执行业务逻辑
result = process_stock_data(raw_data)

# 获取性能指标
metrics = monitor.get_metrics()
print(f"CPU使用率: {metrics['cpu_percent']:.1f}%")
print(f"内存使用: {metrics['memory_mb']:.1f}MB")
```

## 💾 缓存系统 (Cache)

### 多级缓存

```python
class MultiLevelCache:
    """多级缓存系统"""
    
    def __init__(self, l1_size: int = 1000, l2_path: str = "cache"):
        """初始化多级缓存"""
        
    def get(self, key: str) -> Any:
        """获取缓存值"""
        
    def set(self, key: str, value: Any, ttl: int = 3600):
        """设置缓存值"""
        
    def delete(self, key: str):
        """删除缓存"""
        
    def clear(self):
        """清空缓存"""
```

### 缓存装饰器

```python
def cache_result(ttl: int = 3600, key_func: Callable = None):
    """缓存结果装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

### 使用示例

```python
from quant_system.utils.cache import cache_result, MultiLevelCache

# 初始化缓存
cache = MultiLevelCache(l1_size=1000, l2_path="cache")

# 使用缓存装饰器
@cache_result(ttl=3600)
def get_stock_data(stock_code: str, date: str):
    # 耗时的数据获取操作
    return fetch_data_from_api(stock_code, date)

# 手动缓存操作
cache.set("market_status", "open", ttl=1800)
status = cache.get("market_status")
```

## ⚡ 并发处理 (Concurrent)

### 并发处理器

```python
class ConcurrentProcessor:
    """并发处理器"""
    
    def __init__(self, max_workers: int = None):
        """初始化处理器"""
        
    def process_parallel(self, func: Callable, items: List[Any], 
                        chunk_size: int = None) -> List[Any]:
        """并行处理"""
        
    def process_concurrent(self, func: Callable, items: List[Any]) -> List[Any]:
        """并发处理"""
        
    def adaptive_process(self, func: Callable, items: List[Any]) -> List[Any]:
        """自适应处理"""
```

### 并发工具函数

```python
def parallel_process(func: Callable, items: List[Any], 
                    max_workers: int = 4, chunk_size: int = None) -> List[Any]:
    """并行处理函数"""
    
    if len(items) < 100:  # 小数据量使用串行
        return [func(item) for item in items]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        if chunk_size:
            # 分块处理
            chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
            futures = [executor.submit(lambda chunk: [func(item) for item in chunk], chunk) 
                      for chunk in chunks]
            results = []
            for future in as_completed(futures):
                results.extend(future.result())
            return results
        else:
            # 直接并行
            futures = [executor.submit(func, item) for item in items]
            return [future.result() for future in as_completed(futures)]
```

### 使用示例

```python
from quant_system.utils.concurrent import parallel_process, ConcurrentProcessor

# 并行处理股票数据
def process_single_stock(stock_code):
    return get_stock_analysis(stock_code)

stock_codes = ['000001', '000002', '600000', '600036']
results = parallel_process(process_single_stock, stock_codes, max_workers=4)

# 使用并发处理器
processor = ConcurrentProcessor(max_workers=8)
analysis_results = processor.adaptive_process(analyze_stock, stock_data_list)
```

## 🔧 辅助函数 (Helpers)

### 数学计算

```python
def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    """安全除法"""
    try:
        return a / b if b != 0 else default
    except (TypeError, ValueError):
        return default

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """计算百分比变化"""
    if old_value == 0:
        return 0.0
    return (new_value - old_value) / old_value

def round_to_tick(price: float, tick_size: float = 0.01) -> float:
    """价格取整到最小变动单位"""
    return round(price / tick_size) * tick_size
```

### 日期时间工具

```python
def get_trading_dates(start_date: date, end_date: date) -> List[date]:
    """获取交易日期列表"""
    
def is_trading_day(check_date: date) -> bool:
    """判断是否为交易日"""
    
def get_next_trading_day(current_date: date) -> date:
    """获取下一个交易日"""
    
def get_previous_trading_day(current_date: date) -> date:
    """获取上一个交易日"""
```

### 格式化工具

```python
def format_currency(amount: float, currency: str = "¥") -> str:
    """格式化货币"""
    if amount >= 100000000:  # 亿
        return f"{currency}{amount/100000000:.2f}亿"
    elif amount >= 10000:    # 万
        return f"{currency}{amount/10000:.2f}万"
    else:
        return f"{currency}{amount:.2f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """格式化百分比"""
    return f"{value * 100:.{decimal_places}f}%"

def format_number(value: float, decimal_places: int = 2) -> str:
    """格式化数字"""
    return f"{value:,.{decimal_places}f}"
```

## ✅ 数据验证 (Validators)

### 股票代码验证

```python
class StockCodeValidator:
    """股票代码验证器"""
    
    @staticmethod
    def is_valid_a_share(code: str) -> bool:
        """验证A股代码"""
        return bool(re.match(r'^[0-9]{6}$', code))
    
    @staticmethod
    def is_valid_hk_share(code: str) -> bool:
        """验证港股代码"""
        return bool(re.match(r'^[0-9]{5}$', code))
    
    @staticmethod
    def normalize_code(code: str, market: str = "A") -> str:
        """标准化股票代码"""
        code = code.strip().upper()
        if market == "A":
            return code.zfill(6)
        elif market == "HK":
            return code.zfill(5)
        return code
```

### 数据验证函数

```python
def validate_stock_data(data: Dict[str, Any]) -> List[str]:
    """验证股票数据"""
    errors = []
    
    # 必需字段检查
    required_fields = ['code', 'name', 'price', 'volume']
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")
    
    # 价格验证
    if 'price' in data:
        price = data['price']
        if not isinstance(price, (int, float)) or price <= 0:
            errors.append("价格必须是正数")
    
    # 成交量验证
    if 'volume' in data:
        volume = data['volume']
        if not isinstance(volume, int) or volume < 0:
            errors.append("成交量必须是非负整数")
    
    return errors

def validate_date_range(start_date: date, end_date: date) -> bool:
    """验证日期范围"""
    return start_date <= end_date

def validate_config_value(value: Any, value_type: type, 
                         min_value: Any = None, max_value: Any = None) -> bool:
    """验证配置值"""
    if not isinstance(value, value_type):
        return False
    
    if min_value is not None and value < min_value:
        return False
    
    if max_value is not None and value > max_value:
        return False
    
    return True
```

## 🚨 异常定义 (Exceptions)

### 自定义异常类

```python
class QuantSystemError(Exception):
    """量化系统基础异常"""
    pass

class DataSourceError(QuantSystemError):
    """数据源错误"""
    pass

class StrategyError(QuantSystemError):
    """策略执行错误"""
    pass

class BacktestError(QuantSystemError):
    """回测执行错误"""
    pass

class ConfigError(QuantSystemError):
    """配置错误"""
    pass

class ValidationError(QuantSystemError):
    """数据验证错误"""
    pass

class NetworkError(QuantSystemError):
    """网络连接错误"""
    pass

class CacheError(QuantSystemError):
    """缓存操作错误"""
    pass
```

### 异常处理工具

```python
def handle_exception(func: Callable):
    """异常处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行失败: {e}", exc_info=True)
            raise
    return wrapper

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, 
                      exceptions: Tuple = (Exception,)):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"第{attempt + 1}次尝试失败: {e}, {delay}秒后重试")
                    time.sleep(delay)
        return wrapper
    return decorator
```

## 🔧 系统工具

### 目录管理

```python
def ensure_dir(path: Union[str, Path]) -> Path:
    """确保目录存在"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def clean_old_files(directory: Path, days: int = 7, pattern: str = "*"):
    """清理旧文件"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_time < cutoff_date:
                file_path.unlink()
```

### 配置工具

```python
def load_yaml_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml_file(data: Dict[str, Any], file_path: Union[str, Path]):
    """保存YAML文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
```

## 🔗 相关文档

- [开发指南](../developer_guide.md) - 工具模块开发
- [性能优化指南](../performance_optimization.md) - 性能优化
- [配置指南](../configuration.md) - 配置管理
