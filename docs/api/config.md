# 配置系统 API 文档

## ⚙️ 模块概述

配置系统提供灵活的配置管理功能，支持多环境配置、配置验证、热更新等特性。

## 🏗️ 模块架构

```
quant_system/utils/
├── config_loader.py           # 配置加载器
├── config_validator.py        # 配置验证器
└── config_manager.py          # 配置管理器
```

## 📁 配置文件结构

```
config/
├── default.yaml               # 默认配置
├── data_sources.yaml          # 数据源配置
├── environments/              # 环境配置
│   ├── development.yaml       # 开发环境
│   ├── testing.yaml          # 测试环境
│   └── production.yaml       # 生产环境
└── strategies/               # 策略配置
    ├── momentum_strategy.yaml
    └── ml_enhanced_strategy.yaml
```

## 🔧 配置加载器 (ConfigLoader)

### 类定义

```python
class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_dir: str = "config"):
        """初始化配置加载器"""
        
    def load_config(self, config_name: str = "default") -> Dict[str, Any]:
        """加载系统配置"""
        
    def load_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """加载策略配置"""
        
    def load_environment_config(self, env: str) -> Dict[str, Any]:
        """加载环境配置"""
        
    def reload_config(self, config_name: str) -> Dict[str, Any]:
        """重新加载配置"""
```

### 方法详解

#### load_config()

加载系统主配置文件。

**参数:**
- `config_name` (str): 配置文件名，默认"default"

**返回:**
- `Dict[str, Any]`: 配置字典

**示例:**
```python
from quant_system.utils.config_loader import ConfigLoader

loader = ConfigLoader()

# 加载默认配置
config = loader.load_config()
print(f"系统版本: {config['system']['version']}")

# 加载特定配置
dev_config = loader.load_config("development")
print(f"日志级别: {dev_config['logging']['level']}")
```

#### load_strategy_config()

加载策略配置文件。

**参数:**
- `strategy_name` (str): 策略名称

**返回:**
- `Dict[str, Any]`: 策略配置字典

**示例:**
```python
# 加载动量策略配置
momentum_config = loader.load_strategy_config("momentum_strategy")
print(f"连续天数: {momentum_config['basic_criteria']['consecutive_days']}")

# 加载ML策略配置
ml_config = loader.load_strategy_config("ml_enhanced_strategy")
print(f"模型类型: {ml_config['model_config']['model_type']}")
```

### 配置缓存

```python
class ConfigCache:
    """配置缓存"""
    
    def __init__(self, ttl: int = 3600):
        """初始化缓存，TTL为秒"""
        
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """获取缓存的配置"""
        
    def set(self, key: str, config: Dict[str, Any]):
        """设置配置缓存"""
        
    def invalidate(self, key: str):
        """使缓存失效"""
```

## ✅ 配置验证器 (ConfigValidator)

### 类定义

```python
class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        """初始化验证器"""
        
    def validate_system_config(self, config: Dict[str, Any]) -> bool:
        """验证系统配置"""
        
    def validate_strategy_config(self, config: Dict[str, Any]) -> bool:
        """验证策略配置"""
        
    def validate_data_source_config(self, config: Dict[str, Any]) -> bool:
        """验证数据源配置"""
        
    def get_validation_errors(self) -> List[str]:
        """获取验证错误列表"""
```

### 验证规则

#### 系统配置验证

```python
def validate_system_config(self, config: Dict[str, Any]) -> bool:
    """验证系统配置"""
    errors = []
    
    # 必需字段检查
    required_fields = ['system', 'logging', 'database']
    for field in required_fields:
        if field not in config:
            errors.append(f"缺少必需字段: {field}")
    
    # 系统版本检查
    if 'system' in config:
        if 'version' not in config['system']:
            errors.append("系统配置缺少版本信息")
    
    # 日志级别检查
    if 'logging' in config:
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        level = config['logging'].get('level', '').upper()
        if level not in valid_levels:
            errors.append(f"无效的日志级别: {level}")
    
    self.errors = errors
    return len(errors) == 0
```

#### 策略配置验证

```python
def validate_strategy_config(self, config: Dict[str, Any]) -> bool:
    """验证策略配置"""
    errors = []
    
    # 策略信息验证
    if 'strategy_info' not in config:
        errors.append("缺少策略信息")
    else:
        strategy_info = config['strategy_info']
        required_info = ['name', 'version', 'strategy_type']
        for field in required_info:
            if field not in strategy_info:
                errors.append(f"策略信息缺少字段: {field}")
    
    # 基础条件验证
    if 'basic_criteria' in config:
        criteria = config['basic_criteria']
        
        # 连续天数验证
        consecutive_days = criteria.get('consecutive_days', 0)
        if not isinstance(consecutive_days, int) or consecutive_days < 1:
            errors.append("连续天数必须是正整数")
        
        # 收益率验证
        min_return = criteria.get('min_total_return', 0)
        if not isinstance(min_return, (int, float)) or min_return < 0:
            errors.append("最小收益率必须是非负数")
    
    self.errors = errors
    return len(errors) == 0
```

### 使用示例

