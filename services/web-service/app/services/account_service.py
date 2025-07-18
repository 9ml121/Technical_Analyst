"""
账户服务
"""

from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from datetime import datetime, date

from app.models.account import SimulatedAccount, SimulatedPosition
from app.models.trade import SimulatedTrade
from app.schemas.account import AccountCreate, AccountUpdate, AccountSummary
from app.core.config import settings

logger = logging.getLogger(__name__)

class AccountService:
    """账户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_account(self, account_data: AccountCreate) -> SimulatedAccount:
        """创建新账户"""
        try:
            # 创建账户实例
            account = SimulatedAccount(
                name=account_data.name,
                description=account_data.description,
                initial_capital=account_data.initial_capital,
                current_capital=account_data.initial_capital,
                available_capital=account_data.initial_capital,
                strategy_id=account_data.strategy_id,
                config=account_data.config or {}
            )
            
            # 更新总资产
            account.update_asset()
            
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            
            logger.info(f"创建账户成功: {account.name} (ID: {account.id})")
            return account
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建账户失败: {e}")
            raise
    
    async def update_account(self, account_id: int, account_data: AccountUpdate) -> SimulatedAccount:
        """更新账户信息"""
        try:
            account = self.db.query(SimulatedAccount).filter(
                SimulatedAccount.id == account_id
            ).first()
            
            if not account:
                raise ValueError("账户不存在")
            
            # 更新字段
            if account_data.name is not None:
                account.name = account_data.name
            if account_data.description is not None:
                account.description = account_data.description
            if account_data.status is not None:
                account.status = account_data.status
            if account_data.config is not None:
                account.config = account_data.config
            
            account.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(account)
            
            logger.info(f"更新账户成功: {account.name} (ID: {account.id})")
            return account
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新账户失败: {e}")
            raise
    
    async def get_account_summary(self, account_id: int) -> AccountSummary:
        """获取账户概要信息"""
        try:
            account = self.db.query(SimulatedAccount).filter(
                SimulatedAccount.id == account_id
            ).first()
            
            if not account:
                raise ValueError("账户不存在")
            
            # 获取持仓信息
            positions = self.db.query(SimulatedPosition).filter(
                SimulatedPosition.account_id == account_id
            ).all()
            
            # 获取交易统计
            trades = self.db.query(SimulatedTrade).filter(
                SimulatedTrade.account_id == account_id
            ).all()
            
            # 计算统计指标
            position_count = len(positions)
            position_ratio = account.position_ratio
            trade_count = len(trades)
            
            # 计算最大收益（这里简化处理，实际应该从历史数据计算）
            max_return = max(account.total_return_rate, account.today_return_rate)
            
            return AccountSummary(
                total_asset=account.total_asset,
                total_return=account.total_profit,
                total_return_rate=account.total_return_rate,
                today_return=account.today_profit,
                today_return_rate=account.today_return_rate,
                position_count=position_count,
                position_ratio=position_ratio,
                max_return=max_return,
                max_drawdown=account.max_drawdown,
                win_rate=account.win_rate,
                sharpe_ratio=account.sharpe_ratio,
                volatility=12.5,  # 这里应该从历史数据计算
                trade_count=trade_count
            )
            
        except Exception as e:
            logger.error(f"获取账户概要失败: {e}")
            raise
    
    async def reset_account(self, account_id: int):
        """重置账户"""
        try:
            account = self.db.query(SimulatedAccount).filter(
                SimulatedAccount.id == account_id
            ).first()
            
            if not account:
                raise ValueError("账户不存在")
            
            # 删除所有持仓
            self.db.query(SimulatedPosition).filter(
                SimulatedPosition.account_id == account_id
            ).delete()
            
            # 删除所有交易记录（可选，根据需求决定）
            # self.db.query(SimulatedTrade).filter(
            #     SimulatedTrade.account_id == account_id
            # ).delete()
            
            # 重置账户资金
            account.current_capital = account.initial_capital
            account.available_capital = account.initial_capital
            account.frozen_capital = 0
            account.total_market_value = 0
            account.total_profit = 0
            account.total_return_rate = 0
            account.today_profit = 0
            account.today_return_rate = 0
            account.max_drawdown = 0
            account.win_rate = 0
            account.sharpe_ratio = 0
            account.total_trades = 0
            account.win_trades = 0
            
            account.update_asset()
            account.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"重置账户成功: {account.name} (ID: {account.id})")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"重置账户失败: {e}")
            raise
    
    async def update_account_performance(self, account_id: int, market_data: dict):
        """更新账户表现（基于最新市场数据）"""
        try:
            account = self.db.query(SimulatedAccount).filter(
                SimulatedAccount.id == account_id
            ).first()
            
            if not account:
                return
            
            # 获取所有持仓
            positions = self.db.query(SimulatedPosition).filter(
                SimulatedPosition.account_id == account_id
            ).all()
            
            # 更新持仓市值
            total_market_value = 0
            for position in positions:
                if position.symbol in market_data:
                    current_price = market_data[position.symbol]['current_price']
                    position.update_market_value(current_price)
                    total_market_value += position.market_value
            
            # 更新账户信息
            account.total_market_value = total_market_value
            account.update_asset()
            
            # 计算收益
            account.total_profit = account.total_asset - account.initial_capital
            if account.initial_capital > 0:
                account.total_return_rate = (account.total_profit / account.initial_capital) * 100
            
            account.updated_at = datetime.utcnow()
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"更新账户表现失败: {e}")
            raise

    async def get_account_summary(self, account_id: int) -> AccountSummary:
        """获取账户概览信息"""
        try:
            # 获取账户信息
            account = self.db.query(SimulatedAccount).filter(
                SimulatedAccount.id == account_id
            ).first()

            if not account:
                raise ValueError("账户不存在")

            # 获取持仓数量
            position_count = self.db.query(SimulatedPosition).filter(
                SimulatedPosition.account_id == account_id
            ).count()

            # 计算仓位比例
            position_ratio = 0.0
            if account.total_asset > 0:
                position_ratio = (account.total_market_value / account.total_asset) * 100

            # 获取交易统计
            total_trades = account.total_trades or 0
            win_trades = account.win_trades or 0
            win_rate = account.win_rate or 0.0

            # 构建概览数据
            return AccountSummary(
                account_id=account.id,
                account_name=account.name,
                total_asset=account.total_asset or 0.0,
                total_profit=account.total_profit or 0.0,
                total_return_rate=account.total_return_rate or 0.0,
                today_profit=account.today_profit or 0.0,
                today_return_rate=account.today_return_rate or 0.0,
                position_count=position_count,
                position_ratio=position_ratio,
                total_trades=total_trades,
                win_trades=win_trades,
                win_rate=win_rate,
                max_drawdown=account.max_drawdown or 0.0,
                sharpe_ratio=account.sharpe_ratio or 0.0,
                status=account.status or "active",
                last_update=account.updated_at or account.created_at
            )

        except Exception as e:
            logger.error(f"获取账户概览失败: {e}")
            raise
