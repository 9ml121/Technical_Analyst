# 用户使用指南

欢迎使用量化投资系统！本指南将帮助您快速上手并充分利用系统的各项功能。

## 📋 目录

1. [系统概述](#系统概述)
2. [安装和配置](#安装和配置)
3. [基础使用](#基础使用)
4. [数据获取](#数据获取)
5. [策略开发](#策略开发)
6. [回测分析](#回测分析)
7. [实盘交易](#实盘交易)
8. [配置管理](#配置管理)
9. [常见问题](#常见问题)

## 🎯 系统概述

量化投资系统是一个专业的股票量化交易平台，支持：

- **多市场支持**: A股、港股通H股
- **实时数据**: 多数据源实时行情获取
- **策略引擎**: 灵活的量化策略开发框架
- **回测系统**: 完整的历史数据回测和性能分析
- **风险管理**: 多层次风险控制机制

## 🚀 安装和配置

### 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Linux
- **Python版本**: 3.9 或更高版本
- **内存**: 8GB 推荐 (最低 4GB)
- **存储**: 10GB 可用空间
- **网络**: 稳定的互联网连接

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-username/quantitative-investment-system.git
   cd quantitative-investment-system
   ```

2. **创建虚拟环境**
   ```bash
   # 使用 venv
   python -m venv quant_env
   source quant_env/bin/activate  # Linux/macOS
   # 或
   quant_env\Scripts\activate     # Windows
   
   # 使用 conda
   conda create -n quant_system python=3.9
   conda activate quant_system
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **验证安装**
   ```bash
   python scripts/run_tests.py check
   ```

### 初始配置

1. **环境配置**
   ```bash
   # 设置环境变量
   export ENVIRONMENT=development
   
   # Windows
   set ENVIRONMENT=development
   ```

2. **数据源配置**
   ```bash
   # 查看配置
   python scripts/config_manager.py show data_sources
   
   # 验证配置
   python scripts/config_manager.py validate
   ```

3. **Tushare配置** (可选)
   ```bash
   # 设置Tushare token
   export TUSHARE_TOKEN=your_token_here
   ```

## 📊 基础使用

### 快速开始

1. **获取实时行情**
   ```python
   from market_data import get_eastmoney_api
   
   # 初始化API
   api = get_eastmoney_api()
   
   # 获取A股实时数据
   stocks = api.get_a_stock_realtime(limit=10)
   for stock in stocks:
       print(f"{stock['name']}: {stock['price']}")
   ```

2. **运行简单策略**
   ```python
   from quant_system.strategy.momentum import MomentumStrategy
   
   # 创建策略
   strategy = MomentumStrategy({
       'consecutive_days': 3,
       'min_return': 0.15
   })
   
   # 运行策略
   selected_stocks = strategy.select_stocks(stocks)
   ```

3. **执行回测**
   ```python
   from quant_system.backtest import BacktestEngine
   
   # 创建回测
   backtest = BacktestEngine({
       'start_date': '2023-01-01',
       'end_date': '2024-01-01',
       'initial_capital': 1000000
   })
   
   # 运行回测
   results = backtest.run(strategy)
   print(f"总收益率: {results.total_return:.2%}")
   ```

### 命令行工具

系统提供了便捷的命令行工具：

```bash
# 配置管理
python scripts/config_manager.py list
python scripts/config_manager.py validate
python scripts/config_manager.py create-strategy

# 测试运行
python scripts/run_tests.py unit
python scripts/run_tests.py coverage

# 数据获取
python examples/get_realtime_data.py
python examples/get_historical_data.py
```

## 📈 数据获取

### 支持的数据源

| 数据源 | 类型 | 市场 | 特点 |
|--------|------|------|------|
| 东方财富 | 免费 | A股 | 实时数据，无需注册 |
| Tushare | 付费 | A股、港股 | 高质量数据，需要token |
| Yahoo Finance | 免费 | 全球 | 国际市场支持 |

### 实时数据获取

```python
from market_data import get_eastmoney_api

api = get_eastmoney_api()

# 获取指定股票实时数据
stocks = ['000001', '600000', '000002']
data = api.get_a_stock_realtime(stocks)

# 获取股票详细信息
detail = api.get_stock_detail('000001')
print(f"股票名称: {detail['name']}")
print(f"当前价格: {detail['price']}")
print(f"涨跌幅: {detail['pct_change']:.2%}")
```

### 历史数据处理

```python
from market_data.processors import MarketDataProcessor

processor = MarketDataProcessor()

# 加载历史数据
historical_data = processor.load_historical_data(
    '000001', 
    start_date='2023-01-01',
    end_date='2024-01-01'
)

# 计算技术指标
data_with_indicators = processor.calculate_technical_indicators(historical_data)

# 数据清洗和筛选
cleaned_data = processor.clean_stock_data(data_with_indicators)
filtered_data = processor.filter_stocks(cleaned_data, {
    'min_price': 5.0,
    'min_volume': 1000000
})
```

## 🎯 策略开发

### 使用内置策略

系统提供了多种内置策略：

1. **动量策略**
   ```python
   from quant_system.strategy.momentum import MomentumStrategy
   
   strategy = MomentumStrategy({
       'consecutive_days': 3,      # 连续上涨天数
       'min_total_return': 0.15,   # 最小总收益率
       'max_drawdown': 0.05,       # 最大回撤限制
       'max_positions': 5          # 最大持仓数量
   })
   ```

2. **均值回归策略**
   ```python
   from quant_system.strategy.mean_reversion import MeanReversionStrategy
   
   strategy = MeanReversionStrategy({
       'lookback_period': 20,      # 回看周期
       'deviation_threshold': 2.0,  # 偏离阈值
       'reversion_threshold': 0.5   # 回归阈值
   })
   ```

### 开发自定义策略

```python
from quant_system.strategy import BaseStrategy

class MyCustomStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "我的自定义策略"
        self.description = "基于自定义逻辑的选股策略"
    
    def select_stocks(self, market_data):
        """选股逻辑"""
        selected = []
        
        for stock in market_data:
            # 自定义选股条件
            if (stock['pct_change'] > 0.05 and 
                stock['volume'] > 10000000 and
                stock['price'] > 10.0):
                selected.append(stock)
        
        return selected[:self.config.get('max_positions', 5)]
    
    def generate_signals(self, stocks):
        """生成交易信号"""
        signals = []
        
        for stock in stocks:
            signal = {
                'code': stock['code'],
                'action': 'buy',
                'price': stock['price'],
                'quantity': self.calculate_position_size(stock),
                'reason': '满足自定义条件'
            }
            signals.append(signal)
        
        return signals
    
    def calculate_position_size(self, stock):
        """计算仓位大小"""
        # 等权重分配
        return int(self.config.get('position_size', 10000) / stock['price'])
```

### 策略配置

创建策略配置文件：

```bash
python scripts/config_manager.py create-strategy
```

编辑策略配置：

```yaml
# config/strategies/my_strategy.yaml
strategy_info:
  name: "我的策略"
  version: "1.0.0"
  description: "自定义策略描述"
  strategy_type: "custom"

selection_criteria:
  basic_criteria:
    consecutive_days: 3
    min_total_return: 0.15
    max_drawdown: 0.05
  
  price_filters:
    min_stock_price: 5.0
    max_stock_price: 200.0
  
  volume_filters:
    min_avg_volume: 10000000
    min_turnover_rate: 0.01

trading_rules:
  buy_rules:
    - name: "价格突破"
      condition: "price > ma20"
      enabled: true
  
  sell_rules:
    - name: "止盈"
      condition: "profit_pct >= 0.20"
      enabled: true
    - name: "止损"
      condition: "loss_pct >= 0.05"
      enabled: true

risk_management:
  max_single_position: 0.20
  max_sector_exposure: 0.40
  stop_loss_pct: 0.05
  take_profit_pct: 0.20
```

## 📊 回测分析

### 创建回测

```python
from quant_system.backtest import BacktestEngine

# 配置回测参数
backtest_config = {
    'start_date': '2023-01-01',
    'end_date': '2024-01-01',
    'initial_capital': 1000000.0,
    'max_positions': 10,
    'commission_rate': 0.0003,
    'stamp_tax_rate': 0.001,
    'slippage_rate': 0.001
}

# 创建回测引擎
engine = BacktestEngine(backtest_config)

# 运行回测
results = engine.run(strategy)
```

### 性能分析

```python
from quant_system.backtest.analysis import PerformanceAnalyzer

analyzer = PerformanceAnalyzer(results)

# 计算基础指标
metrics = analyzer.calculate_metrics()
print(f"总收益率: {metrics['total_return']:.2%}")
print(f"年化收益率: {metrics['annual_return']:.2%}")
print(f"最大回撤: {metrics['max_drawdown']:.2%}")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"胜率: {metrics['win_rate']:.2%}")

# 生成详细报告
report = analyzer.generate_report()
print(report)
```

### 可视化分析

```python
import matplotlib.pyplot as plt

# 绘制净值曲线
analyzer.plot_equity_curve()
plt.title('策略净值曲线')
plt.show()

# 绘制回撤图
analyzer.plot_drawdown()
plt.title('回撤分析')
plt.show()

# 绘制月度收益热力图
analyzer.plot_monthly_returns()
plt.title('月度收益热力图')
plt.show()
```

### 风险分析

```python
# 计算风险指标
risk_metrics = analyzer.calculate_risk_metrics()
print(f"VaR (95%): {risk_metrics['var_95']:.2%}")
print(f"CVaR (95%): {risk_metrics['cvar_95']:.2%}")
print(f"波动率: {risk_metrics['volatility']:.2%}")
print(f"下行波动率: {risk_metrics['downside_volatility']:.2%}")

# 相关性分析
correlation = analyzer.calculate_correlation_with_benchmark()
print(f"与基准相关性: {correlation:.3f}")
```

## 💼 实盘交易

### 模拟交易

在实盘交易前，建议先进行模拟交易：

```python
from quant_system.trading import SimulatedTrader

# 创建模拟交易器
trader = SimulatedTrader({
    'initial_capital': 1000000,
    'commission_rate': 0.0003
})

# 执行交易信号
for signal in signals:
    order = trader.place_order(
        code=signal['code'],
        action=signal['action'],
        quantity=signal['quantity'],
        price=signal['price']
    )
    print(f"订单状态: {order.status}")

# 查看持仓
positions = trader.get_positions()
for pos in positions:
    print(f"{pos.stock_name}: {pos.quantity}股, 盈亏: {pos.unrealized_pnl:.2f}")
```

### 实盘交易接口

```python
from quant_system.trading import RealTrader

# 注意：实盘交易需要券商API接入
trader = RealTrader({
    'broker': 'your_broker',
    'account': 'your_account',
    'api_key': 'your_api_key'
})

# 实盘交易流程
def execute_strategy():
    # 1. 获取实时数据
    market_data = get_market_data()
    
    # 2. 运行策略
    signals = strategy.run(market_data)
    
    # 3. 风险检查
    validated_signals = risk_manager.validate_signals(signals)
    
    # 4. 执行交易
    for signal in validated_signals:
        trader.place_order(signal)
    
    # 5. 监控持仓
    trader.monitor_positions()
```

## ⚙️ 配置管理

### 环境配置

系统支持多环境配置：

```bash
# 开发环境
export ENVIRONMENT=development

# 测试环境
export ENVIRONMENT=testing

# 生产环境
export ENVIRONMENT=production
```

### 配置文件管理

```bash
# 查看所有配置
python scripts/config_manager.py list

# 验证配置
python scripts/config_manager.py validate

# 查看特定配置
python scripts/config_manager.py show momentum_strategy

# 创建新策略配置
python scripts/config_manager.py create-strategy
```

### 自定义配置

编辑配置文件：

```yaml
# config/environments/production.yaml
system:
  environment: "production"
  debug: false

logging:
  level: "INFO"
  console: false

data_sources:
  eastmoney:
    enabled: true
    timeout: 15
  
  tushare:
    enabled: true
    timeout: 30

backtest:
  initial_capital: 1000000.0
  commission_rate: 0.0003
  max_positions: 10
```

## ❓ 常见问题

### 安装问题

**Q: 安装依赖时出现错误？**
A: 确保Python版本为3.9+，建议使用虚拟环境：
```bash
python --version
pip install --upgrade pip
pip install -r requirements.txt
```

**Q: 导入模块失败？**
A: 检查PYTHONPATH设置：
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### 数据获取问题

**Q: 无法获取实时数据？**
A: 检查网络连接和数据源配置：
```bash
python scripts/config_manager.py show data_sources
```

**Q: Tushare数据获取失败？**
A: 确认token设置正确：
```bash
export TUSHARE_TOKEN=your_token_here
```

### 策略运行问题

**Q: 策略回测结果异常？**
A: 检查数据质量和策略参数：
```python
# 验证数据
from quant_system.utils.validators import validate_stock_data
errors = validate_stock_data(data)

# 检查策略配置
python scripts/config_manager.py validate
```

**Q: 内存使用过高？**
A: 调整数据处理批次大小：
```python
# 分批处理数据
batch_size = 100
for i in range(0, len(data), batch_size):
    batch = data[i:i+batch_size]
    process_batch(batch)
```

### 性能优化

**Q: 回测速度慢？**
A: 启用并行处理：
```yaml
# config/default.yaml
performance:
  max_workers: 4
  enable_multiprocessing: true
```

**Q: 数据加载慢？**
A: 启用缓存：
```yaml
data_processing:
  enable_cache: true
  cache_ttl: 3600
```

## 📞 获取帮助

- 📚 [API文档](api/README.md)
- 🐛 [问题反馈](https://github.com/your-username/quantitative-investment-system/issues)
- 💬 [讨论区](https://github.com/your-username/quantitative-investment-system/discussions)
- 📧 技术支持: support@quant-system.com

---

希望这份指南能帮助您快速上手量化投资系统。如有任何问题，请随时联系我们！
