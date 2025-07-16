"""
API路由包
"""

from fastapi import APIRouter

from .endpoints import (
    accounts, strategies, trades, market_data, 
    performance, websocket
)

# 创建主API路由
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(
    accounts.router, 
    prefix="/accounts", 
    tags=["accounts"]
)

api_router.include_router(
    strategies.router, 
    prefix="/strategies", 
    tags=["strategies"]
)

api_router.include_router(
    trades.router, 
    prefix="/trades", 
    tags=["trades"]
)

api_router.include_router(
    market_data.router, 
    prefix="/market", 
    tags=["market_data"]
)

api_router.include_router(
    performance.router, 
    prefix="/performance", 
    tags=["performance"]
)

api_router.include_router(
    websocket.router, 
    prefix="/ws", 
    tags=["websocket"]
)
