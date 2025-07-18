# 微服务架构初始化指南

## 📋 概述

`scripts/init_microservices.py` 是一个完整的微服务架构初始化脚本，可以自动创建完整的微服务目录结构、基础代码模板和配置文件。

## 🚀 快速开始

### 1. 基础初始化（推荐）
保留现有代码，创建新的微服务结构：

```bash
python scripts/init_microservices.py
```

### 2. 完整迁移（可选）
移动现有代码到legacy目录，完全重构：

```bash
python scripts/init_microservices.py --move-legacy
```

## 📁 创建的目录结构

执行脚本后将创建以下结构：

```
Technical_Analyst/
├── services/                    # 微服务目录
│   ├── gateway/                # API网关 (端口:8000)
│   ├── core-service/           # 核心服务 (端口:8001)
│   ├── data-service/           # 数据服务 (端口:8002)
│   ├── strategy-service/       # 策略服务 (端口:8003)
│   ├── notification-service/   # 通知服务 (端口:8004)
│   └── web-service/           # Web服务 (端口:8005)
├── shared/                     # 共享组件
│   ├── models/                 # 共享数据模型
│   ├── utils/                  # 共享工具类
│   └── proto/                  # gRPC协议定义
├── infrastructure/             # 基础设施配置
│   ├── docker/                 # Docker配置
│   ├── kubernetes/             # K8s配置
│   ├── monitoring/             # 监控配置
│   └── databases/              # 数据库配置
├── tests/                      # 测试目录
├── tools/                      # 开发工具
├── deployment/                 # 部署配置
├── legacy/                     # 遗留代码（可选）
├── docker-compose.yml          # 开发环境
├── .env.example               # 环境配置模板
└── Makefile                   # 管理命令
```

## 🛠️ 每个微服务包含

每个微服务都有完整的结构：

```
services/{service}/
├── Dockerfile                  # Docker配置
├── requirements.txt            # Python依赖
├── app/
│   ├── main.py                # FastAPI主入口
│   ├── api/                   # API路由
│   ├── core/                  # 业务逻辑
│   ├── models/                # 数据模型
│   ├── services/              # 服务层
│   └── database/              # 数据库配置
├── tests/                     # 单元测试
├── config/                    # 配置文件
└── logs/                      # 日志目录
```

## ⚙️ 自动创建的功能

### 1. FastAPI模板
- ✅ 完整的FastAPI应用结构
- ✅ CORS配置
- ✅ 健康检查API (`/health`)
- ✅ 自动API文档 (`/docs`)
- ✅ 统一的日志系统

### 2. 共享组件
- ✅ 统一的数据模型 (BaseEntity, StockData, KLineData)
- ✅ 统一的日志工具 (Logger)
- ✅ 统一的异常处理 (QuantSystemException)
- ✅ 统一的配置管理

### 3. Docker配置
- ✅ 每个服务的Dockerfile
- ✅ docker-compose.yml (包含所有服务)
- ✅ PostgreSQL + TimescaleDB + Redis

### 4. 开发工具
- ✅ Makefile (make up/down/build/test等命令)
- ✅ 环境配置模板 (.env.example)
- ✅ 初始化脚本 (scripts/init_microservices_env.py)

## 🔧 初始化后的操作

### 1. 配置环境
```bash
# 复制并编辑环境配置
cp .env.example .env
vim .env  # 修改数据库密码、API密钥等
```

### 2. 启动开发环境
```bash
# 启动基础服务（数据库）
make dev-up

# 或者启动所有服务
make up
```

### 3. 验证服务
```bash
# 查看服务状态
docker-compose ps

# 查看日志
make logs

# 测试API网关
curl http://localhost:8000/health
```

## 🌐 服务端口分配

| 服务 | 端口 | 说明 |
|-----|------|------|
| Gateway | 8000 | API网关，统一入口 |
| Core Service | 8001 | 核心服务 |
| Data Service | 8002 | 数据服务 |
| Strategy Service | 8003 | 策略服务 |
| Notification Service | 8004 | 通知服务 |
| Web Service | 8005 | Web界面服务 |
| PostgreSQL | 5432 | 主数据库 |
| TimescaleDB | 5433 | 时序数据库 |
| Redis | 6379 | 缓存/消息队列 |

## 📝 迁移现有代码

### 渐进式迁移策略

1. **保留现有代码**
   ```bash
   # 使用基础初始化，现有代码保持不变
   python scripts/init_microservices.py
   ```

2. **逐步迁移业务逻辑**
   ```bash
   # 将 src/market_data/ 迁移到 services/data-service/
   # 将 src/quant_system/core/ 迁移到 services/strategy-service/
   # 将 web/ 迁移到 services/web-service/
   ```

3. **更新导入路径**
   - 使用共享模型：`from shared.models.market_data import StockData`
   - 使用共享工具：`from shared.utils.logger import get_logger`

## 🧪 测试

```bash
# 运行所有测试
make test

# 运行特定服务测试
python -m pytest services/data-service/tests/ -v
```

## 🚨 注意事项

1. **数据库初始化**
   - 首次运行时需要等待数据库启动
   - 可能需要手动运行数据库迁移

2. **环境变量配置**
   - 必须配置 `.env` 文件
   - 数据源API密钥需要单独申请

3. **依赖安装**
   - 每个服务有独立的requirements.txt
   - 共享依赖在shared/requirements.txt

## 🔄 常用命令

```bash
# 查看帮助
make help

# 构建所有服务
make build

# 启动开发环境（仅数据库）
make dev-up

# 启动所有服务
make up

# 停止所有服务
make down

# 查看日志
make logs

# 清理容器和数据
make clean

# 运行测试
make test
```

## 🎯 下一步开发

1. **API设计**: 为每个微服务设计RESTful API
2. **数据库设计**: 设计微服务的数据库模式
3. **服务间通信**: 实现服务间的API调用
4. **业务逻辑迁移**: 将现有业务逻辑迁移到对应微服务
5. **前端改造**: 将前端改为调用API网关

## 🆘 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 修改 docker-compose.yml 中的端口映射
   ports:
     - "8001:8000"  # 改为其他可用端口
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库是否启动
   docker-compose ps
   
   # 查看数据库日志
   docker-compose logs postgres
   ```

3. **权限问题**
   ```bash
   # 设置脚本执行权限
   chmod +x scripts/init_microservices.py
   ```

---

**创建日期**: 2024年1月  
**最后更新**: 2024年1月  
**版本**: v1.0
