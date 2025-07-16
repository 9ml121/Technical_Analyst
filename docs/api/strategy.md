# 策略引擎 API 文档

## 🎯 模块概述

策略引擎是量化投资系统的核心模块，负责策略的开发、执行和管理。支持多种内置策略和自定义策略开发。

## 🏗️ 模块架构

```
quant_system/core/
├── strategy_engine.py         # 策略引擎核心
├── trading_strategy.py        # 交易策略基类
├── ml_enhanced_strategy.py    # 机器学习增强策略
└── feature_extraction.py     # 特征提取模块
```

## 🚀 策略引擎 (StrategyEngine)

### 类定义

```python
class StrategyEngine:
    """策略引擎核心类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """初始化策略引擎"""
        
    def load_config(self, config_file: str) -> SelectionCriteria:
        """加载策略配置"""
        
    def select_stocks(self, stock_data: List[StockData]) -> List[StockData]:
        """选股逻辑"""
        
    def generate_trading_signals(self, stock_data: List[StockData]) -> List[TradingSignal]:
        """生成交易信号"""
```

### 方法详解

#### load_config()

加载策略配置文件，支持YAML格式。

**参数:**
- `config_file` (str): 配置文件路径

**返回:**
- `SelectionCriteria`: 选股条件对象

**示例:**
```python
from quant_system.core.strategy_engine import StrategyEngine

engine = StrategyEngine()
criteria = engine.load_config('config/strategies/momentum_strategy.yaml')
print(f"连续上涨天数: {criteria.consecutive_days}")
```

#### select_stocks()

根据配置的选股条件筛选股票。

**参数:**
- `stock_data` (List[StockData]): 股票数据列表

**返回:**
- `List[StockData]`: 筛选后的股票列表

**选股条件:**
- 连续上涨天数
- 最小总收益率
- 最大回撤限制
- 价格区间过滤
- 市值区间过滤

#### generate_trading_signals()

基于选股结果生成交易信号。

**参数:**
- `stock_data` (List[StockData]): 股票数据列表

**返回:**
- `List[TradingSignal]`: 交易信号列表

## 📈 内置策略

### MomentumStrategy (动量策略)

基于价格动量的选股策略，寻找连续上涨的股票。

#### 类定义

```python
class MomentumStrategy(BaseStrategy):
    """动量策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化动量策略"""
        
    def select_stocks(self, market_data: List[StockData]) -> List[StockData]:
        """动量选股逻辑"""
        
    def generate_signals(self, stocks: List[StockData]) -> List[TradingSignal]:
        """生成交易信号"""
```

#### 策略参数

```yaml
# 动量策略配置示例
basic_criteria:
  consecutive_days: 3          # 连续上涨天数
  min_total_return: 0.15       # 最小总收益率 (15%)
  max_drawdown: 0.05           # 最大回撤限制 (5%)
  exclude_limit_up_first_day: true  # 排除首日涨停

price_filters:
  min_stock_price: 5.0         # 最低股价
  max_stock_price: 200.0       # 最高股价
  
risk_management:
  max_positions: 5             # 最大持仓数量
  position_size_pct: 0.20      # 单股仓位比例
```

#### 使用示例

```python
from quant_system.strategy.momentum import MomentumStrategy

# 创建策略
strategy = MomentumStrategy({
    'consecutive_days': 3,
    'min_total_return': 0.15,
    'max_positions': 5
})

# 运行策略
selected_stocks = strategy.select_stocks(market_data)
signals = strategy.generate_signals(selected_stocks)

print(f"选中股票数量: {len(selected_stocks)}")
print(f"生成信号数量: {len(signals)}")
```

### MLEnhancedStrategy (机器学习增强策略)

结合机器学习模型的高级策略，支持多因子分析和预测。

#### 类定义

```python
class MLEnhancedStrategy:
    """机器学习增强策略"""
    
    def __init__(self, config: MLStrategyConfig):
        """初始化ML策略"""
        
    def train_model(self, training_data: List[List[StockData]]) -> Dict[str, Any]:
        """训练机器学习模型"""
        
    def predict_return(self, stock_data: List[StockData]) -> Tuple[float, float]:
        """预测股票收益率"""
        
    def generate_ml_signals(self, stocks: List[StockData]) -> List[TradingSignal]:
        """生成ML交易信号"""
```

#### 模型配置

```yaml
# ML策略配置示例
model_config:
  model_type: "random_forest"    # 模型类型
  n_estimators: 200              # 树的数量
  max_depth: 15                  # 最大深度
  feature_selection: "kbest"     # 特征选择方法
  n_features: 20                 # 特征数量
  target_horizon: 5              # 预测时间窗口

signal_config:
  signal_threshold: 0.02         # 信号阈值
  confidence_threshold: 0.6      # 置信度阈值
```

#### 特征工程

支持的特征类型：

