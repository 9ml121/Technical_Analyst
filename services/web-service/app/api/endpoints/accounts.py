"""
账户相关API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.database import get_db
from app.models.account import SimulatedAccount, SimulatedPosition
from app.models.trade import SimulatedTrade
from app.services.account_service import AccountService
from app.schemas.account import (
    AccountResponse, AccountCreate, AccountUpdate,
    PositionResponse, AccountSummary
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取账户列表"""
    try:
        accounts = db.query(SimulatedAccount).offset(skip).limit(limit).all()
        return accounts
    except Exception as e:
        logger.error(f"获取账户列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取账户列表失败"
        )

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """获取单个账户信息"""
    try:
        account = db.query(SimulatedAccount).filter(
            SimulatedAccount.id == account_id
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="账户不存在"
            )
        
        return account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取账户信息失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取账户信息失败"
        )

@router.get("/{account_id}/summary", response_model=AccountSummary)
async def get_account_summary(
    account_id: int,
    db: Session = Depends(get_db)
):
    """获取账户概要信息"""
    try:
        account_service = AccountService(db)
        summary = await account_service.get_account_summary(account_id)
        return summary
    except Exception as e:
        logger.error(f"获取账户概要失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取账户概要失败"
        )

@router.get("/{account_id}/positions", response_model=List[PositionResponse])
async def get_account_positions(
    account_id: int,
    db: Session = Depends(get_db)
):
    """获取账户持仓"""
    try:
        positions = db.query(SimulatedPosition).filter(
            SimulatedPosition.account_id == account_id
        ).all()
        
        return positions
    except Exception as e:
        logger.error(f"获取账户持仓失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取账户持仓失败"
        )

@router.get("/{account_id}/trades")
async def get_account_trades(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    side: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取账户交易记录"""
    try:
        query = db.query(SimulatedTrade).filter(
            SimulatedTrade.account_id == account_id
        )
        
        if symbol:
            query = query.filter(SimulatedTrade.symbol == symbol)
        
        if side:
            query = query.filter(SimulatedTrade.side == side)
        
        trades = query.order_by(
            SimulatedTrade.trade_time.desc()
        ).offset(skip).limit(limit).all()
        
        return trades
    except Exception as e:
        logger.error(f"获取交易记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取交易记录失败"
        )

@router.post("/", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """创建新账户"""
    try:
        account_service = AccountService(db)
        new_account = await account_service.create_account(account)
        return new_account
    except Exception as e:
        logger.error(f"创建账户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建账户失败"
        )

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """更新账户信息"""
    try:
        account_service = AccountService(db)
        updated_account = await account_service.update_account(
            account_id, account_update
        )
        return updated_account
    except Exception as e:
        logger.error(f"更新账户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新账户失败"
        )

@router.post("/{account_id}/reset")
async def reset_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """重置账户"""
    try:
        account_service = AccountService(db)
        await account_service.reset_account(account_id)
        return {"message": "账户重置成功"}
    except Exception as e:
        logger.error(f"重置账户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="重置账户失败"
        )

@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    """删除账户"""
    try:
        account = db.query(SimulatedAccount).filter(
            SimulatedAccount.id == account_id
        ).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="账户不存在"
            )
        
        db.delete(account)
        db.commit()
        
        return {"message": "账户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除账户失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除账户失败"
        )
