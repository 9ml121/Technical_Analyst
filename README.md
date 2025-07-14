# 量化投资系统 (Quantitative Investment System)

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-85%25-yellow.svg)](output/coverage/)

一个专业的量化投资系统，专注于A股和港股通H股的量化交易策略开发、回测和实盘交易。

## ✨ 核心特性

- 🚀 **多数据源支持**: 东方财富、Tushare、Yahoo Finance等
- 📊 **实时行情数据**: 支持A股和港股实时数据获取
- 🎯 **策略引擎**: 灵活的选股策略配置和执行
- 📈 **回测系统**: 完整的历史数据回测和性能分析
- ⚙️ **配置管理**: 多环境配置支持，YAML格式配置
- 🧪 **测试体系**: 完整的单元测试和集成测试
- 📚 **文档完善**: 详细的API文档和使用指南

## 🏗️ 系统架构

```
量化投资系统
├── 行情数据模块 (market_data/)
│   ├── 数据获取器 (fetchers/)
│   ├── 数据处理器 (processors/)
│   └── 数据存储 (storage/)
├── 策略引擎 (strategy/)
│   ├── 选股策略 (selection/)
│   ├── 交易信号 (signals/)
│   └── 风险管理 (risk/)
├── 回测系统 (backtest/)
│   ├── 回测引擎 (engine/)
│   ├── 性能分析 (analysis/)
│   └── 报告生成 (reports/)
├── 配置系统 (config/)
│   ├── 环境配置 (environments/)
│   ├── 策略配置 (strategies/)
│   └── 数据源配置 (data_sources/)
└── 工具模块 (utils/)
    ├── 验证器 (validators/)
    ├── 辅助函数 (helpers/)
    └── 日志系统 (logger/)
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- 网络连接
- 8GB+ 内存推荐

### 2. 安装

```bash
# 克隆项目
git clone https://github.com/your-username/quantitative-investment-system.git
cd quantitative-investment-system

# 安装依赖
pip install -r requirements.txt

# 或使用conda
conda env create -f environment.yml
conda activate quant-system
```

### 3. 配置

```bash
# 查看可用配置
python scripts/config_manager.py list

# 验证配置
python scripts/config_manager.py validate

# 创建自定义策略
python scripts/config_manager.py create-strategy
```

### 4. 运行示例

```bash
# 获取实时行情
python examples/get_realtime_data.py

# 运行回测
python examples/run_backtest.py

# 启动策略监控
python examples/strategy_monitor.py
```

## 📊 数据源

### 主要数据源

| 数据源        | 类型 | 支持市场  | 特点                  |
| ------------- | ---- | --------- | --------------------- |
| 东方财富      | 免费 | A股       | 实时数据，无需注册    |
| Tushare       | 付费 | A股、港股 | 高质量数据，需要token |
| Yahoo Finance | 免费 | 全球      | 国际市场支持          |

### 数据类型

- **实时行情**: 价格、成交量、涨跌幅等
- **历史数据**: K线数据、复权数据
- **基本面数据**: 财务指标、公司信息
- **技术指标**: MA、MACD、RSI等

## 🎯 策略开发

### 内置策略

1. **动量策略**: 基于价格动量的选股策略
2. **均值回归**: 基于价格均值回归的策略
3. **技术指标**: 基于技术指标的交易策略

### 自定义策略

```python
from quant_system.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)

    def select_stocks(self, market_data):
        # 实现选股逻辑
        return selected_stocks

    def generate_signals(self, stocks):
        # 生成交易信号
        return signals
```

## 📈 回测系统

### 回测配置

```yaml
backtest:
  start_date: "2023-01-01"
  end_date: "2024-01-01"
  initial_capital: 1000000.0
  max_positions: 10
  commission_rate: 0.0003
```

### 性能指标

- **收益率**: 总收益率、年化收益率
- **风险指标**: 最大回撤、夏普比率、波动率
- **交易统计**: 胜率、盈亏比、换手率

## ⚙️ 配置管理

### 环境配置

```bash
# 开发环境
export ENVIRONMENT=development

# 测试环境
export ENVIRONMENT=testing

# 生产环境
export ENVIRONMENT=production
```

### 配置文件

- `config/default.yaml`: 默认配置
- `config/environments/`: 环境特定配置
- `config/strategies/`: 策略配置
- `config/data_sources.yaml`: 数据源配置

## 🧪 测试

### 运行测试

```bash
# 检查测试环境
python scripts/run_tests.py check

# 运行所有测试
python scripts/run_tests.py all

# 运行单元测试
python scripts/run_tests.py unit

# 生成覆盖率报告
python scripts/run_tests.py coverage
```

### 测试覆盖率

- 总体覆盖率: 85%+
- 核心模块: 90%+
- 工具模块: 85%+

## 📚 文档

- [API文档](docs/api/) - 详细的API参考
- [用户指南](docs/user_guide.md) - 使用说明
- [开发指南](docs/developer_guide.md) - 开发文档
- [配置指南](docs/configuration.md) - 配置说明
- [测试指南](docs/testing_guide.md) - 测试文档

## 🔧 开发

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行代码检查
flake8 src/
black src/
isort src/
```

### 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 支持

- 📧 邮件: support@quant-system.com
- 💬 讨论: [GitHub Discussions](https://github.com/your-username/quantitative-investment-system/discussions)
- 🐛 问题: [GitHub Issues](https://github.com/your-username/quantitative-investment-system/issues)

## 🙏 致谢

感谢以下开源项目的支持：

- [pandas](https://pandas.pydata.org/) - 数据处理
- [numpy](https://numpy.org/) - 数值计算
- [matplotlib](https://matplotlib.org/) - 数据可视化
- [pytest](https://pytest.org/) - 测试框架
- [pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
