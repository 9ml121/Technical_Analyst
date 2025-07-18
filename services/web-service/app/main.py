"""
Technical_Analyst Web Service
微服务架构中的Web界面服务
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List

from app.core.config import settings
from app.core.database import init_db
from app.api import api_router
from app.services.websocket_manager import WebSocketManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# WebSocket管理器
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动Technical_Analyst Web Service...")

    # 初始化数据库
    await init_db()
    logger.info("✅ 数据库初始化完成")

    # 启动实时数据服务
    from app.api.endpoints.websocket import start_realtime_data_push
    import asyncio

    # 在后台启动实时数据推送任务
    asyncio.create_task(start_realtime_data_push())
    logger.info("✅ 实时数据服务启动")

    yield

    # 关闭时清理
    logger.info("🛑 关闭Technical_Analyst Web Service...")

# 创建FastAPI应用
app = FastAPI(
    title="Technical_Analyst Web Service",
    description="量化投资系统Web界面微服务",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点（必须在静态文件挂载之前注册）


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "service": "web-service",
        "status": "healthy"
    }

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接端点"""
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            logger.info(f"收到客户端 {client_id} 消息: {data}")

            # 处理消息并广播
            await websocket_manager.send_personal_message(
                f"Echo: {data}", client_id
            )

    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        logger.info(f"客户端 {client_id} 断开连接")

# 静态文件服务 - 按优先级顺序挂载
# 挂载assets目录（JavaScript和CSS文件）
app.mount(
    "/assets", StaticFiles(directory="/app/frontend/dist/assets"), name="assets")

# 提供主页HTML文件


@app.get("/")
async def serve_index():
    """提供主页HTML文件"""
    from fastapi.responses import FileResponse
    return FileResponse("/app/frontend/dist/index.html")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
