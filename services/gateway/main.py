import logging
from fastapi import Request
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="API网关",
    description="量化投资系统API网关服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 微服务配置
SERVICES = {
    "data": "http://data-service:8002",
    "core": "http://core-service:8001",
    "strategy": "http://strategy-service:8003",
    "notification": "http://notification-service:8004"
}


@app.get("/")
async def root():
    return {
        "service": "API网关",
        "status": "运行中",
        "version": "1.0.0",
        "available_services": list(SERVICES.keys())
    }


@app.get("/health")
async def health_check():
    """网关健康检查"""
    health_status = {
        "status": "healthy",
        "service": "gateway",
        "services": {}
    }

    # 检查各个微服务的健康状态
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                health_status["services"][service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                health_status["services"][service_name] = "unreachable"

    return health_status


@app.api_route("/api/v1/data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_data_service(request: Request, path: str):
    """代理数据服务请求"""
    return await proxy_request(request, "data", path)


@app.api_route("/api/v1/core/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_core_service(request: Request, path: str):
    """代理核心服务请求"""
    return await proxy_request(request, "core", path)


@app.api_route("/api/v1/strategy/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_strategy_service(request: Request, path: str):
    """代理策略服务请求"""
    return await proxy_request(request, "strategy", path)


@app.api_route("/api/v1/notification/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_notification_service(request: Request, path: str):
    """代理通知服务请求"""
    return await proxy_request(request, "notification", path)


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def proxy_request(request: Request, service_name: str, path: str):
    """通用代理请求函数"""
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, detail=f"Service {service_name} not found")

    service_url = SERVICES[service_name]
    # 修正：始终加上/api/v1前缀
    target_url = f"{service_url}/api/v1/{path}"

    logger.info(f"代理请求: {request.method} {target_url}")

    # 获取请求体
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
        except:
            pass

    # 获取查询参数
    query_params = dict(request.query_params)

    try:
        async with httpx.AsyncClient() as client:
            if request.method == "GET":
                response = await client.get(target_url, params=query_params, timeout=10.0)
            elif request.method == "POST":
                response = await client.post(target_url, params=query_params, content=body, timeout=10.0)
            elif request.method == "PUT":
                response = await client.put(target_url, params=query_params, content=body, timeout=10.0)
            elif request.method == "DELETE":
                response = await client.delete(target_url, params=query_params, timeout=10.0)
            else:
                raise HTTPException(
                    status_code=405, detail=f"Method {request.method} not supported")

            logger.info(f"代理响应: {response.status_code}")
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"代理请求错误: {str(e)}")
        raise HTTPException(
            status_code=503, detail=f"Service {service_name} unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"网关错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
