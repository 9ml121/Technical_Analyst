"""
性能分析API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/account/{account_id}")
async def get_account_performance(
    account_id: int,
    time_frame: str = "week",
    db: Session = Depends(get_db)
):
    """获取账户表现数据"""
    try:
        # 模拟账户表现数据
        performance_data = {
            "account_id": account_id,
            "time_frame": time_frame,
            "total_return": 12.5,
            "annual_return": 15.8,
            "max_drawdown": -8.2,
            "sharpe_ratio": 1.45,
            "win_rate": 65.7,
            "profit_factor": 1.85,
            "daily_returns": [
                {"date": "2024-01-15", "return": 0.8},
                {"date": "2024-01-16", "return": -0.3},
                {"date": "2024-01-17", "return": 1.2},
                {"date": "2024-01-18", "return": 0.5},
                {"date": "2024-01-19", "return": -0.7}
            ],
            "monthly_returns": [
                {"month": "2023-12", "return": 3.2},
                {"month": "2024-01", "return": 2.8}
            ],
            "risk_metrics": {
                "volatility": 12.5,
                "beta": 0.85,
                "alpha": 2.3,
                "var_95": -2.1,
                "cvar_95": -3.2
            },
            "benchmark_comparison": {
                "benchmark": "沪深300",
                "account_return": 12.5,
                "benchmark_return": 8.3,
                "excess_return": 4.2,
                "tracking_error": 5.8
            }
        }

        return performance_data
    except Exception as e:
        logger.error(f"获取账户表现失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取账户表现失败"
        )

@router.get("/strategy/{strategy_id}")
async def get_strategy_performance(
    strategy_id: int,
    time_frame: str = "week",
    db: Session = Depends(get_db)
):
    """获取策略表现数据"""
    try:
        # 模拟策略表现数据
        performance_data = {
            "strategy_id": strategy_id,
            "strategy_name": "动量策略",
            "time_frame": time_frame,
            "total_return": 18.3,
            "annual_return": 22.1,
            "max_drawdown": -12.5,
            "sharpe_ratio": 1.68,
            "win_rate": 58.3,
            "profit_factor": 2.15,
            "total_trades": 156,
            "winning_trades": 91,
            "losing_trades": 65,
            "avg_win": 2.8,
            "avg_loss": -1.5,
            "largest_win": 8.5,
            "largest_loss": -4.2,
            "performance_chart": [
                {"date": "2024-01-01", "cumulative_return": 0.0},
                {"date": "2024-01-02", "cumulative_return": 1.2},
                {"date": "2024-01-03", "cumulative_return": 0.8},
                {"date": "2024-01-04", "cumulative_return": 2.1},
                {"date": "2024-01-05", "cumulative_return": 1.9}
            ],
            "monthly_performance": [
                {"month": "2023-12", "return": 4.5, "trades": 23},
                {"month": "2024-01", "return": 3.8, "trades": 28}
            ]
        }

        return performance_data
    except Exception as e:
        logger.error(f"获取策略表现失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取策略表现失败"
        )

@router.get("/comparison")
async def get_performance_comparison(
    account_ids: str,  # 逗号分隔的账户ID
    strategy_ids: Optional[str] = None,  # 逗号分隔的策略ID
    time_frame: str = "month",
    db: Session = Depends(get_db)
):
    """获取性能对比数据"""
    try:
        account_list = [int(id.strip()) for id in account_ids.split(",")]
        strategy_list = []
        if strategy_ids:
            strategy_list = [int(id.strip()) for id in strategy_ids.split(",")]

        # 模拟对比数据
        comparison_data = {
            "time_frame": time_frame,
            "accounts": [
                {
                    "account_id": account_id,
                    "name": f"账户{account_id}",
                    "total_return": 12.5 + account_id * 2,
                    "sharpe_ratio": 1.45 + account_id * 0.1,
                    "max_drawdown": -8.2 - account_id * 0.5
                }
                for account_id in account_list
            ],
            "strategies": [
                {
                    "strategy_id": strategy_id,
                    "name": f"策略{strategy_id}",
                    "total_return": 18.3 + strategy_id * 1.5,
                    "sharpe_ratio": 1.68 + strategy_id * 0.08,
                    "max_drawdown": -12.5 - strategy_id * 0.8
                }
                for strategy_id in strategy_list
            ],
            "benchmark": {
                "name": "沪深300",
                "total_return": 8.3,
                "sharpe_ratio": 0.95,
                "max_drawdown": -15.2
            }
        }

        return comparison_data
    except Exception as e:
        logger.error(f"获取性能对比失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取性能对比失败"
        )
