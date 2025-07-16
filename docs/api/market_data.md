# 行情数据模块 API 文档

## 📊 模块概述

行情数据模块负责从多个数据源获取股票行情数据，包括实时数据和历史数据的获取、处理和存储。

## 🏗️ 模块架构

```
market_data/
├── fetchers/           # 数据获取器
│   ├── eastmoney_api.py       # 东方财富API
│   ├── tushare_api.py         # Tushare API
│   ├── yahoo_finance_api.py   # Yahoo Finance API
│   └── multi_source_fetcher.py # 多数据源获取器
├── processors/         # 数据处理器
│   ├── data_processor.py      # 数据处理器
│   └── technical_indicators.py # 技术指标计算
└── storage/           # 数据存储
    ├── database.py           # 数据库存储
    └── cache.py             # 缓存存储
```

## 📡 数据获取器 (Fetchers)

### EastmoneyAPI

东方财富数据源API，提供A股实时和历史数据。

#### 类定义

```python
class EastmoneyAPI:
    """东方财富数据API"""
    
    def __init__(self, timeout: int = 30):
        """初始化API客户端"""
        
    def get_a_stock_realtime(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取A股实时行情"""
        
    def get_stock_detail(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票详细信息"""
        
    def get_historical_data(self, stock_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取历史数据"""
```

#### 方法详解

##### get_a_stock_realtime()

获取A股实时行情数据。

**参数:**
- `limit` (int): 返回股票数量限制，默认100

**返回:**
- `List[Dict[str, Any]]`: 股票实时数据列表

**示例:**
```python
from market_data.fetchers.eastmoney_api import EastmoneyAPI

api = EastmoneyAPI()
stocks = api.get_a_stock_realtime(limit=10)

for stock in stocks:
    print(f"{stock['name']}: {stock['price']}")
```

##### get_stock_detail()

获取指定股票的详细信息。

**参数:**
- `stock_code` (str): 股票代码，如'000001'

**返回:**
- `Optional[Dict[str, Any]]`: 股票详细信息，失败时返回None

**示例:**
```python
detail = api.get_stock_detail('000001')
if detail:
    print(f"股票名称: {detail['name']}")
    print(f"当前价格: {detail['price']}")
    print(f"涨跌幅: {detail['change_pct']:.2%}")
```

### TushareAPI

Tushare数据源API，提供高质量的A股和港股数据。

#### 类定义

```python
class TushareAPI:
    """Tushare数据API"""
    
    def __init__(self, token: str):
        """初始化API客户端"""
        
    def get_stock_basic(self) -> pd.DataFrame:
        """获取股票基本信息"""
        
    def get_daily_data(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取日线数据"""
        
    def get_realtime_quote(self, ts_codes: List[str]) -> pd.DataFrame:
        """获取实时行情"""
```

### MultiSourceFetcher

多数据源获取器，支持故障转移和数据源切换。

#### 类定义

```python
class MultiSourceFetcher:
    """多数据源获取器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化多数据源获取器"""
        
    def get_realtime_data(self, stock_codes: List[str]) -> List[Dict[str, Any]]:
        """获取实时数据（支持故障转移）"""
        
    def get_historical_data_with_fallback(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """获取历史数据（支持故障转移）"""
```

## 🔄 数据处理器 (Processors)

### MarketDataProcessor

市场数据处理器，负责数据清洗、转换和技术指标计算。

#### 类定义

```python
class MarketDataProcessor:
    """市场数据处理器"""
    
    def __init__(self):
        """初始化处理器"""
        
    def clean_data(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """清洗原始数据"""
        
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        
    def normalize_data(self, data: List[Dict[str, Any]]) -> List[StockData]:
        """标准化数据格式"""
```

#### 方法详解

##### clean_data()

清洗原始数据，去除异常值和缺失值。

**参数:**
- `raw_data` (List[Dict[str, Any]]): 原始数据列表

**返回:**
- `List[Dict[str, Any]]`: 清洗后的数据列表

##### calculate_technical_indicators()

计算技术指标，包括MA、MACD、RSI等。

**参数:**
- `data` (pd.DataFrame): 股票价格数据

**返回:**
- `pd.DataFrame`: 包含技术指标的数据

**支持的技术指标:**
- MA (移动平均线): 5日、10日、20日、60日
- MACD (指数平滑移动平均线)
- RSI (相对强弱指标)
- 布林带 (Bollinger Bands)
- KDJ指标

**示例:**
```python
from market_data.processors.data_processor import MarketDataProcessor

processor = MarketDataProcessor()
data_with_indicators = processor.calculate_technical_indicators(price_data)

print(data_with_indicators[['close', 'ma_5', 'ma_20', 'rsi', 'macd']].head())
```

## 💾 数据存储 (Storage)

### DatabaseStorage

数据库存储模块，支持SQLite和其他数据库。

#### 类定义

```python
class DatabaseStorage:
    """数据库存储"""
    
    def __init__(self, db_path: str):
        """初始化数据库连接"""
        
    def save_stock_data(self, data: List[StockData]) -> bool:
        """保存股票数据"""
        
    def load_stock_data(self, stock_code: str, start_date: date, end_date: date) -> List[StockData]:
        """加载股票数据"""
        
    def update_stock_data(self, stock_code: str, data: List[StockData]) -> bool:
        """更新股票数据"""
```

## 🔧 工具函数

### 数据验证

```python
def validate_stock_code(code: str, market: str = "A") -> bool:
    """验证股票代码格式"""
    
def validate_price_data(price: float) -> bool:
    """验证价格数据"""
    
def validate_volume_data(volume: int) -> bool:
    """验证成交量数据"""
```

### 数据转换

```python
def convert_to_stock_data(raw_data: Dict[str, Any]) -> StockData:
    """转换为标准股票数据格式"""
    
def merge_data_sources(data1: List[Dict], data2: List[Dict]) -> List[Dict]:
    """合并多个数据源的数据"""
```

## 🚨 异常处理

### 异常类型

```python
class DataSourceError(Exception):
    """数据源错误"""
    
class DataValidationError(Exception):
    """数据验证错误"""
    
class NetworkError(Exception):
    """网络连接错误"""
```

### 错误处理示例

```python
try:
    data = api.get_stock_detail('000001')
except DataSourceError as e:
    logger.error(f"数据源错误: {e}")
except NetworkError as e:
    logger.error(f"网络错误: {e}")
```

## 📝 使用示例

### 完整示例

```python
from market_data import get_eastmoney_api
from market_data.processors import MarketDataProcessor
from market_data.storage import DatabaseStorage

# 1. 获取数据
api = get_eastmoney_api()
raw_data = api.get_a_stock_realtime(limit=50)

# 2. 处理数据
processor = MarketDataProcessor()
clean_data = processor.clean_data(raw_data)
stock_data = processor.normalize_data(clean_data)

# 3. 存储数据
storage = DatabaseStorage('data/stock_data.db')
storage.save_stock_data(stock_data)

print(f"成功处理并存储了 {len(stock_data)} 条股票数据")
```

## 🔗 相关文档

- [配置指南](../configuration.md) - 数据源配置
- [用户指南](../user_guide.md) - 基础使用方法
- [开发指南](../developer_guide.md) - 扩展开发
