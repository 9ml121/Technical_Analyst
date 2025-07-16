"""
WebSocket连接管理器
"""

from fastapi import WebSocket
from typing import Dict, List
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃连接
        self.active_connections: Dict[str, WebSocket] = {}
        # 订阅信息
        self.subscriptions: Dict[str, List[str]] = {}  # client_id -> [topics]
        # 主题订阅者
        self.topic_subscribers: Dict[str, List[str]] = {}  # topic -> [client_ids]
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = []
        
        logger.info(f"客户端 {client_id} 已连接，当前连接数: {len(self.active_connections)}")
        
        # 发送连接成功消息
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }, client_id)
    
    def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            # 清理订阅
            if client_id in self.subscriptions:
                topics = self.subscriptions[client_id]
                for topic in topics:
                    if topic in self.topic_subscribers:
                        self.topic_subscribers[topic].remove(client_id)
                        if not self.topic_subscribers[topic]:
                            del self.topic_subscribers[topic]
                del self.subscriptions[client_id]
            
            # 移除连接
            del self.active_connections[client_id]
            
            logger.info(f"客户端 {client_id} 已断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """发送个人消息"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception as e:
                logger.error(f"发送消息给客户端 {client_id} 失败: {e}")
                # 连接可能已断开，清理连接
                self.disconnect(client_id)
    
    async def broadcast_message(self, message: dict):
        """广播消息给所有连接"""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message, ensure_ascii=False)
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message_text)
            except Exception as e:
                logger.error(f"广播消息给客户端 {client_id} 失败: {e}")
                disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_to_topic(self, message: dict, topic: str):
        """发送消息给订阅特定主题的客户端"""
        if topic not in self.topic_subscribers:
            return
        
        message_text = json.dumps(message, ensure_ascii=False)
        disconnected_clients = []
        
        for client_id in self.topic_subscribers[topic]:
            if client_id in self.active_connections:
                try:
                    websocket = self.active_connections[client_id]
                    await websocket.send_text(message_text)
                except Exception as e:
                    logger.error(f"发送主题消息给客户端 {client_id} 失败: {e}")
                    disconnected_clients.append(client_id)
        
        # 清理断开的连接
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def subscribe_topic(self, client_id: str, topic: str):
        """订阅主题"""
        if client_id not in self.active_connections:
            return False
        
        # 添加到客户端订阅列表
        if client_id not in self.subscriptions:
            self.subscriptions[client_id] = []
        
        if topic not in self.subscriptions[client_id]:
            self.subscriptions[client_id].append(topic)
        
        # 添加到主题订阅者列表
        if topic not in self.topic_subscribers:
            self.topic_subscribers[topic] = []
        
        if client_id not in self.topic_subscribers[topic]:
            self.topic_subscribers[topic].append(client_id)
        
        logger.info(f"客户端 {client_id} 订阅主题: {topic}")
        
        # 发送订阅确认
        await self.send_personal_message({
            "type": "subscription",
            "action": "subscribed",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }, client_id)
        
        return True
    
    async def unsubscribe_topic(self, client_id: str, topic: str):
        """取消订阅主题"""
        if client_id not in self.subscriptions:
            return False
        
        # 从客户端订阅列表移除
        if topic in self.subscriptions[client_id]:
            self.subscriptions[client_id].remove(topic)
        
        # 从主题订阅者列表移除
        if topic in self.topic_subscribers and client_id in self.topic_subscribers[topic]:
            self.topic_subscribers[topic].remove(client_id)
            if not self.topic_subscribers[topic]:
                del self.topic_subscribers[topic]
        
        logger.info(f"客户端 {client_id} 取消订阅主题: {topic}")
        
        # 发送取消订阅确认
        await self.send_personal_message({
            "type": "subscription",
            "action": "unsubscribed", 
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        }, client_id)
        
        return True
    
    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.active_connections)
    
    def get_topic_subscriber_count(self, topic: str) -> int:
        """获取主题订阅者数量"""
        return len(self.topic_subscribers.get(topic, []))
    
    async def send_market_data(self, market_data: dict):
        """发送市场数据"""
        message = {
            "type": "market_data",
            "data": market_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_topic(message, "market_data")
    
    async def send_account_update(self, account_data: dict):
        """发送账户更新"""
        message = {
            "type": "account_update",
            "data": account_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_topic(message, "account_updates")
    
    async def send_trade_signal(self, signal_data: dict):
        """发送交易信号"""
        message = {
            "type": "trade_signal",
            "data": signal_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_to_topic(message, "trade_signals")

# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()
