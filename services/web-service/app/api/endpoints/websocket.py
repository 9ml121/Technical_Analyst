"""
WebSocket相关API端点
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
import asyncio
from datetime import datetime

from app.services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)
router = APIRouter()

# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()

@router.websocket("/connect/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket连接端点"""
    await websocket_manager.connect(websocket, client_id)

    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                await handle_websocket_message(client_id, message)
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": "无效的JSON格式",
                    "timestamp": datetime.now().isoformat()
                }, client_id)
            except Exception as e:
                logger.error(f"处理WebSocket消息失败: {e}")
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": "消息处理失败",
                    "timestamp": datetime.now().isoformat()
                }, client_id)

    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        logger.info(f"客户端 {client_id} 断开连接")

async def handle_websocket_message(client_id: str, message: dict):
    """处理WebSocket消息"""
    message_type = message.get("type")

    if message_type == "subscribe":
        # 订阅主题
        topics = message.get("topics", [])
        for topic in topics:
            await websocket_manager.subscribe(client_id, topic)

        await websocket_manager.send_personal_message({
            "type": "subscription_success",
            "topics": topics,
            "timestamp": datetime.now().isoformat()
        }, client_id)

    elif message_type == "unsubscribe":
        # 取消订阅
        topics = message.get("topics", [])
        for topic in topics:
            websocket_manager.unsubscribe(client_id, topic)

        await websocket_manager.send_personal_message({
            "type": "unsubscription_success",
            "topics": topics,
            "timestamp": datetime.now().isoformat()
        }, client_id)

    elif message_type == "ping":
        # 心跳检测
        await websocket_manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }, client_id)

    else:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": f"未知的消息类型: {message_type}",
            "timestamp": datetime.now().isoformat()
        }, client_id)

# 启动实时数据推送任务
async def start_realtime_data_push():
    """启动实时数据推送"""
    while True:
        try:
            # 模拟市场数据推送
            market_data = {
                "indices": [
                    {
                        "code": "000001",
                        "name": "上证指数",
                        "current": 2956.85 + (hash(str(datetime.now().second)) % 20 - 10) * 0.1,
                        "change": 15.23 + (hash(str(datetime.now().second)) % 10 - 5) * 0.1,
                        "change_percent": 0.52 + (hash(str(datetime.now().second)) % 10 - 5) * 0.01
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }

            await websocket_manager.send_market_data(market_data)

            # 模拟账户更新
            account_data = {
                "total_asset": 105000 + (hash(str(datetime.now().second)) % 1000 - 500),
                "today_profit": 1200 + (hash(str(datetime.now().second)) % 200 - 100),
                "timestamp": datetime.now().isoformat()
            }

            await websocket_manager.send_account_update(account_data)

        except Exception as e:
            logger.error(f"实时数据推送失败: {e}")

        # 每5秒推送一次
        await asyncio.sleep(5)

# 获取WebSocket管理器实例（供其他模块使用）
def get_websocket_manager() -> WebSocketManager:
    """获取WebSocket管理器实例"""
    return websocket_manager
