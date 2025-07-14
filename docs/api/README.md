# API 文档

量化投资系统的完整API参考文档。

## 📚 模块概览

### 核心模块

- [行情数据模块](market_data.md) - 数据获取和处理
- [策略引擎](strategy.md) - 策略开发和执行
- [回测系统](backtest.md) - 历史数据回测
- [配置系统](config.md) - 配置管理
- [工具模块](utils.md) - 辅助工具和函数

### 数据模型

- [股票数据模型](models/stock_data.md) - 股票数据结构
- [策略模型](models/strategy.md) - 策略相关数据结构
- [回测模型](models/backtest.md) - 回测相关数据结构

## 🚀 快速开始

### 基本用法

```python
from quant_system import QuantSystem

# 初始化系统
system = QuantSystem()

# 获取实时数据
data = system.get_realtime_data(['000001', '600000'])

# 运行策略
strategy = system.load_strategy('momentum_strategy')
signals = strategy.run(data)

# 执行回测
backtest = system.create_backtest(strategy)
results = backtest.run()
```

### 配置系统

```python
from quant_system.utils import ConfigLoader

# 加载配置
config = ConfigLoader()
system_config = config.load_config('default')
strategy_config = config.load_strategy_config('momentum_strategy')
```

## 📊 数据获取

### 实时数据

```python
from market_data import get_eastmoney_api

api = get_eastmoney_api()

# 获取A股实时数据
stocks = api.get_a_stock_realtime(limit=10)

# 获取特定股票详情
detail = api.get_stock_detail('000001')
```

### 历史数据

```python
from market_data.processors import MarketDataProcessor

processor = MarketDataProcessor()

# 处理历史数据
historical_data = processor.load_historical_data('000001', '2023-01-01', '2024-01-01')
processed_data = processor.calculate_technical_indicators(historical_data)
```

## 🎯 策略开发

### 基础策略类

```python
from quant_system.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "我的策略"
    
    def select_stocks(self, market_data):
        """选股逻辑"""
        # 实现选股算法
        return selected_stocks
    
    def generate_signals(self, stocks):
        """生成交易信号"""
        # 实现信号生成逻辑
        return signals
    
    def manage_risk(self, portfolio):
        """风险管理"""
        # 实现风险控制逻辑
        return risk_actions
```

### 内置策略

```python
from quant_system.strategy.momentum import MomentumStrategy

# 使用内置动量策略
strategy = MomentumStrategy({
    'consecutive_days': 3,
    'min_return': 0.15,
    'max_positions': 5
})
```

## 📈 回测系统

### 创建回测

```python
from quant_system.backtest import BacktestEngine

# 创建回测引擎
engine = BacktestEngine({
    'start_date': '2023-01-01',
    'end_date': '2024-01-01',
    'initial_capital': 1000000,
    'commission_rate': 0.0003
})

# 运行回测
results = engine.run(strategy)
```

### 性能分析

```python
from quant_system.backtest.analysis import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(results)

# 计算性能指标
metrics = analyzer.calculate_metrics()
print(f"总收益率: {metrics['total_return']:.2%}")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {metrics['max_drawdown']:.2%}")
```

## ⚙️ 配置管理

### 配置加载

```python
from quant_system.utils.config_loader import ConfigLoader

loader = ConfigLoader()

# 加载不同类型的配置
system_config = loader.load_config('default')
env_config = loader.get_environment_config('production')
strategy_config = loader.load_strategy_config('momentum_strategy')
data_sources_config = loader.load_data_sources_config()
```

### 配置验证

```python
from quant_system.utils.config_validator import ConfigValidator

validator = ConfigValidator()

# 验证配置
is_valid = validator.validate_system_config(system_config)
if not is_valid:
    print("配置错误:", validator.errors)
```

## 🛠️ 工具函数

### 数据验证

```python
from quant_system.utils.validators import validate_stock_data, StockCodeValidator

# 验证股票代码
is_valid = StockCodeValidator.is_valid_a_share('000001')

# 验证股票数据
errors = validate_stock_data({
    'code': '000001',
    'price': 12.50,
    'volume': 1000000
})
```

### 辅助函数

```python
from quant_system.utils.helpers import (
    calculate_percentage_change,
    format_currency,
    get_trading_dates
)

# 计算百分比变化
change = calculate_percentage_change(100, 120)  # 0.2

# 格式化货币
formatted = format_currency(1234567.89)  # "¥123.46万"

# 获取交易日期
dates = get_trading_dates('2024-01-01', '2024-01-31')
```

## 🔍 错误处理

### 异常类型

```python
from quant_system.exceptions import (
    DataSourceError,
    StrategyError,
    BacktestError,
    ConfigError
)

try:
    data = api.get_stock_detail('INVALID')
except DataSourceError as e:
    print(f"数据源错误: {e}")
```

### 日志系统

```python
from quant_system.utils.logger import get_logger

logger = get_logger(__name__)

logger.info("开始获取数据")
logger.warning("数据质量警告")
logger.error("处理失败", exc_info=True)
```

## 📝 类型提示

系统使用类型提示来提高代码质量：

```python
from typing import List, Dict, Optional
from quant_system.models import StockData, TradingSignal

def process_stocks(stocks: List[StockData]) -> List[TradingSignal]:
    """处理股票数据并生成交易信号"""
    signals: List[TradingSignal] = []
    
    for stock in stocks:
        signal = generate_signal(stock)
        if signal:
            signals.append(signal)
    
    return signals
```

## 🧪 测试支持

### 测试工具

```python
from quant_system.testing import MockDataProvider, TestStrategy

# 使用模拟数据
mock_data = MockDataProvider()
test_data = mock_data.generate_stock_data('000001', days=30)

# 测试策略
test_strategy = TestStrategy()
results = test_strategy.backtest(test_data)
```

## 📊 性能优化

### 并发处理

```python
from quant_system.utils.concurrent import parallel_process

# 并行处理多只股票
results = parallel_process(
    process_stock_data,
    stock_list,
    max_workers=4
)
```

### 缓存机制

```python
from quant_system.utils.cache import cache_result

@cache_result(ttl=3600)  # 缓存1小时
def expensive_calculation(stock_code: str):
    # 耗时计算
    return result
```

## 🔗 扩展开发

### 自定义数据源

```python
from quant_system.market_data.base import BaseDataFetcher

class CustomDataFetcher(BaseDataFetcher):
    def get_realtime_data(self, codes: List[str]) -> List[StockData]:
        # 实现自定义数据获取逻辑
        pass
```

### 插件系统

```python
from quant_system.plugins import BasePlugin

class MyPlugin(BasePlugin):
    def initialize(self):
        # 插件初始化
        pass
    
    def process(self, data):
        # 插件处理逻辑
        return processed_data
```

## 📚 更多资源

- [完整API参考](api_reference.md)
- [示例代码](../examples/)
- [常见问题](../faq.md)
- [更新日志](../changelog.md)

---

如需更详细的API文档，请查看各个模块的具体文档页面。
