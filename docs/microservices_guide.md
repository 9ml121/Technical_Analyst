# 微服务架构使用指南

## 📋 目录
- [服务概览](#服务概览)
- [快速开始](#快速开始)
- [服务访问地址](#服务访问地址)
- [操作命令](#操作命令)
- [API文档](#api文档)
- [开发指南](#开发指南)
- [故障排除](#故障排除)

## 🏗️ 服务概览

### 基础设施服务
| 服务名称 | 端口 | 描述 | 状态 |
|---------|------|------|------|
| PostgreSQL | 5432 | 主数据库 | ✅ 运行中 |
| Redis | 6379 | 缓存服务 | ✅ 运行中 |

### 微服务
| 服务名称 | 端口 | 描述 | 状态 |
|---------|------|------|------|
| API网关 | 8000 | 统一入口点，路由转发 | ✅ 运行中 |
| 核心量化服务 | 8001 | 量化分析、回测 | ✅ 运行中 |
| 数据获取服务 | 8002 | 股票数据获取 | ✅ 运行中 |
| 策略管理服务 | 8003 | 策略管理 | ✅ 运行中 |
| 通知服务 | 8004 | 通知管理 | ✅ 运行中 |

## 🚀 快速开始

### 1. 启动所有服务
```bash
make dev-up
```

### 2. 检查服务状态
```bash
docker-compose ps
```

### 3. 测试网关
```bash
curl http://localhost:8000/
```

## 🌐 服务访问地址

### API网关 (统一入口)
- **主页**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health
- **API文档**: http://localhost:8000/docs

### 通过网关访问各服务
- **数据服务**: http://localhost:8000/api/v1/data/api/v1/stocks/{symbol}
- **核心服务**: http://localhost:8000/api/v1/core/api/v1/analysis/{symbol}
- **策略服务**: http://localhost:8000/api/v1/strategy/api/v1/strategies
- **通知服务**: http://localhost:8000/api/v1/notification/api/v1/notifications

### 直接访问各服务
- **核心量化服务**: http://localhost:8001/
- **数据获取服务**: http://localhost:8002/
- **策略管理服务**: http://localhost:8003/
- **通知服务**: http://localhost:8004/

### 各服务API文档
- **核心服务文档**: http://localhost:8001/docs
- **数据服务文档**: http://localhost:8002/docs
- **策略服务文档**: http://localhost:8003/docs
- **通知服务文档**: http://localhost:8004/docs

## ⚡ 操作命令

### 基础操作
```bash
# 启动所有服务
make dev-up

# 停止所有服务
make dev-down

# 查看服务状态
docker-compose ps

# 查看所有服务日志
make logs

# 重新构建所有服务
make build

# 清理构建和缓存
make clean
```

### 服务管理
```bash
# 启动特定服务
docker-compose up -d [service-name]

# 停止特定服务
docker-compose stop [service-name]

# 重启特定服务
docker-compose restart [service-name]

# 查看特定服务日志
docker-compose logs [service-name]

# 进入服务容器
docker-compose exec [service-name] bash
```

### 数据库操作
```bash
# 连接PostgreSQL
docker exec -it technical_analyst-postgres-1 psql -U quant_user -d quant_db

# 测试Redis连接
docker exec technical_analyst-redis-1 redis-cli ping
```

## 📚 API文档

### 核心量化服务 API
```bash
# 股票分析
GET /api/v1/analysis/{symbol}
curl http://localhost:8001/api/v1/analysis/AAPL

# 回测
POST /api/v1/backtest
curl -X POST http://localhost:8001/api/v1/backtest
```

### 数据获取服务 API
```bash
# 获取股票数据
GET /api/v1/stocks/{symbol}
curl http://localhost:8002/api/v1/stocks/AAPL
```

### 策略管理服务 API
```bash
# 获取策略列表
GET /api/v1/strategies
curl http://localhost:8003/api/v1/strategies

# 创建新策略
POST /api/v1/strategies
curl -X POST http://localhost:8003/api/v1/strategies
```

### 通知服务 API
```bash
# 获取通知列表
GET /api/v1/notifications
curl http://localhost:8004/api/v1/notifications

# 发送通知
POST /api/v1/notifications
curl -X POST http://localhost:8004/api/v1/notifications
```

## 🛠️ 开发指南

### 添加新微服务
1. 在 `services/` 目录下创建新服务目录
2. 创建 `Dockerfile` 和 `requirements.txt`
3. 创建 `main.py` 应用文件
4. 在 `docker-compose.yml` 中添加服务配置
5. 构建并启动服务

### 修改现有服务
1. 修改服务代码
2. 重新构建服务: `docker-compose build [service-name]`
3. 重启服务: `docker-compose restart [service-name]`

### 环境变量配置
- 主配置文件: `.env`
- 示例配置文件: `.env.example`
- 各服务可通过环境变量配置数据库连接等

## 🔧 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 查看详细日志
docker-compose logs [service-name]

# 检查端口占用
lsof -i :[port]

# 重新构建服务
docker-compose build [service-name]
```

#### 2. 数据库连接失败
```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 检查数据库连接
docker exec technical_analyst-postgres-1 psql -U quant_user -d quant_db -c "SELECT version();"
```

#### 3. 服务间通信失败
```bash
# 检查网络
docker network ls
docker network inspect technical_analyst_quant-network

# 检查服务健康状态
curl http://localhost:8000/health
```

#### 4. 内存不足
```bash
# 清理Docker资源
docker system prune -f
docker volume prune -f
```

### 日志查看
```bash
# 查看所有服务日志
make logs

# 查看特定服务日志
docker-compose logs -f [service-name]

# 查看最近100行日志
docker-compose logs --tail=100 [service-name]
```

## 📞 技术支持

如遇到问题，请：
1. 查看服务日志
2. 检查服务状态
3. 参考故障排除部分
4. 联系技术支持团队

---

**最后更新**: 2024年1月15日
**版本**: 1.0.0 