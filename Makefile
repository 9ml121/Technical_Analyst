# 微服务架构 Makefile

.PHONY: help dev-up dev-down build logs clean

help:
	@echo "可用命令："
	@echo "  make dev-up     # 启动全部微服务（需 docker-compose.yml）"
	@echo "  make dev-down   # 停止全部微服务"
	@echo "  make build      # 构建全部微服务镜像"
	@echo "  make logs       # 查看全部服务日志"
	@echo "  make clean      # 清理构建和缓存"

# 启动全部微服务

dev-up:
	docker-compose up -d

# 停止全部微服务

dev-down:
	docker-compose down

# 构建全部微服务镜像

build:
	docker-compose build

# 查看全部服务日志

logs:
	docker-compose logs -f

# 清理构建和缓存

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f
