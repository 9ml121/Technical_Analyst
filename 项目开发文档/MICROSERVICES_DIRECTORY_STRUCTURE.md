# Technical_Analyst 微服务架构目录结构规划

## 📋 重构概述

基于现有的单体架构，按照重构计划将系统拆分为以下微服务：
- **Core Service**: 核心量化服务（用户管理、配置管理、系统监控）
- **Data Service**: 数据获取服务（市场数据获取、存储、分发）
- **Web Service**: Web界面服务（前端应用、API接口）
- **Strategy Service**: 策略管理服务（策略执行、信号生成、回测分析）
- **Notification Service**: 通知服务（邮件、短信、系统通知）
- **Gateway**: API网关（路由、认证、限流）

## 🏗️ 目标目录结构

```
Technical_Analyst/
├── README.md                          # 项目总体说明
├── docker-compose.yml                 # 开发环境容器编排
├── docker-compose.prod.yml           # 生产环境容器编排
├── .gitignore
├── .env.example                       # 环境变量模板
├── Makefile                          # 项目管理脚本
│
├── docs/                             # 文档目录
│   ├── api/                          # API文档
│   │   ├── gateway.md
│   │   ├── core-service.md
│   │   ├── data-service.md
│   │   ├── strategy-service.md
│   │   ├── notification-service.md
│   │   └── web-service.md
│   ├── architecture/                 # 架构文档
│   │   ├── overview.md
│   │   ├── microservices.md
│   │   ├── data-flow.md
│   │   └── deployment.md
│   ├── guides/                       # 操作指南
│   │   ├── development.md
│   │   ├── deployment.md
│   │   ├── testing.md
│   │   └── monitoring.md
│   └── legacy/                       # 遗留文档
│       └── (现有docs内容)
│
├── scripts/                          # 项目脚本
│   ├── setup/                        # 环境配置脚本
│   │   ├── init-dev.sh
│   │   ├── init-prod.sh
│   │   └── cleanup.sh
│   ├── deploy/                       # 部署脚本
│   │   ├── deploy-dev.sh
│   │   ├── deploy-prod.sh
│   │   └── rollback.sh
│   ├── database/                     # 数据库脚本
│   │   ├── migrations/
│   │   ├── init.sql
│   │   └── seed.sql
│   └── monitoring/                   # 监控脚本
│       ├── health-check.sh
│       └── backup.sh
│
├── shared/                           # 共享组件
│   ├── proto/                        # gRPC协议定义
│   │   ├── core.proto
│   │   ├── data.proto
│   │   ├── strategy.proto
│   │   └── notification.proto
│   ├── models/                       # 共享数据模型
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── market_data.py
│   │   ├── strategy.py
│   │   ├── user.py
│   │   └── trade.py
│   ├── utils/                        # 共享工具类
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── config.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── exceptions.py
│   └── requirements.txt              # 共享依赖
│
├── services/                         # 微服务目录
│   │
│   ├── gateway/                      # API网关服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── rate_limit.py
│   │   │   │   └── cors.py
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── core.py
│   │   │   │   ├── data.py
│   │   │   │   ├── strategy.py
│   │   │   │   └── notification.py
│   │   │   └── config/
│   │   │       ├── __init__.py
│   │   │       ├── settings.py
│   │   │       └── routes.yaml
│   │   ├── tests/
│   │   │   ├── test_auth.py
│   │   │   ├── test_routing.py
│   │   │   └── test_rate_limit.py
│   │   └── logs/
│   │
│   ├── core-service/                 # 核心服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── users.py
│   │   │   │   ├── config.py
│   │   │   │   └── system.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user_manager.py
│   │   │   │   ├── config_manager.py
│   │   │   │   └── system_monitor.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py
│   │   │   │   ├── config.py
│   │   │   │   └── system.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── config_service.py
│   │   │   │   └── monitoring_service.py
│   │   │   └── database/
│   │   │       ├── __init__.py
│   │   │       ├── connection.py
│   │   │       └── migrations/
│   │   ├── tests/
│   │   │   ├── test_user_manager.py
│   │   │   ├── test_config_manager.py
│   │   │   └── test_system_monitor.py
│   │   ├── config/
│   │   │   ├── development.yaml
│   │   │   ├── production.yaml
│   │   │   └── testing.yaml
│   │   └── logs/
│   │
│   ├── data-service/                 # 数据服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── market_data.py
│   │   │   │   ├── historical.py
│   │   │   │   └── realtime.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data_fetcher.py
│   │   │   │   ├── data_processor.py
│   │   │   │   └── data_distributor.py
│   │   │   ├── fetchers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── eastmoney_fetcher.py
│   │   │   │   ├── tushare_fetcher.py
│   │   │   │   ├── tencent_fetcher.py
│   │   │   │   └── multi_source_fetcher.py
│   │   │   ├── processors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── data_cleaner.py
│   │   │   │   ├── feature_calculator.py
│   │   │   │   └── data_validator.py
│   │   │   ├── storage/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── timeseries_db.py
│   │   │   │   ├── cache_manager.py
│   │   │   │   └── file_storage.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── market_data.py
│   │   │       └── stock_info.py
│   │   ├── tests/
│   │   │   ├── test_fetchers.py
│   │   │   ├── test_processors.py
│   │   │   └── test_storage.py
│   │   ├── config/
│   │   │   ├── data_sources.yaml
│   │   │   ├── processing.yaml
│   │   │   └── storage.yaml
│   │   ├── data/                     # 数据缓存目录
│   │   │   ├── cache/
│   │   │   ├── historical/
│   │   │   └── temp/
│   │   └── logs/
│   │
│   ├── strategy-service/             # 策略服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── strategies.py
│   │   │   │   ├── backtest.py
│   │   │   │   └── signals.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── strategy_engine.py
│   │   │   │   ├── backtest_engine.py
│   │   │   │   ├── signal_generator.py
│   │   │   │   └── portfolio_manager.py
│   │   │   ├── strategies/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_strategy.py
│   │   │   │   ├── momentum_strategy.py
│   │   │   │   ├── ml_strategy.py
│   │   │   │   └── custom_strategy.py
│   │   │   ├── ml/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── feature_engine.py
│   │   │   │   ├── model_trainer.py
│   │   │   │   ├── predictor.py
│   │   │   │   └── models/
│   │   │   │       ├── lstm_model.py
│   │   │   │       ├── random_forest.py
│   │   │   │       └── xgboost_model.py
│   │   │   ├── backtesting/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── backtest_engine.py
│   │   │   │   ├── performance_analyzer.py
│   │   │   │   └── report_generator.py
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── strategy.py
│   │   │       ├── signal.py
│   │   │       └── performance.py
│   │   ├── tests/
│   │   │   ├── test_strategies.py
│   │   │   ├── test_backtest.py
│   │   │   └── test_ml_models.py
│   │   ├── config/
│   │   │   ├── strategies/
│   │   │   │   ├── momentum_config.yaml
│   │   │   │   ├── ml_config.yaml
│   │   │   │   └── custom_config.yaml
│   │   │   └── ml_models.yaml
│   │   ├── models/                   # 训练好的ML模型
│   │   │   ├── momentum/
│   │   │   ├── ml_enhanced/
│   │   │   └── custom/
│   │   └── logs/
│   │
│   ├── notification-service/         # 通知服务
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── notifications.py
│   │   │   │   └── templates.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── notification_manager.py
│   │   │   │   ├── template_engine.py
│   │   │   │   └── queue_processor.py
│   │   │   ├── providers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── email_provider.py
│   │   │   │   ├── sms_provider.py
│   │   │   │   ├── webhook_provider.py
│   │   │   │   └── push_provider.py
│   │   │   ├── templates/
│   │   │   │   ├── email/
│   │   │   │   │   ├── trade_alert.html
│   │   │   │   │   ├── daily_report.html
│   │   │   │   │   └── system_alert.html
│   │   │   │   └── sms/
│   │   │   │       ├── trade_alert.txt
│   │   │   │       └── system_alert.txt
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── notification.py
│   │   │       └── template.py
│   │   ├── tests/
│   │   │   ├── test_providers.py
│   │   │   ├── test_templates.py
│   │   │   └── test_queue.py
│   │   ├── config/
│   │   │   ├── providers.yaml
│   │   │   └── templates.yaml
│   │   └── logs/
│   │
│   └── web-service/                  # Web服务
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── api/
│       │   │   ├── __init__.py
│       │   │   ├── dashboard.py
│       │   │   ├── trading.py
│       │   │   └── websocket.py
│       │   ├── core/
│       │   │   ├── __init__.py
│       │   │   ├── dashboard_service.py
│       │   │   ├── trading_service.py
│       │   │   └── websocket_manager.py
│       │   ├── static/                # 静态资源
│       │   │   ├── css/
│       │   │   ├── js/
│       │   │   └── images/
│       │   └── templates/             # 模板文件
│       │       ├── dashboard.html
│       │       ├── trading.html
│       │       └── base.html
│       ├── frontend/                  # React前端
│       │   ├── package.json
│       │   ├── package-lock.json
│       │   ├── vite.config.js
│       │   ├── src/
│       │   │   ├── main.jsx
│       │   │   ├── App.jsx
│       │   │   ├── components/
│       │   │   │   ├── Dashboard/
│       │   │   │   ├── Trading/
│       │   │   │   ├── Strategy/
│       │   │   │   ├── Account/
│       │   │   │   └── Common/
│       │   │   ├── pages/
│       │   │   │   ├── DashboardPage.jsx
│       │   │   │   ├── TradingPage.jsx
│       │   │   │   ├── StrategyPage.jsx
│       │   │   │   └── AccountPage.jsx
│       │   │   ├── services/
│       │   │   │   ├── api.js
│       │   │   │   ├── websocket.js
│       │   │   │   └── auth.js
│       │   │   ├── store/
│       │   │   │   ├── index.js
│       │   │   │   ├── slices/
│       │   │   │   │   ├── authSlice.js
│       │   │   │   │   ├── tradingSlice.js
│       │   │   │   │   └── strategySlice.js
│       │   │   └── utils/
│       │   │       ├── helpers.js
│       │   │       └── constants.js
│       │   ├── public/
│       │   └── dist/                  # 构建输出
│       ├── tests/
│       │   ├── test_dashboard.py
│       │   ├── test_trading.py
│       │   └── test_websocket.py
│       ├── config/
│       │   ├── web.yaml
│       │   └── frontend.yaml
│       └── logs/
│
├── infrastructure/                   # 基础设施配置
│   ├── docker/                       # Docker配置
│   │   ├── gateway/
│   │   │   └── Dockerfile
│   │   ├── core-service/
│   │   │   └── Dockerfile
│   │   ├── data-service/
│   │   │   └── Dockerfile
│   │   ├── strategy-service/
│   │   │   └── Dockerfile
│   │   ├── notification-service/
│   │   │   └── Dockerfile
│   │   ├── web-service/
│   │   │   └── Dockerfile
│   │   └── nginx/
│   │       ├── Dockerfile
│   │       └── nginx.conf
│   ├── kubernetes/                   # K8s配置
│   │   ├── namespace.yaml
│   │   ├── configmaps/
│   │   ├── secrets/
│   │   ├── services/
│   │   ├── deployments/
│   │   └── ingress/
│   ├── monitoring/                   # 监控配置
│   │   ├── prometheus/
│   │   │   ├── prometheus.yml
│   │   │   └── rules/
│   │   ├── grafana/
│   │   │   ├── dashboards/
│   │   │   └── datasources/
│   │   └── alertmanager/
│   │       └── alertmanager.yml
│   └── databases/                    # 数据库配置
│       ├── postgresql/
│       │   ├── init.sql
│       │   └── schema/
│       ├── redis/
│       │   └── redis.conf
│       └── timescaledb/
│           └── init.sql
│
├── tests/                           # 集成测试
│   ├── integration/
│   │   ├── test_api_gateway.py
│   │   ├── test_service_communication.py
│   │   └── test_end_to_end.py
│   ├── performance/
│   │   ├── test_load.py
│   │   ├── test_stress.py
│   │   └── test_scalability.py
│   ├── fixtures/
│   │   ├── test_data.json
│   │   └── mock_responses.json
│   └── utils/
│       ├── test_helpers.py
│       └── test_fixtures.py
│
├── tools/                           # 开发工具
│   ├── code_generators/             # 代码生成器
│   │   ├── service_template.py
│   │   ├── api_template.py
│   │   └── model_template.py
│   ├── migration_tools/             # 迁移工具
│   │   ├── data_migrator.py
│   │   ├── schema_migrator.py
│   │   └── config_migrator.py
│   └── monitoring_tools/            # 监控工具
│       ├── health_checker.py
│       ├── log_analyzer.py
│       └── performance_profiler.py
│
├── legacy/                          # 遗留代码（逐步迁移）
│   ├── src/                         # 原有代码
│   ├── web/                         # 原有Web代码
│   ├── config/                      # 原有配置
│   └── examples/                    # 原有示例
│
└── deployment/                      # 部署相关
    ├── environments/
    │   ├── development/
    │   │   ├── docker-compose.yml
    │   │   └── .env
    │   ├── staging/
    │   │   ├── docker-compose.yml
    │   │   └── .env
    │   └── production/
    │       ├── docker-compose.yml
    │       └── .env
    ├── ci-cd/
    │   ├── .github/
    │   │   └── workflows/
    │   │       ├── test.yml
    │   │       ├── build.yml
    │   │       └── deploy.yml
    │   └── jenkins/
    │       └── Jenkinsfile
    └── backup/
        ├── database/
        └── config/
```

