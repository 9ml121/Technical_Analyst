# 股票数据模型 API 文档

## 📊 模块概述

股票数据模型定义了系统中股票相关数据的标准结构，确保数据的一致性和类型安全。

## 🏗️ 数据模型架构

```
quant_system/models/
├── stock_data.py          # 股票数据模型
├── strategy_models.py     # 策略相关模型
└── backtest_models.py     # 回测相关模型
```

## 📈 股票数据模型 (StockData)

### 基础数据类

```python
@dataclass
class StockData:
    """股票数据模型"""
    
    code: str                    # 股票代码
    name: str                    # 股票名称
    date: date                   # 交易日期
    open_price: float           # 开盘价
    close_price: float          # 收盘价
    high_price: float           # 最高价
    low_price: float            # 最低价
    volume: int                 # 成交量
    amount: float               # 成交额
    pre_close: Optional[float] = None    # 前收盘价
    change: Optional[float] = None       # 涨跌额
    change_pct: Optional[float] = None   # 涨跌幅
    turnover_rate: Optional[float] = None # 换手率
    pe_ratio: Optional[float] = None     # 市盈率
    pb_ratio: Optional[float] = None     # 市净率
    market_cap: Optional[float] = None   # 市值
    
    def __post_init__(self):
        """数据初始化后处理"""
        self._calculate_derived_fields()
        self._validate_data()
    
    def _calculate_derived_fields(self):
        """计算衍生字段"""
        if self.pre_close and self.pre_close > 0:
            self.change = self.close_price - self.pre_close
            self.change_pct = self.change / self.pre_close
    
    def _validate_data(self):
        """验证数据有效性"""
        if self.open_price <= 0 or self.close_price <= 0:
            raise ValueError("价格必须大于0")
        if self.volume < 0:
            raise ValueError("成交量不能为负数")
```

### 使用示例

```python
from quant_system.models.stock_data import StockData
from datetime import date

# 创建股票数据
stock = StockData(
    code="000001",
    name="平安银行",
    date=date(2024, 1, 15),
    open_price=12.50,
    close_price=12.80,
    high_price=13.00,
    low_price=12.30,
    volume=1000000,
    amount=12800000,
    pre_close=12.50
)

print(f"股票代码: {stock.code}")
print(f"涨跌幅: {stock.change_pct:.2%}")
print(f"成交额: {stock.amount:,.0f}")
```

## 🔍 数据验证器 (StockDataValidator)

### 验证器类

```python
class StockDataValidator:
    """股票数据验证器"""
    
    @staticmethod
    def validate_stock_code(code: str, market: str = "A") -> bool:
        """验证股票代码"""
        if market == "A":
            return bool(re.match(r'^[0-9]{6}$', code))
        elif market == "HK":
            return bool(re.match(r'^[0-9]{5}$', code))
        return False
    
    @staticmethod
    def validate_price_data(price: float) -> bool:
        """验证价格数据"""
        return isinstance(price, (int, float)) and price > 0
    
    @staticmethod
    def validate_volume_data(volume: int) -> bool:
        """验证成交量数据"""
        return isinstance(volume, int) and volume >= 0
    
    @staticmethod
    def validate_date_data(trade_date: date) -> bool:
        """验证交易日期"""
        return isinstance(trade_date, date) and trade_date <= date.today()
    
    def validate_stock_data(self, data: StockData) -> List[str]:
        """验证完整股票数据"""
        errors = []
        
        # 股票代码验证
        if not self.validate_stock_code(data.code):
            errors.append(f"无效的股票代码: {data.code}")
        
        # 价格数据验证
        price_fields = ['open_price', 'close_price', 'high_price', 'low_price']
        for field in price_fields:
            price = getattr(data, field)
            if not self.validate_price_data(price):
                errors.append(f"无效的{field}: {price}")
        
        # 价格逻辑验证
        if data.high_price < max(data.open_price, data.close_price):
            errors.append("最高价不能低于开盘价或收盘价")
        
        if data.low_price > min(data.open_price, data.close_price):
            errors.append("最低价不能高于开盘价或收盘价")
        
        # 成交量验证
        if not self.validate_volume_data(data.volume):
            errors.append(f"无效的成交量: {data.volume}")
        
        # 日期验证
        if not self.validate_date_data(data.date):
            errors.append(f"无效的交易日期: {data.date}")
        
        return errors
```

### 使用示例

