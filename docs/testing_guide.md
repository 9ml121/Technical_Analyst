# 测试系统指南

## 📋 测试系统概述

量化投资系统采用分层测试架构，包含单元测试、集成测试和端到端测试，确保系统的可靠性和稳定性。

## 🏗️ 测试结构

```
tests/
├── __init__.py
├── conftest.py                    # pytest配置和夹具
├── fixtures/                     # 测试数据夹具
├── unit/                         # 单元测试
│   ├── test_config_system.py     # 配置系统测试
│   ├── test_data_models.py       # 数据模型测试
│   └── test_utils.py             # 工具模块测试
└── integration/                  # 集成测试
    ├── test_market_data_system.py      # 行情数据系统集成测试
    └── test_config_system_integration.py # 配置系统集成测试
```

## 🧪 测试类型

### 单元测试 (Unit Tests)
- **目标**: 测试单个函数、类或模块
- **特点**: 快速、独立、无外部依赖
- **覆盖范围**: 
  - 配置系统 (ConfigLoader, ConfigValidator)
  - 数据模型 (StockData, Strategy, Backtest)
  - 工具函数 (validators, helpers, logger)

### 集成测试 (Integration Tests)
- **目标**: 测试组件间的交互
- **特点**: 可能需要网络、文件系统等外部资源
- **覆盖范围**:
  - 行情数据获取和处理流程
  - 配置加载和验证流程
  - 系统组件协作

## 🚀 运行测试

### 使用测试脚本

```bash
# 检查测试环境
python scripts/run_tests.py check

# 运行所有测试
python scripts/run_tests.py all

# 运行单元测试
python scripts/run_tests.py unit

# 运行集成测试
python scripts/run_tests.py integration

# 运行快速测试（排除慢速测试）
python scripts/run_tests.py fast

# 运行特定测试
python scripts/run_tests.py specific tests/unit/test_config_system.py

# 按标记运行测试
python scripts/run_tests.py marker unit

# 生成覆盖率报告
python scripts/run_tests.py coverage

# 生成测试报告
python scripts/run_tests.py report

# 清理测试文件
python scripts/run_tests.py clean
```

### 直接使用pytest

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/test_config_system.py

# 运行特定测试方法
pytest tests/unit/test_config_system.py::TestConfigLoader::test_init

# 按标记运行
pytest -m unit
pytest -m integration
pytest -m "not slow"

# 生成覆盖率报告
pytest --cov=src --cov-report=html

# 并行运行测试
pytest -n auto
```

## 📊 测试标记

系统使用pytest标记来分类测试：

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.slow`: 慢速测试
- `@pytest.mark.network`: 需要网络的测试
- `@pytest.mark.api`: API相关测试
- `@pytest.mark.data`: 需要数据文件的测试

## 🔧 测试配置

### pytest.ini配置

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html:output/coverage
markers =
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试
    network: 需要网络连接的测试
    api: API相关测试
```

### 测试夹具 (Fixtures)

系统提供了丰富的测试夹具：

```python
# 配置相关夹具
@pytest.fixture
def sample_config():
    return {...}

@pytest.fixture
def config_system():
    return {...}

# 数据相关夹具
@pytest.fixture
def sample_stock_data():
    return StockData(...)

@pytest.fixture
def mock_market_data():
    return [...]
```

## 📈 测试覆盖率

### 覆盖率目标
- **总体覆盖率**: ≥ 80%
- **核心模块覆盖率**: ≥ 90%
- **工具模块覆盖率**: ≥ 85%

### 查看覆盖率报告

```bash
# 生成HTML覆盖率报告
python scripts/run_tests.py coverage

# 查看报告
open output/coverage/index.html
```

## 🐛 测试调试

### 调试失败的测试

```bash
# 详细输出
pytest -v -s

# 进入调试器
pytest --pdb

# 只运行失败的测试
pytest --lf

# 停在第一个失败
pytest -x
```

### 常见问题解决

1. **导入错误**
   ```python
   # 确保添加src到路径
   import sys
   from pathlib import Path
   src_path = Path(__file__).parent.parent.parent / "src"
   sys.path.insert(0, str(src_path))
   ```

2. **临时文件冲突**
   ```python
   # 使用exist_ok=True
   temp_dir.mkdir(exist_ok=True)
   ```

3. **环境变量问题**
   ```python
   # 使用mock或设置默认值
   @patch.dict(os.environ, {'ENVIRONMENT': 'testing'})
   def test_function():
       pass
   ```

## 📝 编写测试的最佳实践

### 1. 测试命名
```python
def test_should_return_valid_config_when_file_exists():
    """测试当文件存在时应该返回有效配置"""
    pass
```

### 2. 测试结构 (AAA模式)
```python
def test_config_loading():
    # Arrange - 准备
    config_loader = ConfigLoader()
    
    # Act - 执行
    result = config_loader.load_config("test")
    
    # Assert - 断言
    assert result is not None
    assert "system" in result
```

### 3. 使用夹具
```python
def test_with_fixture(sample_config):
    # 使用预定义的测试数据
    assert sample_config["system"]["name"] == "Test System"
```

### 4. 异常测试
```python
def test_should_raise_error_for_invalid_input():
    with pytest.raises(ValueError, match="Invalid input"):
        function_under_test("invalid")
```

### 5. 参数化测试
```python
@pytest.mark.parametrize("input,expected", [
    ("000001", True),
    ("invalid", False),
])
def test_stock_code_validation(input, expected):
    assert validate_stock_code(input) == expected
```

## 🔄 持续集成

### GitHub Actions配置示例

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: python scripts/run_tests.py coverage
```

## 📊 测试报告

### 生成报告
```bash
# 生成JUnit XML报告
pytest --junit-xml=output/test-results.xml

# 生成HTML报告
pytest --html=output/test-report.html --self-contained-html
```

### 报告内容
- 测试执行结果
- 覆盖率统计
- 性能指标
- 失败详情

## 🎯 测试策略

### 测试金字塔
```
    /\
   /  \     E2E Tests (少量)
  /____\    
 /      \   Integration Tests (适量)
/__________\ Unit Tests (大量)
```

### 测试优先级
1. **高优先级**: 核心业务逻辑、数据处理、配置管理
2. **中优先级**: 工具函数、辅助模块、UI组件
3. **低优先级**: 第三方集成、边缘情况

## 🚀 性能测试

### 基准测试
```python
def test_performance_benchmark():
    import time
    
    start_time = time.time()
    # 执行操作
    result = expensive_operation()
    end_time = time.time()
    
    # 验证性能要求
    assert end_time - start_time < 1.0  # 1秒内完成
    assert result is not None
```

### 内存测试
```python
def test_memory_usage():
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 执行操作
    large_operation()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # 验证内存使用
    assert memory_increase < 100 * 1024 * 1024  # 小于100MB
```

## 📚 参考资源

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-cov覆盖率插件](https://pytest-cov.readthedocs.io/)
- [Python测试最佳实践](https://docs.python-guide.org/writing/tests/)
- [测试驱动开发(TDD)](https://en.wikipedia.org/wiki/Test-driven_development)

---

**注意**: 测试是保证代码质量的重要手段，建议在开发新功能时同时编写相应的测试用例。
