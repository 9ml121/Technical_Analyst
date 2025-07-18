# 微服务架构迁移优先级计划

## 📊 依赖关系分析结果

### 核心模块依赖图
```
main.py (入口)
├── utils/ (工具类)
│   ├── logger.py ✅ 已迁移到shared/utils
│   ├── config_loader.py ✅ 已迁移到shared/utils  
│   ├── helpers.py ✅ 已迁移到shared/utils
│   ├── validators.py ✅ 已迁移到shared/utils
│   ├── cache.py ⚠️ 待迁移
│   ├── performance.py ⚠️ 待迁移
│   └── concurrent.py ⚠️ 待迁移
├── models/ (数据模型) ✅ 已迁移到shared/models
└── core/ (核心功能)
    ├── data_provider.py ⚠️ 高优先级
    ├── strategy_engine.py ⚠️ 高优先级
    ├── backtest_engine.py ⚠️ 高优先级
    ├── trading_strategy.py ⚠️ 中优先级
    ├── feature_extraction.py ⚠️ 中优先级
    ├── analysis_module.py ⚠️ 低优先级
    └── ml_enhanced_strategy.py ⚠️ 低优先级
```

## 🎯 迁移优先级矩阵

### 🔴 高优先级 (P0) - 立即迁移
**影响范围**: 整个系统核心功能
**迁移难度**: 中等
**业务价值**: 极高

#### 1. `data_provider.py` → `data-service`
- **依赖**: 被 feature_extraction.py 依赖
- **功能**: 历史数据获取、股票列表管理
- **迁移目标**: `services/data-service/app/services/data_provider_service.py`
- **API设计**: 
  ```python
  # 新API接口
  GET /api/v1/stocks/list?market=A
  GET /api/v1/stocks/{code}/history?start_date=xxx&end_date=xxx
  POST /api/v1/stocks/batch-history
  ```

#### 2. `strategy_engine.py` → `strategy-service`
- **依赖**: 被 main.py 直接调用
- **功能**: 选股策略引擎、策略配置管理
- **迁移目标**: `services/strategy-service/app/services/strategy_engine_service.py`
- **API设计**:
  ```python
  # 新API接口
  POST /api/v1/strategies/screen-stocks
  GET /api/v1/strategies/{strategy_id}/signals
  POST /api/v1/strategies/load-config
  ```

#### 3. `backtest_engine.py` → `core-service`
- **依赖**: 被 main.py 直接调用
- **功能**: 回测引擎、性能分析
- **迁移目标**: `services/core-service/app/services/backtest_service.py`
- **API设计**:
  ```python
  # 新API接口
  POST /api/v1/backtest/run
  GET /api/v1/backtest/{backtest_id}/results
  GET /api/v1/backtest/{backtest_id}/performance
  ```

### 🟡 中优先级 (P1) - 近期迁移
**影响范围**: 特定功能模块
**迁移难度**: 中等
**业务价值**: 高

#### 4. `trading_strategy.py` → `strategy-service`
- **依赖**: 被 backtest_engine.py 依赖
- **功能**: 交易策略制定、信号生成
- **迁移目标**: `services/strategy-service/app/services/trading_strategy_service.py`

#### 5. `feature_extraction.py` → `core-service`
- **依赖**: 被 ml_enhanced_strategy.py 依赖
- **功能**: 量化特征提取、技术指标计算
- **迁移目标**: `services/core-service/app/services/feature_extraction_service.py`

### 🟢 低优先级 (P2) - 后期迁移
**影响范围**: 辅助功能
**迁移难度**: 低
**业务价值**: 中等

#### 6. `analysis_module.py` → `core-service`
- **依赖**: 独立模块
- **功能**: 样本数据分析、报告生成
- **迁移目标**: `services/core-service/app/services/analysis_service.py`

#### 7. `ml_enhanced_strategy.py` → `strategy-service`
- **依赖**: 依赖 feature_extraction.py
- **功能**: 机器学习增强策略
- **迁移目标**: `services/strategy-service/app/services/ml_strategy_service.py`

## 📋 详细迁移计划

### 第一阶段：核心数据服务 (Week 1-2)

