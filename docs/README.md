# 量化投资系统文档

欢迎来到量化投资系统的文档中心！这里包含了系统的完整文档，帮助您快速上手并深入了解系统的各项功能。

## 📚 文档导航

### 🚀 快速开始

- [**用户指南**](user_guide.md) - 系统使用的完整指南
  - 安装和配置
  - 基础使用
  - 数据获取
  - 策略开发
  - 回测分析

- [**机器学习小白指南**](ml_for_beginners.md) - 🆕 **AI魔法解密**
  - 机器学习基础概念
  - 量化投资中的AI应用
  - 模型性能指标解释
  - 常见误区澄清
  - 实践建议和资源

### 📖 核心文档

- [**API文档**](api/README.md) - 详细的API参考
  - 核心模块API
  - 数据模型
  - 使用示例
  - 错误处理

- [**配置指南**](configuration.md) - 配置管理详解
  - 配置文件结构
  - 环境配置
  - 策略配置
  - 数据源配置

- [**开发者指南**](developer_guide.md) - 开发和贡献指南
  - 项目架构
  - 开发环境
  - 代码规范
  - 贡献流程

- [**测试指南**](testing_guide.md) - 测试系统说明
  - 测试结构
  - 运行测试
  - 编写测试
  - 测试最佳实践

## 🎯 按用户类型导航

### 👤 普通用户

如果您是第一次使用量化投资系统：

1. 📖 阅读 [用户指南](user_guide.md) 了解基本使用
2. 🧠 学习 [机器学习小白指南](ml_for_beginners.md) 理解AI原理
3. ⚙️ 查看 [配置指南](configuration.md) 进行系统配置
4. 💻 运行 [示例代码](../examples/) 快速体验
5. 📊 查看 [API文档](api/README.md) 了解详细功能

### 👨‍💻 开发者

如果您想参与系统开发或扩展功能：

1. 🏗️ 阅读 [开发者指南](developer_guide.md) 了解架构
2. 🧪 查看 [测试指南](testing_guide.md) 了解测试体系
3. 📝 参考 [API文档](api/README.md) 了解接口设计
4. 🔧 查看 [配置指南](configuration.md) 了解配置系统

### 🏢 系统管理员

如果您负责系统部署和运维：

1. ⚙️ 重点阅读 [配置指南](configuration.md) 的环境配置部分
2. 📖 查看 [用户指南](user_guide.md) 的安装和配置章节
3. 🧪 了解 [测试指南](testing_guide.md) 进行系统验证
4. 🔍 参考故障排除和监控相关文档

## 📋 文档结构

```
docs/
├── README.md                 # 文档索引 (本文件)
├── user_guide.md            # 用户使用指南
├── ml_for_beginners.md      # 🆕 机器学习小白指南
├── developer_guide.md       # 开发者指南
├── configuration.md         # 配置指南
├── testing_guide.md         # 测试指南
├── api/                     # API文档
│   ├── README.md            # API概览
│   ├── market_data.md       # 行情数据API
│   ├── strategy.md          # 策略API
│   ├── backtest.md          # 回测API
│   ├── config.md            # 配置API
│   ├── utils.md             # 工具API
│   └── models/              # 数据模型文档
│       ├── stock_data.md    # 股票数据模型
│       ├── strategy.md      # 策略模型
│       └── backtest.md      # 回测模型
├── examples/                # 示例文档
├── faq.md                   # 常见问题
├── changelog.md             # 更新日志
└── troubleshooting.md       # 故障排除
```

## 🔍 快速查找

### 按功能查找