## 🔄 迁移策略

### 第一阶段：准备工作
1. **创建新目录结构**
   - 建立 `services/` 目录
   - 创建各微服务基础框架
   - 设置共享组件 `shared/`

2. **基础设施准备**
   - 配置 Docker 环境
   - 准备数据库迁移脚本
   - 设置监控系统基础

### 第二阶段：逐步迁移
1. **Data Service 优先**
   - 迁移 `src/market_data/` → `services/data-service/`
   - 保持API兼容性
   - 建立数据分发机制

2. **Core Service**
   - 迁移用户管理功能
   - 迁移配置管理 `src/quant_system/utils/config_loader.py`
   - 建立系统监控

3. **Strategy Service**
   - 迁移 `src/quant_system/core/` → `services/strategy-service/`
   - 保持策略API不变
   - 优化ML模型管理

4. **其他服务**
   - Notification Service (新建)
   - Web Service (重构现有web/)
   - Gateway (新建)

### 第三阶段：优化整合
1. **服务间通信优化**
2. **性能调优**
3. **监控完善**
4. **文档更新**

## 📊 目录对比分析

| 现有结构 | 新结构 | 迁移策略 |
|---------|--------|----------|
| `src/market_data/` | `services/data-service/` | 直接迁移+API化 |
| `src/quant_system/core/` | `services/strategy-service/` | 重构+模块化 |
| `web/` | `services/web-service/` | 前后端分离 |
| `config/` | `shared/` + 各服务config/ | 分散化配置 |
| `examples/` | `tests/` + `tools/` | 重新分类 |

## 🎯 实施建议

1. **渐进式迁移**：保持现有系统运行，逐步替换
2. **API优先**：先定义服务API，再实现具体功能
3. **数据兼容**：确保数据迁移过程中的一致性
4. **测试驱动**：每个服务都要有完整的测试覆盖
5. **文档同步**：架构变更同步更新文档

## 📈 预期收益

- **可维护性**：模块化架构，职责清晰
- **可扩展性**：独立服务，可按需扩容
- **可测试性**：独立测试，覆盖率提升
- **可部署性**：独立部署，降低发布风险
- **团队协作**：并行开发，提升效率

---

**文档版本**: v1.0  
**创建日期**: 2024年1月  
**最后更新**: 2024年1月  
**状态**: 待审查 