#### 1.1 迁移 data_provider.py
```bash
# 迁移步骤
1. 分析 data_provider.py 的接口和功能
2. 在 data-service 中创建对应的服务类
3. 实现 REST API 接口
4. 更新依赖该模块的其他服务
5. 编写单元测试
6. 性能测试和优化
```

**迁移检查清单**:
- [ ] 创建 `DataProviderService` 类
- [ ] 实现股票列表获取 API
- [ ] 实现历史数据获取 API
- [ ] 实现数据缓存机制
- [ ] 添加错误处理和重试机制
- [ ] 编写 API 文档
- [ ] 创建集成测试

#### 1.2 迁移 strategy_engine.py
```bash
# 迁移步骤
1. 分析策略引擎的配置加载逻辑
2. 在 strategy-service 中实现策略管理
3. 创建策略配置的 CRUD API
4. 实现选股逻辑的 API 化
5. 添加策略验证和测试功能
```

**迁移检查清单**:
- [ ] 创建 `StrategyEngineService` 类
- [ ] 实现策略配置管理 API
- [ ] 实现选股逻辑 API
- [ ] 添加策略验证功能
- [ ] 实现策略性能监控
- [ ] 创建策略测试框架

### 第二阶段：核心计算服务 (Week 3-4)

#### 2.1 迁移 backtest_engine.py
```bash
# 迁移步骤
1. 分析回测引擎的核心算法
2. 在 core-service 中实现回测服务
3. 设计异步回测任务处理
4. 实现回测结果存储和查询
5. 添加回测性能优化
```

**迁移检查清单**:
- [ ] 创建 `BacktestService` 类
- [ ] 实现异步回测任务处理
- [ ] 实现回测结果存储
- [ ] 添加回测进度监控
- [ ] 实现回测结果分析 API
- [ ] 优化回测性能

#### 2.2 迁移 trading_strategy.py
```bash
# 迁移步骤
1. 分析交易策略的信号生成逻辑
2. 在 strategy-service 中实现交易策略服务
3. 实现策略参数管理
4. 添加策略回测功能
5. 实现策略性能评估
```

### 第三阶段：高级功能服务 (Week 5-6)

#### 3.1 迁移 feature_extraction.py
#### 3.2 迁移 analysis_module.py
#### 3.3 迁移 ml_enhanced_strategy.py

## 🔧 技术实现细节

### API 设计原则
1. **RESTful 设计**: 遵循 REST 规范
2. **版本控制**: 使用 `/api/v1/` 版本前缀
3. **统一响应格式**: 
   ```json
   {
     "success": true,
     "data": {...},
     "message": "操作成功",
     "timestamp": "2024-01-15T10:30:00Z"
   }
   ```
4. **错误处理**: 统一的错误码和错误信息
5. **分页支持**: 大数据集的分页查询

### 数据迁移策略
1. **渐进式迁移**: 新旧系统并行运行
2. **数据同步**: 确保数据一致性
3. **回滚机制**: 支持快速回滚到旧系统
4. **性能监控**: 实时监控迁移效果

### 测试策略
1. **单元测试**: 每个服务模块的单元测试
2. **集成测试**: 服务间通信测试
3. **端到端测试**: 完整业务流程测试
4. **性能测试**: 负载和压力测试
5. **兼容性测试**: 新旧系统兼容性验证

## 📊 成功指标

### 技术指标
- [ ] API 响应时间 < 200ms
- [ ] 服务可用性 > 99.9%
- [ ] 错误率 < 0.1%
- [ ] 测试覆盖率 > 80%

### 业务指标
- [ ] 功能完整性 100%
- [ ] 数据准确性 100%
- [ ] 用户满意度 > 95%
- [ ] 开发效率提升 > 30%

## 🚨 风险控制

### 高风险点
1. **数据一致性**: 新旧系统数据同步
2. **性能影响**: 服务间通信开销
3. **依赖管理**: 服务间依赖关系复杂

### 缓解措施
1. **数据备份**: 完整的备份和恢复机制
2. **性能监控**: 实时性能监控和告警
3. **灰度发布**: 逐步迁移，降低风险
4. **回滚计划**: 详细的回滚操作指南

---

**计划制定**: 2024年1月
**预计完成**: 2024年3月
**负责人**: 技术团队
**审核人**: 架构师 