```python
from quant_system.models.stock_data import StockDataValidator

validator = StockDataValidator()

# 验证股票数据
errors = validator.validate_stock_data(stock)
if errors:
    print("数据验证失败:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ 数据验证通过")

# 单独验证股票代码
is_valid = validator.validate_stock_code("000001", "A")
print(f"股票代码验证: {'通过' if is_valid else '失败'}")
```

## 📊 技术指标数据 (TechnicalIndicators)

### 技术指标类

```python
@dataclass
class TechnicalIndicators:
    """技术指标数据"""
    
    # 移动平均线
    ma_5: Optional[float] = None      # 5日均线
    ma_10: Optional[float] = None     # 10日均线
    ma_20: Optional[float] = None     # 20日均线
    ma_60: Optional[float] = None     # 60日均线
    
    # MACD指标
    macd: Optional[float] = None      # MACD值
    macd_signal: Optional[float] = None  # MACD信号线
    macd_hist: Optional[float] = None    # MACD柱状图
    
    # RSI指标
    rsi_6: Optional[float] = None     # 6日RSI
    rsi_14: Optional[float] = None    # 14日RSI
    
    # 布林带
    bb_upper: Optional[float] = None  # 布林带上轨
    bb_middle: Optional[float] = None # 布林带中轨
    bb_lower: Optional[float] = None  # 布林带下轨
    
    # KDJ指标
    kdj_k: Optional[float] = None     # K值
    kdj_d: Optional[float] = None     # D值
    kdj_j: Optional[float] = None     # J值
    
    # 成交量指标
    volume_ma_5: Optional[float] = None   # 5日成交量均线
    volume_ratio: Optional[float] = None  # 量比
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典"""
        return {k: v for k, v in asdict(self).items() if v is not None}
```

### 扩展股票数据

```python
@dataclass
class EnhancedStockData(StockData):
    """增强股票数据（包含技术指标）"""
    
    indicators: Optional[TechnicalIndicators] = None
    
    def add_indicators(self, indicators: TechnicalIndicators):
        """添加技术指标"""
        self.indicators = indicators
    
    def get_indicator(self, name: str) -> Optional[float]:
        """获取指定技术指标"""
        if self.indicators:
            return getattr(self.indicators, name, None)
        return None
    
    def has_indicator(self, name: str) -> bool:
        """检查是否有指定技术指标"""
        return self.get_indicator(name) is not None
```

## 📋 股票列表数据 (StockList)

### 股票列表类

```python
class StockList:
    """股票列表管理"""
    
    def __init__(self, stocks: List[StockData] = None):
        """初始化股票列表"""
        self.stocks = stocks or []
        self._index = {}  # 代码索引
        self._build_index()
    
    def _build_index(self):
        """构建代码索引"""
        self._index = {stock.code: i for i, stock in enumerate(self.stocks)}
    
    def add_stock(self, stock: StockData):
        """添加股票"""
        if stock.code in self._index:
            # 更新现有股票
            self.stocks[self._index[stock.code]] = stock
        else:
            # 添加新股票
            self.stocks.append(stock)
            self._index[stock.code] = len(self.stocks) - 1
    
    def get_stock(self, code: str) -> Optional[StockData]:
        """获取指定股票"""
        if code in self._index:
            return self.stocks[self._index[code]]
        return None
    
    def remove_stock(self, code: str) -> bool:
        """移除股票"""
        if code in self._index:
            index = self._index[code]
            del self.stocks[index]
            self._build_index()  # 重建索引
            return True
        return False
    
    def filter_by_criteria(self, criteria: Callable[[StockData], bool]) -> 'StockList':
        """按条件筛选股票"""
        filtered_stocks = [stock for stock in self.stocks if criteria(stock)]
        return StockList(filtered_stocks)
    
    def sort_by(self, key: str, reverse: bool = False) -> 'StockList':
        """按字段排序"""
        sorted_stocks = sorted(self.stocks, 
                             key=lambda x: getattr(x, key, 0), 
                             reverse=reverse)
        return StockList(sorted_stocks)
    
    def to_dataframe(self) -> pd.DataFrame:
        """转换为DataFrame"""
        data = []
        for stock in self.stocks:
            stock_dict = asdict(stock)
            # 处理技术指标
            if hasattr(stock, 'indicators') and stock.indicators:
                stock_dict.update(stock.indicators.to_dict())
            data.append(stock_dict)
        
        return pd.DataFrame(data)
    
    def __len__(self) -> int:
        return len(self.stocks)
    
    def __iter__(self):
        return iter(self.stocks)
    
    def __getitem__(self, index) -> StockData:
        return self.stocks[index]
```

