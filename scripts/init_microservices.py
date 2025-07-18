#!/usr/bin/env python3
"""
微服务架构初始化脚本

用于创建完整的微服务目录结构和基础文件
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict
import shutil
import subprocess

class MicroserviceInitializer:
    """微服务架构初始化器"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.services = [
            'gateway',
            'core-service', 
            'data-service',
            'strategy-service',
            'notification-service',
            'web-service'
        ]
        
        # 目录结构定义
        self.directory_structure = {
            'shared': {
                'proto': [],
                'models': ['__init__.py', 'base.py', 'market_data.py', 'strategy.py', 'user.py', 'trade.py'],
                'utils': ['__init__.py', 'logger.py', 'config.py', 'validators.py', 'helpers.py', 'exceptions.py'],
                'files': ['requirements.txt']
            },
            'services': self._get_services_structure(),
            'infrastructure': {
                'docker': self._get_docker_structure(),
                'kubernetes': ['namespace.yaml'],
                'monitoring': {
                    'prometheus': ['prometheus.yml'],
                    'grafana': ['dashboards', 'datasources'],
                    'alertmanager': ['alertmanager.yml']
                },
                'databases': {
                    'postgresql': ['init.sql', 'schema'],
                    'redis': ['redis.conf'],
                    'timescaledb': ['init.sql']
                }
            },
            'tests': {
                'integration': ['test_api_gateway.py', 'test_service_communication.py', 'test_end_to_end.py'],
                'performance': ['test_load.py', 'test_stress.py', 'test_scalability.py'],
                'fixtures': ['test_data.json', 'mock_responses.json'],
                'utils': ['test_helpers.py', 'test_fixtures.py']
            },
            'tools': {
                'code_generators': ['service_template.py', 'api_template.py', 'model_template.py'],
                'migration_tools': ['data_migrator.py', 'schema_migrator.py', 'config_migrator.py'],
                'monitoring_tools': ['health_checker.py', 'log_analyzer.py', 'performance_profiler.py']
            },
            'legacy': {
                'src': [],
                'web': [],
                'config': [],
                'examples': []
            },
            'deployment': {
                'environments': {
                    'development': ['docker-compose.yml', '.env'],
                    'staging': ['docker-compose.yml', '.env'],
                    'production': ['docker-compose.yml', '.env']
                },
                'ci-cd': {
                    '.github/workflows': ['test.yml', 'build.yml', 'deploy.yml'],
                    'jenkins': ['Jenkinsfile']
                },
                'backup': ['database', 'config']
            }
        }
    
    def _get_services_structure(self) -> Dict:
        """获取微服务目录结构"""
        common_service_structure = {
            'app': {
                '__init__.py': '',
                'main.py': '',
                'api': ['__init__.py'],
                'core': ['__init__.py'],
                'models': ['__init__.py'],
                'services': ['__init__.py'],
                'database': ['__init__.py', 'connection.py', 'migrations']
            },
            'tests': [],
            'config': [],
            'logs': [],
            'files': ['Dockerfile', 'requirements.txt']
        }
        
        # 为每个服务生成结构
        services_structure = {}
        for service in self.services:
            services_structure[service] = common_service_structure.copy()
            
            # 为特定服务添加特殊目录
            if service == 'gateway':
                services_structure[service]['app']['middleware'] = ['__init__.py', 'auth.py', 'rate_limit.py', 'cors.py']
                services_structure[service]['app']['routes'] = ['__init__.py', 'core.py', 'data.py', 'strategy.py', 'notification.py']
            elif service == 'data-service':
                services_structure[service]['app']['fetchers'] = ['__init__.py', 'eastmoney_fetcher.py', 'tushare_fetcher.py', 'tencent_fetcher.py', 'multi_source_fetcher.py']
                services_structure[service]['app']['processors'] = ['__init__.py', 'data_cleaner.py', 'feature_calculator.py', 'data_validator.py']
                services_structure[service]['app']['storage'] = ['__init__.py', 'timeseries_db.py', 'cache_manager.py', 'file_storage.py']
                services_structure[service]['data'] = ['cache', 'historical', 'temp']
            elif service == 'strategy-service':
                services_structure[service]['app']['strategies'] = ['__init__.py', 'base_strategy.py', 'momentum_strategy.py', 'ml_strategy.py', 'custom_strategy.py']
                services_structure[service]['app']['ml'] = {
                    '__init__.py': '',
                    'feature_engine.py': '',
                    'model_trainer.py': '',
                    'predictor.py': '',
                    'models': ['lstm_model.py', 'random_forest.py', 'xgboost_model.py']
                }
                services_structure[service]['app']['backtesting'] = ['__init__.py', 'backtest_engine.py', 'performance_analyzer.py', 'report_generator.py']
                services_structure[service]['models'] = ['momentum', 'ml_enhanced', 'custom']
            elif service == 'web-service':
                services_structure[service]['app']['static'] = ['css', 'js', 'images']
                services_structure[service]['app']['templates'] = ['dashboard.html', 'trading.html', 'base.html']
                services_structure[service]['frontend'] = {
                    'src': {
                        'components': ['Dashboard', 'Trading', 'Strategy', 'Account', 'Common'],
                        'pages': ['DashboardPage.jsx', 'TradingPage.jsx', 'StrategyPage.jsx', 'AccountPage.jsx'],
                        'services': ['api.js', 'websocket.js', 'auth.js'],
                        'store': {
                            'slices': ['authSlice.js', 'tradingSlice.js', 'strategySlice.js'],
                            'files': ['index.js']
                        },
                        'utils': ['helpers.js', 'constants.js'],
                        'files': ['main.jsx', 'App.jsx']
                    },
                    'public': [],
                    'dist': [],
                    'files': ['package.json', 'package-lock.json', 'vite.config.js']
                }
            elif service == 'notification-service':
                services_structure[service]['app']['providers'] = ['__init__.py', 'email_provider.py', 'sms_provider.py', 'webhook_provider.py', 'push_provider.py']
                services_structure[service]['app']['templates'] = {
                    'email': ['trade_alert.html', 'daily_report.html', 'system_alert.html'],
                    'sms': ['trade_alert.txt', 'system_alert.txt']
                }
        
        return services_structure
    
    def _get_docker_structure(self) -> Dict:
        """获取Docker配置结构"""
        docker_structure = {}
        for service in self.services:
            docker_structure[service] = ['Dockerfile']
        docker_structure['nginx'] = ['Dockerfile', 'nginx.conf']
        return docker_structure
    
    def create_directory_structure(self):
        """创建完整的目录结构"""
        print("🏗️  开始创建微服务目录结构...")
        
        # 创建根级目录和文件
        root_files = [
            'docker-compose.yml',
            'docker-compose.prod.yml', 
            '.env.example',
            'Makefile'
        ]
        
        for file in root_files:
            self._create_file(self.base_path / file)
            
        # 递归创建目录结构
        self._create_structure(self.base_path, self.directory_structure)
        
        print("✅ 目录结构创建完成！")
    
    def _create_structure(self, base_path: Path, structure: Dict):
        """递归创建目录结构"""
        for name, content in structure.items():
            current_path = base_path / name
            
            if isinstance(content, dict):
                # 创建目录
                current_path.mkdir(parents=True, exist_ok=True)
                
                # 处理特殊的 'files' 键
                if 'files' in content:
                    for file in content['files']:
                        self._create_file(current_path / file)
                    # 移除 'files' 键，避免递归处理
                    content_copy = {k: v for k, v in content.items() if k != 'files'}
                    if content_copy:
                        self._create_structure(current_path, content_copy)
                else:
                    self._create_structure(current_path, content)
                    
            elif isinstance(content, list):
                # 创建目录
                current_path.mkdir(parents=True, exist_ok=True)
                
                # 创建文件
                for item in content:
                    if isinstance(item, str):
                        if '.' in item:  # 文件
                            self._create_file(current_path / item)
                        else:  # 子目录
                            (current_path / item).mkdir(parents=True, exist_ok=True)
            elif isinstance(content, str):
                # 直接创建文件
                self._create_file(current_path, content)
    
    def _create_file(self, file_path: Path, content: str = ""):
        """创建文件并写入内容"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def create_basic_templates(self):
        """创建基础模板文件"""
        print("📝 创建基础模板文件...")
        
        # 创建共享模型
        self._create_shared_models()
        
        # 创建共享工具
        self._create_shared_utils()
        
        # 创建服务模板
        self._create_service_templates()
        
        # 创建Docker模板
        self._create_docker_templates()
        
        # 创建配置文件
        self._create_config_templates()
        
        print("✅ 基础模板文件创建完成！")
    
    def _create_shared_models(self):
        """创建共享数据模型"""
        models_path = self.base_path / 'shared' / 'models'
        
        # base.py
        base_model = '''"""
