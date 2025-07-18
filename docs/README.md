# 项目文档

欢迎来到量化投资系统文档中心！这里包含了系统的完整文档。

## 📚 文档分类

### 🚀 快速开始
- **[快速参考](quick_reference.md)** - 微服务架构的快速命令和访问地址
- **[微服务架构使用指南](microservices_guide.md)** - 完整的微服务架构使用文档

### 🏗️ 架构文档
- **[微服务架构使用指南](microservices_guide.md)** - 微服务架构详细使用说明
- **[快速参考](quick_reference.md)** - 常用命令和地址快速查询
- **[部署指南](deployment_guide.md)** - 系统部署和运维指南
- **[性能优化](performance_optimization.md)** - 系统性能优化建议

### 👥 用户指南
- **[用户指南](user_guide.md)** - 系统使用指南
- **[配置指南](configuration.md)** - 系统配置说明
- **[测试指南](testing_guide.md)** - 测试相关文档

### 👨‍💻 开发文档
- **[开发者指南](developer_guide.md)** - 开发相关文档
- **[API文档](api/)** - API接口文档
- **[机器学习入门](ml_for_beginners.md)** - 机器学习基础知识

### 📊 数据相关
- **[数据源研究](data_sources_research.md)** - 数据源调研报告
- **[港股数据源研究](free_hk_data_sources_research.md)** - 港股数据源调研

### 📋 项目报告
- **[最终项目报告](final_project_report.md)** - 项目总结报告

## 🎯 推荐阅读顺序

### 新用户
1. [快速参考](quick_reference.md) - 快速了解系统
2. [用户指南](user_guide.md) - 学习如何使用系统
3. [配置指南](configuration.md) - 配置系统参数

### 开发者
1. [微服务架构使用指南](microservices_guide.md) - 了解微服务架构
2. [开发者指南](developer_guide.md) - 开发相关文档
3. [API文档](api/) - 接口文档

### 运维人员
1. [部署指南](deployment_guide.md) - 部署和运维
2. [性能优化](performance_optimization.md) - 性能调优
3. [测试指南](testing_guide.md) - 测试相关

## 🔗 快速链接

### 微服务架构
- **启动服务**: `make dev-up`
- **API网关**: http://localhost:8000/
- **服务状态**: `docker-compose ps`

### 常用命令
```bash
make dev-up          # 启动所有微服务
make dev-down        # 停止所有微服务
make logs            # 查看所有日志
docker-compose ps    # 查看服务状态
```

### 访问地址
- **API网关**: http://localhost:8000/
- **核心服务**: http://localhost:8001/
- **数据服务**: http://localhost:8002/
- **策略服务**: http://localhost:8003/
- **通知服务**: http://localhost:8004/

## 📞 技术支持

如果您在使用过程中遇到问题：

1. 查看 [快速参考](quick_reference.md) 中的故障排除部分
2. 查看 [微服务架构使用指南](microservices_guide.md) 中的详细说明
3. 检查服务日志: `make logs`
4. 联系技术支持团队

---

**最后更新**: 2024年1月15日
**文档版本**: 2.0.0
