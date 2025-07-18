"""
市场数据服务
"""
from app.models.stock_data import (
    StockData, HistoricalData, DataResponse,
    StockListResponse, HistoricalDataResponse, DataSourceInfo
)
import sys
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))


logger = logging.getLogger(__name__)


class MarketDataService:
    """市场数据服务"""

    def __init__(self):
        self.data_sources = {}
        self._init_data_sources()

    def _init_data_sources(self):
        """初始化数据源"""
        try:
            # 延迟导入，避免启动时的依赖问题
            from src.market_data.fetchers.eastmoney_api import EastMoneyAPI
            from src.market_data.fetchers.tushare_api import TushareAPI
            from src.market_data.fetchers.tencent_finance_api import TencentFinanceAPI
            from src.market_data.fetchers.free_data_sources import FreeDataSources

            self.data_sources = {
                "eastmoney": EastMoneyAPI(),
                "tushare": TushareAPI(),
                "tencent": TencentFinanceAPI(),
                "free": FreeDataSources()
            }
            logger.info("数据源初始化成功")
        except Exception as e:
            logger.error(f"数据源初始化失败: {e}")
            self.data_sources = {}

    def get_stock_data(self, symbol: str, source: str = "eastmoney") -> DataResponse:
        """获取股票实时数据"""
        try:
            if source not in self.data_sources:
                return DataResponse(
                    success=False,
                    message=f"不支持的数据源: {source}"
                )

            fetcher = self.data_sources[source]
            data = fetcher.get_stock_data(symbol)

            if data:
                stock_data = StockData(
                    symbol=symbol,
                    name=data.get('name'),
                    price=data.get('price'),
                    change=data.get('change'),
                    change_percent=data.get('change_percent'),
                    volume=data.get('volume'),
                    amount=data.get('amount'),
                    high=data.get('high'),
                    low=data.get('low'),
                    open=data.get('open'),
                    prev_close=data.get('prev_close'),
                    timestamp=datetime.now(),
                    market=data.get('market', 'CN'),
                    source=source
                )

                return DataResponse(
                    success=True,
                    data=stock_data,
                    message="获取成功"
                )
            else:
                return DataResponse(
                    success=False,
                    message="未获取到数据"
                )

        except Exception as e:
            logger.error(f"获取股票数据失败: {e}")
            return DataResponse(
                success=False,
                message=f"获取数据失败: {str(e)}"
            )

    def get_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        source: str = "eastmoney"
    ) -> DataResponse:
        """获取历史数据"""
        try:
            if source not in self.data_sources:
                return DataResponse(
                    success=False,
                    message=f"不支持的数据源: {source}"
                )

            fetcher = self.data_sources[source]
            data = fetcher.get_historical_data(symbol, start_date, end_date)

            if data and len(data) > 0:
                historical_data = []
                for item in data:
                    hist_data = HistoricalData(
                        symbol=symbol,
                        date=item.get('date'),
                        open=item.get('open'),
                        high=item.get('high'),
                        low=item.get('low'),
                        close=item.get('close'),
                        volume=item.get('volume'),
                        amount=item.get('amount'),
                        market=item.get('market', 'CN'),
                        source=source
                    )
                    historical_data.append(hist_data)

                response = HistoricalDataResponse(
                    symbol=symbol,
                    data=historical_data,
                    start_date=start_date,
                    end_date=end_date,
                    total_records=len(historical_data)
                )

                return DataResponse(
                    success=True,
                    data=response,
                    message="获取成功"
                )
            else:
                return DataResponse(
                    success=False,
                    message="未获取到历史数据"
                )

        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return DataResponse(
                success=False,
                message=f"获取历史数据失败: {str(e)}"
            )

    def get_stock_list(self, market: str = "CN", source: str = "eastmoney") -> DataResponse:
        """获取股票列表"""
        try:
            if source not in self.data_sources:
                return DataResponse(
                    success=False,
                    message=f"不支持的数据源: {source}"
                )

            fetcher = self.data_sources[source]
            data = fetcher.get_stock_list(market)

            if data:
                stocks = []
                for item in data:
                    stock = StockData(
                        symbol=item.get('symbol'),
                        name=item.get('name'),
                        price=item.get('price'),
                        change=item.get('change'),
                        change_percent=item.get('change_percent'),
                        volume=item.get('volume'),
                        amount=item.get('amount'),
                        high=item.get('high'),
                        low=item.get('low'),
                        open=item.get('open'),
                        prev_close=item.get('prev_close'),
                        timestamp=datetime.now(),
                        market=market,
                        source=source
                    )
                    stocks.append(stock)

                response = StockListResponse(
                    stocks=stocks,
                    total=len(stocks),
                    page=1,
                    size=len(stocks)
                )

                return DataResponse(
                    success=True,
                    data=response,
                    message="获取成功"
                )
            else:
                return DataResponse(
                    success=False,
                    message="未获取到股票列表"
                )

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return DataResponse(
                success=False,
                message=f"获取股票列表失败: {str(e)}"
            )

    def get_data_sources(self) -> DataResponse:
        """获取可用数据源信息"""
        try:
            sources = []
            for name, fetcher in self.data_sources.items():
                source_info = DataSourceInfo(
                    name=name,
                    description=f"{name}数据源",
                    supported_markets=["CN", "HK"],
                    data_types=["realtime", "historical"],
                    status="active"
                )
                sources.append(source_info)

            return DataResponse(
                success=True,
                data=sources,
                message="获取成功"
            )

        except Exception as e:
            logger.error(f"获取数据源信息失败: {e}")
            return DataResponse(
                success=False,
                message=f"获取数据源信息失败: {str(e)}"
            )

    def search_stocks(self, keyword: str, source: str = "eastmoney") -> DataResponse:
        """搜索股票"""
        try:
            if source not in self.data_sources:
                return DataResponse(
                    success=False,
                    message=f"不支持的数据源: {source}"
                )

            fetcher = self.data_sources[source]
            data = fetcher.search_stocks(keyword)

            if data:
                stocks = []
                for item in data:
                    stock = StockData(
                        symbol=item.get('symbol'),
                        name=item.get('name'),
                        price=item.get('price'),
                        change=item.get('change'),
                        change_percent=item.get('change_percent'),
                        volume=item.get('volume'),
                        amount=item.get('amount'),
                        high=item.get('high'),
                        low=item.get('low'),
                        open=item.get('open'),
                        prev_close=item.get('prev_close'),
                        timestamp=datetime.now(),
                        market=item.get('market', 'CN'),
                        source=source
                    )
                    stocks.append(stock)

                response = StockListResponse(
                    stocks=stocks,
                    total=len(stocks),
                    page=1,
                    size=len(stocks)
                )

                return DataResponse(
                    success=True,
                    data=response,
                    message="搜索成功"
                )
            else:
                return DataResponse(
                    success=False,
                    message="未找到匹配的股票"
                )

        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            return DataResponse(
                success=False,
                message=f"搜索股票失败: {str(e)}"
            )


# 全局服务实例
market_data_service = MarketDataService()
