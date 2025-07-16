"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG
    )

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """初始化数据库"""
    try:
        # 导入所有模型以确保它们被注册
        from app.models import (
            User, SimulatedAccount, SimulatedPosition, Strategy,
            SimulatedTrade, TradingSignal, MarketIndex, MarketStats,
            StockQuote, AccountPerformance, StrategyPerformance, BenchmarkPerformance
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 初始化基础数据
        await init_base_data()
        
        logger.info("✅ 数据库初始化成功")
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise

async def init_base_data():
    """初始化基础数据"""
    db = SessionLocal()
    try:
        from app.models import SimulatedAccount, Strategy
        
        # 检查是否已有默认账户
        default_account = db.query(SimulatedAccount).filter(
            SimulatedAccount.name == "默认模拟账户"
        ).first()
        
        if not default_account:
            # 创建默认模拟账户（带有测试数据）
            default_account = SimulatedAccount(
                name="默认模拟账户",
                initial_capital=100000.0,
                current_capital=85000.0,  # 已投入15000
                available_capital=85000.0,
                total_market_value=20000.0,  # 持仓市值
                total_asset=105000.0,  # 总资产
                total_profit=5000.0,  # 盈利5000
                total_return_rate=5.0,  # 收益率5%
                today_profit=1200.0,  # 今日盈利
                today_return_rate=1.2,  # 今日收益率
                total_trades=35,  # 总交易次数
                win_trades=23,  # 盈利交易次数
                win_rate=65.7,  # 胜率
                max_drawdown=-2.5,  # 最大回撤
                sharpe_ratio=1.85,  # 夏普比率
                status="active"
            )
            db.add(default_account)
            db.flush()  # 获取ID

            # 创建测试持仓数据
            from app.models.account import SimulatedPosition
            from datetime import datetime, timedelta

            test_positions = [
                {
                    "symbol": "000001",
                    "symbol_name": "平安银行",
                    "quantity": 1000,
                    "avg_cost": 12.50,
                    "current_price": 13.20
                },
                {
                    "symbol": "000002",
                    "symbol_name": "万科A",
                    "quantity": 500,
                    "avg_cost": 8.80,
                    "current_price": 9.15
                },
                {
                    "symbol": "600036",
                    "symbol_name": "招商银行",
                    "quantity": 200,
                    "avg_cost": 35.20,
                    "current_price": 36.80
                }
            ]

            for pos_data in test_positions:
                market_value = pos_data["quantity"] * pos_data["current_price"]
                cost_value = pos_data["quantity"] * pos_data["avg_cost"]
                unrealized_pnl = market_value - cost_value
                unrealized_pnl_rate = (unrealized_pnl / cost_value) * 100 if cost_value > 0 else 0

                position = SimulatedPosition(
                    account_id=default_account.id,
                    symbol=pos_data["symbol"],
                    symbol_name=pos_data["symbol_name"],
                    quantity=pos_data["quantity"],
                    avg_cost=pos_data["avg_cost"],
                    current_price=pos_data["current_price"],
                    market_value=market_value,
                    unrealized_pnl=unrealized_pnl,
                    unrealized_pnl_rate=unrealized_pnl_rate,
                    first_buy_date=datetime.now() - timedelta(days=15),
                    last_trade_date=datetime.now() - timedelta(days=3),
                    holding_days=15
                )
                db.add(position)
        
        # 检查是否已有默认策略
        default_strategy = db.query(Strategy).filter(
            Strategy.name == "动量策略"
        ).first()
        
        if not default_strategy:
            # 创建默认动量策略
            default_strategy = Strategy(
                name="动量策略",
                type="momentum",
                version="2.1",
                config={
                    "momentum_period": 20,
                    "buy_threshold": 5.0,
                    "sell_threshold": -3.0,
                    "max_positions": 10,
                    "max_position_size": 0.1,
                    "min_trade_amount": 10000
                },
                risk_config={
                    "stop_loss_rate": 5.0,
                    "take_profit_rate": 15.0,
                    "max_drawdown_limit": 10.0,
                    "max_holding_days": 30
                },
                status="stopped"
            )
            db.add(default_strategy)
        
        db.commit()
        logger.info("✅ 基础数据初始化完成")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 基础数据初始化失败: {e}")
        raise
    finally:
        db.close()

# Redis连接（用于缓存和实时数据）
import redis
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis连接成功")
except Exception as e:
    logger.warning(f"⚠️ Redis连接失败: {e}")
    redis_client = None