共享基础数据模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """基础实体模型"""
    id: Optional[int] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
'''
        self._create_file(models_path / 'base.py', base_model)
        
        # market_data.py
        market_data_model = '''"""
市场数据模型
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from .base import BaseEntity


class StockData(BaseEntity):
    """股票数据模型"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: Decimal = Field(..., description="当前价格")
    change: Decimal = Field(..., description="涨跌额")
    change_percent: Decimal = Field(..., description="涨跌幅")
    volume: int = Field(..., description="成交量")
    amount: Decimal = Field(..., description="成交额")
    market: str = Field(..., description="市场标识")
    timestamp: datetime = Field(..., description="数据时间戳")


class KLineData(BaseEntity):
    """K线数据模型"""
    symbol: str = Field(..., description="股票代码")
    open_price: Decimal = Field(..., description="开盘价")
    close_price: Decimal = Field(..., description="收盘价")
    high_price: Decimal = Field(..., description="最高价")
    low_price: Decimal = Field(..., description="最低价")
    volume: int = Field(..., description="成交量")
    amount: Decimal = Field(..., description="成交额")
    date: datetime = Field(..., description="交易日期")
'''
        self._create_file(models_path / 'market_data.py', market_data_model)
    
    def _create_shared_utils(self):
        """创建共享工具类"""
        utils_path = self.base_path / 'shared' / 'utils'
        
        # logger.py
        logger_util = '''"""
统一日志工具
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class Logger:
    """统一日志管理器"""
    
    def __init__(self, name: str, level: str = "INFO", log_file: str = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: str = None):
        """设置日志处理器"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)


