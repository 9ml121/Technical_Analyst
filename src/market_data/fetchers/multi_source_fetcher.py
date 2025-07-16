#!/usr/bin/env python3
"""
多数据源整合器

实现数据源自动切换、故障转移和数据质量对比验证
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """数据源类型"""
    AKSHARE = "akshare"
    EASTMONEY = "eastmoney"
    TUSHARE = "tushare"
    YAHOO = "yahoo"
    ALPHA_VANTAGE = "alpha_vantage"


@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    type: DataSourceType
    priority: int  # 优先级，数字越小优先级越高
    is_free: bool
    cost_per_month: Optional[float] = None
    rate_limit: Optional[int] = None  # 每分钟请求限制
    supports_a_stock: bool = True
    supports_h_stock: bool = False
    supports_us_stock: bool = False


@dataclass
class DataQualityMetrics:
    """数据质量指标"""
    completeness: float  # 数据完整性 (0-1)
    accuracy: float      # 数据准确性 (0-1)
    timeliness: float    # 数据及时性 (0-1)
    consistency: float   # 数据一致性 (0-1)
    overall_score: float  # 综合评分


class MultiSourceFetcher:
    """多数据源整合器"""

    def __init__(self):
        """初始化多数据源整合器"""
        self.data_sources = self._initialize_data_sources()
        self.health_status = {}
        self.performance_metrics = {}
        self.last_health_check = {}

        # 初始化各个数据源
        self._init_data_sources()

    def _initialize_data_sources(self) -> Dict[str, DataSourceConfig]:
        """初始化数据源配置"""
        return {
            "akshare": DataSourceConfig(
                name="akshare",
                type=DataSourceType.AKSHARE,
                priority=1,
                is_free=True,
                rate_limit=100,
                supports_a_stock=True,
                supports_h_stock=True,
                supports_us_stock=False
            ),
            "eastmoney": DataSourceConfig(
                name="eastmoney",
                type=DataSourceType.EASTMONEY,
                priority=2,
                is_free=True,
                rate_limit=60,
                supports_a_stock=True,
                supports_h_stock=False,
                supports_us_stock=False
            ),
            "tushare": DataSourceConfig(
                name="tushare",
                type=DataSourceType.TUSHARE,
                priority=3,
                is_free=False,
                cost_per_month=199.0,  # 基础版月费
                rate_limit=500,
                supports_a_stock=True,
                supports_h_stock=False,
                supports_us_stock=False
            ),
            "yahoo": DataSourceConfig(
                name="yahoo",
                type=DataSourceType.YAHOO,
                priority=4,
                is_free=True,
                rate_limit=2000,
                supports_a_stock=False,
                supports_h_stock=True,
                supports_us_stock=True
            ),
            "alpha_vantage": DataSourceConfig(
                name="alpha_vantage",
                type=DataSourceType.ALPHA_VANTAGE,
                priority=5,
                is_free=True,
                rate_limit=5,  # 免费版限制很严格
                supports_a_stock=False,
                supports_h_stock=False,
                supports_us_stock=True
            )
        }

    def _init_data_sources(self):
        """初始化各个数据源实例"""
        self.source_instances = {}

        # 初始化akshare
        try:
            import akshare as ak
            self.source_instances["akshare"] = ak
            logger.info("akshare数据源初始化成功")
        except ImportError:
            logger.warning("akshare未安装，跳过初始化")

        # 初始化东方财富API
        try:
            from .eastmoney_api import EastMoneyAPI
            self.source_instances["eastmoney"] = EastMoneyAPI()
            logger.info("东方财富API初始化成功")
        except Exception as e:
            logger.warning(f"东方财富API初始化失败: {e}")

        # 初始化Tushare API
        try:
            from .tushare_api import TushareAPI
            self.source_instances["tushare"] = TushareAPI()
            logger.info("Tushare API初始化成功")
        except Exception as e:
            logger.warning(f"Tushare API初始化失败: {e}")

    def get_available_sources(self, market_type: str = "a_stock") -> List[str]:
        """获取可用的数据源列表"""
        available = []

        for name, config in self.data_sources.items():
            if name not in self.source_instances:
                continue

            if market_type == "a_stock" and config.supports_a_stock:
                available.append(name)
            elif market_type == "h_stock" and config.supports_h_stock:
                available.append(name)
            elif market_type == "us_stock" and config.supports_us_stock:
                available.append(name)

        # 按优先级排序
        available.sort(key=lambda x: self.data_sources[x].priority)
        return available

    def check_source_health(self, source_name: str) -> bool:
        """检查数据源健康状态"""
        if source_name not in self.source_instances:
            return False

        try:
            # 简单的健康检查
            if source_name == "akshare":
                # akshare健康检查
                return True
            elif source_name == "eastmoney":
                # 东方财富API健康检查
                api = self.source_instances[source_name]
                stocks = api.get_a_stock_realtime(limit=1)
                return len(stocks) > 0
            elif source_name == "tushare":
                # Tushare API健康检查
                api = self.source_instances[source_name]
                return api.is_available()

            return True
        except Exception as e:
            logger.error(f"数据源 {source_name} 健康检查失败: {e}")
            return False

    def get_historical_data_with_fallback(self,
                                          stock_code: str,
                                          start_date: date,
                                          end_date: date,
                                          market_type: str = "a_stock") -> Optional[List[Dict[str, Any]]]:
        """获取历史数据，支持故障转移"""

        available_sources = self.get_available_sources(market_type)

        for source_name in available_sources:
            try:
                logger.info(f"尝试使用 {source_name} 获取 {stock_code} 的历史数据")

                data = self._fetch_from_source(
                    source_name, stock_code, start_date, end_date)

                if data and len(data) > 0:
                    logger.info(f"成功从 {source_name} 获取到 {len(data)} 条数据")
                    return data
                else:
                    logger.warning(f"从 {source_name} 获取的数据为空")

            except Exception as e:
                logger.error(f"从 {source_name} 获取数据失败: {e}")
                continue

        logger.error(f"所有数据源都无法获取 {stock_code} 的历史数据")
        return None

    def _fetch_from_source(self, source_name: str, stock_code: str,
                           start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从指定数据源获取数据"""

        if source_name == "akshare":
            return self._fetch_from_akshare(stock_code, start_date, end_date)
        elif source_name == "eastmoney":
            return self._fetch_from_eastmoney(stock_code, start_date, end_date)
        elif source_name == "tushare":
            return self._fetch_from_tushare(stock_code, start_date, end_date)
        elif source_name == "yahoo":
            return self._fetch_from_yahoo(stock_code, start_date, end_date)

        return None

    def _fetch_from_akshare(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从akshare获取数据"""
        try:
            import akshare as ak
            import pandas as pd

            start_date_str = start_date.strftime('%Y%m%d')
            end_date_str = end_date.strftime('%Y%m%d')

            if stock_code.startswith(('6', '0', '3')):
                # A股数据
                df = ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date_str,
                    end_date=end_date_str,
                    adjust=""
                )
            else:
                # 港股数据
                df = ak.stock_hk_hist(
                    symbol=stock_code,
                    period="daily",
                    start_date=start_date_str,
                    end_date=end_date_str,
                    adjust=""
                )

            if df.empty:
                return None

            # 转换为统一格式
            result = []
            for _, row in df.iterrows():
                if '日期' in df.columns:
                    # A股数据格式
                    data = {
                        'date': row['日期'],
                        'open': float(row['开盘']),
                        'close': float(row['收盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'volume': int(row['成交量']),
                        'amount': float(row.get('成交额', 0)),
                        'pct_change': float(row.get('涨跌幅', 0)),
                        'source': 'akshare'
                    }
                else:
                    # 港股数据格式
                    data = {
                        'date': row['日期'],
                        'open': float(row['开盘']),
                        'close': float(row['收盘']),
                        'high': float(row['最高']),
                        'low': float(row['最低']),
                        'volume': int(row['成交量']),
                        'amount': float(row.get('成交额', 0)),
                        'pct_change': 0.0,  # 港股可能没有涨跌幅
                        'source': 'akshare'
                    }
                result.append(data)

            return result

        except Exception as e:
            logger.error(f"akshare获取数据失败: {e}")
            return None

    def _fetch_from_eastmoney(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从东方财富API获取数据"""
        try:
            api = self.source_instances["eastmoney"]
            data = api.get_historical_data(stock_code, start_date, end_date)

            if data:
                # 添加数据源标识
                for item in data:
                    item['source'] = 'eastmoney'

            return data

        except Exception as e:
            logger.error(f"东方财富API获取数据失败: {e}")
            return None

    def _fetch_from_tushare(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从Tushare API获取数据"""
        try:
            api = self.source_instances["tushare"]

            if not api.is_available():
                return None

            # 转换为Tushare格式的代码
            if stock_code.startswith('6'):
                ts_code = f"{stock_code}.SH"
            elif stock_code.startswith(('0', '3')):
                ts_code = f"{stock_code}.SZ"
            else:
                return None  # Tushare不支持港股

            data = api.get_daily_data(
                ts_code,
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )

            if data:
                # 转换为统一格式
                result = []
                for item in data:
                    result.append({
                        'date': item['trade_date'],
                        'open': float(item['open']),
                        'close': float(item['close']),
                        'high': float(item['high']),
                        'low': float(item['low']),
                        'volume': int(item['vol']),
                        'amount': float(item['amount']),
                        'pct_change': float(item['pct_chg']),
                        'source': 'tushare'
                    })
                return result

            return None

        except Exception as e:
            logger.error(f"Tushare API获取数据失败: {e}")
            return None

    def _fetch_from_yahoo(self, stock_code: str, start_date: date, end_date: date) -> Optional[List[Dict[str, Any]]]:
        """从Yahoo Finance获取数据"""
        try:
            import yfinance as yf

            # 转换为Yahoo格式的代码
            if stock_code.startswith('6'):
                yahoo_code = f"{stock_code}.SS"  # 上海证券交易所
            elif stock_code.startswith(('0', '3')):
                yahoo_code = f"{stock_code}.SZ"  # 深圳证券交易所
            else:
                yahoo_code = f"{stock_code}.HK"  # 香港证券交易所

            ticker = yf.Ticker(yahoo_code)
            df = ticker.history(start=start_date, end=end_date)

            if df.empty:
                return None

            # 转换为统一格式
            result = []
            for date_str, row in df.iterrows():
                data = {
                    'date': date_str.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'close': float(row['Close']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'volume': int(row['Volume']),
                    'amount': 0.0,  # Yahoo没有成交额
                    'pct_change': 0.0,  # 需要自己计算
                    'source': 'yahoo'
                }
                result.append(data)

            return result

        except Exception as e:
            logger.error(f"Yahoo Finance获取数据失败: {e}")
            return None

    def compare_data_quality(self, stock_code: str, start_date: date, end_date: date) -> Dict[str, DataQualityMetrics]:
        """比较不同数据源的数据质量"""
        quality_metrics = {}

        available_sources = self.get_available_sources()

        for source_name in available_sources:
            try:
                data = self._fetch_from_source(
                    source_name, stock_code, start_date, end_date)

                if data:
                    metrics = self._calculate_quality_metrics(
                        data, start_date, end_date)
                    quality_metrics[source_name] = metrics

            except Exception as e:
                logger.error(f"计算 {source_name} 数据质量失败: {e}")

        return quality_metrics

    def _calculate_quality_metrics(self, data: List[Dict[str, Any]],
                                   start_date: date, end_date: date) -> DataQualityMetrics:
        """计算数据质量指标"""

        # 数据完整性
        expected_days = (end_date - start_date).days + 1
        actual_days = len(data)
        completeness = actual_days / expected_days if expected_days > 0 else 0

        # 数据准确性 (检查价格是否合理)
        accuracy = 1.0
        for item in data:
            if item['open'] <= 0 or item['close'] <= 0:
                accuracy -= 0.1
            if item['high'] < item['low']:
                accuracy -= 0.1
            if item['high'] < item['open'] or item['high'] < item['close']:
                accuracy -= 0.1
        accuracy = max(0.0, accuracy)

        # 数据及时性 (检查最新数据日期)
        timeliness = 1.0
        if data:
            latest_date = max(item['date'] for item in data)
            latest_date_obj = datetime.strptime(latest_date, '%Y-%m-%d').date()
            days_diff = (date.today() - latest_date_obj).days
            if days_diff > 5:  # 超过5天认为不够及时
                timeliness = max(0.0, 1.0 - days_diff * 0.1)

        # 数据一致性 (检查数据格式是否统一)
        consistency = 1.0
        required_fields = ['date', 'open', 'close', 'high', 'low', 'volume']
        for item in data:
            for field in required_fields:
                if field not in item or item[field] is None:
                    consistency -= 0.1
        consistency = max(0.0, consistency)

        # 综合评分
        overall_score = (completeness + accuracy +
                         timeliness + consistency) / 4

        return DataQualityMetrics(
            completeness=completeness,
            accuracy=accuracy,
            timeliness=timeliness,
            consistency=consistency,
            overall_score=overall_score
        )

    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        report = {
            'total_sources': len(self.data_sources),
            'available_sources': len(self.source_instances),
            'health_status': {},
            'quality_metrics': {},
            'recommendations': []
        }

        # 健康状态
        for source_name in self.data_sources.keys():
            report['health_status'][source_name] = self.check_source_health(
                source_name)

        # 数据质量对比
        if self.performance_metrics:
            report['quality_metrics'] = self.performance_metrics

        # 建议
        free_sources = [name for name, config in self.data_sources.items()
                        if config.is_free and name in self.source_instances]
        paid_sources = [name for name, config in self.data_sources.items()
                        if not config.is_free and name in self.source_instances]

        if free_sources:
            report['recommendations'].append(
                f"推荐使用免费数据源: {', '.join(free_sources)}")

        if paid_sources:
            report['recommendations'].append(
                f"付费数据源: {', '.join(paid_sources)}")

        return report