```python
from quant_system.utils.config_validator import ConfigValidator

validator = ConfigValidator()

# 验证系统配置
if validator.validate_system_config(system_config):
    print("✅ 系统配置验证通过")
else:
    print("❌ 系统配置验证失败:")
    for error in validator.get_validation_errors():
        print(f"  - {error}")

# 验证策略配置
if validator.validate_strategy_config(strategy_config):
    print("✅ 策略配置验证通过")
else:
    print("❌ 策略配置验证失败:")
    for error in validator.get_validation_errors():
        print(f"  - {error}")
```

## 🔄 配置管理器 (ConfigManager)

### 类定义

```python
class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """初始化配置管理器"""
        
    def get_config(self, config_type: str, name: str) -> Dict[str, Any]:
        """获取配置"""
        
    def update_config(self, config_type: str, name: str, updates: Dict[str, Any]):
        """更新配置"""
        
    def create_config(self, config_type: str, name: str, config: Dict[str, Any]):
        """创建新配置"""
        
    def list_configs(self, config_type: str) -> List[str]:
        """列出配置文件"""
```

### 配置热更新

```python
class ConfigWatcher:
    """配置文件监控器"""
    
    def __init__(self, config_dir: str, callback: Callable):
        """初始化监控器"""
        
    def start_watching(self):
        """开始监控配置文件变化"""
        
    def stop_watching(self):
        """停止监控"""
        
    def on_config_changed(self, file_path: str):
        """配置文件变化回调"""
```

### 使用示例

```python
from quant_system.utils.config_manager import ConfigManager, ConfigWatcher

# 创建配置管理器
manager = ConfigManager()

# 获取配置
strategy_config = manager.get_config("strategy", "momentum_strategy")

# 更新配置
updates = {
    "basic_criteria": {
        "consecutive_days": 5,
        "min_total_return": 0.20
    }
}
manager.update_config("strategy", "momentum_strategy", updates)

# 配置热更新
def on_config_update(file_path: str):
    print(f"配置文件已更新: {file_path}")
    # 重新加载配置
    manager.reload_config(file_path)

watcher = ConfigWatcher("config", on_config_update)
watcher.start_watching()
```

## 📋 配置模板

### 系统配置模板

```yaml
# config/default.yaml
system:
  name: "量化投资系统"
  version: "2.0.0"
  environment: "development"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/system.log"
  max_size: "10MB"
  backup_count: 5

database:
  type: "sqlite"
  path: "data/stock_data.db"
  pool_size: 10
  timeout: 30

cache:
  enabled: true
  type: "memory"
  max_size: 1000
  ttl: 3600

performance:
  monitoring_enabled: true
  metrics_interval: 60
  alert_threshold: 0.8
```

### 策略配置模板

```yaml
# config/strategies/momentum_strategy.yaml
strategy_info:
  name: "动量策略"
  version: "1.0.0"
  description: "基于价格动量的选股策略"
  strategy_type: "momentum"

basic_criteria:
  consecutive_days: 3
  min_total_return: 0.15
  max_drawdown: 0.05
  exclude_limit_up_first_day: true

price_filters:
  min_stock_price: 5.0
  max_stock_price: 200.0
  min_market_cap: 10.0
  max_market_cap: 5000.0

risk_management:
  max_positions: 5
  position_size_pct: 0.20
  stop_loss_pct: 0.08
  take_profit_pct: 0.25
```

### 数据源配置模板

```yaml
# config/data_sources.yaml
data_sources:
  eastmoney:
    enabled: true
    priority: 1
    timeout: 30
    retry_count: 3
    
  tushare:
    enabled: false
    priority: 2
    token: "${TUSHARE_TOKEN}"
    timeout: 30
    
  yahoo_finance:
    enabled: true
    priority: 3
    timeout: 30

default_source: "eastmoney"
fallback_enabled: true
cache_enabled: true
cache_ttl: 300
```

## 🔧 配置工具

### 命令行工具

```bash
# 验证配置
python scripts/config_manager.py validate

# 列出配置
python scripts/config_manager.py list

# 显示配置
python scripts/config_manager.py show default

# 创建策略配置
python scripts/config_manager.py create-strategy my_strategy
```

### 配置工具函数

```python
def merge_configs(base_config: Dict, override_config: Dict) -> Dict:
    """合并配置"""
    
def flatten_config(config: Dict, separator: str = ".") -> Dict:
    """扁平化配置"""
    
def expand_config(flat_config: Dict, separator: str = ".") -> Dict:
    """展开扁平化配置"""
    
def substitute_env_vars(config: Dict) -> Dict:
    """替换环境变量"""
```

## 🚨 异常处理

### 配置异常

```python
class ConfigError(Exception):
    """配置错误基类"""
    
class ConfigNotFoundError(ConfigError):
    """配置文件未找到"""
    
class ConfigValidationError(ConfigError):
    """配置验证错误"""
    
class ConfigFormatError(ConfigError):
    """配置格式错误"""
```

### 错误处理示例

```python
try:
    config = loader.load_config("nonexistent")
except ConfigNotFoundError as e:
    logger.error(f"配置文件未找到: {e}")
except ConfigFormatError as e:
    logger.error(f"配置格式错误: {e}")
except ConfigValidationError as e:
    logger.error(f"配置验证失败: {e}")
```

## 🔗 相关文档

- [配置指南](../configuration.md) - 详细配置说明
- [用户指南](../user_guide.md) - 配置使用指南
- [开发指南](../developer_guide.md) - 配置开发指南
