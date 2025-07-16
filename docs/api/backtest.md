# 回测系统 API 文档

## 📈 模块概述

回测系统提供完整的历史数据回测功能，支持策略性能评估、风险分析和报告生成。

## 🏗️ 模块架构

```
quant_system/core/
├── backtest_engine.py         # 回测引擎核心
├── trading_simulator.py       # 交易模拟器
└── analysis_module.py         # 分析模块
```

## 🚀 回测引擎 (BacktestEngine)

### 类定义

```python
class QuantitativeBacktestEngine:
    """量化回测引擎"""
    
    def __init__(self):
        """初始化回测引擎"""
        
    def run_backtest(self, strategy: StrategyEngine, start_date: date, 
                     end_date: date, config: Optional[BacktestConfig] = None) -> Dict:
        """运行回测"""
        
    def generate_report(self, results: Dict) -> BacktestReport:
        """生成回测报告"""
```

### 方法详解

#### run_backtest()

执行完整的回测流程。

**参数:**
- `strategy` (StrategyEngine): 策略引擎实例
- `start_date` (date): 回测开始日期
- `end_date` (date): 回测结束日期
- `config` (BacktestConfig, optional): 回测配置

**返回:**
- `Dict`: 回测结果字典

**示例:**
```python
from quant_system.core.backtest_engine import QuantitativeBacktestEngine
from quant_system.core.strategy_engine import StrategyEngine
from quant_system.models.backtest_models import BacktestConfig
from datetime import date, timedelta

# 创建回测引擎和策略
backtest_engine = QuantitativeBacktestEngine()
strategy = StrategyEngine('config/strategies/momentum_strategy.yaml')

# 配置回测参数
config = BacktestConfig(
    start_date=date(2023, 1, 1),
    end_date=date(2024, 1, 1),
    initial_capital=1000000,  # 100万初始资金
    max_positions=5,          # 最大持仓5只
    commission_rate=0.0003,   # 手续费率0.03%
    slippage_rate=0.001       # 滑点0.1%
)

# 运行回测
results = backtest_engine.run_backtest(strategy, config.start_date, config.end_date, config)

print(f"总收益率: {results['total_return']:.2%}")
print(f"年化收益率: {results['annual_return']:.2%}")
print(f"最大回撤: {results['max_drawdown']:.2%}")
```

## 📊 回测配置 (BacktestConfig)

### 配置参数

```python
@dataclass
class BacktestConfig:
    """回测配置"""
    
    start_date: date                    # 开始日期
    end_date: date                      # 结束日期
    initial_capital: float = 1000000    # 初始资金
    max_positions: int = 10             # 最大持仓数量
    position_size_pct: float = 0.1      # 单股仓位比例
    commission_rate: float = 0.0003     # 手续费率
    slippage_rate: float = 0.001        # 滑点率
    min_trade_amount: float = 1000      # 最小交易金额
```

### 配置验证

```python
def validate_backtest_config(config: BacktestConfig) -> bool:
    """验证回测配置"""
    
    # 日期验证
    if config.start_date >= config.end_date:
        raise ValueError("开始日期必须早于结束日期")
    
    # 资金验证
    if config.initial_capital <= 0:
        raise ValueError("初始资金必须大于0")
    
    # 仓位验证
    if not 0 < config.position_size_pct <= 1:
        raise ValueError("仓位比例必须在0-1之间")
    
    return True
```

## 🎮 交易模拟器 (TradingSimulator)

### 类定义

```python
class TradingSimulator:
    """交易模拟器"""
    
    def __init__(self, config: BacktestConfig):
        """初始化交易模拟器"""
        
    def execute_trade(self, signal: TradingSignal, market_data: Dict) -> TradeRecord:
        """执行交易"""
        
    def update_positions(self, market_data: Dict, current_date: date):
        """更新持仓"""
        
    def calculate_portfolio_value(self, current_date: date) -> float:
        """计算组合价值"""
```

### 交易执行

#### execute_trade()

执行交易信号，考虑手续费和滑点。

**参数:**
- `signal` (TradingSignal): 交易信号
- `market_data` (Dict): 市场数据

**返回:**
- `TradeRecord`: 交易记录

**交易规则:**
- T+1交易制度
- 手续费计算
- 滑点模拟
- 涨跌停限制

#### 示例

```python
from quant_system.models.strategy_models import TradingSignal
from quant_system.models.backtest_models import TradeRecord

# 创建交易信号
signal = TradingSignal(
    code='000001',
    signal_type='BUY',
    price=12.50,
    timestamp=date.today(),
    confidence=0.8,
    reason="动量策略买入信号"
)

# 执行交易
trade_record = simulator.execute_trade(signal, market_data)

print(f"交易股票: {trade_record.stock_code}")
print(f"交易类型: {trade_record.action}")
print(f"交易价格: {trade_record.price}")
print(f"交易数量: {trade_record.quantity}")
print(f"手续费: {trade_record.commission}")
```

## 📈 性能分析 (PerformanceAnalyzer)

### 类定义

```python
class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        """初始化分析器"""
        
    def calculate_returns(self, portfolio_values: List[float]) -> List[float]:
        """计算收益率序列"""
        
    def calculate_metrics(self, returns: List[float]) -> Dict[str, float]:
        """计算性能指标"""
        
    def calculate_risk_metrics(self, returns: List[float]) -> Dict[str, float]:
        """计算风险指标"""
```

### 性能指标

#### 收益指标

```python
def calculate_total_return(returns: List[float]) -> float:
    """总收益率"""
    
def calculate_annual_return(returns: List[float], trading_days: int = 252) -> float:
    """年化收益率"""
    
def calculate_cumulative_returns(returns: List[float]) -> List[float]:
    """累计收益率序列"""
```

