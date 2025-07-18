"""
市场数据服务
"""

from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime, date

from app.models.market_data import MarketIndex, MarketStats
from app.schemas.market_data import MarketOverview, BenchmarkComparison

logger = logging.getLogger(__name__)

class MarketDataService:
    """市场数据服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_market_overview(self) -> MarketOverview:
        """获取市场概览"""
        try:
            # 获取主要指数
            indices = self.db.query(MarketIndex).filter(
                MarketIndex.trade_date == date.today()
            ).all()
            
            # 获取市场统计
            stats = self.db.query(MarketStats).filter(
                MarketStats.trade_date == date.today()
            ).first()
            
            # 如果没有今天的数据，创建模拟数据
            if not stats:
                stats = MarketStats(
                    trade_date=date.today(),
                    rise_count=1856,
                    fall_count=1234,
                    flat_count=456,
                    limit_up_count=23,
                    limit_down_count=8,
                    total_volume=2456000000,
                    total_amount=245600000000.0,
                    market_sentiment="neutral"
                )
            
            return MarketOverview(
                indices=indices,
                stats=stats,
                market_status="open",
                update_time=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            raise
    
    async def get_benchmark_comparison(
        self, 
        benchmark_code: str, 
        account_id: Optional[int] = None,
        strategy_id: Optional[int] = None
    ) -> BenchmarkComparison:
        """获取基准对比数据"""
        try:
            # 这里应该根据account_id或strategy_id获取实际收益率
            # 现在使用模拟数据
            account_return = 5.23
            
            # 根据基准代码获取基准收益率
            benchmark_returns = {
                "sh": 2.15,      # 上证指数
                "hs300": 2.85,   # 沪深300
                "sz": 1.95,      # 深证成指
                "cyb": 3.45      # 创业板指
            }
            
            benchmark_names = {
                "sh": "上证指数",
                "hs300": "沪深300",
                "sz": "深证成指",
                "cyb": "创业板指"
            }
            
            benchmark_return = benchmark_returns.get(benchmark_code, 2.15)
            benchmark_name = benchmark_names.get(benchmark_code, "基准指数")
            
            return BenchmarkComparison(
                benchmark_code=benchmark_code,
                benchmark_name=benchmark_name,
                account_return=account_return,
                benchmark_return=benchmark_return,
                excess_return=account_return - benchmark_return,
                comparison_period="本周"
            )
            
        except Exception as e:
            logger.error(f"获取基准对比失败: {e}")
            raise
    
    async def update_market_data(self):
        """更新市场数据"""
        try:
            # 这里应该从外部数据源获取最新数据
            # 现在创建一些模拟数据
            
            today = date.today()
            
            # 更新指数数据
            indices_data = [
                {"code": "000001", "name": "上证指数", "current": 2956.85, "change": 15.23},
                {"code": "000300", "name": "沪深300", "current": 3456.78, "change": 23.45},
                {"code": "399001", "name": "深证成指", "current": 9234.56, "change": -12.34},
                {"code": "399006", "name": "创业板指", "current": 2123.45, "change": 8.76}
            ]
            
            for data in indices_data:
                index = self.db.query(MarketIndex).filter(
                    MarketIndex.code == data["code"],
                    MarketIndex.trade_date == today
                ).first()
                
                if not index:
                    index = MarketIndex(
                        code=data["code"],
                        name=data["name"],
                        trade_date=today
                    )
                    self.db.add(index)
                
                index.current_value = data["current"]
                index.change_value = data["change"]
                index.change_percent = (data["change"] / (data["current"] - data["change"])) * 100
            
            # 更新市场统计
            stats = self.db.query(MarketStats).filter(
                MarketStats.trade_date == today
            ).first()
            
            if not stats:
                stats = MarketStats(trade_date=today)
                self.db.add(stats)
            
            stats.rise_count = 1856
            stats.fall_count = 1234
            stats.flat_count = 456
            stats.limit_up_count = 23
            stats.limit_down_count = 8
            stats.total_volume = 2456000000
            stats.total_amount = 245600000000.0
            stats.calculate_sentiment()
            
            self.db.commit()
            logger.info("市场数据更新成功")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新市场数据失败: {e}")
            raise
