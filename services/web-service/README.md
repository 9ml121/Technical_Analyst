# Web Service 微服务

Technical_Analyst 系统的Web界面微服务，提供用户交互界面和API接口。

## 功能特性

- 🎨 **现代化前端界面** - 基于React + Ant Design的响应式界面
- 📊 **实时数据展示** - WebSocket实时推送市场数据和交易信息
- 🔄 **微服务架构** - 通过API网关与其他微服务通信
- 📱 **移动端适配** - 支持移动设备访问
- 🔐 **安全认证** - 集成用户认证和权限管理

## 技术栈

### 前端
- React 19.1.0
- Ant Design 5.26.5
- ECharts 5.6.0 (数据可视化)
- Vite 7.0.4 (构建工具)
- Axios 1.10.0 (HTTP客户端)

### 后端
- FastAPI 0.104.1
- SQLAlchemy 2.0.23 (ORM)
- Redis 5.0.1 (缓存)
- WebSocket (实时通信)

## 项目结构

```
web-service/
├── frontend/                 # 前端代码
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── services/        # API服务
│   │   └── assets/          # 静态资源
│   ├── package.json
│   └── vite.config.js
├── app/                     # 后端代码
│   ├── api/                 # API路由
│   ├── core/                # 核心配置
│   ├── models/              # 数据模型
│   ├── services/            # 业务服务
│   └── main.py              # 应用入口
├── config/                  # 配置文件
├── Dockerfile               # 容器配置
└── requirements.txt         # Python依赖
```

## 快速开始

### 本地开发

1. **安装前端依赖**
```bash
cd frontend
npm install
```

2. **启动前端开发服务器**
```bash
npm run dev
```

3. **安装后端依赖**
```bash
pip install -r requirements.txt
```

4. **启动后端服务**
```bash
uvicorn app.main:app --reload --port 8000
```

### Docker部署

1. **构建镜像**
```bash
docker build -t technical-analyst-web-service .
```

2. **运行容器**
```bash
docker run -p 8005:8000 technical-analyst-web-service
```

### 使用Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs web-service
```

## API接口

### 账户管理
- `GET /api/v1/core/accounts/` - 获取账户列表
- `GET /api/v1/core/accounts/{id}/summary` - 获取账户摘要
- `GET /api/v1/core/accounts/{id}/positions` - 获取持仓信息

### 市场数据
- `GET /api/v1/data/market/realtime/indices` - 获取实时指数
- `GET /api/v1/data/market/stats` - 获取市场统计
- `GET /api/v1/data/market/overview` - 获取市场概览

### 策略管理
- `GET /api/v1/strategy/strategies/` - 获取策略列表
- `POST /api/v1/strategy/strategies/{id}/start` - 启动策略
- `POST /api/v1/strategy/strategies/{id}/stop` - 停止策略

### 交易管理
- `GET /api/v1/core/trades/` - 获取交易记录
- `POST /api/v1/core/trades/order` - 创建订单

### WebSocket
- `WS /ws/{client_id}` - WebSocket连接

## 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务监听地址 |
| `PORT` | `8000` | 服务端口 |
| `DEBUG` | `False` | 调试模式 |
| `DATABASE_URL` | `postgresql://...` | 数据库连接 |
| `REDIS_URL` | `redis://...` | Redis连接 |
| `GATEWAY_URL` | `http://gateway:8080` | API网关地址 |

### 微服务通信

Web Service通过以下端点与其他微服务通信：

- **Core Service**: `/core` - 核心业务逻辑
- **Data Service**: `/data` - 数据获取服务
- **Strategy Service**: `/strategy` - 策略管理
- **Notification Service**: `/notification` - 通知服务

## 开发指南

### 添加新页面

1. 在 `frontend/src/pages/` 创建新组件
2. 在 `frontend/src/App.jsx` 添加路由
3. 在 `frontend/src/services/api.js` 添加API调用

### 添加新API

1. 在 `app/api/endpoints/` 创建新端点
2. 在 `app/api/__init__.py` 注册路由
3. 更新前端API服务

### 样式定制

- 全局样式：`frontend/src/index.css`
- 组件样式：`frontend/src/App.css`
- Ant Design主题：在 `App.jsx` 中配置

## 监控和日志

### 健康检查
```bash
curl http://localhost:8005/health
```

### 日志查看
```bash
# Docker日志
docker-compose logs web-service

# 本地日志
tail -f logs/web-service.log
```

## 故障排除

### 常见问题

1. **前端构建失败**
   - 检查Node.js版本 (>=18)
   - 清理node_modules重新安装

2. **后端启动失败**
   - 检查Python版本 (>=3.11)
   - 确认数据库连接正常

3. **API调用失败**
   - 检查微服务是否正常运行
   - 确认API网关配置正确

### 调试模式

设置环境变量启用调试：
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

MIT License 