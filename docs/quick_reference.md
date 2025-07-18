# 微服务架构快速参考

## 🚀 快速命令

### 启动/停止
```bash
make dev-up          # 启动所有服务
make dev-down        # 停止所有服务
docker-compose ps    # 查看服务状态
```

### 日志查看
```bash
make logs            # 查看所有日志
docker-compose logs [service-name]  # 查看特定服务日志
```

### 构建
```bash
make build           # 重新构建所有服务
docker-compose build [service-name]  # 构建特定服务
```

## 🌐 访问地址

### API网关 (主入口)
- **主页**: http://localhost:8000/
- **健康检查**: http://localhost:8000/health
- **API文档**: http://localhost:8000/docs

### 各服务直接访问
- **核心服务**: http://localhost:8001/
- **数据服务**: http://localhost:8002/
- **策略服务**: http://localhost:8003/
- **通知服务**: http://localhost:8004/

### 各服务API文档
- **核心服务**: http://localhost:8001/docs
- **数据服务**: http://localhost:8002/docs
- **策略服务**: http://localhost:8003/docs
- **通知服务**: http://localhost:8004/docs

## 📞 常用API测试

### 通过网关访问
```bash
# 数据服务
curl http://localhost:8000/api/v1/data/api/v1/stocks/AAPL

# 核心服务
curl http://localhost:8000/api/v1/core/api/v1/analysis/AAPL

# 策略服务
curl http://localhost:8000/api/v1/strategy/api/v1/strategies

# 通知服务
curl http://localhost:8000/api/v1/notification/api/v1/notifications
```

### 直接访问
```bash
# 核心服务
curl http://localhost:8001/api/v1/analysis/AAPL

# 数据服务
curl http://localhost:8002/api/v1/stocks/AAPL

# 策略服务
curl http://localhost:8003/api/v1/strategies

# 通知服务
curl http://localhost:8004/api/v1/notifications
```

## 🔧 故障排除

### 服务状态检查
```bash
docker-compose ps                    # 查看所有服务状态
curl http://localhost:8000/health    # 检查网关和所有服务健康状态
```

### 常见问题
```bash
# 端口被占用
lsof -i :8000

# 清理Docker资源
docker system prune -f

# 重新构建特定服务
docker-compose build [service-name] && docker-compose up -d [service-name]
```

---

**详细文档**: [微服务架构使用指南](microservices_guide.md) 