### 使用示例

```python
from quant_system.models.stock_data import StockList

# 创建股票列表
stock_list = StockList()

# 添加股票
stock_list.add_stock(stock1)
stock_list.add_stock(stock2)

# 获取股票
bank_stock = stock_list.get_stock("000001")

# 筛选股票
high_volume_stocks = stock_list.filter_by_criteria(
    lambda s: s.volume > 1000000
)

# 按涨跌幅排序
sorted_stocks = stock_list.sort_by('change_pct', reverse=True)

# 转换为DataFrame
df = stock_list.to_dataframe()
print(df[['code', 'name', 'close_price', 'change_pct']].head())
```

## 🏭 数据工厂 (DataFactory)

### 数据创建工厂

```python
class StockDataFactory:
    """股票数据工厂"""
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> StockData:
        """从字典创建股票数据"""
        # 字段映射
        field_mapping = {
            'symbol': 'code',
            'stock_name': 'name',
            'trade_date': 'date',
            'open': 'open_price',
            'close': 'close_price',
            'high': 'high_price',
            'low': 'low_price',
            'vol': 'volume',
            'amount': 'amount'
        }
        
        # 转换字段名
        normalized_data = {}
        for key, value in data.items():
            mapped_key = field_mapping.get(key, key)
            normalized_data[mapped_key] = value
        
        # 处理日期字段
        if 'date' in normalized_data and isinstance(normalized_data['date'], str):
            normalized_data['date'] = datetime.strptime(
                normalized_data['date'], '%Y-%m-%d').date()
        
        return StockData(**normalized_data)
    
    @staticmethod
    def from_api_response(api_data: Dict[str, Any], source: str) -> StockData:
        """从API响应创建股票数据"""
        if source == "eastmoney":
            return StockDataFactory._from_eastmoney(api_data)
        elif source == "tushare":
            return StockDataFactory._from_tushare(api_data)
        else:
            raise ValueError(f"不支持的数据源: {source}")
    
    @staticmethod
    def _from_eastmoney(data: Dict[str, Any]) -> StockData:
        """从东方财富数据创建"""
        return StockData(
            code=data.get('代码', ''),
            name=data.get('名称', ''),
            date=date.today(),
            open_price=float(data.get('今开', 0)),
            close_price=float(data.get('最新价', 0)),
            high_price=float(data.get('最高', 0)),
            low_price=float(data.get('最低', 0)),
            volume=int(data.get('成交量', 0)),
            amount=float(data.get('成交额', 0)),
            pre_close=float(data.get('昨收', 0)),
            change_pct=float(data.get('涨跌幅', 0)) / 100
        )
    
    @staticmethod
    def create_mock_data(code: str, days: int = 30) -> List[StockData]:
        """创建模拟数据"""
        import random
        
        stocks = []
        base_price = 10.0
        current_date = date.today() - timedelta(days=days)
        
        for i in range(days):
            # 模拟价格变动
            change_pct = random.uniform(-0.1, 0.1)  # ±10%
            base_price *= (1 + change_pct)
            
            # 生成OHLC数据
            open_price = base_price * random.uniform(0.98, 1.02)
            close_price = base_price
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.05)
            low_price = min(open_price, close_price) * random.uniform(0.95, 1.0)
            
            stock = StockData(
                code=code,
                name=f"测试股票{code}",
                date=current_date + timedelta(days=i),
                open_price=round(open_price, 2),
                close_price=round(close_price, 2),
                high_price=round(high_price, 2),
                low_price=round(low_price, 2),
                volume=random.randint(100000, 10000000),
                amount=random.randint(1000000, 100000000)
            )
            
            stocks.append(stock)
        
        return stocks
```

### 使用示例

```python
from quant_system.models.stock_data import StockDataFactory

# 从字典创建
data_dict = {
    'symbol': '000001',
    'stock_name': '平安银行',
    'trade_date': '2024-01-15',
    'open': 12.50,
    'close': 12.80,
    'high': 13.00,
    'low': 12.30,
    'vol': 1000000,
    'amount': 12800000
}

stock = StockDataFactory.from_dict(data_dict)

# 创建模拟数据
mock_stocks = StockDataFactory.create_mock_data("000001", days=30)
print(f"生成了 {len(mock_stocks)} 天的模拟数据")
```

## 🔗 相关文档

- [策略模型](strategy.md) - 策略相关数据模型
- [回测模型](backtest.md) - 回测相关数据模型
- [API文档](../README.md) - 完整API参考