1. **技术指标特征**
   - 价格相关: 收益率、波动率、价格位置
   - 成交量相关: 成交量比率、资金流向
   - 技术指标: MA、MACD、RSI、布林带

2. **基本面特征**
   - 财务指标特征
   - 行业相对指标
   - 市场情绪指标

#### 使用示例

```python
from quant_system.core.ml_enhanced_strategy import MLEnhancedStrategy, MLStrategyConfig

# 创建配置
config = MLStrategyConfig(
    name="ML增强策略",
    model_config=ModelConfig(
        model_type='random_forest',
        n_estimators=200,
        max_depth=15
    ),
    signal_threshold=0.02,
    confidence_threshold=0.6
)

# 创建策略
strategy = MLEnhancedStrategy(config)

# 训练模型
training_results = strategy.train_model(training_data)
print(f"模型R²: {training_results['train_r2']:.3f}")

# 生成预测
prediction, confidence = strategy.predict_return(stock_data)
print(f"预测收益率: {prediction:.2%}, 置信度: {confidence:.2f}")
```

## 🎨 自定义策略开发

### BaseStrategy 基类

所有策略都应继承自BaseStrategy基类。

```python
from quant_system.strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    """自定义策略示例"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "我的自定义策略"
        
    def select_stocks(self, market_data: List[StockData]) -> List[StockData]:
        """实现选股逻辑"""
        selected = []
        
        for stock in market_data:
            if self._meets_criteria(stock):
                selected.append(stock)
                
        return selected
    
    def generate_signals(self, stocks: List[StockData]) -> List[TradingSignal]:
        """实现信号生成逻辑"""
        signals = []
        
        for stock in stocks:
            signal = TradingSignal(
                code=stock.code,
                signal_type='BUY',
                price=stock.close_price,
                timestamp=stock.date,
                confidence=0.8,
                reason="自定义策略信号"
            )
            signals.append(signal)
            
        return signals
    
    def _meets_criteria(self, stock: StockData) -> bool:
        """检查股票是否满足条件"""
        # 实现具体的筛选逻辑
        return True
```

### 策略注册

```python
from quant_system.strategy.registry import StrategyRegistry

# 注册自定义策略
StrategyRegistry.register('my_custom_strategy', MyCustomStrategy)

# 使用注册的策略
strategy = StrategyRegistry.create('my_custom_strategy', config)
```

## 🔄 策略执行流程

### 完整执行流程

```python
from quant_system.core.strategy_engine import StrategyEngine
from market_data import get_eastmoney_api

# 1. 初始化
engine = StrategyEngine('config/strategies/momentum_strategy.yaml')
api = get_eastmoney_api()

# 2. 获取市场数据
market_data = api.get_a_stock_realtime(limit=100)

# 3. 数据预处理
processed_data = engine.preprocess_data(market_data)

# 4. 执行选股
selected_stocks = engine.select_stocks(processed_data)

# 5. 生成交易信号
signals = engine.generate_trading_signals(selected_stocks)

# 6. 风险控制
filtered_signals = engine.apply_risk_management(signals)

print(f"原始股票数量: {len(market_data)}")
print(f"选中股票数量: {len(selected_stocks)}")
print(f"生成信号数量: {len(filtered_signals)}")
```

## 📊 策略性能评估

### 性能指标

```python
class StrategyPerformance:
    """策略性能评估"""
    
    def calculate_metrics(self, signals: List[TradingSignal], 
                         actual_returns: List[float]) -> Dict[str, float]:
        """计算性能指标"""
        return {
            'total_return': self._calculate_total_return(actual_returns),
            'sharpe_ratio': self._calculate_sharpe_ratio(actual_returns),
            'max_drawdown': self._calculate_max_drawdown(actual_returns),
            'win_rate': self._calculate_win_rate(actual_returns),
            'profit_factor': self._calculate_profit_factor(actual_returns)
        }
```

### 使用示例

```python
from quant_system.analysis import StrategyPerformance

performance = StrategyPerformance()
metrics = performance.calculate_metrics(signals, actual_returns)

print(f"总收益率: {metrics['total_return']:.2%}")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {metrics['max_drawdown']:.2%}")
print(f"胜率: {metrics['win_rate']:.2%}")
```

## 🚨 异常处理

### 策略异常

```python
class StrategyError(Exception):
    """策略执行错误"""
    
class ConfigurationError(Exception):
    """配置错误"""
    
class ModelTrainingError(Exception):
    """模型训练错误"""
```

### 错误处理示例

```python
try:
    strategy = MLEnhancedStrategy(config)
    results = strategy.train_model(training_data)
except ModelTrainingError as e:
    logger.error(f"模型训练失败: {e}")
except ConfigurationError as e:
    logger.error(f"配置错误: {e}")
```

## 🔗 相关文档

- [回测系统](backtest.md) - 策略回测
- [配置指南](../configuration.md) - 策略配置
- [用户指南](../user_guide.md) - 策略使用指南