def get_logger(name: str) -> Logger:
    """获取日志器实例"""
    return Logger(name)
'''
        self._create_file(utils_path / 'logger.py', logger_util)
        
        # exceptions.py
        exceptions_util = '''"""
统一异常处理
"""


class QuantSystemException(Exception):
    """量化系统基础异常"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class DataFetchException(QuantSystemException):
    """数据获取异常"""
    pass


class StrategyException(QuantSystemException):
    """策略执行异常"""
    pass


class ConfigException(QuantSystemException):
    """配置异常"""
    pass


class ValidationException(QuantSystemException):
    """数据验证异常"""
    pass
'''
        self._create_file(utils_path / 'exceptions.py', exceptions_util)
    
    def _create_service_templates(self):
        """创建服务模板"""
        for service in self.services:
            self._create_service_main(service)
            self._create_service_dockerfile(service)
            self._create_service_requirements(service)
    
    def _create_service_main(self, service: str):
        """创建服务主文件"""
        main_path = self.base_path / 'services' / service / 'app' / 'main.py'
        
        main_template = f'''"""
{service} 微服务主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# 添加共享模块路径
shared_path = Path(__file__).parent.parent.parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from utils.logger import get_logger

logger = get_logger(f"{service}")

app = FastAPI(
    title="{service.title()} Service",
    description="{service} 微服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """服务启动事件"""
    logger.info(f"{service} service started")


@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭事件"""
    logger.info(f"{service} service shutdown")


@app.get("/")
async def root():
    """根路径"""
    return {{"message": f"{service} service is running"}}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {{"status": "healthy", "service": "{service}"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        self._create_file(main_path, main_template)
    
    def _create_service_dockerfile(self, service: str):
        """创建服务Dockerfile"""
        dockerfile_path = self.base_path / 'services' / service / 'Dockerfile'
        
        dockerfile_template = f'''# {service} 微服务 Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# 复制共享依赖
COPY shared/ /app/shared/

# 复制服务文件
COPY services/{service}/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/{service}/ .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
        self._create_file(dockerfile_path, dockerfile_template)
    
    def _create_service_requirements(self, service: str):
        """创建服务依赖文件"""
        requirements_path = self.base_path / 'services' / service / 'requirements.txt'
        
        base_requirements = '''# 基础依赖
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

# 共享依赖
requests>=2.28.0
pyyaml>=6.0
python-dateutil>=2.8.0
'''
        
        # 为特定服务添加特殊依赖
        service_specific = {
            'data-service': '''
# 数据处理依赖
pandas>=1.5.0
numpy>=1.21.0
yfinance>=0.2.18
akshare>=1.17.0
redis>=5.0.1
''',
            'strategy-service': '''
# 策略和机器学习依赖
pandas>=1.5.0
numpy>=1.21.0
scikit-learn>=1.0.0
joblib>=1.1.0
''',
            'web-service': '''
# Web服务依赖
jinja2>=3.1.0
''',
            'gateway': '''
# 网关依赖
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
''',
            'notification-service': '''
# 通知服务依赖
aiosmtplib>=1.1.7
''',
            'core-service': '''
# 核心服务依赖
sqlalchemy==2.0.23
alembic==1.12.1
'''
        }
        
        requirements = base_requirements
        if service in service_specific:
            requirements += service_specific[service]
            
        self._create_file(requirements_path, requirements)
    
    def _create_docker_templates(self):
        """创建Docker配置文件"""
        # docker-compose.yml
        compose_template = '''version: '3.8'

services:
  gateway:
    build: 
      context: .
      dockerfile: services/gateway/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=development
    depends_on:
      - redis
      - postgres

  core-service:
    build:
      context: .
      dockerfile: services/core-service/Dockerfile
    ports:
      - "8001:8000"
    environment:
      - ENVIRONMENT=development
    depends_on:
      - postgres

  data-service:
    build:
      context: .
      dockerfile: services/data-service/Dockerfile
    ports:
      - "8002:8000"
    environment:
      - ENVIRONMENT=development
    depends_on:
      - redis
      - timescaledb

  strategy-service:
    build:
      context: .
      dockerfile: services/strategy-service/Dockerfile
    ports:
      - "8003:8000"
    environment:
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis

  notification-service:
    build:
      context: .
      dockerfile: services/notification-service/Dockerfile
    ports:
      - "8004:8000"
    environment:
      - ENVIRONMENT=development

  web-service:
    build:
      context: .
      dockerfile: services/web-service/Dockerfile
    ports:
      - "8005:8000"
    environment:
      - ENVIRONMENT=development
    volumes:
      - ./services/web-service/frontend/dist:/app/static

  # 数据库服务
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: quant_system
      POSTGRES_USER: quant_user
      POSTGRES_PASSWORD: quant_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: market_data
      POSTGRES_USER: market_user
      POSTGRES_PASSWORD: market_password
    ports:
      - "5433:5432"
    volumes:
      - timescale_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  timescale_data:
  redis_data:
'''
        self._create_file(self.base_path / 'docker-compose.yml', compose_template)
    
    def _create_config_templates(self):
        """创建配置文件模板"""
        # .env.example
        env_template = '''# 环境配置示例文件
# 复制为 .env 并修改相应配置

# 环境设置
ENVIRONMENT=development
DEBUG=true

# 数据库配置
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=quant_system
POSTGRES_USER=quant_user
POSTGRES_PASSWORD=quant_password

# 时序数据库配置
TIMESCALE_HOST=timescaledb
TIMESCALE_PORT=5432
TIMESCALE_DB=market_data
TIMESCALE_USER=market_user
TIMESCALE_PASSWORD=market_password

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# 数据源配置
TUSHARE_TOKEN=your_tushare_token_here
EASTMONEY_API_KEY=your_eastmoney_key_here

# JWT配置
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_email_password
'''
        self._create_file(self.base_path / '.env.example', env_template)
        
        # Makefile
        makefile_template = '''# 微服务架构管理Makefile

.PHONY: help build up down logs test clean install

help: ## 显示帮助信息
	@echo "可用命令："
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \\033[36m%-15s\\033[0m %s\\n", $$1, $$2}'

install: ## 安装开发环境
	@echo "🔧 安装开发环境..."
	pip install -r requirements-dev.txt
	@echo "✅ 开发环境安装完成"

build: ## 构建所有服务
	@echo "🏗️  构建所有微服务..."
	docker-compose build
	@echo "✅ 构建完成"

up: ## 启动所有服务
	@echo "🚀 启动所有微服务..."
	docker-compose up -d
	@echo "✅ 服务启动完成"

down: ## 停止所有服务
	@echo "⏹️  停止所有微服务..."
	docker-compose down
	@echo "✅ 服务停止完成"

logs: ## 查看服务日志
	docker-compose logs -f

test: ## 运行测试
	@echo "🧪 运行测试..."
	python -m pytest tests/ -v
	@echo "✅ 测试完成"

clean: ## 清理容器和卷
	@echo "🧹 清理容器和数据卷..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ 清理完成"

dev-up: ## 启动开发环境（仅数据库服务）
	@echo "🔧 启动开发环境..."
	docker-compose up -d postgres timescaledb redis
	@echo "✅ 开发环境就绪"

migrate: ## 运行数据库迁移
	@echo "📊 运行数据库迁移..."
	# 这里添加数据库迁移命令
	@echo "✅ 迁移完成"
'''
        self._create_file(self.base_path / 'Makefile', makefile_template)
    
    def move_legacy_code(self):
        """移动现有代码到legacy目录"""
        print("📦 移动现有代码到legacy目录...")
        
        legacy_path = self.base_path / 'legacy'
        
        # 要移动的目录列表
        dirs_to_move = ['src', 'web', 'examples']
        
        for dir_name in dirs_to_move:
            source_path = self.base_path / dir_name
            if source_path.exists() and source_path.is_dir():
                target_path = legacy_path / dir_name
                
                # 如果目标目录已存在，先删除
                if target_path.exists():
                    shutil.rmtree(target_path)
                
                # 移动目录
                shutil.move(str(source_path), str(target_path))
                print(f"  ✅ 移动 {dir_name} -> legacy/{dir_name}")
        
        print("✅ 遗留代码移动完成！")
    
    def create_init_script(self):
        """创建项目初始化脚本"""
        init_script_path = self.base_path / 'scripts' / 'init_microservices_env.py'
        
        init_script_content = '''#!/usr/bin/env python3
"""
微服务项目初始化脚本
运行此脚本来快速设置开发环境
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示进度"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 开始初始化微服务项目...")
    
    # 检查Docker
    if not run_command("docker --version", "检查Docker"):
        print("请先安装Docker")
        return
    
    # 复制环境配置
    if Path(".env").exists():
        print("✅ .env文件已存在")
    else:
        run_command("cp .env.example .env", "复制环境配置文件")
    
    # 启动基础服务（数据库等）
    run_command("make dev-up", "启动开发环境基础服务")
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    import time
    time.sleep(10)
    
    print("🎉 微服务项目初始化完成！")
    print("📝 下一步操作：")
    print("  1. 检查 .env 文件配置")
    print("  2. 运行 'make up' 启动所有服务")
    print("  3. 访问 http://localhost:8000 查看API网关")


if __name__ == "__main__":
    main()
'''
        self._create_file(init_script_path, init_script_content)
        
        # 设置执行权限
        os.chmod(init_script_path, 0o755)
    
    def run_full_initialization(self, move_legacy: bool = False):
        """运行完整初始化"""
        print("🚀 开始微服务架构完整初始化...")
        print("=" * 60)
        
        try:
            # 1. 创建目录结构
            self.create_directory_structure()
            print()
            
            # 2. 创建基础模板
            self.create_basic_templates()
            print()
            
            # 3. 移动遗留代码（可选）
            if move_legacy:
                self.move_legacy_code()
                print()
            
            # 4. 创建初始化脚本
            self.create_init_script()
            print()
            
            print("🎉 微服务架构初始化完成！")
            print("=" * 60)
            print("📁 创建的主要目录：")
            print("  📂 services/           - 微服务目录")
            print("  📂 shared/             - 共享组件")
            print("  📂 infrastructure/     - 基础设施配置")
            print("  📂 tests/              - 测试文件")
            print("  📂 tools/              - 开发工具")
            print("  📂 deployment/         - 部署配置")
            if move_legacy:
                print("  📂 legacy/             - 遗留代码")
            print()
            print("📋 下一步操作：")
            print("  1. 检查并修改 .env.example -> .env")
            print("  2. 运行 'python scripts/init_microservices_env.py' 初始化环境")
            print("  3. 运行 'make dev-up' 启动开发环境")
            print("  4. 开始迁移业务代码到对应的微服务")
            
        except Exception as e:
            print(f"❌ 初始化过程中出现错误：{e}")
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="微服务架构初始化工具")
    parser.add_argument("--move-legacy", action="store_true", 
                       help="是否移动现有代码到legacy目录")
    parser.add_argument("--path", type=str, default=".", 
                       help="项目根目录路径")
    
    args = parser.parse_args()
    
    # 确认操作
    if args.move_legacy:
        confirm = input("⚠️  是否确认移动现有代码到legacy目录？这将影响现有的src/web/examples目录 (y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            return
    
    base_path = Path(args.path).resolve()
    print(f"📁 项目路径: {base_path}")
    
    initializer = MicroserviceInitializer(base_path)
    initializer.run_full_initialization(move_legacy=args.move_legacy)


if __name__ == "__main__":
    main()
