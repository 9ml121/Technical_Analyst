"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine, MetaData
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

# 元数据
metadata = MetaData()

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
            user, account, strategy, trade, 
            market_data, performance
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
        from app.models.account import SimulatedAccount
        from app.models.strategy import Strategy
        
        # 检查是否已有默认账户
        default_account = db.query(SimulatedAccount).filter(
            SimulatedAccount.name == "默认模拟账户"
        ).first()
        
        if not default_account:
            # 创建默认模拟账户
            default_account = SimulatedAccount(
                name="默认模拟账户",
                initial_capital=settings.DEFAULT_INITIAL_CAPITAL,
                current_capital=settings.DEFAULT_INITIAL_CAPITAL,
                status="active"
            )
            db.add(default_account)
        
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
