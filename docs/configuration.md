# 配置指南

量化投资系统采用YAML格式的配置文件，支持多环境配置和灵活的参数管理。

## 📋 目录

1. [配置概述](#配置概述)
2. [配置文件结构](#配置文件结构)
3. [环境配置](#环境配置)
4. [策略配置](#策略配置)
5. [数据源配置](#数据源配置)
6. [配置管理工具](#配置管理工具)
7. [配置验证](#配置验证)
8. [最佳实践](#最佳实践)

## 🎯 配置概述

### 配置层次结构

```
config/
├── default.yaml              # 默认配置
├── data_sources.yaml         # 数据源配置
├── environments/             # 环境特定配置
│   ├── development.yaml      # 开发环境
│   ├── testing.yaml          # 测试环境
│   └── production.yaml       # 生产环境
└── strategies/               # 策略配置
    ├── momentum_strategy.yaml
    ├── mean_reversion.yaml
    └── custom_strategy.yaml
```

### 配置优先级

1. **环境变量** (最高优先级)
2. **环境特定配置** (environments/*.yaml)
3. **默认配置** (default.yaml)

### 配置加载

```python
from quant_system.utils.config_loader import ConfigLoader

# 初始化配置加载器
config_loader = ConfigLoader()

# 加载默认配置
default_config = config_loader.load_config('default')

# 加载环境配置
env_config = config_loader.get_environment_config('production')

# 加载策略配置
strategy_config = config_loader.load_strategy_config('momentum_strategy')
```

## 🏗️ 配置文件结构

### 默认配置 (default.yaml)

```yaml
# 系统基础配置
system:
  name: "量化投资系统"
  version: "0.1.0"
  environment: "development"
  debug: true
  timezone: "Asia/Shanghai"

# 日志配置
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
  file: "system.log"
  dir: "logs"
  max_file_size: 10485760  # 10MB
  backup_count: 5
  console: true

# 数据库配置
database:
  type: "sqlite"
  path: "data/quant_system.db"
  backup_enabled: true
  backup_interval: 86400  # 24小时
  connection_pool_size: 5

# 数据源配置
data_sources:
  eastmoney:
    enabled: true
    base_url: "http://82.push2.eastmoney.com/api/qt"
    timeout: 10
    retry_count: 3
    retry_delay: 1
    rate_limit: 100

  tushare:
    enabled: false
    token: ""  # 从环境变量获取
    timeout: 30
    retry_count: 3
    retry_delay: 2
    rate_limit: 200

# 回测配置
backtest:
  initial_capital: 1000000.0
  start_date: "2023-01-01"
  end_date: "2024-01-01"
  max_positions: 5
  position_size_pct: 0.20
  commission_rate: 0.0003
  stamp_tax_rate: 0.001
  slippage_rate: 0.001
  min_commission: 5.0
  stop_loss_pct: 0.05
  stop_profit_pct: 0.20
  max_drawdown: 0.10
  benchmark: "000300.SH"

# 策略配置
strategy:
  selection_criteria:
    consecutive_days: 3
    min_total_return: 0.15
    max_drawdown: 0.05
    exclude_limit_up_first_day: true
    min_stock_price: 5.0
    max_stock_price: 200.0
    min_market_cap: 1000000000
    max_market_cap: 500000000000
    min_avg_volume: 10000000
    min_turnover_rate: 0.01
    max_turnover_rate: 0.20

# 风险管理配置
risk_management:
  max_single_position: 0.20
  max_sector_exposure: 0.40
  cash_reserve_ratio: 0.05
  max_portfolio_volatility: 0.20
  max_correlation: 0.70
  var_confidence: 0.95
  enable_stop_loss: true
  stop_loss_method: "percentage"
  trailing_stop: false
  stop_loss_buffer: 0.02

# 数据处理配置
data_processing:
  remove_outliers: true
  outlier_method: "iqr"
  outlier_threshold: 3.0
  validate_prices: true
  validate_volumes: true
  validate_ratios: true
  enable_cache: true
  cache_ttl: 3600
  cache_size: 1000

# 性能配置
performance:
  max_workers: 4
  enable_multiprocessing: false
  max_memory_usage: 2147483648  # 2GB
  gc_threshold: 1000
  use_numba: false
  use_cython: false

# 通知配置
notifications:
  email:
    enabled: false
    smtp_server: ""
    smtp_port: 587
    username: ""
    password: ""
    recipients: []

  wechat:
    enabled: false
    webhook_url: ""

  dingtalk:
    enabled: false
    webhook_url: ""
    secret: ""

# 监控配置
monitoring:
  enable_system_monitor: true
  monitor_interval: 60
  enable_performance_monitor: true
  performance_log_interval: 300
  health_check_interval: 30
  health_check_timeout: 5

# 安全配置
security:
  enable_api_key: false
  api_key_header: "X-API-Key"
  encrypt_sensitive_data: false
  encryption_key: ""
  enable_ip_whitelist: false
  ip_whitelist: []
```

## 🌍 环境配置

### 开发环境 (development.yaml)

```yaml
system:
  environment: "development"
  debug: true

logging:
  level: "DEBUG"
  console: true

database:
  path: "data/dev_quant_system.db"
  backup_enabled: false

data_sources:
  eastmoney:
    rate_limit: 50  # 开发环境降低请求频率

  tushare:
    enabled: true
    rate_limit: 100

backtest:
  initial_capital: 100000.0  # 10万用于开发测试
  start_date: "2024-01-01"
  end_date: "2024-06-01"
  max_positions: 3

strategy:
  selection_criteria:
    consecutive_days: 2
    min_total_return: 0.10
    min_stock_price: 3.0

performance:
  max_workers: 2
  enable_multiprocessing: false

notifications:
  email:
    enabled: false
  wechat:
    enabled: false
  dingtalk:
    enabled: false

development:
  enable_debug_mode: true
  debug_sql: true
  debug_api_calls: true
  enable_profiler: true
  enable_memory_profiler: true
```

### 测试环境 (testing.yaml)

```yaml
system:
  environment: "testing"
  debug: false

logging:
  level: "WARNING"
  console: false
  file: "testing.log"

database:
  path: ":memory:"  # 内存数据库
  backup_enabled: false

data_sources:
  eastmoney:
    enabled: false  # 测试环境不使用真实API
  tushare:
    enabled: false
  mock:
    enabled: true
    data_path: "tests/fixtures/mock_data.json"

backtest:
  initial_capital: 50000.0
  start_date: "2024-01-01"
  end_date: "2024-03-01"
  max_positions: 2

performance:
  max_workers: 1
  enable_multiprocessing: false

testing:
  use_mock_data: true
  mock_data_path: "tests/fixtures"
  test_data_size: "small"
  fail_fast: true
  verbose_output: false
  enable_coverage: true
  coverage_threshold: 0.85
  parallel_tests: false
  test_timeout: 30
  cleanup_after_tests: true
```

### 生产环境 (production.yaml)

```yaml
system:
  environment: "production"
  debug: false

logging:
  level: "INFO"
  console: false
  file: "production.log"
  dir: "/var/log/quant_system"
  max_file_size: 52428800  # 50MB
  backup_count: 10

database:
  path: "/data/quant_system/production.db"
  backup_enabled: true
  backup_interval: 21600  # 6小时
  connection_pool_size: 10

data_sources:
  eastmoney:
    timeout: 15
    retry_count: 5
    retry_delay: 2
    rate_limit: 80

  tushare:
    enabled: true
    timeout: 30
    retry_count: 3
    retry_delay: 3
    rate_limit: 150

backtest:
  initial_capital: 1000000.0
  max_positions: 10

strategy:
  selection_criteria:
    consecutive_days: 5
    min_total_return: 0.20
    max_drawdown: 0.03
    min_stock_price: 8.0
    max_stock_price: 150.0
    min_market_cap: 5000000000
    min_avg_volume: 50000000

risk_management:
  max_single_position: 0.15
  max_sector_exposure: 0.30
  cash_reserve_ratio: 0.10
  enable_stop_loss: true
  stop_loss_method: "atr"
  trailing_stop: true

performance:
  max_workers: 8
  enable_multiprocessing: true
  max_memory_usage: 4294967296  # 4GB
  use_numba: true

notifications:
  email:
    enabled: true
    recipients: ["admin@example.com", "trader@example.com"]

  dingtalk:
    enabled: true

monitoring:
  enable_system_monitor: true
  enable_performance_monitor: true
  health_check_interval: 30

security:
  enable_api_key: true
  encrypt_sensitive_data: true
  enable_ip_whitelist: true
  ip_whitelist: ["192.168.1.0/24", "10.0.0.0/8"]

production:
  deployment_mode: "standalone"
  service_port: 8000
  worker_processes: 4
  enable_data_backup: true
  backup_schedule: "0 2 * * *"
  backup_retention_days: 30
  enable_alerts: true
  alert_thresholds:
    cpu_usage: 0.80
    memory_usage: 0.85
    disk_usage: 0.90
    error_rate: 0.05

## 🎯 策略配置

### 策略配置文件结构

```yaml
# config/strategies/momentum_strategy.yaml
strategy_info:
  name: "动量策略"
  version: "1.0.0"
  description: "基于股价连续上涨的动量选股策略"
  author: "量化投资系统"
  created_date: "2024-01-01"
  strategy_type: "momentum"

selection_criteria:
  basic_criteria:
    consecutive_days: 3
    min_total_return: 0.15
    max_drawdown: 0.05
    exclude_limit_up_first_day: true

  price_filters:
    min_stock_price: 5.0
    max_stock_price: 200.0
    min_market_cap: 1000000000
    max_market_cap: 500000000000

  volume_filters:
    min_avg_volume: 10000000
    min_turnover_rate: 0.01
    max_turnover_rate: 0.20
    volume_ratio_threshold: 1.5

  technical_filters:
    enable_technical: true
    rsi:
      enabled: true
      period: 14
      min_value: 30
      max_value: 70
    macd:
      enabled: true
      fast_period: 12
      slow_period: 26
      signal_period: 9
      require_golden_cross: true
    moving_averages:
      enabled: true
      require_ma_bullish: true
      ma_periods: [5, 10, 20, 60]
      price_above_ma: [5, 10]

  fundamental_filters:
    enable_fundamental: true
    profitability:
      min_roe: 0.10
      min_roa: 0.05
      min_gross_margin: 0.20
      min_net_margin: 0.05
    growth:
      min_revenue_growth: 0.05
      min_profit_growth: 0.10
      max_revenue_growth: 1.0
    valuation:
      max_pe_ratio: 30
      max_pb_ratio: 5
      max_ps_ratio: 10
      min_pe_ratio: 5
    financial_health:
      max_debt_ratio: 0.60
      min_current_ratio: 1.0
      min_quick_ratio: 0.5

  sector_filters:
    excluded_industries:
      - "房地产"
      - "钢铁"
      - "煤炭"
    included_sectors:
      - "科技"
      - "医药"
      - "消费"
    new_stock_filter:
      exclude_new_stocks: true
      new_stock_days_limit: 60

trading_rules:
  buy_rules:
    - name: "动量确认"
      description: "确认股票符合动量条件"
      condition: "consecutive_days >= 3 and total_return >= 0.15"
      priority: 1
      enabled: true

    - name: "技术指标确认"
      description: "技术指标支持买入"
      condition: "rsi > 30 and macd_signal == 'golden_cross'"
      priority: 2
      enabled: true

  sell_rules:
    - name: "止盈"
      description: "达到止盈目标"
      condition: "profit_pct >= 0.20"
      priority: 1
      enabled: true

    - name: "止损"
      description: "达到止损线"
      condition: "loss_pct >= 0.05"
      priority: 1
      enabled: true

  risk_rules:
    - name: "单只股票仓位限制"
      description: "单只股票仓位不超过20%"
      condition: "position_pct <= 0.20"
      priority: 1
      enabled: true

position_management:
  allocation_method: "equal_weight"
  base_position_size: 0.20
  max_position_size: 0.25
  min_position_size: 0.05
  dynamic_sizing:
    enabled: true
    momentum_factor: 0.5
    volatility_factor: 0.3
    volume_factor: 0.2
  rebalancing:
    frequency: "weekly"
    threshold: 0.05
    max_turnover: 0.30

risk_management:
  stop_loss:
    method: "percentage"
    percentage: 0.05
    trailing_stop: true
    trailing_percentage: 0.03
  take_profit:
    method: "percentage"
    percentage: 0.20
    partial_profit: true
    profit_levels: [0.10, 0.15, 0.20]
  portfolio_risk:
    max_drawdown: 0.10
    var_limit: 0.05
    correlation_limit: 0.70
  market_risk:
    market_filter: true
    market_trend_period: 20
    bear_market_threshold: -0.15
    reduce_position_in_bear: true

backtest_params:
  start_date: "2023-01-01"
  end_date: "2024-01-01"
  initial_capital: 1000000
  max_positions: 10
  commission_rate: 0.0003
  stamp_tax_rate: 0.001
  slippage_rate: 0.001
  benchmark: "000300.SH"
  rebalance_frequency: "weekly"

optimization:
  objective: "sharpe_ratio"
  parameter_ranges:
    consecutive_days: [2, 3, 4, 5]
    min_total_return: [0.10, 0.15, 0.20, 0.25]
    stop_loss_pct: [0.03, 0.05, 0.08, 0.10]
    take_profit_pct: [0.15, 0.20, 0.25, 0.30]
  method: "grid_search"
  validation:
    method: "walk_forward"
    train_ratio: 0.70
    test_ratio: 0.30

monitoring:
  realtime_metrics:
    - "total_return"
    - "sharpe_ratio"
    - "max_drawdown"
    - "win_rate"
    - "current_positions"
  reporting:
    daily_report: true
    weekly_report: true
    monthly_report: true
  alerts:
    max_drawdown_alert: 0.08
    position_limit_alert: true
    strategy_failure_alert: true
```

## 📊 数据源配置

### 数据源配置文件 (data_sources.yaml)

```yaml
# 数据源优先级配置
priority:
  realtime_data: ["eastmoney", "tushare", "yfinance"]
  historical_data: ["tushare", "eastmoney", "yfinance"]
  fundamental_data: ["tushare", "eastmoney"]
  technical_indicators: ["local_calculation", "tushare"]

# 东方财富API配置
eastmoney:
  name: "东方财富"
  type: "free"
  description: "免费的A股实时行情数据源"
  base_url: "http://82.push2.eastmoney.com/api/qt"
  timeout: 10
  retry_count: 3
  retry_delay: 1
  rate_limit:
    requests_per_minute: 100
    requests_per_hour: 5000
    requests_per_day: 50000
  supported_data:
    realtime_quotes: true
    historical_klines: true
    stock_info: true
    market_status: true
    sector_data: false
    financial_data: false
  endpoints:
    realtime_list: "/clist/get"
    stock_detail: "/stock/get"
    historical_kline: "/stock/kline/get"
    market_overview: "/ulist.np/get"
  default_params:
    ut: "bd1d9ddb04089700cf9c27f6f7426281"
    fltt: "2"
    invt: "2"
  field_mapping:
    code: "f12"
    name: "f14"
    price: "f2"
    change: "f4"
    pct_change: "f3"
    volume: "f5"
    amount: "f6"

# Tushare API配置
tushare:
  name: "Tushare"
  type: "premium"
  description: "专业的金融数据服务平台"
  base_url: "http://api.tushare.pro"
  token_required: true
  timeout: 30
  retry_count: 3
  retry_delay: 2
  rate_limit:
    requests_per_minute: 200
    requests_per_hour: 10000
    daily_points_limit: 10000
  supported_data:
    realtime_quotes: true
    historical_klines: true
    stock_info: true
    financial_data: true
    sector_data: true
    index_data: true
  interfaces:
    stock_basic: "stock_basic"
    daily: "daily"
    daily_basic: "daily_basic"
    income: "income"
    balancesheet: "balancesheet"
    cashflow: "cashflow"
  data_quality:
    enable_validation: true
    max_missing_ratio: 0.05
    outlier_detection: true
    consistency_check: true

# 故障转移配置
failover:
  enable_auto_failover: true
  health_check_interval: 60
  failure_threshold: 3
  recovery_threshold: 2
  strategies:
    realtime_data:
      primary: "eastmoney"
      fallback: ["tushare", "local"]
      timeout: 5
    historical_data:
      primary: "tushare"
      fallback: ["eastmoney", "local"]
      timeout: 30

# 数据质量控制
quality_control:
  validation_rules:
    price_range: [0.01, 10000]
    volume_range: [0, 1000000000000]
    pct_change_range: [-0.20, 0.20]
  anomaly_handling:
    method: "interpolation"
    max_consecutive_missing: 5
    outlier_threshold: 3.0
  integrity_checks:
    enable_duplicate_check: true
    enable_sequence_check: true
    enable_consistency_check: true

# 缓存配置
cache:
  strategy: "lru"
  max_size: 10000
  ttl: 3600
  levels:
    l1_memory:
      enabled: true
      size: 1000
      ttl: 300
    l2_redis:
      enabled: false
      host: "localhost"
      port: 6379
      db: 0
      ttl: 3600
    l3_disk:
      enabled: true
      path: "cache/data"
      size: "1GB"
      ttl: 86400

# 监控和告警
monitoring:
  health_monitoring:
    enabled: true
    check_interval: 60
    timeout: 10
  quality_monitoring:
    enabled: true
    check_interval: 300
    alert_threshold: 0.95
  performance_monitoring:
    enabled: true
    response_time_threshold: 5.0
    error_rate_threshold: 0.05
  alerts:
    data_source_down: true
    data_quality_degraded: true
    rate_limit_exceeded: true
    cache_miss_rate_high: true
```

## 🛠️ 配置管理工具

### 命令行工具

系统提供了便捷的配置管理工具：

```bash
# 列出所有可用配置
python scripts/config_manager.py list

# 验证所有配置文件
python scripts/config_manager.py validate

# 显示特定配置内容
python scripts/config_manager.py show momentum_strategy

# 创建新的策略配置
python scripts/config_manager.py create-strategy

# 测试配置加载功能
python scripts/config_manager.py test
```

### 编程接口

```python
from quant_system.utils.config_loader import ConfigLoader
from quant_system.utils.config_validator import ConfigValidator

# 初始化配置加载器
config_loader = ConfigLoader()

# 加载不同类型的配置
system_config = config_loader.load_config('default')
env_config = config_loader.get_environment_config('production')
strategy_config = config_loader.load_strategy_config('momentum_strategy')
data_sources_config = config_loader.load_data_sources_config()

# 列出可用配置
strategies = config_loader.list_available_strategies()
environments = config_loader.list_available_environments()

# 配置验证
validator = ConfigValidator()
is_valid = validator.validate_system_config(system_config)
if not is_valid:
    print("配置错误:", validator.errors)
    print("配置警告:", validator.warnings)
```

## ✅ 配置验证

### 验证规则

系统提供了完整的配置验证功能：

1. **必需字段检查**: 确保所有必需的配置项都存在
2. **数据类型验证**: 验证配置值的数据类型
3. **取值范围检查**: 验证数值是否在合理范围内
4. **逻辑一致性**: 检查配置项之间的逻辑关系
5. **格式验证**: 验证日期、URL等格式

### 验证示例

```python
from quant_system.utils.config_validator import validate_config_file

# 验证系统配置
result = validate_config_file('config/default.yaml', 'system')

# 验证策略配置
result = validate_config_file('config/strategies/momentum_strategy.yaml', 'strategy')

# 验证数据源配置
result = validate_config_file('config/data_sources.yaml', 'data_sources')
```

### 常见验证错误

1. **缺少必需字段**
   ```
   错误: 系统配置缺少必需字段: version
   解决: 在system节中添加version字段
   ```

2. **无效的数据类型**
   ```
   错误: 初始资金必须是正数
   解决: 确保initial_capital为正数
   ```

3. **取值范围错误**
   ```
   错误: 仓位比例必须在0-1之间
   解决: 调整position_size_pct到合理范围
   ```

## 💡 最佳实践

### 1. 环境分离

- 为不同环境创建独立的配置文件
- 使用环境变量控制敏感信息
- 生产环境配置应该更加严格和安全

### 2. 配置版本控制

```bash
# 配置文件应该纳入版本控制
git add config/
git commit -m "update configuration"

# 敏感信息使用环境变量
export TUSHARE_TOKEN=your_token_here
export DATABASE_PASSWORD=your_password
```

### 3. 配置文档化

- 为每个配置项添加注释
- 说明配置项的作用和取值范围
- 提供配置示例

### 4. 配置验证

```bash
# 部署前验证配置
python scripts/config_manager.py validate

# 定期检查配置一致性
python scripts/config_manager.py test
```

### 5. 配置备份

```bash
# 备份重要配置
cp -r config/ config_backup_$(date +%Y%m%d)/

# 使用版本控制跟踪配置变更
git log --oneline config/
```

### 6. 安全考虑

- 敏感信息不要直接写在配置文件中
- 使用环境变量或密钥管理系统
- 限制配置文件的访问权限

```bash
# 设置配置文件权限
chmod 600 config/environments/production.yaml

# 使用环境变量
export TUSHARE_TOKEN=your_token
export EMAIL_PASSWORD=your_password
```

### 7. 配置监控

```python
# 监控配置变更
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.yaml'):
            print(f"配置文件已修改: {event.src_path}")
            # 重新加载配置
            reload_config()

observer = Observer()
observer.schedule(ConfigChangeHandler(), 'config/', recursive=True)
observer.start()
```

## 🔧 故障排除

### 常见问题

1. **配置文件找不到**
   ```
   错误: 配置文件不存在: momentum_strategy
   解决: 检查文件路径和文件名是否正确
   ```

2. **YAML格式错误**
   ```
   错误: YAML解析失败
   解决: 检查YAML语法，注意缩进和引号
   ```

3. **环境变量未设置**
   ```
   错误: 环境变量TUSHARE_TOKEN未设置
   解决: export TUSHARE_TOKEN=your_token
   ```

### 调试技巧

```python
# 启用配置调试
import logging
logging.getLogger('quant_system.config').setLevel(logging.DEBUG)

# 检查配置加载过程
config_loader = ConfigLoader()
config_loader.debug = True
config = config_loader.load_config('default')
```

---

通过合理的配置管理，您可以轻松地在不同环境间切换，调整策略参数，并确保系统的稳定运行。
```