| 功能 | 相关文档 |
|------|----------|
| 数据获取 | [用户指南 - 数据获取](user_guide.md#数据获取), [API文档 - 行情数据](api/market_data.md) |
| 策略开发 | [用户指南 - 策略开发](user_guide.md#策略开发), [API文档 - 策略](api/strategy.md) |
| 回测分析 | [用户指南 - 回测分析](user_guide.md#回测分析), [API文档 - 回测](api/backtest.md) |
| 机器学习 | [机器学习小白指南](ml_for_beginners.md) - 🆕 **AI原理详解** |
| 配置管理 | [配置指南](configuration.md), [API文档 - 配置](api/config.md) |
| 系统安装 | [用户指南 - 安装和配置](user_guide.md#安装和配置) |
| 错误处理 | [用户指南 - 常见问题](user_guide.md#常见问题), [故障排除](troubleshooting.md) |

### 按问题类型查找

| 问题类型 | 相关文档 |
|----------|----------|
| 安装问题 | [用户指南 - 安装](user_guide.md#安装和配置) |
| 配置问题 | [配置指南](configuration.md), [故障排除](troubleshooting.md) |
| AI/ML问题 | [机器学习小白指南](ml_for_beginners.md) - 🆕 **AI知识大全** |
| API使用 | [API文档](api/README.md) |
| 开发问题 | [开发者指南](developer_guide.md) |
| 测试问题 | [测试指南](testing_guide.md) |
| 性能问题 | [用户指南 - 常见问题](user_guide.md#常见问题) |

## 📖 学习路径

### 🎓 初学者路径

1. **了解系统** → [README.md](../README.md)
2. **理解AI原理** → [机器学习小白指南](ml_for_beginners.md) - 🆕 **必读**
3. **安装配置** → [用户指南 - 安装](user_guide.md#安装和配置)
4. **运行示例** → [示例代码](../examples/)
5. **基础使用** → [用户指南 - 基础使用](user_guide.md#基础使用)
6. **深入学习** → [API文档](api/README.md)

### 🚀 进阶路径

1. **策略开发** → [用户指南 - 策略开发](user_guide.md#策略开发)
2. **回测分析** → [用户指南 - 回测分析](user_guide.md#回测分析)
3. **AI模型优化** → [机器学习小白指南](ml_for_beginners.md) - 🆕 **模型调优**
4. **配置优化** → [配置指南](configuration.md)
5. **性能调优** → [开发者指南 - 性能优化](developer_guide.md)
6. **扩展开发** → [开发者指南](developer_guide.md)

### 💼 专业路径

1. **系统架构** → [开发者指南 - 项目架构](developer_guide.md#项目架构)
2. **代码贡献** → [开发者指南 - 贡献流程](developer_guide.md#贡献流程)
3. **测试开发** → [测试指南](testing_guide.md)
4. **文档编写** → [开发者指南 - 文档编写](developer_guide.md#文档编写)
5. **发布管理** → [开发者指南 - 发布流程](developer_guide.md#发布流程)

## 🔧 工具和资源

### 📊 示例代码

- [获取实时数据](../examples/get_realtime_data.py) - 演示如何获取股票实时行情
- [运行回测](../examples/run_backtest.py) - 演示策略回测流程
- [策略开发](../examples/strategy_development.py) - 自定义策略开发示例
- [配置管理](../examples/config_management.py) - 配置系统使用示例
- [机器学习训练](../examples/robust_strategy_training.py) - 🆕 **AI模型训练示例**

### 🛠️ 管理工具

- [配置管理器](../scripts/config_manager.py) - 配置文件管理工具
- [测试运行器](../scripts/run_tests.py) - 测试执行工具
- [数据验证器](../scripts/data_validator.py) - 数据质量检查工具

### 📚 参考资料

- [Python官方文档](https://docs.python.org/3/)
- [pandas文档](https://pandas.pydata.org/docs/)
- [scikit-learn文档](https://scikit-learn.org/) - 🆕 **机器学习库**
- [pytest文档](https://docs.pytest.org/)
- [YAML规范](https://yaml.org/spec/)

## ❓ 获取帮助

### 📞 支持渠道

- 📧 **邮件支持**: support@quant-system.com
- 💬 **讨论区**: [GitHub Discussions](https://github.com/your-username/quantitative-investment-system/discussions)
- 🐛 **问题反馈**: [GitHub Issues](https://github.com/your-username/quantitative-investment-system/issues)
- 📖 **文档问题**: [文档Issues](https://github.com/your-username/quantitative-investment-system/issues?q=label%3Adocumentation)

### 🤝 社区资源

- 👥 **用户群组**: 加入我们的用户交流群
- 📺 **视频教程**: 观看系统使用教程
- 📝 **博客文章**: 阅读最新的技术文章
- 🎓 **在线课程**: 参加量化投资培训
- 🧠 **AI学习资源**: [机器学习小白指南](ml_for_beginners.md) - 🆕 **AI知识宝库**

## 📝 文档贡献

我们欢迎您为文档做出贡献！

### 如何贡献

1. **发现问题** - 在使用过程中发现文档问题
2. **提出建议** - 通过Issues提出改进建议
3. **编写内容** - 直接提交文档改进的PR
4. **审核反馈** - 参与文档审核和反馈

### 文档规范

- 使用Markdown格式
- 遵循现有的文档结构
- 提供清晰的示例代码
- 包含必要的截图和图表
- 保持内容的准确性和时效性

## 🔄 文档更新

文档会随着系统的更新而持续改进：

- **版本同步** - 文档与代码版本保持同步
- **定期审核** - 定期检查和更新文档内容
- **用户反馈** - 根据用户反馈改进文档
- **最佳实践** - 不断完善文档的最佳实践

## 📊 文档统计

- 📄 **总页数**: 9个主要文档页面（+1个新增）
- 🔗 **内部链接**: 60+ 个交叉引用
- 💻 **代码示例**: 120+ 个代码片段
- 🖼️ **图表**: 25+ 个架构图和流程图
- 🌍 **语言**: 中文为主，关键术语提供英文对照
- 🧠 **AI知识**: 完整的机器学习入门指南

---

📚 **开始您的量化投资之旅吧！** 如果您有任何问题或建议，请随时联系我们。

*最后更新: 2024年1月*
