# Web Service Makefile

.PHONY: help install build test clean docker-build docker-run dev

# 默认目标
help:
	@echo "Web Service 可用命令:"
	@echo "  install      - 安装前端和后端依赖"
	@echo "  build        - 构建前端应用"
	@echo "  test         - 运行集成测试"
	@echo "  clean        - 清理构建文件"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run   - 运行Docker容器"
	@echo "  dev          - 启动开发环境"

# 安装依赖
install:
	@echo "📦 安装前端依赖..."
	cd frontend && npm install
	@echo "🐍 安装后端依赖..."
	pip install -r requirements.txt
	@echo "✅ 依赖安装完成"

# 构建前端
build:
	@echo "🔨 构建前端应用..."
	cd frontend && npm run build
	@echo "✅ 前端构建完成"

# 运行测试
test:
	@echo "🧪 运行集成测试..."
	python test-integration.py

# 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ 清理完成"

# 构建Docker镜像
docker-build:
	@echo "🐳 构建Docker镜像..."
	docker build -t technical-analyst-web-service .
	@echo "✅ Docker镜像构建完成"

# 运行Docker容器
docker-run:
	@echo "🚀 运行Docker容器..."
	docker run -d --name web-service-test -p 8005:8000 technical-analyst-web-service
	@echo "✅ 容器启动完成，访问 http://localhost:8005"

# 开发环境
dev:
	@echo "🚀 启动开发环境..."
	@echo "前端: http://localhost:3000"
	@echo "后端: http://localhost:8000"
	@echo "按 Ctrl+C 停止服务"
	@cd frontend && npm run dev & \
	uvicorn app.main:app --reload --port 8000 & \
	wait

# 停止开发环境
dev-stop:
	@echo "🛑 停止开发环境..."
	pkill -f "npm run dev" || true
	pkill -f "uvicorn" || true
	@echo "✅ 开发环境已停止"

# 完整构建流程
all: install build test
	@echo "🎉 完整构建流程完成！" 