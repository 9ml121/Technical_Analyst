# 开发者指南

欢迎参与量化投资系统的开发！本指南将帮助您了解项目架构、开发流程和贡献方式。

## 📋 目录

1. [项目架构](#项目架构)
2. [开发环境设置](#开发环境设置)
3. [代码规范](#代码规范)
4. [模块开发](#模块开发)
5. [测试开发](#测试开发)
6. [文档编写](#文档编写)
7. [贡献流程](#贡献流程)
8. [发布流程](#发布流程)

## 🏗️ 项目架构

### 目录结构

```
quantitative-investment-system/
├── src/                          # 源代码
│   ├── market_data/              # 行情数据模块
│   │   ├── fetchers/             # 数据获取器
│   │   ├── processors/           # 数据处理器
│   │   └── storage/              # 数据存储
│   ├── quant_system/             # 核心系统
│   │   ├── strategy/             # 策略引擎
│   │   ├── backtest/             # 回测系统
│   │   ├── models/               # 数据模型
│   │   └── utils/                # 工具模块
├── tests/                        # 测试代码
│   ├── unit/                     # 单元测试
│   └── integration/              # 集成测试
├── config/                       # 配置文件
│   ├── environments/             # 环境配置
│   └── strategies/               # 策略配置
├── docs/                         # 文档
├── examples/                     # 示例代码
├── scripts/                      # 脚本工具
└── output/                       # 输出文件
```

### 核心模块

#### 1. 行情数据模块 (market_data)

```python
# 数据获取器基类
class BaseDataFetcher:
    def get_realtime_data(self, codes: List[str]) -> List[StockData]:
        raise NotImplementedError
    
    def get_historical_data(self, code: str, start: str, end: str) -> List[StockData]:
        raise NotImplementedError

# 数据处理器
class MarketDataProcessor:
    def clean_stock_data(self, data: List[Dict]) -> List[Dict]:
        """数据清洗"""
        pass
    
    def calculate_technical_indicators(self, data: List[Dict]) -> List[Dict]:
        """计算技术指标"""
        pass
```

#### 2. 策略引擎 (strategy)

```python
# 策略基类
class BaseStrategy:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = ""
        self.description = ""
    
    def select_stocks(self, market_data: List[StockData]) -> List[StockData]:
        """选股逻辑"""
        raise NotImplementedError
    
    def generate_signals(self, stocks: List[StockData]) -> List[TradingSignal]:
        """生成交易信号"""
        raise NotImplementedError
```

#### 3. 回测系统 (backtest)

```python
# 回测引擎
class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.portfolio = Portfolio()
        self.orders = []
    
    def run(self, strategy: BaseStrategy) -> BacktestResult:
        """运行回测"""
        pass
```

### 设计模式

项目采用以下设计模式：

1. **工厂模式**: 数据源创建
2. **策略模式**: 策略实现
3. **观察者模式**: 事件通知
4. **单例模式**: 配置管理
5. **适配器模式**: 数据源适配

## 🛠️ 开发环境设置

### 1. 克隆项目

```bash
git clone https://github.com/your-username/quantitative-investment-system.git
cd quantitative-investment-system
```

### 2. 创建开发环境

```bash
# 创建虚拟环境
python -m venv dev_env
source dev_env/bin/activate  # Linux/macOS
# 或
dev_env\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements-dev.txt
```

### 3. 安装开发工具

```bash
# 代码格式化
pip install black isort

# 代码检查
pip install flake8 mypy

# 测试工具
pip install pytest pytest-cov pytest-mock

# 文档工具
pip install sphinx sphinx-rtd-theme

# Git钩子
pip install pre-commit
pre-commit install
```

### 4. IDE配置

#### VS Code配置

创建 `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./dev_env/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### PyCharm配置

1. 设置Python解释器为虚拟环境
2. 配置代码风格为Black
3. 启用类型检查
4. 配置测试运行器为pytest

## 📝 代码规范

### 1. Python代码风格

遵循PEP 8规范，使用Black进行格式化：

```bash
# 格式化代码
black src/ tests/

# 排序导入
isort src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```

### 2. 命名规范

```python
# 类名：大驼峰
class StockDataFetcher:
    pass

# 函数名：小写+下划线
def get_stock_data():
    pass

# 变量名：小写+下划线
stock_price = 12.50

# 常量：大写+下划线
MAX_RETRY_COUNT = 3

# 私有成员：前缀下划线
class MyClass:
    def __init__(self):
        self._private_var = None
        self.__very_private = None
```

### 3. 文档字符串

使用Google风格的文档字符串：

```python
def calculate_returns(prices: List[float], periods: int = 1) -> List[float]:
    """计算收益率。
    
    Args:
        prices: 价格序列
        periods: 计算周期，默认为1
        
    Returns:
        收益率序列
        
    Raises:
        ValueError: 当价格序列长度不足时
        
    Example:
        >>> prices = [100, 105, 110]
        >>> returns = calculate_returns(prices)
        >>> print(returns)
        [0.05, 0.047619]
    """
    if len(prices) < periods + 1:
        raise ValueError("价格序列长度不足")
    
    returns = []
    for i in range(periods, len(prices)):
        ret = (prices[i] - prices[i - periods]) / prices[i - periods]
        returns.append(ret)
    
    return returns
```

### 4. 类型提示

使用类型提示提高代码质量：

```python
from typing import List, Dict, Optional, Union, Tuple
from datetime import date, datetime

def process_stock_data(
    data: List[Dict[str, Union[str, float, int]]],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> Tuple[List[StockData], int]:
    """处理股票数据"""
    processed_data: List[StockData] = []
    error_count: int = 0
    
    for item in data:
        try:
            stock = StockData.from_dict(item)
            if start_date and stock.date < start_date:
                continue
            if end_date and stock.date > end_date:
                continue
            processed_data.append(stock)
        except ValueError:
            error_count += 1
    
    return processed_data, error_count
```

## 🔧 模块开发

### 1. 数据获取器开发

创建新的数据获取器：

```python
# src/market_data/fetchers/my_data_fetcher.py
from typing import List, Optional
from ..base import BaseDataFetcher
from ...models.stock_data import StockData

class MyDataFetcher(BaseDataFetcher):
    """自定义数据获取器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
    
    def get_realtime_data(self, codes: List[str]) -> List[StockData]:
        """获取实时数据"""
        data = []
        for code in codes:
            # 实现数据获取逻辑
            stock_data = self._fetch_stock_data(code)
            if stock_data:
                data.append(stock_data)
        return data
    
    def _fetch_stock_data(self, code: str) -> Optional[StockData]:
        """获取单只股票数据"""
        try:
            # 实现具体的API调用
            response = self._make_api_request(code)
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"获取股票{code}数据失败: {e}")
            return None
```

### 2. 策略开发

创建新的策略：

```python
# src/quant_system/strategy/my_strategy.py
from typing import List
from ..base import BaseStrategy
from ...models.stock_data import StockData
from ...models.strategy_models import TradingSignal

class MyStrategy(BaseStrategy):
    """自定义策略"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.name = "我的策略"
        self.description = "基于自定义逻辑的策略"
        
        # 策略参数
        self.lookback_period = config.get('lookback_period', 20)
        self.threshold = config.get('threshold', 0.05)
    
    def select_stocks(self, market_data: List[StockData]) -> List[StockData]:
        """选股逻辑"""
        selected = []
        
        for stock in market_data:
            if self._meets_criteria(stock):
                selected.append(stock)
        
        # 按某种指标排序
        selected.sort(key=lambda x: x.pct_change, reverse=True)
        
        # 返回前N只
        max_positions = self.config.get('max_positions', 10)
        return selected[:max_positions]
    
    def generate_signals(self, stocks: List[StockData]) -> List[TradingSignal]:
        """生成交易信号"""
        signals = []
        
        for stock in stocks:
            signal = TradingSignal(
                stock_code=stock.code,
                signal_type='buy',
                price=stock.close_price,
                confidence=self._calculate_confidence(stock),
                reason=self._get_signal_reason(stock)
            )
            signals.append(signal)
        
        return signals
    
    def _meets_criteria(self, stock: StockData) -> bool:
        """检查是否满足选股条件"""
        # 实现具体的选股逻辑
        return (
            stock.pct_change > self.threshold and
            stock.volume > 1000000 and
            stock.close_price > 5.0
        )
```

### 3. 数据模型开发

创建新的数据模型：

```python
# src/quant_system/models/my_model.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import date

@dataclass
class MyModel:
    """自定义数据模型"""
    
    # 必需字段
    id: str
    name: str
    value: float
    date: date
    
    # 可选字段
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后验证"""
        if self.value < 0:
            raise ValueError("值不能为负数")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MyModel':
        """从字典创建实例"""
        return cls(
            id=data['id'],
            name=data['name'],
            value=float(data['value']),
            date=date.fromisoformat(data['date']),
            description=data.get('description'),
            metadata=data.get('metadata')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'value': self.value,
            'date': self.date.isoformat(),
            'description': self.description,
            'metadata': self.metadata
        }
    
    def validate(self) -> List[str]:
        """验证数据"""
        errors = []
        
        if not self.id:
            errors.append("ID不能为空")
        
        if not self.name:
            errors.append("名称不能为空")
        
        if self.value < 0:
            errors.append("值不能为负数")
        
        return errors
```

## 🧪 测试开发

### 1. 单元测试

```python
# tests/unit/test_my_module.py
import pytest
from unittest.mock import Mock, patch
from src.my_module import MyClass

class TestMyClass:
    """MyClass单元测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.config = {'param1': 'value1'}
        self.instance = MyClass(self.config)
    
    def test_init(self):
        """测试初始化"""
        assert self.instance.config == self.config
        assert self.instance.param1 == 'value1'
    
    def test_method_with_valid_input(self):
        """测试有效输入"""
        result = self.instance.my_method('valid_input')
        assert result == 'expected_output'
    
    def test_method_with_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(ValueError, match="Invalid input"):
            self.instance.my_method('invalid_input')
    
    @patch('src.my_module.external_api_call')
    def test_method_with_mock(self, mock_api):
        """测试使用Mock"""
        mock_api.return_value = {'status': 'success'}
        
        result = self.instance.method_using_api()
        
        mock_api.assert_called_once()
        assert result['status'] == 'success'
    
    @pytest.mark.parametrize("input_value,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_parametrized(self, input_value, expected):
        """参数化测试"""
        result = self.instance.double(input_value)
        assert result == expected
```

### 2. 集成测试

```python
# tests/integration/test_data_flow.py
import pytest
from src.market_data import get_eastmoney_api
from src.market_data.processors import MarketDataProcessor

class TestDataFlow:
    """数据流集成测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.api = get_eastmoney_api()
        self.processor = MarketDataProcessor()
    
    @pytest.mark.integration
    def test_complete_data_flow(self):
        """测试完整数据流"""
        # 1. 获取数据
        stocks = self.api.get_a_stock_realtime(limit=5)
        assert len(stocks) > 0
        
        # 2. 处理数据
        cleaned_stocks = self.processor.clean_stock_data(stocks)
        assert len(cleaned_stocks) <= len(stocks)
        
        # 3. 验证数据质量
        for stock in cleaned_stocks:
            assert 'code' in stock
            assert 'name' in stock
            assert 'price' in stock
            assert stock['price'] > 0
```

### 3. 测试夹具

```python
# tests/conftest.py
import pytest
from datetime import date
from src.models.stock_data import StockData

@pytest.fixture
def sample_stock_data():
    """示例股票数据夹具"""
    return StockData(
        code="000001",
        name="平安银行",
        date=date(2024, 1, 15),
        open_price=12.50,
        close_price=12.80,
        high_price=13.00,
        low_price=12.30,
        volume=1000000,
        amount=12800000
    )

@pytest.fixture
def mock_api_response():
    """模拟API响应夹具"""
    return {
        'code': '000001',
        'name': '平安银行',
        'price': 12.80,
        'change': 0.30,
        'pct_change': 0.024
    }
```

## 📚 文档编写

### 1. API文档

使用Sphinx生成API文档：

```bash
# 安装Sphinx
pip install sphinx sphinx-rtd-theme

# 初始化文档
cd docs/
sphinx-quickstart

# 生成API文档
sphinx-apidoc -o api/ ../src/

# 构建文档
make html
```

### 2. 文档字符串

```python
def complex_function(param1: str, param2: int, param3: Optional[bool] = None) -> Dict[str, Any]:
    """复杂函数的文档字符串示例。
    
    这个函数演示了如何编写详细的文档字符串，包括参数说明、
    返回值说明、异常说明和使用示例。
    
    Args:
        param1: 字符串参数，用于指定操作类型
        param2: 整数参数，表示操作次数
        param3: 可选布尔参数，控制是否启用某个功能
        
    Returns:
        包含操作结果的字典，格式如下：
        {
            'status': str,      # 操作状态
            'result': Any,      # 操作结果
            'count': int        # 操作次数
        }
        
    Raises:
        ValueError: 当param1不是有效操作类型时
        RuntimeError: 当操作执行失败时
        
    Example:
        >>> result = complex_function('process', 5, True)
        >>> print(result['status'])
        'success'
        
    Note:
        这个函数可能会消耗大量内存，建议在处理大量数据时
        分批调用。
        
    See Also:
        simple_function: 简化版本的函数
        related_function: 相关功能的函数
    """
    pass
```

## 🔄 贡献流程

### 1. 开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发和测试
# ... 编写代码 ...
python scripts/run_tests.py unit
python scripts/run_tests.py integration

# 3. 代码检查
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# 4. 提交代码
git add .
git commit -m "feat: add new feature"

# 5. 推送分支
git push origin feature/new-feature

# 6. 创建Pull Request
```

### 2. 提交信息规范

使用Conventional Commits规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型说明：
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(strategy): add momentum strategy implementation

- Implement basic momentum strategy logic
- Add configuration support
- Include unit tests

Closes #123
```

### 3. 代码审查

Pull Request审查要点：

1. **功能正确性**: 代码是否实现了预期功能
2. **代码质量**: 是否遵循代码规范
3. **测试覆盖**: 是否包含充分的测试
4. **文档完整**: 是否更新了相关文档
5. **性能影响**: 是否对性能有负面影响
6. **安全性**: 是否存在安全隐患

## 🚀 发布流程

### 1. 版本管理

使用语义化版本控制：

- `MAJOR.MINOR.PATCH`
- `1.0.0`: 主版本号.次版本号.修订号

### 2. 发布步骤

```bash
# 1. 更新版本号
# 编辑 setup.py 和 __init__.py

# 2. 更新CHANGELOG
# 记录本次发布的变更

# 3. 创建发布分支
git checkout -b release/v1.2.0

# 4. 运行完整测试
python scripts/run_tests.py all
python scripts/run_tests.py coverage

# 5. 构建文档
cd docs/
make html

# 6. 创建标签
git tag -a v1.2.0 -m "Release version 1.2.0"

# 7. 推送标签
git push origin v1.2.0

# 8. 创建GitHub Release
# 在GitHub上创建正式发布
```

### 3. 持续集成

配置GitHub Actions：

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        python scripts/run_tests.py coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

---

感谢您对量化投资系统的贡献！如有任何问题，请随时联系开发团队。