#### 风险指标

```python
def calculate_volatility(returns: List[float]) -> float:
    """波动率"""
    
def calculate_max_drawdown(portfolio_values: List[float]) -> float:
    """最大回撤"""
    
def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.03) -> float:
    """夏普比率"""
    
def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.03) -> float:
    """索提诺比率"""
```

#### 交易指标

```python
def calculate_win_rate(trades: List[TradeRecord]) -> float:
    """胜率"""
    
def calculate_profit_factor(trades: List[TradeRecord]) -> float:
    """盈亏比"""
    
def calculate_average_holding_period(trades: List[TradeRecord]) -> float:
    """平均持仓周期"""
```

### 使用示例

```python
from quant_system.core.analysis_module import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()

# 计算收益率
returns = analyzer.calculate_returns(portfolio_values)

# 计算性能指标
metrics = analyzer.calculate_metrics(returns)
risk_metrics = analyzer.calculate_risk_metrics(returns)

print("=== 收益指标 ===")
print(f"总收益率: {metrics['total_return']:.2%}")
print(f"年化收益率: {metrics['annual_return']:.2%}")

print("=== 风险指标 ===")
print(f"波动率: {risk_metrics['volatility']:.2%}")
print(f"最大回撤: {risk_metrics['max_drawdown']:.2%}")
print(f"夏普比率: {risk_metrics['sharpe_ratio']:.2f}")
```

## 📋 回测报告 (BacktestReport)

### 报告生成

```python
class BacktestReport:
    """回测报告"""
    
    def __init__(self, results: Dict):
        """初始化报告"""
        
    def generate_summary(self) -> Dict[str, Any]:
        """生成摘要报告"""
        
    def generate_detailed_report(self) -> str:
        """生成详细报告"""
        
    def save_to_file(self, filename: str):
        """保存报告到文件"""
```

### 报告内容

#### 摘要报告

```python
summary = {
    "回测期间": "2023-01-01 到 2024-01-01",
    "初始资金": 1000000,
    "最终资金": 1250000,
    "总收益率": "25.00%",
    "年化收益率": "25.00%",
    "最大回撤": "-8.50%",
    "夏普比率": 1.85,
    "胜率": "65.5%",
    "交易次数": 156,
    "平均持仓天数": 8.5
}
```

#### 详细报告

包含以下部分：
1. 回测配置信息
2. 策略参数设置
3. 性能指标详情
4. 风险分析结果
5. 交易记录统计
6. 月度收益分析
7. 持仓分析

### 使用示例

```python
# 生成回测报告
report = BacktestReport(backtest_results)

# 获取摘要
summary = report.generate_summary()
print("回测摘要:")
for key, value in summary.items():
    print(f"  {key}: {value}")

# 生成详细报告
detailed_report = report.generate_detailed_report()
print("\n详细报告:")
print(detailed_report)

# 保存报告
report.save_to_file(f"backtest_report_{date.today()}.txt")
```

## 🔧 高级功能

### 多策略回测

```python
def run_multi_strategy_backtest(strategies: List[StrategyEngine], 
                               config: BacktestConfig) -> Dict[str, Dict]:
    """多策略回测"""
    
    results = {}
    
    for strategy in strategies:
        strategy_name = strategy.name
        strategy_results = backtest_engine.run_backtest(
            strategy, config.start_date, config.end_date, config)
        results[strategy_name] = strategy_results
    
    return results
```

### 参数优化

```python
def optimize_strategy_parameters(strategy_class, parameter_ranges: Dict, 
                               config: BacktestConfig) -> Dict:
    """策略参数优化"""
    
    best_params = None
    best_performance = -float('inf')
    
    for params in generate_parameter_combinations(parameter_ranges):
        strategy = strategy_class(params)
        results = backtest_engine.run_backtest(
            strategy, config.start_date, config.end_date, config)
        
        if results['sharpe_ratio'] > best_performance:
            best_performance = results['sharpe_ratio']
            best_params = params
    
    return {
        'best_params': best_params,
        'best_performance': best_performance
    }
```

### 滚动回测

```python
def run_rolling_backtest(strategy: StrategyEngine, 
                        start_date: date, end_date: date,
                        window_size: int = 252) -> List[Dict]:
    """滚动回测"""
    
    results = []
    current_date = start_date
    
    while current_date + timedelta(days=window_size) <= end_date:
        window_end = current_date + timedelta(days=window_size)
        
        window_results = backtest_engine.run_backtest(
            strategy, current_date, window_end, config)
        
        results.append({
            'start_date': current_date,
            'end_date': window_end,
            'results': window_results
        })
        
        current_date += timedelta(days=30)  # 每月滚动
    
    return results
```

## 🚨 异常处理

### 回测异常

```python
class BacktestError(Exception):
    """回测执行错误"""
    
class InsufficientDataError(Exception):
    """数据不足错误"""
    
class InvalidConfigError(Exception):
    """配置无效错误"""
```

### 错误处理示例

```python
try:
    results = backtest_engine.run_backtest(strategy, start_date, end_date, config)
except InsufficientDataError as e:
    logger.error(f"数据不足: {e}")
except InvalidConfigError as e:
    logger.error(f"配置错误: {e}")
except BacktestError as e:
    logger.error(f"回测执行失败: {e}")
```

## 🔗 相关文档

- [策略引擎](strategy.md) - 策略开发
- [数据模型](models/backtest.md) - 回测数据模型
- [用户指南](../user_guide.md) - 回测使用指南
