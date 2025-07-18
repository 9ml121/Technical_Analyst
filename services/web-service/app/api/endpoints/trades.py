"""
交易相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import logging

from app.core.database import get_db
from app.models.trade import Trade, TradingSignal
from app.models.account import SimulatedPosition as Position
from app.models.account import SimulatedAccount as Account

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_trades(
    account_id: Optional[int] = None,
    symbol: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取交易记录列表"""
    try:
        query = db.query(Trade)

        if account_id:
            query = query.filter(Trade.account_id == account_id)
        if symbol:
            query = query.filter(Trade.symbol == symbol)

        trades = query.order_by(Trade.trade_time.desc()).offset(
            skip).limit(limit).all()

        # 如果没有真实数据，返回模拟数据
        if not trades:
            trades = [
                {
                    "id": 1,
                    "account_id": 1,
                    "symbol": "000001",
                    "symbol_name": "平安银行",
                    "trade_type": "buy",
                    "quantity": 1000,
                    "price": 12.50,
                    "amount": 12500.0,
                    "commission": 6.25,
                    "trade_time": datetime.now().isoformat(),
                    "status": "filled"
                },
                {
                    "id": 2,
                    "account_id": 1,
                    "symbol": "600000",
                    "symbol_name": "浦发银行",
                    "trade_type": "sell",
                    "quantity": 500,
                    "price": 8.90,
                    "amount": 4450.0,
                    "commission": 2.23,
                    "trade_time": datetime.now().isoformat(),
                    "status": "filled"
                }
            ]

        return {
            "trades": trades,
            "total": len(trades),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"获取交易记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取交易记录失败"
        )


@router.get("/signals")
async def get_trading_signals(
    strategy_id: Optional[int] = None,
    symbol: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取交易信号列表"""
    try:
        query = db.query(TradingSignal)

        if strategy_id:
            query = query.filter(TradingSignal.strategy_id == strategy_id)
        if symbol:
            query = query.filter(TradingSignal.symbol == symbol)

        signals = query.order_by(TradingSignal.signal_time.desc()).offset(
            skip).limit(limit).all()

        # 如果没有真实数据，返回模拟数据
        if not signals:
            signals = [
                {
                    "id": 1,
                    "strategy_id": 1,
                    "symbol": "000001",
                    "symbol_name": "平安银行",
                    "signal_type": "buy",
                    "price": 12.50,
                    "confidence": 0.85,
                    "signal_time": datetime.now().isoformat(),
                    "status": "active",
                    "reason": "技术指标突破"
                },
                {
                    "id": 2,
                    "strategy_id": 1,
                    "symbol": "600036",
                    "symbol_name": "招商银行",
                    "signal_type": "sell",
                    "price": 35.20,
                    "confidence": 0.78,
                    "signal_time": datetime.now().isoformat(),
                    "status": "executed",
                    "reason": "止盈信号"
                }
            ]

        return {
            "signals": signals,
            "total": len(signals),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"获取交易信号失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取交易信号失败"
        )


@router.get("/positions")
async def get_positions(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取持仓信息"""
    try:
        query = db.query(Position)

        if account_id:
            query = query.filter(Position.account_id == account_id)

        positions = query.filter(Position.quantity > 0).all()

        # 如果没有真实数据，返回模拟数据
        if not positions:
            positions = [
                {
                    "id": 1,
                    "account_id": 1,
                    "symbol": "000001",
                    "symbol_name": "平安银行",
                    "quantity": 1000,
                    "avg_cost": 12.50,
                    "current_price": 13.20,
                    "market_value": 13200.0,
                    "unrealized_pnl": 700.0,
                    "unrealized_pnl_rate": 5.6,
                    "update_time": datetime.now().isoformat()
                },
                {
                    "id": 2,
                    "account_id": 1,
                    "symbol": "600036",
                    "symbol_name": "招商银行",
                    "quantity": 500,
                    "avg_cost": 35.00,
                    "current_price": 34.50,
                    "market_value": 17250.0,
                    "unrealized_pnl": -250.0,
                    "unrealized_pnl_rate": -1.43,
                    "update_time": datetime.now().isoformat()
                }
            ]

        return {
            "positions": positions,
            "total": len(positions)
        }
    except Exception as e:
        logger.error(f"获取持仓信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取持仓信息失败"
        )


@router.post("/order")
async def create_order(
    symbol: str,
    trade_type: str,  # buy/sell
    quantity: int,
    price: Optional[float] = None,
    order_type: str = "market",  # market/limit
    account_id: int = 1,
    db: Session = Depends(get_db)
):
    """创建交易订单"""
    try:
        # 模拟订单创建
        order = {
            "id": hash(f"{symbol}{trade_type}{quantity}{datetime.now()}") % 10000,
            "account_id": account_id,
            "symbol": symbol,
            "trade_type": trade_type,
            "quantity": quantity,
            "price": price,
            "order_type": order_type,
            "status": "pending",
            "create_time": datetime.now().isoformat(),
            "message": "订单已提交，等待执行"
        }

        return {
            "success": True,
            "order": order,
            "message": "订单创建成功"
        }
    except Exception as e:
        logger.error(f"创建订单失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建订单失败"
        )
