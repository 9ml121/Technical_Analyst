"""
数据服务主应用
提供股票数据获取的微服务
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from app.routes.data_routes import include_data_routes
from shared.utils.exceptions import DataSourceError, NetworkError

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="数据服务 API",
    description="提供股票数据获取的微服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理


@app.exception_handler(DataSourceError)
async def data_source_exception_handler(request, exc):
    """数据源异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": str(exc),
            "error_type": "DataSourceError",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    )


@app.exception_handler(NetworkError)
async def network_exception_handler(request, exc):
    """网络异常处理"""
    return JSONResponse(
        status_code=503,
        content={
            "success": False,
            "message": str(exc),
            "error_type": "NetworkError",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_type": "InternalServerError",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    )

# 根路径


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "数据服务",
        "version": "1.0.0",
        "status": "运行中",
        "description": "提供股票数据获取的微服务",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "stocks": "/api/v1/stocks/list",
            "history": "/api/v1/stocks/{code}/history"
        }
    }

# 包含数据路由
include_data_routes(app)

# 启动事件


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("数据服务启动中...")

    # 确保数据目录存在
    os.makedirs("./data", exist_ok=True)

    logger.info("数据服务启动完成")

# 关闭事件


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("数据服务关闭中...")

if __name__ == "__main__":
    import uvicorn

    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8002"))

    logger.info(f"启动数据服务: {host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
